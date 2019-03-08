resource "aws_ssm_parameter" "audio_bucket_name" {
  name  = "/${var.system_code}/audio_bucket_name"
  type  = "String"
  value = "${aws_s3_bucket.audio-upload-bucket.bucket}"
}

resource "aws_ssm_parameter" "extractor_ecr_repo" {
  name  = "/${var.system_code}/extractor_ecr_repo"
  type  = "String"
  value = "${aws_ecr_repository.spot-rec-ecr.name}"
}
