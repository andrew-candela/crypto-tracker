from service.lib import cryptowatch_metrics as cm
from service import DIMENSION_NAME
from unittest.mock import patch


class MockResponse():

    def raise_for_status(self):
        return None

    def json(self):
        return {
            'result': {'a': 1, 'b': 2},
            'allowance': {'remaining': 10}
        }


class MockRequests():

    @staticmethod
    def get(url: str):
        return MockResponse()


@patch('service.lib.cryptowatch_metrics.requests', MockRequests)
def test_get_cryptowatch_metrics():
    data = cm.get_cryptowatch_metrics()
    assert data == [
        {DIMENSION_NAME: 'a', 'price': 1},
        {DIMENSION_NAME: 'b', 'price': 2}
    ]
