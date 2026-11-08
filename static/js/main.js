/**
 * IPL WINNING TEAM PREDICTION SYSTEM
 * Real-Time Telemetry & Simulation Controller
 */

let wormChart = null;
let autoPlayInterval = null;
let currentSimState = null;
let debounceTimer = null;

// Preset Scenarios
const PRESETS = {
    last_over: {
        batting_team: "Chennai Super Kings",
        bowling_team: "Mumbai Indians",
        venue: "Wankhede Stadium, Mumbai",
        target_runs: 185,
        current_score: 173,
        overs_bowled: 19.0,
        wickets_lost: 6,
        runs_last_5_overs: 52,
        wickets_last_5_overs: 2,
        dew_present: true
    },
    powerplay_blast: {
        batting_team: "Royal Challengers Bengaluru",
        bowling_team: "Sunrisers Hyderabad",
        venue: "M. Chinnaswamy Stadium, Bengaluru",
        target_runs: 215,
        current_score: 74,
        overs_bowled: 5.4,
        wickets_lost: 1,
        runs_last_5_overs: 66,
        wickets_last_5_overs: 1,
        dew_present: true
    },
    middle_squeeze: {
        batting_team: "Kolkata Knight Riders",
        bowling_team: "Rajasthan Royals",
        venue: "Eden Gardens, Kolkata",
        target_runs: 168,
        current_score: 84,
        overs_bowled: 12.3,
        wickets_lost: 4,
        runs_last_5_overs: 26,
        wickets_last_5_overs: 2,
        dew_present: false
    },
    collapse: {
        batting_team: "Delhi Capitals",
        bowling_team: "Gujarat Titans",
        venue: "Narendra Modi Stadium, Ahmedabad",
        target_runs: 178,
        current_score: 104,
        overs_bowled: 15.1,
        wickets_lost: 7,
        runs_last_5_overs: 28,
        wickets_last_5_overs: 3,
        dew_present: false
    }
};

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    initSliders();
    initWormChart();
    triggerPrediction(); // Run initial prediction on load
    startNewSimulation(); // Prepare simulation state
});

function switchTab(tabId) {
    // Hide all contents
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    const content = document.getElementById(`tab-${tabId}`);
    if (content) content.classList.remove('hidden');

    const btn = document.getElementById(`tab-btn-${tabId}`);
    if (btn) btn.classList.add('active');

    // Trigger re-render of icons in new views
    lucide.createIcons();
}

function initSliders() {
    const inputs = [
        { id: 'target_runs', label: 'target-val' },
        { id: 'current_score', label: 'score-val' },
        { id: 'overs_bowled', label: 'overs-val' },
        { id: 'wickets_lost', label: 'wickets-val' },
        { id: 'runs_last_5_overs', label: 'runs-5ov-val' },
        { id: 'wickets_last_5_overs', label: 'wkts-5ov-val' }
    ];

    inputs.forEach(item => {
        const el = document.getElementById(item.id);
        const lbl = document.getElementById(item.label);
        if (el && lbl) {
            el.addEventListener('input', (e) => {
                lbl.innerText = e.target.value;
                debouncedPredict();
            });
        }
    });

    ['batting_team', 'bowling_team', 'venue', 'dew_present'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => {
                triggerPrediction();
            });
        }
    });
}

function debouncedPredict() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        triggerPrediction();
    }, 150);
}

function loadScenario(presetKey) {
    const p = PRESETS[presetKey];
    if (!p) return;

    document.getElementById('batting_team').value = p.batting_team;
    document.getElementById('bowling_team').value = p.bowling_team;
    document.getElementById('venue').value = p.venue;
    document.getElementById('target_runs').value = p.target_runs;
    document.getElementById('target-val').innerText = p.target_runs;
    document.getElementById('current_score').value = p.current_score;
    document.getElementById('score-val').innerText = p.current_score;
    document.getElementById('overs_bowled').value = p.overs_bowled;
    document.getElementById('overs-val').innerText = p.overs_bowled;
    document.getElementById('wickets_lost').value = p.wickets_lost;
    document.getElementById('wickets-val').innerText = p.wickets_lost;
    document.getElementById('runs_last_5_overs').value = p.runs_last_5_overs;
    document.getElementById('runs-5ov-val').innerText = p.runs_last_5_overs;
    document.getElementById('wickets_last_5_overs').value = p.wickets_last_5_overs;
    document.getElementById('wkts-5ov-val').innerText = p.wickets_last_5_overs;
    document.getElementById('dew_present').checked = p.dew_present;

    triggerPrediction();
}

async function triggerPrediction() {
    const payload = {
        batting_team: document.getElementById('batting_team').value,
        bowling_team: document.getElementById('bowling_team').value,
        venue: document.getElementById('venue').value,
        target_runs: parseInt(document.getElementById('target_runs').value),
        current_score: parseInt(document.getElementById('current_score').value),
        overs_bowled: parseFloat(document.getElementById('overs_bowled').value),
        wickets_lost: parseInt(document.getElementById('wickets_lost').value),
        runs_last_5_overs: parseInt(document.getElementById('runs_last_5_overs').value),
        wickets_last_5_overs: parseInt(document.getElementById('wickets_last_5_overs').value),
        dew_present: document.getElementById('dew_present').checked ? 1 : 0
    };

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await response.json();
        if (res.success) {
            updateDashboard(res.data);
        }
    } catch (err) {
        console.error("Prediction failed:", err);
    }
}

function updateDashboard(d) {
    // Team Header and Names
    document.getElementById('live-match-title').innerText = `${d.batting_team_short} vs ${d.bowling_team_short}`;
    document.getElementById('res-bat-name').innerText = `${d.batting_team} (${d.batting_team_short})`;
    document.getElementById('res-bowl-name').innerText = `${d.bowling_team} (${d.bowling_team_short})`;

    // Percentages
    document.getElementById('res-bat-prob').innerText = `${d.batting_win_pct}%`;
    document.getElementById('res-bowl-prob').innerText = `${d.bowling_win_pct}%`;

    // Progress Bar
    document.getElementById('prob-bar-bat').style.width = `${d.batting_win_pct}%`;
    document.getElementById('prob-bar-bowl').style.width = `${d.bowling_win_pct}%`;
    document.getElementById('bar-label-bat').innerText = `${d.batting_team_short}: ${d.batting_win_pct}%`;
    document.getElementById('bar-label-bowl').innerText = `${d.bowling_team_short}: ${d.bowling_win_pct}%`;

    // Telemetry Numbers
    document.getElementById('stat-rrr').innerText = d.rrr > 50 ? 'N/A' : d.rrr.toFixed(2);
    document.getElementById('stat-crr').innerText = d.crr.toFixed(2);
    document.getElementById('stat-runs-left').innerText = d.runs_left;
    document.getElementById('stat-balls-left').innerText = d.balls_left;
    document.getElementById('stat-wickets-hand').innerText = d.wickets_in_hand;

    // Narrative & Pressure Badge
    document.getElementById('status-narrative').innerText = d.status_text;

    const pBadge = document.getElementById('pressure-badge');
    pBadge.innerHTML = `<span class="w-2 h-2 rounded-full" style="background-color: ${d.pressure_color}"></span> ${d.pressure_level} Pressure`;

    // Drivers Container
    const driversDiv = document.getElementById('drivers-container');
    driversDiv.innerHTML = '';
    d.key_drivers.forEach(driver => {
        const item = document.createElement('div');
        item.className = 'flex items-center gap-2 text-xs text-slate-300 bg-[#0D1322] px-3 py-2 rounded-lg border border-slate-800';
        item.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span> ${driver}`;
        driversDiv.appendChild(item);
    });
}

// ==========================================
// SIMULATOR LOGIC & CHART.JS
// ==========================================

function initWormChart() {
    const ctx = document.getElementById('probabilityWormChart');
    if (!ctx) return;

    wormChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [0],
            datasets: [
                {
                    label: 'Batting Team Win %',
                    data: [50],
                    borderColor: '#F59E0B',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 2.5,
                    pointRadius: 2,
                    pointHoverRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Win Prob: ${ctx.parsed.y.toFixed(1)}%`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748B', font: { size: 10 } },
                    title: { display: true, text: 'Deliveries Bowled', color: '#64748B', font: { size: 10 } }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#64748B',
                        font: { size: 10 },
                        callback: (v) => `${v}%`
                    }
                }
            }
        }
    });
}

function startNewSimulation() {
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
        document.getElementById('sim-auto-btn').innerHTML = `<i data-lucide="play" class="w-4 h-4"></i> Auto Play`;
    }

    const batTeam = document.getElementById('sim-batting-team').value;
    const bowlTeam = document.getElementById('sim-bowling-team').value;
    const venue = document.getElementById('sim-venue').value;
    const target = parseInt(document.getElementById('sim-target-input').value) || 185;

    currentSimState = {
        balls_bowled: 0,
        overs_bowled: 0.0,
        current_score: 0,
        wickets_lost: 0,
        target_runs: target,
        batting_team: batTeam,
        bowling_team: bowlTeam,
        venue: venue,
        dew_present: 1,
        recent_balls_runs: [],
        recent_balls_wickets: []
    };

    // Reset UI
    document.getElementById('sim-teams-heading').innerText = `${batTeam} vs ${bowlTeam}`;
    document.getElementById('sim-display-score').innerText = `0/0`;
    document.getElementById('sim-display-overs').innerText = `0.0`;
    document.getElementById('sim-display-target').innerText = target;
    document.getElementById('sim-display-equation').innerText = `Need ${target} runs in 120 balls`;
    document.getElementById('sim-commentary-text').innerText = `Match underway at ${venue}. ${batTeam} begins the chase!`;
    document.getElementById('sim-balls-strip').innerHTML = `<div class="w-8 h-8 rounded-full bg-slate-800 text-slate-400 text-xs flex items-center justify-center font-mono font-bold">-</div>`;
    document.getElementById('sim-total-balls-badge').innerText = `0 / 120 balls`;
    document.getElementById('sim-events-log').innerHTML = `<div class="p-2.5 bg-[#0D1322] rounded-lg border border-slate-800/80 text-slate-300">Match started. Target is ${target}.</div>`;

    // Reset Chart
    if (wormChart) {
        wormChart.data.labels = [0];
        wormChart.data.datasets[0].data = [50];
        wormChart.data.datasets[0].label = `${batTeam} Win %`;
        wormChart.update();
    }

    lucide.createIcons();
}

async function simulateSingleBall() {
    if (!currentSimState) return;

    if (currentSimState.match_over || currentSimState.current_score >= currentSimState.target_runs || currentSimState.wickets_lost >= 10 || currentSimState.balls_bowled >= 120) {
        alert("Match has ended!");
        if (autoPlayInterval) clearInterval(autoPlayInterval);
        return;
    }

    try {
        const response = await fetch('/api/simulate-next-ball', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentSimState)
        });
        const res = await response.json();
        if (res.success) {
            handleSimDeliveryResult(res.data);
        }
    } catch (err) {
        console.error("Simulation step error:", err);
    }
}

function handleSimDeliveryResult(pred) {
    currentSimState.balls_bowled = pred.balls_bowled;
    currentSimState.overs_bowled = pred.balls_bowled / 6.0;
    currentSimState.current_score = pred.current_score;
    currentSimState.wickets_lost = pred.wickets_lost;
    currentSimState.recent_balls_runs = pred.recent_balls_runs;
    currentSimState.recent_balls_wickets = pred.recent_balls_wickets;
    currentSimState.match_over = pred.match_over;

    // Update Scoreboard
    document.getElementById('sim-display-score').innerText = `${pred.current_score}/${pred.wickets_lost}`;
    document.getElementById('sim-display-overs').innerText = pred.over_display;
    document.getElementById('sim-bat-pct').innerText = `${pred.batting_win_pct}%`;
    document.getElementById('sim-bowl-pct').innerText = `${pred.bowling_win_pct}%`;
    document.getElementById('sim-bat-lbl').innerText = `${pred.batting_team_short} Win %`;
    document.getElementById('sim-bowl-lbl').innerText = `${pred.bowling_team_short} Win %`;
    document.getElementById('sim-total-balls-badge').innerText = `${pred.balls_bowled} / 120 balls`;

    if (pred.current_score >= pred.target_runs) {
        document.getElementById('sim-display-equation').innerText = `${pred.batting_team} won by ${10 - pred.wickets_lost} wickets!`;
    } else if (pred.wickets_lost >= 10) {
        document.getElementById('sim-display-equation').innerText = `${pred.bowling_team} won! (All out)`;
    } else if (pred.balls_bowled >= 120) {
        document.getElementById('sim-display-equation').innerText = `${pred.bowling_team} won by ${pred.runs_left} runs!`;
    } else {
        document.getElementById('sim-display-equation').innerText = `Need ${pred.runs_left} off ${pred.balls_left} balls (RRR: ${pred.rrr.toFixed(2)})`;
    }

    // Commentary & Event Tag
    document.getElementById('sim-commentary-text').innerText = pred.last_ball_commentary;

    // Deliveries Strip
    const strip = document.getElementById('sim-balls-strip');
    const ballTag = document.createElement('div');
    const evt = pred.last_ball_event;

    let tagClass = 'ball-dot';
    if (evt === 'W') tagClass = 'ball-wicket';
    else if (evt === '6') tagClass = 'ball-six';
    else if (evt === '4') tagClass = 'ball-four';
    else if (evt === '1' || evt === '2' || evt === '3') tagClass = 'ball-single';

    ballTag.className = `ball-tag ${tagClass}`;
    ballTag.innerText = evt;
    strip.appendChild(ballTag);
    strip.scrollLeft = strip.scrollWidth;

    // Append to Log
    const log = document.getElementById('sim-events-log');
    const logItem = document.createElement('div');
    logItem.className = 'p-2 bg-[#0D1322] rounded border border-slate-800 flex items-center justify-between';
    logItem.innerHTML = `
        <span><strong>${pred.over_display} ov</strong>: [${evt}] ${pred.last_ball_commentary}</span>
        <span class="font-mono text-amber-400 font-bold ml-2">${pred.batting_win_pct}%</span>
    `;
    log.insertBefore(logItem, log.firstChild);

    // Update Worm Chart
    if (wormChart) {
        wormChart.data.labels.push(pred.balls_bowled);
        wormChart.data.datasets[0].data.push(pred.batting_win_pct);
        wormChart.update('none'); // Update without lagging animation
    }

    // Swing Indicator
    const prevProb = wormChart.data.datasets[0].data[wormChart.data.datasets[0].data.length - 2] || 50;
    const diff = pred.batting_win_pct - prevProb;
    const swingEl = document.getElementById('sim-swing-indicator');
    if (diff > 0) {
        swingEl.innerHTML = `<span class="text-emerald-400 font-bold">+${diff.toFixed(1)}% to ${pred.batting_team_short}</span>`;
    } else if (diff < 0) {
        swingEl.innerHTML = `<span class="text-red-400 font-bold">${diff.toFixed(1)}% (swung to ${pred.bowling_team_short})</span>`;
    } else {
        swingEl.innerHTML = `<span class="text-slate-400">0.0% (Equilibrium)</span>`;
    }
}

function toggleAutoPlay() {
    const btn = document.getElementById('sim-auto-btn');
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
        btn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i> Auto Play`;
        lucide.createIcons();
    } else {
        btn.innerHTML = `<i data-lucide="pause" class="w-4 h-4"></i> Pause`;
        lucide.createIcons();
        autoPlayInterval = setInterval(() => {
            if (currentSimState && !currentSimState.match_over) {
                simulateSingleBall();
            } else {
                clearInterval(autoPlayInterval);
                autoPlayInterval = null;
                btn.innerHTML = `<i data-lucide="play" class="w-4 h-4"></i> Auto Play`;
                lucide.createIcons();
            }
        }, 650);
    }
}

async function simulateFullMatchFast() {
    if (autoPlayInterval) {
        clearInterval(autoPlayInterval);
        autoPlayInterval = null;
    }

    const batTeam = document.getElementById('sim-batting-team').value;
    const bowlTeam = document.getElementById('sim-bowling-team').value;
    const venue = document.getElementById('sim-venue').value;
    const target = parseInt(document.getElementById('sim-target-input').value) || 185;

    const payload = {
        batting_team: batTeam,
        bowling_team: bowlTeam,
        venue: venue,
        target_runs: target,
        dew_present: 1
    };

    try {
        const response = await fetch('/api/simulate-full-match', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await response.json();
        if (res.success) {
            renderFullMatchTimeline(res.data);
        }
    } catch (err) {
        console.error("Full simulation error:", err);
    }
}

function renderFullMatchTimeline(data) {
    const timeline = data.timeline;
    if (!timeline || timeline.length === 0) return;

    // Reset Strip and Log
    document.getElementById('sim-balls-strip').innerHTML = '';
    const log = document.getElementById('sim-events-log');
    log.innerHTML = '';

    const labels = [];
    const probs = [];

    timeline.forEach(step => {
        labels.push(step.ball);
        probs.push(step.batting_win_pct);

        if (step.ball > 0) {
            const strip = document.getElementById('sim-balls-strip');
            const ballTag = document.createElement('div');
            const evt = step.event;

            let tagClass = 'ball-dot';
            if (evt === 'W') tagClass = 'ball-wicket';
            else if (evt === '6') tagClass = 'ball-six';
            else if (evt === '4') tagClass = 'ball-four';
            else if (evt === '1' || evt === '2' || evt === '3') tagClass = 'ball-single';

            ballTag.className = `ball-tag ${tagClass}`;
            ballTag.innerText = evt;
            strip.appendChild(ballTag);
        }
    });

    const last = timeline[timeline.length - 1];
    document.getElementById('sim-display-score').innerText = `${last.score}/${last.wickets}`;
    document.getElementById('sim-display-overs').innerText = last.over_display;
    document.getElementById('sim-bat-pct').innerText = `${last.batting_win_pct}%`;
    document.getElementById('sim-bowl-pct').innerText = `${last.bowling_win_pct}%`;
    document.getElementById('sim-commentary-text').innerText = `${data.winner} won! Result: ${data.final_score}`;
    document.getElementById('sim-display-equation').innerText = `Winner: ${data.winner}`;

    // Update Chart
    if (wormChart) {
        wormChart.data.labels = labels;
        wormChart.data.datasets[0].data = probs;
        wormChart.data.datasets[0].label = `${data.batting_team} Win %`;
        wormChart.update();
    }
}

