"""Main pipeline for the Autonomous Manufacturing Recovery System."""

from __future__ import annotations

from pathlib import Path

from data_generator import generate_manufacturing_data
from disruption_engine import score_disruptions, summarize_bottlenecks
from recovery_engine import generate_recovery_plan
from reporting import create_recovery_report
from visualization import generate_all_visuals


def main() -> None:
    Path("data").mkdir(exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)

    data = generate_manufacturing_data(rows=250)
    data.to_csv("data/manufacturing_operations.csv", index=False)

    scored = score_disruptions(data)
    summary = summarize_bottlenecks(scored)
    recovery_plan = generate_recovery_plan(scored)

    scored.to_csv("outputs/reports/scored_manufacturing_operations.csv", index=False)
    recovery_plan.to_csv("outputs/reports/recovery_recommendations.csv", index=False)
    summary.to_csv("outputs/reports/production_cell_summary.csv", index=False)

    generate_all_visuals(scored, summary)
    create_recovery_report(scored, recovery_plan, summary)

    print("Pipeline complete.")
    print("Generated data, reports, and visualizations in outputs/.")


if __name__ == "__main__":
    main()
