terraform {
  backend "s3" {
    bucket = "spot-rec-tf-state"
    key    = "terraform.tfstate"
    region = "eu-west-1"
  }
}

provider "aws" {
  region = "${var.region}"
}
