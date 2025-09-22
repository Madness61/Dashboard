from dash import html, dcc
import dash_bootstrap_components as dbc

from widgets.utils import load_behavior_data  # nur Daten für Datumsauswahl

PKL_FOLDER = "data/action_detection/loaded"

# Baut die Aktivitätsbudget-Detailansicht ohne Heatmap.
def layout():
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return dbc.Alert("Keine Daten verfügbar.", color="danger", className="mb-3")

    dates = sorted({str(d) for d in df["date"].unique()})
    first_date = dates[0] if dates else None

    return html.Div([
        html.H4("AKTIVITÄTSBUDGET"),

        # Steuerung für Budget-Ansicht
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id="budget-mode-select",
                options=[
                    {"label": "Aggregiert", "value": "aggregated"},
                    {"label": "Tagesbezogen", "value": "single"},
                ],
                value="aggregated",
                clearable=False,
            ), xs=12, sm=6, md=4, lg=3, className="mb-2"),
            dbc.Col(dcc.Dropdown(
                id="date-select",
                options=[{"label": d, "value": d} for d in dates],
                value=first_date,
                clearable=False,
            ), xs=12, sm=6, md=4, lg=3, className="mb-2"),
        ], className="align-items-end mb-2"),

        # Budget-Grafik
        dbc.Card(dbc.CardBody(dcc.Graph(id="ab-budget-graph")), className="mb-4"),
    ])
