import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from scipy.stats import mode
from sklearn.cluster import DBSCAN

from widgets.utils import BEHAVIORS

# Verhalten → Farbe
BEHAVIOR_COLORS = {
    "lying": "#1f77b4",
    "feeding": "#ff7f0e",
    "investigating": "#2ca02c",
    "defecating": "#d62728",
    "standing": "#9467bd",
    "sitting": "#8c564b",
    "moving": "#e377c2",
    "playing": "#7f7f7f"
}

def generate_zone_map_image_for_date(df, date_str, behavior_filter=None, eps=40, min_samples=100):
    print(f"\n📅 Clustering-Zonenkarte für {date_str}")
    target_date = pd.to_datetime(date_str).date()
    df_day = df[df['date'] == target_date].copy()

    if df_day.empty:
        return f"Keine Daten für {date_str}."

    if behavior_filter:
        df_day = df_day[df_day['dominant_behavior'].isin(behavior_filter)]
        print(f"🔎 Verhalten gefiltert: {behavior_filter}")

    if df_day.empty:
        return f"Keine Daten für diese Filter am {date_str}."

    X = df_day[['x_center', 'y_center']].values

    # Clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
    df_day['cluster'] = clustering.labels_

    print(f"🧮 Cluster gefunden: {df_day['cluster'].nunique() - (-1 in df_day['cluster'].unique())}")

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_title(f"Zonenkarte am {date_str} (DBSCAN)")
    ax.set_xlabel("x (Pixel)")
    ax.set_ylabel("y (Pixel)")
    ax.invert_yaxis()

    clusters = df_day[df_day['cluster'] != -1].groupby('cluster')
    for cluster_id, group in clusters:
        # Dominantes Verhalten im Cluster
        behavior = mode(group['dominant_behavior'], keepdims=True)[0][0]
        color = BEHAVIOR_COLORS.get(behavior, "#cccccc")

        # Punkte
        ax.scatter(group['x_center'], group['y_center'], s=5, alpha=0.5, color=color)

        # Mittelpunkt + Label
        cx, cy = group['x_center'].mean(), group['y_center'].mean()
        ax.text(cx, cy, behavior, fontsize=9, weight='bold', color='black', ha='center', va='center')

    # Legende nur mit verwendeten Verhalten
    used_behaviors = sorted(df_day['dominant_behavior'].unique(), key=lambda b: BEHAVIORS.index(b) if b in BEHAVIORS else 999)
    handles = [plt.Line2D([0], [0], marker='o', linestyle='None',
               color=BEHAVIOR_COLORS.get(b, "#ccc"), label=b)
               for b in used_behaviors]
    ax.legend(handles=handles, title="Verhalten", bbox_to_anchor=(1.05, 1), loc="upper left")

    plt.tight_layout()

    # Encode to base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    print("✅ Zonenbild erfolgreich generiert.")
    return f"data:image/png;base64,{encoded}"
