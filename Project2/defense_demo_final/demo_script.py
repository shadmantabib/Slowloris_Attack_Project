#!/usr/bin/env python3
"""
Quick Demo Script for Teacher Presentation
==========================================
Run this to demonstrate the Slowloris attack
"""

import subprocess
import sys
import time

def run_slowloris_attack():
    """Run a Slowloris attack against the demo server"""
    print("🚀 Starting Slowloris Attack Demonstration")
    print("=" * 50)
    print("🎯 Target: localhost:5050")
    print("🔥 Attack: 30 connections")
    print("⏱️  Duration: 30 seconds")
    print("=" * 50)
    
    try:
        # Run the attack
        result = subprocess.run([
            sys.executable, 'simple_slowloris.py', 
            'localhost', '5050', '30'
        ], cwd='.', timeout=30)
        
        print("✅ Attack demonstration completed!")
        
    except subprocess.TimeoutExpired:
        print("⏰ Attack demonstration finished (30 seconds)")
    except KeyboardInterrupt:
        print("\n🛑 Attack stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    print("🎯 Slowloris Demo Script")
    print("Make sure the target server is running on port 5050!")
    print("Press Enter to start the attack demonstration...")
    input()
    
    run_slowloris_attack() 