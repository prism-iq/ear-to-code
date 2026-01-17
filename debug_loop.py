#!/usr/bin/env python3
"""
debug_loop.py: Boucle de feedback pour debug
Montre tout ce qui se passe en temps réel
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
import threading
from git_daemon import sync_now

HOME = Path.home()

WATCH_FILES = [
    ("nyx", HOME / "nyx-v2" / "input.json"),
    ("nyx_out", HOME / "nyx-v2" / "output.json"),
    ("cipher", HOME / "cipher" / "input.json"),
    ("flow", HOME / "flow-phoenix" / "input.json"),
    ("ear_log", HOME / "ear-to-code" / "logs"),
]

last_mtimes = {}


def watch_file(name: str, path: Path):
    """Surveille un fichier et affiche les changements"""
    global last_mtimes

    if not path.exists():
        return

    if path.is_dir():
        # Surveille le dernier fichier du dossier
        files = list(path.glob("*.jsonl"))
        if not files:
            return
        path = max(files, key=lambda p: p.stat().st_mtime)

    key = str(path)
    mtime = path.stat().st_mtime

    if key not in last_mtimes:
        last_mtimes[key] = mtime
        return

    if mtime > last_mtimes[key]:
        last_mtimes[key] = mtime
        try:
            with open(path, 'r') as f:
                content = f.read()
                # Prend la dernière ligne si jsonl
                if path.suffix == '.jsonl':
                    lines = content.strip().split('\n')
                    if lines:
                        content = lines[-1]

            data = json.loads(content) if content.strip() else {}
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{ts}] [{name}] {path.name}")
            print(f"  {json.dumps(data, ensure_ascii=False, indent=2)[:200]}")
        except Exception as e:
            print(f"[{name}] Error: {e}")


def debug_loop():
    """Boucle principale de debug"""
    print("=" * 50)
    print("DEBUG FEEDBACK LOOP")
    print("=" * 50)
    print("Watching:")
    for name, path in WATCH_FILES:
        status = "OK" if path.exists() else "NOT FOUND"
        print(f"  [{status}] {name}: {path}")
    print("=" * 50)
    print("Ctrl+C to stop\n")

    while True:
        try:
            for name, path in WATCH_FILES:
                watch_file(name, path)
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[DEBUG] Stopped")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(1)


def commit_push():
    """Appelable par tout le système"""
    ok, msg = sync_now()
    if ok:
        print(f"[git] synced: {msg}")
    return ok


if __name__ == "__main__":
    debug_loop()
