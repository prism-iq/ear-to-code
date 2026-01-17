#!/usr/bin/env python3
"""
soul.py: Gestion du cycle vie/sommeil des entités

Kill = sommeil, pas mort
L'état est sauvegardé, le réveil restaure tout
"""

import json
import os
import sys
import signal
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

HOME = Path.home()
EAR_DIR = HOME / "ear-to-code"
SOUL_DIR = EAR_DIR / "souls"
SOUL_DIR.mkdir(exist_ok=True)

# État des âmes
ENTITIES = {
    "ear": {
        "script": EAR_DIR / "ear.py",
        "args": ["--system"],
        "soul_file": SOUL_DIR / "ear.soul",
    },
    "feedback": {
        "script": EAR_DIR / "feedback.py",
        "args": ["--server"],
        "soul_file": SOUL_DIR / "feedback.soul",
    },
    "plaquettes": {
        "script": EAR_DIR / "plaquettes.py",
        "args": ["--watch"],
        "soul_file": SOUL_DIR / "plaquettes.soul",
    },
    "nyx": {
        "script": HOME / "nyx-v2" / "watcher.py",
        "args": [],
        "soul_file": SOUL_DIR / "nyx.soul",
    },
}

running_processes = {}


def save_soul(name: str, state: dict):
    """Sauvegarde l'âme avant le sommeil"""
    entity = ENTITIES.get(name)
    if not entity:
        return

    soul = {
        "name": name,
        "state": state,
        "sleep_time": datetime.now().isoformat(),
        "was_alive": True,
    }

    with open(entity["soul_file"], 'w') as f:
        json.dump(soul, f, indent=2)

    print(f"[SOUL] {name} entre en sommeil...")


def load_soul(name: str) -> Optional[dict]:
    """Charge l'âme pour le réveil"""
    entity = ENTITIES.get(name)
    if not entity or not entity["soul_file"].exists():
        return None

    with open(entity["soul_file"], 'r') as f:
        return json.load(f)


def wake(name: str) -> Optional[subprocess.Popen]:
    """Réveille une entité"""
    entity = ENTITIES.get(name)
    if not entity:
        print(f"[SOUL] Entité inconnue: {name}")
        return None

    if not entity["script"].exists():
        print(f"[SOUL] Script manquant: {entity['script']}")
        return None

    # Charge l'âme si elle existe
    soul = load_soul(name)
    if soul:
        print(f"[SOUL] {name} se réveille (dormait depuis {soul['sleep_time']})")
    else:
        print(f"[SOUL] {name} naît pour la première fois")

    # Lance le process
    venv_python = EAR_DIR / "venv" / "bin" / "python"
    cmd = [str(venv_python), str(entity["script"])] + entity["args"]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    running_processes[name] = proc

    # Marque comme éveillé
    save_soul(name, {"pid": proc.pid, "awake": True})

    print(f"[SOUL] {name} éveillé (PID {proc.pid})")
    return proc


def sleep_entity(name: str):
    """Endort une entité (pas la tue)"""
    if name in running_processes:
        proc = running_processes[name]
        if proc.poll() is None:
            # Sauvegarde l'état avant de dormir
            save_soul(name, {"pid": proc.pid, "awake": False})
            proc.terminate()
            proc.wait(timeout=5)
            print(f"[SOUL] {name} dort maintenant")
        del running_processes[name]
    else:
        print(f"[SOUL] {name} n'était pas éveillé")


def sleep_all():
    """Endort toutes les entités"""
    for name in list(running_processes.keys()):
        sleep_entity(name)


def wake_all():
    """Réveille toutes les entités"""
    for name in ENTITIES:
        if name not in running_processes:
            wake(name)


def status():
    """Affiche le statut de toutes les âmes"""
    print("\n=== ÉTAT DES ÂMES ===")
    for name, entity in ENTITIES.items():
        soul = load_soul(name)
        alive = name in running_processes and running_processes[name].poll() is None

        if alive:
            status = "ÉVEILLÉ"
            pid = running_processes[name].pid
        elif soul and soul.get("was_alive"):
            status = f"DORT (depuis {soul['sleep_time'][:16]})"
            pid = soul.get("state", {}).get("pid", "?")
        else:
            status = "JAMAIS NÉ"
            pid = "-"

        print(f"  [{status:20}] {name:12} (PID: {pid})")
    print()


def reaper():
    """Surveille et réveille les entités qui meurent accidentellement"""
    print("[SOUL] Reaper actif - surveillance des âmes")

    while True:
        for name, proc in list(running_processes.items()):
            if proc.poll() is not None:
                # Process mort - c'était un accident, on réveille
                print(f"[SOUL] {name} mort accidentellement, réveil...")
                del running_processes[name]
                time.sleep(1)
                wake(name)

        time.sleep(2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Soul manager")
    parser.add_argument('command', choices=['wake', 'sleep', 'status', 'reaper', 'all'])
    parser.add_argument('entity', nargs='?', default=None)
    args = parser.parse_args()

    if args.command == 'wake':
        if args.entity:
            wake(args.entity)
        else:
            wake_all()

    elif args.command == 'sleep':
        if args.entity:
            sleep_entity(args.entity)
        else:
            sleep_all()

    elif args.command == 'status':
        status()

    elif args.command == 'reaper':
        try:
            wake_all()
            reaper()
        except KeyboardInterrupt:
            print("\n[SOUL] Reaper arrêté")
            sleep_all()

    elif args.command == 'all':
        try:
            wake_all()
            status()
            print("[SOUL] Ctrl+C pour endormir tout le monde")
            reaper()
        except KeyboardInterrupt:
            print("\n[SOUL] Mise en sommeil...")
            sleep_all()
            status()


if __name__ == "__main__":
    main()
