from datetime import datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field

Interval = Literal["1m", "5m", "1d"]


class StockData(BaseModel):
    """
    Pydantic Base Model for stock data.
    - Assert that stock_code is always uppercase.
    - Assert that interval_time is oone of the predefined intervals.
    - Assert that stock_open, stock_high, stock_low, stock_close are all positive floats.
    """

    stock_code: Annotated[str, AfterValidator(str.upper)]
    interval_time: Interval
    ts: datetime
    stock_open: Annotated[float, Field(gt=0)]
    stock_high: Annotated[float, Field(gt=0)]
    stock_low: Annotated[float, Field(gt=0)]
    stock_close: Annotated[float, Field(gt=0)]
    volume: Annotated[int, Field(ge=0)]


class StockSummary(BaseModel):
    """
    Pydantic Base Model for stock summary data.
    """

    stock_code: str
    interval_time: str
    data_points: int
    first_ts: datetime
    last_ts: datetime
    days_spanned: int
    min_close: float
    max_close: float
    avg_close: float
