import os

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row

load_dotenv()

app = FastAPI(
    title="Stock Data API",
    description="Summary of stored AAPL stock data across daily, 5 minute and 1 minute intervals.",
)

summary_sql = """
    SELECT
        stock_code,
        interval_time,
        count(*) AS ticker_points,
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


@app.get("/summary")
def get_summary():
    try:
        connection = psycopg.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    except psycopg.Error as e:
        raise HTTPException(500, f"DB connection failed: {type(e).__name__}: {e}")

    with connection as conn:
        try:
            with conn.cursor(row_factory=dict_row) as cur:
                # fetch data
                cur.execute(summary_sql)
                rows = cur.fetchall()
                conn.commit()

        except psycopg.Error:
            # error = f"{type(e).__name__}: {e}"  # Capture error message
            raise HTTPException(404, "no stock data found")

    return rows
