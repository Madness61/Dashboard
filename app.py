import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# --- Modul-Layouts & Callbacks ---
from widgets.pig_behavior.layout import layout as pig_layout
from widgets.pig_behavior.callbacks import register_callbacks as pig_callbacks

from widgets.behavior_position.layout import layout as position_layout
from widgets.behavior_position.callbacks import register_callbacks as position_callbacks

from widgets.activity_budget.layout import layout as budget_layout
from widgets.activity_budget.callbacks import register_callbacks as budget_callbacks

from widgets.behavior_flow.layout import layout as flow_layout
from widgets.behavior_flow.callbacks import register_callbacks as flow_callbacks

# --- Utils & Preview-Bilder ---
from widgets.utils import load_behavior_data
from widgets.behavior_position.plot_zone_overview import generate_zone_overview_image

# optionale Preview-Funktionen
try:
    from widgets.pig_behavior.plot_behavior_heatmap import generate_behavior_heatmap
except Exception:
    generate_behavior_heatmap = None

try:
    from widgets.activity_budget.plot_budget import generate_aggregated_plot
except Exception:
    generate_aggregated_plot = None

try:
    from widgets.behavior_flow.plot_behavior_flow import generate_behavior_dfg
except Exception:
    generate_behavior_dfg = None


# === Dash App ===
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True,
    title="Verhaltensanalyse – Schweine",
)

# Seiten-Registry
TABS = {
    "pig":       {"label": "Verhalten (Tag + Stunde)", "layout": pig_layout,       "path": "/pig"},
    "position":  {"label": "Verhaltenspositionen",      "layout": position_layout, "path": "/position"},
    "budget":    {"label": "Aktivitätsbudget",          "layout": budget_layout,   "path": "/budget"},
    "flow":      {"label": "Prozesspfade",              "layout": flow_layout,     "path": "/flow"},
}


# === Helpers ===
def _latest_date(folder: str) -> str | None:
    try:
        df = load_behavior_data(folder)
        if df is None or df.empty:
            return None
        return str(max(df["date"]))
    except Exception:
        return None


def _placeholder_box(text="Klicke für mehr Details."):
    return html.Div(
        text,
        className="preview-body d-flex align-items-center justify-content-center",
        style={"border": "1px dashed #e1e5ea", "borderRadius": "10px"},
    )


def _small_graph(fig):
    return dcc.Graph(
        figure=fig,
        style={"height": "200px", "marginBottom": 0},
        config={"displayModeBar": False, "responsive": True},
    )


def _preview_card(title: str, body_component, href: str):
    """Einheitliche Preview-Card mit Button immer am unteren Rand."""
    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(title, className="card-title"),
                html.Div(body_component, className="preview-body"),  # feste Höhe, s. CSS
                dcc.Link(  # Button wird durch mt-auto an den unteren Rand gedrückt
                    dbc.Button("ÖFFNEN", color="primary"),
                    href=href,
                    refresh=False,
                    className="mt-auto align-self-start"
                ),
            ],
            className="d-flex flex-column preview-card"  # s. CSS
        ),
        className="mb-4 h-100"
    )


def generate_preview_cards():
    """Erstellt vier Vorschaukarten (eine pro Modul)."""
    data_folder = "data/action_detection/loaded"
    day = _latest_date(data_folder)

    cards = []

    # 1) Verhalten (Heatmap-Vorschau)
    if generate_behavior_heatmap is not None:
        try:
            fig = generate_behavior_heatmap(data_folder, behavior="feeding")
            body = _small_graph(fig)
        except Exception as e:
            body = html.P(f"Fehler: {e}", style={"color": "red"})
    else:
        body = _placeholder_box()
    cards.append(_preview_card(TABS["pig"]["label"], body, TABS["pig"]["path"]))

    # 2) Verhaltenspositionen (Stallübersicht)
    if day:
        try:
            img_src = generate_zone_overview_image(
                data_folder, day, behavior_filter=None, n_clusters=4, fit_sample_fraction=0.20
            )
            if isinstance(img_src, str) and img_src.startswith("data:image"):
                body = html.Img(
                    src=img_src,
                    style={"maxWidth": "100%", "height": "200px", "objectFit": "contain", "borderRadius": "10px"},
                )
            else:
                body = html.P(img_src, style={"color": "red"})
        except Exception as e:
            body = html.P(f"Fehler: {e}", style={"color": "red"})
    else:
        body = _placeholder_box("Keine Tagesdaten gefunden.")
    cards.append(_preview_card(TABS["position"]["label"], body, TABS["position"]["path"]))

    # 3) Aktivitätsbudget (Aggregat)
    if generate_aggregated_plot is not None:
        try:
            img_src = generate_aggregated_plot()
            if isinstance(img_src, str) and img_src.startswith("data:image"):
                body = html.Img(
                    src=img_src,
                    style={"maxWidth": "100%", "height": "200px", "objectFit": "contain", "borderRadius": "10px"},
                )
            else:
                body = html.P(img_src, style={"color": "red"})
        except Exception as e:
            body = html.P(f"Fehler: {e}", style={"color": "red"})
    else:
        body = _placeholder_box()
    cards.append(_preview_card(TABS["budget"]["label"], body, TABS["budget"]["path"]))

    # 4) Prozesspfade (DFG)
    if generate_behavior_dfg is not None and day:
        try:
            fig, _ = generate_behavior_dfg(data_folder, day)
            body = _small_graph(fig)
        except Exception as e:
            body = html.P(f"Fehler: {e}", style={"color": "red"})
    else:
        body = _placeholder_box()
    cards.append(_preview_card(TABS["flow"]["label"], body, TABS["flow"]["path"]))

    return cards


def preview_layout():
    cards = generate_preview_cards()
    return dbc.Container(
        [
            html.H2(
                dcc.Link("DASHBOARD-VORSCHAU", href="/", style={"textDecoration": "none", "color": "inherit"}),
                className="my-4 text-center"
            ),
            dbc.Row([dbc.Col(cards[0], xs=12, md=6, lg=6), dbc.Col(cards[1], xs=12, md=6, lg=6)], className="g-4"),
            dbc.Row([dbc.Col(cards[2], xs=12, md=6, lg=6), dbc.Col(cards[3], xs=12, md=6, lg=6)], className="g-4"),
        ],
        fluid=True,
        style={"maxWidth": "1280px", "margin": "0 auto", "paddingLeft": "15px", "paddingRight": "15px"},
    )


# === App-Layout mit Router ===
app.layout = html.Div([dcc.Location(id="url", refresh=False), html.Div(id="page-content")])


# === Routing mit einheitlichem Seiten-Container + Zurück-Link ===
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname in ("/", "", None):
        return preview_layout()

    for _, conf in TABS.items():
        if conf["path"] == pathname:
            content = conf["layout"]() if callable(conf["layout"]) else conf["layout"]
            back_link = dcc.Link("← Zurück zur Vorschau", href="/",
                                 className="text-decoration-none",
                                 style={"display": "block", "marginBottom": "1rem", "fontWeight": "bold"})
            return dbc.Container([back_link, content], fluid=True,
                                 style={"maxWidth": "1280px", "margin": "0 auto",
                                        "paddingLeft": "15px", "paddingRight": "15px"})

    return dbc.Container(dbc.Alert("Seite nicht gefunden", color="warning"),
                         fluid=True, style={"maxWidth": "900px", "margin": "24px auto"})


# === Modul-Callbacks registrieren ===
pig_callbacks(app)
position_callbacks(app)
budget_callbacks(app)
flow_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
