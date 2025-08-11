import matplotlib.pyplot as plt
import io, base64
import pandas as pd
import matplotlib

matplotlib.use("Agg")

def generate_behavior_bar_plot(xes_path, behavior, thresholds):
    from pm4py.objects.log.importer.xes import importer as xes_importer
    import pm4py

    log = xes_importer.apply(xes_path)
    df = pm4py.convert_to_dataframe(log)
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
    df['duration_timedelta'] = pd.to_timedelta(df['duration'])
    df['date'] = df['time:timestamp'].dt.date

    df = df[df['concept:name'] == behavior]
    if df.empty:
        return f"Keine Daten für {behavior}"

    daily_duration = df.groupby('date')['duration_timedelta'].sum()
    daily_minutes = daily_duration.dt.total_seconds() / 60
    t = thresholds[behavior]

    def colorize(v):
        if v < t["red_min"] or v > t["red_max"]:
            return "red"
        elif v < t["yellow_min"] or v > t["yellow_max"]:
            return "orange"
        return "green"

    colors = daily_minutes.apply(colorize)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(daily_minutes.index, daily_minutes.values, color=colors)
    ax.axhline(t["mean"], linestyle='-', color='black')
    ax.axhline(t["yellow_min"], linestyle='--', color='gray')
    ax.axhline(t["yellow_max"], linestyle='--', color='gray')
    ax.axhline(t["red_min"], linestyle=':', color='gray')
    ax.axhline(t["red_max"], linestyle=':', color='gray')
    ax.set_title(f"{behavior} pro Tag")
    ax.set_ylabel("Minuten")

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"
