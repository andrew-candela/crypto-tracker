"""This will be responsible for returning the historical data for a given metric.
I'll return a list with sorted records for historical performance and also I'll
return the 'rank'.
Rank is computed by computing the standard deviation of the metric over all currencies
(symbols) in the last 24 hrs and ordering the results"""

from service.lib.pg import PG, RealDictRow
from service import LOG_LEVEL
import json
from typing import List, Tuple
import logging


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def stringify_sql_output(row: RealDictRow) -> RealDictRow:
    row['poll_time'] = row['poll_time'].strftime("%s")
    return row


def fetch_historical_performance(metric: str, symbol: str) -> List[RealDictRow]:
    sql_historical = f"""SELECT
            poll_time,
            {metric}
        FROM
            crypto.currency_stats
        WHERE
            symbol = '{symbol}'
            AND poll_time >= NOW() - '1 DAY'::interval
        ;"""
    with PG.create_connection() as conn:
        hist_data = PG.fetch_data(conn, sql_historical)
    return list(map(stringify_sql_output, hist_data))


def fetch_rank(metric: str, symbol: str) -> Tuple[int]:
    sql_rank = f"""SELECT
        symbol,
        stddev({metric}) as {metric}_stddev
    FROM
        crypto.currency_stats
    WHERE
        poll_time >= NOW() - '1 DAY'::interval
    GROUP BY
        symbol
    ORDER BY stddev({metric}) DESC
    ;"""
    with PG.create_connection() as conn:
        stdev_ranks = PG.fetch_data(conn, sql_rank)
    logger.debug(f"found some stddev ranks:\n {stdev_ranks[:5]}")
    num_symbols = len(stdev_ranks)
    found_position = -1
    position = 0
    for record in stdev_ranks:
        position += 1
        if record['symbol'] == symbol:
            found_position = position
            break
    if found_position == -1:
        logger.exception("You are looking for a symbol that doesn't exist "
                         "in the last 24 hours")
    return (found_position, num_symbols)


def lambda_handler(event: {}, context: {}) -> str:
    historical_data = fetch_historical_performance(event['metric'], event['symbol'])
    (rank, total) = fetch_rank(event['metric'], event['symbol'])
    return json.dumps({
        "historical_data": historical_data,
        "rank": f"{rank}/{total}"
    })


if __name__ == "__main__":
    print(lambda_handler({'symbol': 'TGAME/USDT', 'metric': 'best_bid'}, {}))
