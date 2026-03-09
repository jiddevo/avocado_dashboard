from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .constants import MONTH_ORDER


def fig_price_hist_box(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Price Distribution", "Price Box Plot"))
    fig.add_trace(
        go.Histogram(x=df["average_price"], nbinsx=35, marker_color="seagreen", name="avg price"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Box(x=df["average_price"], marker_color="orange", name="avg price", boxpoints="outliers"),
        row=1,
        col=2,
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=60, b=30), showlegend=False)
    return fig


def fig_type_box(df: pd.DataFrame) -> go.Figure:
    fig = px.box(
        df,
        x="type",
        y="average_price",
        color="type",
        title="Weekly Average Price Distribution by Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=50, b=30))
    return fig


def fig_type_mean(type_stats_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        type_stats_df,
        x="type",
        y="mean",
        color="type",
        title="Mean Weekly Average Price by Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=50, b=30), showlegend=False)
    return fig


def fig_monthly_trend(monthly_all: pd.DataFrame, monthly_type: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly_all["date"], y=monthly_all["average_price"], mode="lines", name="overall"))
    for t in monthly_type["type"].astype(str).unique():
        part = monthly_type[monthly_type["type"].astype(str) == t]
        fig.add_trace(go.Scatter(x=part["date"], y=part["average_price"], mode="lines", name=t))
    fig.update_layout(
        title="U.S. Monthly Average Avocado Price Trend by Type",
        height=420,
        margin=dict(l=30, r=20, t=50, b=30),
        xaxis_title="Date",
        yaxis_title="Average Price",
    )
    return fig


def fig_seasonality(month_avg: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        month_avg,
        x="month_name",
        y="average_price",
        title="Seasonality: Mean Price by Calendar Month",
        category_orders={"month_name": MONTH_ORDER},
        color_discrete_sequence=["teal"],
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=50, b=30), showlegend=False)
    return fig


def fig_region_top_bottom(top_df: pd.DataFrame, bottom_df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Top Regions by Mean Price", "Bottom Regions by Mean Price"),
        horizontal_spacing=0.1,
    )
    fig.add_trace(
        go.Bar(x=top_df["average_price"], y=top_df["region"].astype(str), orientation="h", marker_color="navy"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=bottom_df["average_price"], y=bottom_df["region"].astype(str), orientation="h", marker_color="tomato"),
        row=1,
        col=2,
    )
    fig.update_layout(height=520, margin=dict(l=30, r=20, t=60, b=30), showlegend=False)
    return fig


def fig_volume_vs_price(plot_df: pd.DataFrame, corr: float) -> go.Figure:
    fig = px.scatter(
        plot_df,
        x="total_volume",
        y="average_price",
        color="type",
        opacity=0.35,
        title=f"Volume vs Price (corr={corr:.3f})",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_xaxes(type="log", title="Total Volume (log scale)")
    fig.update_yaxes(title="Average Price")

    x = np.log10(plot_df["total_volume"].values)
    y = plot_df["average_price"].values
    if len(x) > 1 and np.isfinite(x).all() and np.isfinite(y).all():
        m, b = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = m * x_line + b
        fig.add_trace(
            go.Scatter(
                x=10 ** x_line,
                y=y_line,
                mode="lines",
                name="trend",
                line=dict(color="black", width=2),
            )
        )

    fig.update_layout(height=440, margin=dict(l=30, r=20, t=50, b=30))
    return fig


def fig_bag_totals(bag_totals_df: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        bag_totals_df,
        x="bag_size",
        y="units",
        title="Total Bag Units Sold by Size",
        color_discrete_sequence=["#2E8B57"],
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=50, b=30), showlegend=False)
    return fig


def fig_bag_by_type(bag_long: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        bag_long,
        x="bag_size",
        y="units",
        color="type",
        barmode="group",
        title="Bag Units Sold by Size and Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=50, b=30))
    return fig


def fig_value_proxy(top_by_type: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        top_by_type,
        x="value_proxy",
        y=top_by_type["region"].astype(str),
        color="type",
        orientation="h",
        title="Top Regions by Value Proxy (Average Price x Total Volume)",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=520, margin=dict(l=30, r=20, t=50, b=30))
    return fig


def fig_corr_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    fig = px.imshow(
        corr_df,
        color_continuous_scale="YlGnBu",
        zmin=0,
        zmax=1,
        title="Regional Similarity: Correlation of Monthly Price Patterns",
    )
    fig.update_layout(height=620, margin=dict(l=30, r=20, t=50, b=30))
    return fig


def fig_top_pairs(pairs_df: pd.DataFrame, top_n: int = 8) -> go.Figure:
    top_pairs = pairs_df.head(top_n).copy()
    top_pairs["pair"] = top_pairs.apply(lambda r: f"{r['region_a']} vs {r['region_b']}", axis=1)
    fig = px.bar(
        top_pairs,
        x="corr",
        y="pair",
        orientation="h",
        title="Top Similar Region Pairs",
        color_discrete_sequence=["#2a9d8f"],
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=50, b=30), showlegend=False)
    return fig


def fig_forecast(results_df: pd.DataFrame, selected_models: list[str]) -> go.Figure:
    plot_df = results_df.reset_index().rename(columns={"index": "date"})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df["date"], y=plot_df["actual"], mode="lines", name="actual", line=dict(color="black", width=3)))

    for m in selected_models:
        if m in plot_df.columns:
            fig.add_trace(go.Scatter(x=plot_df["date"], y=plot_df[m], mode="lines", name=m))

    fig.update_layout(
        title="Forecast Backtest for 2023 Monthly Average Prices",
        height=420,
        margin=dict(l=30, r=20, t=50, b=30),
        xaxis_title="Date",
        yaxis_title="Average Price",
    )
    return fig


def fig_cagr_bars(conv_top: pd.DataFrame, org_top: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Top 5 Conventional CAGR Regions", "Top 5 Organic CAGR Regions"),
        horizontal_spacing=0.12,
    )
    c1 = conv_top.sort_values("cagr")
    c2 = org_top.sort_values("cagr")
    fig.add_trace(
        go.Bar(x=c1["cagr"], y=c1["region"].astype(str), orientation="h", marker_color="steelblue"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=c2["cagr"], y=c2["region"].astype(str), orientation="h", marker_color="salmon"),
        row=1,
        col=2,
    )
    fig.update_layout(height=480, margin=dict(l=30, r=20, t=60, b=30), showlegend=False)
    return fig


def fig_type_year_volume(type_year: pd.DataFrame) -> go.Figure:
    fig = px.line(
        type_year,
        x="year",
        y="total_volume",
        color="type",
        markers=True,
        title="Yearly Total Avocado Volume by Type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(height=420, margin=dict(l=30, r=20, t=50, b=30))
    return fig
