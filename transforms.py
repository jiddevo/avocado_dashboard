from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from .constants import MONTH_ORDER
except ImportError:
    from constants import MONTH_ORDER


def apply_filters(
    df: pd.DataFrame,
    start_date: str | None,
    end_date: str | None,
    avocado_type: str,
    regions: list[str] | None,
) -> pd.DataFrame:
    out = df.copy()

    if start_date:
        out = out[out["date"] >= pd.to_datetime(start_date)]
    if end_date:
        out = out[out["date"] <= pd.to_datetime(end_date)]

    if avocado_type and avocado_type != "all":
        out = out[out["type"].astype(str) == avocado_type]

    if regions:
        out = out[out["region"].astype(str).isin(regions)]

    return out


def get_overview_stats(df: pd.DataFrame) -> dict[str, str]:
    stats = {
        "rows": f"{len(df):,}",
        "regions": f"{df['region'].nunique():,}",
        "types": f"{df['type'].nunique():,}",
        "date_range": f"{df['date'].min().date()} to {df['date'].max().date()}",
    }
    return stats


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["small_bags", "large_bags", "xlarge_bags"]
    records = []
    for c in cols:
        if c in df.columns:
            miss = int(df[c].isna().sum())
            records.append({"column": c, "missing_count": miss, "missing_share": miss / len(df) if len(df) else 0.0})
    return pd.DataFrame(records)


def price_distribution_stats(df: pd.DataFrame) -> dict[str, float]:
    q1 = df["average_price"].quantile(0.25)
    q3 = df["average_price"].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = ((df["average_price"] < lower) | (df["average_price"] > upper)).sum()
    return {
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower": float(lower),
        "upper": float(upper),
        "outliers": int(outliers),
        "outlier_share": float(outliers / len(df)) if len(df) else 0.0,
    }


def type_price_stats(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    type_stats = df.groupby("type", observed=True)["average_price"].agg(["mean", "median", "std", "count"]).reset_index()

    premium = np.nan
    if set(type_stats["type"].astype(str).tolist()) >= {"conventional", "organic"}:
        conv = float(type_stats.loc[type_stats["type"].astype(str) == "conventional", "mean"].iloc[0])
        org = float(type_stats.loc[type_stats["type"].astype(str) == "organic", "mean"].iloc[0])
        premium = (org / conv - 1.0) * 100.0

    return type_stats, premium


def monthly_trends(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly_all = df.set_index("date").resample("ME")["average_price"].mean().reset_index()
    monthly_type = (
        df.set_index("date").groupby("type", observed=True)["average_price"].resample("ME").mean().reset_index()
    )
    return monthly_all, monthly_type


def seasonality(df: pd.DataFrame) -> pd.DataFrame:
    month_avg = df.groupby("month_name", observed=True)["average_price"].mean().reindex(MONTH_ORDER).reset_index()
    return month_avg


def region_rankings(df: pd.DataFrame, top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    region_avg = df.groupby("region", observed=True)["average_price"].mean().sort_values()
    top = region_avg.tail(top_n).reset_index()
    bottom = region_avg.head(top_n).reset_index()
    return top, bottom, region_avg


def volume_price_sample(df: pd.DataFrame, sample_size: int = 7000) -> tuple[pd.DataFrame, float]:
    corr = float(df["total_volume"].corr(df["average_price"]))
    plot_df = df.sample(min(sample_size, len(df)), random_state=42)
    return plot_df, corr


def bag_totals_and_long(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    small_col = "small_bags" if "small_bags" in df.columns else "smal_bags"
    bag_cols = [small_col, "large_bags", "xlarge_bags"]

    bag_totals_df = (
        df[bag_cols].sum(numeric_only=True).rename("units").reset_index().rename(columns={"index": "bag_size"})
    )
    label_map = {small_col: "small_bags", "large_bags": "large_bags", "xlarge_bags": "xlarge_bags"}
    bag_totals_df["bag_size"] = bag_totals_df["bag_size"].replace(label_map)
    bag_totals_df["bag_size"] = pd.Categorical(
        bag_totals_df["bag_size"], categories=["small_bags", "large_bags", "xlarge_bags"], ordered=True
    )
    bag_totals_df = bag_totals_df.sort_values("bag_size")

    bag_long = (
        df.groupby("type", observed=True)[bag_cols]
        .sum(numeric_only=True)
        .reset_index()
        .melt(id_vars="type", var_name="bag_size", value_name="units")
    )
    bag_long["bag_size"] = bag_long["bag_size"].replace(label_map)
    bag_long["bag_size"] = pd.Categorical(
        bag_long["bag_size"], categories=["small_bags", "large_bags", "xlarge_bags"], ordered=True
    )
    bag_long = bag_long.sort_values(["bag_size", "type"])

    return bag_totals_df, bag_long, small_col


def value_proxy_by_type(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    tmp = df.copy()
    tmp["value_proxy"] = tmp["average_price"] * tmp["total_volume"]
    value_rt = tmp.groupby(["type", "region"], observed=True)["value_proxy"].mean().reset_index()
    top_by_type = (
        value_rt.sort_values(["type", "value_proxy"], ascending=[True, False]).groupby("type", observed=True).head(top_n)
    )
    return top_by_type


def overview_dashboard_data(df: pd.DataFrame, top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    monthly_all = df.set_index("date").resample("ME")["average_price"].mean().reset_index()
    type_mean = df.groupby("type", observed=True)["average_price"].mean().reset_index()
    month_avg = seasonality(df)
    value_region_df = (
        df.assign(value_proxy=df["average_price"] * df["total_volume"])
        .groupby("region", observed=True)["value_proxy"]
        .mean()
        .nlargest(top_n)
        .sort_values()
        .reset_index()
    )
    return monthly_all, type_mean, month_avg, value_region_df


def regional_competition(df: pd.DataFrame, focus_n: int = 12) -> tuple[pd.DataFrame, pd.DataFrame]:
    monthly_region_price = (
        df.set_index("date").groupby("region", observed=True)["average_price"].resample("ME").mean().reset_index()
    )
    focus_regions = df.groupby("region", observed=True)["total_volume"].sum().nlargest(focus_n).index.tolist()
    price_pivot = monthly_region_price[monthly_region_price["region"].isin(focus_regions)].pivot(
        index="date", columns="region", values="average_price"
    )
    corr = price_pivot.corr()

    corr_named = corr.copy()
    corr_named.index.name = "region_a"
    corr_named.columns.name = "region_b"
    pairs = (
        corr_named.where(np.triu(np.ones(corr_named.shape), k=1).astype(bool))
        .stack()
        .rename("corr")
        .reset_index()
        .sort_values("corr", ascending=False)
    )
    return corr, pairs


def forecast_backtest(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Timestamp, float]:
    monthly_price = df.set_index("date")["average_price"].resample("ME").mean().to_frame("actual")
    monthly_price["year"] = monthly_price.index.year
    test = monthly_price[monthly_price["year"] == 2023].copy()

    pred_naive = monthly_price["actual"].shift(1).loc[test.index]
    pred_roll3 = monthly_price["actual"].rolling(3).mean().shift(1).loc[test.index]

    pred_seasonal = []
    for dt in test.index:
        last_year_same_month = monthly_price[
            (monthly_price.index.year == dt.year - 1) & (monthly_price.index.month == dt.month)
        ]["actual"]
        pred_seasonal.append(last_year_same_month.iloc[0] if len(last_year_same_month) > 0 else np.nan)
    pred_seasonal = pd.Series(pred_seasonal, index=test.index)

    results = pd.DataFrame(
        {
            "actual": test["actual"],
            "naive_last_month": pred_naive,
            "rolling_3_month": pred_roll3,
            "seasonal_naive": pred_seasonal,
        }
    )

    mae = results.drop(columns=["actual"]).sub(results["actual"], axis=0).abs().mean().sort_values()
    next_month = monthly_price.index.max() + pd.offsets.MonthEnd(1)
    next_forecast = float(monthly_price["actual"].iloc[-1])
    return results, mae, next_month, next_forecast


def growth_analysis(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, float]]:
    yearly_volume = df.groupby(["type", "region", "year"], observed=True)["total_volume"].sum().reset_index()

    start_year = int(yearly_volume["year"].min())
    end_year = int(yearly_volume["year"].max())
    periods = end_year - start_year

    start = yearly_volume[yearly_volume["year"] == start_year].set_index(["type", "region"])["total_volume"]
    end = yearly_volume[yearly_volume["year"] == end_year].set_index(["type", "region"])["total_volume"]

    cagr = pd.concat([start.rename("start_volume"), end.rename("end_volume")], axis=1).dropna()
    cagr = cagr[cagr["start_volume"] > 0]
    if periods > 0:
        cagr["cagr"] = (cagr["end_volume"] / cagr["start_volume"]) ** (1 / periods) - 1
    else:
        cagr["cagr"] = 0.0
    cagr = cagr.reset_index()

    type_year = df.groupby(["type", "year"], observed=True)["total_volume"].sum().reset_index()

    type_cagr = {}
    for t in type_year["type"].astype(str).unique():
        s = type_year[(type_year["type"].astype(str) == t) & (type_year["year"] == start_year)]["total_volume"].iloc[0]
        e = type_year[(type_year["type"].astype(str) == t) & (type_year["year"] == end_year)]["total_volume"].iloc[0]
        if periods > 0 and s > 0:
            type_cagr[t] = float((e / s) ** (1 / periods) - 1)
        else:
            type_cagr[t] = 0.0

    conv_top = cagr[cagr["type"].astype(str) == "conventional"].nlargest(5, "cagr")
    org_top = cagr[cagr["type"].astype(str) == "organic"].nlargest(5, "cagr")

    return conv_top, org_top, type_year, type_cagr


def executive_summary_text(df: pd.DataFrame) -> dict[str, str]:
    _, premium = type_price_stats(df)
    _, corr = volume_price_sample(df)
    monthly_all, _ = monthly_trends(df)
    month_avg = seasonality(df)

    highest = month_avg.loc[month_avg["average_price"].idxmax(), "month_name"]
    lowest = month_avg.loc[month_avg["average_price"].idxmin(), "month_name"]

    price_start = float(monthly_all["average_price"].iloc[0])
    price_end = float(monthly_all["average_price"].iloc[-1])

    return {
        "finding_1": f"Average price moved from ${price_start:.2f} to ${price_end:.2f} over the selected period.",
        "finding_2": f"Organic premium vs conventional is {premium:.1f}%.",
        "finding_3": f"Volume-price correlation is {corr:.3f}.",
        "finding_4": f"Seasonal high month is {highest}, low month is {lowest}.",
    }
