import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from widgets.utils import load_behavior_data

# Stallrahmen (wie in deinen anderen Plots)
STALL_X_MIN, STALL_X_MAX = 50, 820
STALL_Y_MIN, STALL_Y_MAX = 80, 460

ASSETS_BG = "assets/stall_topview.png"  # optionales Top-View-Bild

def _has_bg():
    return os.path.exists(ASSETS_BG)

def generate_spatial_hour_heatmap(
    folder_path: str,
    behavior: str,
    date: str,
    hour: int,
    gridsize: tuple[int,int] = (60, 40),     # x-bins, y-bins
    sample_fraction: float = 0.25,           # Stichprobe fürs Zählen
    max_points: int = 50_000,                # Deckel für Stichprobe
    smoothing_sigma: float | None = 1.0,     # optionales Glätten (requires scipy)
    random_state: int = 42,
):
    df = load_behavior_data(folder_path)
    if df.empty:
        return _empty_fig("Keine Daten geladen.")

    # Filtern
    day = pd.to_datetime(date).date() if date else None
    if day is not None:
        df = df[df["date"] == day]
    if behavior:
        df = df[df["dominant_behavior"] == behavior]
    if hour is not None:
        df = df[df["hour"] == int(hour)]

    if df.empty:
        return _empty_fig(f"Keine Daten für {behavior} – {date} Stunde {hour}")

    # Sampling -> schneller, später hochskalieren
    scale = 1.0
    if 0 < sample_fraction < 1.0:
        n = min(max_points, max(1, int(len(df) * sample_fraction)))
        if n < len(df):
            df = df.sample(n=n, random_state=random_state)
            scale = (len(df.index) / n) if n else 1.0
        else:
            scale = 1.0

    # 2D-Histogramm über Stallkoordinaten
    nx, ny = gridsize
    xbins = np.linspace(STALL_X_MIN, STALL_X_MAX, nx + 1)
    ybins = np.linspace(STALL_Y_MIN, STALL_Y_MAX, ny + 1)
    H, xedges, yedges = np.histogram2d(
        df["x_center"].values,
        df["y_center"].values,
        bins=[xbins, ybins]
    )
    H = H.T * scale  # Heatmap erwartet z[y, x], y invertieren wir per Achse

    # optional glätten
    if smoothing_sigma and smoothing_sigma > 0:
        try:
            from scipy.ndimage import gaussian_filter
            H = gaussian_filter(H, sigma=float(smoothing_sigma))
        except Exception:
            pass  # SciPy nicht zwingend

    # Zellmittelpunkte
    xmid = (xedges[:-1] + xedges[1:]) / 2
    ymid = (yedges[:-1] + yedges[1:]) / 2

    fig = go.Figure()

    # Hintergrundbild (falls vorhanden)
    if _has_bg():
        fig.add_layout_image(
            dict(
                source=f"/{ASSETS_BG}",  # Dash assets
                xref="x", yref="y",
                x=STALL_X_MIN, y=STALL_Y_MAX,
                sizex=(STALL_X_MAX - STALL_X_MIN),
                sizey=(STALL_Y_MAX - STALL_Y_MIN),
                sizing="stretch",
                layer="below",
                opacity=0.65,
            )
        )

    fig.add_trace(
        go.Heatmap(
            x=xmid, y=ymid, z=H,
            coloraxis="coloraxis",
            hovertemplate="x=%{x:.0f}, y=%{y:.0f}<br>Frames: %{z:.0f}<extra></extra>"
        )
    )

    fig.update_layout(
        title=f"Räumliche Aufenthaltsdauer – {behavior} – {date} – Stunde {hour:02d}",
        margin=dict(l=30, r=10, t=50, b=30),
        coloraxis=dict(colorbar_title="Frames (skaliert)"),
        xaxis=dict(range=[STALL_X_MIN, STALL_X_MAX], title="x (Pixel)"),
        yaxis=dict(range=[STALL_Y_MAX, STALL_Y_MIN], title="y (Pixel)"),  # invertiert
    )
    return fig

def _empty_fig(msg: str):
    import plotly.graph_objects as go
    f = go.Figure()
    f.update_layout(title=msg, xaxis_visible=False, yaxis_visible=False)
    return f
