provider "aws" {
  version = "~> 2.0"
  # Replace with your own bucket and region
  region  = "us-west-2"
}

terraform {
  backend "s3" {
    # Replace with your own bucket and region
    bucket = "apc-tf"
    key    = "crypto_tracker/terraform.tfstate"
    # Replace with your own bucket and region
    region = "us-west-2"
  }
}
