resource "aws_lambda_function" "api-get" {
  function_name = "spot-rec-api-get"
  s3_bucket = "${aws_s3_bucket.api-get-lambda-bucket.bucket}"
  s3_key = "v0.1.0/hello-lambda.zip"

  handler = "main.get_handler"
  runtime = "python3.7"

  role = "${aws_iam_role.get_lambda_exec.arn}"
}

resource "aws_iam_role" "get_lambda_exec" {
  name = "get_handler_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}
