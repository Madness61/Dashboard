from dash import html, dcc
import pandas as pd
import glob
import os

PKL_FOLDER = "data/action_detection/loaded"

def layout():
    # PKL-Dateien laden
    file_list = sorted(glob.glob(os.path.join(PKL_FOLDER, "*.pkl")))
    if not file_list:
        return html.P("Keine PKL-Dateien gefunden.", style={"color": "red"})

    dfs = [pd.read_pickle(f) for f in file_list]
    df = pd.concat(dfs)
    df['t'] = pd.to_datetime(df['t'])
    df['date'] = df['t'].dt.date
    dates = sorted({str(d) for d in df['date'].unique()})

    return html.Div([
        html.H4("Aktivitätsbudget über den Tag (pro Stunde, pro Verhalten)"),

        html.Div("Darstellung wählen:"),
        dcc.RadioItems(
            id="budget-mode",
            options=[
                {"label": "Einzeltag", "value": "single"},
                {"label": "Aggregiert über alle Tage", "value": "aggregate"},
            ],
            value="single",
            labelStyle={"display": "inline-block", "marginRight": "1em"}
        ),

        html.Div("Datum auswählen (nur bei Einzeltag):"),
        dcc.Dropdown(
            id="budget-date-selector",
            options=[{"label": d, "value": d} for d in dates],
            value=dates[0],
            clearable=False
        ),

        html.Br(),
        html.Div(id="budget-plot-output")
    ])
