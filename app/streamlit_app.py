"""Streamlit dashboard for the Autonomous Manufacturing Recovery System."""

from __future__ import annotations

import sys
from pathlib import Path

import networkx as nx
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from data_generator import generate_manufacturing_data
from disruption_engine import score_disruptions, summarize_bottlenecks
from recovery_engine import generate_recovery_plan
from simulation_engine import apply_scenario


st.set_page_config(
    page_title="Autonomous Manufacturing Recovery System",
    layout="wide",
)

st.title("Autonomous Manufacturing Recovery System")
st.caption(
    "AI-assisted operational recovery and replanning demonstration using synthetic defense manufacturing data."
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load generated manufacturing data, or generate it if missing."""
    data_path = ROOT / "data" / "manufacturing_operations.csv"

    if data_path.exists():
        return pd.read_csv(data_path)

    return generate_manufacturing_data(rows=300)


LABELS = {
    "Production_Cell": "Production Cell",
    "Avg_Delay_Hours": "Average Delay Hours",
    "Avg_Risk": "Average Risk",
    "High_Risk_Count": "High-Risk Count",
    "Avg_Readiness_Impact": "Average Readiness Impact",
    "Primary_Disruption": "Primary Disruption",
    "Count": "Count",
    "Readiness_Impact_Delta": "Readiness Impact Change",
    "Delay_Delta": "Delay Change",
    "Risk_Delta": "Risk Change",
    "Estimated_Delay_Hours": "Estimated Delay Hours",
    "Readiness_Impact": "Readiness Impact",
    "Operational_Risk": "Operational Risk",
    "Risk_Level": "Risk Level",
    "Work_Order_ID": "Work Order ID",
    "Component_Type": "Component Type",
}


base_df = load_data()

st.sidebar.header("Scenario Simulation")

focus_cell = st.sidebar.selectbox(
    "Disruption focus area",
    ["All Production Cells"] + sorted(base_df["Production_Cell"].unique().tolist()),
)

supplier_delay = st.sidebar.slider(
    "Supplier risk multiplier",
    min_value=1.0,
    max_value=2.5,
    value=1.0,
    step=0.1,
)

machine_downtime = st.sidebar.slider(
    "Machine downtime multiplier",
    min_value=1.0,
    max_value=3.0,
    value=1.0,
    step=0.1,
)

workforce_reduction = st.sidebar.slider(
    "Workforce availability reduction",
    min_value=0.0,
    max_value=0.40,
    value=0.0,
    step=0.05,
)

quality_increase = st.sidebar.slider(
    "Quality hold increase",
    min_value=0.0,
    max_value=2.0,
    value=0.0,
    step=0.1,
)

scenario_df = apply_scenario(
    base_df,
    supplier_delay_multiplier=supplier_delay,
    machine_downtime_multiplier=machine_downtime,
    workforce_reduction=workforce_reduction,
    quality_failure_increase=quality_increase,
    focus_cell=focus_cell,
)

scored = score_disruptions(scenario_df)
summary = summarize_bottlenecks(scored)

baseline_scored = score_disruptions(base_df)
baseline_summary = summarize_bottlenecks(baseline_scored)[
    [
        "Production_Cell",
        "Avg_Readiness_Impact",
        "Avg_Delay_Hours",
        "Avg_Risk",
    ]
]

impact_summary = summary.merge(
    baseline_summary,
    on="Production_Cell",
    suffixes=("", "_Baseline"),
)

impact_summary["Readiness_Impact_Delta"] = (
    impact_summary["Avg_Readiness_Impact"]
    - impact_summary["Avg_Readiness_Impact_Baseline"]
).round(2)

impact_summary["Delay_Delta"] = (
    impact_summary["Avg_Delay_Hours"] - impact_summary["Avg_Delay_Hours_Baseline"]
).round(2)

impact_summary["Risk_Delta"] = (
    impact_summary["Avg_Risk"] - impact_summary["Avg_Risk_Baseline"]
).round(2)

impact_summary = impact_summary.sort_values(
    "Readiness_Impact_Delta",
    ascending=False,
)

recovery_plan = generate_recovery_plan(scored)

avg_readiness = scored["Readiness_Impact"].mean()
high_risk_count = int((scored["Risk_Level"] == "High").sum())
avg_delay = scored["Estimated_Delay_Hours"].mean()
critical_cell = impact_summary.iloc[0]["Production_Cell"]

display_cell = str(critical_cell).replace("Avionics Assembly", "Avionics")

col1, col2, col3, col4 = st.columns([1.1, 1.1, 1.1, 1.4])

col1.metric("Avg Readiness Impact", f"{avg_readiness:.1f}")
col2.metric("High-Risk Work Orders", high_risk_count)
col3.metric("Avg Delay", f"{avg_delay:.1f} hrs")
col4.metric("Top Impact Cell", display_cell)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Operations Overview",
        "Recovery Plan",
        "Simulation Impact",
        "Disruption Network",
    ]
)

with tab1:
    st.subheader("Production Cell Bottlenecks")

    fig = px.bar(
        summary,
        x="Production_Cell",
        y="Avg_Delay_Hours",
        hover_data=[
            "Avg_Risk",
            "High_Risk_Count",
            "Avg_Readiness_Impact",
        ],
        title="Average Delay by Production Cell",
        labels=LABELS,
    )

    fig.update_layout(
        xaxis_title="Production Cell",
        yaxis_title="Average Delay Hours",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Disruption Mix")

    disruption_counts = scored["Primary_Disruption"].value_counts().reset_index()
    disruption_counts.columns = ["Primary_Disruption", "Count"]

    fig2 = px.pie(
        disruption_counts,
        names="Primary_Disruption",
        values="Count",
        title="Primary Disruption Categories",
        labels=LABELS,
    )

    fig2.update_traces(
        hovertemplate="Primary Disruption: %{label}<br>Count: %{value}<extra></extra>"
    )

    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Autonomous Recovery Recommendations")

    display_cols = [
        "Work_Order_ID",
        "Production_Cell",
        "Component_Type",
        "Primary_Disruption",
        "Estimated_Delay_Hours",
        "Readiness_Impact",
        "Recovery_Priority",
        "Recommended_Action",
    ]

    display_table = recovery_plan[display_cols].head(20).rename(
        columns={
            "Work_Order_ID": "Work Order ID",
            "Production_Cell": "Production Cell",
            "Component_Type": "Component Type",
            "Primary_Disruption": "Primary Disruption",
            "Estimated_Delay_Hours": "Estimated Delay Hours",
            "Readiness_Impact": "Readiness Impact",
            "Recovery_Priority": "Recovery Priority",
            "Recommended_Action": "Recommended Action",
        }
    )

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
    )

    top = recovery_plan.iloc[0]

    st.info(
        f"Highest-priority recovery action: {top['Recommended_Action']} "
        f"This applies to {top['Work_Order_ID']} in {top['Production_Cell']} "
        f"with a readiness impact of {top['Readiness_Impact']}."
    )

with tab3:
    st.subheader("Scenario Impact Compared With Baseline")

    delta_chart = px.bar(
        impact_summary,
        x="Production_Cell",
        y="Readiness_Impact_Delta",
        hover_data=[
            "Delay_Delta",
            "Risk_Delta",
            "Avg_Readiness_Impact",
        ],
        title="Readiness Impact Increase by Production Cell",
        labels=LABELS,
    )

    delta_chart.update_layout(
        xaxis_title="Production Cell",
        yaxis_title="Readiness Impact Change",
    )

    st.plotly_chart(delta_chart, use_container_width=True)

    st.subheader("Risk and Readiness Under Current Scenario")

    fig3 = px.scatter(
        scored,
        x="Estimated_Delay_Hours",
        y="Readiness_Impact",
        size="Operational_Risk",
        color="Risk_Level",
        hover_data=[
            "Work_Order_ID",
            "Production_Cell",
            "Component_Type",
            "Primary_Disruption",
        ],
        title="Operational Risk vs. Readiness Impact",
        labels=LABELS,
    )

    fig3.update_layout(
        xaxis_title="Estimated Delay Hours",
        yaxis_title="Readiness Impact",
        legend_title_text="Risk Level",
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Risk Heatmap")

    heatmap_data = scored[scored["Primary_Disruption"] != "Nominal"]

    heatmap = pd.pivot_table(
        heatmap_data,
        values="Operational_Risk",
        index="Production_Cell",
        columns="Primary_Disruption",
        aggfunc="mean",
        fill_value=0,
    )

    fig4 = px.imshow(
        heatmap,
        aspect="auto",
        color_continuous_scale="Blues",
        labels={
            "x": "Primary Disruption",
            "y": "Production Cell",
            "color": "Average Risk",
        },
        title="Operational Risk Concentration by Production Cell",
    )

    fig4.update_layout(
        xaxis_title="Primary Disruption",
        yaxis_title="Production Cell",
        height=520,
        margin=dict(l=80, r=80, t=80, b=90),
        coloraxis_colorbar=dict(
            title="Average Risk",
            thickness=14,
            len=0.75,
        ),
    )

    fig4.update_xaxes(
        tickangle=0,
        showgrid=False,
    )

    fig4.update_yaxes(
        showgrid=False,
    )

    st.plotly_chart(fig4, use_container_width=True)

with tab4:
    st.subheader("Cascading Disruption Network")

    st.write(
        "This network links suppliers, production cells, components, and mission priority levels "
        "for the highest-impact work orders."
    )

    top_net = scored.sort_values(
        "Readiness_Impact",
        ascending=False,
    ).head(25)

    graph = nx.DiGraph()
    edges = []

    for _, row in top_net.iterrows():
        supplier = f"Supplier: {row['Supplier']}"
        cell = f"Cell: {row['Production_Cell']}"
        component = f"Component: {row['Component_Type']}"
        mission = f"Mission Priority {row['Mission_Priority']}"

        new_edges = [
            (supplier, cell),
            (cell, component),
            (component, mission),
        ]

        edges.extend(new_edges)
        graph.add_edges_from(new_edges)

    st.write(
        f"Network nodes: {graph.number_of_nodes()} | "
        f"Network edges: {graph.number_of_edges()}"
    )

    network_table = pd.DataFrame(
        edges,
        columns=["Source", "Target"],
    ).drop_duplicates()

    st.dataframe(
        network_table,
        use_container_width=True,
        hide_index=True,
    )

st.divider()

st.caption(
    "Disclaimer: This dashboard uses synthetic data only and is intended as a portfolio demonstration, "
    "not as an operational defense system."
)