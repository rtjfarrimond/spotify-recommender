resource "aws_s3_bucket" "recommender-bucket" {
  bucket = "spotify-recommender-bucket"
  acl    = "private"
  region = "${var.region}"

  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket" "api-get-lambda-bucket" {
  bucket = "spot-rec-api-get-lambda-bucket"
  acl    = "private"
  region = "${var.region}"

  versioning {
    enabled = true
  }
}
