import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import glob
import os

from widgets.utils import BEHAVIORS

matplotlib.use("Agg")  # für Dash/Webumgebung

PKL_FOLDER = "data/action_detection/loaded"
HOURS_RANGE = range(6, 19)  # 6–18 Uhr

def load_full_dataframe():
    file_list = sorted(glob.glob(os.path.join(PKL_FOLDER, "*.pkl")))
    if not file_list:
        return pd.DataFrame()

    dfs = []
    for f in file_list:
        df = pd.read_pickle(f)
        df['t'] = pd.to_datetime(df['t'])
        dfs.append(df)

    df = pd.concat(dfs)
    df['dominant_behavior'] = df[BEHAVIORS].idxmax(axis=1)
    df['date'] = df['t'].dt.date
    df['hour'] = df['t'].dt.hour

    return df


def generate_single_day_plot(date_str):
    df = load_full_dataframe()
    if df.empty:
        return "Keine Daten vorhanden."

    target_date = pd.to_datetime(date_str).date()
    df = df[df['date'] == target_date]
    if df.empty:
        return f"Keine Daten für {date_str}"

    all_index = pd.MultiIndex.from_product(
        [HOURS_RANGE, BEHAVIORS],
        names=["hour", "dominant_behavior"]
    )
    grouped = (
        df.groupby(['hour', 'dominant_behavior'])
        .size()
        .reindex(all_index, fill_value=0)
    )

    behavior_counts = grouped.unstack(fill_value=0)
    percentages = behavior_counts.div(behavior_counts.sum(axis=1), axis=0).fillna(0) * 100

    # Nur relevante Stunden, kein lying
    empty_index = pd.Index(HOURS_RANGE, name="hour")
    stacked_df = percentages.drop(columns="lying", errors="ignore").reindex(empty_index, fill_value=0)

    # Rest = 100 – Summe sichtbarer Anteile
    sum_visible = stacked_df.sum(axis=1)
    rest_series = 100 - sum_visible
    rest_series = rest_series.clip(lower=0)

    # Plot
    fig, ax1 = plt.subplots(figsize=(10, 5))
    stacked_df.plot(kind='bar', stacked=True, ax=ax1, colormap='tab20')

    # Linie für Rest
    ax2 = ax1.twinx()
    ax2.plot(
        range(len(HOURS_RANGE)),
        rest_series.values,
        color='black',
        linewidth=2,
        linestyle='--',
        label='Rest zu 100 %'
    )
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Nicht dargestellte Anteile (%)")

    # Achsen
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("Anteil an Frames (%)")
    ax1.set_xlabel("Stunde")
    ax1.set_title(f"Aktivitätsbudget am {date_str} (Rest als Linie)")
    ax1.set_xticks(range(len(HOURS_RANGE)))
    ax1.set_xticklabels([f"{h}:00" for h in HOURS_RANGE])

    # Legende
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, title="Verhalten", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Speichern
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"



def generate_aggregated_plot():
    df = load_full_dataframe()
    if df.empty:
        return "Keine Daten vorhanden."

    all_index = pd.MultiIndex.from_product(
        [sorted(df['date'].unique()), HOURS_RANGE, BEHAVIORS],
        names=["date", "hour", "dominant_behavior"]
    )
    grouped = (
        df.groupby(['date', 'hour', 'dominant_behavior'])
        .size()
        .reindex(all_index, fill_value=0)
    )

    counts = grouped.unstack(fill_value=0)
    percentages = counts.div(counts.sum(axis=1), axis=0).fillna(0) * 100
    mean_per_hour = percentages.groupby('hour').mean().reindex(HOURS_RANGE, fill_value=0)

    # Nur sichtbare Verhaltensklassen (kein lying)
    stacked_df = mean_per_hour.drop(columns='lying', errors='ignore')

    # Berechne Rest als fehlenden Anteil auf 100 %
    sum_visible = stacked_df.sum(axis=1)
    rest_series = 100 - sum_visible
    rest_series = rest_series.clip(lower=0)

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # Gestapelte Balken
    stacked_df.plot(kind='bar', stacked=True, ax=ax1, colormap='tab20')

    # Linie für Rest (zweite Achse)
    ax2 = ax1.twinx()
    ax2.plot(
        range(len(HOURS_RANGE)),
        rest_series.values,
        color='black',
        linestyle='--',
        linewidth=2,
        label='Rest zu 100 %'
    )
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("Nicht dargestellte Anteile (%)")

    # Achsentitel etc.
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("Durchschnittlicher Anteil an Frames (%)")
    ax1.set_xlabel("Stunde")
    ax1.set_title("Aggregiertes Aktivitätsbudget über alle Tage (Rest als Linie)")
    ax1.set_xticks(range(len(HOURS_RANGE)))
    ax1.set_xticklabels([f"{h}:00" for h in HOURS_RANGE])

    # Legende kombinieren
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, title="Verhalten", bbox_to_anchor=(1.05, 1), loc='upper left')

    # Speichern als PNG im Speicher
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"