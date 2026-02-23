"""Daily pipeline entry point. Run directly or via Prefect."""
from __future__ import annotations

import argparse
import uuid
from datetime import date, datetime

import pandas as pd
from prefect import flow, task

from apac_pipeline.cleaning.align_calendars import filter_to_trading_days
from apac_pipeline.cleaning.validate import validate_macro, validate_prices
from apac_pipeline.config.markets import MARKET_METADATA
from apac_pipeline.config.settings import START_DATE
from apac_pipeline.ingestion.fetch_macro import fetch_corporate_actions, fetch_macro_indicators
from apac_pipeline.ingestion.fetch_prices import fetch_equity_prices
from apac_pipeline.pipeline.logger import get_logger
from apac_pipeline.storage.database import initialize_schema, insert_dataframe, query

logger = get_logger(__name__)


@task(retries=3, retry_delay_seconds=60)
def fetch_prices_task(start_date: str, end_date: str) -> pd.DataFrame:
    return fetch_equity_prices(start_date, end_date)


@task(retries=3, retry_delay_seconds=60)
def fetch_macro_task(start_date: str, end_date: str) -> pd.DataFrame:
    return fetch_macro_indicators(start_date, end_date)


@task(retries=3, retry_delay_seconds=60)
def fetch_corporate_actions_task() -> pd.DataFrame:
    return fetch_corporate_actions()


@task(retries=3, retry_delay_seconds=60)
def validate_and_store_prices_task(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    df = validate_prices(df)
    rows = 0
    for market in df["market"].unique():
        market_df = df[df["market"] == market].copy()
        market_df = filter_to_trading_days(market_df, market)
        cols = ["date", "ticker", "market", "open", "high", "low", "close", "volume"]
        rows += insert_dataframe(market_df[cols], "raw_prices")
    return rows


@task(retries=3, retry_delay_seconds=60)
def validate_and_store_macro_task(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    df = validate_macro(df)
    cols = ["date", "market", "indicator", "source", "value"]
    return insert_dataframe(df[cols], "macro_indicators")


@flow(name="APAC Daily Pipeline")
def run_pipeline(
    start_date: str | None = None,
    end_date: str | None = None,
) -> None:
    initialize_schema()

    if start_date is None:
        start_date = str(date.today())
    if end_date is None:
        end_date = str(date.today())

    # Submit price and macro fetches concurrently
    prices_future = fetch_prices_task.submit(start_date, end_date)
    macro_future = fetch_macro_task.submit(start_date, end_date)
    actions_future = fetch_corporate_actions_task.submit()

    prices_df = prices_future.result()
    macro_df = macro_future.result()
    actions_df = actions_future.result()

    price_rows = validate_and_store_prices_task(prices_df)
    macro_rows = validate_and_store_macro_task(macro_df)

    if not actions_df.empty:
        insert_dataframe(actions_df, "corporate_actions")

    total_rows = price_rows + macro_rows
    run_id = uuid.uuid4().hex[:8]
    status = "SUCCESS" if total_rows > 0 else "PARTIAL"

    log_df = pd.DataFrame([{
        "run_id": run_id,
        "run_date": datetime.utcnow(),
        "status": status,
        "rows_inserted": total_rows,
        "error_message": None,
    }])
    insert_dataframe(log_df, "pipeline_log")
    logger.info("Pipeline complete. run_id=%s status=%s rows=%d", run_id, status, total_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="APAC macro pipeline")
    parser.add_argument(
        "--historical",
        action="store_true",
        help="Run historical load from START_DATE.",
    )
    args = parser.parse_args()

    if args.historical:
        run_pipeline(start_date=START_DATE, end_date=str(date.today()))
    else:
        run_pipeline()
