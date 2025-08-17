# widgets/activity_budget/callbacks.py
import dash
from dash import Input, Output, callback
from .plot_budget import generate_aggregated_plot, generate_single_day_plot

DETAIL_PATH = "/budget"

def register_callbacks(app):

    @callback(
        Output("budget-agg", "figure"),
        Output("budget-stacked", "figure"),
        Input("url", "pathname"),                 # <-- Navigation triggert Render
        Input("budget-behavior", "value"),
        Input("budget-date", "date"),
        prevent_initial_call=False                # <-- initial feuern erlauben
    )
    def update_budget(pathname, behavior, date):
        if pathname != DETAIL_PATH:
            raise dash.exceptions.PreventUpdate   # fremde Seiten ignorieren
        if not behavior or not date:
            raise dash.exceptions.PreventUpdate

        fig_agg = generate_aggregated_plot(behavior=behavior)
        fig_stack = generate_single_day_plot(behavior=behavior, date=date)
        return fig_agg, fig_stack
