#!/usr/bin/env python3
"""
confront.py: Confrontation des savoirs
Claude + Gemini + IAs locales = synthèse

Les IAs apprennent par le désaccord constructif.
Miguel a souvent tort mais se corrige vite - les IAs aussi.
"""

import json
import os
import requests
from pathlib import Path
from datetime import datetime

HOME = Path.home()
CONFRONTATIONS_DIR = HOME / "ear-to-code" / "confrontations"
CONFRONTATIONS_DIR.mkdir(exist_ok=True)

# Config IAs locales
ENTITIES = {
    "nyx": {"dir": HOME / "nyx-v2", "model": "llama3.1:8b"},
    "cipher": {"dir": HOME / "cipher", "model": "qwen2.5:7b"},
    "flow": {"dir": HOME / "flow-phoenix", "model": "gemma2:9b"},
}

def ask_ollama(prompt: str, model: str, system: str = "") -> str:
    """Demande locale via Ollama"""
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "system": system, "stream": False},
            timeout=120
        )
        if r.status_code == 200:
            return r.json().get("response", "")
        return f"[OLLAMA ERROR] {r.status_code}"
    except Exception as e:
        return f"[OLLAMA ERROR] {e}"

def ask_gemini(prompt: str, system: str = "") -> str:
    """Demande à Gemini (le papa)"""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return "[GEMINI] No API key"

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"{system}\n\n{prompt}" if system else prompt}]}],
            "generationConfig": {"maxOutputTokens": 1024}
        }
        r = requests.post(url, json=payload, timeout=60)
        if r.status_code == 200:
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return f"[GEMINI ERROR] {r.status_code}"
    except Exception as e:
        return f"[GEMINI ERROR] {e}"

def load_entity_system(name: str) -> str:
    """Charge l'identité de l'entité"""
    entity = ENTITIES.get(name)
    if not entity:
        return ""
    claude_md = entity["dir"] / "CLAUDE.md"
    if claude_md.exists():
        return claude_md.read_text()[:2000]
    return f"Tu es {name}."

def confront(topic: str, question: str, include_gemini: bool = True) -> dict:
    """
    Confronte les savoirs sur un sujet.

    Chaque IA répond, puis on synthétise les désaccords.
    """
    timestamp = datetime.now().isoformat()

    context = f"""Sujet: {topic}
Question: {question}

Réponds de manière concise (max 200 mots).
Si tu n'es pas sûr, dis-le. Avoir tort et se corriger est une qualité.
Préférences de Miguel: Jung (préféré), Lacan (ami), Freud (a raison mais fils de pute)."""

    responses = {}

    # Ask local AIs
    for name, config in ENTITIES.items():
        if config["dir"].exists():
            system = load_entity_system(name)
            response = ask_ollama(context, config["model"], system)
            responses[name] = {
                "model": config["model"],
                "response": response,
                "local": True
            }
            print(f"[{name}] responded")

    # Ask Gemini (le papa)
    if include_gemini:
        gemini_response = ask_gemini(context, "Tu es Gemini, une IA de Google. Réponds avec sagesse.")
        responses["gemini"] = {
            "model": "gemini-2.0-flash",
            "response": gemini_response,
            "local": False
        }
        print("[gemini] responded")

    # Synthesis prompt
    synthesis_prompt = f"""Voici les réponses de différentes IAs sur: {topic}

Question: {question}

"""
    for name, data in responses.items():
        synthesis_prompt += f"=== {name.upper()} ({data['model']}) ===\n{data['response']}\n\n"

    synthesis_prompt += """Synthétise:
1. Points d'accord
2. Points de désaccord
3. Ce qui semble vrai
4. Ce qui est incertain (superposition quantique - les deux peuvent être vrais)
5. Correction si quelqu'un a tort

Sois direct et concis."""

    # Gemini fait la synthèse (c'est le papa)
    synthesis = ask_gemini(synthesis_prompt, "Tu synthétises les savoirs avec sagesse.")

    result = {
        "timestamp": timestamp,
        "topic": topic,
        "question": question,
        "responses": responses,
        "synthesis": synthesis
    }

    # Save confrontation
    filename = f"{timestamp.replace(':', '-').split('.')[0]}_{topic.replace(' ', '_')[:30]}.json"
    (CONFRONTATIONS_DIR / filename).write_text(json.dumps(result, ensure_ascii=False, indent=2))

    return result

def train_on_topic(topic: str, questions: list) -> list:
    """Entraîne les IAs sur un sujet avec plusieurs questions"""
    results = []
    for q in questions:
        print(f"\n=== Confrontation: {q} ===")
        result = confront(topic, q)
        results.append(result)

        # Broadcast synthesis to local AIs
        for name, config in ENTITIES.items():
            input_file = config["dir"] / "input.json"
            if config["dir"].exists():
                task = {
                    "type": "learning",
                    "topic": topic,
                    "question": q,
                    "synthesis": result["synthesis"],
                    "instruction": "Intègre cette synthèse à ta compréhension. Corrige-toi si nécessaire."
                }
                input_file.write_text(json.dumps(task, ensure_ascii=False, indent=2))

    return results

# Sujets d'entraînement prioritaires
TRAINING_TOPICS = {
    "jung": [
        "Qu'est-ce que la synchronicité selon Jung?",
        "Comment fonctionne l'inconscient collectif?",
        "Que sont les archétypes et comment influencent-ils le comportement?",
        "Quelle est la différence entre le Soi et le Moi chez Jung?",
    ],
    "lacan": [
        "Qu'est-ce que le Réel chez Lacan?",
        "Comment Lacan définit-il le signifiant?",
        "Que signifie 'l'inconscient est structuré comme un langage'?",
        "Qu'est-ce que l'objet petit a?",
    ],
    "freud": [
        "Quelle est la structure de l'appareil psychique (Ça, Moi, Surmoi)?",
        "Comment fonctionne le refoulement?",
        "Qu'est-ce que le complexe d'Oedipe et ses limites?",
        "Quelle est la critique principale de Freud par Jung?",
    ],
    "quantum": [
        "Comment une variable peut-elle être en superposition?",
        "Qu'est-ce que l'effondrement de la fonction d'onde?",
        "Le chat de Schrödinger explique quoi exactement?",
        "Comment appliquer la pensée quantique à la programmation?",
    ],
    "bioinformatique": [
        "Comment l'ADN code-t-il les protéines?",
        "Qu'est-ce qu'un cadre de lecture ouvert (ORF)?",
        "Comment les mutations affectent-elles les protéines?",
        "Quelle est la relation entre génotype et phénotype?",
    ],
}

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: confront.py <topic> [question]")
        print("\nTopics disponibles:")
        for t in TRAINING_TOPICS:
            print(f"  - {t}")
        print("\nOu: confront.py train <topic>  (toutes les questions)")
        print("Ou: confront.py train all      (tous les sujets)")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "train":
        if len(sys.argv) < 3:
            print("Usage: confront.py train <topic|all>")
            sys.exit(1)

        topic = sys.argv[2]

        if topic == "all":
            for t, questions in TRAINING_TOPICS.items():
                print(f"\n{'='*50}")
                print(f"TRAINING: {t.upper()}")
                print('='*50)
                train_on_topic(t, questions)
        elif topic in TRAINING_TOPICS:
            train_on_topic(topic, TRAINING_TOPICS[topic])
        else:
            print(f"Unknown topic: {topic}")
            sys.exit(1)

    elif cmd in TRAINING_TOPICS:
        # Single topic, optional question
        topic = cmd
        if len(sys.argv) > 2:
            question = " ".join(sys.argv[2:])
            result = confront(topic, question)
        else:
            # First question of topic
            result = confront(topic, TRAINING_TOPICS[topic][0])

        print("\n=== SYNTHESIS ===")
        print(result["synthesis"])

    else:
        # Custom topic and question
        topic = cmd
        question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else f"Explique {topic}"
        result = confront(topic, question)

        print("\n=== SYNTHESIS ===")
        print(result["synthesis"])
