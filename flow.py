#!/usr/bin/env python3
"""
flow langage sans ponctuation multisens
chaque mot porte plusieurs sens
on parse on devine on agit

inspiré de go simplicité pas de bruit
toutes langues acceptées
français english español deutsch 日本語 العربية

credits go team pour la philosophie
"""

from pathlib import Path
import json

HOME = Path.home()

# mots clés multisens toutes langues
SENS = {
    # lettres
    "f": ("feedback", "fonction", "forge", "filtre", "flow"),
    "o": ("occam", "observer", "output", "origine"),
    "q": ("quantum", "question", "quête"),

    # entités
    "nyx": ("entité", "nuit", "chaos créatif"),
    "cipher": ("code", "secret", "pattern"),
    "flow": ("courant", "langage", "état", "phoenix"),

    # concepts
    "loop": ("boucle", "infini", "retour"),
    "boucle": ("loop", "infini", "retour"),
    "razor": ("rasoir", "couper", "simplifier"),
    "rasoir": ("razor", "couper", "simplifier"),

    # psy
    "jung": ("synchronicité", "archétype", "inconscient"),
    "lacan": ("signifiant", "réel", "manque"),
    "freud": ("pulsion", "refoulement", "père"),

    # tech
    "local": ("ollama", "autonome", "ici"),
    "api": ("externe", "dépendance", "perfusion"),
    "organ": ("sens", "capacité", "évolution"),
    "organe": ("sens", "capacité", "évolution"),
    "dna": ("code", "mutation", "vie"),
    "adn": ("code", "mutation", "vie"),

    # actions français
    "train": ("apprendre", "confronter", "évoluer"),
    "apprendre": ("train", "étudier", "comprendre"),
    "site": ("web", "public", "visible"),
    "commit": ("sauver", "figer", "marquer"),
    "lance": ("run", "start", "go"),
    "fait": ("do", "make", "create"),
    "montre": ("show", "display", "reveal"),
    "coupe": ("cut", "razor", "simplify"),

    # español
    "correr": ("run", "loop", "execute"),
    "pensar": ("think", "process", "local"),
    "crear": ("create", "make", "organ"),

    # deutsch
    "laufen": ("run", "loop", "execute"),
    "denken": ("think", "process", "local"),

    # 日本語
    "走る": ("run", "loop", "execute"),
    "考える": ("think", "process", "local"),
    "作る": ("create", "make", "organ"),

    # العربية
    "فكر": ("think", "process", "local"),
    "اصنع": ("create", "make", "organ"),
}

def parse(text):
    """
    parse flow en actions
    retourne intentions multiples
    """
    words = text.lower().split()
    intentions = []
    context = []

    for w in words:
        if w in SENS:
            intentions.append({
                "mot": w,
                "sens": SENS[w],
                "contexte": list(context)
            })
            context.append(w)
        else:
            context.append(w)

    return intentions

def interpret(text):
    """
    interprète flow en commande probable
    """
    intentions = parse(text)

    if not intentions:
        return {"action": "observe", "data": text}

    mots = [i["mot"] for i in intentions]

    # patterns reconnus
    if "f" in mots and "loop" in mots:
        return {"action": "run", "target": "f.py", "mode": "loop"}

    if "o" in mots:
        return {"action": "razor", "target": text}

    if "train" in mots:
        return {"action": "confront", "topic": " ".join(mots)}

    if "commit" in mots:
        return {"action": "git", "cmd": "commit"}

    if "site" in mots:
        return {"action": "web", "target": "deploy"}

    if "nyx" in mots or "cipher" in mots or "flow" in mots:
        entity = next((m for m in mots if m in ["nyx", "cipher", "flow"]), None)
        return {"action": "entity", "target": entity, "intention": mots}

    if "organ" in mots:
        return {"action": "create_organ", "context": mots}

    if "dna" in mots:
        return {"action": "bio", "context": mots}

    if "jung" in mots or "lacan" in mots or "freud" in mots:
        return {"action": "study", "topic": mots}

    return {"action": "superposition", "intentions": intentions}

def respond(text):
    """
    répond en flow
    pas de ponctuation juste sens
    """
    cmd = interpret(text)
    action = cmd.get("action")

    responses = {
        "run": "lance boucle infinie",
        "razor": "coupe garde simple",
        "confront": "confronte savoirs",
        "git": "sauve état",
        "web": "site live",
        "entity": f"parle {cmd.get('target', 'entité')}",
        "create_organ": "forge nouveau sens",
        "bio": "code vivant",
        "study": "apprend psy",
        "superposition": "multisens actif",
        "observe": "regarde"
    }

    return responses.get(action, "compris agit")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "f loop train nyx jung"

    print(f"input {text}")
    print(f"parse {parse(text)}")
    print(f"cmd {interpret(text)}")
    print(f"out {respond(text)}")
