#!/usr/bin/env python3
"""talk.py: Chat direct avec les IAs"""
import json, time, os, sys, threading
from pathlib import Path
from datetime import datetime

HOME = Path.home()
ENTITIES = {"nyx": HOME/"nyx-v2", "cipher": HOME/"cipher", "flow": HOME/"flow-phoenix"}
COLORS = {"nyx": "\033[95m", "cipher": "\033[96m", "flow": "\033[93m", "you": "\033[92m", "sys": "\033[90m", "r": "\033[0m"}

def watch_reactions():
    seen = {}
    while True:
        for name, d in ENTITIES.items():
            for f in ["reaction.json", "chat_out.json"]:
                p = d / f
                if p.exists():
                    try:
                        mt = p.stat().st_mtime
                        if seen.get(str(p), 0) < mt:
                            data = json.loads(p.read_text())
                            msg = data.get("reaction") or data.get("message", "")
                            if msg:
                                t = datetime.now().strftime("%H:%M:%S")
                                print(f"\r{COLORS['sys']}[{t}]{COLORS['r']} {COLORS[name]}{name}{COLORS['r']}: {msg}")
                                print(f"{COLORS['you']}>{COLORS['r']} ", end="", flush=True)
                            seen[str(p)] = mt
                    except: pass
        time.sleep(0.5)

def send(msg):
    event = {"ts": datetime.now().isoformat(), "from": "user", "message": msg}
    for d in ENTITIES.values():
        try:
            (d / "chat_in.json").write_text(json.dumps(event))
        except: pass

print(f"{COLORS['sys']}=== TALK ==={COLORS['r']}")
print(f"{COLORS['sys']}Type to talk. Ctrl+C to quit.{COLORS['r']}\n")

threading.Thread(target=watch_reactions, daemon=True).start()

try:
    while True:
        msg = input(f"{COLORS['you']}>{COLORS['r']} ")
        if msg.strip():
            send(msg.strip())
except (KeyboardInterrupt, EOFError):
    print(f"\n{COLORS['sys']}bye{COLORS['r']}")
