"""
IPL Win Predictor - Machine Learning Model Training Pipeline
Incorporates modern cricket telemetry, feature engineering, probability calibration,
and ensemble techniques.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, roc_auc_score, brier_score_loss, log_loss

from data.generate_dataset import save_default_dataset

def engineer_features(df):
    """
    Computes modern cricket metrics: pressure index, run-rate differentials,
    wickets-to-balls ratios, and momentum factors.
    """
    df = df.copy()

    # Boundary protection and clean calculations
    df['runs_left'] = np.maximum(0, df['target_runs'] - df['current_score'])
    df['balls_left'] = np.clip(df['balls_left'], 0, 120)
    df['wickets_in_hand'] = np.clip(df['wickets_in_hand'], 0, 10)

    # Current and Required Run Rates
    overs_completed = np.maximum(0.1, (120 - df['balls_left']) / 6.0)
    df['crr'] = df['current_score'] / overs_completed
    overs_left = np.maximum(0.1, df['balls_left'] / 6.0)
    df['rrr'] = df['runs_left'] / overs_left

    # Modern Derived Metrics
    df['rr_diff'] = df['rrr'] - df['crr']
    df['pressure_index'] = (df['rrr'] * (11 - df['wickets_in_hand'])) / np.maximum(1.0, overs_left)
    df['wickets_ratio'] = df['wickets_in_hand'] / 10.0
    df['balls_ratio'] = df['balls_left'] / 120.0
    df['target_difficulty'] = df['target_runs'] / np.maximum(100.0, df['venue_avg_1st_innings'])

    # Momentum in last 5 overs
    df['recent_crr'] = df['runs_last_5_overs'] / 5.0
    df['recent_momentum_swing'] = df['recent_crr'] - df['crr']

    return df

def train_and_evaluate():
    data_path = os.path.join(os.path.dirname(__file__), "data", "ipl_live_ground_dataset.csv")
    if not os.path.exists(data_path):
        print("Dataset not found. Generating fresh ground dataset...")
        df_raw = save_default_dataset(data_path)
    else:
        print(f"Loading existing dataset from {data_path}...")
        df_raw = pd.read_csv(data_path)

    print("Engineering modern cricket features...")
    df = engineer_features(df_raw)

    categorical_features = ['batting_team', 'bowling_team', 'venue']
    numerical_features = [
        'target_runs', 'current_score', 'balls_left', 'wickets_in_hand',
        'runs_left', 'crr', 'rrr', 'rr_diff', 'pressure_index',
        'runs_last_5_overs', 'wickets_last_5_overs', 'dew_present',
        'venue_avg_1st_innings', 'venue_chasing_win_pct',
        'wickets_ratio', 'balls_ratio', 'target_difficulty', 'recent_momentum_swing'
    ]

    X = df[categorical_features + numerical_features]
    y = df['winner'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train)} samples | Testing set: {len(X_test)} samples")

    # Column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ],
        remainder='drop'
    )

    # Base Models
    print("Fitting candidate machine learning models...")
    rf_base = RandomForestClassifier(n_estimators=100, max_depth=12, min_samples_split=10, random_state=42, n_jobs=-1)
    hgb_base = HistGradientBoostingClassifier(max_iter=120, max_depth=8, learning_rate=0.08, random_state=42)
    lr_base = LogisticRegression(max_iter=1000, C=1.0, random_state=42)

    # Ensemble with Soft Voting
    voting_clf = VotingClassifier(
        estimators=[
            ('rf', rf_base),
            ('hgb', hgb_base),
            ('lr', lr_base)
        ],
        voting='soft'
    )

    # Pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', voting_clf)
    ])

    print("Training modern ensemble pipeline...")
    pipeline.fit(X_train, y_train)

    # Predictions & Calibration Evaluation
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    auc = float(roc_auc_score(y_test, y_prob))
    brier = float(brier_score_loss(y_test, y_prob))
    logloss = float(log_loss(y_test, y_prob))

    print("\n--- MODEL EVALUATION METRICS ---")
    print(f"Accuracy:    {acc * 100:.2f}%")
    print(f"ROC-AUC:     {auc:.4f}")
    print(f"Brier Score: {brier:.4f} (Lower is better, ideal < 0.15)")
    print(f"Log Loss:    {logloss:.4f}")
    print("--------------------------------\n")

    # Model persistence
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    model_file = os.path.join(models_dir, "ipl_win_predictor.joblib")
    joblib.dump(pipeline, model_file)
    print(f"Model saved successfully to {model_file}")

    # Metadata persistence
    metadata = {
        "model_type": "Modern Soft-Voting Ensemble (Random Forest + HistGradientBoosting + Logistic Regression)",
        "accuracy": round(acc * 100, 2),
        "roc_auc": round(auc, 4),
        "brier_score": round(brier, 4),
        "log_loss": round(logloss, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "categorical_features": categorical_features,
        "numerical_features": numerical_features,
        "classes": ["Bowling Team Win (Target Defended)", "Batting Team Win (Target Chased)"]
    }
    metadata_file = os.path.join(models_dir, "model_metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)
    print(f"Metadata saved to {metadata_file}")

    return pipeline, metadata

if __name__ == "__main__":
    train_and_evaluate()

