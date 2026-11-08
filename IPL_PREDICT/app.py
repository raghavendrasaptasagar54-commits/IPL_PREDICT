"""
IPL Winning Team Prediction System - Web Application Entrypoint
Run this file directly via: python app.py
Automatically initializes ML models, launches local web server, and opens UI.
"""

import os
import sys
import threading
import webbrowser
import socket
from flask import Flask, render_template, request, jsonify

from data.teams_and_venues import TEAMS, VENUES
from predictor import IPLPredictor

# Ensure current working directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Initialize Flask application
app = Flask(__name__, template_folder="templates", static_folder="static")

# Initialize Machine Learning Engine
predictor = IPLPredictor()

def ensure_model_trained():
    """Checks if the trained ML model exists; if not, triggers training routine."""
    model_path = os.path.join(CURRENT_DIR, "models", "ipl_win_predictor.joblib")
    if not os.path.exists(model_path):
        print("\n[!] Trained model not detected. Initializing data generation and training pipeline...")
        from train_model import train_and_evaluate
        train_and_evaluate()
        predictor.load_model()
        print("[✓] Model pipeline initialized successfully.\n")
    else:
        print("[✓] Pre-trained Machine Learning Model loaded and ready.")

ensure_model_trained()

def find_free_port(starting_port=5000):
    """Finds an available local port starting from the given port."""
    port = starting_port
    while port < starting_port + 20:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
            port += 1
    return starting_port

@app.route("/")
def index():
    """Serves the main interactive dashboard."""
    return render_template(
        "index.html",
        teams=TEAMS,
        venues=VENUES,
        metadata=predictor.metadata
    )

@app.route("/api/teams-venues", methods=["GET"])
def get_teams_and_venues():
    """Returns team and venue configurations."""
    return jsonify({
        "teams": TEAMS,
        "venues": VENUES
    })

@app.route("/api/predict", methods=["POST"])
def predict_live():
    """Computes real-time win probability and match pressure telemetry."""
    try:
        data = request.get_json(force=True)
        result = predictor.predict(data)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/simulate-next-ball", methods=["POST"])
def simulate_ball():
    """Simulates a single ball with live ground physics and TV commentary."""
    try:
        data = request.get_json(force=True)
        result = predictor.simulate_next_delivery(data)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/simulate-full-match", methods=["POST"])
def simulate_match():
    """Simulates an entire 2nd innings chase ball-by-ball for live animated replay."""
    try:
        data = request.get_json(force=True)
        result = predictor.simulate_full_match(data)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/model-stats", methods=["GET"])
def get_model_stats():
    """Returns AI model architecture and performance evaluation metrics."""
    return jsonify({
        "success": True,
        "metadata": predictor.metadata
    })

def open_browser(url):
    """Opens browser automatically after short delay."""
    import time
    time.sleep(1.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass

if __name__ == "__main__":
    port = find_free_port(5000)
    local_url = f"http://127.0.0.1:{port}"
    print("=" * 65)
    print("🏏 IPL WINNING TEAM PREDICTION SYSTEM (ML POWERED)")
    print("=" * 65)
    print(f"Server is starting at: {local_url}")
    print("Trained on live ground datasets with modern cricket telemetry.")
    print("Press CTRL+C to stop the server anytime.")
    print("=" * 65)

    # Launch browser automatically
    threading.Thread(target=open_browser, args=(local_url,), daemon=True).start()

    # Run Flask server
    app.run(host="127.0.0.1", port=port, debug=False)

