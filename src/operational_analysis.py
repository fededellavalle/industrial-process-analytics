from __future__ import annotations

from pathlib import Path

import pandas as pd

from .analytics import machine_kpis, shift_kpis
from .config import REPORTS_DIR


REPORT_PATH = REPORTS_DIR / "operational_analysis_report.md"


def _anomaly_type_counts(analyzed: pd.DataFrame) -> dict[str, int]:
    """Count anomaly types using the exact flags produced by detect_anomalies."""
    counts: dict[str, int] = {}

    for flags in analyzed.loc[analyzed["is_anomaly"], "anomaly_flags"]:
        if not flags:
            continue
        for flag in str(flags).split(","):
            counts[flag] = counts.get(flag, 0) + 1

    return counts


def _anomaly_by_machine(analyzed: pd.DataFrame) -> pd.DataFrame:
    result = (
        analyzed.groupby("machine_id")
        .agg(
            readings=("machine_id", "size"),
            anomalies=("is_anomaly", "sum"),
        )
        .reset_index()
    )
    result["anomaly_rate_pct"] = (
        result["anomalies"] / result["readings"] * 100
    )
    result = result.sort_values(
        ["anomaly_rate_pct", "anomalies"],
        ascending=False,
    )
    return result


def _build_findings(
    machine_data: pd.DataFrame,
    shift_data: pd.DataFrame,
    anomaly_data: pd.DataFrame,
    anomaly_count: int,
) -> list[str]:
    findings = []

    best_production = machine_data.loc[machine_data["production_units"].idxmax()]
    worst_production = machine_data.loc[machine_data["production_units"].idxmin()]
    best_availability = machine_data.loc[machine_data["availability_pct"].idxmax()]
    worst_anomaly = anomaly_data.iloc[0]
    best_shift = shift_data.loc[shift_data["production_units"].idxmax()]
    worst_shift = shift_data.loc[shift_data["production_units"].idxmin()]

    findings.append(
        f"**{best_production['machine_id']}** generated the highest production "
        f"volume with {best_production['production_units']:,.0f} units."
    )

    findings.append(
        f"**{worst_production['machine_id']}** generated the lowest production "
        f"volume with {worst_production['production_units']:,.0f} units."
    )

    findings.append(
        f"**{best_availability['machine_id']}** achieved the highest "
        f"availability at {best_availability['availability_pct']:.2f}%."
    )

    if anomaly_count:
        findings.append(
            f"**{worst_anomaly['machine_id']}** has the highest anomaly rate "
            f"at {worst_anomaly['anomaly_rate_pct']:.2f}%."
        )
    else:
        findings.append("No anomalous readings were detected in this run.")

    findings.append(
        f"The **{best_shift['shift']}** shift recorded the highest production "
        f"volume with {best_shift['production_units']:,.0f} units."
    )

    if best_shift["shift"] != worst_shift["shift"]:
        findings.append(
            f"The **{worst_shift['shift']}** shift recorded the lowest production "
            f"volume with {worst_shift['production_units']:,.0f} units."
        )

    return findings


def _build_recommendations(
    machine_data: pd.DataFrame,
    anomaly_data: pd.DataFrame,
    anomaly_counts: dict[str, int],
    anomaly_count: int,
) -> list[str]:
    recommendations = []

    worst_anomaly = anomaly_data.iloc[0]
    worst_production = machine_data.loc[machine_data["production_units"].idxmin()]

    if anomaly_count:
        recommendations.append(
            f"Review the anomalous readings associated with **{worst_anomaly['machine_id']}**, "
            "which has the highest anomaly rate."
        )

    recommendations.append(
        f"Review the production performance of **{worst_production['machine_id']}** "
        "and compare its operating conditions with the other lines."
    )

    if "energy_kwh" in anomaly_counts:
        recommendations.append(
            "Investigate periods of excessive energy consumption and compare "
            "them with production levels."
        )

    if "temperature_c" in anomaly_counts:
        recommendations.append(
            "Monitor recurring temperature deviations to determine whether "
            "they are isolated events or persistent operating conditions."
        )

    if "pressure_bar" in anomaly_counts:
        recommendations.append(
            "Review pressure deviations and their relationship with production "
            "and flow conditions."
        )

    if "flow_l_min" in anomaly_counts:
        recommendations.append(
            "Investigate flow deviations and compare them with production "
            "and machine operating conditions."
        )

    if "low_production" in anomaly_counts:
        recommendations.append(
            "Investigate low-production periods while machines were operating, "
            "as these may indicate efficiency losses."
        )

    return recommendations


def generate_operational_report(analyzed: pd.DataFrame) -> Path:
    """Generate an automatic operational report from the pipeline's analyzed data."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    anomaly_count = int(analyzed["is_anomaly"].sum())
    anomaly_rate = anomaly_count / len(analyzed) * 100 if len(analyzed) else 0

    machine_data = machine_kpis()
    shift_data = shift_kpis()
    anomaly_data = _anomaly_by_machine(analyzed)
    anomaly_counts = _anomaly_type_counts(analyzed)

    findings = _build_findings(
        machine_data,
        shift_data,
        anomaly_data,
        anomaly_count,
    )
    recommendations = _build_recommendations(
        machine_data,
        anomaly_data,
        anomaly_counts,
        anomaly_count,
    )

    machine_table = machine_data.copy()
    machine_table.columns = [
        "Machine",
        "Production (units)",
        "Energy (kWh)",
        "Energy / unit",
        "Avg. temperature (°C)",
        "Avg. pressure (bar)",
        "Availability (%)",
    ]

    anomaly_table = anomaly_data.copy()
    anomaly_table.columns = [
        "Machine",
        "Readings",
        "Anomalies",
        "Anomaly rate (%)",
    ]

    shift_table = shift_data.copy()
    shift_table.columns = [
        "Shift",
        "Production (units)",
        "Energy (kWh)",
        "Energy / unit",
        "Avg. temperature (°C)",
    ]

    anomaly_type_lines = (
        "\n".join(
            f"- **{name}:** {count} readings"
            for name, count in sorted(
                anomaly_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )
        if anomaly_counts
        else "- No anomaly types were detected."
    )

    findings_md = "\n".join(f"- {item}" for item in findings)
    recommendations_md = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(recommendations, start=1)
    )

    report = f"""# Industrial Process — Operational Analysis

Generated automatically from the same dataset analyzed by the main pipeline.

## 1. Operational overview

| Metric | Value |
|---|---:|
| Sensor readings | {len(analyzed):,} |
| Machines | {analyzed['machine_id'].nunique()} |
| Total anomalies | {anomaly_count:,} |
| Anomaly rate | {anomaly_rate:.2f}% |

## 2. Automatic findings

{findings_md}

## 3. Anomaly analysis

### Anomaly types

{anomaly_type_lines}

### Anomalies by machine

{anomaly_table.to_markdown(index=False)}

## 4. Machine performance

{machine_table.to_markdown(index=False)}

## 5. Shift analysis

{shift_table.to_markdown(index=False)}

## 6. Recommendations

{recommendations_md}

## 7. Interpretation

This report is generated automatically from the simulated industrial
process dataset. The findings and recommendations are rule-based and are
intended to demonstrate how Python can transform operational data into
actionable information.

> Note: all industrial data in this project is simulated and intended for
> demonstration of Python, SQL, data analysis, and automation capabilities.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")
    return REPORT_PATH
