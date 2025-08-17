from dash import Input, Output, html
from widgets.activity_budget.plot_budget import generate_single_day_plot, generate_aggregated_plot

# Import heatmap generators from pig_behavior. These functions already
# provide the interactive heatmap visualisations that we need for the
# activity budget page: one for the behaviour‑specific average over all
# days and one for a single day overview across behaviours.  By reusing
# these functions we avoid duplicating code and ensure a consistent
# look and feel across the dashboard.
from widgets.pig_behavior.plot_behavior_heatmap import (
    generate_behavior_heatmap,
    generate_behavior_heatmap_for_day,
)

def register_callbacks(app):
    """Register callbacks for the activity budget module.

    There are two separate interactive plots on the activity budget page:

    * The first heatmap shows the average behaviour intensity per hour
      across all days for a selected behaviour.  It is controlled via
      the ``ab‑behavior‑selector`` dropdown and writes its figure to
      ``ab‑heatmap‑behavior``.
    * The second heatmap shows the distribution of behaviours per hour
      on a specific date.  It is controlled via the ``ab‑date‑selector``
      dropdown and writes its figure to ``ab‑heatmap‑day``.

    There is also a legacy callback for the budget preview which
    generates a static image depending on the selected mode (single day
    or aggregated).  It has been retained for backwards compatibility.
    """

    # Legacy budget plot (used in preview card).  Leave this intact so
    # that the preview continues to function as before.
    @app.callback(
        Output("budget-plot-output", "children"),
        Input("budget-mode", "value"),
        Input("budget-date-selector", "value"),
    )
    def update_budget_plot(mode, date):
        if mode == "single":
            image_src = generate_single_day_plot(date)
        else:
            image_src = generate_aggregated_plot()

        if isinstance(image_src, str) and image_src.startswith("data:image"):
            return html.Img(src=image_src, style={"maxWidth": "100%"})
        return html.P(image_src, style={"color": "red"})

    # First heatmap: average intensity per hour across all days for a
    # selected behaviour.  If there is an error (function returns a
    # string) then embed the message into a blank figure to avoid
    # crashing the Graph component.
    @app.callback(
        Output("ab-heatmap-behavior", "figure"),
        Input("ab-behavior-selector", "value"),
    )
    def update_ab_heatmap_behavior(behavior):
        fig = generate_behavior_heatmap("data/action_detection/loaded", behavior)
        if isinstance(fig, str):
            from plotly.graph_objects import Figure
            return Figure(layout={"annotations": [{"text": fig, "showarrow": False}]})
        return fig

    # Second heatmap: behaviour distribution per hour on a selected day.
    @app.callback(
        Output("ab-heatmap-day", "figure"),
        Input("ab-date-selector", "value"),
    )
    def update_ab_heatmap_day(date):
        fig = generate_behavior_heatmap_for_day(date)
        if isinstance(fig, str):
            from plotly.graph_objects import Figure
            return Figure(layout={"annotations": [{"text": fig, "showarrow": False}]})
        return fig