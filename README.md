# Avocado Dashboard (Dash + Plotly)

Interactive dashboard built from the HW1 avocado analysis logic.

## Data Source
- Professor GitHub dataset:
  - `https://raw.githubusercontent.com/kostis-christodoulou/e628/main/data/avocado.csv`

## Tech Stack
- Python
- pandas / numpy
- Plotly
- Dash

## Run Locally
1. Install dependencies:
```bash
python -m pip install -r avocado_dashboard/requirements.txt
```

2. Start app from the `HW3` directory:
```bash
python -m avocado_dashboard.app
```

3. Open:
- `http://127.0.0.1:8050`

## Dashboard Sections
- Overview
- Price Explorer
- Region & Volume
- Deep Dive
- Executive Summary

## Notes
- Analysis behavior follows notebook logic (filters, aggregations, formulas), with Plotly replacing static matplotlib/seaborn visuals.
- Global filters:
  - Date range
  - Type
  - Regions
  - Top N
  - Forecast model toggle
