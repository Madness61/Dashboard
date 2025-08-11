import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.patches import Rectangle
from widgets.utils import load_behavior_data

# Definierte feste Zonen
ZONES = [
    {"name": "Fressen",     "x1": 600, "x2": 820, "y1": 300, "y2": 460},
    {"name": "Liegen",      "x1": 300, "x2": 600, "y1": 400, "y2": 460},
    {"name": "Spielen",     "x1": 100, "x2": 300, "y1": 200, "y2": 400},
    {"name": "Gangzone",    "x1": 100, "x2": 820, "y1": 80,  "y2": 300}
]

def generate_zone_overview_image(folder_path, behavior, date):
    df = load_behavior_data(folder_path)
    if df.empty:
        return "Keine Daten geladen."

    df = df[df['dominant_behavior'] == behavior]
    df = df[df['date'] == pd.to_datetime(date).date()]
    if df.empty:
        return f"Keine Daten für {behavior} am {date}"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(50, 820)
    ax.set_ylim(460, 80)  # Invertierte Y-Achse
    ax.set_title(f"Zonenübersicht: {behavior} am {date}")
    ax.set_xlabel("x (Pixel)")
    ax.set_ylabel("y (Pixel)")
    ax.grid(True)

    # Streupunkte
    ax.scatter(df['x_center'], df['y_center'], alpha=0.4, s=8, label="Positionen")

    # Zonen einzeichnen
    for zone in ZONES:
        rect = Rectangle(
            (zone['x1'], zone['y1']),
            zone['x2'] - zone['x1'],
            zone['y2'] - zone['y1'],
            linewidth=2,
            edgecolor='black',
            facecolor='none'
        )
        ax.add_patch(rect)
        cx = (zone['x1'] + zone['x2']) / 2
        cy = (zone['y1'] + zone['y2']) / 2
        ax.text(cx, cy, zone['name'], ha='center', va='center', fontsize=10, weight='bold')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
