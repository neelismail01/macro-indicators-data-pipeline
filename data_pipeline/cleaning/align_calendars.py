import exchange_calendars as ec
import pandas as pd

from data_pipeline.config.markets import MARKET_METADATA
from data_pipeline.pipeline.logger import get_logger

logger = get_logger(__name__)


def get_valid_trading_days(market: str, start_date: str, end_date: str) -> pd.DatetimeIndex:
    cal = ec.get_calendar(MARKET_METADATA[market]["calendar"])
    sessions = cal.sessions_in_range(start_date, end_date)
    return sessions


def filter_to_trading_days(df: pd.DataFrame, market: str) -> pd.DataFrame:
    initial = len(df)
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.normalize().dt.tz_localize(None)

    start = df["date"].min().strftime("%Y-%m-%d")
    end = df["date"].max().strftime("%Y-%m-%d")
    valid_days = get_valid_trading_days(market, start, end).normalize().tz_localize(None)

    df = df[df["date"].isin(valid_days)]
    removed = initial - len(df)
    logger.info(
        "filter_to_trading_days[%s] removed %d rows (from %d).",
        market,
        removed,
        initial,
    )
    return df.reset_index(drop=True)
