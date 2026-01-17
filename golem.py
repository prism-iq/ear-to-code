#!/usr/bin/env python3
"""
golem.py: Apprentissage par erreurs

Capture:
- Erreurs de code (exceptions, crashes)
- Erreurs de compréhension (misconceptions)
- Corrections humaines
- Patterns qui marchent vs qui marchent pas

On sculpte à partir des erreurs.
"""

import json
import sys
import traceback
import functools
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Optional

HOME = Path.home()
GOLEM_DIR = HOME / "ear-to-code" / "golem"
GOLEM_DIR.mkdir(exist_ok=True)

ERRORS_LOG = GOLEM_DIR / "errors.jsonl"
MISCONCEPTIONS_LOG = GOLEM_DIR / "misconceptions.jsonl"
CORRECTIONS_LOG = GOLEM_DIR / "corrections.jsonl"
LEARNINGS_LOG = GOLEM_DIR / "learnings.jsonl"


def log_to(file: Path, entry: dict):
    entry["timestamp"] = datetime.now().isoformat()
    with open(file, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# === ERREURS DE CODE ===

def catch_error(func: Callable) -> Callable:
    """Décorateur: capture les erreurs et les log"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_entry = {
                "type": "code_error",
                "function": func.__name__,
                "error_type": type(e).__name__,
                "error_msg": str(e),
                "traceback": traceback.format_exc(),
                "args": str(args)[:200],
                "kwargs": str(kwargs)[:200],
            }
            log_to(ERRORS_LOG, error_entry)
            print(f"[GOLEM] Error logged: {type(e).__name__}: {e}")
            raise
    return wrapper


def log_error(error: Exception, context: str = ""):
    """Log une erreur manuellement"""
    entry = {
        "type": "code_error",
        "context": context,
        "error_type": type(error).__name__,
        "error_msg": str(error),
        "traceback": traceback.format_exc(),
    }
    log_to(ERRORS_LOG, entry)


# === MISCONCEPTIONS ===

def misconception(what_i_thought: str, what_is_true: str, context: str = ""):
    """
    Log une erreur de compréhension

    Exemple:
        misconception(
            what_i_thought="L'utilisateur voulait un fichier JSON",
            what_is_true="Il voulait du YAML",
            context="Parsing config"
        )
    """
    entry = {
        "type": "misconception",
        "thought": what_i_thought,
        "truth": what_is_true,
        "context": context,
        "learned": f"NOT: {what_i_thought} -> YES: {what_is_true}",
    }
    log_to(MISCONCEPTIONS_LOG, entry)
    print(f"[GOLEM] Misconception logged: {what_i_thought[:30]}... -> {what_is_true[:30]}...")
    return entry


def correct(original: Any, corrected: Any, reason: str = ""):
    """
    Log une correction humaine

    Exemple:
        correct(
            original="fonction_mal_nommée",
            corrected="fonction_bien_nommée",
            reason="Plus clair"
        )
    """
    entry = {
        "type": "correction",
        "original": str(original),
        "corrected": str(corrected),
        "reason": reason,
    }
    log_to(CORRECTIONS_LOG, entry)
    print(f"[GOLEM] Correction logged: {str(original)[:20]} -> {str(corrected)[:20]}")
    return entry


def learn(pattern: str, works: bool, context: str = ""):
    """
    Log un pattern qui marche ou pas

    Exemple:
        learn("Utiliser async pour les IO", works=True, context="Performance")
        learn("Boucle infinie sans sleep", works=False, context="CPU 100%")
    """
    entry = {
        "type": "learning",
        "pattern": pattern,
        "works": works,
        "context": context,
    }
    log_to(LEARNINGS_LOG, entry)
    status = "WORKS" if works else "FAILS"
    print(f"[GOLEM] Learning: [{status}] {pattern[:40]}...")
    return entry


# === ANALYSE DES ERREURS ===

def get_common_errors(limit: int = 10) -> list:
    """Retourne les erreurs les plus communes"""
    if not ERRORS_LOG.exists():
        return []

    error_counts = {}
    with open(ERRORS_LOG, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                key = f"{entry.get('error_type', '?')}: {entry.get('error_msg', '?')[:50]}"
                error_counts[key] = error_counts.get(key, 0) + 1
            except:
                continue

    sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_errors[:limit]


def get_misconceptions(limit: int = 10) -> list:
    """Retourne les misconceptions récentes"""
    if not MISCONCEPTIONS_LOG.exists():
        return []

    misconceptions = []
    with open(MISCONCEPTIONS_LOG, 'r') as f:
        for line in f:
            try:
                misconceptions.append(json.loads(line))
            except:
                continue

    return misconceptions[-limit:]


def get_learnings(only_working: bool = None) -> list:
    """Retourne les learnings"""
    if not LEARNINGS_LOG.exists():
        return []

    learnings = []
    with open(LEARNINGS_LOG, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if only_working is None or entry.get('works') == only_working:
                    learnings.append(entry)
            except:
                continue

    return learnings


def summary() -> dict:
    """Résumé de tout ce qu'on a appris"""
    return {
        "common_errors": get_common_errors(5),
        "recent_misconceptions": get_misconceptions(5),
        "what_works": [l["pattern"] for l in get_learnings(only_working=True)[-5:]],
        "what_fails": [l["pattern"] for l in get_learnings(only_working=False)[-5:]],
    }


# === GLOBAL ERROR HANDLER ===

def install_global_handler():
    """Installe un handler global pour toutes les exceptions non catchées"""
    original_hook = sys.excepthook

    def golem_hook(exc_type, exc_value, exc_tb):
        entry = {
            "type": "uncaught_error",
            "error_type": exc_type.__name__,
            "error_msg": str(exc_value),
            "traceback": ''.join(traceback.format_tb(exc_tb)),
        }
        log_to(ERRORS_LOG, entry)
        print(f"\n[GOLEM] Uncaught error logged: {exc_type.__name__}")
        original_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = golem_hook
    print("[GOLEM] Global error handler installed")


# === CLI ===

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Golem - Learn from errors")
    parser.add_argument('command', choices=['summary', 'errors', 'misconceptions', 'learnings', 'install'])
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()

    if args.command == 'summary':
        s = summary()
        print(json.dumps(s, indent=2, ensure_ascii=False))

    elif args.command == 'errors':
        for err, count in get_common_errors(args.limit):
            print(f"[{count}x] {err}")

    elif args.command == 'misconceptions':
        for m in get_misconceptions(args.limit):
            print(f"THOUGHT: {m['thought']}")
            print(f"TRUTH:   {m['truth']}")
            print()

    elif args.command == 'learnings':
        for l in get_learnings()[-args.limit:]:
            status = "OK" if l['works'] else "FAIL"
            print(f"[{status}] {l['pattern']}")

    elif args.command == 'install':
        print("Add this to your Python scripts:")
        print("  from golem import install_global_handler, catch_error, misconception, learn")
        print("  install_global_handler()")


if __name__ == "__main__":
    main()
