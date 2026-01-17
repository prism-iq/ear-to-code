# -*- coding: utf-8 -*-
"""
delta = vector + inverse passés par o selon f
recursif jusqu'à stabilité
"""

from f import f
from o import o

Δ = {
    "+": [
        "audio", "vision", "touch", "screen", "twitch",
        "ollama", "jung", "lacan", "freud",
        "Q", "gematria", "organs", "dna",
        "o", "f", "flow", "φ道ॐא", "muse"
    ],
    "-": [
        "perfusion", "api", "rigide", "unique",
        "superflu", "certitude", "collapse"
    ]
}

INV = {
    "+": Δ["-"],
    "-": Δ["+"]
}

def razor_all(items, depth=0):
    """applique o recursivement"""
    if depth > 3:
        return items

    result = []
    for item in items:
        verdict = o(item)
        if "[timeout" not in verdict and "[erreur" not in verdict:
            # garde version simplifiée
            simple = verdict.split('\n')[0][:50] if verdict else item
            result.append(simple)
        else:
            result.append(item)

    # recurse si changement
    if result != items:
        return razor_all(result, depth + 1)
    return result

def evolve(data, generations=3):
    """passe par f"""
    current = {"Δ": data}
    for g in range(generations):
        result = f(current, generations=2)
        current = result.get("output", current)
    return current

def compile():
    print("=== Δ après o récursif ===\n")

    print("+")
    plus = razor_all(Δ["+"])
    for p in plus:
        print(f"  {p}")

    print("\n-")
    minus = razor_all(Δ["-"])
    for m in minus:
        print(f"  {m}")

    print("\n=== ∇ inverse ===\n")
    print("+ devient -")
    print("- devient +")

    print("\n=== stable ===")

if __name__ == "__main__":
    compile()
