"""
IPL Teams, Venues, and Ground Telemetry Configuration
Includes historical ground statistics, team colors, and venue profiles.
"""

TEAMS = {
    "Chennai Super Kings": {
        "short_name": "CSK",
        "primary_color": "#F9CD05",
        "secondary_color": "#1C2D5A",
        "text_color": "#000000",
        "batting_rating": 88,
        "bowling_rating": 86,
        "home_ground": "MA Chidambaram Stadium, Chepauk, Chennai",
        "championships": 5
    },
    "Mumbai Indians": {
        "short_name": "MI",
        "primary_color": "#004BA0",
        "secondary_color": "#D1AB3E",
        "text_color": "#FFFFFF",
        "batting_rating": 89,
        "bowling_rating": 87,
        "home_ground": "Wankhede Stadium, Mumbai",
        "championships": 5
    },
    "Royal Challengers Bengaluru": {
        "short_name": "RCB",
        "primary_color": "#EC1C24",
        "secondary_color": "#000000",
        "text_color": "#FFFFFF",
        "batting_rating": 90,
        "bowling_rating": 82,
        "home_ground": "M. Chinnaswamy Stadium, Bengaluru",
        "championships": 0
    },
    "Kolkata Knight Riders": {
        "short_name": "KKR",
        "primary_color": "#3A225D",
        "secondary_color": "#ECC542",
        "text_color": "#FFFFFF",
        "batting_rating": 88,
        "bowling_rating": 87,
        "home_ground": "Eden Gardens, Kolkata",
        "championships": 3
    },
    "Rajasthan Royals": {
        "short_name": "RR",
        "primary_color": "#EA1A85",
        "secondary_color": "#254AA5",
        "text_color": "#FFFFFF",
        "batting_rating": 86,
        "bowling_rating": 86,
        "home_ground": "Sawai Mansingh Stadium, Jaipur",
        "championships": 1
    },
    "Sunrisers Hyderabad": {
        "short_name": "SRH",
        "primary_color": "#F26522",
        "secondary_color": "#000000",
        "text_color": "#FFFFFF",
        "batting_rating": 89,
        "bowling_rating": 84,
        "home_ground": "Rajiv Gandhi International Stadium, Uppal, Hyderabad",
        "championships": 1
    },
    "Delhi Capitals": {
        "short_name": "DC",
        "primary_color": "#004C97",
        "secondary_color": "#EE2737",
        "text_color": "#FFFFFF",
        "batting_rating": 85,
        "bowling_rating": 85,
        "home_ground": "Arun Jaitley Stadium, Delhi",
        "championships": 0
    },
    "Punjab Kings": {
        "short_name": "PBKS",
        "primary_color": "#ED1B24",
        "secondary_color": "#D7A22A",
        "text_color": "#FFFFFF",
        "batting_rating": 84,
        "bowling_rating": 83,
        "home_ground": "Punjab Cricket Association IS Bindra Stadium, Mohali",
        "championships": 0
    },
    "Gujarat Titans": {
        "short_name": "GT",
        "primary_color": "#1C3C6B",
        "secondary_color": "#C3A154",
        "text_color": "#FFFFFF",
        "batting_rating": 87,
        "bowling_rating": 88,
        "home_ground": "Narendra Modi Stadium, Ahmedabad",
        "championships": 1
    },
    "Lucknow Super Giants": {
        "short_name": "LSG",
        "primary_color": "#0057B8",
        "secondary_color": "#EE3124",
        "text_color": "#FFFFFF",
        "batting_rating": 86,
        "bowling_rating": 86,
        "home_ground": "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow",
        "championships": 0
    }
}

VENUES = {
    "Wankhede Stadium, Mumbai": {
        "city": "Mumbai",
        "avg_1st_innings": 174,
        "avg_chasing_score": 168,
        "chasing_win_pct": 54.2,
        "dew_intensity": "High",
        "pitch_nature": "Batting Friendly / Fast Outfield",
        "pace_vs_spin_wickets_pct": [68, 32]
    },
    "Eden Gardens, Kolkata": {
        "city": "Kolkata",
        "avg_1st_innings": 178,
        "avg_chasing_score": 169,
        "chasing_win_pct": 53.5,
        "dew_intensity": "High",
        "pitch_nature": "High-Scoring / True Bounce",
        "pace_vs_spin_wickets_pct": [62, 38]
    },
    "M. Chinnaswamy Stadium, Bengaluru": {
        "city": "Bengaluru",
        "avg_1st_innings": 185,
        "avg_chasing_score": 176,
        "chasing_win_pct": 55.8,
        "dew_intensity": "Moderate",
        "pitch_nature": "Small Boundaries / Six Hitter's Haven",
        "pace_vs_spin_wickets_pct": [65, 35]
    },
    "MA Chidambaram Stadium, Chepauk, Chennai": {
        "city": "Chennai",
        "avg_1st_innings": 163,
        "avg_chasing_score": 152,
        "chasing_win_pct": 46.8,
        "dew_intensity": "Low",
        "pitch_nature": "Dry / Spin Friendly / Slower Deck",
        "pace_vs_spin_wickets_pct": [48, 52]
    },
    "Narendra Modi Stadium, Ahmedabad": {
        "city": "Ahmedabad",
        "avg_1st_innings": 175,
        "avg_chasing_score": 165,
        "chasing_win_pct": 51.5,
        "dew_intensity": "Moderate",
        "pitch_nature": "Even Bounce / Large Boundaries",
        "pace_vs_spin_wickets_pct": [64, 36]
    },
    "Rajiv Gandhi International Stadium, Uppal, Hyderabad": {
        "city": "Hyderabad",
        "avg_1st_innings": 176,
        "avg_chasing_score": 164,
        "chasing_win_pct": 49.0,
        "dew_intensity": "Low",
        "pitch_nature": "Flat Deck / High Initial Scoring",
        "pace_vs_spin_wickets_pct": [60, 40]
    },
    "Arun Jaitley Stadium, Delhi": {
        "city": "Delhi",
        "avg_1st_innings": 172,
        "avg_chasing_score": 166,
        "chasing_win_pct": 52.4,
        "dew_intensity": "Moderate",
        "pitch_nature": "Short Square Boundaries / Fast Outfield",
        "pace_vs_spin_wickets_pct": [58, 42]
    },
    "Sawai Mansingh Stadium, Jaipur": {
        "city": "Jaipur",
        "avg_1st_innings": 164,
        "avg_chasing_score": 157,
        "chasing_win_pct": 53.0,
        "dew_intensity": "Low",
        "pitch_nature": "Balanced / Big Outfield",
        "pace_vs_spin_wickets_pct": [55, 45]
    },
    "Punjab Cricket Association IS Bindra Stadium, Mohali": {
        "city": "Mohali",
        "avg_1st_innings": 173,
        "avg_chasing_score": 166,
        "chasing_win_pct": 54.0,
        "dew_intensity": "High",
        "pitch_nature": "Pace Friendly / Good Carry",
        "pace_vs_spin_wickets_pct": [71, 29]
    },
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium, Lucknow": {
        "city": "Lucknow",
        "avg_1st_innings": 160,
        "avg_chasing_score": 149,
        "chasing_win_pct": 44.5,
        "dew_intensity": "Low",
        "pitch_nature": "Gripping Black & Red Soil / Low Scoring",
        "pace_vs_spin_wickets_pct": [46, 54]
    }
}

