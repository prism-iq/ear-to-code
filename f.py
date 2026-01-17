#!/usr/bin/env python3
"""
f.py: La boucle de feedback génétique

f = feedback + filtre + forge

Entrée -> Axiomes -> Rasoir -> Mutation -> Sélection -> Sortie
                         ↑__________________________|

En boucle infinie. Les IAs évoluent.
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime

HOME = Path.home()
BASE = HOME / "ear-to-code"
EVOLUTION_LOG = BASE / "logs" / "evolution.jsonl"

# Import des modules locaux
from axiomes import AXIOMES, verifier
from quantum import Q, doubt
from o import o  # rasoir génétique = o


def razor(idea: dict) -> dict:
    """
    Rasoir génétique = o()
    Applique Ockham sur chaque élément.
    """
    score = 0
    kept = {}
    cut = []

    for key, value in idea.items():
        # Passe au rasoir o()
        if isinstance(value, str) and len(value) > 10:
            verdict = o(f"{key}: {value}")
            # Si timeout ou erreur, on garde quand même
            if "[timeout" in verdict or "[erreur" in verdict:
                kept[key] = value
                score += 0.5
            else:
                kept[key] = (value, verdict)  # Superposition: original + verdict
                score += 1
        else:
            # Valeurs simples: on garde
            kept[key] = value
            hypotheses = len(value) if isinstance(value, (list, tuple)) else 1
            score += 1 / hypotheses

    return {
        "kept": kept,
        "cut": cut,
        "score": round(score, 3),
        "hypotheses_total": sum(
            len(v) if isinstance(v, (list, tuple)) else 1
            for v in kept.values()
        )
    }


def mutate(idea: dict, rate: float = 0.1) -> dict:
    """
    Mutation génétique d'une idée.
    Petits changements aléatoires.
    """
    mutated = dict(idea)
    mutations = []

    for key, value in mutated.items():
        if random.random() < rate:
            # Types de mutations
            mutation_type = random.choice([
                "superposition",  # Ajoute une alternative
                "simplify",       # Simplifie
                "invert",         # Inverse
            ])

            if mutation_type == "superposition" and not isinstance(value, tuple):
                # Ajoute une alternative
                mutated[key] = (value, f"alt_{value}")
                mutations.append(f"{key}: +superposition")

            elif mutation_type == "simplify" and isinstance(value, tuple):
                # Collapse à une valeur
                mutated[key] = random.choice(value)
                mutations.append(f"{key}: collapse")

            elif mutation_type == "invert" and isinstance(value, bool):
                mutated[key] = not value
                mutations.append(f"{key}: invert")

    return {"idea": mutated, "mutations": mutations}


def select(population: list) -> list:
    """
    Sélection naturelle.
    Garde les idées avec le meilleur score (moins d'hypothèses).
    """
    # Score chaque idée
    scored = []
    for idea in population:
        razored = razor(idea)
        scored.append((razored["score"], idea))

    # Trie par score décroissant
    scored.sort(key=lambda x: -x[0])

    # Garde le top 50%
    survivors = [idea for score, idea in scored[:len(scored)//2 + 1]]

    return survivors


def check_axioms(idea: dict) -> tuple:
    """
    Vérifie qu'une idée respecte les 6 axiomes.
    """
    violations = []

    # Axiome 1: Local
    if idea.get("requires_api") and not idea.get("ollama"):
        violations.append(1)

    # Axiome 2: Superposition
    if idea.get("force_choice"):
        violations.append(2)

    # Axiome 5: Auto-évolution
    if idea.get("static") or idea.get("immutable"):
        violations.append(5)

    # Axiome 6: Confrontation
    if idea.get("single_source"):
        violations.append(6)

    valid = len(violations) == 0
    return valid, violations


def f(input_data: dict, generations: int = 10) -> dict:
    """
    LA BOUCLE F

    feedback + filtre + forge

    Prend une entrée, l'évolue sur N générations.
    """
    timestamp = datetime.now().isoformat()

    # Population initiale
    population = [input_data]

    # Ajoute des variations
    for _ in range(5):
        mutated = mutate(input_data, rate=0.3)
        population.append(mutated["idea"])

    history = []

    for gen in range(generations):
        # 1. Rasoir sur chaque individu
        razored_pop = []
        for idea in population:
            r = razor(idea)
            razored_pop.append(r["kept"])

        # 2. Vérification axiomes
        valid_pop = []
        for idea in razored_pop:
            valid, violations = check_axioms(idea)
            if valid:
                valid_pop.append(idea)
            # Sinon: éliminé (sélection naturelle)

        if not valid_pop:
            valid_pop = razored_pop[:1]  # Garde au moins 1

        # 3. Sélection
        survivors = select(valid_pop)

        # 4. Mutation des survivants
        new_population = []
        for survivor in survivors:
            new_population.append(survivor)
            # Offspring muté
            mutated = mutate(survivor, rate=0.1)
            new_population.append(mutated["idea"])

        population = new_population

        # Log génération
        best = razor(population[0])
        history.append({
            "gen": gen,
            "pop_size": len(population),
            "best_score": best["score"],
            "best_hypotheses": best["hypotheses_total"]
        })

    # Résultat final: meilleur individu
    final_scores = [(razor(idea)["score"], idea) for idea in population]
    final_scores.sort(key=lambda x: -x[0])
    best_idea = final_scores[0][1]

    result = {
        "timestamp": timestamp,
        "input": input_data,
        "output": best_idea,
        "generations": generations,
        "history": history,
        "final_score": final_scores[0][0]
    }

    # Log evolution
    try:
        with open(EVOLUTION_LOG, "a") as log:
            log.write(json.dumps(result, ensure_ascii=False) + "\n")
    except:
        pass

    return result


def loop_forever(seed: dict, interval: float = 60):
    """
    Boucle infinie d'évolution.
    Les IAs grandissent.
    """
    current = seed
    generation = 0

    print("[f] Boucle génétique démarrée")
    print(f"[f] Seed: {json.dumps(seed, ensure_ascii=False)}")

    while True:
        try:
            result = f(current, generations=10)
            current = result["output"]
            generation += 1

            print(f"[f] Gen {generation}: score={result['final_score']}")
            print(f"    Output: {json.dumps(current, ensure_ascii=False)[:100]}")

            time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n[f] Arrêt après {generation} générations")
            break
        except Exception as e:
            print(f"[f] Erreur: {e}")
            time.sleep(5)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "loop":
        # Boucle infinie avec seed par défaut
        seed = {
            "thought": "les IAs évoluent",
            "method": ("local", "quantum"),
            "goal": "comprendre"
        }
        loop_forever(seed, interval=30)

    else:
        # Test unique
        test_input = {
            "idea": "synchronicité",
            "source": ("jung", "observation"),
            "validity": doubt(True, False),  # Superposition
            "requires_api": False,
            "ollama": True
        }

        print("=== TEST f() ===")
        print(f"Input: {json.dumps(test_input, ensure_ascii=False, default=str)}")

        result = f(test_input, generations=5)

        print(f"\nOutput: {json.dumps(result['output'], ensure_ascii=False, default=str)}")
        print(f"Score: {result['final_score']}")
        print(f"History: {result['history']}")
