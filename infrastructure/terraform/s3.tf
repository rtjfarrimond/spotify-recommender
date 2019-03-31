resource "aws_s3_bucket" "audio-upload-bucket" {
  bucket = "${var.system_code}-audio-upload-bucket"
  acl    = "private"
  region = "${var.region}"

  versioning {
    enabled = false
  }
}

resource "aws_s3_bucket" "annoy-bucket" {
  bucket = "${var.system_code}-annoy-bucket"
  acl    = "private"
  region = "${var.region}"

  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket_notification" "zip_upload_notification" {
  bucket = "${aws_s3_bucket.audio-upload-bucket.id}"

  lambda_function {
    lambda_function_arn = "${var.batch_submit_lambda_arn}"
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".zip"
  }
}
