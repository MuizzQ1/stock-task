import polars as pl


def dt_conv(df, date, interval):
    df = df.with_columns(
        pl.col(date).dt.convert_time_zone("America/New_York").dt.replace_time_zone(None)
    )

    if date == "Datetime":
        df = df.rename({"Datetime": "Date"})

    df = df.with_columns(pl.lit(interval).alias("Interval"))

    return df
