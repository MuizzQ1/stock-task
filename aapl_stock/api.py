import logging
import os

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row

from .models import StockSummary
from .pipeline import run_pipeline

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} | {levelname:<8} | {name:<28} | {message}",
    datefmt="%H:%M:%S",
    style="{",
)

load_dotenv()

app = FastAPI(
    title="Stock Data API",
    description="""
    Summary - Summary of stored AAPL stock data across daily, 5 minute and 1 minute intervals.
    
    Ingest - Ingests AAPL stock data from Yahoo Finance and stores it in a PostgreSQL database. Data is upserted to avoid duplicates.
    """,
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

        logger.info("DB connection established successfully")

    except psycopg.Error as e:
        logger.error(f"DB connection failed: {type(e).__name__}: {e}")

        raise HTTPException(500, "DB connection failed")

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
            raise HTTPException(404, "no stock data found")

    return rows


@app.post("/ingest")
def trigger_ingest():

    logger.info("Triggering /ingest...")

    try:
        run_pipeline()
    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(500, "ingestion failed") from e
    return {"status": "success"}
