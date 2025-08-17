# widgets/activity_budget/plot_budget.py
import os
import glob
import io
import base64
from datetime import datetime

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from widgets.utils import BEHAVIORS

matplotlib.use("Agg")  # für Dash/Webumgebung

PKL_FOLDER = "data/action_detection/loaded"
HOURS_RANGE = range(6, 19)  # 6–18 Uhr


def _log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[plot_budget {ts}] {msg}")


def load_full_dataframe():
    _log(f"Starte load_full_dataframe() – suche PKLs in: {os.path.abspath(PKL_FOLDER)}")
    file_list = sorted(glob.glob(os.path.join(PKL_FOLDER, "*.pkl")))
    _log(f"Gefundene Dateien: {len(file_list)}")
    if len(file_list) <= 10:
        for f in file_list:
            try:
                size_mb = os.path.getsize(f) / (1024 * 1024)
            except Exception:
                size_mb = -1
            _log(f"  - {os.path.basename(f)} ({size_mb:.2f} MB)")

    if not file_list:
        _log("ABBRUCH: Keine PKL-Dateien gefunden.")
        return pd.DataFrame()

    dfs = []
    for f in file_list:
        try:
            df = pd.read_pickle(f)
            if "t" not in df.columns:
                _log(f"WARNUNG: Spalte 't' fehlt in {os.path.basename(f)} – Spalten={list(df.columns)[:10]}...")
            else:
                df["t"] = pd.to_datetime(df["t"], errors="coerce")

            # Fehlende BEHAVIOR-Spalten mit 0 auffüllen, damit idxmax später nicht crasht
            missing_beh = [b for b in BEHAVIORS if b not in df.columns]
            if missing_beh:
                _log(f"WARNUNG: {len(missing_beh)} Verhaltensspalten fehlen und werden mit 0 ergänzt: {missing_beh}")
                for b in missing_beh:
                    df[b] = 0.0

            dfs.append(df)
            _log(f"geladen: {os.path.basename(f)} – Zeilen={len(df)}, Spalten={len(df.columns)}")
        except Exception as e:
            _log(f"FEHLER beim Laden {os.path.basename(f)}: {e}")

    if not dfs:
        _log("ABBRUCH: Keine DataFrames erfolgreich geladen.")
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)
    _log(f"Concat fertig – Gesamtzeilen={len(df)}, Spalten={len(df.columns)}")
    try:
        mem_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        _log(f"Speicherschätzung DataFrame: {mem_mb:.1f} MB")
    except Exception:
        pass

    # Basismerkmale
    if "t" in df.columns:
        df["date"] = df["t"].dt.date
        df["hour"] = df["t"].dt.hour
        _log(
            f"Zeitfenster: min={df['t'].min()} | max={df['t'].max()} | "
            f"Anzahl Tage={df['date'].nunique()} | Stundenwerte vorhanden={sorted(df['hour'].dropna().unique().tolist())[:10]}..."
        )
    else:
        _log("WARNUNG: 't' nicht vorhanden/parsebar – 'date'/'hour' werden fehlen.")

    # Dominantes Verhalten (auf Basis der BEHAVIORS)
    try:
        df["dominant_behavior"] = df[BEHAVIORS].idxmax(axis=1)
        _log("dominant_behavior berechnet (idxmax über BEHAVIORS).")
    except Exception as e:
        _log(f"FEHLER bei idxmax über BEHAVIORS: {e}")
        # Fallback: lege Spalte trotzdem an
        df["dominant_behavior"] = None

    _log("load_full_dataframe() abgeschlossen.")
    return df


def _fig_to_data_uri(fig) -> str:
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    _log(f"PNG erzeugt – Base64-Länge={len(b64)}")
    return f"data:image/png;base64,{b64}"


def generate_single_day_plot(date_str: str):
    _log(f"generate_single_day_plot(date_str='{date_str}') aufgerufen.")
    df = load_full_dataframe()
    if df.empty:
        _log("ABBRUCH: DataFrame ist leer.")
        return "Keine Daten vorhanden."

    try:
        target_date = pd.to_datetime(date_str).date()
        _log(f"Ziel-Datum geparst: {target_date}")
    except Exception as e:
        _log(f"FEHLER: Konnte date_str nicht parsen: {e}")
        return f"Ungültiges Datum: {date_str}"

    df_day = df[df.get("date") == target_date]
    _log(f"Zeilen am Ziel-Datum: {len(df_day)}")
    if df_day.empty:
        _log("ABBRUCH: Keine Zeilen für Ziel-Datum.")
        return f"Keine Daten für {date_str}"

    # Sicherstellen, dass HOURS_RANGE und BEHAVIORS vollständig abgedeckt werden
    all_index = pd.MultiIndex.from_product(
        [HOURS_RANGE, BEHAVIORS],
        names=["hour", "dominant_behavior"],
    )

    try:
        grouped = (
            df_day.groupby(["hour", "dominant_behavior"])
            .size()
            .reindex(all_index, fill_value=0)
        )
        behavior_counts = grouped.unstack(fill_value=0)
        _log(f"groupby fertig – shape behavior_counts={behavior_counts.shape}")
    except Exception as e:
        _log(f"FEHLER bei groupby/unstack: {e}")
        return "Fehler bei der Tagesaggregation."

    try:
        percentages = behavior_counts.div(behavior_counts.sum(axis=1), axis=0).fillna(0) * 100
        _log("Prozentwerte berechnet.")
    except Exception as e:
        _log(f"FEHLER bei Prozentrechnung: {e}")
        return "Fehler bei der Normalisierung auf Prozent."

    # Nur sichtbare Klassen (kein lying), leere Stunden auffüllen
    stacked_df = (
        percentages.drop(columns="lying", errors="ignore")
        .reindex(pd.Index(HOURS_RANGE, name="hour"), fill_value=0)
    )
    sum_visible = stacked_df.sum(axis=1)
    rest_series = (100 - sum_visible).clip(lower=0)
    _log(
        f"Stacked-Daten: shape={stacked_df.shape} | "
        f"min sichtb. Summe={sum_visible.min():.2f} | max sichtb. Summe={sum_visible.max():.2f}"
    )

    # Plot
    try:
        fig, ax1 = plt.subplots(figsize=(10, 5))
        stacked_df.plot(kind="bar", stacked=True, ax=ax1, colormap="tab20")
        ax2 = ax1.twinx()
        ax2.plot(range(len(HOURS_RANGE)), rest_series.values, color="black", linewidth=2, linestyle="--", label="Rest zu 100 %")
        ax1.set_ylim(0, 100)
        ax2.set_ylim(0, 100)
        ax1.set_ylabel("Anteil an Frames (%)")
        ax2.set_ylabel("Nicht dargestellte Anteile (%)")
        ax1.set_xlabel("Stunde")
        ax1.set_title(f"Aktivitätsbudget am {date_str} (Rest als Linie)")
        ax1.set_xticks(range(len(HOURS_RANGE)))
        ax1.set_xticklabels([f"{h}:00" for h in HOURS_RANGE])

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, title="Verhalten", bbox_to_anchor=(1.05, 1), loc="upper left")
        _log("Plot für Einzeltag erstellt.")
        return _fig_to_data_uri(fig)
    except Exception as e:
        _log(f"FEHLER beim Plotten (Einzeltag): {e}")
        return "Fehler beim Erstellen der Tagesgrafik."


def generate_aggregated_plot():
    _log("generate_aggregated_plot() aufgerufen.")
    df = load_full_dataframe()
    if df.empty:
        _log("ABBRUCH: DataFrame ist leer.")
        return "Keine Daten vorhanden."

    try:
        unique_dates = sorted(df["date"].dropna().unique())
        _log(f"Anzahl Tage gesamt: {len(unique_dates)} – Beispiel: {unique_dates[:5]}")
    except Exception as e:
        _log(f"FEHLER: 'date' fehlt oder ist unbrauchbar: {e}")
        return "Fehler: Keine gültigen Datumsinformationen."

    all_index = pd.MultiIndex.from_product(
        [unique_dates, HOURS_RANGE, BEHAVIORS],
        names=["date", "hour", "dominant_behavior"],
    )

    try:
        grouped = (
            df.groupby(["date", "hour", "dominant_behavior"])
            .size()
            .reindex(all_index, fill_value=0)
        )
        counts = grouped.unstack(fill_value=0)
        _log(f"groupby fertig – counts.shape={counts.shape}")
    except Exception as e:
        _log(f"FEHLER bei groupby/unstack (aggregiert): {e}")
        return "Fehler bei der Aggregation über Tage."

    try:
        percentages = counts.div(counts.sum(axis=1), axis=0).fillna(0) * 100
        mean_per_hour = percentages.groupby("hour").mean().reindex(HOURS_RANGE, fill_value=0)
        _log(f"Prozentwerte + Stundenmittel berechnet – mean_per_hour.shape={mean_per_hour.shape}")
    except Exception as e:
        _log(f"FEHLER bei Prozentrechnung/Mean: {e}")
        return "Fehler bei der Normalisierung der aggregierten Daten."

    stacked_df = mean_per_hour.drop(columns="lying", errors="ignore")
    sum_visible = stacked_df.sum(axis=1)
    rest_series = (100 - sum_visible).clip(lower=0)
    _log(
        f"Stacked-Daten (agg.): shape={stacked_df.shape} | "
        f"min sichtb. Summe={sum_visible.min():.2f} | max sichtb. Summe={sum_visible.max():.2f}"
    )

    try:
        fig, ax1 = plt.subplots(figsize=(10, 5))
        stacked_df.plot(kind="bar", stacked=True, ax=ax1, colormap="tab20")
        ax2 = ax1.twinx()
        ax2.plot(range(len(HOURS_RANGE)), rest_series.values, color="black", linestyle="--", linewidth=2, label="Rest zu 100 %")
        ax1.set_ylim(0, 100)
        ax2.set_ylim(0, 100)
        ax1.set_ylabel("Durchschnittlicher Anteil an Frames (%)")
        ax2.set_ylabel("Nicht dargestellte Anteile (%)")
        ax1.set_xlabel("Stunde")
        ax1.set_title("Aggregiertes Aktivitätsbudget über alle Tage (Rest als Linie)")
        ax1.set_xticks(range(len(HOURS_RANGE)))
        ax1.set_xticklabels([f"{h}:00" for h in HOURS_RANGE])

        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax1.legend(h1 + h2, l1 + l2, title="Verhalten", bbox_to_anchor=(1.05, 1), loc="upper left")
        _log("Plot für Aggregation erstellt.")
        return _fig_to_data_uri(fig)
    except Exception as e:
        _log(f"FEHLER beim Plotten (Aggregation): {e}")
        return "Fehler beim Erstellen der aggregierten Grafik."
