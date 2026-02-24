CREATE TABLE IF NOT EXISTS raw_prices (
    date        DATE NOT NULL,
    ticker      VARCHAR NOT NULL,
    market      VARCHAR NOT NULL,
    open        DOUBLE PRECISION,
    high        DOUBLE PRECISION,
    low         DOUBLE PRECISION,
    close       DOUBLE PRECISION,
    volume      BIGINT,
    PRIMARY KEY (date, ticker)
);

CREATE TABLE IF NOT EXISTS adjusted_prices (
    date        DATE NOT NULL,
    ticker      VARCHAR NOT NULL,
    market      VARCHAR NOT NULL,
    open        DOUBLE PRECISION,
    high        DOUBLE PRECISION,
    low         DOUBLE PRECISION,
    close       DOUBLE PRECISION,
    volume      BIGINT,
    adj_factor  DOUBLE PRECISION,
    PRIMARY KEY (date, ticker)
);

CREATE TABLE IF NOT EXISTS corporate_actions (
    date        DATE NOT NULL,
    ticker      VARCHAR NOT NULL,
    action_type VARCHAR NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (date, ticker, action_type)
);

CREATE TABLE IF NOT EXISTS macro_indicators (
    date        DATE NOT NULL,
    market      VARCHAR NOT NULL,
    indicator   VARCHAR NOT NULL,
    source      VARCHAR NOT NULL,
    value       DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (date, market, indicator)
);

CREATE TABLE IF NOT EXISTS pipeline_log (
    run_id        VARCHAR NOT NULL PRIMARY KEY,
    run_date      TIMESTAMP NOT NULL,
    status        VARCHAR NOT NULL,
    rows_inserted INTEGER,
    error_message VARCHAR
);
