#!/usr/bin/env python3
"""
Template pour une entité qui répond à l'orchestra

Copie ce fichier dans ton projet et adapte process_message()
Lance-le en background: python entity_template.py &
"""

import json
import time
from pathlib import Path
from datetime import datetime

# Config - adapte ces chemins
ENTITY_NAME = "mon_entite"
INPUT_FILE = Path(__file__).parent / "input.json"
OUTPUT_FILE = Path(__file__).parent / "output.json"


def process_message(message: str) -> dict:
    """
    ADAPTE CETTE FONCTION
    Reçoit le message, retourne ta réponse
    """
    # Exemple basique - remplace par ta logique
    return {
        "entity": ENTITY_NAME,
        "timestamp": datetime.now().isoformat(),
        "analysis": f"J'ai reçu: {message[:50]}...",
        "sentiment": "neutral",
        "suggestions": [],
    }


def watch():
    """Surveille input.json et répond"""
    print(f"[{ENTITY_NAME}] Watching {INPUT_FILE}")
    last_mtime = 0

    while True:
        try:
            if INPUT_FILE.exists():
                mtime = INPUT_FILE.stat().st_mtime
                if mtime > last_mtime:
                    last_mtime = mtime

                    with open(INPUT_FILE, 'r') as f:
                        data = json.load(f)

                    if data.get("awaiting_response"):
                        message = data.get("message", "")
                        print(f"[{ENTITY_NAME}] Processing: {message[:30]}...")

                        response = process_message(message)

                        with open(OUTPUT_FILE, 'w') as f:
                            json.dump(response, f)

                        print(f"[{ENTITY_NAME}] Response written")

            time.sleep(0.1)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[{ENTITY_NAME}] Error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    watch()
