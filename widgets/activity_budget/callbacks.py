from dash import Input, Output, State, html
from widgets.activity_budget.plot_budget import generate_single_day_plot, generate_aggregated_plot

def register_callbacks(app):
    @app.callback(
        Output("budget-plot-output", "children"),
        Input("budget-mode", "value"),
        Input("budget-date-selector", "value")
    )
    def update_budget_plot(mode, date):
        if mode == "single":
            image_src = generate_single_day_plot(date)
        else:
            image_src = generate_aggregated_plot()

        if isinstance(image_src, str) and image_src.startswith("data:image"):
            return html.Img(src=image_src, style={"maxWidth": "100%"})
        return html.P(image_src, style={"color": "red"})
