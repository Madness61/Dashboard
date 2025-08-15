"""
Aufenthaltsdauer je Zone (Barplot) auf Basis eines *tagesweit* gelernten Zonenmodells.

- Die Zonen werden pro Tag (ohne Verhaltensfilter) mittels KMeans gelernt und gecacht.
- Für die Dauerberechnung filtern wir auf das gewünschte Verhalten, weisen aber mit dem
  Tages-Modell die Zone zu -> Zone bleibt über Verhaltenswechsel stabil.
- Optionales Sampling beim Zählen beschleunigt die Aggregation; die Ergebnisse werden
  auf die Gesamtmenge hochskaliert.

Rückgabe: data:image/png;base64,...  (oder ein Fehlertext)
"""

from __future__ import annotations

import io
import base64
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from widgets.utils import load_behavior_data
from widgets.behavior_position.zone_learning import (
    get_or_fit_kmeans_for_date,
    assign_zone_labels,
)

matplotlib.use("Agg")


def generate_zone_duration_image(
    folder_path: str,
    behavior: str,
    date: str,
    n_clusters: int = 4,
    fit_sample_fraction: float = 0.20,      # wird im Tages-Modell verwendet
    predict_sample_fraction: float | None = 0.25,  # Sampling fürs Zählen (None = alle)
    max_fit_points: int = 20_000,
    random_state: int = 42,
) -> str:
    """
    Erzeugt einen Balkenplot der Aufenthaltsdauer (in Stunden) je automatisch gelernter Zone
    für ein gegebenes Verhalten an einem Tag. Zonen sind pro Tag fix (lernen ohne Verhaltensfilter).

    Parameters
    ----------
    folder_path : str
        Ordner mit den geladenen Pickle-Dateien (load_behavior_data liest daraus).
    behavior : str
        Verhalten, für das die Dauer je Zone berechnet werden soll.
    date : str
        Datum im Format 'YYYY-MM-DD'.
    n_clusters : int
        Anzahl der Zonen (KMeans-Cluster).
    fit_sample_fraction : float
        Stichprobenanteil für das *Fitten* des Tages-Modells.
    predict_sample_fraction : float | None
        Stichprobenanteil für das *Zählen* (Zuweisung + Aggregation). None = alle Daten.
    max_fit_points : int
        Obergrenze der Punkte beim Fitten (Performance).
    random_state : int
        RNG für reproduzierbares Sampling.

    Returns
    -------
    str
        "data:image/png;base64,..." oder ein Fehlertext.
    """
    if not date:
        return "Kein Datum gewählt."

    # Tagesdaten (ohne Verhaltensfilter fürs Modell)
    df_all = load_behavior_data(folder_path)
    if df_all is None or df_all.empty:
        return "Keine Daten geladen."

    day = pd.to_datetime(date).date()
    df_day = df_all[df_all["date"] == day]
    if df_day.empty:
        return f"Keine Daten am {date}"

    # Tages-Zonenmodell (ohne Verhaltensfilter) -> stabil über Verhalten
    kmeans, feat_cols = get_or_fit_kmeans_for_date(
        folder_path=folder_path,
        date=date,
        n_clusters=n_clusters,
        sample_fraction=fit_sample_fraction,
        max_points=max_fit_points,
        random_state=random_state,
    )
    if kmeans is None:
        return "Zonenlernen fehlgeschlagen."

    # Für die Dauer: nur das gewählte Verhalten heranziehen
    df = df_day[df_day["dominant_behavior"] == behavior]
    if df.empty:
        return f"Keine Daten für {behavior} am {date}"

    # Zählen mit optionalem Sampling + Hochrechnung
    df_count = df
    scale = 1.0
    if predict_sample_fraction and 0 < predict_sample_fraction < 1.0:
        n = max(1, int(len(df) * predict_sample_fraction))
        if n < len(df):
            df_count = df.sample(n=n, random_state=random_state)
            scale = len(df) / n

    # Zonen zuweisen (mit *Tages*-Modell)
    df_count = df_count.copy()
    df_count["zone_label"] = assign_zone_labels(df_count, kmeans, tuple(feat_cols))

    # Frames -> Stunden (1 Frame ≈ 1/6 s)
    counts = df_count["zone_label"].value_counts().sort_index()
    hours = (counts * scale / 6.0 / 60.0 / 60.0)

    if hours.empty:
        return f"Keine gültigen Zuordnungen für {behavior} am {date}"

    # Schöner beschriften: "Zone 1..K"
    hours.index = [f"Zone {int(z)}" for z in hours.index]

    # Plotten
    fig, ax = plt.subplots(figsize=(8, 4))
    hours.plot(kind="bar", ax=ax)

    ax.set_ylabel("Zeit in Stunden")
    ax.set_xlabel("Zone (automatisch gelernt, tagesweit)")
    ax.set_title(f"{behavior} am {date} – Aufenthaltsdauer je Zone")
    ax.grid(axis="y", alpha=0.3)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)

    data_uri = "data:image/png;base64," + base64.b64encode(buf.read()).decode("utf-8")
    return data_uri
