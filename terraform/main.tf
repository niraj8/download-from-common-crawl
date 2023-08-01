terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.17.1"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "random_pet" "one" {
  length    = 1
}

resource "random_pet" "two" {
  length = 1
}
