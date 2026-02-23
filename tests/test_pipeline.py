"""Smoke tests for the APAC macro pipeline."""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import pytest

from apac_pipeline.cleaning.align_calendars import filter_to_trading_days
from apac_pipeline.cleaning.validate import validate_prices
from apac_pipeline.ingestion.fetch_macro import fetch_macro_indicators
from apac_pipeline.ingestion.fetch_prices import fetch_equity_prices
from apac_pipeline.storage.database import initialize_schema, query

_TODAY = str(date.today())
_FIVE_DAYS_AGO = str(date.today() - timedelta(days=7))  # extra buffer for weekends

EXPECTED_PRICE_COLS = {"date", "ticker", "market", "open", "high", "low", "close", "volume"}
EXPECTED_MACRO_COLS = {"date", "market", "indicator", "source", "value"}
EXPECTED_TABLES = {
    "raw_prices",
    "adjusted_prices",
    "corporate_actions",
    "macro_indicators",
    "pipeline_log",
}


def test_schema_initialization(tmp_path, monkeypatch):
    monkeypatch.setattr("apac_pipeline.config.settings.DB_PATH", tmp_path / "test.duckdb")
    import apac_pipeline.storage.database as db_module
    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.duckdb")

    initialize_schema()

    tables_df = query(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
    )
    found = set(tables_df["table_name"].tolist())
    assert EXPECTED_TABLES.issubset(found), f"Missing tables: {EXPECTED_TABLES - found}"


def test_fetch_single_ticker():
    df = fetch_equity_prices(start_date=_FIVE_DAYS_AGO, end_date=_TODAY)
    toyota = df[df["ticker"] == "7203.T"]
    assert not toyota.empty, "Expected rows for 7203.T"
    assert EXPECTED_PRICE_COLS.issubset(set(toyota.columns))


def test_fetch_single_macro():
    import yfinance as yf
    import pandas as pd

    raw = yf.download("USDJPY=X", start=_FIVE_DAYS_AGO, end=_TODAY, progress=False)
    assert not raw.empty, "Expected non-empty result for USDJPY=X from yfinance"


def test_validate_prices_removes_bad_rows():
    good_row = {
        "date": "2024-01-02",
        "ticker": "TEST",
        "market": "JP",
        "open": 100.0,
        "high": 110.0,
        "low": 90.0,
        "close": 105.0,
        "volume": 1000,
    }
    bad_rows = [
        {**good_row, "close": None},           # null close
        {**good_row, "high": 80.0, "low": 90.0},  # high < low
        {**good_row, "close": 0.0},            # zero price
    ]
    df = pd.DataFrame([good_row] + bad_rows)
    result = validate_prices(df)
    assert len(result) == 1, f"Expected 1 valid row, got {len(result)}"
    assert result.iloc[0]["close"] == 105.0


def test_calendar_alignment():
    # Build a DataFrame that includes known Japanese public holidays
    # 2024-01-01 (New Year's Day) and 2024-01-08 (Coming of Age Day)
    dates = pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-08", "2024-01-09"])
    df = pd.DataFrame({
        "date": dates,
        "ticker": "7203.T",
        "market": "JP",
        "open": 100.0,
        "high": 110.0,
        "low": 90.0,
        "close": 105.0,
        "volume": 1000,
    })
    result = filter_to_trading_days(df, "JP")
    result_dates = set(result["date"].dt.strftime("%Y-%m-%d").tolist())
    assert "2024-01-01" not in result_dates, "New Year's Day should be filtered out"
    assert "2024-01-08" not in result_dates, "Coming of Age Day should be filtered out"
