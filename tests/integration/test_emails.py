from service.routes import emails as em
from service.lib.pg import PG
import json
import unittest


class TestSuite(unittest.TestCase):

    def setUp(self):
        with PG.create_connection() as conn:
            PG.write_dictionary_to_table(
                [{"address": 'test@email.com'}],
                "crypto.email_recipients",
                conn
            )

    def tearDown(self):
        with PG.create_connection() as conn:
            PG.run_sql_command(conn, "DELETE FROM crypto.email_recipients")

    def test_get_emails(self):
        event = {
            'httpMethod': 'GET',
        }
        resp = em.lambda_handler(event, {})
        assert resp['body'] == json.dumps({'Emails': ['test@email.com']})

    def test_remove_email(self):
        event = {
            'httpMethod': 'DELETE',
            'body': '{"email":"test@email.com"}'
        }
        em.lambda_handler(event, {})
        emails = em.get_emails()
        assert set(emails) == set([])

    def test_add_existing_email(self):
        event = {
            'httpMethod': 'POST',
            'body': '{"email":"test@email.com"}'
        }
        em.lambda_handler(event, {})
        emails = em.get_emails()
        assert set(emails) == set(['test@email.com'])

    def test_add_new_email(self):
        event = {
            'httpMethod': 'POST',
            'body': '{"email":"test2@email.com"}'
        }
        em.lambda_handler(event, {})
        emails = em.get_emails()
        assert set(emails) == set(['test@email.com', 'test2@email.com'])
