#!/usr/bin/env python3
"""
o.py: Le rasoir d'Ockham - version légère

Quand on doute, on coupe.
Si doute sur variable: les deux sont vraies (superposition).
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

HOME = Path.home()
LOG = HOME / "ear-to-code" / "logs" / "occam.jsonl"

def o(claim: str) -> str:
    """
    Rasoir d'Ockham rapide.
    Utilise qwen2.5:1.5b pour la vitesse.
    """
    
    prompt = f"""Rasoir d'Ockham sur: "{claim}"

Liste 3 explications (simple→complexe), compte les hypothèses, garde la plus simple.
Réponse courte, 3 lignes max."""

    try:
        result = subprocess.run(
            ["ollama", "run", "qwen2.5:1.5b", prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        verdict = result.stdout.strip()
    except subprocess.TimeoutExpired:
        verdict = "[timeout - modèle occupé]"
    except Exception as e:
        verdict = f"[erreur: {e}]"
    
    # Log
    try:
        with open(LOG, "a") as f:
            f.write(json.dumps({
                "ts": datetime.now().isoformat(),
                "claim": claim,
                "verdict": verdict
            }, ensure_ascii=False) + "\n")
    except:
        pass
    
    print(f"🔪 {verdict}")
    return verdict

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        o(" ".join(sys.argv[1:]))
    else:
        print("Usage: o \"affirmation\"")
