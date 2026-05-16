"""Scenario simulation utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def apply_scenario(
    df: pd.DataFrame,
    supplier_delay_multiplier: float = 1.0,
    machine_downtime_multiplier: float = 1.0,
    workforce_reduction: float = 0.0,
    quality_failure_increase: float = 0.0,
    focus_cell: str = "All Production Cells",
) -> pd.DataFrame:
    """Apply a disruption scenario and recalculate operational risk metrics."""
    scenario = df.copy()

    if focus_cell != "All Production Cells":
        focus_mask = scenario["Production_Cell"].eq(focus_cell)
    else:
        focus_mask = pd.Series(True, index=scenario.index)

    # Different production cells react differently to supplier disruptions.
    supplier_sensitivity = {
    "Machining": 1.10,
    "Avionics Assembly": 1.15,
    "Systems Integration": 1.12,
    "Inspection": 0.75,
    "Surface Treatment": 1.05,
    "Final Assembly": 1.18,
    }

    sensitivity = scenario["Production_Cell"].map(supplier_sensitivity).fillna(1.0)

    scenario.loc[focus_mask, "Supplier_Risk"] = (
        scenario.loc[focus_mask, "Supplier_Risk"]
        * supplier_delay_multiplier
        * sensitivity.loc[focus_mask]
    ).clip(0, 1)

    # Workforce reductions affect labor-heavy cells more strongly.
    labor_sensitivity = {
    "Machining": 1.00,
    "Avionics Assembly": 1.05,
    "Systems Integration": 1.10,
    "Inspection": 1.00,
    "Surface Treatment": 0.95,
    "Final Assembly": 1.15,
    }

    labor_factor = scenario["Production_Cell"].map(labor_sensitivity).fillna(1.0)

    scenario.loc[focus_mask, "Workforce_Availability"] = (
        scenario.loc[focus_mask, "Workforce_Availability"]
        - workforce_reduction * labor_factor.loc[focus_mask]
    ).clip(0.10, 1.0)

    # Machine downtime impacts equipment-heavy cells more heavily.
    machine_sensitivity = {
        "Machining": 1.45,
        "Surface Treatment": 1.25,
        "Final Assembly": 1.05,
        "Avionics Assembly": 0.90,
        "Systems Integration": 0.85,
        "Inspection": 0.75,
    }

    machine_factor = scenario["Production_Cell"].map(machine_sensitivity).fillna(1.0)

    downtime_probability = (
        0.04 * machine_downtime_multiplier * machine_factor
    ).clip(0, 0.65)

    downtime_mask = (
        focus_mask
        & scenario["Machine_Status"].isin(["Operational", "Degraded"])
        & ((scenario.index % 100) / 100 < downtime_probability)
    )

    scenario.loc[
        downtime_mask & scenario["Machine_Status"].eq("Operational"),
        "Machine_Status",
    ] = "Degraded"

    scenario.loc[
        downtime_mask & scenario["Machine_Status"].eq("Degraded"),
        "Machine_Status",
    ] = "Down"

    # Quality issues affect inspection, surface treatment, and final assembly more strongly.
    quality_sensitivity = {
    "Inspection": 1.35,
    "Surface Treatment": 1.25,
    "Final Assembly": 1.15,
    "Systems Integration": 1.05,
    "Avionics Assembly": 0.90,
    "Machining": 0.95,
    }

    quality_factor = scenario["Production_Cell"].map(quality_sensitivity).fillna(1.0)

    quality_probability = (
        0.05 * quality_failure_increase * quality_factor
    ).clip(0, 0.70)

    quality_mask = (
        focus_mask
        & scenario["Quality_Flag"].eq("Pass")
        & ((scenario.index % 100) / 100 < quality_probability)
    )

    scenario.loc[quality_mask, "Quality_Flag"] = "Inspection Hold"

    scrap_mask = (
        focus_mask
        & scenario["Quality_Flag"].eq("Inspection Hold")
        & quality_failure_increase.ge(1.5)
        if hasattr(quality_failure_increase, "ge")
        else (
            focus_mask
            & scenario["Quality_Flag"].eq("Inspection Hold")
            & (quality_failure_increase >= 1.5)
            & (scenario.index % 17 == 0)
        )
    )

    scenario.loc[scrap_mask, "Quality_Flag"] = "Scrap Risk"

    scenario["Defect_Type"] = np.where(
        scenario["Quality_Flag"].eq("Pass"),
        "None",
        scenario["Defect_Type"],
    )

    inventory_shortage = scenario["Inventory_Level"] < scenario["Reorder_Point"]

    status_delay = scenario["Machine_Status"].map(
        {
            "Operational": 2,
            "Degraded": 14,
            "Down": 40,
        }
    )

    quality_delay = scenario["Quality_Flag"].map(
        {
            "Pass": 0,
            "Rework": 12,
            "Inspection Hold": 22,
            "Scrap Risk": 36,
        }
    )

    inventory_delay = np.where(
        inventory_shortage,
        20,
        np.where(scenario["Inventory_Level"] < 90, 7, 1),
    )

    supplier_delay = (
        scenario["Supplier_Risk"] * 16
        + np.where(scenario["Single_Source_Supplier"].eq("Yes"), 10, 0)
        + np.where(scenario["Critical_Material_Flag"].eq("Yes"), 7, 0)
    ).round(0)

    workforce_delay = ((1 - scenario["Workforce_Availability"]) * 26).round(0)

    inspection_delay = np.where(
        scenario["Quality_Flag"].isin(["Inspection Hold", "Scrap Risk"]),
        scenario["Inspection_Backlog_Hours"] * 0.75,
        scenario["Inspection_Backlog_Hours"] * 0.15,
    ).round(0)

    scenario["Estimated_Delay_Hours"] = (
        status_delay
        + quality_delay
        + inventory_delay
        + supplier_delay
        + workforce_delay
        + inspection_delay
    ).astype(int)

    scenario["Contract_Delivery_Risk"] = np.where(
        scenario["Estimated_Delay_Hours"] / 24
        > scenario["Delivery_Deadline_Days"] * 0.35,
        "Elevated",
        "Controlled",
    )

    scenario["Operational_Risk"] = (
        scenario["Supplier_Risk"] * 24
        + np.where(inventory_shortage, 15, 0)
        + np.where(scenario["Single_Source_Supplier"].eq("Yes"), 8, 0)
        + np.where(scenario["Critical_Material_Flag"].eq("Yes"), 6, 0)
        + scenario["Estimated_Delay_Hours"] * 0.55
        + (1 - scenario["First_Pass_Yield"]) * 35
        + (6 - scenario["Mission_Priority"]) * 1.5
    ).clip(0, 100).round(1)

    scenario["Readiness_Impact"] = (
        scenario["Operational_Risk"]
        * (scenario["Mission_Priority"] / 5)
        * np.where(scenario["Contract_Delivery_Risk"].eq("Elevated"), 1.15, 1.0)
    ).clip(0, 100).round(1)

    scenario["Risk_Level"] = pd.cut(
        scenario["Operational_Risk"],
        bins=[-1, 35, 65, 100],
        labels=["Low", "Moderate", "High"],
    ).astype(str)

    scenario["Recovery_Confidence"] = (
        0.35
        + np.where(scenario["Alternate_Route_Available"].eq("Yes"), 0.18, 0)
        + np.where(scenario["Alternate_Supplier_Available"].eq("Yes"), 0.18, 0)
        + np.where(scenario["Overtime_Available"].eq("Yes"), 0.14, 0)
        - np.where(scenario["Single_Source_Supplier"].eq("Yes"), 0.10, 0)
        - np.where(scenario["Quality_Flag"].eq("Scrap Risk"), 0.12, 0)
    ).clip(0.15, 0.95).round(2)

    scenario["Estimated_Recovery_Hours"] = (
        scenario["Estimated_Delay_Hours"]
        * (1 - scenario["Recovery_Confidence"] * 0.45)
    ).round(0).astype(int)

    return scenario