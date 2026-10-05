from __future__ import annotations

import pandas as pd

from .database import query_dataframe


def calculate_kpis() -> dict:
    sql = """
    SELECT
        COUNT(*) AS readings,
        COUNT(DISTINCT machine_id) AS machines,
        SUM(production_units) AS total_production,
        AVG(production_units) AS avg_production_per_reading,
        SUM(energy_kwh) AS total_energy,
        AVG(temperature_c) AS avg_temperature,
        AVG(pressure_bar) AS avg_pressure,
        AVG(flow_l_min) AS avg_flow,
        SUM(operating_hours) AS operating_hours,
        SUM(CASE WHEN operating_hours = 0 THEN 1 ELSE 0 END) AS stop_readings
    FROM sensor_readings;
    """

    row = query_dataframe(sql).iloc[0]

    total_production = float(row["total_production"])
    total_energy = float(row["total_energy"])
    readings = int(row["readings"])
    stop_readings = int(row["stop_readings"])

    availability = (
        (readings - stop_readings) / readings * 100
        if readings else 0
    )

    energy_per_unit = (
        total_energy / total_production
        if total_production else 0
    )

    return {
        "readings": readings,
        "machines": int(row["machines"]),
        "total_production": total_production,
        "avg_production_per_reading": float(row["avg_production_per_reading"]),
        "total_energy": total_energy,
        "energy_per_unit": energy_per_unit,
        "avg_temperature": float(row["avg_temperature"]),
        "avg_pressure": float(row["avg_pressure"]),
        "avg_flow": float(row["avg_flow"]),
        "availability": availability,
        "stop_readings": stop_readings,
    }


def machine_kpis() -> pd.DataFrame:
    sql = """
    SELECT
        machine_id,
        SUM(production_units) AS production_units,
        SUM(energy_kwh) AS energy_kwh,
        ROUND(
            SUM(energy_kwh) / NULLIF(SUM(production_units), 0),
            4
        ) AS energy_per_unit,
        ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
        ROUND(AVG(pressure_bar), 2) AS avg_pressure_bar,
        ROUND(
            AVG(operating_hours) * 100,
            2
        ) AS availability_pct
    FROM sensor_readings
    GROUP BY machine_id
    ORDER BY production_units DESC;
    """

    return query_dataframe(sql)


def shift_kpis() -> pd.DataFrame:
    sql = """
    SELECT
        shift,
        SUM(production_units) AS production_units,
        SUM(energy_kwh) AS energy_kwh,
        ROUND(
            SUM(energy_kwh) / NULLIF(SUM(production_units), 0),
            4
        ) AS energy_per_unit,
        ROUND(AVG(temperature_c), 2) AS avg_temperature_c
    FROM sensor_readings
    GROUP BY shift
    ORDER BY production_units DESC;
    """

    return query_dataframe(sql)


def hourly_trend() -> pd.DataFrame:
    sql = """
    SELECT
        substr(timestamp, 1, 13) AS hour,
        SUM(production_units) AS production_units,
        SUM(energy_kwh) AS energy_kwh,
        AVG(temperature_c) AS temperature_c
    FROM sensor_readings
    GROUP BY hour
    ORDER BY hour;
    """

    return query_dataframe(sql)
