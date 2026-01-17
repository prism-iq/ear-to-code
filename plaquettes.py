#!/usr/bin/env python3
"""
plaquettes.py: Agents de réparation automatique

Quand le système saigne (erreur), les plaquettes colmatent.
- Surveille les erreurs
- Tente des réparations automatiques
- Apprend des patterns de fix
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

HOME = Path.home()
GOLEM_DIR = HOME / "ear-to-code" / "golem"
PLAQUETTES_LOG = GOLEM_DIR / "plaquettes.jsonl"
ERRORS_LOG = GOLEM_DIR / "errors.jsonl"

# Patterns de réparation connus
REPAIR_PATTERNS = {
    "FileNotFoundError": [
        ("mkdir -p", lambda e: f"mkdir -p {Path(str(e)).parent}"),
        ("touch", lambda e: f"touch {e}"),
    ],
    "PermissionError": [
        ("chmod", lambda e: f"chmod +x {e}"),
    ],
    "ConnectionRefusedError": [
        ("restart_service", lambda e: "systemctl --user restart ear-to-code"),
    ],
    "ModuleNotFoundError": [
        ("pip_install", lambda e: f"pip install {str(e).split(chr(39))[1]}"),
    ],
    "JSONDecodeError": [
        ("reset_json", lambda e: None),  # Special handling
    ],
}


def log(entry: dict):
    entry["timestamp"] = datetime.now().isoformat()
    with open(PLAQUETTES_LOG, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def try_repair(error_type: str, error_msg: str, context: str = "") -> Optional[dict]:
    """Tente de réparer une erreur automatiquement"""

    if error_type not in REPAIR_PATTERNS:
        return None

    for repair_name, repair_fn in REPAIR_PATTERNS[error_type]:
        try:
            cmd = repair_fn(error_msg)
            if cmd is None:
                continue

            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            repair_result = {
                "error_type": error_type,
                "error_msg": error_msg[:100],
                "repair_attempted": repair_name,
                "command": cmd,
                "success": result.returncode == 0,
                "output": result.stdout[:200] if result.stdout else result.stderr[:200],
            }

            log(repair_result)

            if result.returncode == 0:
                print(f"[PLAQUETTE] Fixed {error_type} with {repair_name}")
                return repair_result

        except Exception as e:
            print(f"[PLAQUETTE] Repair failed: {e}")
            continue

    return None


def coagulate(func):
    """Décorateur: tente de réparer automatiquement les erreurs"""
    def wrapper(*args, **kwargs):
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                error_msg = str(e)

                print(f"[PLAQUETTE] Saignement détecté: {error_type}")

                repair = try_repair(error_type, error_msg, func.__name__)

                if repair and repair.get("success"):
                    print(f"[PLAQUETTE] Cicatrisation réussie, retry {attempt + 1}")
                    continue
                else:
                    print(f"[PLAQUETTE] Cicatrisation échouée")
                    break

        # Si on arrive ici, on n'a pas pu réparer
        raise last_error

    return wrapper


def watch_and_heal():
    """Surveille les erreurs et tente de les réparer"""
    print("[PLAQUETTES] Mode surveillance actif")
    print(f"[PLAQUETTES] Watching: {ERRORS_LOG}")

    last_size = ERRORS_LOG.stat().st_size if ERRORS_LOG.exists() else 0

    while True:
        try:
            if ERRORS_LOG.exists():
                current_size = ERRORS_LOG.stat().st_size

                if current_size > last_size:
                    # Nouvelle erreur
                    with open(ERRORS_LOG, 'r') as f:
                        f.seek(last_size)
                        new_content = f.read()

                    for line in new_content.strip().split('\n'):
                        if not line:
                            continue
                        try:
                            error = json.loads(line)
                            error_type = error.get('error_type', '')
                            error_msg = error.get('error_msg', '')

                            print(f"[PLAQUETTES] Nouvelle blessure: {error_type}")
                            repair = try_repair(error_type, error_msg)

                            if repair and repair.get('success'):
                                print(f"[PLAQUETTES] Cicatrisé!")
                            else:
                                print(f"[PLAQUETTES] Besoin d'intervention manuelle")

                        except json.JSONDecodeError:
                            continue

                    last_size = current_size

            time.sleep(1)

        except KeyboardInterrupt:
            print("\n[PLAQUETTES] Arrêt")
            break
        except Exception as e:
            print(f"[PLAQUETTES] Erreur interne: {e}")
            time.sleep(5)


def add_repair_pattern(error_type: str, name: str, command_template: str):
    """Ajoute un nouveau pattern de réparation (apprentissage)"""
    if error_type not in REPAIR_PATTERNS:
        REPAIR_PATTERNS[error_type] = []

    REPAIR_PATTERNS[error_type].append(
        (name, lambda e, cmd=command_template: cmd.format(error=e))
    )

    log({
        "type": "new_pattern",
        "error_type": error_type,
        "repair_name": name,
        "command": command_template,
    })

    print(f"[PLAQUETTE] Nouveau pattern appris: {error_type} -> {name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        watch_and_heal()
    else:
        print("Usage: plaquettes.py --watch")
        print("Or import: from plaquettes import coagulate, try_repair")
