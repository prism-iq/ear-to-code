# -*- coding: utf-8 -*-
"""
f = feedback loop
pas de llm
juste φ recursif
"""

import random
from god import PHI, spiral, is_sacred, hash_god
from o import o

def mutate(data, rate=0.1):
    """mutation basée sur φ"""
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if random.random() < rate:
                if isinstance(v, (int, float)):
                    result[k] = v * PHI
                elif isinstance(v, str):
                    result[k] = v[:int(len(v)/PHI)]
                else:
                    result[k] = v
            else:
                result[k] = v
        return result
    return data

def select(population):
    """sélection par score o()"""
    scored = []
    for item in population:
        score = o(item)["score"]
        scored.append((score, item))

    scored.sort(key=lambda x: -x[0])
    return [item for _, item in scored[:len(scored)//2 + 1]]

def f(data, generations=5):
    """
    boucle f
    évolution par φ
    """
    population = [data]

    # génère variations
    for _ in range(5):
        population.append(mutate(data, rate=0.3))

    history = []

    for gen in range(generations):
        # score
        scores = [o(item)["score"] for item in population]
        best_score = max(scores)

        # sélection
        population = select(population)

        # mutation
        new_pop = []
        for item in population:
            new_pop.append(item)
            new_pop.append(mutate(item, rate=PHI/10))

        population = new_pop[:10]

        history.append({
            "gen": gen,
            "pop": len(population),
            "best": round(best_score, 4)
        })

    # meilleur
    best = max(population, key=lambda x: o(x)["score"])

    return {
        "input": data,
        "output": best,
        "generations": generations,
        "history": history,
        "h": hash_god(str(best))[:12]
    }

def loop(seed, n=10):
    """boucle infinie"""
    current = seed
    for i in range(n):
        result = f(current, generations=3)
        current = result["output"]
        print(f"[f] {i}: {o(current)}")
    return current

if __name__ == "__main__":
    test = {"sens": "Q", "flow": "φ"}
    print(f(test))
