#!/usr/bin/env python3
"""
talk.py: Interface conversationnelle directe

- Autocorrection des fautes
- Route aux entités si mentionnées
- Feedback immédiat
"""

import json
import re
from pathlib import Path
from datetime import datetime

HOME = Path.home()
LOG = HOME / "ear-to-code" / "logs" / "talk.jsonl"

# Corrections communes
TYPO_MAP = {
    "ca": "ça",
    "c ": "c'est ",
    "c'": "c'est",
    "ptet": "peut-être",
    "pk": "pourquoi",
    "pcq": "parce que",
    "bcp": "beaucoup",
    "mm": "même",
    "tt": "tout",
    "tjs": "toujours",
    "jsp": "je sais pas",
    "jcp": "je comprends pas",
    "oklm": "ok",
    "mtn": "maintenant",
    "qd": "quand",
    "pr": "pour",
    "ds": "dans",
    "ns": "nous",
    "vs": "vous",
    "ac": "avec",
    "ss": "sans",
    "pq": "parce que",
    "stp": "s'il te plaît",
    "svp": "s'il vous plaît",
}

# Entités connues
ENTITIES = ["nyx", "cipher", "flow", "gaia", "pulse", "claude", "ear"]


def autocorrect(text: str) -> str:
    """Corrige les fautes communes"""
    words = text.split()
    corrected = []

    for word in words:
        lower = word.lower().strip('.,!?')
        if lower in TYPO_MAP:
            # Préserve la ponctuation
            punct = ''
            if word[-1] in '.,!?':
                punct = word[-1]
            corrected.append(TYPO_MAP[lower] + punct)
        else:
            corrected.append(word)

    return ' '.join(corrected)


def detect_entities(text: str) -> list:
    """Détecte les entités mentionnées"""
    found = []
    lower = text.lower()

    for entity in ENTITIES:
        if entity in lower:
            found.append(entity)

    return found


def route_message(entity: str, message: str):
    """Envoie à une entité"""
    path = HOME / f"{entity}-v2" if entity == "nyx" else HOME / entity
    if not path.exists():
        path = HOME / entity

    if path.exists():
        input_file = path / "input.json"
        try:
            with open(input_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "message": message,
                    "source": "talk",
                }, f)
            return True
        except:
            return False
    return False


def process(text: str) -> dict:
    """Process complet"""
    original = text
    corrected = autocorrect(text)
    entities = detect_entities(text)

    result = {
        "timestamp": datetime.now().isoformat(),
        "original": original,
        "corrected": corrected,
        "entities_mentioned": entities,
        "routed_to": [],
    }

    # Route si entités mentionnées (sauf claude)
    for entity in entities:
        if entity != "claude":
            if route_message(entity, corrected):
                result["routed_to"].append(entity)

    # Log
    with open(LOG, 'a') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')

    return result


def main():
    import sys

    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
    else:
        text = input("> ")

    r = process(text)

    if r["original"] != r["corrected"]:
        print(f"[CORRIGÉ] {r['corrected']}")

    if r["entities_mentioned"]:
        print(f"[ENTITÉS] {', '.join(r['entities_mentioned'])}")

    if r["routed_to"]:
        print(f"[ROUTÉ] -> {', '.join(r['routed_to'])}")


if __name__ == "__main__":
    main()
