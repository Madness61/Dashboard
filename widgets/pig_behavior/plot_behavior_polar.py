import pandas as pd
import plotly.express as px
from widgets.utils import load_behavior_data, BEHAVIORS

def generate_polar_figure(df, hour, title_prefix="Aktivitätsverteilung", scale="linear"):
    hour_df = df[df['hour'] == hour]

    if hour_df.empty:
        return px.bar_polar(title=f"{title_prefix} um {hour}:00 Uhr – keine Daten")

    behavior_counts = hour_df['dominant_behavior'].value_counts().reindex(BEHAVIORS, fill_value=0).reset_index()
    behavior_counts.columns = ['behavior', 'count']
    behavior_counts['percentage'] = (behavior_counts['count'] / behavior_counts['count'].sum() * 100).round(1)
    behavior_counts['tooltip'] = behavior_counts.apply(
        lambda row: f"{row['behavior']}: {row['count']} ({row['percentage']}%)", axis=1
    )

    fig = px.bar_polar(
        behavior_counts,
        r="count",
        theta="behavior",
        color="count",
        hover_name="tooltip",
        template="plotly_white",
        color_continuous_scale=px.colors.sequential.Plasma,
        category_orders={"behavior": BEHAVIORS},
        log_r=(scale == "logarithmic"),
        title=f"{title_prefix} um {hour}:00 Uhr"
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(showticklabels=False, ticks='')
        )
    )
    return fig


def generate_two_polar_charts(hour, date, scale="linear"):
    df = load_behavior_data("data/action_detection/loaded")  # Pfad wird übergeben

    if df.empty:
        return (
            px.bar_polar(title="Keine Daten für aggregierten Plot"),
            px.bar_polar(title="Keine Daten für Tagesplot")
        )

    fig_all = generate_polar_figure(df, hour, title_prefix="Aggregierte Verteilung", scale=scale)

    try:
        day = pd.to_datetime(date).date()
        df_day = df[df['date'] == day]
    except Exception:
        df_day = pd.DataFrame()

    fig_day = generate_polar_figure(df_day, hour, title_prefix=f"Verteilung am {date}", scale=scale)

    return fig_all, fig_day
