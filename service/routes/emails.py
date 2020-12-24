"""This will be responsible for allowing users to sign up for notifications.
It will also support removal of notifications...
I expect the notifications will be quite noisy.
"""

from service.lib.pg import PG
from service.lib import utils as ut
from service import LOG_LEVEL
import logging
from typing import List
import json


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def get_emails() -> List[str]:
    logger.debug("fetching emails")
    with PG.create_connection() as conn:
        recs = PG.fetch_data(conn, "SELECT DISTINCT address FROM crypto.email_recipients;")
    return [rec['address'] for rec in recs]


def add_email_address(email: str) -> None:
    logger.debug(f"adding email {email}")
    with PG.create_connection() as conn:
        PG.write_dictionary_to_table([{"address": email}], "crypto.email_recipients", conn)


def remove_email_address(email: str) -> None:
    logger.debug(f"removing email: {email}")
    with PG.create_connection() as conn:
        PG.delete_records_from_table("address", [email], "crypto.email_recipients", conn)


def lambda_handler(event: {}, context: {}) -> str:
    if event['httpMethod'] == 'GET':
        emails = get_emails()
        return ut.webify_output({'Emails': emails})

    params = ut.parse_body_parameters(event)
    print(params)
    if 'email' not in params:
        return ut.webify_output("Must include 'email' in request body", 400)

    if event['httpMethod'] == 'POST':
        add_email_address(params['email'])
        return ut.webify_output(f"Added {params['email']}")

    if event['httpMethod'] == 'DELETE':
        remove_email_address(params.get('email'))
        return ut.webify_output(f"Removed {params['email']} from subscribers list")


if __name__ == "__main__":
    event = {
        'httpMethod': 'POST',
        'body': '{"email":"email@email.com"}'
    }
    resp = lambda_handler(event, {})
    print(resp)
