"""Queries https://api.livecoin.net/exchange/ticker
to get crypto metrics every minute and update a DB
The intent here is to run this as a scheduled lambda function.
"""

import logging
import requests
from service.lib.pg import PG, RealDictRow, connection
from service.lib.email import Emailer
from service import LOG_LEVEL, CRYPTO_METRICS, ALERT_THRESHOLD, METRIC_URL
from datetime import datetime
from typing import List, Dict, Any
import time
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def data_to_dict(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {rec['symbol']: rec for rec in data}


def generate_historical_sql_command():
    averages = ", ".join([f"avg({metric}) as {metric}" for metric in CRYPTO_METRICS])
    sql_command = f"""SELECT
        symbol,
        {averages}
    FROM crypto.currency_stats
    WHERE
        poll_time >= NOW() - '1 HOUR'::interval
    GROUP BY
        symbol
    ;"""
    return sql_command


# This will be the logic to satisfy requirement 3
# I'll loop through each metric in each record of data
# and then compare if to the average of the last hour.
# The run time is O(#metrics * #records).
# It would be best to vectorize this operation on the next go.
# For now it runs fast enough.
def compare_metrics(data_dict: Dict[str, Any],
                    averages: List[RealDictRow]) -> List[Dict[str, Any]]:
    logger.debug(f"comparing {len(averages)} average records to {len(data_dict)} recent records")
    anomolous_metrics = defaultdict(dict)
    for average_rec in averages:
        symbol = average_rec['symbol']
        for metric in CRYPTO_METRICS:
            try:
                # many metrics are often 0 or close to it
                if average_rec[metric] > .00001 and \
                  float(average_rec[metric]) * float(ALERT_THRESHOLD) < data_dict[symbol][metric]:
                    anomolous_metrics[symbol][metric] = float(average_rec[metric])
                    logger.debug(
                        f"symbol:{symbol} metric: {metric} average last hr: "
                        f"{average_rec[metric]}  current value: {data_dict[symbol][metric]}"
                    )
            except TypeError as e:
                logger.exception(
                    f"metric: {metric}\naverage_rec:\n{average_rec}"
                    f"\naverage_rec[metric]: {average_rec[metric]}"
                )
                raise e
    return anomolous_metrics


def get_utc_offset() -> int:
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    return int(offset / 60 / 60 * -1)


def get_metrics() -> List[Dict[str, Any]]:
    logger.info("getting metrics...")
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    utc_offset = get_utc_offset()
    now += f"{utc_offset}"
    metrics_payload = requests.get(METRIC_URL)
    metrics_payload.raise_for_status()
    metrics = metrics_payload.json()
    for metric in metrics:
        metric["poll_time"] = now
    return metrics


def write_metrics(metrics, conn: connection) -> None:
    logger.info(f"Writing {len(metrics)} metrics to postgres...")
    PG.write_dictionary_to_table(metrics, "crypto.currency_stats", conn)


def check_alert(metrics, conn: connection, emails: List[str]):
    logger.info("checking for alert conditions..")
    sql_command = generate_historical_sql_command()
    averages = PG.fetch_data(conn, sql_command)
    alertable_metrics = compare_metrics(metrics, averages)
    if alertable_metrics:
        em = Emailer()
        em.send_email(alertable_metrics, emails)
        return None
    logger.info("Found 0 records worthy of an alert")


def fetch_email_recipients(conn: connection) -> List[str]:
    recs = PG.fetch_data(conn, "SELECT address FROM crypto.email_recipients;")
    return [rec['address'] for rec in recs]


def lambda_handler(event={}, context={}) -> None:
    metrics = get_metrics()
    data_dict = data_to_dict(metrics)
    with PG.create_connection() as conn:
        write_metrics(metrics, conn)
        email_recipients = fetch_email_recipients(conn)
        check_alert(data_dict, conn, email_recipients)


if __name__ == "__main__":
    lambda_handler()
