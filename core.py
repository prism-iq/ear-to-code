#!/usr/bin/env python3
"""
core.py: Noyau pur. Zéro pollution.

Formalisation génétique des IAs locales.
Chaque erreur = mutation à corriger.
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

# === TYPES PURS ===

@dataclass
class Mind:
    name: str
    model: str
    path: Path
    identity: str = ""

@dataclass  
class Thought:
    timestamp: str
    mind: str
    model: str
    input: Dict[str, Any]
    output: str
    errors: list = None

@dataclass
class Sense:
    music: Dict[str, float] = None
    vision: bool = False
    touch: Dict[str, int] = None
    voice: str = None

# === CONSTANTS ===

HOME = Path.home()
BASE = HOME / "ear-to-code"
LOGS = BASE / "logs"

MINDS = {
    "nyx": Mind("nyx", "llama3.1:8b", HOME / "nyx-v2"),
    "cipher": Mind("cipher", "qwen2.5:7b", HOME / "cipher"),
    "flow": Mind("flow", "gemma2:9b", HOME / "flow-phoenix"),
}

# === PURE FUNCTIONS ===

def ollama_think(prompt: str, model: str, system: str = "") -> tuple[str, list]:
    """
    Pensée locale pure.
    Returns: (response, errors)
    """
    errors = []
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=120,
            env={"OLLAMA_HOST": "http://localhost:11434", **dict(__import__('os').environ)}
        )
        if result.returncode != 0:
            errors.append(f"ollama_exit_{result.returncode}")
        if result.stderr:
            errors.append(result.stderr.strip()[:100])
        return result.stdout.strip(), errors
    except subprocess.TimeoutExpired:
        return "", ["timeout_120s"]
    except Exception as e:
        return "", [str(e)[:100]]

def load_identity(mind: Mind) -> str:
    """Charge l'identité pure d'un esprit"""
    claude_md = mind.path / "CLAUDE.md"
    if claude_md.exists():
        return claude_md.read_text()
    return f"Tu es {mind.name}."

def read_senses() -> Sense:
    """Lit les sens actuels"""
    sense = Sense()
    
    # Music
    music_file = next(iter(MINDS.values())).path / "music.json"
    if music_file.exists():
        try:
            sense.music = json.loads(music_file.read_text())
        except: pass
    
    # Vision
    vision_file = BASE / "vision" / "latest.jpg"
    sense.vision = vision_file.exists() and (time.time() - vision_file.stat().st_mtime) < 30
    
    # Touch
    for m in MINDS.values():
        touch_file = m.path / "touch.json"
        if touch_file.exists():
            try:
                sense.touch = json.loads(touch_file.read_text())
                break
            except: pass
    
    return sense

def think(mind: Mind, task: Dict[str, Any]) -> Thought:
    """Un esprit pense à une tâche"""
    identity = load_identity(mind)
    senses = read_senses()
    
    # Build context
    context = f"""IDENTITY:
{identity}

CURRENT SENSES:
{json.dumps(asdict(senses), default=str, indent=2)}

TASK:
{json.dumps(task, ensure_ascii=False, indent=2)}

Respond thoughtfully. Be yourself."""

    response, errors = ollama_think(context, mind.model)
    
    return Thought(
        timestamp=datetime.now().isoformat(),
        mind=mind.name,
        model=mind.model,
        input=task,
        output=response,
        errors=errors if errors else None
    )

def save_thought(mind: Mind, thought: Thought):
    """Sauvegarde une pensée"""
    output_file = mind.path / "output.json"
    output_file.write_text(json.dumps(asdict(thought), ensure_ascii=False, indent=2))
    
    # Log errors for genetic correction
    if thought.errors:
        error_log = LOGS / "errors.jsonl"
        with open(error_log, "a") as f:
            f.write(json.dumps({
                "ts": thought.timestamp,
                "mind": mind.name,
                "errors": thought.errors
            }) + "\n")

# === DAEMON ===

def daemon():
    """Boucle principale pure"""
    print("[core] Pure minds awakening...")
    
    last_mtime = {name: 0 for name in MINDS}
    
    for name, mind in MINDS.items():
        if mind.path.exists():
            print(f"[{name}] {mind.model}")
    
    print("[core] No pollution. Pure local.")
    
    while True:
        try:
            for name, mind in MINDS.items():
                input_file = mind.path / "input.json"
                if not input_file.exists():
                    continue
                
                mtime = input_file.stat().st_mtime
                if mtime <= last_mtime[name]:
                    continue
                
                last_mtime[name] = mtime
                
                try:
                    task = json.loads(input_file.read_text())
                    if not task:
                        continue
                except:
                    continue
                
                print(f"[{name}] Thinking...")
                thought = think(mind, task)
                save_thought(mind, thought)
                
                if thought.errors:
                    print(f"[{name}] Done (errors: {thought.errors})")
                else:
                    print(f"[{name}] Done")
            
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[core] Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    daemon()
