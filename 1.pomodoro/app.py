# Pomodoro Timer App with Gamification
from flask import Flask, render_template_string, request, jsonify
import sqlite3
import json
from datetime import datetime, date, timedelta
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'pomodoro.db')

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        completed_at TEXT,
        session_type TEXT,
        duration INTEGER,
        completed INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
        id INTEGER PRIMARY KEY DEFAULT 1,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        streak INTEGER DEFAULT 0,
        last_session_date TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        badge_key TEXT UNIQUE,
        earned_at TEXT
    )''')
    c.execute(
        'INSERT OR IGNORE INTO user_stats (id, xp, level, streak, last_session_date) VALUES (1, 0, 1, 0, NULL)'
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# XP / Level helpers
# ---------------------------------------------------------------------------

XP_PER_WORK_SESSION = 25
XP_PER_BREAK_SESSION = 10
XP_PER_LEVEL = 100


def calculate_level(xp: int) -> int:
    return 1 + xp // XP_PER_LEVEL


def xp_in_current_level(xp: int) -> int:
    return xp % XP_PER_LEVEL


# ---------------------------------------------------------------------------
# Streak helper
# ---------------------------------------------------------------------------

def update_streak(conn) -> int:
    c = conn.cursor()
    c.execute('SELECT last_session_date, streak FROM user_stats WHERE id = 1')
    row = c.fetchone()
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    if row['last_session_date'] == today:
        return row['streak']
    elif row['last_session_date'] == yesterday:
        new_streak = row['streak'] + 1
    else:
        new_streak = 1

    c.execute(
        'UPDATE user_stats SET streak = ?, last_session_date = ? WHERE id = 1',
        (new_streak, today),
    )
    conn.commit()
    return new_streak


# ---------------------------------------------------------------------------
# Badge definitions
# ---------------------------------------------------------------------------

BADGE_DEFINITIONS = [
    {
        'key': 'first_session',
        'icon': '🎯',
        'name': '初セッション',
        'desc': '最初のポモドーロセッションを完了しました',
        'check': lambda s: s['total_sessions'] >= 1,
    },
    {
        'key': 'streak_3',
        'icon': '🔥',
        'name': '3日連続',
        'desc': '3日連続でセッションを完了しました',
        'check': lambda s: s['streak'] >= 3,
    },
    {
        'key': 'streak_7',
        'icon': '⚡',
        'name': '1週間連続',
        'desc': '7日連続でセッションを完了しました',
        'check': lambda s: s['streak'] >= 7,
    },
    {
        'key': 'week_10',
        'icon': '💪',
        'name': '週間ファイター',
        'desc': '1週間に10回セッションを完了しました',
        'check': lambda s: s['sessions_this_week'] >= 10,
    },
    {
        'key': 'daily_5',
        'icon': '🌟',
        'name': '集中マスター',
        'desc': '1日に5回のセッションを完了しました',
        'check': lambda s: s['sessions_today'] >= 5,
    },
    {
        'key': 'sessions_10',
        'icon': '🥉',
        'name': '10セッション達成',
        'desc': '合計10回のセッションを完了しました',
        'check': lambda s: s['total_sessions'] >= 10,
    },
    {
        'key': 'sessions_25',
        'icon': '🥈',
        'name': '25セッション達成',
        'desc': '合計25回のセッションを完了しました',
        'check': lambda s: s['total_sessions'] >= 25,
    },
    {
        'key': 'sessions_100',
        'icon': '💯',
        'name': 'センチュリー',
        'desc': '合計100回のセッションを完了しました',
        'check': lambda s: s['total_sessions'] >= 100,
    },
    {
        'key': 'level_5',
        'icon': '🎖️',
        'name': 'レベル5到達',
        'desc': 'レベル5に到達しました',
        'check': lambda s: s['level'] >= 5,
    },
    {
        'key': 'level_10',
        'icon': '👑',
        'name': 'レベル10到達',
        'desc': 'レベル10に到達しました',
        'check': lambda s: s['level'] >= 10,
    },
]


def check_and_award_badges(conn, stats: dict) -> list:
    c = conn.cursor()
    c.execute('SELECT badge_key FROM badges')
    earned_keys = {row['badge_key'] for row in c.fetchall()}

    newly_earned = []
    for badge in BADGE_DEFINITIONS:
        if badge['key'] not in earned_keys and badge['check'](stats):
            c.execute(
                'INSERT INTO badges (badge_key, earned_at) VALUES (?, ?)',
                (badge['key'], datetime.now().isoformat()),
            )
            newly_earned.append({'icon': badge['icon'], 'name': badge['name'], 'desc': badge['desc']})
    conn.commit()
    return newly_earned


# ---------------------------------------------------------------------------
# Stats helper
# ---------------------------------------------------------------------------

def get_stats(conn) -> dict:
    c = conn.cursor()
    today = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()
    month_start = date.today().replace(day=1).isoformat()

    c.execute('SELECT COUNT(*) as cnt FROM sessions WHERE completed = 1 AND session_type = "work"')
    total = c.fetchone()['cnt']

    c.execute(
        'SELECT COUNT(*) as cnt FROM sessions WHERE completed = 1 AND session_type = "work" AND date(completed_at) = ?',
        (today,),
    )
    today_count = c.fetchone()['cnt']

    c.execute(
        'SELECT COUNT(*) as cnt FROM sessions WHERE completed = 1 AND session_type = "work" AND date(completed_at) >= ?',
        (week_start,),
    )
    week_count = c.fetchone()['cnt']

    c.execute(
        'SELECT COUNT(*) as cnt FROM sessions WHERE completed = 1 AND session_type = "work" AND date(completed_at) >= ?',
        (month_start,),
    )
    month_count = c.fetchone()['cnt']

    c.execute('SELECT xp, level, streak FROM user_stats WHERE id = 1')
    user = c.fetchone()

    return {
        'total_sessions': total,
        'sessions_today': today_count,
        'sessions_this_week': week_count,
        'sessions_this_month': month_count,
        'xp': user['xp'],
        'level': user['level'],
        'streak': user['streak'],
        'xp_in_level': xp_in_current_level(user['xp']),
        'xp_per_level': XP_PER_LEVEL,
    }


# ---------------------------------------------------------------------------
# HTML Template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🍅 ポモドーロタイマー</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  body { background: #1a1a2e; color: #eee; }
  .card { background: #16213e; border: 1px solid #0f3460; color: #eee; }
  .timer-display {
    font-size: 5rem; font-weight: 700; letter-spacing: 4px;
    color: #e94560; text-shadow: 0 0 20px rgba(233,69,96,0.5);
  }
  .xp-bar-container { background: #0f3460; border-radius: 20px; height: 14px; }
  .xp-bar { background: linear-gradient(90deg, #e94560, #f5a623);
            border-radius: 20px; height: 100%; transition: width 0.6s ease; }
  .badge-card { background: #0f3460; border-radius: 12px; padding: 12px;
               text-align: center; opacity: 0.4; transition: opacity 0.3s; }
  .badge-card.earned { opacity: 1; box-shadow: 0 0 12px rgba(249,166,35,0.5); }
  .streak-number { font-size: 3rem; font-weight: 700; color: #f5a623; }
  .btn-work { background: #e94560; border: none; font-size: 1.1rem; }
  .btn-break { background: #0f7b6c; border: none; font-size: 1.1rem; }
  .btn-work:hover { background: #c73652; }
  .btn-break:hover { background: #0a6359; }
  .level-badge {
    display: inline-block; background: linear-gradient(135deg,#e94560,#f5a623);
    padding: 4px 14px; border-radius: 20px; font-weight: 700; font-size: 1rem;
  }
  .toast-container { position: fixed; top: 20px; right: 20px; z-index: 9999; }
  .session-type-label { font-size: 1.2rem; color: #aaa; margin-bottom: 8px; }
  nav { background: #0f3460 !important; }
</style>
</head>
<body>
<nav class="navbar navbar-dark mb-4" style="background:#0f3460!important">
  <div class="container">
    <span class="navbar-brand fw-bold fs-4">🍅 ポモドーロタイマー</span>
    <span id="nav-level" class="level-badge">Lv.1</span>
  </div>
</nav>

<div class="container pb-5">
  <div class="row g-4">

    <!-- Timer Card -->
    <div class="col-12 col-lg-5">
      <div class="card rounded-4 p-4 text-center h-100">
        <div class="session-type-label" id="session-type-label">🍅 ワークセッション</div>
        <div class="timer-display my-3" id="timer">25:00</div>
        <div class="d-flex gap-2 justify-content-center mb-4">
          <button class="btn btn-work text-white px-4 py-2 rounded-3" onclick="startTimer()">▶ スタート</button>
          <button class="btn btn-secondary px-4 py-2 rounded-3" onclick="pauseTimer()">⏸ 一時停止</button>
          <button class="btn btn-outline-danger px-4 py-2 rounded-3" onclick="resetTimer()">↺ リセット</button>
        </div>
        <div class="d-flex gap-2 justify-content-center">
          <button class="btn btn-work text-white px-3 py-1 rounded-3 btn-sm" onclick="setMode('work')">🍅 ワーク (25分)</button>
          <button class="btn btn-break text-white px-3 py-1 rounded-3 btn-sm" onclick="setMode('short_break')">☕ 短休憩 (5分)</button>
          <button class="btn btn-break text-white px-3 py-1 rounded-3 btn-sm" onclick="setMode('long_break')">🛋️ 長休憩 (15分)</button>
        </div>
      </div>
    </div>

    <!-- Stats / XP Card -->
    <div class="col-12 col-lg-7">
      <div class="card rounded-4 p-4 h-100">
        <h5 class="mb-3">📊 ステータス</h5>
        <div class="row g-3 mb-3">
          <div class="col-6 col-sm-3 text-center">
            <div class="fs-2 fw-bold text-danger" id="stat-today">0</div>
            <div class="small text-muted">今日</div>
          </div>
          <div class="col-6 col-sm-3 text-center">
            <div class="streak-number" id="stat-streak">0</div>
            <div class="small text-muted">🔥 ストリーク</div>
          </div>
          <div class="col-6 col-sm-3 text-center">
            <div class="fs-2 fw-bold text-info" id="stat-week">0</div>
            <div class="small text-muted">今週</div>
          </div>
          <div class="col-6 col-sm-3 text-center">
            <div class="fs-2 fw-bold text-success" id="stat-total">0</div>
            <div class="small text-muted">合計</div>
          </div>
        </div>
        <hr style="border-color:#0f3460">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span>⚡ XP / レベル</span>
          <span id="xp-label" class="text-warning fw-bold">0 / 100 XP</span>
        </div>
        <div class="xp-bar-container mb-1">
          <div class="xp-bar" id="xp-bar" style="width:0%"></div>
        </div>
        <div class="text-end small text-muted mt-1">
          <span id="level-label" class="level-badge">Lv.1</span>
        </div>
      </div>
    </div>

    <!-- Weekly Chart -->
    <div class="col-12 col-md-6">
      <div class="card rounded-4 p-4">
        <h5 class="mb-3">📅 週間統計</h5>
        <canvas id="weeklyChart" height="180"></canvas>
      </div>
    </div>

    <!-- Monthly Chart -->
    <div class="col-12 col-md-6">
      <div class="card rounded-4 p-4">
        <h5 class="mb-3">🗓️ 月間統計（過去4週間）</h5>
        <canvas id="monthlyChart" height="180"></canvas>
      </div>
    </div>

    <!-- Badges -->
    <div class="col-12">
      <div class="card rounded-4 p-4">
        <h5 class="mb-3">🏅 達成バッジ</h5>
        <div class="row g-3" id="badges-grid"></div>
      </div>
    </div>

  </div>
</div>

<!-- Toast notifications -->
<div class="toast-container" id="toast-container"></div>

<script>
// ---------------------------------------------------------------------------
// Timer logic
// ---------------------------------------------------------------------------
const MODES = {
  work:        { label: '🍅 ワークセッション', seconds: 25 * 60, type: 'work' },
  short_break: { label: '☕ 短休憩',           seconds:  5 * 60, type: 'short_break' },
  long_break:  { label: '🛋️ 長休憩',           seconds: 15 * 60, type: 'long_break' },
};

let currentMode = 'work';
let remaining = MODES.work.seconds;
let timerInterval = null;
let isRunning = false;

function formatTime(sec) {
  const m = String(Math.floor(sec / 60)).padStart(2, '0');
  const s = String(sec % 60).padStart(2, '0');
  return `${m}:${s}`;
}

function setMode(mode) {
  pauseTimer();
  currentMode = mode;
  remaining = MODES[mode].seconds;
  document.getElementById('timer').textContent = formatTime(remaining);
  document.getElementById('session-type-label').textContent = MODES[mode].label;
}

function startTimer() {
  if (isRunning) return;
  isRunning = true;
  timerInterval = setInterval(() => {
    remaining--;
    document.getElementById('timer').textContent = formatTime(remaining);
    if (remaining <= 0) {
      clearInterval(timerInterval);
      isRunning = false;
      onTimerComplete();
    }
  }, 1000);
}

function pauseTimer() {
  clearInterval(timerInterval);
  isRunning = false;
}

function resetTimer() {
  pauseTimer();
  remaining = MODES[currentMode].seconds;
  document.getElementById('timer').textContent = formatTime(remaining);
}

async function onTimerComplete() {
  const type = MODES[currentMode].type;
  const duration = MODES[currentMode].seconds;
  try {
    const res = await fetch('/api/session/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_type: type, duration }),
    });
    const data = await res.json();
    showToast(`✅ セッション完了！ +${data.xp_gained} XP`, 'success');
    data.new_badges.forEach(b => showToast(`🏅 バッジ獲得: ${b.icon} ${b.name}`, 'warning'));
    if (data.leveled_up) showToast(`🎉 レベルアップ！ Lv.${data.new_level} になりました！`, 'info');
    await refreshStats();
    await refreshCharts();
    await refreshBadges();
  } catch (e) {
    console.error(e);
  }
  // Auto-switch to next mode
  if (currentMode === 'work') setMode('short_break');
  else setMode('work');
}

// ---------------------------------------------------------------------------
// Toast
// ---------------------------------------------------------------------------
function showToast(msg, type = 'success') {
  const tc = document.getElementById('toast-container');
  const colors = { success: '#198754', warning: '#f5a623', info: '#0dcaf0', danger: '#dc3545' };
  const el = document.createElement('div');
  el.style.cssText = `background:${colors[type]};color:#fff;padding:12px 18px;border-radius:10px;margin-bottom:8px;
                      box-shadow:0 4px 12px rgba(0,0,0,0.3);font-weight:600;max-width:320px;`;
  el.textContent = msg;
  tc.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------
async function refreshStats() {
  const res = await fetch('/api/stats');
  const s = await res.json();
  document.getElementById('stat-today').textContent  = s.sessions_today;
  document.getElementById('stat-streak').textContent = s.streak;
  document.getElementById('stat-week').textContent   = s.sessions_this_week;
  document.getElementById('stat-total').textContent  = s.total_sessions;
  const pct = (s.xp_in_level / s.xp_per_level * 100).toFixed(1);
  document.getElementById('xp-bar').style.width = pct + '%';
  document.getElementById('xp-label').textContent = `${s.xp_in_level} / ${s.xp_per_level} XP`;
  const lv = `Lv.${s.level}`;
  document.getElementById('level-label').textContent = lv;
  document.getElementById('nav-level').textContent   = lv;
}

async function refreshBadges() {
  const res = await fetch('/api/badges');
  const data = await res.json();
  const grid = document.getElementById('badges-grid');
  grid.innerHTML = '';
  data.all_badges.forEach(b => {
    const col = document.createElement('div');
    col.className = 'col-6 col-sm-4 col-md-3 col-lg-2';
    const earned = data.earned_keys.includes(b.key);
    col.innerHTML = `<div class="badge-card${earned ? ' earned' : ''}">
      <div style="font-size:1.8rem">${b.icon}</div>
      <div style="font-size:0.75rem;font-weight:700;margin-top:4px">${b.name}</div>
      <div style="font-size:0.65rem;color:#aaa;margin-top:4px">${b.desc}</div>
      ${earned ? '<div style="font-size:0.6rem;color:#f5a623;margin-top:4px">✓ 獲得済み</div>' : ''}
    </div>`;
    grid.appendChild(col);
  });
}

// ---------------------------------------------------------------------------
// Charts
// ---------------------------------------------------------------------------
let weeklyChart = null;
let monthlyChart = null;

const CHART_DEFAULTS = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: { ticks: { color: '#aaa' }, grid: { color: '#1e3a5f' } },
    y: { ticks: { color: '#aaa', stepSize: 1 }, grid: { color: '#1e3a5f' }, beginAtZero: true },
  },
};

async function refreshCharts() {
  const res = await fetch('/api/stats/charts');
  const data = await res.json();

  // Weekly
  const wCtx = document.getElementById('weeklyChart').getContext('2d');
  if (weeklyChart) weeklyChart.destroy();
  weeklyChart = new Chart(wCtx, {
    type: 'bar',
    data: {
      labels: data.weekly.labels,
      datasets: [{
        data: data.weekly.values,
        backgroundColor: 'rgba(233,69,96,0.7)',
        borderColor: '#e94560',
        borderWidth: 2,
        borderRadius: 6,
      }],
    },
    options: { ...CHART_DEFAULTS },
  });

  // Monthly
  const mCtx = document.getElementById('monthlyChart').getContext('2d');
  if (monthlyChart) monthlyChart.destroy();
  monthlyChart = new Chart(mCtx, {
    type: 'line',
    data: {
      labels: data.monthly.labels,
      datasets: [{
        data: data.monthly.values,
        borderColor: '#f5a623',
        backgroundColor: 'rgba(245,166,35,0.15)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#f5a623',
      }],
    },
    options: { ...CHART_DEFAULTS },
  });
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
(async () => {
  await refreshStats();
  await refreshCharts();
  await refreshBadges();
})();
</script>
</body>
</html>'''

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/session/complete', methods=['POST'])
def complete_session():
    data = request.get_json()
    session_type = data.get('session_type', 'work')
    duration = data.get('duration', 1500)

    conn = get_db()
    c = conn.cursor()

    # Record session
    c.execute(
        'INSERT INTO sessions (completed_at, session_type, duration, completed) VALUES (?, ?, ?, 1)',
        (datetime.now().isoformat(), session_type, duration),
    )
    conn.commit()

    # XP gain (work sessions earn more XP than break sessions)
    xp_gained = XP_PER_WORK_SESSION if session_type == 'work' else XP_PER_BREAK_SESSION
    c.execute('SELECT xp, level FROM user_stats WHERE id = 1')
    user = c.fetchone()
    old_level = user['level']
    new_xp = user['xp'] + xp_gained
    new_level = calculate_level(new_xp)
    c.execute('UPDATE user_stats SET xp = ?, level = ? WHERE id = 1', (new_xp, new_level))
    conn.commit()

    # Streak update
    new_streak = update_streak(conn)

    # Stats for badge check
    stats = get_stats(conn)

    # Badge check
    new_badges = check_and_award_badges(conn, stats)
    conn.close()

    return jsonify({
        'xp_gained': xp_gained,
        'new_xp': new_xp,
        'new_level': new_level,
        'leveled_up': new_level > old_level,
        'streak': new_streak,
        'new_badges': new_badges,
    })


@app.route('/api/stats')
def api_stats():
    conn = get_db()
    stats = get_stats(conn)
    conn.close()
    return jsonify(stats)


@app.route('/api/stats/charts')
def api_stats_charts():
    conn = get_db()
    c = conn.cursor()

    # Weekly: last 7 days
    weekly_labels = []
    weekly_values = []
    day_names = ['月', '火', '水', '木', '金', '土', '日']
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        c.execute(
            'SELECT COUNT(*) as cnt FROM sessions WHERE completed = 1 AND session_type = "work" AND date(completed_at) = ?',
            (d.isoformat(),),
        )
        weekly_labels.append(f'{d.month}/{d.day}({day_names[d.weekday()]})')
        weekly_values.append(c.fetchone()['cnt'])

    # Monthly: last 30 days grouped by week
    monthly_labels = []
    monthly_values = []
    for i in range(3, -1, -1):
        week_end = date.today() - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        c.execute(
            'SELECT COUNT(*) as cnt FROM sessions WHERE completed = 1 AND session_type = "work"'
            ' AND date(completed_at) BETWEEN ? AND ?',
            (week_start.isoformat(), week_end.isoformat()),
        )
        monthly_labels.append(f'{week_start.month}/{week_start.day}~')
        monthly_values.append(c.fetchone()['cnt'])

    conn.close()
    return jsonify({
        'weekly': {'labels': weekly_labels, 'values': weekly_values},
        'monthly': {'labels': monthly_labels, 'values': monthly_values},
    })


@app.route('/api/badges')
def api_badges():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT badge_key FROM badges')
    earned_keys = [row['badge_key'] for row in c.fetchall()]
    conn.close()
    all_badges = [{'key': b['key'], 'icon': b['icon'], 'name': b['name'], 'desc': b['desc']} for b in BADGE_DEFINITIONS]
    return jsonify({'all_badges': all_badges, 'earned_keys': earned_keys})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    init_db()
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, port=5000)
