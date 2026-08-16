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

    return (dt_conv,)


@app.cell
def _(aapl, date, dt_conv, pl, relativedelta, timedelta):
    end = date.today() - timedelta(days=59)
    start = end - relativedelta(years=5)

    aapl_df_day = pl.DataFrame(
        aapl.history(start=start, end=end, interval="1d").reset_index()
    )

    last_5m = aapl_df_day["Date"].max() + relativedelta(days=1)
    end_5m = last_5m + relativedelta(days=52)

    aapl_df_5m = pl.DataFrame(
        aapl.history(start=last_5m, end=end_5m, interval="5m").reset_index()
    )

    last_1m = aapl_df_5m["Datetime"].max() + timedelta(hours=1)
    end_1m = last_1m + timedelta(days=7)

    aapl_df_1m = pl.DataFrame(
        aapl.history(start=last_1m, end=end_1m, interval="1m").reset_index()
    )

    tables = [(aapl_df_day, "Date"), (aapl_df_5m, "Datetime"), (aapl_df_1m, "Datetime")]

    tables_cln = []
    for t, c in tables:
        _t = dt_conv(t, c)
        tables_cln.append(_t)

    aapl_df_all = pl.concat(tables_cln)
    return (aapl_df_all,)


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
    - Logging
    - Docker container

    # Good to share:
    - Dividend/split adjustment, error rates with opening & closing times, api data is only up until day before
    - Connectivity security
    - pyscopg dependency (binary vs non binary)
    - Creating AAPL package and pulling code in sibling directories -> toml backend code
    - Store redundnat data vs spreed of data return to user
    - One bad str instead of int in polars df will cause whole polars schema for a col to become invalid -> makes pydantic validation all rows return error for one bad row.
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
    from dotenv import load_dotenv
    import os
    load_dotenv() 
    return


@app.cell
def _():
    import psycopg

    return


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


if __name__ == "__main__":
    app.run()
