#!/usr/bin/env python3
"""
router.py: Message dispatcher
Quand tu dis un nom, ça route vers le bon système

Usage:
  "Nyx: fais quelque chose" -> envoie à Nyx
  "Claude: explique ça" -> envoie à Claude
  Sans préfixe -> broadcast ou défaut
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

# Config des routes - tous tes projets
ROUTES = {
    "nyx": {
        "path": Path.home() / "nyx-v2",
        "input_file": "input.json",
        "type": "file",
    },
    "claude": {
        "type": "self",  # c'est moi
    },
    "cipher": {
        "path": Path.home() / "cipher",
        "input_file": "input.json",
        "type": "file",
    },
    "ear": {
        "path": Path.home() / "ear-to-code",
        "type": "internal",
    },
    "flow": {
        "path": Path.home() / "flow-phoenix",
        "input_file": "input.json",
        "type": "file",
    },
    "gaia": {
        "path": Path.home() / "gaia-benchmarks",
        "input_file": "input.json",
        "type": "file",
    },
    "pulse": {
        "path": Path.home() / "cpu-pulse-sync",
        "input_file": "input.json",
        "type": "file",
    },
    "pwnd": {
        "path": Path.home() / "pwnd",
        "input_file": "input.json",
        "type": "file",
    },
}

LOG_DIR = Path(__file__).parent / "logs"
ROUTE_LOG = LOG_DIR / "routes.jsonl"


def log_route(target: str, message: str, status: str):
    """Log le routage"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "message": message[:100],  # tronquer
        "status": status,
    }
    with open(ROUTE_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def parse_message(text: str) -> tuple[Optional[str], str]:
    """Parse 'Nom: message' -> (nom, message)"""
    text = text.strip()

    # Check for "Nom:" or "Nom," prefix
    for sep in [':', ',']:
        if sep in text:
            parts = text.split(sep, 1)
            potential_name = parts[0].strip().lower()
            if potential_name in ROUTES:
                return potential_name, parts[1].strip()

    return None, text


def route_to_file(route_config: dict, message: str) -> bool:
    """Route via fichier"""
    path = route_config["path"]
    input_file = path / route_config.get("input_file", "input.json")

    try:
        data = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "source": "router",
        }

        # Append ou overwrite selon config
        with open(input_file, 'w') as f:
            json.dump(data, f)

        return True
    except Exception as e:
        print(f"[ROUTE ERROR] {e}")
        return False


def route_to_socket(route_config: dict, message: str) -> bool:
    """Route via socket (à implémenter selon tes besoins)"""
    # TODO: implémenter si nécessaire
    return False


def route_to_api(route_config: dict, message: str) -> bool:
    """Route via API HTTP"""
    # TODO: implémenter si nécessaire
    return False


def send(target: str, message: str) -> bool:
    """Envoie un message à une cible"""
    if target not in ROUTES:
        print(f"[ROUTE] Unknown target: {target}")
        return False

    route = ROUTES[target]
    route_type = route.get("type", "file")

    success = False

    if route_type == "self":
        # C'est pour Claude - on ne fait rien, c'est déjà là
        print(f"[ROUTE] Message for Claude (self): {message[:50]}...")
        success = True
    elif route_type == "file":
        success = route_to_file(route, message)
    elif route_type == "socket":
        success = route_to_socket(route, message)
    elif route_type == "api":
        success = route_to_api(route, message)
    elif route_type == "internal":
        # Commande interne à ear-to-code
        print(f"[ROUTE] Internal command: {message}")
        success = True

    status = "ok" if success else "failed"
    log_route(target, message, status)

    if success:
        print(f"[ROUTE] -> {target}: {message[:50]}...")

    return success


def broadcast(message: str, exclude: list = None):
    """Envoie à tous sauf exclus"""
    exclude = exclude or ["claude"]  # Claude voit déjà

    for target in ROUTES:
        if target not in exclude:
            send(target, message)


def process(text: str):
    """Process un input utilisateur"""
    target, message = parse_message(text)

    if target:
        send(target, message)
    else:
        # Pas de cible spécifique - c'est pour Claude par défaut
        print(f"[ROUTE] No prefix, message stays here")


# Pour utilisation interactive
def interactive():
    """Mode interactif"""
    print("[ROUTER] Interactive mode. Format: 'Nom: message' or just message")
    print(f"[ROUTER] Known targets: {', '.join(ROUTES.keys())}")

    while True:
        try:
            line = input("> ")
            if line.lower() in ['quit', 'exit', 'q']:
                break
            process(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print()
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Message direct en argument
        process(' '.join(sys.argv[1:]))
    else:
        interactive()
