from dash import Input, Output, State, html
from widgets.pig_behavior.plot_behavior_bar import generate_behavior_bar_plot
from widgets.pig_behavior.plot_behavior_polar import generate_two_polar_charts
from widgets.pig_behavior.plot_behavior_heatmap import generate_behavior_heatmap, generate_behavior_heatmap_for_day
from widgets.pig_behavior.layout import DEFAULT_XES_PATH, EXCLUDED_BEHAVIORS

PKL_FOLDER = "data/action_detection/loaded"

def register_callbacks(app):
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

    @app.callback(
        Output("polar-graph-all", "figure"),
        Output("polar-graph-day", "figure"),
        Input("polar-hour-slider", "value"),
        Input("polar-scale-toggle", "value"),
        Input("polar-date-selector", "value")
    )
    def update_polar_plots(hour, scale, date):
        return generate_two_polar_charts(hour, date, scale)

    @app.callback(
        Output("behavior-heatmap", "figure"),
        Input("heatmap-behavior-selector", "value"),
    )
    def update_heatmap(behavior):
        fig = generate_behavior_heatmap(PKL_FOLDER, behavior)
        return fig
    
    @app.callback(
        Output("single-day-heatmap", "figure"),
        Input("heatmap-date-selector", "value")
    )
    def update_single_day_heatmap(date_str):
        return generate_behavior_heatmap_for_day(date_str)