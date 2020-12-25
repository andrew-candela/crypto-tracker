"""Queries https://api.livecoin.net/exchange/ticker
to get crypto metrics every minute and update a DB
The intent here is to run this as a scheduled lambda function.
"""

import logging
from service.lib.pg import PG, RealDictRow, connection
from service.lib.email import Emailer
from service.lib.cryptowatch_metrics import get_cryptowatch_metrics
from service import LOG_LEVEL, CRYPTO_METRICS, ALERT_THRESHOLD, DIMENSION_NAME
from typing import List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


def data_to_dict(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {rec[DIMENSION_NAME]: rec for rec in data}


def generate_historical_sql_command():
    averages = ", ".join([f"avg({metric}) as {metric}" for metric in CRYPTO_METRICS])
    sql_command = f"""SELECT
        {DIMENSION_NAME},
        {averages}
    FROM crypto.currency_stats
    WHERE
        poll_time >= NOW() - '1 HOUR'::interval
    GROUP BY
        {DIMENSION_NAME}
    ;"""
    return sql_command


# This will be the logic to satisfy requirement 3
# I'll loop through each metric in each record of data
# and then compare if to the average of the last hour.
# The time complexity is O(#metrics * #records).
# It would be best to vectorize this operation on the next go.
# For now it runs fast enough since there are about 10 metrics and 1000 records
def compare_metrics(data_dict: Dict[str, Any],
                    averages: List[RealDictRow]) -> Dict[str, Any]:
    logger.debug(f"comparing {len(averages)} average records to {len(data_dict)} recent records")
    anomolous_metrics = defaultdict(dict)
    for average_rec in averages:
        symbol = average_rec[DIMENSION_NAME]
        for metric in CRYPTO_METRICS:
            try:
                # many metrics are often 0 or close to it
                if average_rec[metric] > .00001 and \
                  float(average_rec[metric]) * float(ALERT_THRESHOLD) < data_dict[symbol][metric]:
                    anomolous_metrics[symbol][metric] = float(data_dict[symbol][metric])
                    logger.debug(
                        f"{DIMENSION_NAME}:{symbol} metric: {metric} average last hr: "
                        f"{average_rec[metric]}  current value: {data_dict[symbol][metric]}"
                    )
            except TypeError as e:
                logger.exception(
                    f"metric: {metric}\naverage_rec:\n{average_rec}"
                    f"\naverage_rec[metric]: {average_rec[metric]}"
                )
                raise e
    return anomolous_metrics


def write_metrics(metrics, conn: connection) -> None:
    logger.info(f"Writing {len(metrics)} metrics to postgres...")
    PG.write_dictionary_to_table(metrics, "crypto.currency_stats", conn)


def check_alert(metrics, conn: connection, emails: List[str]):
    logger.info("checking for alert conditions..")
    sql_command = generate_historical_sql_command()
    averages = PG.fetch_data(conn, sql_command)
    alertable_metrics = compare_metrics(metrics, averages)
    print(alertable_metrics)
    if alertable_metrics:
        em = Emailer()
        em.send_email(alertable_metrics, emails)
        return None
    logger.info("Found 0 records worthy of an alert")


def fetch_email_recipients(conn: connection) -> List[str]:
    recs = PG.fetch_data(conn, "SELECT address FROM crypto.email_recipients;")
    return [rec['address'] for rec in recs]


def lambda_handler(event={}, context={}) -> None:
    metrics = get_cryptowatch_metrics()
    data_dict = data_to_dict(metrics)
    logger.info("writing metrics to DB")
    with PG.create_connection() as conn:
        write_metrics(metrics, conn)
        email_recipients = fetch_email_recipients(conn)
        check_alert(data_dict, conn, email_recipients)


if __name__ == "__main__":
    lambda_handler()
