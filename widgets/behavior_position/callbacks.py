import pandas as pd
from dash import Input, Output, html

from widgets.utils import load_behavior_data
from widgets.behavior_position.plot_position_image import generate_behavior_position_image
from widgets.behavior_position.plot_zone_duration import generate_zone_duration_image
from widgets.behavior_position.plot_zone_overview import generate_zone_overview_image
from widgets.behavior_position.plot_zone_hour_heatmap import generate_zone_hour_heatmap  # ⬅️ wieder Matrix

PKL_FOLDER = "data/action_detection/loaded"


def _available_dates(folder_path: str, behavior: str | None) -> list[str]:
    df = load_behavior_data(folder_path)
    if behavior:
        df = df[df["dominant_behavior"] == behavior]
    if df.empty:
        return []
    return sorted({d.strftime("%Y-%m-%d") for d in df["date"]})


def register_callbacks(app):
    # --- Position / Aufenthaltsdauer / Stallübersicht ---
    @app.callback(
        Output("position-image-output", "children"),
        Output("zone-image-output", "children"),
        Output("zone-overview-image-output", "children"),
        Input("position-behavior-selector", "value"),
        Input("position-date-selector", "value"),
    )
    def update_plots(behavior, date):
        # Positionen (mit Sampling)
        scatter_src = generate_behavior_position_image(
            PKL_FOLDER, behavior, date,
            sample_fraction=0.10, max_points=10000
        )
        scatter_element = (
            html.Img(src=scatter_src, style={"maxWidth": "100%"})
            if isinstance(scatter_src, str) and scatter_src.startswith("data:image")
            else html.P(scatter_src, style={"color": "red"})
        )

        # Aufenthaltsdauer je Zone (tagesweises Zonenmodell)
        zone_src = generate_zone_duration_image(
            PKL_FOLDER, behavior, date,
            n_clusters=4, fit_sample_fraction=0.20, predict_sample_fraction=0.25
        )
        zone_element = (
            html.Img(src=zone_src, style={"maxWidth": "100%"})
            if isinstance(zone_src, str) and zone_src.startswith("data:image")
            else html.P(zone_src, style={"color": "red"})
        )

        # Stallübersicht (tagesweises Zonenmodell)
        overview_src = generate_zone_overview_image(
            PKL_FOLDER, date, behavior_filter=behavior,
            n_clusters=4, fit_sample_fraction=0.20
        )
        overview_element = (
            html.Img(src=overview_src, style={"maxWidth": "100%"})
            if isinstance(overview_src, str) and overview_src.startswith("data:image")
            else html.P(overview_src, style={"color": "red"})
        )

        return scatter_element, zone_element, overview_element

    # --- Dropdown für Position-Datum dynamisch füllen ---
    @app.callback(
        Output("position-date-selector", "options"),
        Output("position-date-selector", "value"),
        Input("position-behavior-selector", "value"),
    )
    def sync_position_dates(behavior):
        dates = _available_dates(PKL_FOLDER, behavior)
        value = dates[-1] if dates else None
        return [{"label": d, "value": d} for d in dates], value

    # --- Dropdown für Matrix-Heatmap-Datum dynamisch füllen ---
    @app.callback(
        Output("zone-hour-date-selector", "options"),
        Output("zone-hour-date-selector", "value"),
        Input("zone-hour-behavior-selector", "value"),
    )
    def sync_zonehour_dates(behavior):
        dates = _available_dates(PKL_FOLDER, behavior)
        value = dates[-1] if dates else None
        return [{"label": d, "value": d} for d in dates], value

    # --- Matrix-Heatmap: Zone × Stunde ---
    @app.callback(
        Output("zone-hour-heatmap", "figure"),
        Input("zone-hour-behavior-selector", "value"),
        Input("zone-hour-date-selector", "value"),
    )
    def update_zone_hour_heatmap(behavior, date):
        fig = generate_zone_hour_heatmap(
            PKL_FOLDER, behavior, date,
            n_clusters=4, fit_sample_fraction=0.20, predict_sample_fraction=0.25
        )
        return fig
