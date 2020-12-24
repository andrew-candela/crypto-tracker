# Variables
data "aws_caller_identity" "current" {}

# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "crypto-api"
}

resource "aws_api_gateway_resource" "get_metrics" {
  path_part   = "get_metrics"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "get_metrics" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.get_metrics.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.get_metrics.id
  http_method             = aws_api_gateway_method.get_metrics.http_method
  integration_http_method = "GET"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.crypto_inspect.invoke_arn
}

# Lambda
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crypto_inspect.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.AWS_DEFAULT_REGION}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.get_metrics.http_method}${aws_api_gateway_resource.get_metrics.path}"
}
