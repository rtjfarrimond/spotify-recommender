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

resource "aws_s3_bucket" "recommender-bucket" {
  bucket = "spotify-recommender-bucket"
  acl    = "private"
  region = "${var.region}"

  versioning {
    enabled = true
  }
}

resource "aws_dynamodb_table" "audio-features" {
  name             = "AudioFeatures"
  billing_mode     = "PROVISIONED"
  read_capacity    = 20
  write_capacity   = 20
  hash_key         = "TrackId"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "TrackId"
    type = "S"
  }
}
