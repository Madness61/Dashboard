import dash
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from widgets.pig_behavior.layout import layout as pig_layout
from widgets.pig_behavior.callbacks import register_callbacks as pig_callbacks

from widgets.behavior_position.layout import layout as position_layout
from widgets.behavior_position.callbacks import register_callbacks as position_callbacks

from widgets.activity_budget.layout import layout as budget_layout
from widgets.activity_budget.callbacks import register_callbacks as budget_callbacks

from widgets.behavior_flow.layout import layout as flow_layout
from widgets.behavior_flow.callbacks import register_callbacks as register_flow_callbacks



# Dash App initialisieren
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
app.title = "Verhaltensanalyse – Schweine"

TABS = {
    "pig": {
        "label": "Verhalten (Tag + Stunde)",
        "layout": pig_layout
    },
    "position": {
        "label": "Verhaltenspositionen",
        "layout": position_layout
    },
    "budget": {
        "label": "Aktivitätsbudget",
        "layout": budget_layout
    },
    "flow": {
        "label": "Prozesspfade",
        "layout": flow_layout
    },
}


# App Layout
app.layout = dbc.Container([
    html.H2("KI-gestütztes Dashboard zur Verhaltensanalyse in der Schweinehaltung", className="my-4 text-center"),

    dbc.Tabs(
        id="tabs",
        active_tab="pig",
        children=[
            dbc.Tab(label=config["label"], tab_id=key) for key, config in TABS.items()
        ]
    ),
    html.Div(id="tab-content", className="mt-4")
], fluid=True)

# Tab-Inhalte dynamisch laden
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab(active_tab):
    return TABS[active_tab]["layout"]()

# Callback-Funktionen registrieren
pig_callbacks(app)
position_callbacks(app)
budget_callbacks(app)
register_flow_callbacks(app)

# App starten
if __name__ == "__main__":
    app.run(debug=True)
