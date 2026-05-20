"""Synthetic defense manufacturing operations data generator."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RNG_SEED = 42


def generate_manufacturing_data(rows: int = 300, seed: int = RNG_SEED) -> pd.DataFrame:
    """Generate realistic synthetic manufacturing operations data.
    """
    rng = np.random.default_rng(seed)

    programs = [
        "Tactical UAV Production",
        "Radar Modernization",
        "Avionics Retrofit",
        "Ground Sensor Platform",
        "Mission Systems Upgrade",
    ]

    platforms = [
        "UAV",
        "Radar System",
        "Ground Vehicle",
        "Sensor Package",
        "Avionics Kit",
    ]

    production_cells = [
        "Machining",
        "Avionics Assembly",
        "Systems Integration",
        "Inspection",
        "Surface Treatment",
        "Final Assembly",
    ]

    operation_steps = [
        "Material Prep",
        "CNC Machining",
        "Surface Finish",
        "Electronics Install",
        "Subsystem Integration",
        "Quality Inspection",
        "Final Assembly",
        "Acceptance Test",
    ]

    components = [
        "Radar Housing",
        "Guidance Module",
        "Flight Control Bracket",
        "Sensor Mount",
        "Power Unit",
        "Actuator Assembly",
        "Thermal Shield",
        "Navigation Board",
    ]

    suppliers = [
        "AeroForge",
        "Delta Circuits",
        "Vector Metals",
        "Northline Components",
        "Orion Plating",
        "Summit Electronics",
    ]

    machine_statuses = ["Operational", "Degraded", "Down"]
    quality_flags = ["Pass", "Rework", "Inspection Hold", "Scrap Risk"]
    defect_types = [
        "Dimensional",
        "Surface Finish",
        "Electrical",
        "Foreign Object Debris",
        "Coating Defect",
    ]

    cell_profiles = {
        "Machining": {
            "machine_weights": [0.55, 0.30, 0.15],
            "quality_weights": [0.78, 0.12, 0.08, 0.02],
            "supplier_risk_range": (0.10, 0.65),
            "workforce_range": (0.72, 1.00),
            "inspection_backlog": (1, 10),
            "yield_range": (0.84, 0.98),
        },
        "Avionics Assembly": {
            "machine_weights": [0.72, 0.22, 0.06],
            "quality_weights": [0.68, 0.18, 0.10, 0.04],
            "supplier_risk_range": (0.35, 0.95),
            "workforce_range": (0.68, 0.96),
            "inspection_backlog": (3, 16),
            "yield_range": (0.80, 0.96),
        },
        "Systems Integration": {
            "machine_weights": [0.75, 0.20, 0.05],
            "quality_weights": [0.70, 0.16, 0.10, 0.04],
            "supplier_risk_range": (0.25, 0.85),
            "workforce_range": (0.65, 0.94),
            "inspection_backlog": (2, 18),
            "yield_range": (0.82, 0.97),
        },
        "Inspection": {
            "machine_weights": [0.90, 0.08, 0.02],
            "quality_weights": [0.58, 0.18, 0.18, 0.06],
            "supplier_risk_range": (0.05, 0.45),
            "workforce_range": (0.70, 0.98),
            "inspection_backlog": (10, 30),
            "yield_range": (0.72, 0.92),
        },
        "Surface Treatment": {
            "machine_weights": [0.68, 0.24, 0.08],
            "quality_weights": [0.62, 0.18, 0.15, 0.05],
            "supplier_risk_range": (0.10, 0.60),
            "workforce_range": (0.75, 1.00),
            "inspection_backlog": (4, 20),
            "yield_range": (0.78, 0.95),
        },
        "Final Assembly": {
            "machine_weights": [0.78, 0.17, 0.05],
            "quality_weights": [0.72, 0.14, 0.10, 0.04],
            "supplier_risk_range": (0.20, 0.75),
            "workforce_range": (0.60, 0.90),
            "inspection_backlog": (3, 15),
            "yield_range": (0.82, 0.97),
        },
    }

    records = []

    selected_cells = rng.choice(production_cells, rows)

    for i, cell in enumerate(selected_cells):
        profile = cell_profiles[cell]

        quality_flag = rng.choice(
            quality_flags,
            p=profile["quality_weights"],
        )

        defect_type = "None" if quality_flag == "Pass" else rng.choice(defect_types)

        record = {
            "Work_Order_ID": f"WO-{10000 + i}",
            "Program_Name": rng.choice(programs),
            "Platform": rng.choice(platforms),
            "Production_Cell": cell,
            "Operation_Step": rng.choice(operation_steps),
            "Component_Type": rng.choice(components),
            "Supplier": rng.choice(suppliers),
            "Machine_ID": f"M-{rng.integers(1, 24):02d}",
            "Machine_Status": rng.choice(
                machine_statuses,
                p=profile["machine_weights"],
            ),
            "Quality_Flag": quality_flag,
            "Defect_Type": defect_type,
            "Inventory_Level": rng.integers(5, 190),
            "Reorder_Point": rng.integers(25, 75),
            "Supplier_Risk": round(
                rng.uniform(*profile["supplier_risk_range"]),
                2,
            ),
            "Supplier_Lead_Time_Days": rng.integers(5, 60),
            "Single_Source_Supplier": rng.choice(
                ["Yes", "No"],
                p=[0.28, 0.72],
            ),
            "Critical_Material_Flag": rng.choice(
                ["Yes", "No"],
                p=[0.36, 0.64],
            ),
            "Cycle_Time_Hours": round(rng.uniform(2.0, 28.0), 1),
            "Queue_Time_Hours": round(rng.uniform(1.0, 36.0), 1),
            "Labor_Hours_Required": round(rng.uniform(1.5, 22.0), 1),
            "Workforce_Availability": round(
                rng.uniform(*profile["workforce_range"]),
                2,
            ),
            "Inspection_Backlog_Hours": round(
                rng.uniform(*profile["inspection_backlog"]),
                1,
            ),
            "First_Pass_Yield": round(
                rng.uniform(*profile["yield_range"]),
                2,
            ),
            "Mission_Priority": rng.integers(1, 6),
            "Delivery_Deadline_Days": rng.integers(3, 45),
            "Recovery_Cost": rng.integers(2500, 75000),
            "Alternate_Route_Available": rng.choice(
                ["Yes", "No"],
                p=[0.63, 0.37],
            ),
            "Alternate_Supplier_Available": rng.choice(
                ["Yes", "No"],
                p=[0.48, 0.52],
            ),
            "Overtime_Available": rng.choice(
                ["Yes", "No"],
                p=[0.68, 0.32],
            ),
        }

        records.append(record)

    df = pd.DataFrame(records)

    inventory_shortage = df["Inventory_Level"] < df["Reorder_Point"]

    status_delay = df["Machine_Status"].map(
        {
            "Operational": 2,
            "Degraded": 14,
            "Down": 40,
        }
    )

    quality_delay = df["Quality_Flag"].map(
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
        np.where(df["Inventory_Level"] < 90, 7, 1),
    )

    supplier_delay = (
        df["Supplier_Risk"] * 16
        + np.where(df["Single_Source_Supplier"].eq("Yes"), 10, 0)
        + np.where(df["Critical_Material_Flag"].eq("Yes"), 7, 0)
    ).round(0)

    workforce_delay = ((1 - df["Workforce_Availability"]) * 26).round(0)

    inspection_delay = np.where(
        df["Quality_Flag"].isin(["Inspection Hold", "Scrap Risk"]),
        df["Inspection_Backlog_Hours"] * 0.75,
        df["Inspection_Backlog_Hours"] * 0.15,
    ).round(0)

    df["Estimated_Delay_Hours"] = (
        status_delay
        + quality_delay
        + inventory_delay
        + supplier_delay
        + workforce_delay
        + inspection_delay
    ).astype(int)

    df["Contract_Delivery_Risk"] = np.where(
        df["Estimated_Delay_Hours"] / 24 > df["Delivery_Deadline_Days"] * 0.35,
        "Elevated",
        "Controlled",
    )

    df["Operational_Risk"] = (
        df["Supplier_Risk"] * 24
        + np.where(inventory_shortage, 15, 0)
        + np.where(df["Single_Source_Supplier"].eq("Yes"), 8, 0)
        + np.where(df["Critical_Material_Flag"].eq("Yes"), 6, 0)
        + df["Estimated_Delay_Hours"] * 0.55
        + (1 - df["First_Pass_Yield"]) * 35
        + (6 - df["Mission_Priority"]) * 1.5
    ).clip(0, 100).round(1)

    df["Readiness_Impact"] = (
        df["Operational_Risk"]
        * (df["Mission_Priority"] / 5)
        * np.where(df["Contract_Delivery_Risk"].eq("Elevated"), 1.15, 1.0)
    ).clip(0, 100).round(1)

    df["Risk_Level"] = pd.cut(
        df["Operational_Risk"],
        bins=[-1, 35, 65, 100],
        labels=["Low", "Moderate", "High"],
    ).astype(str)

    df["Recovery_Confidence"] = (
        0.35
        + np.where(df["Alternate_Route_Available"].eq("Yes"), 0.18, 0)
        + np.where(df["Alternate_Supplier_Available"].eq("Yes"), 0.18, 0)
        + np.where(df["Overtime_Available"].eq("Yes"), 0.14, 0)
        - np.where(df["Single_Source_Supplier"].eq("Yes"), 0.10, 0)
        - np.where(df["Quality_Flag"].eq("Scrap Risk"), 0.12, 0)
    ).clip(0.15, 0.95).round(2)

    df["Estimated_Recovery_Hours"] = (
        df["Estimated_Delay_Hours"]
        * (1 - df["Recovery_Confidence"] * 0.45)
    ).round(0).astype(int)

    return df


if __name__ == "__main__":
    output_path = Path("data/manufacturing_operations.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = generate_manufacturing_data()
    data.to_csv(output_path, index=False)

    print(f"Generated {output_path}")
