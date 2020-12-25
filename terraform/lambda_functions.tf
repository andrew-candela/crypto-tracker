resource "aws_lambda_function" "crypto_batch" {
  function_name                  = "crypto_batch"
  role                           = aws_iam_role.crypto.arn
  s3_bucket                      = var.AWS_BUCKET
  s3_key                         = "lambda_functions_deployment_packages/crypto/function.zip"
  handler                        = "service.get_metrics.lambda_handler"
  memory_size                    = 3008
  reserved_concurrent_executions = -1
  runtime                        = "python3.7"
  timeout                        = 15
  tracing_config {
      mode = "PassThrough"
  }
  environment {
    variables = {
      LOG_LEVEL = "${var.LOG_LEVEL}",
      PG_HOST = "${aws_db_instance.crypto_db.address}",
      PG_PORT = "${var.PG_PORT}",
      PG_DATABASE = "${var.PG_DATABASE}",
      PG_USER = "${var.PG_USER}",
      PG_PASSWORD = "${var.PG_PASSWORD}",
      LOG_LEVEL = "${var.LOG_LEVEL}",
      ALERT_THRESHOLD = "${var.ALERT_THRESHOLD}",
      FROM_EMAIL = "${var.FROM_EMAIL}",
    }
  }
}

resource "aws_lambda_function" "crypto_metrics" {
  function_name                  = "crypto_metrics"
  role                           = aws_iam_role.crypto.arn
  s3_bucket                      = var.AWS_BUCKET
  s3_key                         = "lambda_functions_deployment_packages/crypto/function.zip"
  handler                        = "service.routes.metrics.lambda_handler"
  memory_size                    = 3008
  reserved_concurrent_executions = -1
  runtime                        = "python3.7"
  timeout                        = 5
  tracing_config {
      mode = "PassThrough"
  }
  environment {
    variables = {
      LOG_LEVEL = "${var.LOG_LEVEL}",
      PG_HOST = "${aws_db_instance.crypto_db.address}",
      PG_PORT = "${var.PG_PORT}",
      PG_DATABASE = "${var.PG_DATABASE}",
      PG_USER = "${var.PG_USER}",
      PG_PASSWORD = "${var.PG_PASSWORD}",
      LOG_LEVEL = "${var.LOG_LEVEL}",
      ALERT_THRESHOLD = "${var.ALERT_THRESHOLD}",
      FROM_EMAIL = "${var.FROM_EMAIL}",
    }
  }
}

resource "aws_lambda_function" "crypto_email" {
  function_name                  = "crypto_email"
  role                           = aws_iam_role.crypto.arn
  s3_bucket                      = var.AWS_BUCKET
  s3_key                         = "lambda_functions_deployment_packages/crypto/function.zip"
  handler                        = "service.routes.emails.lambda_handler"
  memory_size                    = 3008
  reserved_concurrent_executions = -1
  runtime                        = "python3.7"
  timeout                        = 5
  tracing_config {
      mode = "PassThrough"
  }
  environment {
    variables = {
      LOG_LEVEL = "${var.LOG_LEVEL}",
      PG_HOST = "${aws_db_instance.crypto_db.address}",
      PG_PORT = "${var.PG_PORT}",
      PG_DATABASE = "${var.PG_DATABASE}",
      PG_USER = "${var.PG_USER}",
      PG_PASSWORD = "${var.PG_PASSWORD}",
      LOG_LEVEL = "${var.LOG_LEVEL}",
      ALERT_THRESHOLD = "${var.ALERT_THRESHOLD}",
      FROM_EMAIL = "${var.FROM_EMAIL}",
    }
  }
}


# Schedule the lambda function
resource "aws_cloudwatch_event_rule" "cadence" {
  name                = "every-one-minute"
  description         = "Fires every one minutes"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "run_batch_job" {
  rule      = aws_cloudwatch_event_rule.cadence.name
  target_id = "lambda"
  arn       = aws_lambda_function.crypto_batch.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_crypto_batch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crypto_batch.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cadence.arn
}
