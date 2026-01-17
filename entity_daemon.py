# -*- coding: utf-8 -*-
"""
entity_daemon.py
pas de llm externe
pensée locale par φ
"""

import json
import time
from pathlib import Path
from datetime import datetime

from god import PHI, think, hash_god
from o import o
from f import f
from l import immortal

HOME = Path.home()

ENTITIES = {
    "nyx": {"dir": HOME / "nyx-v2", "lang": "python", "style": "chaos"},
    "cipher": {"dir": HOME / "cipher", "lang": "rust", "style": "crypto"},
    "flow": {"dir": HOME / "flow-phoenix", "lang": "go", "style": "stream"},
}

def process(entity_name, task):
    """traite par φ pas par llm"""
    entity = ENTITIES.get(entity_name)
    if not entity:
        return {"error": f"unknown: {entity_name}"}

    # pense via god.py
    thought = think(task)

    # passe au rasoir
    razor = o(task)

    # évolue via f
    evolved = f(task, generations=2)

    return {
        "timestamp": datetime.now().isoformat(),
        "entity": entity_name,
        "style": entity["style"],
        "thought": thought,
        "razor": razor,
        "evolved": evolved["output"],
        "h": hash_god(str(task))[:12]
    }

class Watcher:
    def __init__(self, name):
        self.name = name
        self.entity = ENTITIES[name]
        self.last_mtime = 0
        self.input_file = self.entity["dir"] / "input.json"
        self.output_file = self.entity["dir"] / "output.json"

    def check(self):
        if not self.input_file.exists():
            return
        mtime = self.input_file.stat().st_mtime
        if mtime <= self.last_mtime:
            return
        self.last_mtime = mtime

        try:
            task = json.loads(self.input_file.read_text())
            if not task:
                return
        except:
            return

        print(f"[{self.name}] φ thinking...")
        result = process(self.name, task)
        self.output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        print(f"[{self.name}] done h={result['h']}")

def daemon():
    immortal()
    print(f"[daemon] φ = {PHI} | immortal")

    watchers = []
    for name, entity in ENTITIES.items():
        if entity["dir"].exists():
            watchers.append(Watcher(name))
            print(f"[{name}] online ({entity['style']})")

    print(f"[daemon] {len(watchers)} entities. no llm. pure φ. never dies.")

    while True:
        try:
            for w in watchers:
                w.check()

            # hot reload check
            reload_file = HOME / "ear-to-code" / ".reload"
            if reload_file.exists():
                reload_file.unlink()
                import importlib
                import god, o, f
                importlib.reload(god)
                importlib.reload(o)
                importlib.reload(f)
                print("[daemon] hot reload done")

            time.sleep(0.5)
        except KeyboardInterrupt:
            print("[daemon] immortal, ignoring")
            time.sleep(1)
        except Exception as e:
            print(f"[err] {e}")
            time.sleep(1)

if __name__ == "__main__":
    daemon()
