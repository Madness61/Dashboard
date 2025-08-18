from dash import html, dcc
import dash_bootstrap_components as dbc

from widgets.utils import load_behavior_data, BEHAVIORS

PKL_FOLDER = "data/action_detection/loaded"

def layout():
    """Detailansicht: Aktivitätsbudget & Tagesmuster.

    - Oberer Block: Heatmap des Aktivitätsbudgets (Ø-Intensität eines Verhaltens über Stunden, alle Tage)
      -> Steuert sich NUR über 'behavior-select'.
    - Unterer Block: Aktivitätsbudget als Balkendiagramm (aggregiert ODER tagesbasiert)
      -> Steuert sich über 'budget-mode-select' und 'date-select'.
    """
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return dbc.Alert("Keine Daten verfügbar.", color="danger", className="mb-3")

    dates = sorted({str(d) for d in df["date"].unique()})
    first_date = dates[0] if dates else None

    return html.Div([
        html.H4("AKTIVITÄTSBUDGET & TAGESMUSTER"),

        # --- Block 1: Heatmap (nur Verhaltenswahl hier!) ---
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id="behavior-select",
                options=[{"label": b, "value": b} for b in BEHAVIORS],
                value=BEHAVIORS[0] if BEHAVIORS else None,
                clearable=False,
            ), xs=12, sm=6, md=4, lg=3, className="mb-2"),
        ], className="align-items-end"),
        html.Div([
            html.Div("TAGESMUSTER: Ø-VERHALTENSINTENSITÄT ÜBER STUNDEN (ALLE TAGE)",
                     className="mb-2 fw-semibold"),
            dbc.Card(dbc.CardBody(dcc.Graph(id="ab-heatmap")), className="mb-4"),
        ]),

        # --- Block 2: Aktivitätsbudget (Modus/Datum gehören HIER hin) ---
        html.Div([
            html.Div("AKTIVITÄTSBUDGET", className="mb-2 fw-semibold"),
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
            dbc.Card(dbc.CardBody(dcc.Graph(id="ab-budget-graph")), className="mb-4"),
        ]),
    ])
