from dash import Input, Output, html
from widgets.behavior_position.plot_position_image import generate_behavior_position_image
from widgets.behavior_position.plot_zone_duration import generate_zone_duration_image
# from widgets.behavior_position.learn_zones_from_behavior import generate_zone_map_image_for_date  
from widgets.behavior_position.plot_zone_hour_heatmap import generate_zone_hour_heatmap
from widgets.behavior_position.plot_zone_overview import generate_zone_overview_image

from widgets.utils import load_behavior_data

PKL_FOLDER = "data/action_detection/loaded"

def register_callbacks(app):
    # 🔹 Positions-Scatterplot + Zonen-Barplot
    @app.callback(
        Output("position-image-output", "children"),
        Output("zone-image-output", "children"),
        Input("position-behavior-selector", "value"),
        Input("position-date-selector", "value")
    )
    def update_plots(behavior, date):
        # 🟢 Positionen
        scatter_src = generate_behavior_position_image(PKL_FOLDER, behavior, date)
        scatter_element = (
            html.Img(src=scatter_src, style={"maxWidth": "100%"})
            if isinstance(scatter_src, str) and scatter_src.startswith("data:image")
            else html.P(scatter_src, style={"color": "red"})
        )

        # 🟢 Aufenthaltsdauer pro Zone
        zone_src = generate_zone_duration_image(PKL_FOLDER, behavior, date)
        zone_element = (
            html.Img(src=zone_src, style={"maxWidth": "100%"})
            if isinstance(zone_src, str) and zone_src.startswith("data:image")
            else html.P(zone_src, style={"color": "red"})
        )

        # 🔴 Automatisch erkannte Zonen 
        # df = load_behavior_data(PKL_FOLDER)
        # learned_zones_src = generate_zone_map_image_for_date(df, date)
        # if isinstance(learned_zones_src, str) and learned_zones_src.startswith("data:image"):
        #     learned_zones_element = html.Img(src=learned_zones_src, style={"maxWidth": "100%"})
        # else:
        #     learned_zones_element = html.P(learned_zones_src, style={"color": "red"})

        return scatter_element, zone_element  # , learned_zones_element

    # 🔹 Heatmap: Aufenthaltsdauer pro Zone & Stunde
    #@app.callback(
    #    Output("zone-hour-heatmap", "figure"),
    #    Input("zone-hour-behavior-selector", "value"),
    #    Input("zone-hour-date-selector", "value")
    #)
    #def update_zone_hour_heatmap(behavior, date):
    #    return generate_zone_hour_heatmap(PKL_FOLDER, behavior, date)

    