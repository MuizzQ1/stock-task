import os

import psycopg
from dotenv import load_dotenv

from .validation import validate_stock_data


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
        connection = psycopg.connect(
            host=self.host, dbname=self.dbname, user=self.user, password=self.password
        )

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
                rows_upserted = len(valid_rows)

            except psycopg.Error as e:
                conn.rollback()  # Keep connection healthy
                status = "failed"
                error = f"{type(e).__name__}: {e}"  # Capture error message

            # Log postgres uplaod into observation table
            with conn.cursor() as cur:
                cur.execute(
                    self.observation_sql,
                    (rows_upserted, error, status),
                )
                conn.commit()
