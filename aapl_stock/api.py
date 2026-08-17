import os
from datetime import datetime

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

load_dotenv()


class StockSummary(BaseModel):
    stock_code: str
    interval_time: str
    ticker_points: int
    first_ts: datetime
    last_ts: datetime
    days_spanned: int
    min_close: float
    max_close: float
    avg_close: float


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


@app.get("/summary", response_model=list[StockSummary])
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
