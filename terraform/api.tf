# Variables
data "aws_caller_identity" "current" {}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "crypto-api"
}

# ------------------------------------------------------------------------------------
# Metrics endpoints
resource "aws_api_gateway_resource" "metrics" {
  path_part   = "metrics"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "metrics" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.metrics.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "metrics" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.metrics.id
  http_method             = aws_api_gateway_method.metrics.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crypto_metrics.invoke_arn
}

resource "aws_api_gateway_resource" "list_metrics" {
  path_part   = "list-metrics"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "list_metrics" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.list_metrics.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "list_metrics" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.list_metrics.id
  http_method             = aws_api_gateway_method.list_metrics.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crypto_metrics.invoke_arn
}

# ----
# Email management
resource "aws_api_gateway_resource" "emails" {
  path_part   = "emails"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "emails" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.emails.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "emails" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.emails.id
  http_method             = aws_api_gateway_method.emails.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crypto_email.invoke_arn
}
# metrics access
resource "aws_lambda_permission" "apigw_lambda_metrics" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crypto_metrics.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

# email access
resource "aws_lambda_permission" "apigw_lambda_emails" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crypto_email.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

resource "aws_api_gateway_deployment" "prod" {
  depends_on = [
    aws_api_gateway_integration.emails,
    aws_api_gateway_integration.metrics,
    aws_api_gateway_integration.list_metrics
  ]
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod"
}

