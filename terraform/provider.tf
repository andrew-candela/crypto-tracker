provider "aws" {
  version = "~> 2.0"
  region  = "us-west-2"
}

terraform {
  backend "s3" {
    bucket = "apc-tf"
    key    = "crypto_tracker/terraform.tfstate"
    region = "us-west-2"
  }
}
