from contextlib import contextmanager
from pathlib import Path
import pandas as pd
import psycopg2
import psycopg2.extras
from supabase import create_client, Client

from apac_pipeline.config.settings import SUPABASE_URL, SUPABASE_KEY, DATABASE_URL
from apac_pipeline.pipeline.logger import get_logger

logger = get_logger(__name__)

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


@contextmanager
def _get_pg_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_schema() -> None:
    sql = _SCHEMA_PATH.read_text()
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    with _get_pg_connection() as conn:
        with conn.cursor() as cur:
            for statement in statements:
                cur.execute(statement)
    logger.info("Schema initialized.")


def insert_dataframe(df: pd.DataFrame, table: str) -> int:
    df = df.where(pd.notnull(df), None)
    rows = []
    for record in df.to_dict(orient="records"):
        row = {}
        for k, v in record.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
            else:
                row[k] = v
        rows.append(row)
    _get_client().table(table).upsert(rows).execute()
    logger.info("Upserted %d rows into %s.", len(rows), table)
    return len(rows)


def query(sql: str) -> pd.DataFrame:
    with _get_pg_connection() as conn:
        return pd.read_sql(sql, conn)
