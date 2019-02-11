resource "aws_s3_bucket" "recommender-bucket" {
  bucket = "spotify-recommender-bucket"
  acl    = "private"
  region = "${var.region}"

  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket" "spot-rec-lambda-bucket" {
  bucket        = "${var.system_code}-lambda-bucket"
  acl           = "private"
  region        = "${var.region}"
  force_destroy = true

  versioning {
    enabled = true
  }
}
