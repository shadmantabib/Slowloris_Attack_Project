#!/usr/bin/env python3
"""
VULNERABLE HTTP SERVER
=====================
A simple HTTP server that is vulnerable to Slowloris attacks.
Can be protected with defense mechanisms.
"""

import socket
import threading
import time
import signal
import sys
from datetime import datetime
import json

class VulnerableHTTPServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.protection_enabled = False
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': datetime.now()
        }
        self.active_connections = {}
        self.connection_lock = threading.Lock()
        
    def start(self):
        """Start the vulnerable server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)  # Small backlog - makes it vulnerable
        self.running = True
        
        print("🎯 Starting Vulnerable HTTP Server")
        print("=" * 50)
        print(f"🌐 Server URL: http://{self.host}:{self.port}")
        print("💀 Server is VULNERABLE to Slowloris attacks!")
        print(f"🛡️ Protection: {'ENABLED' if self.protection_enabled else 'DISABLED'}")
        print("=" * 50)
        
        try:
            while self.running:
                client_socket, addr = self.socket.accept()
                # Handle each connection in a separate thread
                thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, addr)
                )
                thread.daemon = True
                thread.start()
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            if self.socket:
                self.socket.close()
    
    def handle_client(self, client_socket, addr):
        """Handle individual client connections"""
        client_ip = addr[0]
        
        # Track connection
        with self.connection_lock:
            if client_ip not in self.active_connections:
                self.active_connections[client_ip] = 0
            self.active_connections[client_ip] += 1
            total_connections = sum(self.active_connections.values())
        
        try:
            # VULNERABILITY: If not protected and too many connections
            if not self.protection_enabled and total_connections > 3:
                print(f"💀 VULNERABILITY: {total_connections} connections from {client_ip} - server overwhelmed!")
                # Simulate server being overwhelmed
                time.sleep(20)  # Long delay
                self.stats['failed_requests'] += 1
                client_socket.close()
                return
            
            # PROTECTION: If protected, handle quickly
            if self.protection_enabled and total_connections > 10:
                print(f"🛡️ PROTECTION: Blocking excessive connections from {client_ip}")
                response = "HTTP/1.1 429 Too Many Requests\r\n\r\nProtection Active"
                client_socket.send(response.encode())
                client_socket.close()
                return
            
            # Receive request with timeout
            client_socket.settimeout(5.0 if self.protection_enabled else 30.0)
            request = client_socket.recv(4096).decode()
            
            if not request:
                return
                
            self.stats['total_requests'] += 1
            
            # Parse request
            lines = request.split('\r\n')
            if not lines:
                return
                
            request_line = lines[0]
            method, path, _ = request_line.split() if len(request_line.split()) == 3 else ('GET', '/', 'HTTP/1.1')
            
            # Route handling
            if path == '/':
                response = self.get_home_page()
            elif path == '/api/stats':
                response = self.get_stats_api()
            elif path == '/api/protection' and method == 'POST':
                response = self.toggle_protection_api()
            else:
                response = self.get_404_page()
            
            # Send response
            client_socket.send(response.encode())
            self.stats['successful_requests'] += 1
            
        except socket.timeout:
            print(f"⏰ Connection from {client_ip} timed out")
            self.stats['failed_requests'] += 1
        except Exception as e:
            print(f"❌ Error handling {client_ip}: {e}")
            self.stats['failed_requests'] += 1
        finally:
            # Remove connection
            with self.connection_lock:
                if client_ip in self.active_connections:
                    self.active_connections[client_ip] -= 1
                    if self.active_connections[client_ip] <= 0:
                        del self.active_connections[client_ip]
            
            try:
                client_socket.close()
            except:
                pass
    
    def get_home_page(self):
        """Generate the main page"""
        uptime = datetime.now() - self.stats['start_time']
        total_connections = sum(self.active_connections.values())
        
        if self.protection_enabled:
            theme_color = "#27ae60"
            status_text = "🛡️ PROTECTED"
            message = "Server is protected and handling attacks!"
        else:
            theme_color = "#e74c3c"
            status_text = "💀 VULNERABLE"
            message = "Server is vulnerable to Slowloris attacks!"
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Vulnerable HTTP Server Demo</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: {theme_color}; color: white; }}
        .container {{ background: rgba(0,0,0,0.2); padding: 30px; border-radius: 15px; }}
        .status {{ padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center; font-size: 24px; font-weight: bold; background: rgba(0,0,0,0.3); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: rgba(0,0,0,0.2); padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; margin-bottom: 10px; }}
        .stat-label {{ font-size: 14px; opacity: 0.8; }}
        .control-btn {{ background: rgba(0,0,0,0.3); color: white; padding: 15px 30px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer; margin: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Vulnerable HTTP Server Demo</h1>
        <div class="status">{status_text}</div>
        <div class="stats">
            <div class="stat-card"><div class="stat-value">{self.stats['total_requests']}</div><div class="stat-label">Total Requests</div></div>
            <div class="stat-card"><div class="stat-value">{self.stats['successful_requests']}</div><div class="stat-label">Successful</div></div>
            <div class="stat-card"><div class="stat-value">{self.stats['failed_requests']}</div><div class="stat-label">Failed</div></div>
            <div class="stat-card"><div class="stat-value">{total_connections}</div><div class="stat-label">Active Connections</div></div>
        </div>
        <div style="text-align: center;">
            <button class="control-btn" onclick="toggleProtection()">{'Disable' if self.protection_enabled else 'Enable'} Protection</button>
            <button class="control-btn" onclick="window.location.reload()">Refresh</button>
        </div>
        <p style="text-align: center; margin-top: 30px;">
            <em>{message}</em>
        </p>
    </div>
    <script>
        function toggleProtection() {{
            fetch('/api/protection', {{ method: 'POST' }}).then(() => window.location.reload());
        }}
    </script>
</body>
</html>"""
        
        return f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
    
    def get_stats_api(self):
        """API endpoint for stats"""
        stats_data = {
            'protection_enabled': self.protection_enabled,
            'active_connections': sum(self.active_connections.values()),
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'server_health': 'protected' if self.protection_enabled else 'vulnerable'
        }
        
        json_data = json.dumps(stats_data)
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(json_data)}\r\n\r\n{json_data}"
    
    def toggle_protection_api(self):
        """Toggle protection mechanism"""
        self.protection_enabled = not self.protection_enabled
        print(f"🔄 Protection toggled: {'ENABLED' if self.protection_enabled else 'DISABLED'}")
        
        response_data = json.dumps({
            'success': True,
            'protection_enabled': self.protection_enabled
        })
        
        return f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response_data)}\r\n\r\n{response_data}"
    
    def get_404_page(self):
        """404 error page"""
        html = "<html><body><h1>404 Not Found</h1></body></html>"
        return f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\nContent-Length: {len(html)}\r\n\r\n{html}"
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            self.socket.close()

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    print('\n🛑 Shutting down vulnerable server...')
    server.stop()
    sys.exit(0)

if __name__ == '__main__':
    server = VulnerableHTTPServer()
    signal.signal(signal.SIGINT, signal_handler)
    server.start() 