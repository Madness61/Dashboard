import dash
from dash import html, dcc
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

from widgets.utils import load_behavior_data
from widgets.behavior_position.plot_zone_overview import generate_zone_overview_image

# Dash App initialisieren
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True
)
app.title = "Verhaltensanalyse – Schweine"

# Seitenkonfiguration: Label, Layout-Funktion und Pfad
TABS = {
    "pig": {
        "label": "Verhalten (Tag + Stunde)",
        "layout": pig_layout,
        "path": "/pig",
    },
    "position": {
        "label": "Verhaltenspositionen",
        "layout": position_layout,
        "path": "/position",
    },
    "budget": {
        "label": "Aktivitätsbudget",
        "layout": budget_layout,
        "path": "/budget",
    },
    "flow": {
        "label": "Prozesspfade",
        "layout": flow_layout,
        "path": "/flow",
    },
}

def generate_preview_cards():
    """
    Erstellt Vorschau-Karten für jede Seite. 
    Für die Positionsseite wird automatisch eine Stallübersicht mit den gelernten Zonen generiert.
    Für die anderen Seiten erscheint ein Platzhaltertext.
    """
    # Neueste Datum ermitteln (für die Stallübersicht)
    default_date = None
    try:
        df = load_behavior_data("data/action_detection/loaded")
        if df is not None and not df.empty:
            default_date = str(max(df["date"]))
    except Exception:
        pass

    cards = []
    for key, conf in TABS.items():
        header = html.H5(conf["label"], className="card-title")
        # Nur für die Positions-Seite eine Grafik generieren
        if key == "position" and default_date:
            try:
                img_src = generate_zone_overview_image(
                    "data/action_detection/loaded",
                    default_date,
                    behavior_filter=None,
                    n_clusters=4,
                    fit_sample_fraction=0.20,
                )
                if isinstance(img_src, str) and img_src.startswith("data:image"):
                    body = html.Img(
                        src=img_src,
                        style={
                            "maxWidth": "100%",
                            "height": "200px",
                            "objectFit": "contain"
                        },
                    )
                else:
                    body = html.P(img_src, style={"color": "red", "minHeight": "200px"})
            except Exception as e:
                body = html.P(f"Fehler: {e}", style={"color": "red", "minHeight": "200px"})
        else:
            body = html.Div(
                "Klicke für mehr Details.",
                style={
                    "minHeight": "200px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "backgroundColor": "#f8f9fa"
                }
            )
        link = dcc.Link(
            dbc.Button("Öffnen", color="primary", className="mt-2"),
            href=conf["path"],
            refresh=False,
        )
        cards.append(
            dbc.Card(
                dbc.CardBody([header, body, link]),
                className="mb-4"
            )
        )
    return cards

def preview_layout():
    """
    Startseite: zeigt eine Vorschau für jede verfügbare Seite.
    """
    cards = generate_preview_cards()
    return dbc.Container(
        [
            html.H2("Dashboard-Vorschau", className="my-4 text-center"),
            dbc.Row(
                [dbc.Col(card, xs=12, md=6, lg=6) for card in cards[:2]],
                className="g-4"
            ),
            dbc.Row(
                [dbc.Col(card, xs=12, md=6, lg=6) for card in cards[2:]],
                className="g-4"
            ),
        ],
        fluid=True,
        style={"maxWidth": "1280px", "margin": "0 auto"}
    )

# App Layout: Seitennavigation über URL
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ]
)

# Callback: wählt die richtige Seite anhand der URL
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname in ("/", "", None):
        return preview_layout()
    for key, conf in TABS.items():
        if conf["path"] == pathname:
            layout_callable = conf["layout"]
            return layout_callable() if callable(layout_callable) else layout_callable
    return dbc.Alert("Seite nicht gefunden", color="warning")

# Callback-Funktionen der jeweiligen Module registrieren
pig_callbacks(app)
position_callbacks(app)
budget_callbacks(app)
register_flow_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
