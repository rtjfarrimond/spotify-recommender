resource "aws_dynamodb_table" "audio-features" {
  name             = "${var.system_code}-dynamodb"
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
