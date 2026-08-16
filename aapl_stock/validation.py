import logging

from pydantic import ValidationError

from .models import StockData

logger = logging.getLogger(__name__)


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

    logger.info(
        f"Validation completed. Valid rows: {len(valid)}, Rejected rows: {len(rejected)}"
    )
    valid_rows = []
    for row in valid:
        valid_rows.append(tuple(row.model_dump().values()))

    return valid_rows
