from __future__ import annotations

from dash import Dash

from .callbacks import register_callbacks
from .data_loader import load_avocado_data
from .layout import create_layout


def create_app() -> Dash:
    df = load_avocado_data()
    app = Dash(__name__, title="US Avocado Dashboard")
    app.layout = create_layout(df)
    register_callbacks(app, df)
    return app


app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(debug=True, port=8050)
