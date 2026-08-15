CREATE TABLE stocks (
    stock_code TEXT NOT NULL,
    interval_time TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    stock_open NUMERIC,
    stock_high NUMERIC,
    stock_low NUMERIC,
    stock_close NUMERIC,
    volume BIGINT,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (stock_code, interval_time, ts)
);

CREATE TABLE observation (
    run_id SERIAL PRIMARY KEY,
    stock_code TEXT NOT NULL,
    interval_time TEXT NOT NULL,
    rows_upserted INT,
    error TEXT,
    run_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL
);
