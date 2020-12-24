from service.routes import metrics as mt
from service.lib import utils as ut
from unittest.mock import patch


class TestSuite():

    def test_lambda_handler_not_get(self):
        resp = mt.lambda_handler({'httpMethod': 'POST'}, {})
        assert resp == ut.webify_output("Only GET is supported", 400)

    @patch('service.routes.metrics.fetch_metrics_and_symbols', lambda: 'mock_out')
    def test_lambda_handler_list(self):
        resp = mt.lambda_handler({'httpMethod': 'GET', 'path': '/list-metrics'}, {})
        assert resp == ut.webify_output("mock_out")

    @patch('service.routes.metrics.fetch_historical_performance', lambda x, y: "mock_hist")
    @patch('service.routes.metrics.fetch_rank', lambda x, y: "mock_rank")
    def test_lambda_handler_history_and_rank(self):
        resp = mt.lambda_handler(
            {
                'httpMethod': 'GET',
                'path': 'anything',
                'queryStringParameters': {"metric": "a", "symbol": "b"}
            },
            {}
        )
        assert resp == ut.webify_output({'HistoricalData': "mock_hist", 'Rank': "mock_rank"})
