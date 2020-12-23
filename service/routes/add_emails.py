"""This will be responsible for allowing users to sign up for notifications.
It will also support removal of notifications...
I expect the notifications will be quite noisy.
"""

from service.lib.pg import PG
from service import LOG_LEVEL
import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def add_email_address(email: str) -> None:
    logger.debug(f"adding email {email}")
    with PG.create_connection() as conn:
        PG.write_dictionary_to_table([{"address": email}], "crypto.email_recipients", conn)


def lambda_handler(event: {}, context: {}) -> str:
    add_email_address(event['email'])


if __name__ == "__main__":
    email = sys.argv[1]
    print(add_email_address(email))
