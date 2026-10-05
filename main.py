from __future__ import annotations

import pandas as pd

from src.analytics import calculate_kpis, machine_kpis, shift_kpis
from src.anomaly_detection import detect_anomalies
from src.config import PROCESSED_DIR, PROCESSED_FILE
from src.data_generator import generate_sensor_data, save_raw_data
from src.database import initialize_database, replace_readings
from src.operational_analysis import generate_operational_report
from src.reports import create_charts, create_markdown_report


def main() -> None:
    print("=" * 60)
    print("INDUSTRIAL PROCESS ANALYTICS")
    print("=" * 60)

    print("\n[1/7] Generating simulated process data...")
    df = generate_sensor_data()
    save_raw_data(df)
    print(f"      Generated {len(df):,} readings.")

    print("\n[2/7] Processing data...")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    df.to_csv(PROCESSED_FILE, index=False)
    print("      Data processed successfully.")

    print("\n[3/7] Loading data into SQLite...")
    initialize_database()
    replace_readings(df)
    print("      Database updated successfully.")

    print("\n[4/7] Detecting anomalies...")
    analyzed = detect_anomalies(df)
    anomaly_file = PROCESSED_DIR / "anomalies.csv"
    analyzed[analyzed["is_anomaly"]].to_csv(anomaly_file, index=False)
    print(
        f"      Detected {analyzed['is_anomaly'].sum():,} anomalous readings."
    )

    print("\n[5/7] Calculating KPIs...")
    kpis = calculate_kpis()
    machines = machine_kpis()
    shifts = shift_kpis()

    print(f"      Production: {kpis['total_production']:,.0f} units")
    print(f"      Energy: {kpis['total_energy']:,.0f} kWh")
    print(f"      Availability: {kpis['availability']:.2f}%")
    print(f"      Energy/unit: {kpis['energy_per_unit']:.4f} kWh/unit")

    print("\nMachine performance:")
    print(machines.to_string(index=False))

    print("\nShift performance:")
    print(shifts.to_string(index=False))

    print("\n[6/7] Generating charts and main report...")
    create_charts()
    create_markdown_report(kpis, analyzed)
    print("      Main report generated successfully.")

    print("\n[7/7] Generating operational analysis...")
    operational_report = generate_operational_report(analyzed)
    print(f"      Operational report: {operational_report}")

    print("\nPipeline completed successfully.")
    print("Outputs:")
    print("  - data/industrial_process.db")
    print("  - data/raw/sensor_readings.csv")
    print("  - data/processed/sensor_readings_processed.csv")
    print("  - data/processed/anomalies.csv")
    print("  - charts/")
    print("  - reports/industrial_process_report.md")
    print("  - reports/operational_analysis_report.md")


if __name__ == "__main__":
    main()
