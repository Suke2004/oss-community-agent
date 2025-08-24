#!/usr/bin/env python3
"""
Full System Launcher for OSS Community Agent

Runs both the frontend (Streamlit UI) and backend (Portia Agent) simultaneously
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
import threading

def run_frontend():
    """Run the Streamlit frontend"""
    ui_dir = Path(__file__).parent / "apps" / "ui"
    os.chdir(ui_dir)
    
    print("🎨 Starting Frontend (Streamlit UI)...")
    try:
        subprocess.run([
            "python3", "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--theme.primaryColor", "#6366f1"
        ])
    except KeyboardInterrupt:
        print("🎨 Frontend stopped")

def run_backend():
    """Run the Portia agent backend"""
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("🤖 Starting Backend (Portia Agent)...")
    try:
        # Set environment variables for the agent
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        subprocess.run([
            "python3", "apps/agent/main.py"
        ], env=env)
    except KeyboardInterrupt:
        print("🤖 Backend stopped")

def main():
    """Main function to run both frontend and backend"""
    
    # Load environment variables from root .env file
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Environment variables loaded from .env")
        except ImportError:
            print("⚠️  python-dotenv not available")
    else:
        print("⚠️  No .env file found, using system environment variables")
    
    print("🚀 Starting OSS Community Agent - Full System")
    print("=" * 60)
    print("Frontend: http://localhost:8501")
    print("Backend: Portia Agent running in background")
    print("Press Ctrl+C to stop both services")
    print("=" * 60)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend a moment to start
    time.sleep(2)
    
    try:
        # Run frontend in main thread (so it opens browser)
        run_frontend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down OSS Community Agent...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("🛑 Full system stopped")

if __name__ == "__main__":
    main()
