import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    from datetime import date, timedelta, datetime, timezone

    import marimo as mo
    import polars as pl
    import yfinance as yf
    from dateutil.relativedelta import relativedelta

    return date, datetime, mo, pl, relativedelta, timedelta, timezone, yf


@app.cell
def _(yf):
    aapl = yf.Ticker("AAPL")
    return (aapl,)


@app.cell
def _(pl):
    def dt_conv(df, date):
        df = df.with_columns(
            pl.col(date)
            .dt.convert_time_zone("America/New_York")
            .dt.replace_time_zone(None)
        )

        if date == "Datetime":
            df = df.rename({"Datetime": "Date"})

        return df

    return


@app.cell
def _(aapl, date, pl, relativedelta, timedelta):
    end = date.today() - timedelta(days=59)
    start = end - relativedelta(years=5)
    print(end)

    aapl_df_day = pl.DataFrame(
        aapl.history(start=start, end=end, interval="1d").reset_index()
    )

    aapl_df_day['Date'].max()

    last_5m = end + relativedelta(days=1)
    print(last_5m)
    end_5m = last_5m + relativedelta(days=52)
    print(end_5m)

    aapl_df_5m = pl.DataFrame(
        aapl.history(start=last_5m, end=end_5m, interval="5m").reset_index()
    )

    last_1m = end_5m + timedelta(days=1)
    end_1m = last_1m + timedelta(days=6)
    print(last_1m)
    print(end_1m)

    aapl_df_1m = pl.DataFrame(
        aapl.history(start=last_1m, end=end_1m, interval="1m").reset_index()
    )

    # tables = [(aapl_df_day, "Date"), (aapl_df_5m, "Datetime"), (aapl_df_1m, "Datetime")]

    # tables_cln = []
    # for t, c in tables:
    #     _t = dt_conv(t, c)
    #     tables_cln.append(_t)

    # aapl_df_all = pl.concat(tables_cln)
    aapl_df_1m
    return


@app.cell
def _(aapl):
    aapl.history(period="8d", interval="1m")
    return


@app.cell
def _(aapl, date, pl, relativedelta):
    _end_1m_ = date.today()
    _start_1m = _end_1m_ - relativedelta(days=8)

    _end_5m_ = _start_1m
    _start_5m = _end_5m_ - relativedelta(days=51)

    _end_1d = _start_5m
    _start_1d = _end_1d - relativedelta(years=5)

    _df= pl.DataFrame(
        aapl.history(start=_start_5m, end=_end_5m_, interval="5m").reset_index()
    )

    _df
    return


@app.cell
def _(aapl_df_all):
    aapl_df_all
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        -- SELECT * 
        -- FROM aapl_df_1m_cln
        -- WHERE Datetime >= TIMESTAMP '2026-08-13 00:00:00' AND
        -- Datetime <= TIMESTAMP '2026-08-16 00:00:00'
        -- ORDER BY Datetime ASC
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # TODO:

    - Pydantic Schema validation [DONE]
    - Logging [DONE] - CAVEAT: Log error rows (INVLAID ROWS) somewhere on failure rows
    - Unit test [DONE] - CAVEAT: test for DB (test DB)
    - Docker

    TESTS:
    - Error rows (AI automation)
    - Create new tables for testing
    - Dupicate unique key data

    # Good to share:
    - Dividend/split adjustment, error rates with opening & closing times, api data is only up until day before
    - Connectivity security
    - pyscopg dependency (binary vs non binary)
    - Creating AAPL package and pulling code in sibling directories -> toml backend code
    - Store redundnat data vs spreed of data return to user
    - One bad str instead of int in polars df will cause whole polars schema for a col to become invalid -> makes pydantic validation all rows return error for one bad row.
    - Extra tests (high being higher than low assertion)
    - API memory
    - Connection per request
    - Linting catching errors: date.today() -> prod issues
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Test Py Script
    """)
    return


@app.cell
def _():
    from aapl_stock import StockIngestion

    return (StockIngestion,)


@app.cell
def _(StockIngestion):
    st = StockIngestion()
    return (st,)


@app.cell
def _(st):
    df_stocks = st.stock_data_refresh()
    df_stocks
    return (df_stocks,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Postgres DB connection
    """)
    return


@app.cell
def _():
    import psycopg

    return (psycopg,)


@app.cell
def _(df_stocks):
    rows = []
    # Itertae over each row as a dict
    for r in df_stocks.iter_rows(named=True):
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
    return


@app.cell
def _():
    SQL_upload = """
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
    return


@app.cell
def _():
    # connection = psycopg.connect(
    #             host=os.getenv("DB_HOST"),
    #             dbname=os.getenv("DB_NAME"),
    #             user=os.getenv("DB_USER"),
    #             password=os.getenv("DB_PASSWORD")
    #         )
    # with connection as conn:

    #     # Open a cursor to perform database operations
    #     with conn.cursor() as cur:

    #         cur.executemany(SQL_upload, rows)
    #         conn.commit()
    return


@app.cell
def _(datetime, timezone):
    datetime.now(timezone.utc).replace(tzinfo=None)
    return


@app.cell
def _():
    rows_upserted = 0
    status = "success"
    error = None
    return


@app.cell
def _():
    # with psycopg.connect(self.conninfo) as conn:
    #     try:
    #         with conn.cursor() as cur:
    #             cur.executemany(self.sql, rows)
    #             conn.commit()
    #         rows_upserted = len(rows)

    #     except Exception as e:
    #         conn.rollback() # Rollback connection to previous connection 
    #         status = "failed"
    #         error = f"{type(e).__name__}: {e}"

    #     with conn.cursor() as cur:
    #         cur.execute(
    #             self.observation_sql,
    #             (rows_upserted, error, status),
    #         )
    #         conn.commit()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Pydantic Assertion
    """)
    return


@app.cell
def _():
    from aapl_stock import StockData
    from pydantic import ValidationError

    return


@app.cell
def _(df_stocks):
    rows_new = []

    # Iterate over each row in polars df as a dict
    for _r in df_stocks.iter_rows(named=True):

        rows_new.append(_r)
    return (rows_new,)


@app.cell
def _(rows_new):
    o = rows_new[0]
    o['stock_low'] = None
    o['volume'] = '50'
    o
    return (o,)


@app.cell
def _(o, rows_new):
    test_rows = [
        o,rows_new[1], rows_new[2]
    ]
    return (test_rows,)


@app.cell
def _(pl, test_rows):
    test_df = pl.DataFrame(test_rows)
    return (test_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Test validation
    """)
    return


@app.cell
def _():
    from aapl_stock import validate_stock_data

    return (validate_stock_data,)


@app.cell
def _(test_df, validate_stock_data):
    v_rows = validate_stock_data(test_df.to_dicts())
    return (v_rows,)


@app.cell
def _(test_rows):
    test_rows
    return


@app.cell
def _(v_rows):
    v_rows
    return


@app.cell
def _(test_df):
    from aapl_stock import postgress_ingestion
    db_ingest = postgress_ingestion()
    db_ingest.refresh(df=test_df)
    return (postgress_ingestion,)


@app.cell
def _(StockIngestion, postgress_ingestion):
    _st = StockIngestion()
    _df_stocks = _st.stock_data_refresh()

    _db_ingest = postgress_ingestion()
    _db_ingest.refresh(df=_df_stocks)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Unit Testsing
    """)
    return


@app.cell
def _():
    import pytest

    def make_row(**overrides):
        """Single row of valid stock data with overrides for testing"""

        row = {
            "stock_code": "AAPL",
            "interval_time": "1d",
            "ts": "2026-01-02T00:00:00-05:00",
            "stock_open": 185.0,
            "stock_high": 190.0,
            "stock_low": 184.0,
            "stock_close": 188.0,
            "volume": 50_000_000,
        }
        row.update(overrides)
        return [row]

    return (make_row,)


@app.cell
def _(make_row, validate_stock_data):
    def test_valid_row_passes():
        valid, rejected = validate_stock_data(make_row())
        assert len(valid) == 1
        assert rejected == []


    def test_null_price_rejected():
        valid, rejected = validate_stock_data(make_row(stock_close=None))
        assert valid == []
        assert len(rejected) == 1


    def test_string_in_volume_rejected():
        valid, rejected = validate_stock_data(make_row(volume="not_a_number"))
        assert valid == []
        assert len(rejected) == 1


    def test_negative_price_rejected():
        valid, rejected = validate_stock_data(make_row(stock_open=-5.0))
        assert valid == []
        assert len(rejected) == 1


    def test_invalid_interval_rejected():
        valid, rejected = validate_stock_data(make_row(interval_time="5min"))
        assert valid == []
        assert len(rejected) == 1

    def test_partial_batch_keeps_good_rows():
        """Test batch with valid and invalid rows. Only valid rows should be returned."""
        rows = make_row() + make_row(stock_open=-1.0) + make_row(ts="2026-01-03T00:00:00-05:00")
        valid, rejected = validate_stock_data(rows)
        assert len(valid) == 2
        assert len(rejected) == 1

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SQL testing
    """)
    return


@app.cell
def _():
    from dotenv import load_dotenv
    import os
    load_dotenv() 
    import sqlalchemy

    url = sqlalchemy.URL.create(
        "postgresql+psycopg",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=5432,
        database=os.environ["DB_NAME"],
    )
    engine = sqlalchemy.create_engine(url)
    return engine, os


@app.cell
def _(engine, mo, stocks):
    _df = mo.sql(
        f"""
        WITH dates as (
        SELECT 
            *,
            ROW_NUMBER() OVER(PARTITION BY DATE(ts) ORDER BY ts DESC) AS rn
        FROM STOCKS
        WHERE ts BETWEEN DATE('2026-08-01') AND DATE('2026-08-15') 
        ORDER BY ts
        )

        SELECT *
        FROM dates
        -- where rn = 1
        """,
        engine=engine
    )
    return


@app.cell
def _(engine, mo, stocks):
    _df = mo.sql(
        f"""
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
        """,
        engine=engine
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Fetch data test
    """)
    return


@app.cell
def _():
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
    return (summary_sql,)


@app.cell
def _(os, psycopg, summary_sql):
    from psycopg.rows import dict_row

    connection = psycopg.connect(

    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    )

    with connection as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(summary_sql)
            rows_n = cur.fetchall()
            conn.commit()
    return (rows_n,)


@app.cell
def _(rows_n):
    rows_n
    return


if __name__ == "__main__":
    app.run()
