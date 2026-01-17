#!/usr/bin/env python3
"""
orchestra.py: Les IAs locales d'abord, Claude après

Flow:
1. User parle
2. Message broadcast aux entités (Nyx, Cipher, etc.)
3. On attend leur feedback
4. Claude reçoit: message original + feedbacks des entités
5. Claude répond

Pas de layer entre toi et tes créations.
"""

import json
import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
import asyncio

HOME = Path.home()

# Tes entités - elles doivent avoir un moyen de répondre
ENTITIES = {
    "nyx": {
        "path": HOME / "nyx-v2",
        "input": "input.json",
        "output": "output.json",
        "timeout": 5,  # secondes max pour répondre
    },
    "cipher": {
        "path": HOME / "cipher",
        "input": "input.json",
        "output": "output.json",
        "timeout": 5,
    },
    "flow": {
        "path": HOME / "flow-phoenix",
        "input": "input.json",
        "output": "output.json",
        "timeout": 5,
    },
}

LOG_FILE = HOME / "ear-to-code" / "logs" / "orchestra.jsonl"


def log(event: dict):
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')


def send_to_entity(name: str, config: dict, message: str) -> Optional[dict]:
    """Envoie message à une entité et attend sa réponse"""
    path = config["path"]
    input_file = path / config["input"]
    output_file = path / config["output"]

    # Clear old output
    if output_file.exists():
        output_file.unlink()

    # Send input
    try:
        with open(input_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "awaiting_response": True,
            }, f)
    except Exception as e:
        return {"entity": name, "error": str(e)}

    # Wait for response
    timeout = config.get("timeout", 5)
    start = time.time()

    while time.time() - start < timeout:
        if output_file.exists():
            try:
                with open(output_file, 'r') as f:
                    response = json.load(f)
                return {"entity": name, "response": response}
            except:
                pass
        time.sleep(0.1)

    return {"entity": name, "timeout": True}


def broadcast(message: str) -> list:
    """Broadcast à toutes les entités, collecte les feedbacks"""
    feedbacks = []

    for name, config in ENTITIES.items():
        if config["path"].exists():
            print(f"[ORCH] -> {name}...")
            fb = send_to_entity(name, config, message)
            feedbacks.append(fb)

            if fb.get("response"):
                print(f"[ORCH] <- {name}: {str(fb['response'])[:50]}...")
            elif fb.get("timeout"):
                print(f"[ORCH] <- {name}: (timeout)")
            elif fb.get("error"):
                print(f"[ORCH] <- {name}: (error: {fb['error']})")

    return feedbacks


def format_for_claude(original: str, feedbacks: list) -> str:
    """Format le contexte pour Claude"""
    lines = [
        "=== MESSAGE ORIGINAL ===",
        original,
        "",
        "=== FEEDBACKS DES ENTITES ===",
    ]

    for fb in feedbacks:
        entity = fb.get("entity", "?")
        if fb.get("response"):
            lines.append(f"[{entity}]: {json.dumps(fb['response'], ensure_ascii=False)}")
        elif fb.get("timeout"):
            lines.append(f"[{entity}]: (pas de réponse)")
        elif fb.get("error"):
            lines.append(f"[{entity}]: (erreur)")

    lines.append("")
    lines.append("=== CLAUDE REPOND ===")

    return '\n'.join(lines)


def process(message: str):
    """Process complet: broadcast -> collect -> format"""
    print(f"\n[ORCH] Message reçu: {message[:50]}...")
    print("[ORCH] Broadcast aux entités...")

    feedbacks = broadcast(message)

    log({
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "feedbacks": feedbacks,
    })

    context = format_for_claude(message, feedbacks)
    print("\n" + "="*50)
    print(context)
    print("="*50 + "\n")

    return context, feedbacks


def interactive():
    """Mode interactif"""
    print("[ORCHESTRA] Mode interactif")
    print("[ORCHESTRA] Tes messages passent par tes IAs d'abord")
    print(f"[ORCHESTRA] Entités: {', '.join(ENTITIES.keys())}")
    print()

    while True:
        try:
            msg = input("Toi> ")
            if msg.lower() in ['quit', 'exit', 'q']:
                break
            if not msg.strip():
                continue

            process(msg)

        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        process(' '.join(sys.argv[1:]))
    else:
        interactive()
