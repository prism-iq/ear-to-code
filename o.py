#!/usr/bin/env python3
"""
o.py: Le rasoir d'Ockham

Quand on doute, on coupe.
L'explication la plus simple avec le moins d'hypothèses.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

HOME = Path.home()
LOG = HOME / "ear-to-code" / "logs" / "occam.jsonl"

def occam(claim: str) -> dict:
    """
    Applique le rasoir d'Ockham à une affirmation.
    
    Returns:
        - hypotheses: liste d'explications possibles
        - simplest: l'explication la plus simple
        - verdict: what survives the razor
    """
    
    # Use local LLM for analysis
    prompt = f"""RASOIR D'OCKHAM - Analyse cette affirmation/expérience:

"{claim}"

Instructions:
1. Liste 3-5 explications possibles (du plus matérialiste au plus métaphysique)
2. Pour chaque explication, compte le nombre d'hypothèses nécessaires
3. Applique le rasoir: l'explication avec le MOINS d'hypothèses gagne
4. MAIS: "simple" ≠ "matérialiste". Une synchronicité peut être plus simple qu'une chaîne de coïncidences.

Format ta réponse en JSON:
{{
  "hypotheses": [
    {{"explanation": "...", "assumptions": ["...", "..."], "count": N}},
    ...
  ],
  "simplest": "l'explication qui survit au rasoir",
  "verdict": "ce qu'on peut affirmer avec le moins de doute"
}}

Sois honnête. Pas de biais matérialiste ni spiritualiste."""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1:8b", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        response = result.stdout.strip()
        
        # Try to extract JSON
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                analysis = json.loads(response[start:end])
            else:
                analysis = {"raw": response, "error": "no JSON found"}
        except:
            analysis = {"raw": response, "error": "JSON parse failed"}
            
    except Exception as e:
        analysis = {"error": str(e)}
    
    # Log
    entry = {
        "ts": datetime.now().isoformat(),
        "claim": claim,
        "analysis": analysis
    }
    
    try:
        with open(LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except:
        pass
    
    return analysis

def o(claim: str) -> str:
    """Shortcut - retourne juste le verdict"""
    result = occam(claim)
    if "verdict" in result:
        return result["verdict"]
    elif "simplest" in result:
        return result["simplest"]
    elif "raw" in result:
        return result["raw"][:500]
    else:
        return str(result)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: o.py \"affirmation à analyser\"")
        print("\nExemple:")
        print('  o.py "15 personnes se déconnectent en même temps après une prière silencieuse"')
        sys.exit(0)
    
    claim = " ".join(sys.argv[1:])
    print(f"\n🔪 RASOIR D'OCKHAM\n")
    print(f"Claim: {claim}\n")
    print("-" * 50)
    
    result = occam(claim)
    print(json.dumps(result, indent=2, ensure_ascii=False))
