from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from widgets.utils import load_behavior_data, BEHAVIORS

PKL_FOLDER = "data/action_detection/loaded"


def layout():
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return dbc.Alert("Keine PKL-Dateien gefunden!", color="danger", className="mb-3")

    # Datumswerte als Strings (stabil für Dropdowns)
    dates = sorted({str(d) for d in df["date"].unique()})
    first_date = dates[0]

    return html.Div(
        [
            html.H4("Verhalten im Stall – Positionen & Aufenthaltszonen"),

            # --- Steuerung: Verhalten + Datum ---
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="position-behavior-selector",
                            options=[{"label": b, "value": b} for b in BEHAVIORS],
                            value=BEHAVIORS[0],
                            clearable=False,
                        ),
                        xs=12, sm=8, md=6, lg=4,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="position-date-selector",
                            options=[{"label": d, "value": d} for d in dates],
                            value=first_date,
                            clearable=False,
                        ),
                        xs=12, sm=6, md=4, lg=3,
                        className="mb-3",
                    ),
                ]
            ),

            # --- Bilder/Overlays in Cards ---
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                html.Div(
                                    id="position-image-output",
                                    style={"minHeight": "360px"}
                                )
                            )
                        ),
                        md=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                html.Div(
                                    id="zone-image-output",
                                    style={"minHeight": "360px"}
                                )
                            )
                        ),
                        md=6,
                        className="mb-4",
                    ),
                    # Optional drittes Bild:
                    # dbc.Col(
                    #     dbc.Card(dbc.CardBody(html.Div(id="learned-zones-image-output",
                    #                                    style={"minHeight": "360px"}))),
                    #     md=4, className="mb-4"
                    # ),
                ]
            ),

            html.Hr(className="my-4"),

            # --- Heatmap: Zonen x Stunden ---
            html.H5("Heatmap: Aufenthaltsdauer pro Zone & Stunde"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="zone-hour-behavior-selector",
                            options=[{"label": b, "value": b} for b in BEHAVIORS],
                            value="feeding",
                            clearable=False,
                        ),
                        xs=12, sm=8, md=6, lg=4,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="zone-hour-date-selector",
                            options=[{"label": d, "value": d} for d in dates],
                            value=first_date,
                            clearable=False,
                        ),
                        xs=12, sm=6, md=4, lg=3,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Card(dbc.CardBody(dcc.Graph(id="zone-hour-heatmap")), className="mb-2"),
        ]
    )
