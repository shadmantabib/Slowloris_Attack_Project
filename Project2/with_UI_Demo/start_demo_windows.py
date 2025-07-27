#!/usr/bin/env python3
"""
Slowloris Attack Demo Startup Script - Windows Version
====================================================

Windows-optimized version of the demo launcher with better
compatibility for Python 3.12 and Windows systems.

Usage: python start_demo_windows.py
"""

import os
import sys
import subprocess
import time
import webbrowser
import signal
import threading
from pathlib import Path
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class WindowsDemoLauncher:
    def __init__(self):
        self.processes = []
        self.demo_running = False
        
    def print_banner(self):
        """Print the demo banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   SLOWLORIS ATTACK LIVE DEMO - WINDOWS                      ║
║                          Educational Demonstration                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 Features:                                                                ║
║     • Real-time attack monitoring dashboard                                  ║
║     • Live graphs and statistics                                             ║
║     • Interactive attack controls                                            ║
║     • Docker-based vulnerable server                                         ║
║     • Windows-optimized WebSocket updates                                    ║
║                                                                              ║
║  ⚠️  WARNING: FOR EDUCATIONAL PURPOSES ONLY                                 ║
║      Use only on systems you own or have permission to test                 ║
║                                                                              ║
║  🖥️  Windows Optimizations:                                                 ║
║     • Threading-based WebSocket (no greenlet issues)                        ║
║     • Pre-compiled package compatibility                                     ║
║     • Windows Docker Desktop integration                                     ║
║     • PowerShell-friendly commands                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking Windows system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 7):
            print("❌ Python 3.7 or higher is required")
            return False
        
        if sys.version_info >= (3, 12):
            print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected (using Windows-compatible packages)")
        else:
            print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} check passed")
        
        # Check if Docker Desktop is available
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10, shell=True)
            if result.returncode != 0:
                print("❌ Docker is not available. Please install Docker Desktop for Windows")
                print("   Download from: https://www.docker.com/products/docker-desktop")
                return False
            print("✅ Docker Desktop check passed")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Docker Desktop is not installed or not in PATH")
            print("   Please install Docker Desktop for Windows")
            return False
        
        # Check if Docker Desktop is running
        try:
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10, shell=True)
            if result.returncode != 0:
                print("❌ Docker Desktop is not running. Please start Docker Desktop")
                return False
            print("✅ Docker Desktop is running")
        except:
            print("❌ Cannot connect to Docker. Please ensure Docker Desktop is running")
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
        """Install Python dependencies with Windows optimizations"""
        print("📦 Installing Python dependencies (Windows-optimized)...")
        
        # Try Windows-specific requirements first
        requirements_file = 'requirements_windows.txt' if os.path.exists('requirements_windows.txt') else 'requirements.txt'
        
        try:
            # Use --only-binary to avoid compilation issues
            cmd = [
                sys.executable, '-m', 'pip', 'install', 
                '-r', requirements_file,
                '--only-binary=all',  # Prefer pre-compiled wheels
                '--upgrade'
            ]
            
            print(f"   Using requirements file: {requirements_file}")
            print("   Installing pre-compiled packages to avoid compilation...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            if result.returncode != 0:
                print(f"⚠️  Standard installation failed, trying alternative approach...")
                
                # Try installing core packages individually
                core_packages = [
                    'Flask==2.3.3',
                    'Flask-SocketIO==5.3.6', 
                    'requests==2.31.0',
                    'psutil==5.9.5',
                    'docker==6.1.3'
                ]
                
                for package in core_packages:
                    try:
                        subprocess.run([
                            sys.executable, '-m', 'pip', 'install', 
                            package, '--only-binary=all'
                        ], check=True, timeout=60)
                        print(f"   ✅ Installed {package}")
                    except:
                        print(f"   ⚠️  Failed to install {package}, will try without it")
                
                print("✅ Core dependencies installed (some optional packages may be missing)")
                return True
            
            print("✅ All dependencies installed successfully")
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
            ], capture_output=True, text=True, timeout=300, shell=True)
            
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
                         capture_output=True, timeout=30, shell=True)
            
            # Remove existing container
            subprocess.run(['docker', 'rm', 'slowloris-demo'], 
                         capture_output=True, timeout=30, shell=True)
            
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
            # Start Flask app with Windows-friendly settings
            process = subprocess.Popen([
                sys.executable, 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
               creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            
            self.processes.append(process)
            
            # Wait a moment for the server to start
            time.sleep(5)
            
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
            time.sleep(3)
            
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
        if hasattr(signal, 'SIGTERM'):
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
            input("Press Enter to start the Windows demo setup (Ctrl+C to cancel)...")
        except KeyboardInterrupt:
            print("\n❌ Demo cancelled by user")
            return False
        
        print("\n🚀 Starting Slowloris Attack Demo Setup (Windows)...")
        print("=" * 60)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Check requirements
        if not self.check_requirements():
            print("❌ Requirements check failed. Please fix the issues and try again.")
            print("\n💡 Common solutions:")
            print("   • Install Docker Desktop from https://www.docker.com/products/docker-desktop")
            print("   • Ensure Docker Desktop is running")
            print("   • Use Python 3.7+ (3.12 recommended)")
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            print("❌ Dependency installation failed")
            print("\n💡 Try manual installation:")
            print("   pip install Flask Flask-SocketIO requests psutil docker")
            return False
        
        # Setup Docker
        if not self.setup_docker_image():
            print("❌ Docker setup failed")
            print("   Please ensure Docker Desktop is running and try again")
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
        print("🎉 WINDOWS DEMO SETUP COMPLETE!")
        print("=" * 60)
        print("📊 Dashboard: http://localhost:5000")
        print("🎯 Use the dashboard to control the attack demonstration")
        print("📚 Windows-optimized features:")
        print("   • Threading-based WebSocket (no compilation needed)")
        print("   • Pre-compiled package installation")
        print("   • Docker Desktop integration")
        print("   • Windows-friendly process management")
        print("=" * 60)
        
        # Monitor until shutdown
        self.monitor_processes()
        
        return True

def main():
    """Main function"""
    launcher = WindowsDemoLauncher()
    
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