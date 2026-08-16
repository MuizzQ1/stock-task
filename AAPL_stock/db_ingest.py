import os

import psycopg
from dotenv import load_dotenv


class postgress_ingestion:
    def __init__(self):
        self.sql = """
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
        load_dotenv()

        self.host = os.getenv("DB_HOST")
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    def refresh(self, df):

        # Connect to the Stocks PostgreSQL database
        connection = psycopg.connect(
            host=self.host, dbname=self.dbname, user=self.user, password=self.password
        )

        rows = []

        # Itertae over each row in polars df as a dict
        for r in df.iter_rows(named=True):
            r_tuple = (
                r["stock_code"],
                r["interval_time"],
                r["ts"],
                r["stock_open"],
                r["stock_high"],
                r["stock_low"],
                r["stock_close"],
                r["volume"],
            )
            rows.append(r_tuple)

        # Connect to stock DB using defined connection
        # open a cursor to perform database operations
        with connection as conn, conn.cursor() as cur:
            # Upload data in a batch
            cur.executemany(self.sql, rows)
            conn.commit()
