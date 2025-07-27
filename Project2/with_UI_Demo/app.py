#!/usr/bin/env python3
"""
Slowloris Attack Live Demo Dashboard
===================================

Real-time monitoring dashboard for Slowloris attack demonstration.
Shows live graphs, statistics, and attack progress.

Author: Security Research Team
Purpose: Educational demonstration of DoS attacks
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import json
import subprocess
import requests
import psutil
import docker
from datetime import datetime, timedelta
import queue
import sys
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path to import attack modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'slowloris_demo_2024'
# Use threading mode for Windows compatibility
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global variables for monitoring
attack_process = None
monitoring_active = False
metrics_queue = queue.Queue()
docker_client = None

# Initialize Docker client
try:
    docker_client = docker.from_env()
    print("✅ Docker client initialized successfully")
except Exception as e:
    print(f"❌ Docker client initialization failed: {e}")

class AttackMonitor:
    def __init__(self):
        self.start_time = None
        self.attack_active = False
        self.docker_container = None
        self.metrics = {
            'connections': [],
            'response_times': [],
            'success_rate': [],
            'server_status': [],
            'network_traffic': [],
            'cpu_usage': [],
            'memory_usage': [],
            'attack_events': []
        }
        
    def start_monitoring(self):
        self.start_time = datetime.now()
        self.attack_active = True
        self.metrics = {k: [] for k in self.metrics.keys()}
        
    def stop_monitoring(self):
        self.attack_active = False
        
    def add_metric(self, metric_type, value, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        
        if metric_type in self.metrics:
            self.metrics[metric_type].append({
                'timestamp': timestamp.isoformat(),
                'value': value
            })
            
            # Keep only last 100 points for performance
            if len(self.metrics[metric_type]) > 100:
                self.metrics[metric_type] = self.metrics[metric_type][-100:]

monitor = AttackMonitor()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current attack and monitoring status"""
    global attack_process
    return jsonify({
        'attack_active': attack_process is not None and attack_process.poll() is None,
        'monitoring_active': monitoring_active,
        'attack_phase': monitor.attack_active,  # True during attack, False during recovery monitoring
        'start_time': monitor.start_time.isoformat() if monitor.start_time else None,
        'uptime': str(datetime.now() - monitor.start_time) if monitor.start_time else None,
        'docker_status': check_docker_server(),
        'phase_description': 'Attack in progress' if monitor.attack_active else 'Monitoring recovery' if monitoring_active else 'Idle'
    })

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics data"""
    return jsonify(monitor.metrics)

@app.route('/api/reset_metrics', methods=['POST'])
def reset_metrics():
    """Reset all dashboard metrics to start fresh"""
    try:
        print("🧹 Manually resetting all metrics...")
        monitor.metrics = {k: [] for k in monitor.metrics.keys()}
        monitor.attack_active = False
        monitor.start_time = None
        
        # If server is running, get fresh baseline
        if check_docker_server():
            server_test = test_server_response()
            if server_test['success']:
                monitor.add_metric('response_times', server_test['response_time'])
                monitor.add_metric('success_rate', 100.0)
                monitor.add_metric('connections', 0)
                monitor.add_metric('server_status', 1)
                monitor.add_metric('attack_events', {
                    'type': 'metrics_reset',
                    'message': 'Dashboard metrics reset - showing fresh server stats'
                })
        
        return jsonify({'success': True, 'message': 'Metrics reset successfully'})
    except Exception as e:
        print(f"❌ Error resetting metrics: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_attack', methods=['POST'])
def start_attack():
    """Start the Slowloris attack"""
    global attack_process, monitoring_active
    
    try:
        # Step 1: Check if Docker server is running, start if needed
        if not check_docker_server():
            print("🐳 Starting vulnerable Apache server...")
            if not start_docker_server():
                return jsonify({'success': False, 'error': 'Failed to start Docker server'})
            
            # Wait for server to be ready
            print("⏳ Waiting for server to start...")
            time.sleep(8)
        else:
            print("✅ Docker server already running on localhost:8080")
        
        # Step 2: Test server connectivity
        print("🔍 Testing server connectivity...")
        server_test = test_server_response()
        if not server_test['success']:
            return jsonify({'success': False, 'error': f'Server not responding: {server_test["status_code"]}'})
        
        # Step 3: Start attack process using the bridge script
        print("🎯 Starting Slowloris attack...")
        attack_script = os.path.join(os.path.dirname(__file__), 'attack_bridge.py')
        
        if not os.path.exists(attack_script):
            return jsonify({'success': False, 'error': f'Attack script not found: {attack_script}'})
        
        # Launch attack with localhost:8080 as target
        attack_process = subprocess.Popen([
            sys.executable, attack_script, 'localhost', '8080', '400'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Step 4: Activate attack monitoring (monitoring already running)
        monitor.attack_active = True  # This switches monitoring to attack mode
        
        # Add attack start event
        monitor.add_metric('attack_events', {
            'type': 'attack_start',
            'message': 'Slowloris attack initiated against localhost:8080'
        })
        
        # Monitoring is already active from system initialization
        
        print("✅ Attack started successfully!")
        return jsonify({'success': True, 'message': 'Slowloris attack started against localhost:8080'})
        
    except Exception as e:
        print(f"❌ Error starting attack: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop the live monitoring dashboard"""
    global monitoring_active
    try:
        monitoring_active = False
        monitor.stop_monitoring()
        print("📊 Live monitoring stopped")
        return jsonify({'success': True, 'message': 'Live monitoring stopped'})
    except Exception as e:
        print(f"❌ Error stopping monitoring: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_server', methods=['POST'])
def start_server():
    """Manually start the Docker server"""
    try:
        print("🐳 Manually starting Docker server...")
        if start_docker_server():
            return jsonify({'success': True, 'message': 'Docker server started on localhost:8080'})
        else:
            return jsonify({'success': False, 'error': 'Failed to start Docker server'})
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_server', methods=['POST'])
def stop_server():
    """Manually stop the Docker server"""
    try:
        print("🐳 Manually stopping Docker server...")
        stop_docker_server()
        return jsonify({'success': True, 'message': 'Docker server stopped'})
    except Exception as e:
        print(f"❌ Error stopping server: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_attack', methods=['POST'])
def stop_attack():
    """Stop the Slowloris attack but keep monitoring and server running"""
    global attack_process, monitoring_active
    
    try:
        # Terminate attack process ONLY
        if attack_process and attack_process.poll() is None:
            print("🛑 Stopping attack process...")
            attack_process.terminate()
            try:
                attack_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                attack_process.kill()
                attack_process.wait()
        
        # Stop attack but keep monitoring active and server running
        monitor.attack_active = False
        attack_process = None
        
        # NOTE: We DO NOT stop monitoring_active or Docker server
        # This allows continuous monitoring to show before/during/after comparison
        
        # Add stop event
        monitor.add_metric('attack_events', {
            'type': 'attack_stop',
            'message': 'Attack stopped - monitoring continues to show recovery'
        })
        
        print("✅ Attack stopped successfully!")
        print("📊 Server continues running on localhost:8080")
        print("📈 Monitoring continues to show server recovery")
        return jsonify({'success': True, 'message': 'Attack stopped - monitoring continues'})
        
    except Exception as e:
        print(f"❌ Error stopping attack: {e}")
        return jsonify({'success': False, 'error': str(e)})

def start_docker_server():
    """Start the vulnerable Apache server"""
    try:
        if not docker_client:
            print("❌ Docker client not available")
            return False
        
        # Stop existing container if running
        try:
            container = docker_client.containers.get('slowloris-demo')
            print("🧹 Stopping existing container...")
            container.stop()
            container.remove()
        except docker.errors.NotFound:
            pass
        except Exception as e:
            print(f"⚠️ Warning during cleanup: {e}")
        
        # Build image if needed
        dockerfile_path = os.path.dirname(os.path.dirname(__file__))
        print(f"🔨 Building Docker image from {dockerfile_path}...")
        
        try:
            docker_client.images.build(path=dockerfile_path, tag='slowloris-vulnerable', rm=True)
            print("✅ Docker image built successfully")
        except Exception as e:
            print(f"⚠️ Build warning (may already exist): {e}")
        
        # Start new container
        print("🚀 Starting vulnerable Apache server container...")
        container = docker_client.containers.run(
            'slowloris-vulnerable',
            name='slowloris-demo',
            ports={'80/tcp': 8080},
            detach=True,
            remove=True  # Auto-remove when stopped
        )
        
        monitor.docker_container = container
        
        # Add event to metrics
        monitor.add_metric('attack_events', {
            'type': 'server_start',
            'message': 'Vulnerable Apache server started on localhost:8080'
        })
        
        print("✅ Apache server started on http://localhost:8080")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start Docker server: {e}")
        return False

def stop_docker_server():
    """Stop the vulnerable Apache server"""
    try:
        if not docker_client:
            return True
            
        container = docker_client.containers.get('slowloris-demo')
        container.stop()
        # Container will auto-remove due to remove=True flag
        
        monitor.docker_container = None
        
        # Add event to metrics
        monitor.add_metric('attack_events', {
            'type': 'server_stop',
            'message': 'Vulnerable Apache server stopped'
        })
        
        print("✅ Docker server stopped")
        return True
        
    except docker.errors.NotFound:
        print("ℹ️ Container already stopped/removed")
        return True
    except Exception as e:
        print(f"❌ Failed to stop Docker server: {e}")
        return False

def check_docker_server():
    """Check if Docker server is running"""
    try:
        if not docker_client:
            return False
        container = docker_client.containers.get('slowloris-demo')
        return container.status == 'running'
    except:
        return False

def test_server_response():
    """Test server response time and status"""
    try:
        start_time = time.time()
        response = requests.get('http://localhost:8080', timeout=10)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            'success': True,
            'status_code': response.status_code,
            'response_time': response_time
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'status_code': 'TIMEOUT',
            'response_time': 10000
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'status_code': 'CONNECTION_ERROR',
            'response_time': 0
        }
    except Exception as e:
        return {
            'success': False,
            'status_code': f'ERROR: {str(e)}',
            'response_time': 0
        }

def get_system_metrics():
    """Get system resource usage"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_used': memory.used,
            'memory_total': memory.total
        }
    except Exception as e:
        return {
            'cpu_usage': 0,
            'memory_usage': 0,
            'memory_used': 0,
            'memory_total': 0
        }

def monitoring_loop():
    """Main monitoring loop that collects metrics"""
    global monitoring_active
    
    connection_count = 0
    success_count = 0
    total_requests = 0
    
    print("👀 Starting monitoring loop...")
    
    # Start with fresh baseline - test server immediately
    if not monitor.attack_active:  # Only if not in attack mode
        server_test = test_server_response()
        if server_test['success']:
            monitor.add_metric('response_times', server_test['response_time'])
            monitor.add_metric('success_rate', 100.0)
            monitor.add_metric('connections', 0)
            monitor.add_metric('server_status', 1)
            print(f"📊 Fresh baseline: {server_test['response_time']:.0f}ms response, 100% success rate")
    
    while monitoring_active:
        try:
            # Test server response
            server_test = test_server_response()
            total_requests += 1
            
            if server_test['success']:
                success_count += 1
                monitor.add_metric('response_times', server_test['response_time'])
                monitor.add_metric('server_status', 1)
            else:
                monitor.add_metric('response_times', server_test['response_time'])
                monitor.add_metric('server_status', 0)
            
            # Calculate success rate (percentage of HTTP requests that complete successfully)
            # 100% = server responding normally to all requests
            # Lower % = server struggling due to Slowloris attack (timeouts, connection errors)
            success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 100
            monitor.add_metric('success_rate', success_rate)
            
            # Simulate connection count based on attack progress
            # In reality, this would come from the attack script output
            if monitor.attack_active and total_requests > 3:  # Give attack time to establish
                # Gradually increase connections, then maintain
                if total_requests < 15:
                    connection_count = min(connection_count + 25, 400)
                else:
                    # Fluctuate around 400 connections
                    connection_count = max(350, min(400, connection_count + random.randint(-20, 20)))
            else:
                # When attack is stopped, gradually reduce connections to 0
                # This shows the recovery process in real-time
                connection_count = max(connection_count - 30, 0)
            
            monitor.add_metric('connections', connection_count)
            
            # Get system metrics
            sys_metrics = get_system_metrics()
            monitor.add_metric('cpu_usage', sys_metrics['cpu_usage'])
            monitor.add_metric('memory_usage', sys_metrics['memory_usage'])
            
            # Calculate network traffic based on connections and response issues
            network_traffic = connection_count * 0.8 + (100 - success_rate) * 3
            monitor.add_metric('network_traffic', network_traffic)
            
            # Emit real-time data to connected clients
            socketio.emit('metrics_update', {
                'connections': connection_count,
                'success_rate': success_rate,
                'response_time': server_test['response_time'],
                'server_status': server_test['success'],
                'cpu_usage': sys_metrics['cpu_usage'],
                'memory_usage': sys_metrics['memory_usage'],
                'network_traffic': network_traffic,
                'timestamp': datetime.now().isoformat()
            })
            
            # Log significant events based on attack status
            if monitor.attack_active:
                # During attack phase
                if success_rate < 50 and total_requests > 5:
                    monitor.add_metric('attack_events', {
                        'type': 'dos_detected',
                        'message': f'DoS effect detected - Success rate: {success_rate:.1f}%'
                    })
                    print(f"🔥 DoS Effect: Success rate dropped to {success_rate:.1f}% - Server under attack!")
                elif success_rate > 80:
                    print(f"⚡ Attack Impact: Success rate at {success_rate:.1f}% - Attack in progress")
            else:
                # Normal server operation or post-attack recovery
                if total_requests > 3:
                    if success_rate > 95:
                        print(f"✅ Server Healthy: Success rate is {success_rate:.1f}% - Normal operation")
                    elif success_rate > 80:
                        monitor.add_metric('attack_events', {
                            'type': 'recovery_progress',
                            'message': f'Server recovering - Success rate: {success_rate:.1f}%'
                        })
                        print(f"🔄 Recovery: Success rate recovering to {success_rate:.1f}%")
                    else:
                        print(f"📊 Baseline: Success rate at {success_rate:.1f}% - Monitoring normal server")
            
            time.sleep(3)  # Update every 3 seconds
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            time.sleep(1)

import random

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('👤 Client connected to dashboard')
    emit('status', {'message': 'Connected to Slowloris Demo Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('👤 Client disconnected from dashboard')

@socketio.on('request_metrics')
def handle_metrics_request():
    """Handle request for current metrics"""
    emit('metrics_data', monitor.metrics)

def initialize_system():
    """Initialize the system by starting Docker server and starting fresh monitoring"""
    print("🔧 Initializing system...")
    
    # Reset all metrics to start completely fresh
    print("🧹 Resetting all metrics to start fresh...")
    monitor.metrics = {k: [] for k in monitor.metrics.keys()}
    monitor.attack_active = False
    monitor.start_time = datetime.now()  # Start monitoring time immediately
    
    # Start Docker server automatically and keep it running
    print("🐳 Starting vulnerable Apache server...")
    if start_docker_server():
        print("✅ Apache server started successfully on http://localhost:8080")
        print("🌐 You can test the server by visiting http://localhost:8080")
        
        # Add initial fresh server event
        monitor.add_metric('attack_events', {
            'type': 'server_start',
            'message': 'Fresh Apache server started - monitoring baseline performance'
        })
        
        # Test initial server response to get baseline metrics
        time.sleep(3)  # Give server time to fully start
        server_test = test_server_response()
        if server_test['success']:
            monitor.add_metric('response_times', server_test['response_time'])
            monitor.add_metric('success_rate', 100.0)  # Fresh server should be 100%
            monitor.add_metric('connections', 0)  # No attack connections
            monitor.add_metric('server_status', 1)
            print(f"✅ Server baseline: {server_test['response_time']:.0f}ms response time")
        
        # Start monitoring immediately to show baseline
        global monitoring_active
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_loop)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        print("📊 Live monitoring started - showing baseline server performance")
        
    else:
        print("❌ Failed to start Apache server automatically")
        print("💡 You can manually start it using the dashboard controls")

if __name__ == '__main__':
    print("🚀 Starting Slowloris Demo Dashboard...")
    print("📊 Dashboard URL: http://localhost:5000")
    print("🎯 Target: localhost:8080 (Apache server in Docker)")
    print("🔧 Using threading mode for Windows compatibility")
    print("=" * 60)
    
    # Initialize system
    initialize_system()
    
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 