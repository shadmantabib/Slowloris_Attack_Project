#!/usr/bin/env python3
"""
Vulnerable Server Demo Starter
==============================
Starts the vulnerable HTTP server and attack dashboard.
"""

import subprocess
import time
import signal
import sys
import os

def start_vulnerable_server():
    """Start the vulnerable HTTP server"""
    return subprocess.Popen([
        sys.executable, 'vulnerable_server.py'
    ], cwd=os.path.dirname(__file__))

def start_dashboard():
    """Start the attack dashboard"""
    return subprocess.Popen([
        sys.executable, 'attack_dashboard.py'
    ], cwd=os.path.dirname(__file__))

def main():
    print("🎯 Starting Vulnerable Server Slowloris Demo")
    print("=" * 60)
    
    # Start vulnerable server
    print("💀 Starting vulnerable HTTP server on localhost:8080...")
    server_process = start_vulnerable_server()
    time.sleep(2)
    
    # Start dashboard
    print("📊 Starting attack dashboard on localhost:4000...")
    dashboard_process = start_dashboard()
    time.sleep(2)
    
    print("✅ Both services started successfully!")
    print("=" * 60)
    print("🌐 Vulnerable Server: http://localhost:8080")
    print("📊 Attack Dashboard: http://localhost:4000")
    print("=" * 60)
    print("📖 Demo Instructions:")
    print("1. Open http://localhost:8080 - Server is VULNERABLE (red)")
    print("2. Open http://localhost:4000 - Attack dashboard")
    print("3. Launch Slowloris attack - Server will become unresponsive!")
    print("4. Toggle protection - Server turns PROTECTED (green)")
    print("5. Launch attack again - Server survives!")
    print("=" * 60)
    print("Press Ctrl+C to stop both services")
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down demo...")
        server_process.terminate()
        dashboard_process.terminate()
        
        # Wait for graceful shutdown
        try:
            server_process.wait(timeout=5)
            dashboard_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            dashboard_process.kill()
        
        print("✅ Demo stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Wait for processes
    try:
        while True:
            if server_process.poll() is not None:
                print("❌ Vulnerable server stopped unexpectedly")
                break
            if dashboard_process.poll() is not None:
                print("❌ Dashboard stopped unexpectedly")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 