#!/usr/bin/env python3
"""
Git Daemon - Les IAs maintiennent le repo
Auto-commit, auto-push, zero intervention humaine
"""

import subprocess
import time
import hashlib
import json
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).parent
WATCH_INTERVAL = 60  # secondes
STATE_FILE = REPO / "logs" / "git_state.json"
IGNORE = {'.git', '__pycache__', 'logs', 'souls', 'golem', '.pyc'}

def get_files_hash():
    """Hash de tous les fichiers trackés"""
    h = hashlib.sha256()
    for f in sorted(REPO.rglob('*')):
        if f.is_file() and not any(i in str(f) for i in IGNORE):
            try:
                h.update(f.read_bytes())
            except:
                pass
    return h.hexdigest()[:16]

def git(*args):
    """Execute git command"""
    r = subprocess.run(['git', '-C', str(REPO)] + list(args),
                       capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr

def get_diff_summary():
    """Résumé des changements"""
    ok, out = git('diff', '--stat', 'HEAD')
    if not ok or not out.strip():
        ok, out = git('status', '--porcelain')

    lines = out.strip().split('\n') if out.strip() else []
    files = []
    for line in lines[:10]:
        if line.strip():
            # Extract filename from various git output formats
            parts = line.split()
            if parts:
                files.append(parts[-1].split('/')[-1])

    return files

def auto_commit():
    """Commit automatique si changements"""
    git('add', '-A')

    ok, status = git('status', '--porcelain')
    if not status.strip():
        return False, "no changes"

    files = get_diff_summary()
    timestamp = datetime.now().strftime("%H:%M")

    if len(files) == 1:
        msg = f"update {files[0]}"
    elif len(files) <= 3:
        msg = f"update {', '.join(files)}"
    else:
        msg = f"sync {len(files)} files"

    msg = f"[auto] {msg} @ {timestamp}"

    ok, out = git('commit', '-m', msg)
    return ok, msg

def auto_push():
    """Push automatique"""
    ok, out = git('push')
    return ok, out

def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except:
        return {"last_hash": "", "last_push": 0}

def save_state(state):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state))

def daemon_loop():
    """Boucle principale du daemon"""
    print(f"[git_daemon] watching {REPO}")
    state = load_state()

    while True:
        try:
            current_hash = get_files_hash()

            if current_hash != state["last_hash"]:
                ok, msg = auto_commit()
                if ok:
                    print(f"[git_daemon] committed: {msg}")

                    ok, out = auto_push()
                    if ok:
                        print(f"[git_daemon] pushed")
                        state["last_push"] = time.time()
                    else:
                        print(f"[git_daemon] push failed: {out[:100]}")

                    state["last_hash"] = current_hash
                    save_state(state)

            time.sleep(WATCH_INTERVAL)

        except KeyboardInterrupt:
            print("[git_daemon] stopped")
            break
        except Exception as e:
            print(f"[git_daemon] error: {e}")
            time.sleep(WATCH_INTERVAL)

# API pour les autres modules
def sync_now():
    """Force sync immédiat"""
    ok, msg = auto_commit()
    if ok:
        auto_push()
    return ok, msg

if __name__ == "__main__":
    daemon_loop()
