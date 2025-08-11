import pandas as pd
import numpy as np
import glob
import os
from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py

# Pfade
PKL_FOLDER = "data/action_detection/loaded"
NPZ_FOLDER = "data/tracking/processed"
XES_PATH = "data/clustered_log_10s.xes"

BEHAVIORS = ['lying', 'feeding', 'investigating', 'defecating',
             'standing', 'sitting', 'moving', 'playing']

def load_pkl_data(folder):
    dfs = []
    for f in sorted(glob.glob(os.path.join(folder, "*.pkl"))):
        try:
            df = pd.read_pickle(f)
            if 't' in df.columns:
                df['t'] = pd.to_datetime(df['t'])
                df['hour'] = df['t'].dt.hour
                df['date'] = df['t'].dt.date
            if all(c in df.columns for c in ['x1', 'x2', 'y1', 'y2']):
                df['x_center'] = (df['x1'] + df['x2']) / 2
                df['y_center'] = (df['y1'] + df['y2']) / 2
            available = [b for b in BEHAVIORS if b in df.columns]
            if available:
                df['dominant_behavior'] = df[available].idxmax(axis=1)
            dfs.append(df)
        except:
            continue
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def load_npz_data(folder):
    npz_files = sorted(glob.glob(os.path.join(folder, "*.npz")))
    data_list = []
    for f in npz_files:
        try:
            npz = np.load(f, allow_pickle=True)
            flat = {key: npz[key] for key in npz.files}
            flat['source_file'] = os.path.basename(f)
            df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in flat.items()]))
            data_list.append(df)
        except:
            continue
    return pd.concat(data_list, ignore_index=True) if data_list else pd.DataFrame()

def load_xes(path):
    try:
        log = xes_importer.apply(path)
        return pm4py.convert_to_dataframe(log)
    except:
        return pd.DataFrame()

df_pkl = load_pkl_data(PKL_FOLDER)
df_npz = load_npz_data(NPZ_FOLDER)
df_xes = load_xes(XES_PATH)

print("\n📦 PKL-Dateien Vorschau:")
print(df_pkl.head(20))

print("\n📦 NPZ-Dateien Vorschau:")
print(df_npz.head(20))

print("\n📦 XES-Datei Vorschau:")
print(df_xes.head(20))
