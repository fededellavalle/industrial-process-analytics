from __future__ import annotations

import pandas as pd

# Operational limits are intentionally explicit so they are easy to review.
LIMITS = {
    "temperature_c": (45.0, 95.0),
    "pressure_bar": (3.5, 8.0),
    "flow_l_min": (45.0, 180.0),
    "energy_kwh": (20.0, 150.0),
}


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """Return a row-level anomaly table based on operational thresholds."""

    result = df.copy()
    result["anomaly_flags"] = ""
    result["is_anomaly"] = False

    for column, (low, high) in LIMITS.items():
        mask = (result[column] < low) | (result[column] > high)
        result.loc[mask, "is_anomaly"] = True

        labels = result.loc[mask, "anomaly_flags"].astype(str)
        labels = labels.where(labels == "", labels + ",")
        labels = labels + column
        result.loc[mask, "anomaly_flags"] = labels

    # Production anomaly: unusually low production while the machine is operating.
    production_mask = (
        (result["operating_hours"] > 0)
        & (result["production_units"] < 350)
    )
    result.loc[production_mask, "is_anomaly"] = True
    labels = result.loc[production_mask, "anomaly_flags"].astype(str)
    labels = labels.where(labels == "", labels + ",")
    result.loc[production_mask, "anomaly_flags"] = labels + "low_production"

    return result
