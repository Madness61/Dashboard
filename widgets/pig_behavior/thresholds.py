def get_behavior_thresholds(xes_path, behaviors):
    from pm4py.objects.log.importer.xes import importer as xes_importer
    import pm4py
    import pandas as pd

    log = xes_importer.apply(xes_path)
    df = pm4py.convert_to_dataframe(log)
    df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
    df['duration_timedelta'] = pd.to_timedelta(df['duration'])
    df['date'] = df['time:timestamp'].dt.date

    thresholds = {}
    for b in behaviors:
        sub = df[df['concept:name'] == b]
        if sub.empty:
            continue
        daily = sub.groupby('date')['duration_timedelta'].sum()
        minutes = daily.dt.total_seconds() / 60
        mean = minutes.mean()
        thresholds[b] = {
            "mean": mean,
            "yellow_min": mean * 0.9,
            "yellow_max": mean * 1.1,
            "red_min": mean * 0.8,
            "red_max": mean * 1.2
        }
    return thresholds
