#!/usr/bin/env python3
"""
launch_all.py: Lance tout le système ear-to-code
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

HOME = Path.home()
EAR_DIR = HOME / "ear-to-code"
VENV_PYTHON = EAR_DIR / "venv" / "bin" / "python"

processes = []

def launch(name: str, script: str, args: list = None):
    """Lance un script en background"""
    args = args or []
    cmd = [str(VENV_PYTHON), str(EAR_DIR / script)] + args

    print(f"[LAUNCH] {name}...")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    processes.append((name, proc))
    return proc

def cleanup(sig=None, frame=None):
    """Kill all processes"""
    print("\n[LAUNCH] Arrêt...")
    for name, proc in processes:
        print(f"[LAUNCH] Killing {name}")
        proc.terminate()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("=" * 60)
    print("EAR-TO-CODE - SYSTÈME COMPLET")
    print("=" * 60)

    # 1. Feedback loop (socket + HTTP)
    launch("feedback", "feedback.py", ["--server"])
    time.sleep(0.5)

    # 2. Plaquettes (auto-repair)
    launch("plaquettes", "plaquettes.py", ["--watch"])
    time.sleep(0.5)

    # 3. Audio (ear)
    launch("ear", "ear.py", ["--system"])
    time.sleep(0.5)

    # 4. Nyx watcher
    nyx_watcher = HOME / "nyx-v2" / "watcher.py"
    if nyx_watcher.exists():
        launch("nyx", str(nyx_watcher))

    print("=" * 60)
    print("TOUS LES SYSTÈMES ACTIFS")
    print("=" * 60)
    print("Processes:")
    for name, proc in processes:
        print(f"  [{proc.pid}] {name}")
    print("=" * 60)
    print("Ctrl+C pour arrêter")
    print("=" * 60)
    print()

    # Stream tous les outputs
    import select

    while True:
        readable = []
        for name, proc in processes:
            if proc.stdout and proc.poll() is None:
                readable.append((name, proc.stdout))

        if not readable:
            time.sleep(0.1)
            continue

        for name, stdout in readable:
            try:
                line = stdout.readline()
                if line:
                    print(f"[{name}] {line.rstrip()}")
            except:
                pass

        time.sleep(0.05)

if __name__ == "__main__":
    main()
