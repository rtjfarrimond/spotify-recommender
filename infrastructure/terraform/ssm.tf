resource "aws_ssm_parameter" "dynamodb-table" {
  name      = "/${var.system_code}/dynamodb-table"
  type      = "String"
  value     = "${aws_dynamodb_table.audio-features.name}"
  overwrite = true
}
