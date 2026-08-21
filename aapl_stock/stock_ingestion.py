import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import polars as pl
import yfinance as yf
from dateutil.relativedelta import relativedelta

from .helper import col_processing, dt_conv

logger = logging.getLogger(__name__)


class StockIngestion:
    """
    Pull Stock Data from Yahoo Finance API and return a Polars DataFrame with the following columns:
    - date: The date of the stock data
    - stock_open: The opening price of the stock
    - stock_high: The highest price of the stock
    - stock_low: The lowest price of the stock
    - stock_close: The closing price of the stock
    - stock_volume: The volume of the stock traded
    - interval: The interval of the stock data (1d, 5m, 1m)
    """

    def __init__(self, ticker="AAPL"):
        # Predefine the ticker symbol for Apple
        self.aapl = yf.Ticker(ticker)

    def stock_data_refresh(self):
        """
        Create polars df which spans multiple intervals of stock data for the last 5 years.

        No overlapping data is pulled.
        Returns data in a single polars df.
        """

        # Define the date range for the last 5 years
        _end_1m_ = datetime.now(ZoneInfo("America/New_York")).date()
        _start_1m = _end_1m_ - relativedelta(days=8)

        # Define the date range for the 5 minute intervals
        _end_5m_ = _start_1m
        _start_5m = _end_5m_ - relativedelta(days=51)

        # Define the date range for the last 1 minute intervals
        _end_1d_ = _start_5m
        _start_1d = _end_1d_ - relativedelta(years=5)

        aapl_df_day = pl.DataFrame(
            self.aapl.history(
                start=_start_1d, end=_end_1d_, interval="1d"
            ).reset_index()
        )
        logger.info("Retrieved daily stock data")
        logger.info("Daily data range:")
        logger.info(f"Start: {aapl_df_day['Date'].min()}")
        logger.info(f"End: {aapl_df_day['Date'].max()}")

        aapl_df_5m = pl.DataFrame(
            self.aapl.history(
                start=_start_5m, end=_end_5m_, interval="5m"
            ).reset_index()
        )

        logger.info("Retrieved 5-minute stock data")
        logger.info("5-minute data range:")
        logger.info(f"Start: {aapl_df_5m['Datetime'].min()}")
        logger.info(f"End: {aapl_df_5m['Datetime'].max()}")

        aapl_df_1m = pl.DataFrame(
            self.aapl.history(
                start=_start_1m, end=_end_1m_, interval="1m"
            ).reset_index()
        )

        logger.info("Retrieved 1-minute stock data")
        logger.info("1-minute data range:")
        logger.info(f"Start: {aapl_df_1m['Datetime'].min()}")
        logger.info(f"End: {aapl_df_1m['Datetime'].max()}")

        tables = [
            (aapl_df_day, "Date", "1d"),
            (aapl_df_5m, "Datetime", "5m"),
            (aapl_df_1m, "Datetime", "1m"),
        ]

        tables_cln = []
        for table, date_col, interval in tables:
            _t = dt_conv(table, date_col)
            _t = col_processing(_t, interval)
            tables_cln.append(_t)

        aapl_df_all = pl.concat(tables_cln)

        return aapl_df_all
