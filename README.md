#       Example of automating deployment of AWS CloudFormation templates

          This example uses pynt, a lightweight python build tool, to execute tasks for creating and deleting AWS CloudFormation templates.
          
          The examples of AWS CloudFormation stacks include 
                    Individual Templates
                    Nested Stack

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
             Store the private portion of the key-pair safely on your local machine.

## Description of this repository's CloudFormation Templates

### Nested Stack example

#### webapp-nested-resources
          $ pynt create_nested_stack["webapp-nested-resources"]
          
          This stack creates a fully functional web application running using python Flask with postgresdb as its datastore. 
          The webapplication can be accessed using http://<webapp-instance-public-dns>:8000/ .
          Creates network-resources, natgw-resources, ssm-resources, postgres-db-resources, webapp-resources. 

### Individual Stacks example

          The program has options to create the following stacks individually. Description of each of the stack is provided below:

#### network-resources
          $ pynt create_stack["network-resources"]
          
          Creates a custom VPC and its related resources [subnets, route tables, igw].
         
#### natgw-resources
          $ pynt create_stack["natgw-resources"]
          
          Creates a nat gateway in one of the public subnets and an associated route table with a private subnet mapping.
          This stack is dependent on the network-resources stack created above.
          
#### ssm-resources 
          $ pynt create_stack["ssm-resources"]
          
          Creates required ssm parameters for postgres-db-resources and webapp-resouces template to use.
          There is no dependency on any stack.
          
#### postgres-db-resources
          $ pynt create_stack["postgres-db-resources"]
          
          Creates an ec2 instance with a postgres db hosted on it in a private subnet.
          This stack is dependent on the network-resources stack and ssm-resources stack created above.
          
#### webapp-resources 
          $ pynt create_stack["webapp-resources"]
          
          Creates an ec2 instance with a python Flask webapp hosted on it in a public subnet. 
          The webapplication can be accessed using http://<webapp-instance-public-dns>:8000/
          This stack is dependent on the network-resources stack and ssm-resources stack created above.
          
#### Note
          If you choose to create all the above individual stacks in the specified order, then you will have a fully functional web application running on python Flask with postgredb as its datastore.
          
          You can execute all the individual stacks using one command as shown below:
          
                    $ pynt create_stack["network-resources","natgw-resources","ssm-resources","postgres-db-resources","webapp-resources"]

### Regarding the source code, "build.py"
          This is the python code which gets invoked when "pynt" is executed on the command line.
          A function with "task" decorator is executed when the specific function is invoked using the following command:
        
          You can include your own tasks with dependencies across tasks and create your own automation deployment pipeline.
