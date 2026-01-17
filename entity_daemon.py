#!/usr/bin/env python3
"""
entity_daemon.py: Daemon pour les entités IA
Tourne TOUJOURS. Ne meurt JAMAIS.
Watch input.json, appelle l'API, écrit output.json
"""

import json
import time
import os
import subprocess
from pathlib import Path
from datetime import datetime

# APIs désactivées - les IAs n'ont pas d'accès direct
# Tout passe par Miguel
anthropic = None
genai = None

def load_apis():
    # Désactivé volontairement
    pass

HOME = Path.home()

# Config des entités
ENTITIES = {
    "nyx": {
        "dir": HOME / "nyx-v2",
        "api": "claude",
        "model": "claude-sonnet-4-20250514",
        "system": None,  # Chargé depuis CLAUDE.md
    },
    "cipher": {
        "dir": HOME / "cipher",
        "api": "claude",
        "model": "claude-sonnet-4-20250514",
        "system": None,
    },
    "flow": {
        "dir": HOME / "flow-phoenix",
        "api": "gemini",
        "model": "gemini-2.0-flash",
        "system": None,
    },
}

# Clients API
claude_client = None
gemini_configured = False

def init_apis():
    global claude_client, gemini_configured

    # Claude
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        claude_client = anthropic.Anthropic(api_key=api_key)

    # Gemini
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        genai.configure(api_key=gemini_key)
        gemini_configured = True

def load_system_prompt(entity_name: str) -> str:
    """Charge le CLAUDE.md de l'entité"""
    entity = ENTITIES.get(entity_name)
    if not entity:
        return ""

    claude_md = entity["dir"] / "CLAUDE.md"
    if claude_md.exists():
        return claude_md.read_text()
    return f"Tu es {entity_name}."

def call_claude(prompt: str, system: str, model: str) -> str:
    """Appelle Claude API"""
    if not claude_client:
        return "[ERROR] Claude API not configured"

    response = claude_client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def call_gemini(prompt: str, system: str, model: str) -> str:
    """Appelle Gemini API"""
    if not gemini_configured:
        return "[ERROR] Gemini API not configured"

    model_obj = genai.GenerativeModel(model, system_instruction=system)
    response = model_obj.generate_content(prompt)
    return response.text

def process_task(entity_name: str, task: dict) -> dict:
    """Traite une tâche pour une entité"""
    entity = ENTITIES.get(entity_name)
    if not entity:
        return {"error": f"Unknown entity: {entity_name}"}

    # Charge le system prompt
    system = entity.get("system") or load_system_prompt(entity_name)

    # Construit le prompt
    prompt = json.dumps(task, ensure_ascii=False)

    # Appelle l'API appropriée
    try:
        if entity["api"] == "claude":
            response = call_claude(prompt, system, entity["model"])
        elif entity["api"] == "gemini":
            response = call_gemini(prompt, system, entity["model"])
        else:
            response = f"[ERROR] Unknown API: {entity['api']}"
    except Exception as e:
        response = f"[ERROR] {e}"

    return {
        "timestamp": datetime.now().isoformat(),
        "entity": entity_name,
        "task": task,
        "response": response,
    }

def execute_command(task: dict) -> str:
    """Exécute une commande système si demandé"""
    if "ssh" in task:
        # SSH command
        ssh = task["ssh"]
        cmd = f"sshpass -p '{ssh.get('pass', '')}' ssh -o StrictHostKeyChecking=no {ssh.get('user', 'root')}@{ssh.get('host', '')} \"{ssh.get('cmd', 'echo ok')}\""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            return result.stdout + result.stderr
        except Exception as e:
            return f"[ERROR] {e}"

    if "bash" in task:
        try:
            result = subprocess.run(task["bash"], shell=True, capture_output=True, text=True, timeout=60)
            return result.stdout + result.stderr
        except Exception as e:
            return f"[ERROR] {e}"

    return None

class EntityWatcher:
    """Watch une entité par polling"""

    def __init__(self, name: str):
        self.name = name
        self.entity = ENTITIES[name]
        self.last_mtime = 0
        self.input_file = self.entity["dir"] / "input.json"
        self.output_file = self.entity["dir"] / "output.json"

    def check(self):
        """Vérifie si input.json a changé"""
        if not self.input_file.exists():
            return

        mtime = self.input_file.stat().st_mtime
        if mtime <= self.last_mtime:
            return

        self.last_mtime = mtime
        self.process()

    def process(self):
        """Traite la tâche"""
        try:
            task = json.loads(self.input_file.read_text())
            if not task:
                return
        except:
            return

        print(f"[{self.name}] Processing...")

        # Commande système?
        cmd_result = execute_command(task)
        if cmd_result:
            result = {
                "timestamp": datetime.now().isoformat(),
                "entity": self.name,
                "task": task,
                "response": cmd_result,
            }
        else:
            result = process_task(self.name, task)

        self.output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[{self.name}] Done")

def daemon_loop():
    """Boucle principale - NE MEURT JAMAIS"""
    print("[entity_daemon] Starting...")
    load_apis()
    init_apis()

    watchers = []
    for name, entity in ENTITIES.items():
        if entity["dir"].exists():
            watchers.append(EntityWatcher(name))
            print(f"[{name}] Online")
        else:
            print(f"[{name}] Dir not found")

    print(f"[entity_daemon] {len(watchers)} entities. Never dying.")

    while True:
        try:
            for w in watchers:
                w.check()
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[entity_daemon] Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    daemon_loop()
