from dash import Input, Output, html
from widgets.activity_budget.plot_budget import (
    generate_single_day_plot,      # nur für die Vorschaukachel (Legacy)
    generate_aggregated_plot,      # nur für die Vorschaukachel (Legacy)
    generate_single_day_figure,    # interaktives Balkendiagramm (Tag)
    generate_aggregated_figure,    # interaktives Balkendiagramm (Ø alle Tage)
    generate_behavior_heatmap,     # Heatmap nach Verhalten (Ø, alle Tage)
)

def register_callbacks(app):
    """Callbacks für Aktivitätsbudget."""

    # --- Dashboard-Preview (bestehende Kachel) ---
    @app.callback(
        Output("budget-plot-output", "children"),
        Input("budget-mode", "value"),
        Input("budget-date-selector", "value"),
    )
    def update_budget_preview(mode, date):
        img = generate_single_day_plot(date) if mode == "single" else generate_aggregated_plot()
        if isinstance(img, str) and img.startswith("data:image"):
            return html.Img(src=img, style={"maxWidth": "100%"})
        return html.P(img, style={"color": "red"})

    # --- Block 1: Heatmap (nur Verhalten steuert) ---
    @app.callback(
        Output("ab-heatmap", "figure"),
        Input("behavior-select", "value"),
    )
    def update_heatmap(behavior):
        fig = generate_behavior_heatmap(behavior)
        if isinstance(fig, str):
            from plotly.graph_objects import Figure
            return Figure(layout={"annotations": [{"text": fig, "showarrow": False}]})
        return fig

    # --- Block 2: Aktivitätsbudget (Modus & Datum steuern) ---
    @app.callback(
        Output("ab-budget-graph", "figure"),
        Input("budget-mode-select", "value"),
        Input("date-select", "value"),
    )
    def update_budget_graph(mode, date):
        fig = generate_single_day_figure(date) if mode == "single" else generate_aggregated_figure()
        if isinstance(fig, str):
            from plotly.graph_objects import Figure
            return Figure(layout={"annotations": [{"text": fig, "showarrow": False}]})
        return fig
