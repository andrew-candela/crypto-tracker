"""This will be responsible for returning the historical data for a given metric.
I'll return a list with sorted records for historical performance and also I'll
return the 'rank'.
Rank is computed by computing the standard deviation of the metric over all currencies
(dimensions) in the last 24 hrs and ordering the results"""

from service.lib.pg import PG, RealDictRow
from service.lib import utils as ut
from service import LOG_LEVEL, CRYPTO_METRICS, DIMENSION_NAME
import json
from typing import List, Dict, Any
import logging


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def fetch_metrics_and_dimensions() -> Dict[str, Any]:
    sql_command = f"SELECT DISTINCT {DIMENSION_NAME} FROM crypto.currency_stats"
    with PG.create_connection() as conn:
        unique_dimensions = PG.fetch_data(conn, sql_command)
    out_dict = {
        "dims": unique_dimensions,
        "available_metrics": CRYPTO_METRICS
    }
    return out_dict


def fetch_historical_performance(metric: str, dimension: str) -> List[RealDictRow]:
    sql_historical = f"""SELECT
            poll_time,
            {metric}
        FROM
            crypto.currency_stats
        WHERE
            {DIMENSION_NAME} = '{dimension}'
            AND poll_time >= NOW() - '1 DAY'::interval
        ;"""
    with PG.create_connection() as conn:
        hist_data = PG.fetch_data(conn, sql_historical)
    return list(map(PG.stringify_sql_output, hist_data))


def fetch_rank(metric: str, dimension: str) -> str:
    sql_rank = f"""SELECT
        {DIMENSION_NAME} as dimension,
        stddev({metric}) as {metric}_stddev
    FROM
        crypto.currency_stats
    WHERE
        poll_time >= NOW() - '1 DAY'::interval
    GROUP BY
        {DIMENSION_NAME}
    ORDER BY stddev({metric}) DESC
    ;"""
    with PG.create_connection() as conn:
        stdev_ranks = PG.fetch_data(conn, sql_rank)
    logger.debug(f"found some stddev ranks:\n {stdev_ranks[:5]}")
    num_dimensions = len(stdev_ranks)
    found_position = -1
    position = 0
    for record in stdev_ranks:
        position += 1
        if record['dimension'] == dimension:
            found_position = position
            break
    if found_position == -1:
        logger.exception("You are looking for a dimension that doesn't exist "
                         "in the last 24 hours")
    return f"{found_position}/{num_dimensions}"


def lambda_handler(event: {}, context: {}) -> str:
    if event['httpMethod'] != 'GET':
        return ut.webify_output("Only GET is supported", 400)
    if event['path'] == '/list-metrics':
        # return list of available metrics and dimensions
        output = fetch_metrics_and_dimensions()
        return ut.webify_output(output)
    params = ut.parse_path_parameters(event)
    # give historical and rank
    if 'metric' not in params or 'dimension' not in params:
        return ut.webify_output("Must supply both 'metric' AND 'dimension' as path params", 400)
    historical_data = fetch_historical_performance(params['metric'], params['dimension'])
    rank = fetch_rank(params['metric'], params['dimension'])
    output = {'HistoricalData': historical_data, 'Rank': rank}
    return ut.webify_output(output)


if __name__ == "__main__":
    event = {
        'path': '/list-metrics',
        'httpMethod': 'GET',
        'queryStringParameters': {"metric": "price", "dimension": "market:bitstamp:omggbp"}
    }
    print(json.dumps((lambda_handler(event, {}))))
