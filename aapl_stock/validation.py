from pydantic import ValidationError

from .models import StockData


def validate_stock_data(rows):
    """
    Validate per row basis.
    Remove rows which contain faulty data according to the schema defined in models.py.
    """
    valid, rejected = [], []
    for row in rows:
        try:
            valid.append(StockData(**row))
        except ValidationError as e:
            rejected.append({"row": row, "errors": e.errors()})

    valid_rows = []
    for row in valid:
        valid_rows.append(tuple(row.model_dump().values()))

    return valid_rows
