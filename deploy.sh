#!/bin/bash
environment="$1"
if [ -z "$environment" ]
then
    echo "Usage: deploy.sh <environment>"
    exit 1
fi

echo -e "\n+++++ Starting deployment +++++\n"

echo "+++++ apply terraform +++++"
cd terraform
terraform init
if [ $? -ne 0 ]
then
    echo "terraform init failed"
    exit 1
fi

terraform workspace new $environment
terraform workspace select $environment

terraform apply --auto-approve

echo -e "\n+++++ Deployment done +++++\n"