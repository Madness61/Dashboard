from dash import Input, Output
from widgets.behavior_flow.plot_behavior_flow import generate_behavior_dfg
from widgets.behavior_flow.plot_top_sequences import get_top_behavior_sequences

PKL_FOLDER = "data/action_detection/loaded"

def register_callbacks(app):
    @app.callback(
        Output("behavior-flow-graph", "figure"),
        Output("behavior-flow-text", "children"),
        Output("behavior-top-sequences", "children"),  # NEU
        Input("flow-date-selector", "value")
    )
    def update_flow(date):
        fig, report = generate_behavior_dfg(PKL_FOLDER, date)
        sequences_text = get_top_behavior_sequences(PKL_FOLDER, date)

        if isinstance(fig, str):
            from plotly.graph_objects import Figure
            return Figure(layout={"annotations": [{"text": fig, "showarrow": False}]}), "", ""
        return fig, report, sequences_text
