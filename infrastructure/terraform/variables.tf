variable "region" {
  default = "eu-west-1"
}

variable "system_code" {
  default = "spot-rec"
}

variable "extractor_image" {
  default = "feature-extractor"
}

variable "aws_account_id" {
  default = "479503948477"
}

variable "dynamodb_hash_key_name" {
  default = "TrackId"
}

variable "dynamodb_sort_key_name" {
  default = "Source"
}

variable "feature_vector_length" {
  default = "160"
}

variable "annoy_file_name" {
  default = "annoy.ann"
}

variable "feature_column_name" {
  default = "Features"
}

variable "annoy_index_col_name" {
  default = "AnnoyIndex"
}

variable "vpc" {}
variable "cidr_block" {}
variable "subnet_id" {}
variable "security_group" {}
variable "batch_submit_lambda_arn" {}
