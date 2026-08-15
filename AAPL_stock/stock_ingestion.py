import polars as pl
import yfinance as yf
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .helper import dt_conv


class StockIngestion:
    """
    Pull Stock Data from Yahoo Finance API and return a Polars DataFrame with the following columns:
    - Date: The date of the stock data
    - Open: The opening price of the stock
    - High: The highest price of the stock
    - Low: The lowest price of the stock
    - Close: The closing price of the stock
    - Volume: The volume of the stock traded
    - Interval: The interval of the stock data (1d, 5m, 1m)
    """

    def __init__(self, ticker="AAPL"):
        # Predefine the ticker symbol for Apple
        self.aapl = yf.Ticker(ticker)

    def stock_data_refresh(self):
        """
        Create polars df which spans:
            - last 5 years of daily data
            - last 60 days of 5 minute data
            - last 7 days of 1 minute data.

        No overlapping data is pulled.
        Returns data in a single polars df.
        """

        # Define the date range for the last 5 years
        end = date.today() - timedelta(days=59)
        start = end - relativedelta(years=5)

        aapl_df_day = pl.DataFrame(
            self.aapl.history(start=start, end=end, interval="1d").reset_index()
        )

        # Define the date range for the 5 minute intervals
        last_5m = aapl_df_day["Date"].max() + relativedelta(days=1)
        end_5m = last_5m + relativedelta(days=52)

        aapl_df_5m = pl.DataFrame(
            self.aapl.history(start=last_5m, end=end_5m, interval="5m").reset_index()
        )

        # Define the date range for the last 1 minute intervals
        last_1m = aapl_df_5m["Datetime"].max() + timedelta(hours=1)
        end_1m = last_1m + timedelta(days=7)

        aapl_df_1m = pl.DataFrame(
            self.aapl.history(start=last_1m, end=end_1m, interval="1m").reset_index()
        )

        tables = [
            (aapl_df_day, "Date", "1d"),
            (aapl_df_5m, "Datetime", "5m"),
            (aapl_df_1m, "Datetime", "1m"),
        ]

        tables_cln = []
        for t, c, i in tables:
            _t = dt_conv(t, c, i)
            tables_cln.append(_t)

        aapl_df_all = pl.concat(tables_cln)

        return aapl_df_all
