"""One-command launcher for Medical Report AI"""
import sys
import os
import subprocess
import signal
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
os.chdir(ROOT_DIR)
os.environ["PYTHONPATH"] = str(ROOT_DIR)


def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║             🏥 MEDICAL REPORT AI v2.0                   ║
    ║     Chest X-Ray Analysis & Diagnostic Report System     ║
    ╚══════════════════════════════════════════════════════════╝
    """)


def start_backend():
    print("🚀 Starting backend server...")
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=ROOT_DIR,
    )


def start_frontend():
    print("🚀 Starting frontend server...")
    return subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app/main.py",
         "--server.port", "8501", "--server.address", "0.0.0.0"],
        cwd=ROOT_DIR,
    )


def main():
    print_banner()

    backend = start_backend()
    time.sleep(3)
    frontend = start_frontend()

    print("\n✅ Services started!")
    print(f"   📊 Frontend:  http://localhost:8501")
    print(f"   🔌 Backend:   http://localhost:8000")
    print(f"   📚 API Docs:  http://localhost:8000/docs")
    print("\n   Press Ctrl+C to stop all services.\n")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("✅ All services stopped.")


if __name__ == "__main__":
    main()
