import numpy as np
import pandas as pd

from data_pipeline.pipeline.logger import get_logger

logger = get_logger(__name__)


def validate_prices(df: pd.DataFrame) -> pd.DataFrame:
    initial = len(df)

    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df[df["high"] >= df["low"]]
    df = df[df["close"] > 0]

    prev_close = df.groupby("ticker")["close"].shift(1)
    daily_return = (df["close"] - prev_close) / prev_close
    extreme = daily_return.abs() > 0.5
    if extreme.any():
        flagged = df.loc[extreme, ["date", "ticker", "close"]].head(10)
        logger.warning(
            "%d rows have daily return > 50%%. Sample:\n%s",
            extreme.sum(),
            flagged.to_string(index=False),
        )

    removed = initial - len(df)
    logger.info("validate_prices removed %d rows (from %d).", removed, initial)
    return df.reset_index(drop=True)


def validate_macro(df: pd.DataFrame) -> pd.DataFrame:
    initial = len(df)
    df = df.replace([float("inf"), float("-inf")], float("nan"))
    df = df.dropna(subset=["value"])
    removed = initial - len(df)
    logger.info("validate_macro removed %d rows (from %d).", removed, initial)
    return df.reset_index(drop=True)
