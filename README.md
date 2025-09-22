# Dashboard – Verhaltensanalyse

Ein interaktives Dashboard zur Visualisierung von **Aktivitätsbudgets**, **Verhaltens-Tagesmustern** und **Behavior Flows (DFG)** auf Basis von vorverarbeiteten Pickle-Dateien. Ziel ist es, typische Verhaltensmuster (z. B. *lying, feeding, moving, investigating …*) schnell zu verstehen und Prozessbeziehungen sichtbar zu machen.

## Start

1. Daten (`.pkl`) nach `data/action_detection/loaded` legen.
2. App starten:
   ```bash
   python app.py
3. Browser öffnen: http://127.0.0.1:8050/

## Requirements
- dash>=2.11
- dash-bootstrap-components>=1.6
- pandas>=2.0
- numpy>=1.24
- plotly>=5.18
- matplotlib>=3.7
- networkx>=3.1
- scikit-learn>=1.2
- scipy>=1.9
- pm4py>=2.5  # für Process Mining und XES-Logs

## Ordnerstruktur
```
├── app.py                        # Einstiegspunkt der Dash-Anwendung
├── assets/                       # CSS / statische Dateien
├── data/
│   └── action_detection/
│       └── loaded/              # hier liegen die .pkl-Dateien (Eingabedaten)
├── widgets/
│   ├── utils.py                 # Datenladefunktionen, BEHAVIORS-Liste
│   ├── pig_behavior/            # Modul für Verhaltensanalyse
│   ├── behavior_position/       # Modul für Positionen & Zonen
│   ├── activity_budget/         # Modul für Aktivitätsbudget
│   └── behavior_flow/           # Modul für Behavior Flows (DFG)
└── …                            # weitere Dateien

```
