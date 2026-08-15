import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import yfinance as yf
    import polars as pl
    from datetime import datetime, date, timedelta, timezone
    from dateutil.relativedelta import relativedelta

    return date, mo, pl, relativedelta, timedelta, yf


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

        if date == 'Datetime':
            df = df.rename({'Datetime': 'Date'})

        return df

    return (dt_conv,)


@app.cell
def _(aapl, date, dt_conv, pl, relativedelta, timedelta):
    end = date.today() - timedelta(days=59)
    start = end - relativedelta(years=5)

    aapl_df_day = pl.DataFrame(aapl.history(
        start=start,
        end=end, 
        interval="1d").reset_index())

    last_5m = aapl_df_day['Date'].max() + relativedelta(days=1)
    end_5m = last_5m + relativedelta(days=52)

    aapl_df_5m = pl.DataFrame(aapl.history(
        start = last_5m,
        end = end_5m,
        interval="5m").reset_index())

    last_1m = aapl_df_5m['Datetime'].max()+timedelta(hours=1)
    end_1m = last_1m + timedelta(days=7)

    aapl_df_1m = pl.DataFrame(aapl.history(
        start = last_1m,
        end=end_1m,
        interval="1m").reset_index())

    tables = [
        (aapl_df_day, 'Date'),
        (aapl_df_5m, 'Datetime'),
        (aapl_df_1m, 'Datetime')
    ]

    tables_cln = []
    for t, c in tables:
        _t = dt_conv(t,c)
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

    - Extract data sequentially using current datetime
    - Package into a rerun python class/method
    - Remove overlapping data (should be solved by sequential step)

    # Good to share:
    - Dividend/split adjustment, error rates with opening & closing times, api data is only up until day before
    - Connectivity security
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
    from AAPL_stock import StockIngestion

    return (StockIngestion,)


@app.cell
def _(StockIngestion):
    st = StockIngestion()
    return (st,)


@app.cell
def _(st):
    st.stock_data_refresh()
    return


if __name__ == "__main__":
    app.run()
