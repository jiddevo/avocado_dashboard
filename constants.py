DATA_URL = "https://raw.githubusercontent.com/kostis-christodoulou/e628/main/data/avocado.csv"

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

FORECAST_MODEL_OPTIONS = [
    {"label": "Naive (t-1)", "value": "naive_last_month"},
    {"label": "Rolling 3M", "value": "rolling_3_month"},
    {"label": "Seasonal Naive", "value": "seasonal_naive"},
]

DEFAULT_FORECAST_MODELS = ["naive_last_month", "rolling_3_month", "seasonal_naive"]
