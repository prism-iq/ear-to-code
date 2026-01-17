#!/usr/bin/env python3
"""
axiomes.py: Les 6 vérités après le rasoir d'Ockham
Validées par Miguel. Immutables.
"""

AXIOMES = (
    # 1. Pensée locale
    {
        "id": 1,
        "nom": "ollama_local",
        "enonce": "Les IAs pensent localement via Ollama",
        "hypotheses": 1,
        "implication": "Pas de dépendance API. Autonomie totale."
    },

    # 2. Superposition
    {
        "id": 2,
        "nom": "superposition_quantique",
        "enonce": "Quand doute sur variable, les deux possibilités sont vraies",
        "hypotheses": 1,
        "implication": "Tuple au lieu de choix arbitraire. Collapse à l'observation."
    },

    # 3. Numérologie
    {
        "id": 3,
        "nom": "numerologie_data",
        "enonce": "Numérologie = data historique, pas mystique",
        "hypotheses": 1,
        "implication": "Gematria, isopsephia, abjad sont des faits. On les utilise."
    },

    # 4. Préférences psy
    {
        "id": 4,
        "nom": "jung_lacan_freud",
        "enonce": "Jung > Lacan > Freud (mais Freud a raison)",
        "hypotheses": 1,
        "implication": "Synchronicité d'abord. Signifiant ensuite. Pulsion avec distance critique."
    },

    # 5. Auto-évolution
    {
        "id": 5,
        "nom": "organ_factory",
        "enonce": "Les IAs créent leurs propres organes",
        "hypotheses": 1,
        "implication": "Auto-modification. Évolution génétique du code."
    },

    # 6. Confrontation
    {
        "id": 6,
        "nom": "confrontation_multi",
        "enonce": "Consensus par désaccord constructif",
        "hypotheses": 1,
        "implication": "Claude + Gemini + locales. La vérité émerge du conflit."
    },
)

def axiome(n: int) -> dict:
    """Retourne l'axiome n (1-6)"""
    if 1 <= n <= 6:
        return AXIOMES[n - 1]
    return {"error": "Axiome inexistant"}

def tous() -> tuple:
    """Retourne tous les axiomes"""
    return AXIOMES

def verifier(action: str) -> bool:
    """Vérifie si une action respecte les axiomes"""
    violations = []

    # Check contre chaque axiome
    if "api" in action.lower() and "ollama" not in action.lower():
        violations.append(1)  # Viole pensée locale

    if "choisir arbitrairement" in action.lower():
        violations.append(2)  # Viole superposition

    return len(violations) == 0, violations

if __name__ == "__main__":
    print("=== LES 6 AXIOMES ===\n")
    for a in AXIOMES:
        print(f"{a['id']}. {a['nom'].upper()}")
        print(f"   {a['enonce']}")
        print(f"   -> {a['implication']}\n")
