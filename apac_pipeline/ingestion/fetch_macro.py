from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf
from fredapi import Fred

from apac_pipeline.config.markets import MACRO_INDICATORS
from apac_pipeline.config.settings import EQUITY_UNIVERSE, FRED_API_KEY, RAW_DATA_PATH
from apac_pipeline.pipeline.logger import get_logger

logger = get_logger(__name__)


def _fred_series(fred: Fred, ticker: str, start: str, end: str) -> pd.DataFrame:
    series = fred.get_series(ticker, observation_start=start, observation_end=end)
    df = series.reset_index()
    df.columns = ["date", "value"]
    return df


def _yf_series(ticker: str, start: str, end: str) -> pd.DataFrame:
    raw = yf.download(ticker, start=start, end=end, progress=False)
    if raw.empty:
        return pd.DataFrame()
    close = raw["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    df = close.reset_index()
    df.columns = ["date", "value"]
    return df


def fetch_macro_indicators(
    start_date: str,
    end_date: str | None = None,
) -> pd.DataFrame:
    if end_date is None:
        end_date = str(date.today())

    fred = Fred(api_key=FRED_API_KEY)
    frames: list[pd.DataFrame] = []

    for market, indicators in MACRO_INDICATORS.items():
        for indicator, meta in indicators.items():
            ticker, source = meta["ticker"], meta["source"]
            try:
                if source == "fred":
                    df = _fred_series(fred, ticker, start_date, end_date)
                else:
                    df = _yf_series(ticker, start_date, end_date)

                if df.empty:
                    logger.warning("Empty result for %s/%s.", market, indicator)
                    continue

                df = df.dropna(subset=["value"])
                df["market"] = market
                df["indicator"] = indicator
                df["source"] = source
                frames.append(df)
            except Exception as exc:
                logger.error("Failed to fetch %s/%s: %s", market, indicator, exc)

    if not frames:
        logger.warning("No macro data fetched.")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    out_path = Path(RAW_DATA_PATH) / f"raw_macro_{end_date}.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(out_path, index=False)
    logger.info("Saved %d macro rows to %s.", len(result), out_path)
    return result


def fetch_corporate_actions() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for market, tickers in EQUITY_UNIVERSE.items():
        for ticker in tickers:
            try:
                t = yf.Ticker(ticker)

                divs = t.dividends
                if not divs.empty:
                    df = divs.reset_index()
                    df.columns = ["date", "value"]
                    df["ticker"] = ticker
                    df["action_type"] = "dividend"
                    frames.append(df[["date", "ticker", "action_type", "value"]])

                splits = t.splits
                if not splits.empty:
                    df = splits.reset_index()
                    df.columns = ["date", "value"]
                    df["ticker"] = ticker
                    df["action_type"] = "split"
                    frames.append(df[["date", "ticker", "action_type", "value"]])
            except Exception as exc:
                logger.error("Failed to fetch corporate actions for %s: %s", ticker, exc)

    if not frames:
        logger.warning("No corporate actions fetched.")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    logger.info("Fetched %d corporate action rows.", len(result))
    return result
