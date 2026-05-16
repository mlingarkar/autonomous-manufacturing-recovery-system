"""Visualization generation for the manufacturing recovery system."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def ensure_output_dirs() -> None:
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)


def plot_disruption_heatmap(df: pd.DataFrame) -> None:
    pivot = pd.pivot_table(
        df,
        values="Operational_Risk",
        index="Production_Cell",
        columns="Primary_Disruption",
        aggfunc="mean",
        fill_value=0,
    )
    plt.figure(figsize=(11, 6))
    plt.imshow(pivot.values, aspect="auto")
    plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=35, ha="right")
    plt.yticks(range(len(pivot.index)), pivot.index)
    plt.colorbar(label="Average Operational Risk")
    plt.title("Disruption Risk Heatmap by Production Cell")
    plt.tight_layout()
    plt.savefig("outputs/figures/disruption_heatmap.png", dpi=160)
    plt.close()


def plot_bottlenecks(summary: pd.DataFrame) -> None:
    plt.figure(figsize=(10, 6))
    plt.bar(summary["Production_Cell"], summary["Avg_Delay_Hours"])
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Average Delay Hours")
    plt.title("Production Bottlenecks by Average Delay")
    plt.tight_layout()
    plt.savefig("outputs/figures/production_bottlenecks.png", dpi=160)
    plt.close()


def plot_readiness_impact(df: pd.DataFrame) -> None:
    readiness = df.groupby("Production_Cell")["Readiness_Impact"].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    plt.plot(readiness.index, readiness.values, marker="o")
    plt.xticks(rotation=30, ha="right")
    plt.ylabel("Average Readiness Impact")
    plt.title("Mission Readiness Impact by Production Cell")
    plt.tight_layout()
    plt.savefig("outputs/figures/readiness_impact.png", dpi=160)
    plt.close()


def plot_cascading_network(df: pd.DataFrame) -> None:
    top = df.sort_values("Readiness_Impact", ascending=False).head(35)
    graph = nx.DiGraph()

    for _, row in top.iterrows():
        supplier = f"Supplier: {row['Supplier']}"
        cell = f"Cell: {row['Production_Cell']}"
        component = f"Component: {row['Component_Type']}"
        mission = f"Mission Priority {row['Mission_Priority']}"
        graph.add_edge(supplier, cell, weight=row["Supplier_Risk"])
        graph.add_edge(cell, component, weight=row["Operational_Risk"])
        graph.add_edge(component, mission, weight=row["Readiness_Impact"])

    plt.figure(figsize=(14, 9))
    pos = nx.spring_layout(graph, seed=42, k=0.9)
    sizes = [350 + graph.degree(node) * 90 for node in graph.nodes]
    nx.draw_networkx_nodes(graph, pos, node_size=sizes, alpha=0.85)
    nx.draw_networkx_edges(graph, pos, arrows=True, alpha=0.35)
    nx.draw_networkx_labels(graph, pos, font_size=7)
    plt.title("Cascading Manufacturing Disruption Network")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("outputs/figures/cascading_disruption_network.png", dpi=160)
    plt.close()


def generate_all_visuals(df: pd.DataFrame, summary: pd.DataFrame) -> None:
    ensure_output_dirs()
    plot_disruption_heatmap(df)
    plot_bottlenecks(summary)
    plot_readiness_impact(df)
    plot_cascading_network(df)
