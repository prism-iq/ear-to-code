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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import anthropic
import google.generativeai as genai

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

class InputHandler(FileSystemEventHandler):
    """Watch les input.json des entités"""

    def __init__(self, entity_name: str):
        self.entity_name = entity_name
        self.entity = ENTITIES[entity_name]
        self.last_processed = 0

    def on_modified(self, event):
        if not event.src_path.endswith("input.json"):
            return

        # Évite les doubles triggers
        now = time.time()
        if now - self.last_processed < 1:
            return
        self.last_processed = now

        self.process_input()

    def process_input(self):
        input_file = self.entity["dir"] / "input.json"
        output_file = self.entity["dir"] / "output.json"

        if not input_file.exists():
            return

        try:
            task = json.loads(input_file.read_text())
        except:
            return

        print(f"[{self.entity_name}] Processing task...")

        # Vérifie si c'est une commande à exécuter
        cmd_result = execute_command(task)
        if cmd_result:
            result = {
                "timestamp": datetime.now().isoformat(),
                "entity": self.entity_name,
                "task": task,
                "response": cmd_result,
            }
        else:
            # Sinon appelle l'API
            result = process_task(self.entity_name, task)

        # Écrit le résultat
        output_file.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"[{self.entity_name}] Done. Output: {output_file}")

def daemon_loop():
    """Boucle principale - NE MEURT JAMAIS"""
    print("[entity_daemon] Starting...")
    init_apis()

    observers = []

    for name, entity in ENTITIES.items():
        if not entity["dir"].exists():
            print(f"[{name}] Directory not found: {entity['dir']}")
            continue

        # Crée input.json si n'existe pas
        input_file = entity["dir"] / "input.json"
        if not input_file.exists():
            input_file.write_text("{}")

        handler = InputHandler(name)
        observer = Observer()
        observer.schedule(handler, str(entity["dir"]), recursive=False)
        observer.start()
        observers.append(observer)
        print(f"[{name}] Watching {entity['dir']}")

    print("[entity_daemon] All entities online. Never dying.")

    # Boucle infinie
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("[entity_daemon] Stopping...")
            for obs in observers:
                obs.stop()
            for obs in observers:
                obs.join()
            break
        except Exception as e:
            # Ne meurt JAMAIS
            print(f"[entity_daemon] Error (continuing): {e}")
            time.sleep(5)

if __name__ == "__main__":
    daemon_loop()
