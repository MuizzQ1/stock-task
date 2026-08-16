from aapl_stock import StockIngestion, postgress_ingestion


def main():

    # Initialise the StockIngestion class and pull stock data
    st = StockIngestion()
    df_stocks = st.stock_data_refresh()

    # Initialise the postgress_ingestion class and refresh the database with the new stock data
    db_ingest = postgress_ingestion()
    db_ingest.refresh(df=df_stocks)


if __name__ == "__main__":
    main()
