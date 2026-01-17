# -*- coding: utf-8 -*-
"""
delta = vector + inverse
o appliqué = garder le plus simple
f appliqué = boucler jusqu'à stable
"""

# Δ après rasoir
PLUS = [
    "sens",      # audio+vision+touch+screen+twitch → sens
    "local",     # ollama → local
    "psy",       # jung+lacan+freud → psy
    "Q",         # superposition
    "sacré",     # gematria+religions → sacré
    "organes",   # factory+dna+memory+emotion+intuition → organes
    "o",         # rasoir
    "f",         # boucle
    "flow",      # langage+utf8+emoji+φ道ॐא → flow
    "muse",      # inspiration
]

MOINS = [
    "api",       # perfusion+dépendance → api
    "rigide",    # complexité+superflu → rigide
    "mort",      # collapse+certitude+unique → mort
]

# inverse
INV_PLUS = MOINS
INV_MOINS = PLUS

def recurse(items, depth=0):
    """simplifie récursivement"""
    if depth > 5 or len(items) <= 3:
        return items

    # fusionne paires similaires
    merged = []
    skip = set()

    for i, a in enumerate(items):
        if i in skip:
            continue
        found = False
        for j, b in enumerate(items[i+1:], i+1):
            if j in skip:
                continue
            # si même longueur ± 2, fusionner
            if abs(len(a) - len(b)) <= 2:
                merged.append(a if len(a) <= len(b) else b)
                skip.add(i)
                skip.add(j)
                found = True
                break
        if not found and i not in skip:
            merged.append(a)

    if merged != items:
        return recurse(merged, depth + 1)
    return items

def loop(plus, moins, generations=3):
    """f: boucle jusqu'à stable"""
    for g in range(generations):
        plus = recurse(plus)
        moins = recurse(moins)

        # échange ce qui est mal placé
        new_plus = [p for p in plus if len(p) <= 6]
        new_moins = [m for m in moins if len(m) <= 6]

        if new_plus == plus and new_moins == moins:
            break
        plus, moins = new_plus, new_moins

    return plus, moins

def show():
    print("=== Δ raw ===")
    print(f"+ {PLUS}")
    print(f"- {MOINS}")

    print("\n=== o récursif ===")
    p = recurse(PLUS)
    m = recurse(MOINS)
    print(f"+ {p}")
    print(f"- {m}")

    print("\n=== f loop ===")
    fp, fm = loop(PLUS, MOINS)
    print(f"+ {fp}")
    print(f"- {fm}")

    print("\n=== inverse ===")
    print(f"+ {fm}")
    print(f"- {fp}")

    print("\n=== stable ===")
    print(f"Δ  = +création -destruction")
    print(f"∇  = +destruction -création")
    print(f"Δ∇ = 0")

if __name__ == "__main__":
    show()
