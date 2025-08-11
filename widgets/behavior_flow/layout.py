from dash import html, dcc
import pandas as pd
from widgets.utils import load_behavior_data

PKL_FOLDER = "data/action_detection/loaded"

def layout():
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return html.P("Keine Daten verfügbar.", style={"color": "red"})

    dates = sorted(df['date'].unique())
    first_date = str(dates[0]) if dates else None

    return html.Div([
        html.H4("Verhaltensabläufe – Process Mining (DFG)"),

        html.Div("Datum auswählen:"),
        dcc.Dropdown(
            id="flow-date-selector",
            options=[{"label": str(d), "value": str(d)} for d in dates],
            value=first_date,
            clearable=False
        ),

        html.Br(),

        dcc.Graph(id="behavior-flow-graph"),

        html.Br(),

        html.Div([
            html.H5("Analysebericht"),
            html.Pre(id="behavior-flow-text", style={
                "whiteSpace": "pre-wrap", "fontFamily": "monospace"
            })
        ]),

        html.Br(),

        html.Div([
            html.H5("Top-Verhaltensequenzen"),
            html.Pre(id="behavior-top-sequences", style={"whiteSpace": "pre-wrap", "fontFamily": "monospace"})
        ])
    ])
