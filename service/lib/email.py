from typing import Any, Dict, List
from service import LOG_LEVEL
import boto3
import logging
import os
import json


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
FROM_EMAIL = os.getenv("FROM_EMAIL")
aws_region = os.environ.get("AWS_DEFAULT_REGION", "us-west-2")


class Emailer():

    @staticmethod
    def send_email(metrics: Dict[str, Any], email_addresses: List) -> None:
        if not email_addresses:
            logger.warning("Tried to alert but there were no email addresses to send to")
            return None
        logger.debug(f"sending an alert with metrics like this: {metrics[0]}")
        ses = boto3.client("ses")
        ses.send_email(
            Destination={"ToAddresses": email_addresses},
            Message={
                "Subject": {"Data": "Crypto Alerts!"},
                "Body": {
                    "Text": {
                        "Data": "Here are the latest symbols and metrics that have crossed "
                                f"the alerting threshold:\n{json.dumps(metrics, indent=True)}"
                    }
                }
            },
            Source=FROM_EMAIL
        )
