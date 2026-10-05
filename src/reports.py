from __future__ import annotations

from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

from .analytics import hourly_trend, machine_kpis, shift_kpis
from .config import CHARTS_DIR, REPORTS_DIR


def create_charts() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    trend = hourly_trend()

    plt.figure(figsize=(12, 5))
    plt.plot(
        pd.to_datetime(trend["hour"]),
        trend["production_units"],
        linewidth=1,
    )
    plt.title("Production Trend")
    plt.xlabel("Time")
    plt.ylabel("Production units")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "production_trend.png", dpi=150)
    plt.close()

    machines = machine_kpis()

    plt.figure(figsize=(9, 5))
    plt.bar(machines["machine_id"], machines["production_units"])
    plt.title("Production by Machine")
    plt.xlabel("Machine")
    plt.ylabel("Production units")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "production_by_machine.png", dpi=150)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.bar(machines["machine_id"], machines["energy_per_unit"])
    plt.title("Energy Consumption per Unit")
    plt.xlabel("Machine")
    plt.ylabel("kWh / unit")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "energy_efficiency.png", dpi=150)
    plt.close()


def create_markdown_report(
    kpis: dict,
    anomalies: pd.DataFrame,
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    machine_data = machine_kpis()
    shift_data = shift_kpis()

    anomaly_count = int(anomalies["is_anomaly"].sum())
    anomaly_rate = (
        anomaly_count / len(anomalies) * 100
        if len(anomalies)
        else 0
    )

    top_machine = machine_data.iloc[0]

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""# Industrial Process Analytics Report

Generated: **{generated_at}**

## Executive Summary

This report summarizes the analysis of simulated industrial process data.
The pipeline stores sensor readings in SQLite, calculates operational KPIs
using SQL, and identifies abnormal readings using configurable thresholds.

## Overall KPIs

| KPI | Value |
|---|---:|
| Sensor readings | {kpis["readings"]:,} |
| Machines | {kpis["machines"]} |
| Total production | {kpis["total_production"]:,.0f} units |
| Total energy | {kpis["total_energy"]:,.0f} kWh |
| Energy per unit | {kpis["energy_per_unit"]:.4f} kWh/unit |
| Average temperature | {kpis["avg_temperature"]:.2f} °C |
| Average pressure | {kpis["avg_pressure"]:.2f} bar |
| Average flow | {kpis["avg_flow"]:.2f} L/min |
| Availability | {kpis["availability"]:.2f}% |
| Stop readings | {kpis["stop_readings"]:,} |

## Anomaly Detection

- Anomalous readings: **{anomaly_count:,}**
- Anomaly rate: **{anomaly_rate:.2f}%**

Detected conditions include:

- Temperature outside configured operating limits.
- Pressure outside configured operating limits.
- Flow outside configured operating limits.
- Excessive energy consumption.
- Low production while a machine is operating.

## Best Performing Machine

**{top_machine["machine_id"]}**

- Production: {top_machine["production_units"]:,.0f} units
- Energy consumption: {top_machine["energy_kwh"]:,.0f} kWh
- Energy per unit: {top_machine["energy_per_unit"]:.4f} kWh/unit
- Availability: {top_machine["availability_pct"]:.2f}%

## Machine KPIs

{machine_data.to_markdown(index=False)}

## Shift KPIs

{shift_data.to_markdown(index=False)}

## Generated Charts

- `charts/production_trend.png`
- `charts/production_by_machine.png`
- `charts/energy_efficiency.png`

> Note: all data in this project is simulated and intended for demonstration
> of data engineering, analytics, SQL, and Python capabilities.
"""

    (REPORTS_DIR / "industrial_process_report.md").write_text(
        report,
        encoding="utf-8",
    )
