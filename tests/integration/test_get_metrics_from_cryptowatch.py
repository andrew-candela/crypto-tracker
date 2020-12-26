from service.lib import cryptowatch_metrics as crm
from service import DIMENSION_NAME, CRYPTO_METRICS


def test_get_data_from_cryptowatch():
    data = crm.get_cryptowatch_metrics()
    metrics = set(CRYPTO_METRICS)
    assert len(data) > 0
    for rec in data:
        assert DIMENSION_NAME in rec
        assert metrics.issubset(set(rec.keys()))
