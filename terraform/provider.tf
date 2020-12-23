provider "aws" {
  version = "~> 2.0"
  region  = "${var.AWS_DEFAULT_REGION}"
}

terraform {
  backend "s3" {
    bucket = "${var.AWS_BUCKET}"
    key    = "crypto_tracker/terraform.tfstate"
    region = "${var.AWS_DEFAULT_REGION}"
  }
}
