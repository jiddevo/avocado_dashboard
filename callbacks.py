from __future__ import annotations

from dash import Input, Output, callback, html
import plotly.graph_objects as go

from .charts import (
    fig_bag_by_type,
    fig_bag_totals,
    fig_cagr_bars,
    fig_corr_heatmap,
    fig_forecast,
    fig_monthly_trend,
    fig_price_hist_box,
    fig_region_top_bottom,
    fig_seasonality,
    fig_top_pairs,
    fig_type_box,
    fig_type_mean,
    fig_type_year_volume,
    fig_value_proxy,
    fig_volume_vs_price,
)
from .constants import DEFAULT_FORECAST_MODELS
from .transforms import (
    apply_filters,
    bag_totals_and_long,
    executive_summary_text,
    forecast_backtest,
    get_missing_summary,
    get_overview_stats,
    growth_analysis,
    monthly_trends,
    overview_dashboard_data,
    price_distribution_stats,
    region_rankings,
    regional_competition,
    seasonality,
    type_price_stats,
    value_proxy_by_type,
    volume_price_sample,
)


def _empty_fig(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=title, height=400)
    return fig


def register_callbacks(app, base_df) -> None:
    min_date = base_df["date"].min().date().isoformat()
    max_date = base_df["date"].max().date().isoformat()
    default_regions = sorted(base_df["region"].astype(str).unique().tolist())

    @app.callback(
        Output("date-range", "start_date"),
        Output("date-range", "end_date"),
        Output("type-filter", "value"),
        Output("region-filter", "value"),
        Output("top-n", "value"),
        Output("forecast-models", "value"),
        Input("reset-filters", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_filters(_n_clicks):
        return min_date, max_date, "all", default_regions, 10, DEFAULT_FORECAST_MODELS

    @app.callback(
        Output("kpi-rows", "children"),
        Output("kpi-regions", "children"),
        Output("kpi-types", "children"),
        Output("kpi-dates", "children"),
        Output("kpi-premium", "children"),
        Output("kpi-corr", "children"),
        Output("missing-summary", "children"),
        Output("fig-overview-trend", "figure"),
        Output("fig-overview-type", "figure"),
        Output("fig-overview-season", "figure"),
        Output("fig-overview-value", "figure"),
        Output("fig-price-dist", "figure"),
        Output("fig-price-type-box", "figure"),
        Output("fig-price-type-mean", "figure"),
        Output("fig-price-trend", "figure"),
        Output("fig-price-seasonality", "figure"),
        Output("fig-region-rank", "figure"),
        Output("fig-region-scatter", "figure"),
        Output("fig-region-bag-total", "figure"),
        Output("fig-region-bag-type", "figure"),
        Output("fig-region-value", "figure"),
        Output("fig-deep-corr", "figure"),
        Output("fig-deep-pairs", "figure"),
        Output("fig-deep-forecast", "figure"),
        Output("fig-deep-cagr", "figure"),
        Output("fig-deep-type-year", "figure"),
        Output("mae-summary", "children"),
        Output("summary-find-1", "children"),
        Output("summary-find-2", "children"),
        Output("summary-find-3", "children"),
        Output("summary-find-4", "children"),
        Output("summary-rec-1", "children"),
        Output("summary-rec-2", "children"),
        Output("summary-rec-3", "children"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("type-filter", "value"),
        Input("region-filter", "value"),
        Input("top-n", "value"),
        Input("forecast-models", "value"),
    )
    def update_dashboard(start_date, end_date, avocado_type, regions, top_n, forecast_models):
        fdf = apply_filters(base_df, start_date, end_date, avocado_type, regions)
        if fdf.empty:
            empty = _empty_fig("No data after filters")
            return (
                "0",
                "0",
                "0",
                "No dates",
                "N/A",
                "N/A",
                "No data after filters.",
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                empty,
                "No MAE stats.",
                "No finding (no data).",
                "No finding (no data).",
                "No finding (no data).",
                "No finding (no data).",
                "No recommendation (no data).",
                "No recommendation (no data).",
                "No recommendation (no data).",
            )

        stats = get_overview_stats(fdf)
        type_stats_df, premium = type_price_stats(fdf)
        _, corr = volume_price_sample(fdf)
        missing_df = get_missing_summary(fdf)

        missing_summary = html.Table(
            [
                html.Thead(html.Tr([html.Th("Column"), html.Th("Missing"), html.Th("Share")])),
                html.Tbody(
                    [
                        html.Tr(
                            [
                                html.Td(r["column"]),
                                html.Td(f"{int(r['missing_count']):,}"),
                                html.Td(f"{100*r['missing_share']:.2f}%"),
                            ]
                        )
                        for _, r in missing_df.iterrows()
                    ]
                ),
            ],
            style={"width": "420px", "backgroundColor": "white", "border": "1px solid #ddd"},
        )

        monthly_all, monthly_type = monthly_trends(fdf)
        month_avg = seasonality(fdf)
        top_df, bottom_df, _ = region_rankings(fdf, top_n=top_n)
        plot_df, corr = volume_price_sample(fdf)
        bag_totals_df, bag_long, _small_col = bag_totals_and_long(fdf)
        top_by_type = value_proxy_by_type(fdf, top_n=top_n)

        ov_monthly, ov_type_mean, ov_month_avg, ov_value = overview_dashboard_data(fdf, top_n=top_n)

        corr_df, pairs_df = regional_competition(fdf)
        forecast_df, mae, next_month, next_forecast = forecast_backtest(fdf)
        conv_top, org_top, type_year, type_cagr = growth_analysis(fdf)
        summary = executive_summary_text(fdf)

        mae_summary = html.Div(
            [
                html.Div("MAE (lower is better):", style={"fontWeight": "bold"}),
                html.Ul([html.Li(f"{k}: {v:.4f}") for k, v in mae.items()]),
                html.Div(f"Next month naive forecast ({next_month.date()}): ${next_forecast:.2f}"),
                html.Div(
                    "Type CAGR: "
                    + ", ".join([f"{k}={v:.2%}" for k, v in type_cagr.items()]),
                    style={"marginTop": "8px"},
                ),
            ],
            style={"padding": "8px", "backgroundColor": "white", "border": "1px solid #ddd"},
        )

        rec_1 = "Use regional pricing clusters instead of one national rule."
        rec_2 = "Use a seasonal buying calendar (cheaper winter, tighter summer margins)."
        rec_3 = "Expand organic selectively in high-growth regions."

        return (
            stats["rows"],
            stats["regions"],
            stats["types"],
            stats["date_range"],
            (f"{premium:.1f}%" if premium == premium else "N/A"),
            f"{corr:.3f}",
            missing_summary,
            fig_monthly_trend(ov_monthly, monthly_type),
            fig_type_mean(ov_type_mean.rename(columns={"average_price": "mean"})),
            fig_seasonality(ov_month_avg),
            fig_value_proxy(
                ov_value.assign(type="all").rename(columns={"value_proxy": "value_proxy"})[
                    ["type", "region", "value_proxy"]
                ]
            ),
            fig_price_hist_box(fdf),
            fig_type_box(fdf),
            fig_type_mean(type_stats_df),
            fig_monthly_trend(monthly_all, monthly_type),
            fig_seasonality(month_avg),
            fig_region_top_bottom(top_df, bottom_df),
            fig_volume_vs_price(plot_df, corr),
            fig_bag_totals(bag_totals_df),
            fig_bag_by_type(bag_long),
            fig_value_proxy(top_by_type),
            fig_corr_heatmap(corr_df),
            fig_top_pairs(pairs_df, top_n=min(8, len(pairs_df))),
            fig_forecast(forecast_df, forecast_models or DEFAULT_FORECAST_MODELS),
            fig_cagr_bars(conv_top, org_top),
            fig_type_year_volume(type_year),
            mae_summary,
            summary["finding_1"],
            summary["finding_2"],
            summary["finding_3"],
            summary["finding_4"],
            rec_1,
            rec_2,
            rec_3,
        )
