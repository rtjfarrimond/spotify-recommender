resource "aws_s3_bucket" "audio-upload-bucket" {
  bucket = "${var.system_code}-audio-upload-bucket"
  acl    = "private"
  region = "${var.region}"

  versioning {
    enabled = false
  }
}
