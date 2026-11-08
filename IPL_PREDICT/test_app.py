import json
from app import app

client = app.test_client()

# 1. Test index page
res1 = client.get('/')
assert res1.status_code == 200, f'Index failed: {res1.status_code}'
print('[✓] GET / -> HTTP 200 OK')

# 2. Test live predict API
payload = {
    'batting_team': 'Chennai Super Kings',
    'bowling_team': 'Mumbai Indians',
    'venue': 'Wankhede Stadium, Mumbai',
    'target_runs': 185,
    'current_score': 142,
    'overs_bowled': 15.2,
    'wickets_lost': 3,
    'runs_last_5_overs': 46,
    'wickets_last_5_overs': 1,
    'dew_present': 1
}
res2 = client.post('/api/predict', json=payload)
assert res2.status_code == 200, f'Predict failed: {res2.status_code}'
data2 = res2.get_json()
assert data2['success'] is True
bat_pct = data2["data"]["batting_win_pct"]
bowl_pct = data2["data"]["bowling_win_pct"]
print(f'[✓] POST /api/predict -> Batting Win: {bat_pct}%, Bowling Win: {bowl_pct}%')

# 3. Test single ball simulation
sim_payload = {
    'balls_bowled': 10,
    'current_score': 14,
    'wickets_lost': 1,
    'target_runs': 180,
    'batting_team': 'Royal Challengers Bengaluru',
    'bowling_team': 'Kolkata Knight Riders',
    'venue': 'M. Chinnaswamy Stadium, Bengaluru',
    'dew_present': 1,
    'recent_balls_runs': [1, 4, 0, 1, 0, 6, 1, 0, 1, 0],
    'recent_balls_wickets': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
}
res3 = client.post('/api/simulate-next-ball', json=sim_payload)
assert res3.status_code == 200
data3 = res3.get_json()
assert data3['success'] is True
ball_event = data3["data"]["last_ball_event"]
comm = data3["data"]["last_ball_commentary"][:45]
print(f'[✓] POST /api/simulate-next-ball -> Ball: {ball_event}, Commentary: {comm}...')

# 4. Test full match simulation
match_payload = {
    'batting_team': 'Chennai Super Kings',
    'bowling_team': 'Mumbai Indians',
    'venue': 'Wankhede Stadium, Mumbai',
    'target_runs': 175,
    'dew_present': 1
}
res4 = client.post('/api/simulate-full-match', json=match_payload)
assert res4.status_code == 200
data4 = res4.get_json()
assert data4['success'] is True
winner = data4["data"]["winner"]
timeline_len = len(data4["data"]["timeline"])
print(f'[✓] POST /api/simulate-full-match -> Winner: {winner}, Timeline events: {timeline_len}')

# 5. Test model stats
res5 = client.get('/api/model-stats')
assert res5.status_code == 200
data5 = res5.get_json()
acc = data5["metadata"]["accuracy"]
auc = data5["metadata"]["roc_auc"]
print(f'[✓] GET /api/model-stats -> Accuracy: {acc}%, AUC: {auc}')
print('\n🎉 All tests passed successfully!')

