#       Example of automating deployment of CloudFormation templates

          This example uses pynt, a lightweight python build tool, to execute tasks for creating and deleting CloudFormation templates.
          
          The examples of CloudFormation templates include 
                    Individual Templates
                    Nested Templates

## Pre-requirements for using this repository

          1. Install python3 (latest version preferrable)

          2. Install and Configure AWS CLI on your local machine OR 
             Configure appropriate IAM role on the EC2 instance for executing the AWS CLI commands.

## Clone this repostory

git clone https://github.com/paachary/automating-cloudformation-deployment.git

## Execute the setup.sh script
          
          $ cd automating-cloudformation-deployment 
          $ sh setup.sh
          
    This script installs the python packages required for running the tasks successfully
       a. specifically the pynt package
       b. sets up the virtual environment for executing the tasks

## Tasks available

          Following tasks are available as a part of this repository:
          
          $ cd automating-cloudformation-deployment 
          $ . myenv/bin/activate
          
          $ pynt -l
          <<output>>
                    create_nested_stack     [Default]  Creating cloudformation nested stack. The argument to this function is the parent stack name (s) 
                    create_stack                       Creating cloudformation stacks based on stack names 
                    delete_stack                       Delete stacks using CloudFormation.
          
## Pre-requisites before executing any tasks
          
          1. Login into the AWS Console
          
          2. Create a KeyPair in the EC2 (Elastic Compute) UI with the name "keypair".
             Store the private part of the key-pair safely on your local machine.
          

