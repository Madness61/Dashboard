from dash import html, dcc
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
        return html.P("Keine PKL-Dateien gefunden!", style={"color": "red"})

    dfs = [pd.read_pickle(f) for f in file_list]
    df = pd.concat(dfs)
    df['t'] = pd.to_datetime(df['t'])
    df['hour'] = df['t'].dt.hour
    df['date'] = df['t'].dt.date

    hours = sorted(df['hour'].unique())
    dates = sorted({str(d) for d in df['date'].unique()})

    return html.Div([
        html.H4("Verhaltensanalyse pro Tag (Balkendiagramm)"),
        dcc.Dropdown(
            id="behavior-selector",
            options=[{"label": b, "value": b} for b in behaviors],
            value=behaviors[0],
            clearable=False
        ),
        html.Div(id="behavior-plot-output"),
        dcc.Store(id="behavior-thresholds", data=thresholds),

        html.Hr(),
        html.H4("Verhaltensverteilung nach Uhrzeit – aggregiert vs. pro Tag"),
        html.Div("Skalierung wählen:"),
        dcc.RadioItems(
            id="polar-scale-toggle",
            options=[
                {"label": "Linear", "value": "linear"},
                {"label": "Logarithmisch", "value": "logarithmic"},
            ],
            value="linear",
            labelStyle={"display": "inline-block", "marginRight": "1em"}
        ),
        html.Div("Stunde auswählen:"),
        dcc.Slider(
            id="polar-hour-slider",
            min=int(min(hours)),
            max=int(max(hours)),
            step=1,
            value=int(hours[0]),
            marks={int(h): f"{int(h)}:00" for h in hours}
        ),
        html.Div("Datum auswählen:"),
        dcc.Dropdown(
            id="polar-date-selector",
            options=[{"label": d, "value": d} for d in dates],
            value=dates[0],
            clearable=False
        ),
        html.Br(),
        html.Div([
            html.Div([dcc.Graph(id="polar-graph-all")], style={"width": "48%", "display": "inline-block"}),
            html.Div([dcc.Graph(id="polar-graph-day")], style={"width": "48%", "display": "inline-block"}),
        ]),
        html.Br(),
        html.H5("Tagesmuster-Heatmap"),
        html.Div("Verhalten wählen:"),
        dcc.Dropdown(
            id="heatmap-behavior-selector",
            options=[{"label": b, "value": b} for b in BEHAVIORS],
            value="feeding",
            clearable=False
        ),
        dcc.Graph(id="behavior-heatmap"),
        html.Br(),
        html.H5("Heatmap des Aktivitätsbudgets"),
        html.Div("Datum auswählen:"),
        dcc.Dropdown(
            id="heatmap-date-selector",
            options=[{"label": d, "value": d} for d in dates],
            value=dates[0],
            clearable=False
        ),
        dcc.Graph(id="single-day-heatmap")
    ])
