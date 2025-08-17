from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from widgets.utils import load_behavior_data

PKL_FOLDER = "data/action_detection/loaded"


def layout():
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return dbc.Alert("Keine Daten verfügbar.", color="danger", className="mb-3")

    # Datumswerte als Strings für stabile Dropdown-Values
    dates = sorted({str(d) for d in df["date"].unique()})
    first_date = dates[0] if dates else None

    return html.Div(
        [
            html.H4("Verhaltensabläufe – Process Mining"),

            # --- Steuerung: Datum ---
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="flow-date-selector",
                            options=[{"label": d, "value": d} for d in dates],
                            value=first_date,
                            clearable=False,
                        ),
                        xs=12, sm=8, md=6, lg=4,
                        className="mb-3",
                    ),
                ]
            ),

            # --- DFG-Graph ---
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id="behavior-flow-graph")
                ),
                className="mb-4"
            ),

            html.Hr(className="my-4"),

            # --- Analysebericht ---
            html.H5("Analysebericht"),
            dbc.Card(
                dbc.CardBody(
                    html.Pre(
                        id="behavior-flow-text",
                        style={
                            "whiteSpace": "pre-wrap",
                            "fontFamily": "monospace",
                            "minHeight": "160px",
                            "marginBottom": 0
                        }
                    )
                ),
                className="mb-4"
            ),

            # --- Top-Sequenzen ---
            html.H5("Top-Verhaltensequenzen"),
            dbc.Card(
                dbc.CardBody(
                    html.Pre(
                        id="behavior-top-sequences",
                        style={
                            "whiteSpace": "pre-wrap",
                            "fontFamily": "monospace",
                            "minHeight": "160px",
                            "marginBottom": 0
                        }
                    )
                ),
                className="mb-2"
            ),
        ]
    )
