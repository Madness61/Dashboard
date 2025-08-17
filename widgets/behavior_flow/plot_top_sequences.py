import pandas as pd
from collections import Counter

from widgets.utils import load_behavior_data

def get_top_behavior_sequences(folder_path, date=None, n=3, top_k=5):
    df = load_behavior_data(folder_path)
    
    if date:
        df = df[df['date'] == pd.to_datetime(date).date()]
    if df.empty or len(df) < n:
        return "Keine ausreichenden Daten vorhanden."

    # Nur relevante Spalte
    behaviors = df['dominant_behavior'].tolist()

    # Erzeuge n-gramme: z. B. ("feeding", "lying", "feeding")
    sequences = zip(*[behaviors[i:] for i in range(n)])
    sequence_counts = Counter(sequences)

    # Sortiere nach Häufigkeit
    most_common = sequence_counts.most_common(top_k)

    lines = [f"Top-{top_k} {n}-er Verhaltensequenzen am {date}:\n"]
    for i, (seq, count) in enumerate(most_common, 1):
        lines.append(f"{i}. {' → '.join(seq)} ({count}x)")

    return "\n".join(lines)
