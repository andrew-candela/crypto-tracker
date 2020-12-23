"""Provides a high level SQL interface for running queries in PG."""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extras import RealDictRow
from psycopg2.extensions import connection
import os
import logging
from typing import List, Dict, Any
from service import LOG_LEVEL


logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


class PG():

    @staticmethod
    def create_connection() -> connection:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            port=os.getenv("PG_PORT")
        )
        return conn

    @staticmethod
    def execute_sql_file(sql_file: str, conn: connection) -> None:
        with conn.cursor() as cursor:
            sql_command = open(sql_file, "r").read()
            logger.debug(f"running SQL command:\n{sql_command}")
            cursor.execute(sql_command)
            conn.commit()

    @staticmethod
    def write_dictionary_to_table(data: List[Dict[str, Any]], table: str,
                                  conn: connection) -> None:
        if not data:
            return None
        # This is dangerous as it depends on the same columns being in each record
        cols = data[0].keys()
        col_string = ",".join(cols)
        val_list = [f"%({col})s" for col in cols]
        val_string = ",".join(val_list)
        insert_sql = f"INSERT INTO {table} ({col_string}) values ({val_string})"

        with conn.cursor() as cursor:
            cursor.executemany(insert_sql, data)
            conn.commit()

    @staticmethod
    def fetch_data(conn: connection, sql_command: str) -> List[RealDictRow]:
        logger.debug(f"running:\n{sql_command}")
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql_command)
            records = cursor.fetchall()
        return records
