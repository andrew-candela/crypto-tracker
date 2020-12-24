"""This will be responsible for returning a list of
available symbol/metric combinations to the user"""

from service.lib.pg import PG
from service import CRYPTO_METRICS
import json


def fetch_metrics_and_symbols() -> str:
    sql_command = "SELECT DISTINCT symbol FROM crypto.currency_stats"
    with PG.create_connection() as conn:
        unique_symbols = PG.fetch_data(conn, sql_command)
    out_dict = {
        "symbols": unique_symbols,
        "available_metrics": CRYPTO_METRICS
    }
    return json.dumps(out_dict)


def lambda_handler(event: {}, context: {}) -> str:
    output = fetch_metrics_and_symbols()
    response = {
        'statusCode': 200,
        'body': output
    }
    return response


if __name__ == "__main__":
    print(fetch_metrics_and_symbols())
