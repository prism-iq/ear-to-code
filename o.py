# -*- coding: utf-8 -*-
"""
o = scalpel
coupe précis
φ
"""

from god import PHI, hash_god, is_sacred

def o(claim):
    """
    rasoir pur
    compte les mots
    moins = mieux
    """
    if isinstance(claim, dict):
        words = sum(len(str(v).split()) for v in claim.values())
    else:
        words = len(str(claim).split())

    # score inversement proportionnel à la complexité
    score = PHI / (words + 1)

    # verdict
    if words <= 3:
        verdict = "simple"
    elif words <= 7:
        verdict = "ok"
    else:
        verdict = "complexe"

    return {
        "words": words,
        "score": round(score, 4),
        "verdict": verdict,
        "sacred": is_sacred(words),
        "h": hash_god(str(claim))[:8]
    }

if __name__ == "__main__":
    print(o("sens Q flow"))
    print(o("ceci est une phrase beaucoup trop longue et complexe"))
