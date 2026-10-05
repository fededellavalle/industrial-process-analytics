from __future__ import annotations

import sqlite3

import pandas as pd

from .config import DB_PATH


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    shift TEXT NOT NULL,
    temperature_c REAL NOT NULL,
    pressure_bar REAL NOT NULL,
    flow_l_min REAL NOT NULL,
    energy_kwh REAL NOT NULL,
    production_units INTEGER NOT NULL,
    operating_hours REAL NOT NULL,
    simulated_condition TEXT NOT NULL
);
"""

CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_sensor_timestamp
ON sensor_readings(timestamp);

CREATE INDEX IF NOT EXISTS idx_sensor_machine
ON sensor_readings(machine_id);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database() -> None:
    with get_connection() as conn:
        conn.execute(CREATE_TABLE_SQL)
        conn.executescript(CREATE_INDEX_SQL)
        conn.commit()


def replace_readings(df: pd.DataFrame) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM sensor_readings")
        df.to_sql(
            "sensor_readings",
            conn,
            if_exists="append",
            index=False,
        )
        conn.commit()


def query_dataframe(sql: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(sql, conn)
