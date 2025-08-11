import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64

from widgets.utils import load_behavior_data, BEHAVIORS

matplotlib.use("Agg")  # für Webumgebung

# Stallrahmen (optional anpassbar)
STALL_X_MIN = 50
STALL_X_MAX = 820
STALL_Y_MIN = 80
STALL_Y_MAX = 460

PKL_FOLDER = "data/action_detection/loaded"

def generate_behavior_position_image(folder_path, behavior='feeding', date=None):
    df = load_behavior_data(folder_path)

    if df.empty:
        return "Keine Daten geladen."

    if date:
        df = df[df['date'] == pd.to_datetime(date).date()]
    df = df[df['dominant_behavior'] == behavior]

    if df.empty:
        return f"Keine Daten für {behavior} am {date}"

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df['x_center'], df['y_center'], alpha=0.3, s=10)

    ax.set_title(f"Aktivitätspositionen: {behavior} am {date}")
    ax.set_xlabel("x-Position (Pixel)")
    ax.set_ylabel("y-Position (Pixel)")
    ax.set_xlim(STALL_X_MIN - 20, STALL_X_MAX + 20)
    ax.set_ylim(STALL_Y_MAX + 20, STALL_Y_MIN - 20)
    ax.grid(True)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
