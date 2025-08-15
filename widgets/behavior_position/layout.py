import dash_bootstrap_components as dbc
from dash import dcc, html

from widgets.utils import BEHAVIORS

def layout():
    return html.Div(
        [
            # === Positionen (ganze Breite) ===
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="position-behavior-selector",
                                                    options=[{"label": b, "value": b} for b in BEHAVIORS],
                                                    value="feeding",
                                                    clearable=False,
                                                ),
                                                md=6
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id="position-date-selector",
                                                    options=[],     # dynamisch per Callback
                                                    value=None,
                                                    placeholder="Datum wählen",
                                                    clearable=False,
                                                ),
                                                md=6
                                            ),
                                        ],
                                        className="g-2 mb-3"
                                    ),
                                    html.Div(id="position-image-output", style={"minHeight": "420px"}),
                                ]
                            )
                        ),
                        xs=12, md=12, lg=12,
                        className="mb-4",
                    ),
                ]
            ),

            # === Aufenthaltsdauer (links) + Stallübersicht (rechts) ===
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                html.Div(id="zone-image-output", style={"minHeight": "420px"})
                            )
                        ),
                        xs=12, md=6, lg=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                html.Div(id="zone-overview-image-output", style={"minHeight": "420px"})
                            )
                        ),
                        xs=12, md=6, lg=6,
                        className="mb-4",
                    ),
                ]
            ),

            # === Matrix-Heatmap: Zone × Stunde (KEIN Slider) ===
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="zone-hour-behavior-selector",
                                        options=[{"label": b, "value": b} for b in BEHAVIORS],
                                        value="feeding",
                                        clearable=False,
                                    ),
                                    md=6
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id="zone-hour-date-selector",
                                        options=[],      # dynamisch per Callback
                                        value=None,
                                        placeholder="Datum wählen",
                                        clearable=False,
                                    ),
                                    md=6
                                ),
                            ],
                            className="g-2 mb-3"
                        ),
                        dcc.Graph(id="zone-hour-heatmap", style={"height": "520px"}),
                    ]
                ),
                className="mb-4"
            ),
        ]
    )
