from service.routes import emails as em
from service.lib import utils as ut
from unittest.mock import patch


mock_emails = [
    {'address': 'a'},
    {'address': 'b'},
]


class MockConn():

    def __enter__(self):
        return 'conn'

    def __exit__(self, *args, **kwargs):
        pass


class MockPG():

    @staticmethod
    def fetch_data(conn, sql_command: str):
        return mock_emails

    @staticmethod
    def create_connection():
        return MockConn()


class TestSuite():

    @patch('service.routes.emails.PG', MockPG)
    def test_get_emails(self):
        emails = em.get_emails()
        assert emails == ['a', 'b']

    @patch('service.routes.emails.get_emails', lambda: 'a')
    def test_lambda_handler_get(self):
        resp = em.lambda_handler({'httpMethod': 'GET'}, {})
        assert resp == ut.webify_output({'Emails': 'a'})

    @patch('service.routes.emails.add_email_address', lambda x: True)
    def test_lambda_handler_POST(self):
        resp = em.lambda_handler(
            {
                'httpMethod': 'POST',
                'body': '{"email": "a"}'
            },
            {}
        )
        assert resp == ut.webify_output("Added a")

    @patch('service.routes.emails.add_email_address', lambda x: True)
    def test_lambda_handler_bad_request(self):
        resp = em.lambda_handler(
            {
                'httpMethod': 'POST',
                'body': '{"not_email": "a"}'
            },
            {}
        )
        assert resp == ut.webify_output("Must include 'email' in request body", 400)

    @patch('service.routes.emails.remove_email_address', lambda x: True)
    def test_lambda_handler_DELETE(self):
        resp = em.lambda_handler(
            {
                'httpMethod': 'DELETE',
                'body': '{"email": "your_email"}'
            },
            {}
        )
        assert resp == ut.webify_output("Removed your_email from subscribers list")
