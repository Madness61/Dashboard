import os, glob, io, base64
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import plotly.graph_objects as go

from widgets.utils import BEHAVIORS

matplotlib.use("Agg")

PKL_FOLDER = "data/action_detection/loaded"
HOURS_RANGE = range(6, 19)

def load_full_dataframe():
    files = sorted(glob.glob(os.path.join(PKL_FOLDER, "*.pkl")))
    if not files:
        return pd.DataFrame()
    dfs = []
    for f in files:
        df = pd.read_pickle(f)
        df["t"] = pd.to_datetime(df["t"])
        dfs.append(df)
    df = pd.concat(dfs)
    df["dominant_behavior"] = df[BEHAVIORS].idxmax(axis=1)
    df["date"] = df["t"].dt.date
    df["hour"] = df["t"].dt.hour
    return df

# ---------------- PNG für Preview-Kachel ----------------
def _png_from_fig(fig):
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode()}"

def generate_single_day_plot(date_str: str):
    df = load_full_dataframe()
    if df.empty: return "Keine Daten vorhanden."
    d = pd.to_datetime(date_str).date()
    day = df[df["date"] == d]
    if day.empty: return f"Keine Daten für {date_str}"

    idx = pd.MultiIndex.from_product([HOURS_RANGE, BEHAVIORS], names=["hour","dominant_behavior"])
    counts = day.groupby(["hour","dominant_behavior"]).size().reindex(idx, fill_value=0).unstack(fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0).fillna(0)*100
    stacked = pct.drop(columns="lying", errors="ignore").reindex(pd.Index(HOURS_RANGE, name="hour"), fill_value=0)
    rest = (100 - stacked.sum(axis=1)).clip(lower=0)

    fig, ax1 = plt.subplots(figsize=(10,5))
    stacked.plot(kind="bar", stacked=True, ax=ax1, colormap="tab20")
    ax2 = ax1.twinx()
    ax2.plot(range(len(HOURS_RANGE)), rest.values, color="black", linewidth=2, linestyle="--", label="Rest zu 100 %")
    ax2.set_ylim(0,100); ax2.set_ylabel("")                  # rechte Achse: Label entfernen
    ax1.set_ylim(0,100); ax1.set_ylabel("Anteil an Frames (%)")
    ax1.set_xlabel("Stunde"); ax1.set_title(f"Aktivitätsbudget am {date_str}")
    ax1.set_xticks(range(len(HOURS_RANGE))); ax1.set_xticklabels([f"{h}:00" for h in HOURS_RANGE])
    h1,l1=ax1.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, title="Verhalten", bbox_to_anchor=(1.05,1), loc="upper left")
    return _png_from_fig(fig)

def generate_aggregated_plot():
    df = load_full_dataframe()
    if df.empty: return "Keine Daten vorhanden."
    idx = pd.MultiIndex.from_product([sorted(df["date"].unique()), HOURS_RANGE, BEHAVIORS],
                                     names=["date","hour","dominant_behavior"])
    counts = df.groupby(["date","hour","dominant_behavior"]).size().reindex(idx, fill_value=0).unstack(fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0).fillna(0)*100
    mean_h = pct.groupby("hour").mean().reindex(HOURS_RANGE, fill_value=0)
    stacked = mean_h.drop(columns="lying", errors="ignore")
    rest = (100 - stacked.sum(axis=1)).clip(lower=0)

    fig, ax1 = plt.subplots(figsize=(10,5))
    stacked.plot(kind="bar", stacked=True, ax=ax1, colormap="tab20")
    ax2 = ax1.twinx()
    ax2.plot(range(len(HOURS_RANGE)), rest.values, color="black", linestyle="--", linewidth=2, label="Rest zu 100 %")
    ax2.set_ylim(0,100); ax2.set_ylabel("")                  # rechte Achse: Label entfernen
    ax1.set_ylim(0,100); ax1.set_ylabel("Durchschnittlicher Anteil an Frames (%)")
    ax1.set_xlabel("Stunde"); ax1.set_title("Aggregiertes Aktivitätsbudget über alle Tage")
    ax1.set_xticks(range(len(HOURS_RANGE))); ax1.set_xticklabels([f"{h}:00" for h in HOURS_RANGE])
    h1,l1=ax1.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, title="Verhalten", bbox_to_anchor=(1.05,1), loc="upper left")
    return _png_from_fig(fig)

# ---------------- Plotly (interaktiv) ----------------
def _barline(stacked_df: pd.DataFrame, rest: pd.Series, title: str, y_label: str) -> go.Figure:
    labels = [f"{h}:00" for h in HOURS_RANGE]
    fig = go.Figure()
    for col in stacked_df.columns:
        fig.add_trace(go.Bar(x=labels, y=stacked_df[col], name=col))
    fig.add_trace(go.Scatter(x=labels, y=rest.values, name="Rest zu 100 %", mode="lines",
                             line=dict(color="black", dash="dash"), yaxis="y2"))
    fig.update_layout(
        title=title, barmode="stack",
        yaxis=dict(title=y_label, range=[0,100]),
        yaxis2=dict(title="", range=[0,100], overlaying="y", side="right", showgrid=False),
        xaxis=dict(title="Stunde"),
        legend=dict(title="Verhalten", x=1.05, y=1),
        margin=dict(l=50, r=150, t=50, b=50),
    )
    return fig

def generate_single_day_figure(date_str: str):
    df = load_full_dataframe()
    if df.empty: return "Keine Daten vorhanden."
    d = pd.to_datetime(date_str).date()
    day = df[df["date"] == d]
    if day.empty: return f"Keine Daten für {date_str}"
    idx = pd.MultiIndex.from_product([HOURS_RANGE, BEHAVIORS], names=["hour","dominant_behavior"])
    counts = day.groupby(["hour","dominant_behavior"]).size().reindex(idx, fill_value=0).unstack(fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0).fillna(0)*100
    stacked = pct.drop(columns="lying", errors="ignore").reindex(pd.Index(HOURS_RANGE, name="hour"), fill_value=0)
    rest = (100 - stacked.sum(axis=1)).clip(lower=0)
    return _barline(stacked, rest, f"Aktivitätsbudget am {date_str}", "Anteil an Frames (%)")

def generate_aggregated_figure():
    df = load_full_dataframe()
    if df.empty: return "Keine Daten vorhanden."
    idx = pd.MultiIndex.from_product([sorted(df["date"].unique()), HOURS_RANGE, BEHAVIORS],
                                     names=["date","hour","dominant_behavior"])
    counts = df.groupby(["date","hour","dominant_behavior"]).size().reindex(idx, fill_value=0).unstack(fill_value=0)
    pct = counts.div(counts.sum(axis=1), axis=0).fillna(0)*100
    mean_h = pct.groupby("hour").mean().reindex(HOURS_RANGE, fill_value=0)
    stacked = mean_h.drop(columns="lying", errors="ignore")
    rest = (100 - stacked.sum(axis=1)).clip(lower=0)
    return _barline(stacked, rest, "Aggregiertes Aktivitätsbudget über alle Tage",
                    "Durchschnittlicher Anteil an Frames (%)")

# ---------------- Heatmap (wie auf Verhalten, aber hier im Aktivitätsbudget) ----------------
def generate_behavior_heatmap(behavior: str):
    df = load_full_dataframe()
    if df.empty: return "Keine Daten vorhanden."
    if behavior not in BEHAVIORS: return f"Unbekanntes Verhalten: {behavior}"

    idx = pd.MultiIndex.from_product([sorted(df["date"].unique()), HOURS_RANGE], names=["date","hour"])
    series = df.groupby(["date", "hour"])[behavior].mean().reindex(idx, fill_value=0)
    pivot = series.unstack("hour").reindex(columns=HOURS_RANGE, fill_value=0)

    x = [f"{h}:00" for h in HOURS_RANGE]
    y = [pd.to_datetime(str(d)).strftime("%b %d") for d in pivot.index]
    z = (pivot.values * 100).tolist()

    fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y, colorscale="OrRd",
                                    colorbar=dict(title="Ø Verhalten (%)")))
    fig.update_layout(
        title=f"Tagesmuster: {behavior} über Stunden",
        xaxis_title="Stunde", yaxis_title="Datum",
        margin=dict(l=60, r=60, t=50, b=50),
    )
    return fig
