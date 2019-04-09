resource "aws_dynamodb_table" "metadata_table" {
  name         = "${var.system_code}-audio-metadata"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "${var.dynamodb_hash_key_name}"
  range_key    = "Source"

  attribute {
    name = "${var.dynamodb_hash_key_name}"
    type = "S"
  }

  attribute {
    name = "Source"
    type = "S"
  }

  attribute {
    name = "AnnoyIndex"
    type = "N"
  }

  global_secondary_index {
    name            = "annoy_index"
    hash_key        = "AnnoyIndex"
    projection_type = "ALL"
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"
}
