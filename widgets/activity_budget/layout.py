from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

from widgets.utils import load_behavior_data, BEHAVIORS

PKL_FOLDER = "data/action_detection/loaded"


def layout():
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return dbc.Alert("Keine Daten verfügbar.", color="danger", className="mb-3")

    # Datumswerte als Strings (stabil für Dropdowns)
    dates = sorted({str(d) for d in df["date"].unique()})
    first_date = dates[0] if dates else None

    return html.Div(
        [
            html.H4("Aktivitätsbudget & Tagesmuster"),

            # --- Steuerung: Verhalten + Datum ---
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="ab-behavior-selector",
                            options=[{"label": b, "value": b} for b in BEHAVIORS],
                            value=BEHAVIORS[0],
                            clearable=False,
                        ),
                        xs=12, sm=8, md=6, lg=4,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="ab-date-selector",
                            options=[{"label": d, "value": d} for d in dates],
                            value=first_date,
                            clearable=False,
                        ),
                        xs=12, sm=6, md=4, lg=3,
                        className="mb-3",
                    ),
                ]
            ),

            # --- Heatmap 1: Tagesmuster für ein Verhalten (alle Tage) ---
            html.H5("Tagesmuster: Ø-Verhaltensintensität über Stunden (alle Tage)"),
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id="ab-heatmap-behavior")
                ),
                className="mb-4",
            ),

            # --- Heatmap 2: Aktivitätsbudget (ein Tag, alle Verhaltensarten) ---
            html.H5("Aktivitätsbudget: Anteil je Verhalten und Stunde (ein Tag)"),
            dbc.Card(
                dbc.CardBody(
                    dcc.Graph(id="ab-heatmap-day")
                ),
                className="mb-2",
            ),
        ]
    )
