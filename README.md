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
    This script installs the python packages required for running the tasks successfully
       a. specifically the pynt package
       b. sets up the virtual environment for executing the tasks
