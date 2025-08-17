from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import glob
import os

from widgets.pig_behavior.thresholds import get_behavior_thresholds
from widgets.utils import get_available_behaviors, BEHAVIORS

DEFAULT_XES_PATH = "data/clustered_log_10s.xes"
PKL_FOLDER = "data/action_detection/loaded"
EXCLUDED_BEHAVIORS = ["start", "end", "other", "lying_start", "lying_end"]


def layout():
    # Verfügbare Verhalten und Schwellenwerte laden
    behaviors = get_available_behaviors(DEFAULT_XES_PATH, EXCLUDED_BEHAVIORS)
    thresholds = get_behavior_thresholds(DEFAULT_XES_PATH, behaviors)

    # Stunden und Datum aus .pkl-Dateien extrahieren
    file_list = sorted(glob.glob(os.path.join(PKL_FOLDER, "*.pkl")))
    if not file_list:
        return dbc.Alert("Keine PKL-Dateien gefunden!", color="danger", className="mb-3")

    dfs = [pd.read_pickle(f) for f in file_list]
    df = pd.concat(dfs)
    df["t"] = pd.to_datetime(df["t"])
    df["hour"] = df["t"].dt.hour
    df["date"] = df["t"].dt.date

    hours = sorted(df["hour"].unique())
    dates = sorted({str(d) for d in df["date"].unique()})

    return html.Div(
        [
            # ---------------- Section 1: Balkendiagramm ----------------
            html.H4("Verhaltensanalyse pro Tag"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="behavior-selector",
                            options=[{"label": b, "value": b} for b in behaviors],
                            value=behaviors[0],
                            clearable=False,
                        ),
                        xs=12,
                        sm=8,
                        md=6,
                        lg=4,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Card(dbc.CardBody(html.Div(id="behavior-plot-output")), className="mb-4"),
            dcc.Store(id="behavior-thresholds", data=thresholds),

            html.Hr(className="my-4"),

            # ---------------- Section 2: Polarplots ----------------
            html.H4("Verhaltensverteilung nach Uhrzeit"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.RadioItems(
                            id="polar-scale-toggle",
                            options=[
                                {"label": "Linear", "value": "linear"},
                                {"label": "Logarithmisch", "value": "logarithmic"},
                            ],
                            value="linear",
                            inline=True,
                        ),
                        xs=12,
                        sm=12,
                        md=8,
                        lg=6,
                        className="mb-2",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Slider(
                            id="polar-hour-slider",
                            min=int(min(hours)),
                            max=int(max(hours)),
                            step=1,
                            value=int(hours[0]),
                            marks={int(h): f"{int(h)}:00" for h in hours},
                        ),
                        xs=12,
                        md=8,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id="polar-date-selector",
                            options=[{"label": d, "value": d} for d in dates],
                            value=dates[0],
                            clearable=False,
                        ),
                        xs=12,
                        sm=6,
                        md=4,
                        lg=3,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(dbc.CardBody(dcc.Graph(id="polar-graph-all"))),
                        md=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(dbc.CardBody(dcc.Graph(id="polar-graph-day"))),
                        md=6,
                        className="mb-4",
                    ),
                ]
            ),

            # ---------------- Section 3: Heatmap – Tagesmuster ----------------
            html.H5("Tagesmuster-Heatmap"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="heatmap-behavior-selector",
                            options=[{"label": b, "value": b} for b in BEHAVIORS],
                            value="feeding",
                            clearable=False,
                        ),
                        xs=12,
                        sm=8,
                        md=6,
                        lg=4,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Card(dbc.CardBody(dcc.Graph(id="behavior-heatmap")), className="mb-4"),

            # ---------------- Section 4: Heatmap – Aktivitätsbudget ----------------
            html.H5("Heatmap des Aktivitätsbudgets"),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="heatmap-date-selector",
                            options=[{"label": d, "value": d} for d in dates],
                            value=dates[0],
                            clearable=False,
                        ),
                        xs=12,
                        sm=8,
                        md=6,
                        lg=4,
                        className="mb-3",
                    ),
                ]
            ),
            dbc.Card(dbc.CardBody(dcc.Graph(id="single-day-heatmap")), className="mb-2"),
        ]
    )
