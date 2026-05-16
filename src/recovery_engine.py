"""Autonomous recovery recommendation engine."""

from __future__ import annotations

import pandas as pd


def recommend_action(row: pd.Series) -> str:
    """Return a practical recovery action for one disrupted work order."""
    disruption = row["Primary_Disruption"]

    if disruption == "Machine Downtime":
        if row["Alternate_Route_Available"] == "Yes":
            return "Reroute work order to alternate production path and prioritize maintenance recovery."
        return "Escalate maintenance response and resequence lower-priority work orders."

    if disruption == "Material Shortage":
        if row["Alternate_Supplier_Available"] == "Yes":
            return "Expedite replenishment and activate alternate qualified supplier review."
        return "Escalate material shortage, review safety stock, and protect mission-critical inventory."

    if disruption == "Supply Chain Constraint":
        if row["Single_Source_Supplier"] == "Yes":
            return "Escalate single-source supplier risk and evaluate contingency sourcing options."
        return "Initiate supplier recovery review and monitor inbound material lead time."

    if disruption == "Quality / Inspection":
        if row["Quality_Flag"] == "Scrap Risk":
            return "Isolate suspect lot, prioritize MRB review, and assign rework containment support."
        return "Prioritize inspection queue and allocate rework capacity to reduce backlog."

    if disruption == "Labor Constraint":
        if row["Overtime_Available"] == "Yes":
            return "Apply targeted overtime and reallocate skilled labor to priority production cell."
        return "Resequence work orders and protect labor coverage for mission-priority builds."

    if disruption == "Yield Loss":
        return "Review first-pass yield drivers, isolate defect pattern, and initiate process correction."

    if disruption == "Schedule Risk":
        return "Escalate delivery risk, resequence priority work orders, and update recovery timeline."

    return "Continue monitoring; no immediate recovery action required."


def generate_recovery_plan(df: pd.DataFrame) -> pd.DataFrame:
    """Generate ranked recovery recommendations."""
    plan = df.copy()

    plan["Recommended_Action"] = plan.apply(recommend_action, axis=1)

    plan["Mitigation_Effectiveness"] = (
        plan["Recovery_Confidence"] * 70
        + plan["Alternate_Route_Available"].eq("Yes").astype(int) * 8
        + plan["Alternate_Supplier_Available"].eq("Yes").astype(int) * 8
        + plan["Overtime_Available"].eq("Yes").astype(int) * 5
        - plan["Single_Source_Supplier"].eq("Yes").astype(int) * 8
        - plan["Quality_Flag"].eq("Scrap Risk").astype(int) * 10
    ).clip(5, 95).round(1)

    plan["Avoided_Delay_Hours"] = (
        plan["Estimated_Delay_Hours"] - plan["Estimated_Recovery_Hours"]
    ).clip(lower=0).round(0).astype(int)

    plan["Recovery_Value_Score"] = (
        plan["Readiness_Impact"] * 0.40
        + plan["Avoided_Delay_Hours"] * 0.35
        + plan["Mission_Priority"] * 5
        + plan["Mitigation_Effectiveness"] * 0.20
    ).round(1)

    plan["Recovery_Priority"] = pd.cut(
        plan["Recovery_Value_Score"],
        bins=[-1, 35, 55, 75, 200],
        labels=["Routine", "Moderate", "High", "Critical"],
    ).astype(str)

    return plan.sort_values("Recovery_Value_Score", ascending=False)