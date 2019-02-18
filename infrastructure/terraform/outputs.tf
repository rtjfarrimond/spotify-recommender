output "get_base_url" {
  value = "${aws_api_gateway_deployment.spot-rec-api-deployment.invoke_url}"
}

