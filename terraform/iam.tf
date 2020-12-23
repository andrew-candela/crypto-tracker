resource "aws_iam_role" "crypto" {
    name = "crypto-lambda"
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

resource "aws_iam_policy" "crypto_access" {
  name = "crypto-access"
  description = "Grands the crypto monitor needed access"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:DescribeLogGroups",
            "logs:DescribeLogStreams",
            "logs:PutLogEvents",
            "logs:GetLogEvents",
            "logs:FilterLogEvents"
        ],
        "Resource": "*"
    },
    {
        "Action": ["ses:SendEmail"],
        "Effect": "Allow",
        "Resource": "*"
    }
  ]
}
EOF
}

resource aws_iam_role_policy_attachment crypto {
    role = aws_iam_role.crypto.name
    policy_arn = aws_iam_policy.crypto_access.arn
}