from __future__ import annotations

import os

from dash import Dash

try:
    from .callbacks import register_callbacks
    from .data_loader import load_avocado_data
    from .layout import create_layout
except ImportError:
    from callbacks import register_callbacks
    from data_loader import load_avocado_data
    from layout import create_layout


def create_app() -> Dash:
    df = load_avocado_data()
    app = Dash(__name__, title="US Avocado Dashboard")
    app.layout = create_layout(df)
    register_callbacks(app, df)
    return app


app = create_app()
server = app.server


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)
