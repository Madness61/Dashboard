import pandas as pd
import plotly.express as px
from widgets.utils import load_behavior_data, BEHAVIORS

PKL_FOLDER = "data/action_detection/loaded"
HOURS_RANGE = range(6, 19)

def generate_behavior_heatmap(folder_path, behavior='feeding'):
    df = load_behavior_data(folder_path)
    if df.empty or behavior not in df.columns:
        return "Keine gültigen Daten gefunden."

    df['date'] = pd.to_datetime(df['t']).dt.date
    df['hour'] = pd.to_datetime(df['t']).dt.hour

    # Gruppieren nach Tag und Stunde
    grouped = df.groupby(['date', 'hour'])[behavior].mean().reset_index()

    # Pivotieren für Heatmap
    pivot = grouped.pivot(index='date', columns='hour', values=behavior)

    fig = px.imshow(
        pivot,
        labels=dict(x="Stunde", y="Datum", color="Ø Verhalten (%)"),
        x=pivot.columns.tolist(),
        y=[str(d) for d in pivot.index],
        color_continuous_scale="OrRd",
        aspect="auto"
    )
    fig.update_layout(
        title=f"Tagesmuster: {behavior} über Stunden",
        xaxis_nticks=24,
        yaxis_autorange="reversed"
    )

    return fig


def generate_behavior_heatmap_for_day(date_str):
    df = load_behavior_data(PKL_FOLDER)
    if df.empty:
        return "Keine Daten vorhanden."

    target_date = pd.to_datetime(date_str).date()
    df = df[df['date'] == target_date]
    if df.empty:
        return f"Keine Daten für {date_str}"

    df = df[df['hour'].isin(HOURS_RANGE)]
    df['dominant_behavior'] = df[BEHAVIORS].idxmax(axis=1)

    grouped = df.groupby(['hour', 'dominant_behavior']).size().reset_index(name='count')
    total_per_hour = grouped.groupby('hour')['count'].transform('sum')
    grouped['percentage'] = (grouped['count'] / total_per_hour * 100).round(1)

    # Pivotieren zu Stunden (x) und Verhalten (y)
    pivot = grouped.pivot(index='dominant_behavior', columns='hour', values='percentage')
    pivot = pivot.reindex(index=[b for b in BEHAVIORS if b in pivot.index])
    
    fig = px.imshow(
        pivot,
        color_continuous_scale='OrRd',
        labels=dict(x="Stunde", y="Verhalten", color="Anteil (%)"),
        text_auto=True,
        aspect="auto"
    )
    fig.update_layout(
        title=f"Aktivitätsbudget als Heatmap ({date_str})",
        xaxis=dict(tickmode='linear'),
        yaxis=dict(autorange="reversed")
    )
    return fig