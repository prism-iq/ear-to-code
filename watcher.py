#!/usr/bin/env python3
"""
Watcher: Monitor ear-to-code heartbeat
Alerts if the ear dies
"""
import json
import time
import sys
import subprocess
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent / "logs"
STATE_FILE = LOG_DIR / "ear_state.json"
HEARTBEAT_TIMEOUT = 15  # seconds before considered dead


def check_alive() -> tuple[bool, dict]:
    """Check if ear is alive based on state file"""
    if not STATE_FILE.exists():
        return False, {"error": "No state file"}

    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)

        ts = datetime.fromisoformat(state['timestamp'])
        age = (datetime.now() - ts).total_seconds()

        if age > HEARTBEAT_TIMEOUT:
            return False, {"error": f"Stale heartbeat ({age:.1f}s old)", "state": state}

        return True, state

    except Exception as e:
        return False, {"error": str(e)}


def restart_ear():
    """Try to restart ear-to-code"""
    print("[WATCHER] Attempting restart...")
    try:
        # Try systemd first
        result = subprocess.run(
            ["systemctl", "--user", "restart", "ear-to-code"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[WATCHER] Restarted via systemd")
            return True
    except:
        pass

    # Manual restart
    try:
        subprocess.Popen(
            [sys.executable, str(Path(__file__).parent / "ear.py"), "--system"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        print("[WATCHER] Started manually")
        return True
    except Exception as e:
        print(f"[WATCHER] Failed to restart: {e}")
        return False


def main():
    print("[WATCHER] Monitoring ear-to-code...")
    print(f"[WATCHER] Heartbeat timeout: {HEARTBEAT_TIMEOUT}s")

    consecutive_failures = 0

    while True:
        alive, info = check_alive()

        if alive:
            consecutive_failures = 0
            song = info.get('current_song', {})
            if song:
                title = song.get('title', '?')
                print(f"[WATCHER] Alive | Playing: {title}")
            else:
                print(f"[WATCHER] Alive | Silent")
        else:
            consecutive_failures += 1
            print(f"[WATCHER] DEAD! {info.get('error')} (failure #{consecutive_failures})")

            if consecutive_failures >= 2:
                restart_ear()
                consecutive_failures = 0

        time.sleep(5)


if __name__ == "__main__":
    main()
