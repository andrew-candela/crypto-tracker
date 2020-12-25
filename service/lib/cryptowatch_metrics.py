from service import METRIC_URL, LOG_LEVEL, DIMENSION_NAME
import requests
from typing import Dict, List
import logging


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def get_cryptowatch_metrics() -> List[Dict[str, int]]:
    resp = requests.get(METRIC_URL)
    resp.raise_for_status()
    logger.info(f"CryptoWatch quota remaining: {resp.json()['allowance']['remaining']}")
    data = resp.json()['result']
    return [
        {DIMENSION_NAME: market, 'price': price}
        for (market, price) in data.items()
    ]
