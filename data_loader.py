from __future__ import annotations

import re

import pandas as pd

try:
    from .constants import DATA_URL
except ImportError:
    from constants import DATA_URL


def _clean_column_name(name: str) -> str:
    out = name.strip().lower()
    out = re.sub(r"[^a-z0-9]+", "_", out)
    out = re.sub(r"_+", "_", out).strip("_")
    return out


def load_avocado_data(url: str = DATA_URL) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [_clean_column_name(c) for c in df.columns]

    if "region" in df.columns:
        df = df[df["region"] != "TotalUS"].copy()

    df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name().str.slice(stop=3)

    if "type" in df.columns:
        df["type"] = df["type"].astype("category")
    if "region" in df.columns:
        df["region"] = df["region"].astype("category")

    return df
