terraform {
  backend "s3" {
    bucket = "spotify-recommender-bucket"
    key    = "terraform.tfstate"
    region = "eu-west-1"
  }
}

provider "aws" {
  region = "${var.region}"
}
