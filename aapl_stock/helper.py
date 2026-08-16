import polars as pl


def dt_conv(df, date):
    df = df.with_columns(
        pl.col(date).dt.convert_time_zone("America/New_York").dt.replace_time_zone(None)
    )

    if date == "Datetime":
        df = df.rename({"Datetime": "Date"})

    return df


def col_processing(df, interval):

    df = df.with_columns(
        pl.lit(interval).alias("interval_time"), pl.lit("AAPL").alias("stock_code")
    )

    df = df.rename(
        {
            "Date": "ts",
            "Open": "stock_open",
            "High": "stock_high",
            "Low": "stock_low",
            "Close": "stock_close",
            "Volume": "volume",
        }
    )

    df = df.drop(["Dividends", "Stock Splits"])

    return df
