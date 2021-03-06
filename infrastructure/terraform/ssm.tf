resource "aws_ssm_parameter" "audio_bucket_name" {
  name  = "/${var.system_code}/audio_bucket_name"
  type  = "String"
  value = "${aws_s3_bucket.audio-upload-bucket.bucket}"
}

resource "aws_ssm_parameter" "annoy_bucket_name" {
  name  = "/${var.system_code}/annoy_bucket_name"
  type  = "String"
  value = "${aws_s3_bucket.annoy-bucket.bucket}"
}

resource "aws_ssm_parameter" "extractor_ecr_repo" {
  name  = "/${var.system_code}/extractor_ecr_repo"
  type  = "String"
  value = "${aws_ecr_repository.spot-rec-ecr.name}"
}

resource "aws_ssm_parameter" "extractor_job_queue" {
  name  = "/${var.system_code}/extractor_job_queue"
  type  = "String"
  value = "${aws_batch_job_queue.extractor_queue.name}"
}

resource "aws_ssm_parameter" "extractor_job_definition" {
  name  = "/${var.system_code}/extractor_job_definition"
  type  = "String"
  value = "${aws_batch_job_definition.feature_extractor.name}"
}

resource "aws_ssm_parameter" "dynamodb_table" {
  name  = "/${var.system_code}/dynamodb"
  type  = "String"
  value = "${aws_dynamodb_table.metadata_table.name}"
}

resource "aws_ssm_parameter" "dynamodb_table_hash_key" {
  name  = "/${var.system_code}/dynamodb_hash_key_name"
  type  = "String"
  value = "${var.dynamodb_hash_key_name}"
}

resource "aws_ssm_parameter" "dynamodb_table_sort_key" {
  name  = "/${var.system_code}/dynamodb_sort_key_name"
  type  = "String"
  value = "${var.dynamodb_sort_key_name}"
}

resource "aws_ssm_parameter" "feature_vector_length" {
  name  = "/${var.system_code}/feature_vector_length"
  type  = "String"
  value = "${var.feature_vector_length}"
}

resource "aws_ssm_parameter" "annoy_file_name" {
  name  = "/${var.system_code}/annoy_file_name"
  type  = "String"
  value = "${var.annoy_file_name}"
}

resource "aws_ssm_parameter" "annoy_index_col_name" {
  name  = "/${var.system_code}/annoy_index_col_name"
  type  = "String"
  value = "${var.annoy_index_col_name}"
}

resource "aws_ssm_parameter" "feature_column_name" {
  name  = "/${var.system_code}/feature_column_name"
  type  = "String"
  value = "${var.feature_column_name}"
}
