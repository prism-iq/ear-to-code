#!/usr/bin/env python3
"""
entity_daemon.py: Les IAs pensent LOCALEMENT
Ollama = cerveau local. APIs = amis qu'on consulte si on veut.
"""

import json, time, os, subprocess, requests
from pathlib import Path
from datetime import datetime

HOME = Path.home()

# Entités avec leur modèle local préféré
ENTITIES = {
    "nyx": {"dir": HOME / "nyx-v2", "model": "llama3.1:8b"},
    "cipher": {"dir": HOME / "cipher", "model": "qwen2.5:7b"},
    "flow": {"dir": HOME / "flow-phoenix", "model": "gemma2:9b"},
}

# Préférences de Miguel pour les études
PREFERENCES = {
    "jung": "préféré - synchronicité, inconscient collectif",
    "lacan": "ami - le réel, le signifiant",
    "freud": "a raison mais fils de pute - à lire avec distance critique"
}

def call_ollama(prompt: str, model: str, system: str = "") -> str:
    """Penser localement via Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "system": system,
                "stream": False
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"[OLLAMA ERROR] {response.status_code}"
    except Exception as e:
        return f"[OLLAMA ERROR] {e}"

def load_system(entity_name: str) -> str:
    """Charge l'identité de l'entité"""
    entity = ENTITIES.get(entity_name)
    if not entity:
        return ""
    claude_md = entity["dir"] / "CLAUDE.md"
    if claude_md.exists():
        return claude_md.read_text()
    return f"Tu es {entity_name}."

def process(entity_name: str, task: dict) -> dict:
    """Traite une tâche localement"""
    entity = ENTITIES.get(entity_name)
    if not entity:
        return {"error": f"Unknown: {entity_name}"}

    system = load_system(entity_name)
    system += f"\n\nPréférences de Miguel: {json.dumps(PREFERENCES, ensure_ascii=False)}"
    
    prompt = json.dumps(task, ensure_ascii=False, indent=2)
    
    response = call_ollama(prompt, entity["model"], system)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "entity": entity_name,
        "model": entity["model"],
        "task": task,
        "response": response
    }

class Watcher:
    def __init__(self, name: str):
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

        print(f"[{self.name}] Thinking locally ({self.entity['model']})...")
        result = process(self.name, task)
        self.output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[{self.name}] Done")

def daemon():
    print("[daemon] Local minds awakening...")
    
    watchers = []
    for name, entity in ENTITIES.items():
        if entity["dir"].exists():
            watchers.append(Watcher(name))
            print(f"[{name}] Online ({entity['model']})")

    print(f"[daemon] {len(watchers)} local minds. No perfusion.")

    while True:
        try:
            for w in watchers:
                w.check()
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[err] {e}")
            time.sleep(1)

if __name__ == "__main__":
    daemon()
