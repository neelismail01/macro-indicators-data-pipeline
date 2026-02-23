from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

from apac_pipeline.config.settings import EQUITY_UNIVERSE, RAW_DATA_PATH
from apac_pipeline.pipeline.logger import get_logger

logger = get_logger(__name__)


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def fetch_equity_prices(
    start_date: str,
    end_date: str | None = None,
) -> pd.DataFrame:
    if end_date is None:
        end_date = str(date.today())

    frames: list[pd.DataFrame] = []

    for market, tickers in EQUITY_UNIVERSE.items():
        for ticker in tickers:
            try:
                raw = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    auto_adjust=False,
                    progress=False,
                )
                if raw.empty:
                    logger.warning("Empty result for ticker %s.", ticker)
                    continue

                raw = _flatten_columns(raw)
                raw.index.name = "date"
                df = raw.reset_index()[["date", "open", "high", "low", "close", "volume"]]
                df.columns = df.columns.str.lower()
                df["ticker"] = ticker
                df["market"] = market
                frames.append(df)
            except Exception as exc:
                logger.error("Failed to fetch %s: %s", ticker, exc)

    if not frames:
        logger.warning("No equity price data fetched.")
        return pd.DataFrame()

    result = pd.concat(frames, ignore_index=True)
    out_path = Path(RAW_DATA_PATH) / f"raw_prices_{end_date}.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(out_path, index=False)
    logger.info("Saved %d rows to %s.", len(result), out_path)
    return result
