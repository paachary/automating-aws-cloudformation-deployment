#!/usr/bin/python

import sys
from pynt import task
import boto3
import time
import botocore
from botocore.exceptions import ClientError
import json
import re


"""
Private functions within the module to perform specific tasks
"""

def _read_json(jsonf_path):
    '''Read a JSON file into a dict.'''
    with open(jsonf_path, 'r') as jsonf:
        json_text = jsonf.read()
        return json.loads(json_text)


def _create_individual_stack(stack):
    cfn_path = "templates/{}.yaml".format(stack)
    cfn_params_path = "parameters/{}-params.json".format(stack)
    cfn_params = _read_json(cfn_params_path)
    stack_name = stack

    cfn_file = open(cfn_path, 'r')
    cfn_template = cfn_file.read(51200) #Maximum size of a cfn template

    cfn_client = boto3.client('cloudformation')
    print("Attempting to CREATE '%s' stack using CloudFormation." % stack_name)
    start_t = time.time()
    response = cfn_client.create_stack(
        StackName=stack_name,
        TemplateBody=cfn_template,
        Parameters=cfn_params,
        Capabilities=[
            'CAPABILITY_NAMED_IAM',
        ],
    )

    print("Waiting until '%s' stack status is CREATE_COMPLETE" % stack_name)

    try:
        cfn_stack_delete_waiter = cfn_client.get_waiter('stack_create_complete')
        cfn_stack_delete_waiter.wait(StackName=stack_name)
        print("Stack CREATED in approximately %d secs." % int(time.time() - start_t))

    except Exception as e:
        print("Stack creation FAILED.")
        print(e.message)

def _get_stack_output(stack_name):
    cloudformation = boto3.resource('cloudformation')
    
    stack_object = cloudformation.Stack(stack_name)

    for i in range(0, len(stack_object.outputs)):
        if (stack_object.outputs[i]['OutputKey'] == 'S3Bucket'):
            return (stack_object.outputs[i]['OutputValue'])


def _upload_children_template_files(stack):
    print("Uploading children template files to the s3 bucket")
    s3_bucket_name = _get_stack_output(stack)

    s3_client = boto3.client("s3")

    templates=[ "network-resources",
                "natgw-resources",
                "ssm-resources",
                "postgres-db-resources",
                "webapp-resources" ]
    for file in range(0, len(templates)):
        cfn_path = "templates/{}.yaml".format(templates[file])
        cfn_file = open(cfn_path, 'rb')
        with cfn_file as data:
            print(data)
            s3_client.upload_fileobj(data, s3_bucket_name, 'cloudformation-templates/{}.yaml'.format(templates[file]))

def _empty_s3_contents(stack):
    s3 = boto3.resource('s3')
    s3_bucket_name = _get_stack_output(stack)    
    bucket = s3.Bucket(s3_bucket_name)
    bucket.objects.delete()

"""
End of Private functions section
"""

"""
Tasks' section
"""
@task()
def _check_aws_settings():
    print("Checking if AWS environment has been setup...")
    region_name = boto3.session.Session().region_name
    if (region_name == None):
        raise Exception('AWS CLI has not been configured. Please configure aws cli and re-run the module.')

@task()
def _create_s3_bucket(*stacks):
    """ Creating an s3 bucket to hold the cloudformation templates of all children stacks"""

    stack = "s3-resources"
    _create_individual_stack(stack)
    _upload_children_template_files(stack)


@task(_check_aws_settings, _create_s3_bucket)
def create_nested_stack(*stacks):
    """ Creating cloudformation nested stack. The argument to this function is the parent stack name (s) """

    if len(stacks) == 0:
        print("\nERROR!! Specify atleast one stack to be created. \nSyntax: create-stack[value1, value2, ...]. \n"+
        "Valid values are: \n\n" + 
            "   webapp-nested-resources -> Creates network-resources, natgw-resources, ssm-resources, postgres-db-resources, webapp-resources. \n" + 
                " If you choose to create the individual resources, please choose pynt create_stack[] option.")
        return                

    create_stack(*stacks)

    print("Emptying the temporary s3 bucket contents and deleting the S3 bucket...")

    _empty_s3_contents("s3-resources")
    delete_stack("s3-resources")


@task(_check_aws_settings)
def create_stack(*stacks, **kwargs):
    """ Creating cloudformation stacks based on stack names """

    if len(stacks) == 0:
        print("\nERROR!! Specify atleast one stack to be created. \nSyntax: create-stack[value1, value2, ...]. \n"+
        "Valid values are: \n\n" + 
            "   webapp-nested-resources -> Creates network-resources, natgw-resources, ssm-resources, postgres-db-resources, webapp-resources. \n" + 
                " If you choose to create the individual resources, please choose all or any of the following stacks.\n\n\n" +
            "   network-resources       -> Creates a custom VPC and its related resources [subnets, route tables, igw]. \n" +
            "   natgw-resources         -> Creates a nat gateway in one of the public subnets and an associated route table with a private subnet mapping. \n"+
            "   ssm-resources           -> Creates required ssm parameters for postgres-db-resources and webapp-resouces template to use. \n" +
            "   postgres-db-resources   -> Creates an ec2 instance with a postgres db hosted on it in a private subnet.\n" +
            "   webapp-resources        -> Creates an ec2 instance with a python Flask webapp hosted on it in a public subnet.")
        return

    for stack in stacks:
        print(stack)    
        _create_individual_stack(stack)

@task(_check_aws_settings)
def delete_stack(* stacks):
    '''Delete stacks using CloudFormation.'''

    if len(stacks) == 0:
        print("ERROR: Please specify a stack to delete.")
        return

    for stack in stacks:
        stack_name = stack
    
        cfn_client = boto3.client('cloudformation')

        print("Attempting to DELETE '%s' stack using CloudFormation." % stack_name)
        start_t = time.time()
        response = cfn_client.delete_stack(
            StackName=stack_name
        )

        print("Waiting until '%s' stack status is DELETE_COMPLETE" % stack_name)
        cfn_stack_delete_waiter = cfn_client.get_waiter('stack_delete_complete')
        cfn_stack_delete_waiter.wait(StackName=stack_name)
        print("Stack DELETED in approximately %d secs." % int(time.time() - start_t))


@task(_check_aws_settings)
def cleanup_env():
    """ PLEASE BE CAREFUL WHILE USING THIS TASK. THIS WILL ATTEMPT TO DELETE ALL THE STACKS IN YOUR USER ACCOUNT!!! """
    
    print("Emptying s3 contents..")

    _empty_s3_contents("s3-resources")

    cfn_client = boto3.client('cloudformation')

    response = cfn_client.list_stacks(
        StackStatusFilter=['CREATE_COMPLETE']
    )

    stack_info = response['StackSummaries']

    stacks = []

    for i in range(0, len(stack_info)):
        if 'ParentId' not in stack_info[i]:
            stacks.append(stack_info[i]['StackName'])

    print("Deleting stacks...")
    delete_stack(*stacks)

       
# Default task (if specified) is run when no task is specified in the command line
# make sure you define the variable __DEFAULT__ after the task is defined
# A good convention is to define it at the end of the module
# __DEFAULT__ is an optional member

__DEFAULT__= create_nested_stack