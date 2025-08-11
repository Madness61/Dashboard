import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

from widgets.utils import load_behavior_data

matplotlib.use("Agg")

PKL_FOLDER = "data/action_detection/loaded"

def get_zone_label(x, y):
    if x < 300:
        return "Ruhebereich"
    elif x > 600:
        return "Fressbereich"
    elif y < 200:
        return "Kotbereich"
    else:
        return "Übergangsbereich"

def generate_zone_duration_image(folder_path, behavior, date):
    df = load_behavior_data(folder_path)
    if df.empty:
        return "Keine Daten geladen."

    df = df[df['dominant_behavior'] == behavior]
    df = df[df['date'] == pd.to_datetime(date).date()]
    if df.empty:
        return f"Keine Daten für {behavior} am {date}"

    df['zone'] = df.apply(lambda row: get_zone_label(row['x_center'], row['y_center']), axis=1)

    zone_counts = df['zone'].value_counts().sort_index()
    zone_hours = (zone_counts / 6 / 60 / 60).round(2)

    fig, ax = plt.subplots(figsize=(8, 4))
    zone_hours.plot(kind='bar', ax=ax, color='steelblue')
    ax.set_ylabel("Zeit in Stunden")
    ax.set_xlabel("Zone")
    ax.set_title(f"{behavior} am {date} – Aufenthaltsdauer je Zone")
    ax.grid(axis='y')

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"

