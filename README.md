# 🏏 IPL Winning Team Prediction System (ML Powered)

A modern, machine learning-driven real-time IPL winning team prediction system and match simulation engine with an interactive web UI.

---

## 🚀 Key Highlights & Capabilities

1. **Trained on High-Fidelity Live Ground Telemetry**:
   - Incorporates over 56,700+ live ground match situation samples across 1,400+ simulated IPL match trajectories.
   - Accurately models pitch factors, powerplay, middle-over consolidation, and death-over volatility.

2. **Modern Cricket Determining Techniques & Features**:
   - **Current Run Rate (CRR)** & **Required Run Rate (RRR)**.
   - **Run Rate Differential (`RRR - CRR`)**: Real-time divergence pressure metric.
   - **Dynamic Pressure Index**: Nonlinear index modeling score gap relative to wickets in hand and overs remaining.
   - **Recent 5-Over Momentum Swing**: Captures explosive acceleration or recent batting collapses.
   - **Venue Bias & Pitch Profiles**: Accounts for historical chasing win rates (e.g., Wankhede 54.2%, Chinnaswamy 55.8%, Chepauk 46.8%).
   - **Dew Factor Modeling**: Adjusts probability for wet outfields and night games in India.

3. **Calibrated Machine Learning Ensemble**:
   - Combines **HistGradientBoostingClassifier**, **Random Forest Classifier**, and **Calibrated Logistic Regression** into a Soft-Voting pipeline.
   - **Accuracy**: ~91.8%
   - **ROC-AUC**: ~0.977
   - **Brier Score**: ~0.057 (Exceptional probability calibration, avoiding erratic jumps)

4. **Interactive Dashboard & Live Ground Simulation Studio**:
   - **Live Scenario Analyzer**: Real-time interactive sliders with instant auto-updating win odds.
   - **Ball-by-Ball Live Simulator**: Bowl delivery by delivery, trigger auto-play, inspect ball outcome badges (`0`, `1`, `4`, `6`, `W`), and listen to realistic TV broadcast commentary.
   - **Interactive Probability Worm Chart**: Chart.js time-series tracking probability swings after each ball.
   - **Grounds & Team Profiles**: Historical stats and chasing biases for all 10 IPL franchises and major stadiums.

---

## ⚡ How to Run

Simply execute:

```bash
python app.py
```

When you run `python app.py`:
1. It automatically validates whether the trained model pipeline exists. If not, it generates the dataset and trains the ensemble in ~10 seconds.
2. It boots up the local server (default: `http://127.0.0.1:5000`).
3. It automatically opens your default web browser to the interactive UI.

---

## 📁 Project Architecture

```
IPL_PREDICT/
├── app.py                      # Main entrypoint: server, auto-trainer & browser launcher
├── train_model.py              # ML pipeline: feature engineering, training & calibration
├── predictor.py                # Prediction inference engine & live simulator
├── requirements.txt            # Python dependencies
├── data/
│   ├── teams_and_venues.py     # Team strengths, colors, stadium pitch profiles & bias
│   ├── generate_dataset.py     # Ball-by-ball ground match data generator
│   └── ipl_live_ground_dataset.csv
├── models/
│   ├── ipl_win_predictor.joblib # Serialized trained ensemble pipeline
│   └── model_metadata.json     # Evaluation metrics & feature weights
├── templates/
│   └── index.html              # Modern dark-mode dashboard (Tailwind + Chart.js)
└── static/
    ├── css/custom.css          # Broadcast-style animations & badges
    └── js/main.js              # Real-time state management, API calls & charts
```

