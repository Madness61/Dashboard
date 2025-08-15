import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io, base64
from widgets.utils import load_behavior_data

matplotlib.use("Agg")

STALL_X_MIN, STALL_X_MAX = 50, 820
STALL_Y_MIN, STALL_Y_MAX = 80, 460

def generate_behavior_position_image(
    folder_path,
    behavior='feeding',
    date=None,
    sample_fraction: float = 0.10,
    max_points: int = 10000,
    random_state: int = 42
):
    df = load_behavior_data(folder_path)
    if df.empty:
        return "Keine Daten geladen."

    if date:
        df = df[df['date'] == pd.to_datetime(date).date()]
    if behavior:
        df = df[df['dominant_behavior'] == behavior]

    if df.empty:
        return f"Keine Daten für {behavior} am {date}"

    # 🔹 Sampling für schnelleres Plotten
    if 0 < sample_fraction < 1.0:
        n = min(max_points, max(1, int(len(df) * sample_fraction)))
        if n < len(df):
            df = df.sample(n=n, random_state=random_state)

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
