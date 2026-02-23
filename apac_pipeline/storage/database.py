from pathlib import Path
import duckdb
import pandas as pd

from apac_pipeline.config.settings import DB_PATH
from apac_pipeline.pipeline.logger import get_logger

logger = get_logger(__name__)

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_connection() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def initialize_schema() -> None:
    sql = _SCHEMA_PATH.read_text()
    with get_connection() as conn:
        conn.executescript(sql)
    logger.info("Schema initialized.")


def insert_dataframe(df: pd.DataFrame, table: str) -> int:
    with get_connection() as conn:
        conn.execute(f"INSERT OR REPLACE INTO {table} SELECT * FROM df")
        rows = len(df)
    logger.info("Inserted %d rows into %s.", rows, table)
    return rows


def query(sql: str) -> pd.DataFrame:
    with get_connection() as conn:
        return conn.execute(sql).df()
