# The REST API is the container for all of the other api gateway objects we create.
resource "aws_api_gateway_rest_api" "spot-rec-api" {
  name        = "spot-rec-rest-api"
  description = "A GET endpoint to get tracks that sound like a query track."
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.spot-rec-api.id}"
  parent_id   = "${aws_api_gateway_rest_api.spot-rec-api.root_resource_id}"
  path_part   = "sounds-like"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = "${aws_api_gateway_rest_api.spot-rec-api.id}"
  resource_id   = "${aws_api_gateway_resource.proxy.id}"
  http_method   = "GET"
  authorization = "NONE"

  request_parameters {
    "method.request.querystring.trackId" = true
  }
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = "${aws_api_gateway_rest_api.spot-rec-api.id}"
  resource_id = "${aws_api_gateway_method.proxy.resource_id}"
  http_method = "${aws_api_gateway_method.proxy.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.api-get.invoke_arn}"
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = "${aws_api_gateway_rest_api.spot-rec-api.id}"
  resource_id   = "${aws_api_gateway_rest_api.spot-rec-api.root_resource_id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = "${aws_api_gateway_rest_api.spot-rec-api.id}"
  resource_id = "${aws_api_gateway_method.proxy_root.resource_id}"
  http_method = "${aws_api_gateway_method.proxy_root.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.api-get.invoke_arn}"
}

resource "aws_api_gateway_deployment" "spot-rec-api-deployment" {
  depends_on = [
    "aws_api_gateway_integration.lambda",
    "aws_api_gateway_integration.lambda_root",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.spot-rec-api.id}"
  stage_name  = "sounds-like"
}
