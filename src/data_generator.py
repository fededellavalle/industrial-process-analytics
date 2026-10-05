from __future__ import annotations

import numpy as np
import pandas as pd

from .config import RAW_DIR, RAW_FILE, RANDOM_SEED, SAMPLE_ROWS


def generate_sensor_data(rows: int = SAMPLE_ROWS) -> pd.DataFrame:
    """Generate simulated hourly industrial process readings."""

    rng = np.random.default_rng(RANDOM_SEED)

    timestamps = pd.date_range(
        end=pd.Timestamp.now().floor("h"),
        periods=rows,
        freq="h",
    )

    machine = rng.choice(
        ["LINE-01", "LINE-02", "LINE-03", "LINE-04"],
        size=rows,
        p=[0.30, 0.27, 0.23, 0.20],
    )

    hours = timestamps.hour.to_numpy()

    shift = np.select(
        [
            (hours >= 6) & (hours <= 13),
            (hours >= 14) & (hours <= 21),
        ],
        ["Morning", "Afternoon"],
        default="Night",
    )

    ambient = 22 + 6 * np.sin(2 * np.pi * timestamps.hour.to_numpy() / 24)
    load = np.clip(rng.normal(0.78, 0.10, rows), 0.35, 1.00)

    temperature = (
        58
        + load * 22
        + ambient * 0.25
        + rng.normal(0, 2.5, rows)
    )

    pressure = 4.6 + load * 2.1 + rng.normal(0, 0.22, rows)
    flow = 70 + load * 78 + rng.normal(0, 5.5, rows)
    energy = 42 + load * 70 + rng.normal(0, 4.0, rows)
    production = np.maximum(
        0,
        420 + load * 620 + rng.normal(0, 55, rows)
    )

    operating_hours = np.ones(rows)

    # Simulated planned/unplanned stops.
    stop_mask = rng.random(rows) < 0.025
    operating_hours[stop_mask] = 0
    production[stop_mask] *= rng.uniform(0.02, 0.20, stop_mask.sum())
    energy[stop_mask] *= rng.uniform(0.25, 0.55, stop_mask.sum())

    # Simulated sensor anomalies.
    anomaly_mask = rng.random(rows) < 0.012
    anomaly_type = np.full(rows, "normal", dtype=object)

    anomaly_types = rng.choice(
        ["high_temperature", "high_pressure", "high_energy", "low_production"],
        size=anomaly_mask.sum(),
    )

    anomaly_indexes = np.flatnonzero(anomaly_mask)

    for idx, kind in zip(anomaly_indexes, anomaly_types):
        anomaly_type[idx] = kind

        if kind == "high_temperature":
            temperature[idx] += rng.uniform(12, 25)
        elif kind == "high_pressure":
            pressure[idx] += rng.uniform(1.5, 3.0)
        elif kind == "high_energy":
            energy[idx] += rng.uniform(25, 55)
        elif kind == "low_production":
            production[idx] *= rng.uniform(0.15, 0.45)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "machine_id": machine,
            "shift": shift,
            "temperature_c": np.round(temperature, 2),
            "pressure_bar": np.round(pressure, 2),
            "flow_l_min": np.round(flow, 2),
            "energy_kwh": np.round(energy, 2),
            "production_units": np.round(production, 0).astype(int),
            "operating_hours": operating_hours,
            "simulated_condition": anomaly_type,
        }
    )

    return df


def save_raw_data(df: pd.DataFrame) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_FILE, index=False)
