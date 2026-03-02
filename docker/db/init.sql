-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- OHLCV hypertable for time-series market data
CREATE TABLE IF NOT EXISTS ohlcv (
    time        TIMESTAMPTZ     NOT NULL,
    ticker      VARCHAR(20)     NOT NULL,
    open        DOUBLE PRECISION,
    high        DOUBLE PRECISION,
    low         DOUBLE PRECISION,
    close       DOUBLE PRECISION,
    volume      DOUBLE PRECISION,
    adj_close   DOUBLE PRECISION,
    PRIMARY KEY (time, ticker)
);

SELECT create_hypertable('ohlcv', 'time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS ohlcv_ticker_time_idx ON ohlcv (ticker, time DESC);

-- Universe / asset master table
CREATE TABLE IF NOT EXISTS assets (
    ticker      VARCHAR(20)     PRIMARY KEY,
    name        VARCHAR(255),
    exchange    VARCHAR(20),
    currency    VARCHAR(10),
    sector      VARCHAR(100),
    industry    VARCHAR(100),
    country     VARCHAR(50),
    created_at  TIMESTAMPTZ     DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     DEFAULT NOW()
);

-- Fundamentals table (annual / quarterly snapshots)
CREATE TABLE IF NOT EXISTS fundamentals (
    time        TIMESTAMPTZ     NOT NULL,
    ticker      VARCHAR(20)     NOT NULL,
    period      VARCHAR(10)     NOT NULL,  -- 'annual' | 'quarterly'
    revenue     DOUBLE PRECISION,
    net_income  DOUBLE PRECISION,
    eps         DOUBLE PRECISION,
    pe_ratio    DOUBLE PRECISION,
    pb_ratio    DOUBLE PRECISION,
    roe         DOUBLE PRECISION,
    debt_equity DOUBLE PRECISION,
    PRIMARY KEY (time, ticker, period)
);

SELECT create_hypertable('fundamentals', 'time', if_not_exists => TRUE);
