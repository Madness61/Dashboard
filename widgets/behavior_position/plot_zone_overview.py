import os
import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

from widgets.utils import load_behavior_data
from widgets.behavior_position.zone_learning import learn_zones_kmeans

matplotlib.use("Agg")

# Optionales Hintergrundbild (Top‑View des Stalls).
# Lege z.B. ein Foto oder Schema als PNG hier ab:
#   assets/stall_topview.png
ASSETS_BG = "assets/stall_topview.png"

# Stallrahmen für Achsen (wie in deinen Plots)
STALL_X_MIN, STALL_X_MAX = 50, 820
STALL_Y_MIN, STALL_Y_MAX = 80, 460

# Heuristik: Clusterzentren -> semantische Zonenbezeichnung
# (anpassbar an deine Stallgeometrie)
def name_from_centroid(cx, cy):
    # Recht weit rechts -> Fressbereich
    if cx > (STALL_X_MIN + 0.75 * (STALL_X_MAX - STALL_X_MIN)):
        return "Fressbereich"
    # sehr weit oben -> Kotbereich
    if cy < (STALL_Y_MIN + 0.35 * (STALL_Y_MAX - STALL_Y_MIN)):
        return "Kotbereich"
    # unten -> Liegebereich
    if cy > (STALL_Y_MIN + 0.75 * (STALL_Y_MAX - STALL_Y_MIN)):
        return "Liegebereich"
    # Rest -> Gang/Übergang
    return "Übergangs-/Gangzone"

def _load_bg_image(ax):
    if os.path.exists(ASSETS_BG):
        try:
            img = plt.imread(ASSETS_BG)
            ax.imshow(img, extent=[STALL_X_MIN, STALL_X_MAX, STALL_Y_MAX, STALL_Y_MIN])  # invert y
            return True
        except Exception:
            pass
    # Fallback: helles Rechteck als Schema
    ax.imshow(
        np.ones((10, 10, 3)),
        extent=[STALL_X_MIN, STALL_X_MAX, STALL_Y_MAX, STALL_Y_MIN]
    )
    return False

def generate_zone_overview_image(
    folder_path,
    date: str | None,
    behavior_filter: str | None = None,
    n_clusters: int = 4,
    fit_sample_fraction: float = 0.2,
    max_fit_points: int = 20000,
    random_state: int = 42
):
    """Erstellt ein Bild: Hintergrund (Stall) + gelernten Zonen (als farbige Flächen) + Legende."""
    df = load_behavior_data(folder_path)
    if df.empty:
        return "Keine Daten geladen."

    if date:
        df = df[df["date"] == pd.to_datetime(date).date()]
    if behavior_filter:
        df = df[df["dominant_behavior"] == behavior_filter]
    if df.empty:
        return f"Keine Daten für Filter am {date}"

    # Zonen auf Stichprobe lernen
    kmeans, feat_cols = learn_zones_kmeans(
        df, n_clusters=n_clusters,
        sample_fraction=fit_sample_fraction,
        max_points=max_fit_points,
        random_state=random_state
    )
    if kmeans is None:
        return "Zonenlernen fehlgeschlagen."

    # Clusterzentren & semantische Namen
    centers = kmeans.cluster_centers_
    zone_names = [name_from_centroid(cx, cy) for (cx, cy) in centers]

    # Einfache Polygone um Cluster (konvexe Hülle der Clusterpunkte)
    try:
        from scipy.spatial import ConvexHull
        use_hull = True
    except Exception:
        use_hull = False

    # Für die Hüllen brauchen wir ein paar Punkte pro Cluster
    labels = kmeans.predict(df[feat_cols].values)
    df_plot = df.copy()
    df_plot["zone_id"] = labels  # 0..K-1

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(STALL_X_MIN - 20, STALL_X_MAX + 20)
    ax.set_ylim(STALL_Y_MAX + 20, STALL_Y_MIN - 20)  # invert y
    ax.set_xlabel("x (Pixel)")
    ax.set_ylabel("y (Pixel)")
    ax.set_title(f"Stallübersicht – automatisch gelernte Zonen ({date})")

    _load_bg_image(ax)

    # Farben pro Zone (wiederverwendbar)
    cmap = plt.get_cmap("tab10")
    handles = []
    for zid in range(len(centers)):
        color = cmap(zid % 10)
        pts = df_plot[df_plot["zone_id"] == zid][["x_center", "y_center"]].values

        # Hülle zeichnen, sonst Punktwolke dünn
        if use_hull and len(pts) >= 3:
            try:
                hull = ConvexHull(pts)
                poly = pts[hull.vertices]
                ax.fill(poly[:,0], poly[:,1], alpha=0.25, color=color, edgecolor=color, linewidth=1.0)
            except Exception:
                ax.scatter(pts[:,0], pts[:,1], s=3, alpha=0.2, color=color)
        else:
            ax.scatter(pts[:,0], pts[:,1], s=3, alpha=0.2, color=color)

        cx, cy = centers[zid]
        ax.scatter([cx], [cy], s=60, color=color, edgecolor="black", zorder=3)
        ax.text(cx, cy, f"Zone {zid+1}", ha="center", va="center", fontsize=9, weight="bold")

        # Legenden-Handle sammeln
        handles.append(plt.Line2D([0],[0], marker='s', linestyle='None', color=color, label=f"Zone {zid+1} – {zone_names[zid]}"))

    # Legende rechts außen
    if handles:
        ax.legend(handles=handles, title="Zonenzuordnung", bbox_to_anchor=(1.02, 1), loc="upper left")

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
