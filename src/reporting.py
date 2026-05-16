"""Executive-style recovery report generation utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def create_recovery_report(
    df: pd.DataFrame,
    recovery_plan: pd.DataFrame,
    summary: pd.DataFrame,
) -> str:
    """Generate an executive manufacturing recovery report."""

    top_actions = recovery_plan.head(10)

    high_risk = int((df["Risk_Level"] == "High").sum())
    critical_orders = int((df["Recovery_Priority"] == "Critical").sum())

    avg_risk = df["Operational_Risk"].mean()
    avg_delay = df["Estimated_Delay_Hours"].mean()
    avg_recovery = df["Estimated_Recovery_Hours"].mean()
    avg_confidence = df["Recovery_Confidence"].mean()

    top_cell = summary.iloc[0]["Production_Cell"]

    elevated_delivery = int(
        (df["Contract_Delivery_Risk"] == "Elevated").sum()
    )

    machine_down = int(
        (df["Machine_Status"] == "Down").sum()
    )

    inspection_holds = int(
        (
            df["Quality_Flag"].isin(
                ["Inspection Hold", "Scrap Risk"]
            )
        ).sum()
    )

    supplier_constraints = int(
        (
            df["Primary_Disruption"] == "Supply Chain Constraint"
        ).sum()
    )

    lines = [
        "AUTONOMOUS MANUFACTURING RECOVERY SYSTEM",
        "EXECUTIVE OPERATIONS RECOVERY REPORT",
        "=" * 78,
        "",
        "EXECUTIVE SUMMARY",
        "-" * 78,
        f"Total work orders assessed: {len(df)}",
        f"High-risk work orders detected: {high_risk}",
        f"Critical recovery actions identified: {critical_orders}",
        f"Average operational risk score: {avg_risk:.1f}/100",
        f"Average estimated delay: {avg_delay:.1f} hours",
        f"Average estimated recovery timeline: {avg_recovery:.1f} hours",
        f"Average recovery confidence: {avg_confidence:.2f}",
        f"Highest-impact production cell: {top_cell}",
        "",
        "CURRENT OPERATIONAL CONDITIONS",
        "-" * 78,
        f"Machine downtime events detected: {machine_down}",
        f"Inspection holds / scrap risks detected: {inspection_holds}",
        f"Elevated contract delivery risks: {elevated_delivery}",
        f"Supply chain constraint events: {supplier_constraints}",
        "",
        "TOP RECOVERY PRIORITIES",
        "-" * 78,
    ]

    for _, row in top_actions.iterrows():
        lines.extend(
            [
                "",
                f"Work Order ID: {row['Work_Order_ID']}",
                f"Program: {row['Program_Name']}",
                f"Platform: {row['Platform']}",
                f"Production Cell: {row['Production_Cell']}",
                f"Component: {row['Component_Type']}",
                f"Primary Disruption: {row['Primary_Disruption']}",
                f"Recovery Priority: {row['Recovery_Priority']}",
                f"Operational Risk: {row['Operational_Risk']}",
                f"Readiness Impact: {row['Readiness_Impact']}",
                f"Estimated Delay: {row['Estimated_Delay_Hours']} hours",
                f"Estimated Recovery Time: {row['Estimated_Recovery_Hours']} hours",
                f"Recovery Confidence: {row['Recovery_Confidence']}",
                f"Recommended Recovery Action: {row['Recommended_Action']}",
            ]
        )

    lines.extend(
        [
            "",
            "STRATEGIC OBSERVATIONS",
            "-" * 78,
            "• Production bottlenecks are concentrated in high-readiness-impact manufacturing cells.",
            "• Supply chain volatility and inspection backlog remain primary operational risk drivers.",
            "• Recovery confidence improves significantly when alternate routing and supplier options exist.",
            "• Mission-priority work orders require aggressive disruption mitigation to reduce delivery risk.",
            "",
            "DISCLAIMER",
            "-" * 78,
            "This project uses fully synthetic data and is intended solely as a portfolio demonstration",
            "of manufacturing operations analytics, disruption simulation, and AI-assisted operational",
            "decision-support concepts. It does not contain real defense, supplier, manufacturing,",
            "or proprietary production information.",
        ]
    )

    report = "\n".join(lines)

    output_dir = Path("outputs/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "recovery_action_report.txt"

    report_path.write_text(
        report,
        encoding="utf-8",
    )

    return report