import pandas as pd
import plotly.express as px

from widgets.utils import load_behavior_data
from widgets.behavior_position.zone_learning import (
    get_or_fit_kmeans_for_date,
    assign_zone_labels,
)

def generate_zone_hour_heatmap(
    folder_path: str,
    behavior: str,
    date: str,
    n_clusters: int = 4,
    fit_sample_fraction: float = 0.20,          # fürs *Tages*-Modell (stabil pro Datum)
    predict_sample_fraction: float | None = 0.25,  # Sampling fürs Zählen (None = alle)
    max_fit_points: int = 20_000,
    random_state: int = 42,
):
    if not date:
        return _err("Kein Datum gewählt.")

    df_all = load_behavior_data(folder_path)
    if df_all is None or df_all.empty:
        return _err("Keine Daten geladen.")

    day = pd.to_datetime(date).date()
    df_day = df_all[df_all["date"] == day]
    if df_day.empty:
        return _err(f"Keine Daten am {date}")

    # 🔒 Zonenmodell PRO TAG (ohne Verhaltensfilter) -> Zonen bleiben bei Verhaltenswechsel konstant
    kmeans, feat_cols = get_or_fit_kmeans_for_date(
        folder_path=folder_path,
        date=date,
        n_clusters=n_clusters,
        sample_fraction=fit_sample_fraction,
        max_points=max_fit_points,
        random_state=random_state,
    )
    if kmeans is None:
        return _err("Zonenlernen fehlgeschlagen.")

    # Für die Heatmap nach Verhalten filtern (Zonen bleiben gleich)
    df = df_day[df_day["dominant_behavior"] == behavior]
    if df.empty:
        return _err(f"Keine Daten für {behavior} am {date}")

    # Optionales Sampling fürs Zählen + Hochrechnung
    scale = 1.0
    if predict_sample_fraction and 0 < predict_sample_fraction < 1.0:
        n = max(1, int(len(df) * predict_sample_fraction))
        if n < len(df):
            df = df.sample(n=n, random_state=random_state)
            scale = len(df) / n

    # Zonen zuweisen und Zone×Stunde aggregieren
    df = df.copy()
    df["zone_label"] = assign_zone_labels(df, kmeans, tuple(feat_cols))
    grp = df.groupby(["zone_label", "hour"]).size().reset_index(name="count")
    grp["count"] = grp["count"] * scale

    # Pivot: Zeilen = Zonen, Spalten = Stunden
    pivot = grp.pivot(index="zone_label", columns="hour", values="count").fillna(0.0)
    pivot.index = [f"Zone {int(z)}" for z in pivot.index]  # hübschere Labels

    fig = px.imshow(
        pivot,
        labels=dict(x="Stunde", y="Zone", color="Frames (skaliert)"),
        aspect="auto",
    )
    fig.update_layout(
        title=f"Aufenthaltsdauer pro Zone & Stunde – {behavior} ({date})",
        xaxis_nticks=13,
        margin=dict(l=40, r=10, t=60, b=40),
    )
    return fig

def _err(msg: str):
    import plotly.graph_objects as go
    f = go.Figure()
    f.update_layout(title=msg, xaxis_visible=False, yaxis_visible=False, margin=dict(l=40,r=10,t=60,b=40))
    return f
