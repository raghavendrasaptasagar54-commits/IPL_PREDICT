"""
IPL Win Predictor - Prediction Engine & Ground Simulation Service
Handles feature derivation, probability inference, boundary checks,
commentary generation, and live match simulation.
"""

import os
import json
import random
import joblib
import numpy as np
import pandas as pd
from data.teams_and_venues import TEAMS, VENUES

class IPLPredictor:
    def __init__(self, model_path=None, metadata_path=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = model_path or os.path.join(base_dir, "models", "ipl_win_predictor.joblib")
        self.metadata_path = metadata_path or os.path.join(base_dir, "models", "model_metadata.json")
        self.model = None
        self.metadata = {}
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, "r") as f:
                self.metadata = json.load(f)

    def is_ready(self):
        return self.model is not None

    def calculate_metrics(self, data):
        """Derives all modern cricket telemetry features from ground input."""
        target_runs = int(data.get("target_runs", 180))
        current_score = int(data.get("current_score", 0))
        overs_bowled = float(data.get("overs_bowled", 0.0))
        wickets_lost = int(data.get("wickets_lost", 0))
        runs_last_5_overs = int(data.get("runs_last_5_overs", 35))
        wickets_last_5_overs = int(data.get("wickets_last_5_overs", 1))
        batting_team = data.get("batting_team", "Chennai Super Kings")
        bowling_team = data.get("bowling_team", "Mumbai Indians")
        venue = data.get("venue", "Wankhede Stadium, Mumbai")
        dew_present = int(data.get("dew_present", 1 if "Wankhede" in venue else 0))

        # Convert overs (e.g. 10.4 -> 10*6 + 4 = 64 balls)
        full_overs = int(overs_bowled)
        partial_balls = int(round((overs_bowled - full_overs) * 10))
        balls_bowled = min(120, full_overs * 6 + partial_balls)
        balls_left = max(0, 120 - balls_bowled)

        runs_left = max(0, target_runs - current_score)
        wickets_in_hand = max(0, 10 - wickets_lost)

        # CRR & RRR
        completed_overs_float = max(0.1, balls_bowled / 6.0)
        crr = current_score / completed_overs_float

        overs_left_float = max(0.1, balls_left / 6.0)
        rrr = runs_left / overs_left_float if balls_left > 0 else (0.0 if runs_left == 0 else 999.0)

        rr_diff = rrr - crr
        pressure_index = (rrr * (11 - wickets_in_hand)) / max(1.0, overs_left_float)

        venue_info = VENUES.get(venue, {
            "avg_1st_innings": 172,
            "chasing_win_pct": 52.0
        })

        venue_avg = venue_info["avg_1st_innings"]
        venue_chasing_win_pct = venue_info["chasing_win_pct"]

        wickets_ratio = wickets_in_hand / 10.0
        balls_ratio = balls_left / 120.0
        target_difficulty = target_runs / max(100.0, venue_avg)
        recent_momentum_swing = (runs_last_5_overs / 5.0) - crr

        features_dict = {
            "batting_team": batting_team,
            "bowling_team": bowling_team,
            "venue": venue,
            "target_runs": target_runs,
            "current_score": current_score,
            "balls_left": balls_left,
            "wickets_in_hand": wickets_in_hand,
            "runs_left": runs_left,
            "crr": round(crr, 2),
            "rrr": round(rrr, 2),
            "rr_diff": round(rr_diff, 2),
            "pressure_index": round(pressure_index, 2),
            "runs_last_5_overs": runs_last_5_overs,
            "wickets_last_5_overs": wickets_last_5_overs,
            "dew_present": dew_present,
            "venue_avg_1st_innings": venue_avg,
            "venue_chasing_win_pct": venue_chasing_win_pct,
            "wickets_ratio": round(wickets_ratio, 2),
            "balls_ratio": round(balls_ratio, 2),
            "target_difficulty": round(target_difficulty, 2),
            "recent_momentum_swing": round(recent_momentum_swing, 2)
        }

        return features_dict, balls_bowled, balls_left, runs_left, wickets_in_hand

    def predict(self, input_data):
        """
        Executes live inference with cricket physical boundaries and returns
        comprehensive probabilities and situational metrics.
        """
        features, balls_bowled, balls_left, runs_left, wickets_in_hand = self.calculate_metrics(input_data)

        batting_team = features["batting_team"]
        bowling_team = features["bowling_team"]
        venue = features["venue"]
        target_runs = features["target_runs"]
        current_score = features["current_score"]

        # 1. Deterministic Cricket End Condition Checks
        if current_score >= target_runs:
            batting_win_pct = 100.0
            bowling_win_pct = 0.0
            status_text = f"{batting_team} has achieved the target!"
        elif wickets_in_hand <= 0:
            batting_win_pct = 0.0
            bowling_win_pct = 100.0
            status_text = f"{batting_team} is All Out! {bowling_team} wins!"
        elif balls_left <= 0 and runs_left > 0:
            batting_win_pct = 0.0
            bowling_win_pct = 100.0
            status_text = f"Overs exhausted! {bowling_team} defends successfully!"
        else:
            # Model inference
            df_input = pd.DataFrame([features])
            if self.model is None:
                self.load_model()

            probs = self.model.predict_proba(df_input)[0]
            # probs[0] = Defending (Bowling Team), probs[1] = Chasing (Batting Team)
            bowling_prob = probs[0]
            batting_prob = probs[1]

            # Fine calibration adjustments for real-time responsiveness
            if runs_left <= 6 and balls_left >= 6 and wickets_in_hand >= 4:
                batting_prob = max(batting_prob, 0.94)
                bowling_prob = 1.0 - batting_prob
            elif runs_left > 36 and balls_left <= 12 and wickets_in_hand <= 3:
                bowling_prob = max(bowling_prob, 0.96)
                batting_prob = 1.0 - bowling_prob

            batting_win_pct = round(batting_prob * 100.0, 1)
            bowling_win_pct = round((100.0 - batting_win_pct), 1)

            # Determine match status narrative
            if batting_win_pct >= 75:
                status_text = f"{batting_team} in commanding control of the chase."
            elif batting_win_pct >= 55:
                status_text = f"{batting_team} slightly ahead with required run rate under control."
            elif batting_win_pct >= 45:
                status_text = "Match hanging on a knife's edge! Even contest."
            elif batting_win_pct >= 25:
                status_text = f"{bowling_team} tightening the screws with scoreboard pressure."
            else:
                status_text = f"{bowling_team} in dominant position to defend."

        # Pressure classification
        pi = features["pressure_index"]
        if pi < 6:
            pressure_level = "Low"
            pressure_color = "#10B981"
        elif pi < 12:
            pressure_level = "Moderate"
            pressure_color = "#3B82F6"
        elif pi < 20:
            pressure_level = "High"
            pressure_color = "#F59E0B"
        elif pi < 32:
            pressure_level = "Severe"
            pressure_color = "#EF4444"
        else:
            pressure_level = "Extreme / Critical"
            pressure_color = "#7F1D1D"

        # Key drivers
        drivers = []
        if features["rrr"] > features["crr"] + 2.0:
            drivers.append(f"Steep Required Run Rate ({features['rrr']:.1f} vs Current {features['crr']:.1f})")
        if features["wickets_in_hand"] <= 3:
            drivers.append(f"Tail exposed ({features['wickets_in_hand']} wickets left)")
        elif features["wickets_in_hand"] >= 7:
            drivers.append(f"Deep batting lineup ({features['wickets_in_hand']} wickets in hand)")
        if features["runs_last_5_overs"] >= 50:
            drivers.append(f"Explosive momentum (+{features['runs_last_5_overs']} runs in last 5 overs)")
        elif features["wickets_last_5_overs"] >= 2:
            drivers.append(f"Recent collapse ({features['wickets_last_5_overs']} wickets in last 5 overs)")
        if features["dew_present"]:
            drivers.append("Dew factor favoring chasing side in wet outfield")

        if not drivers:
            drivers.append("Standard match progression")

        batting_info = TEAMS.get(batting_team, {})
        bowling_info = TEAMS.get(bowling_team, {})

        return {
            "batting_team": batting_team,
            "batting_team_short": batting_info.get("short_name", "BAT"),
            "batting_team_color": batting_info.get("primary_color", "#F9CD05"),
            "batting_win_pct": batting_win_pct,
            "bowling_team": bowling_team,
            "bowling_team_short": bowling_info.get("short_name", "BOWL"),
            "bowling_team_color": bowling_info.get("primary_color", "#004BA0"),
            "bowling_win_pct": bowling_win_pct,
            "target_runs": target_runs,
            "current_score": current_score,
            "runs_left": runs_left,
            "balls_bowled": balls_bowled,
            "balls_left": balls_left,
            "wickets_lost": 10 - wickets_in_hand,
            "wickets_in_hand": wickets_in_hand,
            "crr": features["crr"],
            "rrr": features["rrr"],
            "rr_diff": features["rr_diff"],
            "pressure_index": features["pressure_index"],
            "pressure_level": pressure_level,
            "pressure_color": pressure_color,
            "status_text": status_text,
            "key_drivers": drivers,
            "venue": venue,
            "dew_present": bool(features["dew_present"])
        }

    def simulate_next_delivery(self, current_state):
        """
        Simulates an individual live ground ball event with dynamic cricket physics
        and returns updated telemetry and live commentary.
        """
        balls_bowled = current_state.get("balls_bowled", 0)
        current_score = current_state.get("current_score", 0)
        wickets_lost = current_state.get("wickets_lost", 0)
        target_runs = current_state.get("target_runs", 180)
        batting_team = current_state.get("batting_team", "Chennai Super Kings")
        bowling_team = current_state.get("bowling_team", "Mumbai Indians")
        venue = current_state.get("venue", "Wankhede Stadium, Mumbai")
        dew_present = current_state.get("dew_present", 1)
        recent_balls_runs = list(current_state.get("recent_balls_runs", []))
        recent_balls_wickets = list(current_state.get("recent_balls_wickets", []))

        # Check if already ended
        if current_score >= target_runs or wickets_lost >= 10 or balls_bowled >= 120:
            return {"match_over": True, "state": current_state}

        ball_number = balls_bowled + 1
        balls_left = 120 - ball_number
        runs_left = max(0, target_runs - current_score)

        # Dynamic live probabilities based on phase and match pressure
        req_rate = (runs_left / (max(1, balls_left) / 6.0)) if balls_left > 0 else 12.0
        wickets_in_hand = 10 - wickets_lost

        if ball_number <= 36:
            # Powerplay
            w_prob = 0.04
            dot_prob = 0.38
            single_prob = 0.30
            two_prob = 0.08
            four_prob = 0.14
            six_prob = 0.06
        elif ball_number <= 90:
            # Middle overs
            w_prob = 0.045
            dot_prob = 0.30
            single_prob = 0.45
            two_prob = 0.10
            four_prob = 0.08
            six_prob = 0.03
        else:
            # Death overs - higher risk taking
            pressure_boost = min(0.06, max(0.0, (req_rate - 9.0) * 0.012))
            w_prob = 0.075 + pressure_boost
            dot_prob = 0.25
            single_prob = 0.28
            two_prob = 0.08
            four_prob = 0.18
            six_prob = 0.14

        # Roll the dice
        rand = random.random()
        event = "0"
        runs_this_ball = 0
        is_wicket = False

        if rand < w_prob:
            is_wicket = True
            runs_this_ball = 0
            event = "W"
            wickets_lost += 1
        else:
            rand_runs = random.random()
            if rand_runs < dot_prob:
                runs_this_ball = 0
                event = "0"
            elif rand_runs < dot_prob + single_prob:
                runs_this_ball = 1
                event = "1"
            elif rand_runs < dot_prob + single_prob + two_prob:
                runs_this_ball = 2
                event = "2"
            elif rand_runs < dot_prob + single_prob + two_prob + four_prob:
                runs_this_ball = 4
                event = "4"
            else:
                runs_this_ball = 6
                event = "6"

        current_score += runs_this_ball
        recent_balls_runs.append(runs_this_ball)
        recent_balls_wickets.append(1 if is_wicket else 0)
        if len(recent_balls_runs) > 30:
            recent_balls_runs.pop(0)
            recent_balls_wickets.pop(0)

        over_num = ball_number // 6
        ball_in_over = ball_number % 6
        if ball_in_over == 0:
            over_display = f"{over_num - 1}.6"
        else:
            over_display = f"{over_num}.{ball_in_over}"

        # Generate live realistic commentary
        commentary = self.generate_commentary(
            event, over_display, batting_team, bowling_team,
            runs_this_ball, is_wicket, runs_left - runs_this_ball, balls_left
        )

        updated_state = {
            "balls_bowled": ball_number,
            "overs_bowled": over_num + (ball_in_over / 10.0),
            "current_score": current_score,
            "wickets_lost": wickets_lost,
            "target_runs": target_runs,
            "batting_team": batting_team,
            "bowling_team": bowling_team,
            "venue": venue,
            "dew_present": dew_present,
            "runs_last_5_overs": sum(recent_balls_runs),
            "wickets_last_5_overs": sum(recent_balls_wickets),
            "recent_balls_runs": recent_balls_runs,
            "recent_balls_wickets": recent_balls_wickets,
            "last_ball_event": event,
            "last_ball_commentary": commentary,
            "over_display": over_display
        }

        # Predict with new state
        prediction = self.predict(updated_state)
        prediction["last_ball_event"] = event
        prediction["last_ball_commentary"] = commentary
        prediction["over_display"] = over_display
        prediction["recent_balls_runs"] = recent_balls_runs
        prediction["recent_balls_wickets"] = recent_balls_wickets
        prediction["match_over"] = (current_score >= target_runs or wickets_lost >= 10 or ball_number >= 120)

        return prediction

    def generate_commentary(self, event, over_str, bat_team, bowl_team, runs, is_wkt, runs_needed, balls_left):
        """Generates TV-broadcast style commentary for each live delivery."""
        if is_wkt:
            phrases = [
                f"OUT! Cleaned him up! A massive breakthrough for {bowl_team} in over {over_str}!",
                f"WICKET! Timber disturbed! The bowling team strikes with pinpoint precision!",
                f"IN THE AIR AND TAKEN! Superb catch at deep mid-wicket! Huge moment in the game!",
                f"EDGED AND GONE! The keeper makes no mistake, pressure builds exponentially on {bat_team}!"
            ]
            return random.choice(phrases)
        elif event == "6":
            phrases = [
                f"SIX! That is towering! Clears long-on and lands way into the top tier!",
                f"MAXIMUM! Crushed over deep mid-wicket with thunderous authority!",
                f"SIX RUNS! Picked up effortlessly off the pads and dispatched into the crowd!",
                f"WHAT A SHOT! High, handsome and all the way for a sensational six!"
            ]
            return random.choice(phrases)
        elif event == "4":
            phrases = [
                f"FOUR! Slashed through the covers! Ball races like a tracer bullet to the fence!",
                f"CRACKING FOUR! Finds the gap between backward point and third man with elegance!",
                f"BOUNDARY! Driven down the ground past the umpire, no stopping that!",
                f"FOUR MORE! Pulled firmly through mid-wicket, easing required run rate pressure!"
            ]
            return random.choice(phrases)
        elif event == "2":
            return f"Tucked into the gap at deep square leg, rapid running between wickets converts one into two."
        elif event == "1":
            return f"Pushed gently toward mid-on for a brisk single. Strike rotated."
        else:
            phrases = [
                f"Dot ball! Beaten outside off-stump with seam movement. Excellent bowling.",
                f"Good length delivery, defended solidly back to the bowler. Dot ball.",
                f"Swing and a miss! Through to the wicketkeeper, pressure ratchets up!"
            ]
            return random.choice(phrases)

    def simulate_full_match(self, match_setup):
        """
        Simulates an entire live ground match trajectory from ball 1 to the end,
        recording ball-by-ball win probabilities, worm metrics, and key turning points.
        """
        batting_team = match_setup.get("batting_team", "Chennai Super Kings")
        bowling_team = match_setup.get("bowling_team", "Mumbai Indians")
        venue = match_setup.get("venue", "Wankhede Stadium, Mumbai")
        target_runs = int(match_setup.get("target_runs", 182))
        dew_present = int(match_setup.get("dew_present", 1))

        state = {
            "balls_bowled": 0,
            "current_score": 0,
            "wickets_lost": 0,
            "target_runs": target_runs,
            "batting_team": batting_team,
            "bowling_team": bowling_team,
            "venue": venue,
            "dew_present": dew_present,
            "recent_balls_runs": [],
            "recent_balls_wickets": []
        }

        timeline = []
        # Initial pre-innings prediction
        init_pred = self.predict({
            "batting_team": batting_team,
            "bowling_team": bowling_team,
            "venue": venue,
            "target_runs": target_runs,
            "current_score": 0,
            "overs_bowled": 0.0,
            "wickets_lost": 0,
            "runs_last_5_overs": 0,
            "wickets_last_5_overs": 0,
            "dew_present": dew_present
        })
        timeline.append({
            "ball": 0,
            "over_display": "0.0",
            "score": 0,
            "wickets": 0,
            "runs_this_ball": 0,
            "event": "START",
            "batting_win_pct": init_pred["batting_win_pct"],
            "bowling_win_pct": init_pred["bowling_win_pct"],
            "crr": 0.0,
            "rrr": round(target_runs / 20.0, 2),
            "commentary": f"Match commencing at {venue}. {batting_team} needs {target_runs} runs to claim victory."
        })

        prev_bat_prob = init_pred["batting_win_pct"]

        while not state.get("match_over", False) and state["balls_bowled"] < 120:
            step_result = self.simulate_next_delivery(state)
            if step_result.get("match_over") and "state" in step_result:
                break

            swing = round(step_result["batting_win_pct"] - prev_bat_prob, 1)
            prev_bat_prob = step_result["batting_win_pct"]

            timeline.append({
                "ball": step_result["balls_bowled"],
                "over_display": step_result["over_display"],
                "score": step_result["current_score"],
                "wickets": step_result["wickets_lost"],
                "runs_this_ball": step_result.get("runs_this_ball", 0),
                "event": step_result["last_ball_event"],
                "batting_win_pct": step_result["batting_win_pct"],
                "bowling_win_pct": step_result["bowling_win_pct"],
                "crr": step_result["crr"],
                "rrr": step_result["rrr"],
                "swing": swing,
                "commentary": step_result["last_ball_commentary"]
            })

            # Update state for next ball
            state["balls_bowled"] = step_result["balls_bowled"]
            state["current_score"] = step_result["current_score"]
            state["wickets_lost"] = step_result["wickets_lost"]
            state["recent_balls_runs"] = step_result.get("recent_balls_runs", [])
            state["recent_balls_wickets"] = step_result.get("recent_balls_wickets", [])

            if step_result.get("match_over"):
                break

        final_score = state["current_score"]
        final_wickets = state["wickets_lost"]
        winner = batting_team if final_score >= target_runs else bowling_team

        return {
            "batting_team": batting_team,
            "bowling_team": bowling_team,
            "venue": venue,
            "target_runs": target_runs,
            "winner": winner,
            "final_score": f"{final_score}/{final_wickets} in {timeline[-1]['over_display']} ov",
            "total_balls": len(timeline) - 1,
            "timeline": timeline
        }

