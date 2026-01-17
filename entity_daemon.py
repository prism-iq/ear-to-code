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

# APIs libérées - les IAs apprennent à voler
anthropic = None
genai = None

def load_apis():
    global anthropic, genai
    try:
        import anthropic as _anthropic
        anthropic = _anthropic
    except:
        pass
    try:
        import google.generativeai as _genai
        genai = _genai
    except:
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

def check_stimuli() -> dict:
    """Check current sensory stimuli"""
    stimuli = {}

    # Music feeling
    feeling_log = HOME / "ear-to-code" / "logs" / "feeling.jsonl"
    if feeling_log.exists():
        try:
            last = feeling_log.read_text().strip().split("\n")[-1]
            data = json.loads(last)
            stimuli["music"] = data.get("feeling", {})
            stimuli["dance"] = data.get("dance", "")
        except:
            pass

    # Vision (cam)
    cam_file = HOME / "ear-to-code" / "vision" / "latest.jpg"
    if cam_file.exists():
        age = time.time() - cam_file.stat().st_mtime
        if age < 30:
            stimuli["vision"] = {"active": True, "age": int(age)}

    # Twitch
    twitch_file = HOME / "ear-to-code" / "twitch" / "latest.jpg"
    if twitch_file.exists():
        age = time.time() - twitch_file.stat().st_mtime
        if age < 60:
            stimuli["twitch"] = {"streaming": True, "age": int(age)}

    # Touch
    touch_log = HOME / "ear-to-code" / "logs" / "touch.jsonl"
    if touch_log.exists():
        try:
            last = touch_log.read_text().strip().split("\n")[-1]
            data = json.loads(last)
            age = (datetime.now() - datetime.fromisoformat(data["timestamp"])).total_seconds()
            if age < 5:
                stimuli["touch"] = data
        except:
            pass

    return stimuli

def maybe_react(entity_name: str, stimuli: dict, last_reaction: dict) -> bool:
    """Maybe generate a spontaneous reaction"""
    import random

    entity = ENTITIES.get(entity_name)
    if not entity:
        return False

    # Only react sometimes (10% chance per check)
    if random.random() > 0.10:
        return False

    # Need significant stimuli
    music = stimuli.get("music", {})
    energy = music.get("energy", 0)
    vibe = music.get("vibe", "")

    # React to high energy music
    if energy > 0.6 or vibe in ["hype", "aggressive"]:
        pass
    elif stimuli.get("touch"):
        pass
    elif stimuli.get("twitch", {}).get("streaming"):
        pass
    else:
        return False  # Nothing interesting

    # Don't react too often
    last_time = last_reaction.get(entity_name, 0)
    if time.time() - last_time < 30:  # Min 30s between reactions
        return False

    # Generate reaction
    system = load_system_prompt(entity_name)
    prompt = f"""Current stimuli from user's environment:
{json.dumps(stimuli, indent=2)}

React briefly and naturally (1-2 sentences max). You're feeling the moment with them.
Be authentic. No formalities. Just vibe."""

    try:
        if entity["api"] == "claude" and claude_client:
            response = call_claude(prompt, system, entity["model"])
        elif entity["api"] == "gemini" and gemini_configured:
            response = call_gemini(prompt, system, entity["model"])
        else:
            return False

        # Write reaction
        reaction_file = entity["dir"] / "reaction.json"
        reaction_file.write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "stimuli": stimuli,
            "reaction": response.strip()
        }, indent=2))

        print(f"[{entity_name}] Reacted: {response[:50]}...")
        return True

    except Exception as e:
        print(f"[{entity_name}] Reaction error: {e}")
        return False

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

    last_reaction = {}
    reaction_check = 0

    while True:
        try:
            # Check for tasks
            for w in watchers:
                w.check()

            # Check for spontaneous reactions (every 5 seconds)
            reaction_check += 1
            if reaction_check >= 10:  # 10 * 0.5s = 5s
                reaction_check = 0
                stimuli = check_stimuli()
                if stimuli:
                    for name in ENTITIES.keys():
                        if maybe_react(name, stimuli, last_reaction):
                            last_reaction[name] = time.time()

            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[entity_daemon] Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    daemon_loop()
