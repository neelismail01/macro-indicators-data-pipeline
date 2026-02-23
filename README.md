# APAC Macro Indicators Data Pipeline

## Overview

This pipeline collects, validates, and stores macroeconomic and equity price data for four major APAC markets: Japan (JP), Hong Kong (HK), South Korea (KR), and Taiwan (TW). The goal is to support systematic macro investment research by maintaining a clean, queryable time-series database spanning from 2015 onward.

Data is sourced from two complementary providers. The Federal Reserve Economic Data (FRED) API supplies monetary policy rates, inflation (CPI), 10-year government bond yields, and FX rates against the USD — all critical inputs for relative-value and carry-trade strategies across APAC fixed income and currency markets. Yahoo Finance supplements with equity index levels and individual stock OHLCV data, enabling analysis of equity risk premia alongside macro conditions. Together, these sources provide the raw material for cross-asset regime detection, factor decomposition, and policy-driven event studies.

The pipeline is designed for incremental daily updates and a one-time historical backfill. All data lands in a local DuckDB database, which is optimised for analytical queries and requires no external server infrastructure. The cleaning layer enforces trading-calendar alignment and basic price sanity checks before any data is written to the database.

---

## Prerequisites

- Python 3.11+
- A FRED API key (free registration at https://fred.stlouisfed.org/docs/api/api_key.html)

---

## Setup

```bash
pip install -r requirements.txt

cp .env.example .env
# Edit .env and set FRED_API_KEY=<your_key>
```

---

## Running the pipeline

### Initial historical load (2015-01-01 to today)

```bash
python -m apac_pipeline.pipeline.run_daily --historical
```

### Daily update (today only)

```bash
python -m apac_pipeline.pipeline.run_daily
```

---

## Querying the database

The database is stored at `data/apac_pipeline.duckdb`. Open it with the DuckDB CLI or query it from Python:

```python
import duckdb
conn = duckdb.connect("data/apac_pipeline.duckdb")

# Latest closing prices for all JP tickers
conn.execute("""
    SELECT date, ticker, close
    FROM raw_prices
    WHERE market = 'JP'
    ORDER BY date DESC
    LIMIT 20
""").df()

# USD/JPY exchange rate over time
conn.execute("""
    SELECT date, value AS usdjpy
    FROM macro_indicators
    WHERE market = 'JP' AND indicator = 'FX_VS_USD'
    ORDER BY date
""").df()

# Pipeline run history
conn.execute("SELECT * FROM pipeline_log ORDER BY run_date DESC LIMIT 10").df()
```

---

## Limitations

**Survivorship bias**: The equity universe is a fixed list of currently-listed large-cap names. Companies that were delisted, merged, or went bankrupt between 2015 and today are not included. Any backtest built on this data will overstate historical returns. A production-grade system would source historical constituent lists from a commercial data vendor (e.g. Bloomberg, Refinitiv) to reconstruct the index membership at each point in time.

---

## Orchestration notes

**Why Prefect over cron?** A cron job runs a script and offers no visibility into retries, partial failures, or run history. Prefect provides task-level retry logic (3 retries with 60-second delays), a UI for monitoring run state, and structured logging of each run's outcome to the `pipeline_log` table. For a pipeline that depends on external APIs that can be flaky, this observability is valuable.

**Production deployment with Airflow**: In a team or cloud environment, this pipeline would be expressed as an Airflow DAG. The key differences are: Airflow requires a metadata database (Postgres/MySQL) and a scheduler process; tasks become Airflow `PythonOperator` or `TaskFlow` functions; the DAG file replaces `run_daily.py`; and deployment would use a managed service such as AWS MWAA or Google Cloud Composer. The pipeline logic itself (ingestion, validation, storage) would remain unchanged.

---

## APAC-specific data considerations

- **Trading calendars**: Each market observes different public holidays and trading hours. The `cleaning/align_calendars.py` module uses the `exchange-calendars` library to filter price data to valid trading sessions per market, preventing the introduction of stale prices on non-trading days.
- **Corporate actions**: Dividends and stock splits are fetched separately via `fetch_corporate_actions()` and stored in the `corporate_actions` table. These are required to construct adjusted price series for accurate return calculations.
- **Market microstructure**: APAC equity markets differ significantly in tick sizes, lot sizes, and transaction taxes (e.g. stamp duty in HK, securities transaction tax in TW and KR). These friction costs are not modelled in this pipeline but are documented here as a reminder for any downstream strategy implementation.
