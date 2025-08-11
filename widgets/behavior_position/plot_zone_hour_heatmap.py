import pandas as pd
import plotly.express as px
from widgets.utils import load_behavior_data

PKL_FOLDER = "data/action_detection/loaded"

# 🧱 Manuell definierte Zonen
ZONES = [
    {"name": "Fressen",     "x1": 600, "x2": 820, "y1": 300, "y2": 460},
    {"name": "Liegen",      "x1": 300, "x2": 600, "y1": 400, "y2": 460},
    {"name": "Spielen",     "x1": 100, "x2": 300, "y1": 200, "y2": 400},
    {"name": "Gangzone",    "x1": 100, "x2": 820, "y1": 80,  "y2": 300}
]

def generate_zone_hour_heatmap(folder_path, behavior="feeding", date=None):
    df = load_behavior_data(folder_path)
    if df.empty:
        return "Keine Daten vorhanden."

    if date:
        df = df[df['date'] == pd.to_datetime(date).date()]
    if behavior:
        df = df[df['dominant_behavior'] == behavior]
    if df.empty:
        return f"Keine Daten für {behavior} am {date}"

    # 🔁 Zonen zuweisen
    def assign_zone(row):
        for zone in ZONES:
            if zone["x1"] <= row["x_center"] <= zone["x2"] and zone["y1"] <= row["y_center"] <= zone["y2"]:
                return zone["name"]
        return "Unbekannt"

    df['zone_name'] = df.apply(assign_zone, axis=1)
    df = df[df['zone_name'] != "Unbekannt"]

    # Gruppieren
    grouped = df.groupby(['zone_name', 'hour']).size().reset_index(name='count')
    pivot = grouped.pivot(index='zone_name', columns='hour', values='count').fillna(0)

    fig = px.imshow(
        pivot,
        color_continuous_scale='YlOrRd',
        labels=dict(x="Stunde", y="Zone", color="Anzahl Frames"),
        aspect="auto"
    )
    fig.update_layout(
        title=f"Zone-Stunde-Nutzung für: {behavior} ({date})",
        xaxis_nticks=13
    )
    return fig
