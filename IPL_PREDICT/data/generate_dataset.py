"""
IPL Ball-by-Ball Match Telemetry and Live Dataset Generator
Simulates comprehensive ball-by-ball match progressions based on real IPL ground statistics,
team strengths, venue biases, and modern pressure metrics.
"""

import os
import random
import numpy as np
import pandas as pd
from data.teams_and_venues import TEAMS, VENUES

def generate_realistic_match_dataset(num_matches=1200, random_seed=42):
    """
    Generates a high-fidelity dataset of second-innings match situations
    derived from realistic ball-by-ball ground simulations.
    """
    np.random.seed(random_seed)
    random.seed(random_seed)

    team_names = list(TEAMS.keys())
    venue_names = list(VENUES.keys())

    dataset_rows = []

    print(f"Generating realistic IPL match telemetry dataset from {num_matches} matches...")

    for match_id in range(1, num_matches + 1):
        # Pick 2 distinct teams
        team1, team2 = random.sample(team_names, 2)
        # Random toss and innings choice
        batting_team = team1
        bowling_team = team2
        venue = random.choice(venue_names)

        venue_info = VENUES[venue]
        batting_info = TEAMS[batting_team]
        bowling_info = TEAMS[bowling_team]

        # 1st Innings Target generation based on venue average and team strengths
        base_avg = venue_info["avg_1st_innings"]
        bat_factor = (bowling_info["batting_rating"] - 85) * 1.5
        bowl_factor = (batting_info["bowling_rating"] - 85) * 1.2
        target_mean = base_avg + bat_factor - bowl_factor
        target_runs = int(np.clip(np.random.normal(target_mean, 18), 125, 245))

        dew_present = 1 if (venue_info["dew_intensity"] == "High" and random.random() < 0.75) else (1 if random.random() < 0.35 else 0)

        # Simulate 2nd Innings Ball-by-Ball
        current_score = 0
        wickets_lost = 0
        balls_bowled = 0
        recent_balls_runs = [] # Keep track of last 30 balls (5 overs)
        recent_balls_wickets = []

        # Ground pitch impact
        pitch_spin_bias = venue_info["pace_vs_spin_wickets_pct"][1] / 100.0

        match_snapshots = []
        match_finished = False
        winner = None

        # Outcomes: 0, 1, 2, 3, 4, 6, Wicket, Extra
        for ball in range(1, 121):
            balls_bowled = ball
            balls_left = 120 - balls_bowled
            runs_left = max(0, target_runs - current_score)

            # Determine match phase
            if ball <= 36:
                phase = "powerplay"
                wicket_prob = 0.042 - (batting_info["batting_rating"] - 85) * 0.001
                boundary_prob = 0.22 + (dew_present * 0.02)
            elif ball <= 90:
                phase = "middle"
                wicket_prob = 0.048 + (pitch_spin_bias * 0.015) - (batting_info["batting_rating"] - 85) * 0.001
                boundary_prob = 0.14
            else:
                phase = "death"
                # In death overs, higher risk when required run rate is high
                req_rate = (runs_left / (balls_left / 6.0)) if balls_left > 0 else 12.0
                pressure_bump = min(0.06, max(0.0, (req_rate - 9.0) * 0.01))
                wicket_prob = 0.075 + pressure_bump
                boundary_prob = 0.20 + (dew_present * 0.03)

            # Adjust probabilities based on team strengths
            bowl_strength_mod = (bowling_info["bowling_rating"] - 85) * 0.002
            wicket_prob = np.clip(wicket_prob + bowl_strength_mod, 0.02, 0.18)

            # Ball outcome event
            rand_val = random.random()
            ball_runs = 0
            is_wicket = 0

            if rand_val < wicket_prob:
                is_wicket = 1
                wickets_lost += 1
                ball_runs = 0
            else:
                run_rand = random.random()
                if run_rand < 0.35:
                    ball_runs = 0
                elif run_rand < 0.70:
                    ball_runs = 1
                elif run_rand < 0.82:
                    ball_runs = 2
                elif run_rand < 0.83:
                    ball_runs = 3
                elif run_rand < 0.94:
                    ball_runs = 4
                else:
                    ball_runs = 6

            current_score += ball_runs
            recent_balls_runs.append(ball_runs)
            recent_balls_wickets.append(is_wicket)

            if len(recent_balls_runs) > 30:
                recent_balls_runs.pop(0)
                recent_balls_wickets.pop(0)

            # Sample every 3-6 balls for balanced state representation
            if ball % 3 == 0 or ball in [6, 12, 18, 24, 30, 36, 60, 90, 100, 110, 115, 118]:
                runs_last_5_overs = sum(recent_balls_runs)
                wickets_last_5_overs = sum(recent_balls_wickets)

                crr = round((current_score / (balls_bowled / 6.0)), 2)
                rrr = round((runs_left / (balls_left / 6.0)), 2) if balls_left > 0 else 99.0

                snapshot = {
                    "match_id": match_id,
                    "batting_team": batting_team,
                    "bowling_team": bowling_team,
                    "venue": venue,
                    "target_runs": target_runs,
                    "current_score": current_score,
                    "balls_bowled": balls_bowled,
                    "balls_left": balls_left,
                    "wickets_lost": wickets_lost,
                    "wickets_in_hand": 10 - wickets_lost,
                    "runs_left": runs_left,
                    "crr": crr,
                    "rrr": rrr,
                    "runs_last_5_overs": runs_last_5_overs,
                    "wickets_last_5_overs": wickets_last_5_overs,
                    "dew_present": dew_present,
                    "venue_avg_1st_innings": venue_info["avg_1st_innings"],
                    "venue_chasing_win_pct": venue_info["chasing_win_pct"]
                }
                match_snapshots.append(snapshot)

            # Check if match ended
            if current_score >= target_runs:
                winner = 1 # Batting team won
                match_finished = True
                break
            elif wickets_lost >= 10 or ball == 120:
                winner = 0 # Bowling team won (defended target)
                match_finished = True
                break

        if winner is None:
            winner = 1 if current_score >= target_runs else 0

        # Assign outcome to all sampled states in this match
        for s in match_snapshots:
            s["winner"] = winner
            dataset_rows.append(s)

    df = pd.DataFrame(dataset_rows)
    print(f"Generated {len(df)} live ground situation data points across {num_matches} matches.")
    return df

def save_default_dataset(output_path="data/ipl_live_ground_dataset.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = generate_realistic_match_dataset(num_matches=1400)
    df.to_csv(output_path, index=False)
    print(f"Dataset successfully saved to: {output_path}")
    return df

if __name__ == "__main__":
    save_default_dataset()

