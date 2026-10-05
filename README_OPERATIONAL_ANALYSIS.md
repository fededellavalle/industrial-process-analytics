## Automatic operational analysis

In addition to the main KPI report, the pipeline generates an
`reports/operational_analysis_report.md` file.

This second report analyzes the generated data and automatically identifies:

- Best and lowest production performance by machine.
- Highest anomaly rate by machine.
- Anomaly types and their frequency.
- Production performance by shift.
- Operational findings.
- Rule-based recommendations.

The analysis is generated from the SQLite database after the main
pipeline finishes, so every execution can produce different findings
when the simulated data changes.

> Note: the industrial data is simulated and intended for demonstration.
