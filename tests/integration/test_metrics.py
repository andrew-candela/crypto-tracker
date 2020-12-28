from service.routes import metrics as mt
from service import get_metrics as gm
from service.lib import utils as ut
from service.lib.pg import PG
import json
import unittest

mock_metric_historical_data = [
    {"market_symbol_combo": "mk:kr:btc", "price": "123"},
    {"market_symbol_combo": "mk:kr:btc", "price": "124"},
    {"market_symbol_combo": "mk:kr:ltc", "price": "23"},
    {"market_symbol_combo": "mk:kr:ltc", "price": "124"},
]


class TestSuite(unittest.TestCase):

    def setUp(self):
        with PG.create_connection() as conn:
            gm.write_metrics(mock_metric_historical_data, conn)
            gm.cleanup(conn)

    def tearDown(self):
        sql = "DELETE FROM crypto.currency_stats"
        with PG.create_connection() as conn:
            PG.run_sql_command(conn, sql)

    def test_list_metrics(self):
        event = {
            'path': '/list-metrics',
            'httpMethod': 'GET',
        }
        out = mt.lambda_handler(event, {})
        assert out == ut.webify_output(mt.fetch_metrics_and_dimensions())

    def test_historical_performance(self):
        event = {
            'path': '/metrics',
            'httpMethod': 'GET',
            'queryStringParameters': {"metric": "price", "dimension": "mk:kr:ltc"}
        }
        out = mt.lambda_handler(event, {})
        data_out = json.loads(out['body'])
        assert set([rec['price'] for rec in data_out['HistoricalData']]) == {124, 23}
        assert data_out['Rank'] == '1/2'

    def test_historical_performance_bad_params(self):
        event = {
            'path': '/metrics',
            'httpMethod': 'GET',
            'queryStringParameters': {"dimension": "mk:kr:ltc", "missing_metric": "anything"}
        }
        out = mt.lambda_handler(event, {})
        assert out['statusCode'] == 400

    def test_historical_performance_bad_method(self):
        event = {
            'path': '/metrics',
            'httpMethod': 'POST',
        }
        out = mt.lambda_handler(event, {})
        assert out['statusCode'] == 400

    def test_historical_performance_bad_metric(self):
        event = {
            'path': '/metrics',
            'httpMethod': 'GET',
            'queryStringParameters': {"metric": "bad_metric", "dimension": "mk:kr:ltc"}
        }
        out = mt.lambda_handler(event, {})
        assert out['statusCode'] == 400
