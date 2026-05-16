"""Disruption scoring and bottleneck detection."""

from __future__ import annotations

import pandas as pd


def score_disruptions(df: pd.DataFrame) -> pd.DataFrame:
    """Classify operational disruptions using manufacturing conditions."""
    scored = df.copy()

    def category(row: pd.Series) -> str:
        # Machine-related disruptions
        if row["Machine_Status"] == "Down":
            return "Machine Downtime"

        # Severe quality issues
        if row["Quality_Flag"] in {"Inspection Hold", "Scrap Risk"}:
            return "Quality / Inspection"

        # Supply chain disruptions
        if (
            row["Supplier_Risk"] >= 0.75
            or row["Single_Source_Supplier"] == "Yes"
        ):
            return "Supply Chain Constraint"

        # Inventory shortages
        if row["Inventory_Level"] < row["Reorder_Point"]:
            return "Material Shortage"

        # Workforce limitations
        if row["Workforce_Availability"] < 0.68:
            return "Labor Constraint"

        # Inspection / yield degradation
        if row["First_Pass_Yield"] < 0.82:
            return "Yield Loss"

        # Contract delivery pressure
        if row["Contract_Delivery_Risk"] == "Elevated":
            return "Schedule Risk"

        return "Nominal"

    scored["Primary_Disruption"] = scored.apply(category, axis=1)

    # Recovery priority classification
    def recovery_priority(row: pd.Series) -> str:
        if row["Readiness_Impact"] >= 70:
            return "Critical"

        if row["Readiness_Impact"] >= 45:
            return "High"

        if row["Readiness_Impact"] >= 25:
            return "Moderate"

        return "Routine"

    scored["Recovery_Priority"] = scored.apply(
        recovery_priority,
        axis=1,
    )

    # Escalation logic
    scored["Escalation_Required"] = (
        (
            scored["Recovery_Priority"] == "Critical"
        )
        | (
            scored["Quality_Flag"] == "Scrap Risk"
        )
        | (
            scored["Machine_Status"] == "Down"
        )
    )

    # Bottleneck severity scoring
    scored["Bottleneck_Severity"] = (
        scored["Estimated_Delay_Hours"] * 0.45
        + scored["Operational_Risk"] * 0.40
        + scored["Readiness_Impact"] * 0.15
    ).round(1)

    return scored


def summarize_bottlenecks(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize operational bottlenecks by production cell."""

    summary = (
        df.groupby("Production_Cell")
        .agg(
            Work_Orders=("Work_Order_ID", "count"),
            Avg_Risk=("Operational_Risk", "mean"),
            Avg_Delay_Hours=("Estimated_Delay_Hours", "mean"),
            Avg_Readiness_Impact=("Readiness_Impact", "mean"),
            Avg_Recovery_Hours=("Estimated_Recovery_Hours", "mean"),
            Avg_Recovery_Confidence=("Recovery_Confidence", "mean"),
            High_Risk_Count=("Risk_Level", lambda x: (x == "High").sum()),
            Critical_Work_Orders=("Recovery_Priority", lambda x: (x == "Critical").sum()),
            Escalations=("Escalation_Required", "sum"),
        )
        .reset_index()
        .sort_values(
            "Avg_Readiness_Impact",
            ascending=False,
        )
    )

    return summary.round(2)