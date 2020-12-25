from service import get_metrics as gm
from service import DIMENSION_NAME
from unittest.mock import patch


mock_metrics = ['a', 'b']
mock_averages = [
    {DIMENSION_NAME: 'normal', 'a': 1, 'b': 2},
    {DIMENSION_NAME: 'alert', 'a': 2, 'b': 1.5},
]
mock_data = {
    'normal': {'a': 1, 'b': 2},
    'alert': {'a': 1, 'b': 10},
}
mock_emails = [
    {'address': 'a'},
    {'address': 'b'},
]


class MockPG():

    @staticmethod
    def fetch_data(conn, sql_command: str):
        if 'crypto.email_recipients' in sql_command:
            return mock_emails
        else:
            return mock_averages


@patch('service.get_metrics.CRYPTO_METRICS', mock_metrics)
class TestCases():

    def test_data_to_dict(self):
        input = [{DIMENSION_NAME: 'a', 'field': 'b'}]
        output = gm.data_to_dict(input)
        assert output == {
            'a': {DIMENSION_NAME: 'a', 'field': 'b'}
        }

    def test_generate_historical_sql(self):
        sql = gm.generate_historical_sql_command()
        assert sql == f"""SELECT
        {DIMENSION_NAME},
        avg(a) as a, avg(b) as b
    FROM crypto.currency_stats
    WHERE
        poll_time >= NOW() - '1 HOUR'::interval
    GROUP BY
        {DIMENSION_NAME}
    ;"""

    @patch('service.get_metrics.ALERT_THRESHOLD', 5)
    def test_compare_metrics(self):
        result = gm.compare_metrics(mock_data, mock_averages)
        assert result == {'alert': {'b': 10}}

    @patch('service.get_metrics.PG.write_dictionary_to_table')
    def test_write_metrics(self, mock_write_dict):
        gm.write_metrics('metrics', 'conn')
        mock_write_dict.assert_called_once_with('metrics', 'crypto.currency_stats', 'conn')

    @patch('service.get_metrics.PG', MockPG)
    @patch('service.get_metrics.Emailer.send_email')
    @patch('service.get_metrics.ALERT_THRESHOLD', 11)
    def test_check_alert_do_nothing(self, mock_emailer):
        gm.check_alert(mock_data, 'mock_conn', ['mock_emails'])
        mock_emailer.assert_not_called()

    @patch('service.get_metrics.PG', MockPG)
    @patch('service.get_metrics.Emailer.send_email')
    @patch('service.get_metrics.ALERT_THRESHOLD', 5)
    def test_check_alert_send_alert(self, mock_emailer):
        gm.check_alert(mock_data, 'mock_conn', ['mock_emails'])
        mock_emailer.assert_called_once_with({'alert': {'b': 10}}, ['mock_emails'])

    @patch('service.get_metrics.PG', MockPG)
    def test_fetch_email_recipients(self):
        emails = gm.fetch_email_recipients('mock_conn')
        assert emails == ['a', 'b']
