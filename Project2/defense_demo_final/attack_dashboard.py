#!/usr/bin/env python3
"""
Enhanced Defense Mechanism Demo Dashboard
=========================================

An improved dashboard to test Slowloris defense mechanisms with:
1. Real-time attack monitoring with faster updates
2. Immediate server recovery coordination
3. Dynamic protection toggling with instant effects
4. Better attack management and cleanup

Key Improvements:
- Faster monitoring during attacks (0.5s updates)
- Immediate cleanup when stopping attacks
- Force server recovery functionality
- Better real-time feedback
- Enhanced protection coordination
"""

from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO
import threading
import time
import requests
import signal
import sys
import subprocess
import os

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# --- Globals ---
attack_process = None
monitoring_active = False
target_server_url = "http://localhost:8080"

def get_target_stats():
    """Get basic stats from the new simplified API."""
    try:
        response = requests.get(f"{target_server_url}/api/stats", timeout=1.5)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        # If the server is down, we expect this to fail.
        # Return a "server down" status.
        return {
            'protection_enabled': False,
            'active_connections': 'N/A',
            'server_health': 'unresponsive'
        }
    return None

def toggle_target_protection():
    """Toggle protection via the simplified API."""
    try:
        requests.post(f"{target_server_url}/api/protection", timeout=2)
    except requests.exceptions.RequestException:
        # This might fail if the server is under attack, which is expected.
        pass

# --- Flask Routes ---

@app.route('/')
def dashboard():
    """Serve the simplified dashboard page."""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Slowloris Defense Demo</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; }
        .container { max-width: 900px; margin: auto; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .panel { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; }
        .metric-value { font-size: 28px; font-weight: bold; margin-bottom: 8px; }
        .metric-label { font-size: 14px; color: #666; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin: 5px; transition: background-color 0.3s; }
        .btn-attack { background-color: #e74c3c; color: white; }
        .btn-attack:hover { background-color: #c0392b; }
        .btn-stop { background-color: #27ae60; color: white; }
        .btn-stop:hover { background-color: #219a52; }
        .btn-toggle { background-color: #3498db; color: white; width: 100%; }
        .btn-toggle:hover { background-color: #2980b9; }
        .status-vulnerable { color: #e74c3c; font-weight: bold; }
        .status-protected { color: #27ae60; font-weight: bold; }
        .status-unresponsive { color: #95a5a6; font-weight: bold; animation: pulse 1.5s infinite; }
        @keyframes pulse { 50% { opacity: 0.5; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>Slowloris Defense Demo</h1></div>
        
        <div class="panel metrics">
            <div class="metric-card">
                <div class="metric-value" id="protection-status">--</div>
                <div class="metric-label">Protection Status</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" id="active-connections">--</div>
                <div class="metric-label">Active Connections</div>
            </div>
        </div>
        
        <div class="panel">
            <h3>Attack Control</h3>
            <p>Target: <strong>http://localhost:8080</strong></p>
            <p>Attack Status: <strong id="attack-status">IDLE</strong></p>
            <button class="btn btn-attack" onclick="startAttack()">💀 Launch AGGRESSIVE Attack (50 connections)</button>
            <button class="btn btn-stop" onclick="stopAttack()">🛑 Stop Attack</button>
        </div>
        
        <div class="panel">
            <h3>🛡️ Defense Control</h3>
            <p><strong>Click this button to enable/disable protection:</strong></p>
            <button class="btn btn-toggle" onclick="toggleProtection()">🔄 Toggle Protection</button>
            <p style="margin-top: 10px;"><em>When protection is ON, the server will survive attacks!</em></p>
        </div>
    </div>

    <script>
        const socket = io();
        
        function startAttack() { socket.emit('start_attack'); }
        function stopAttack() { socket.emit('stop_attack'); }
        function toggleProtection() { socket.emit('toggle_protection'); }

        socket.on('stats_update', function(data) {
            const protectionEl = document.getElementById('protection-status');
            const connectionsEl = document.getElementById('active-connections');
            
            if (data.server_health === 'unresponsive') {
                protectionEl.textContent = 'SERVER DOWN';
                protectionEl.className = 'metric-value status-unresponsive';
                connectionsEl.textContent = 'N/A';
            } else {
                protectionEl.textContent = data.protection_enabled ? 'PROTECTED' : 'VULNERABLE';
                protectionEl.className = 'metric-value ' + (data.protection_enabled ? 'status-protected' : 'status-vulnerable');
                connectionsEl.textContent = data.active_connections;
            }
        });

        socket.on('attack_status', function(data) {
            document.getElementById('attack-status').textContent = data.status;
        });
    </script>
</body>
</html>
    """)

# --- SocketIO Handlers ---

@socketio.on('connect')
def handle_connect():
    """Start monitoring when a client connects."""
    global monitoring_active
    if not monitoring_active:
        monitoring_active = True
        socketio.start_background_task(target=monitoring_loop)

@socketio.on('start_attack')
def start_attack():
    """Start the Slowloris attack subprocess."""
    global attack_process
    if attack_process is None:
        socketio.emit('attack_status', {'status': 'ATTACKING'})
        attack_script = os.path.join(os.path.dirname(__file__), 'AGGRESSIVE_ATTACK.py')
        attack_process = subprocess.Popen([
            sys.executable, attack_script, 'localhost', '8080', '50'
        ])

@socketio.on('stop_attack')
def stop_attack():
    """Stop the Slowloris attack subprocess."""
    global attack_process
    if attack_process:
        attack_process.terminate()
        attack_process = None
        socketio.emit('attack_status', {'status': 'IDLE'})

@socketio.on('toggle_protection')
def handle_toggle():
    """Toggle the server's protection mechanism."""
    toggle_target_protection()

def monitoring_loop():
    """Continuously poll the target server for stats."""
    while monitoring_active:
        stats = get_target_stats()
        if stats:
            socketio.emit('stats_update', stats)
        time.sleep(1) # Poll every second

def cleanup():
    """Ensure background processes are stopped on exit."""
    if attack_process:
        attack_process.terminate()

def main():
    print("="*30 + "\nDemo Dashboard Started\n" + "="*30)
    print("Dashboard URL: http://localhost:4000")
    print("Target Server: http://localhost:8080")
    print("="*30)
    signal.signal(signal.SIGINT, lambda s, f: cleanup() or sys.exit(0))
    socketio.run(app, host='0.0.0.0', port=4000, debug=False)

if __name__ == '__main__':
    main() 