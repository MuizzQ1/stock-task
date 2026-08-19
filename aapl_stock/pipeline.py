import logging

from .db_ingest import postgress_ingestion
from .stock_ingestion import StockIngestion

logger = logging.getLogger(__name__)


def run_pipeline():

    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} | {levelname:<8} | {name:<28} | {message}",
        datefmt="%H:%M:%S",
        style="{",
    )

    logger.info("Starting the stock data ingestion process...")

    # Initialise the StockIngestion class and pull stock data
    st = StockIngestion()
    df_stocks = st.stock_data_refresh()

    # Initialise the postgress_ingestion class and refresh the database with the new stock data
    db_ingest = postgress_ingestion()
    db_ingest.refresh(df=df_stocks)

    logger.info("Stock data ingestion process completed")
