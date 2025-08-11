import pandas as pd
import glob
import os

# Globale Definition der Verhaltensspalten
BEHAVIORS = ['lying', 'sitting', 'standing', 'moving',
             'investigating', 'feeding', 'defecating', 'playing']

def load_behavior_data(folder_path, exclude=None):
    file_list = sorted(glob.glob(os.path.join(folder_path, "*.pkl")))
    if not file_list:
        return pd.DataFrame()

    dfs = []
    for file in file_list:
        df = pd.read_pickle(file)

        # sicherstellen, dass Zeitspalte existiert
        if 't' not in df.columns:
            continue

        df['t'] = pd.to_datetime(df['t'])
        dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs)

    # Spalten berechnen
    df['hour'] = df['t'].dt.hour
    df['date'] = df['t'].dt.date

    # dominantes Verhalten
    df['dominant_behavior'] = df[BEHAVIORS].idxmax(axis=1)

    # Mittelpunktberechnung
    df['x_center'] = (df['x1'] + df['x2']) / 2
    df['y_center'] = (df['y1'] + df['y2']) / 2

    # Verhalten ausschließen
    if exclude:
        df = df[~df['dominant_behavior'].isin(exclude)]

    return df


def get_available_behaviors(xes_path, exclude=None):
    from pm4py.objects.log.importer.xes import importer as xes_importer
    import pm4py

    log = xes_importer.apply(xes_path)
    df = pm4py.convert_to_dataframe(log)
    behaviors = sorted(df['concept:name'].unique())
    if exclude:
        behaviors = [b for b in behaviors if b not in exclude]
    return behaviors
