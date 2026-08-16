import logging
import os

import psycopg
from dotenv import load_dotenv

from .validation import validate_stock_data

logger = logging.getLogger(__name__)


class postgress_ingestion:
    def __init__(self):

        load_dotenv()

        self.stocks_sql = """
            INSERT INTO stocks
                (stock_code, interval_time, ts, stock_open, stock_high, stock_low, stock_close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (stock_code, interval_time, ts)
            DO UPDATE SET
                stock_open  = EXCLUDED.stock_open,
                stock_high  = EXCLUDED.stock_high,
                stock_low   = EXCLUDED.stock_low,
                stock_close = EXCLUDED.stock_close,
                volume      = EXCLUDED.volume,
                ingested_at = now();
        """

        self.observation_sql = """
            INSERT INTO observation
                (rows_upserted, error, status)
            VALUES (%s, %s, %s);
        """

        self.host = os.getenv("DB_HOST")
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    def refresh(self, df):

        # Connect to the Stocks PostgreSQL database
        try:
            connection = psycopg.connect(
                host=self.host,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
            )
        except psycopg.Error as e:
            logger.error(f"Error connecting to the database: {e}")
            return

        rows_upserted = 0
        status = "success"
        error = None

        rows = df.to_dicts()

        # Validate the data using the Pydantic model
        valid_rows = validate_stock_data(rows)

        # Connect to stock DB using defined connectio
        with connection as conn:
            try:
                with conn.cursor() as cur:
                    # open a cursor to perform database operations
                    cur.executemany(self.stocks_sql, valid_rows)
                    conn.commit()
                    logger.info("Data upserted successfully")

                rows_upserted = len(valid_rows)
                logger.info(f"Rows upserted: {rows_upserted}")

            except psycopg.Error as e:
                conn.rollback()  # Keep connection healthy
                status = "failed"
                error = f"{type(e).__name__}: {e}"  # Capture error message
                logger.error(f"Error upserting data, {error}")

            # Log postgres uplaod into observation table
            with conn.cursor() as cur:
                cur.execute(
                    self.observation_sql,
                    (rows_upserted, error, status),
                )
                conn.commit()
