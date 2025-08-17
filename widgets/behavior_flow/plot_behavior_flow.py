import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from widgets.utils import load_behavior_data

PKL_FOLDER = "data/action_detection/loaded"

def generate_behavior_dfg(folder_path, date=None):
    df = load_behavior_data(folder_path)

    if date:
        df = df[df['date'] == pd.to_datetime(date).date()]
    if df.empty:
        return "Keine Daten geladen.", ""

    df = df.sort_values("t")
    df['next_behavior'] = df['dominant_behavior'].shift(-1)
    transitions = df[df['dominant_behavior'] != df['next_behavior']]

    # Übergänge zählen
    dfg_counts = transitions.groupby(['dominant_behavior', 'next_behavior']).size().reset_index(name='count')

    # Graph erzeugen
    G = nx.DiGraph()
    for _, row in dfg_counts.iterrows():
        G.add_edge(row['dominant_behavior'], row['next_behavior'], weight=row['count'])

    # Positionierung
    pos = nx.spring_layout(G, k=0.7, seed=42)

    # Kanten zeichnen
    edge_x = []
    edge_y = []
    for src, tgt in G.edges():
        x0, y0 = pos[src]
        x1, y1 = pos[tgt]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo='none',
        mode='lines'
    )

    # Knoten zeichnen
    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        in_deg = G.in_degree(node, weight='weight')
        out_deg = G.out_degree(node, weight='weight')
        node_text.append(f"{node}\nIn: {in_deg}, Out: {out_deg}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[n for n in G.nodes()],
        textposition="bottom center",
        hovertext=node_text,
        marker=dict(
            showscale=True,
            colorscale='Blues',
            color=[G.in_degree(n, weight='weight') for n in G.nodes()],
            size=30,
            colorbar=dict(thickness=10, title='Eingehende Pfade')
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Directly-Follows-Graph (Verhaltenspfade)",
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        ))

    # Analysebericht generieren
    top_transition = dfg_counts.sort_values('count', ascending=False).iloc[0]
    most_common_path = f"• Häufigste Sequenz: {top_transition['dominant_behavior']} → {top_transition['next_behavior']} ({top_transition['count']}x)"

    in_deg_all = dict(G.in_degree(weight='weight'))
    out_deg_all = dict(G.out_degree(weight='weight'))
    central_node = max(in_deg_all, key=in_deg_all.get)
    active_node = max(out_deg_all, key=out_deg_all.get)

    report_lines = [
        f"Verhaltenstransitions am {date}:",
        most_common_path,
        f"• Zentrales Verhalten (meiste eingehende Übergänge): {central_node} ({in_deg_all[central_node]}x)",
        f"• Aktivstes Startverhalten (ausgehend): {active_node} ({out_deg_all[active_node]}x)"
    ]

    # Seltene oder isolierte Verhalten
    low_degree = [n for n in G.nodes() if in_deg_all[n] + out_deg_all[n] <= 2]
    if low_degree:
        report_lines.append(f"• Seltene oder isolierte Verhalten: {', '.join(low_degree)}")

    report = "\n".join(report_lines)
    return fig, report
