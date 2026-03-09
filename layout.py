from __future__ import annotations

from dash import dcc, html

from .constants import DEFAULT_FORECAST_MODELS, FORECAST_MODEL_OPTIONS


def _card(title: str, value_id: str) -> html.Div:
    return html.Div(
        [
            html.Div(title, style={"fontSize": "12px", "color": "#666"}),
            html.Div(id=value_id, style={"fontSize": "20px", "fontWeight": "bold"}),
        ],
        style={"border": "1px solid #ddd", "borderRadius": "8px", "padding": "12px", "backgroundColor": "white"},
    )


def create_layout(df) -> html.Div:
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    type_options = [{"label": "All", "value": "all"}] + [
        {"label": str(t).title(), "value": str(t)} for t in sorted(df["type"].astype(str).unique())
    ]
    region_options = [{"label": str(r), "value": str(r)} for r in sorted(df["region"].astype(str).unique())]
    default_regions = [r["value"] for r in region_options]

    return html.Div(
        [
            html.H1("US Avocado Sales Dashboard", style={"marginBottom": "4px"}),
            html.Div("Built from HW1 analysis logic (2015-2023)", style={"marginBottom": "16px", "color": "#666"}),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Date Range"),
                            dcc.DatePickerRange(
                                id="date-range",
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=min_date,
                                end_date=max_date,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Type"),
                            dcc.Dropdown(id="type-filter", options=type_options, value="all", clearable=False),
                        ],
                        style={"minWidth": "180px"},
                    ),
                    html.Div(
                        [
                            html.Label("Regions"),
                            dcc.Dropdown(
                                id="region-filter",
                                options=region_options,
                                value=default_regions,
                                multi=True,
                            ),
                        ],
                        style={"minWidth": "320px"},
                    ),
                    html.Div(
                        [
                            html.Label("Top N"),
                            dcc.Slider(id="top-n", min=5, max=20, step=1, value=10, marks={i: str(i) for i in [5, 10, 15, 20]}),
                        ],
                        style={"width": "240px", "paddingTop": "4px"},
                    ),
                    html.Div(
                        [
                            html.Label("Forecast Models"),
                            dcc.Checklist(
                                id="forecast-models",
                                options=FORECAST_MODEL_OPTIONS,
                                value=DEFAULT_FORECAST_MODELS,
                                inline=True,
                            ),
                        ],
                        style={"paddingTop": "2px"},
                    ),
                    html.Button("Reset filters", id="reset-filters", n_clicks=0),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "2fr 1fr 3fr 2fr 3fr auto",
                    "gap": "12px",
                    "alignItems": "end",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                [
                    _card("Rows", "kpi-rows"),
                    _card("Regions", "kpi-regions"),
                    _card("Types", "kpi-types"),
                    _card("Date Range", "kpi-dates"),
                    _card("Organic Premium", "kpi-premium"),
                    _card("Price-Volume Corr", "kpi-corr"),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(6, 1fr)", "gap": "10px", "marginBottom": "20px"},
            ),
            dcc.Tabs(
                id="main-tabs",
                value="tab-overview",
                children=[
                    dcc.Tab(
                        label="Overview",
                        value="tab-overview",
                        children=[
                            html.Div(id="missing-summary", style={"margin": "12px 0"}),
                            html.Div(
                                [
                                    dcc.Graph(id="fig-overview-trend"),
                                    dcc.Graph(id="fig-overview-type"),
                                    dcc.Graph(id="fig-overview-season"),
                                    dcc.Graph(id="fig-overview-value"),
                                ],
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="Price Explorer",
                        value="tab-price",
                        children=[
                            html.Div(
                                [
                                    dcc.Graph(id="fig-price-dist"),
                                    dcc.Graph(id="fig-price-type-box"),
                                    dcc.Graph(id="fig-price-type-mean"),
                                    dcc.Graph(id="fig-price-trend"),
                                    dcc.Graph(id="fig-price-seasonality"),
                                ],
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="Region & Volume",
                        value="tab-region",
                        children=[
                            html.Div(
                                [
                                    dcc.Graph(id="fig-region-rank"),
                                    dcc.Graph(id="fig-region-scatter"),
                                    dcc.Graph(id="fig-region-bag-total"),
                                    dcc.Graph(id="fig-region-bag-type"),
                                    dcc.Graph(id="fig-region-value"),
                                ],
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="Deep Dive",
                        value="tab-deep",
                        children=[
                            html.Div(
                                [
                                    dcc.Graph(id="fig-deep-corr"),
                                    dcc.Graph(id="fig-deep-pairs"),
                                    dcc.Graph(id="fig-deep-forecast"),
                                    dcc.Graph(id="fig-deep-cagr"),
                                    dcc.Graph(id="fig-deep-type-year"),
                                    html.Div(id="mae-summary", style={"padding": "10px 0"}),
                                ],
                                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "10px"},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="Executive Summary",
                        value="tab-summary",
                        children=[
                            html.Div(
                                [
                                    html.H3("Key Findings"),
                                    html.Ul(
                                        [
                                            html.Li(id="summary-find-1"),
                                            html.Li(id="summary-find-2"),
                                            html.Li(id="summary-find-3"),
                                            html.Li(id="summary-find-4"),
                                        ]
                                    ),
                                    html.H3("Business Recommendations"),
                                    html.Ul(
                                        [
                                            html.Li(id="summary-rec-1"),
                                            html.Li(id="summary-rec-2"),
                                            html.Li(id="summary-rec-3"),
                                        ]
                                    ),
                                ],
                                style={"padding": "16px"},
                            )
                        ],
                    ),
                ],
            ),
        ],
        style={"padding": "20px", "fontFamily": "Arial, sans-serif", "backgroundColor": "#f7f7f7"},
    )
