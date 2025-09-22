from dash import Input, Output, State, html
from widgets.pig_behavior.plot_behavior_bar import generate_behavior_bar_plot
from widgets.pig_behavior.plot_behavior_polar import generate_two_polar_charts
from widgets.pig_behavior.plot_behavior_heatmap import generate_behavior_heatmap, generate_behavior_heatmap_for_day
from widgets.pig_behavior.layout import DEFAULT_XES_PATH, EXCLUDED_BEHAVIORS

PKL_FOLDER = "data/action_detection/loaded"

# Registriert alle Callbacks für das Modul "pig_behavior".
def register_callbacks(app):
    # Aktualisiert den Balkenplot je nach ausgewähltem Verhalten; gibt Bild oder Fehlermeldung zurück.
    @app.callback(
        Output("behavior-plot-output", "children"),
        Input("behavior-selector", "value"),
        State("behavior-thresholds", "data")
    )
    def update_bar_chart(behavior, thresholds):
        image_src = generate_behavior_bar_plot(DEFAULT_XES_PATH, behavior, thresholds)
        if isinstance(image_src, str) and image_src.startswith("data:image"):
            return html.Img(src=image_src, style={"max-width": "100%"})
        return html.P(image_src, style={"color": "red"})

    # Aktualisiert zwei Polar-Charts (aggregiert und tagesbezogen) basierend auf Stunde, Skalierung und Datum.
    @app.callback(
        Output("polar-graph-all", "figure"),
        Output("polar-graph-day", "figure"),
        Input("polar-hour-slider", "value"),
        Input("polar-scale-toggle", "value"),
        Input("polar-date-selector", "value")
    )
    def update_polar_plots(hour, scale, date):
        return generate_two_polar_charts(hour, date, scale)

    # Aktualisiert die Tagesmuster-Heatmap für das gewählte Verhalten.
    @app.callback(
        Output("behavior-heatmap", "figure"),
        Input("heatmap-behavior-selector", "value"),
    )
    def update_heatmap(behavior):
        fig = generate_behavior_heatmap(PKL_FOLDER, behavior)
        return fig
    
    # Aktualisiert die Aktivitätsbudget-Heatmap für das gewählte Datum.
    @app.callback(
        Output("single-day-heatmap", "figure"),
        Input("heatmap-date-selector", "value")
    )
    def update_single_day_heatmap(date_str):
        return generate_behavior_heatmap_for_day(date_str)
