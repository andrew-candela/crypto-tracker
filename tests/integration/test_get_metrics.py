from service import get_metrics as gm
from service.lib.pg import PG
import unittest
from unittest.mock import patch


mock_metric_historical_data = [
    {"market_symbol_combo": "should_not_alert", "price": 123},
    {"market_symbol_combo": "should_not_alert", "price": 124},
    {"market_symbol_combo": "should_alert", "price": 23},
    {"market_symbol_combo": "should_alert", "price": 124},
    {"market_symbol_combo": "should_alert", "price": 124},
    {"market_symbol_combo": "just_shy_of_alert", "price": 124},
]

mock_metric_current_data = [
    {"market_symbol_combo": "should_not_alert", "price": 123},
    {"market_symbol_combo": "should_alert", "price": 1530},
    {"market_symbol_combo": "just_shy_of_alert", "price": 1239},
]


class TestSuite(unittest.TestCase):

    def setUp(self):
        with PG.create_connection() as conn:
            gm.write_metrics(mock_metric_historical_data, conn)
            PG.write_dictionary_to_table(
                [{"address": 'test@email.com'}],
                "crypto.email_recipients",
                conn
            )

    def tearDown(self):
        with PG.create_connection() as conn:
            PG.run_sql_command(conn, "DELETE FROM crypto.currency_stats")
            PG.run_sql_command(conn, "DELETE FROM crypto.email_recipients")

    @patch('service.get_metrics.get_cryptowatch_metrics', lambda: mock_metric_current_data)
    @patch('service.get_metrics.write_metrics', lambda x, y: None)
    @patch('service.get_metrics.ALERT_THRESHOLD', 10)
    @patch('service.get_metrics.Emailer')
    def test_alert(self, mock_emailer):
        gm.lambda_handler()
        mock_emailer.send_email.assert_called_once_with(
            {'should_alert': {'price': 1530}},
            ['test@email.com']
        )
