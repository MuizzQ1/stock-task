import argparse
import json
import logging
import os

import psycopg
from psycopg.rows import dict_row

logger = logging.getLogger(__name__)
from dotenv import load_dotenv

from .pipeline import run_pipeline

load_dotenv()

summary_sql = """
    SELECT
        stock_code,
        interval_time,
        count(*) AS data_points,
        min(ts) AS first_ts,
        max(ts) AS last_ts,
        max(ts)::date - min(ts)::date AS days_spanned,
        round(min(stock_close), 2) AS min_close,
        round(max(stock_close), 2) AS max_close,
        round(avg(stock_close), 2) AS avg_close
    FROM stocks
    GROUP BY stock_code, interval_time
    ORDER BY max(ts) DESC
"""


def main():

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} | {levelname:<8} | {name:<28} | {message}",
        datefmt="%H:%M:%S",
        style="{",
    )

    p = argparse.ArgumentParser(prog="aapl_stock")
    p.add_argument("cmd", choices=("ingest", "summary"))
    args = p.parse_args()

    if args.cmd == "ingest":
        logger.info("Ingest command selected")

        # Run the stock data ingestion pipeline
        run_pipeline()

    elif args.cmd == "summary":
        logger.info("Summary command selected")

        try:
            connection = psycopg.connect(
                host=os.getenv("DB_HOST"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            )

            logger.info("DB connection established successfully")

        except psycopg.Error as e:
            logger.error(f"DB connection failed: {type(e).__name__}: {e}")

        with connection as conn:
            try:
                with conn.cursor(row_factory=dict_row) as cur:
                    # fetch data
                    cur.execute(summary_sql)
                    rows = cur.fetchall()
                    conn.commit()

            except psycopg.Error as e:
                logger.error(
                    f"Error occurred while fetching summary data: {type(e).__name__}: {e}"
                )

        return print(json.dumps(rows, default=str, indent=2))

    else:
        logger.error(f"Invalid command: {args.cmd}")


if __name__ == "__main__":
    main()
