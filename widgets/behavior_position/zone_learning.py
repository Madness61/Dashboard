# Zonenlernen und -zuweisung für behavior_position.
# Strategie: Ein KMeans pro Tag, In-Memory-Cache; Darstellung kann nach Verhalten filtern, Zonen bleiben konstant.

from __future__ import annotations

from typing import Dict, Tuple, Optional, List
import pandas as pd
import numpy as np

try:
    from sklearn.cluster import KMeans
except Exception as e:
    raise ImportError("scikit-learn wird benötigt (sklearn.cluster.KMeans).") from e

from widgets.utils import load_behavior_data

# Cache: key = (date_iso, n_clusters, random_state) -> KMeans
_MODEL_CACHE: Dict[Tuple[str, int, int], KMeans] = {}

# Erzeugt KMeans mit kompatiblem n_init für verschiedene sklearn-Versionen.
def _make_kmeans(n_clusters: int, random_state: int) -> KMeans:
    try:
        return KMeans(n_clusters=n_clusters, n_init="auto", random_state=random_state)
    except TypeError:
        return KMeans(n_clusters=n_clusters, n_init=10, random_state=random_state)

# Lernt Zonen aus (x_center, y_center) per KMeans auf Stichprobe.
def learn_zones_kmeans(
    df: pd.DataFrame,
    n_clusters: int = 4,
    sample_fraction: float = 0.2,
    max_points: int = 20_000,
    random_state: int = 42,
) -> Tuple[Optional[KMeans], List[str]]:
    feature_cols = ["x_center", "y_center"]
    if df is None or df.empty:
        return None, feature_cols

    feats = df[feature_cols]
    if 0 < sample_fraction < 1.0:
        n = max(1, int(len(feats) * sample_fraction))
        if n > max_points:
            n = max_points
        if n < len(feats):
            feats = feats.sample(n=n, random_state=random_state)

    km = _make_kmeans(n_clusters=n_clusters, random_state=random_state)
    km.fit(feats.values)
    return km, feature_cols

# Weist Zonen-IDs (1..K) per KMeans zu.
def assign_zone_labels(
    df: pd.DataFrame,
    kmeans: Optional[KMeans],
    feature_cols: Tuple[str, str] = ("x_center", "y_center"),
) -> pd.Series:
    if df is None or df.empty or kmeans is None:
        return pd.Series(dtype="int64", name="zone_label")

    X = df[list(feature_cols)].values
    labels = kmeans.predict(X)
    return pd.Series(labels + 1, index=df.index, name="zone_label")

# Bildet Cache-Schlüssel: (datum, k, seed).
def _cache_key(day_iso: str, n_clusters: int, random_state: int) -> Tuple[str, int, int]:
    return (day_iso, n_clusters, random_state)

# Leert den Zonenmodell-Cache ganz oder für ein Datum.
def clear_zone_model_cache(date: Optional[str] = None) -> None:
    if not _MODEL_CACHE:
        return
    if date is None:
        _MODEL_CACHE.clear()
        return

    day_iso = pd.to_datetime(date).date().isoformat()
    keys_to_del = [k for k in _MODEL_CACHE if k[0] == day_iso]
    for k in keys_to_del:
        _MODEL_CACHE.pop(k, None)

# Holt oder trainiert Tages-KMeans ohne Verhaltensfilter und cached es.
def get_or_fit_kmeans_for_date(
    folder_path: str,
    date: str,
    n_clusters: int = 4,
    sample_fraction: float = 0.2,
    max_points: int = 20_000,
    random_state: int = 42,
) -> Tuple[Optional[KMeans], List[str]]:
    feature_cols = ["x_center", "y_center"]
    if not date:
        return None, feature_cols

    day = pd.to_datetime(date).date()
    key = _cache_key(day.isoformat(), n_clusters, random_state)

    km = _MODEL_CACHE.get(key)
    if km is not None:
        return km, feature_cols

    df = load_behavior_data(folder_path)
    if df is None or df.empty:
        return None, feature_cols

    df_day = df[df["date"] == day]
    if df_day.empty:
        return None, feature_cols

    feats = df_day[feature_cols]
    if 0 < sample_fraction < 1.0:
        n = max(1, int(len(feats) * sample_fraction))
        if n > max_points:
            n = max_points
        if n < len(feats):
            feats = feats.sample(n=n, random_state=random_state)

    km = _make_kmeans(n_clusters=n_clusters, random_state=random_state)
    km.fit(feats.values)

    _MODEL_CACHE[key] = km
    return km, feature_cols
