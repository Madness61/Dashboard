from dash import html, dcc
import pandas as pd
from widgets.utils import load_behavior_data, BEHAVIORS

PKL_FOLDER = "data/action_detection/loaded"

def layout():
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return html.P("Keine PKL-Dateien gefunden!", style={"color": "red"})

    dates = sorted(df['date'].unique())
    first_date = dates[0]

    return html.Div([
        html.H4("Verhalten im Stall – Positionen & Aufenthaltszonen"),

        html.Div("Verhalten auswählen:"),
        dcc.Dropdown(
            id="position-behavior-selector",
            options=[{"label": b, "value": b} for b in BEHAVIORS],
            value=BEHAVIORS[0],
            clearable=False
        ),

        html.Br(),
        html.Div("Datum auswählen:"),
        dcc.Dropdown(
            id="position-date-selector",
            options=[{"label": str(d), "value": str(d)} for d in dates],
            value=str(first_date),
            clearable=False
        ),

        html.Br(),

        html.Div([
            html.Div(id="position-image-output", style={
                "width": "48%", "display": "inline-block", "verticalAlign": "top", "paddingRight": "2%"
            }),
            html.Div(id="zone-image-output", style={
                "width": "48%", "display": "inline-block", "verticalAlign": "top", "paddingRight": "2%"
            }),
            #html.Div(id="learned-zones-image-output", style={
            #    "width": "32%", "display": "inline-block", "verticalAlign": "top"
            #}),
            html.Hr(),
            html.H5("Heatmap: Aufenthaltsdauer pro Zone & Stunde"),
            html.Div("Verhalten wählen:"),
            dcc.Dropdown(
                id="zone-hour-behavior-selector",
                options=[{"label": b, "value": b} for b in BEHAVIORS],
                value="feeding",
                clearable=False
            ),
            html.Div("Datum wählen:"),
            dcc.Dropdown(
                id="zone-hour-date-selector",
                options=[{"label": str(d), "value": str(d)} for d in dates],
                value=dates[0],
                clearable=False
            ),
            dcc.Graph(id="zone-hour-heatmap")
        ])
    ])
