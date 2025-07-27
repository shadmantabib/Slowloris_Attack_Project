#!/usr/bin/env python3
"""
Slowloris Attack Demo Startup Script
===================================

This script sets up and launches the complete Slowloris attack demonstration
including the Flask dashboard, Docker container management, and monitoring.

Usage: python start_demo.py
"""

import os
import sys
import subprocess
import time
import webbrowser
import signal
import threading
from pathlib import Path

class DemoLauncher:
    def __init__(self):
        self.processes = []
        self.demo_running = False
        
    def print_banner(self):
        """Print the demo banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        SLOWLORIS ATTACK LIVE DEMO                           ║
║                          Educational Demonstration                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 Features:                                                                ║
║     • Real-time attack monitoring dashboard                                  ║
║     • Live graphs and statistics                                             ║
║     • Interactive attack controls                                            ║
║     • Docker-based vulnerable server                                         ║
║     • WebSocket-powered real-time updates                                    ║
║                                                                              ║
║  ⚠️  WARNING: FOR EDUCATIONAL PURPOSES ONLY                                 ║
║      Use only on systems you own or have permission to test                 ║
║                                                                              ║
║  📚 Learning Objectives:                                                     ║
║     • Understanding DoS attack mechanics                                     ║
║     • Network security vulnerability assessment                              ║
║     • Real-time monitoring and analysis                                      ║
║     • Defense strategy development                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ Python 3.7 or higher is required")
            return False
        print("✅ Python version check passed")
        
        # Check if Docker is available
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ Docker is not available or not working")
                return False
            print("✅ Docker check passed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Docker is not installed or not accessible")
            return False
        
        # Check if required files exist
        required_files = [
            'app.py',
            'templates/dashboard.html',
            'requirements.txt',
            '../Dockerfile',
            '../enhanced_attack.py'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                print(f"❌ Required file missing: {file_path}")
                return False
        print("✅ Required files check passed")
        
        return True
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing Python dependencies...")
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"❌ Failed to install dependencies: {result.stderr}")
                return False
            
            print("✅ Dependencies installed successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Dependency installation timed out")
            return False
        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
            return False
    
    def setup_docker_image(self):
        """Build the Docker image for the vulnerable server"""
        print("🐳 Setting up Docker environment...")
        
        try:
            # Change to parent directory for Docker build
            parent_dir = os.path.dirname(os.getcwd())
            
            print("   Building vulnerable Apache server image...")
            result = subprocess.run([
                'docker', 'build', '-t', 'slowloris-vulnerable', parent_dir
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                print(f"❌ Failed to build Docker image: {result.stderr}")
                return False
            
            print("✅ Docker image built successfully")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Docker image build timed out")
            return False
        except Exception as e:
            print(f"❌ Error building Docker image: {e}")
            return False
    
    def cleanup_existing_containers(self):
        """Clean up any existing demo containers"""
        print("🧹 Cleaning up existing containers...")
        
        try:
            # Stop existing container if running
            subprocess.run(['docker', 'stop', 'slowloris-demo'], 
                         capture_output=True, timeout=30)
            
            # Remove existing container
            subprocess.run(['docker', 'rm', 'slowloris-demo'], 
                         capture_output=True, timeout=30)
            
            print("✅ Cleanup completed")
            return True
            
        except subprocess.TimeoutExpired:
            print("⚠️  Container cleanup timed out")
            return True  # Continue anyway
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
            return True  # Continue anyway
    
    def start_dashboard(self):
        """Start the Flask dashboard"""
        print("🚀 Starting dashboard server...")
        
        try:
            # Start Flask app
            process = subprocess.Popen([
                sys.executable, 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(process)
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print("✅ Dashboard server started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Dashboard failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
            return False
    
    def open_browser(self):
        """Open the dashboard in the default web browser"""
        print("🌐 Opening dashboard in browser...")
        
        try:
            # Wait a moment to ensure server is fully ready
            time.sleep(2)
            
            # Open browser
            webbrowser.open('http://localhost:5000')
            print("✅ Dashboard opened in browser")
            
        except Exception as e:
            print(f"⚠️  Could not open browser automatically: {e}")
            print("   Please manually open: http://localhost:5000")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received shutdown signal ({signum})")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def monitor_processes(self):
        """Monitor running processes"""
        print("👀 Monitoring demo processes...")
        print("   Press Ctrl+C to stop the demo")
        print("   Dashboard URL: http://localhost:5000")
        print("-" * 60)
        
        try:
            while self.demo_running:
                time.sleep(1)
                
                # Check if any processes have died
                for process in self.processes:
                    if process.poll() is not None:
                        print("⚠️  A demo process has stopped unexpectedly")
                        
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
    
    def shutdown(self):
        """Shutdown all demo components"""
        print("\n🔄 Shutting down demo components...")
        self.demo_running = False
        
        # Terminate Flask processes
        for process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        # Clean up Docker containers
        self.cleanup_existing_containers()
        
        print("✅ Demo shutdown complete")
    
    def run_demo(self):
        """Run the complete demo setup"""
        self.print_banner()
        
        # Get user confirmation
        try:
            input("Press Enter to start the demo setup (Ctrl+C to cancel)...")
        except KeyboardInterrupt:
            print("\n❌ Demo cancelled by user")
            return False
        
        print("\n🚀 Starting Slowloris Attack Demo Setup...")
        print("=" * 60)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Check requirements
        if not self.check_requirements():
            print("❌ Requirements check failed. Please fix the issues and try again.")
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            print("❌ Dependency installation failed")
            return False
        
        # Setup Docker
        if not self.setup_docker_image():
            print("❌ Docker setup failed")
            return False
        
        # Cleanup existing containers
        self.cleanup_existing_containers()
        
        # Start dashboard
        if not self.start_dashboard():
            print("❌ Dashboard startup failed")
            return False
        
        # Open browser
        browser_thread = threading.Thread(target=self.open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Set demo as running
        self.demo_running = True
        
        print("\n" + "=" * 60)
        print("🎉 DEMO SETUP COMPLETE!")
        print("=" * 60)
        print("📊 Dashboard: http://localhost:5000")
        print("🎯 Use the dashboard to control the attack demonstration")
        print("📚 Educational features:")
        print("   • Real-time attack monitoring")
        print("   • Live performance graphs")
        print("   • Interactive controls")
        print("   • Detailed statistics")
        print("=" * 60)
        
        # Monitor until shutdown
        self.monitor_processes()
        
        return True

def main():
    """Main function"""
    launcher = DemoLauncher()
    
    try:
        success = launcher.run_demo()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted")
        launcher.shutdown()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        launcher.shutdown()
        sys.exit(1)
    finally:
        launcher.shutdown()

if __name__ == "__main__":
    main() 