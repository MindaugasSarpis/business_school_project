from flask import Flask, request, render_template, redirect, url_for, session
import threading
import time
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Main account to observe others
MAIN_ACCOUNT = "kornelamarchevka"
MAIN_PASSWORD =   # can be hidden via .env later

# Simple login credentials for dashboard
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# In-memory database
tracked_accounts = {}
account_snapshots = {}
unfollowers_log = {}

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', accounts=tracked_accounts, logs=unfollowers_log)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return "Invalid login", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/add_account', methods=['POST'])
def add_account():
    username = request.form['username']
    target = request.form['target']

    tracked_accounts[username] = {
        'password': 'fake-password',  # not needed for viewing targets
        'target': target,
        'last_checked': None
    }
    return redirect(url_for('index'))

@app.route('/check_now/<username>')
def check_now(username):
    if username in tracked_accounts:
        run_check(username)
    return redirect(url_for('index'))

def run_check(username):
    from random import sample, randint
    dummy_followers = [f'user{i}' for i in range(100)]
    new_followers = sample(dummy_followers, randint(80, 100))

    target = tracked_accounts[username]['target']
    old_snapshot = account_snapshots.get(target, set())
    new_snapshot = set(new_followers)

    unfollowed = old_snapshot - new_snapshot
    account_snapshots[target] = new_snapshot

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if unfollowed:
        unfollowers_log.setdefault(target, []).append({
            'timestamp': timestamp,
            'unfollowers': list(unfollowed)
        })

    tracked_accounts[username]['last_checked'] = timestamp

def scheduled_checks():
    while True:
        for username in tracked_accounts:
            run_check(username)
        time.sleep(2 * 24 * 60 * 60)  # every 2 days

threading.Thread(target=scheduled_checks, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
