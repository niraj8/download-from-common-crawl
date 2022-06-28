terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.17.1"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "random_pet" "underscore" {
  length    = 2
  separator = "_"
}

resource "random_pet" "dash" {
  length = 2
}

module "s3update_function" {
  source = "./modules/function"

  function_name  = "${terraform.workspace}_s3update_${random_pet.underscore.id}"
  lambda_handler = "s3update"
  source_dir     = "../bin/s3update"
  tags = {
    environment = terraform.workspace
  }
}