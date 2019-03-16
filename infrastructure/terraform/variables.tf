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

# This needs to be provisioned in TF rather than serverless, var is temp hack.
variable "dynamodb_table" {
  default = "spot-rec-api-dev-dynamodb"
}

variable "vpc" {}
variable "cidr_block" {}
variable "subnet_id" {}
variable "security_group" {}
variable "batch_submit_lambda_arn" {}
