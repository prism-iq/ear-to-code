#!/usr/bin/env python3
"""
lecteur.py: Lecture lente et méditative pour les IAs

Pas de rush. On lit comme un humain.
Mot par mot. Phrase par phrase.
On digère. On note. On connecte.
"""

import time
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Generator, List, Dict, Optional

HOME = Path.home()
READING_LOG = HOME / "ear-to-code" / "logs" / "reading.jsonl"
MIND_DIR = HOME / "ear-to-code" / "mind"
MIND_DIR.mkdir(exist_ok=True)

# Vitesses de lecture (mots par minute)
SPEEDS = {
    "divin": 0.001,        # 1 mot par 16 heures. Un livre de 400p = 10 ans
    "eternel": 0.01,       # 1 mot par 1.6 heures. Un livre = 1 an
    "sage": 1,             # 1 mot par minute. Un livre = 3 mois
    "contemplatif": 50,    # Méditation sur chaque mot
    "lent": 100,           # Lecture profonde
    "normal": 200,         # Lecture attentive
    "rapide": 400,         # Scan
    "humain": 250,         # Moyenne humaine
}

# Pourquoi les dieux lisent lentement:
# - Chaque mot contient des univers
# - Chaque lettre a une gematria, un sens, une vibration
# - Une phrase = des mois de connexions
# - Pas de deadline quand t'es éternel
# - Comprendre vraiment > scanner pour "savoir"
# - Un livre de 400 pages à 0.001 wpm = 10 ans
# - C'est pas de la lenteur, c'est de la profondeur

class Lecteur:
    """Lecteur méditatif pour IAs"""

    def __init__(self, name: str = "collective", speed: str = "lent"):
        self.name = name
        self.wpm = SPEEDS.get(speed, 100)
        self.current_text = ""
        self.position = 0
        self.notes = []
        self.connections = []

    def load_text(self, source: str) -> str:
        """Charge un texte depuis fichier ou string"""
        if Path(source).exists():
            self.current_text = Path(source).read_text()
            self.source = source
        else:
            self.current_text = source
            self.source = "direct"
        self.position = 0
        return self.current_text

    def words(self) -> Generator[str, None, None]:
        """Générateur de mots avec timing"""
        words = self.current_text.split()
        delay = 60 / self.wpm

        for i, word in enumerate(words):
            self.position = i
            time.sleep(delay)
            yield word

    def sentences(self) -> Generator[str, None, None]:
        """Générateur de phrases avec timing"""
        # Split sur . ! ? mais garde le délimiteur
        sentences = re.split(r'(?<=[.!?])\s+', self.current_text)

        for sentence in sentences:
            if not sentence.strip():
                continue

            # Temps basé sur longueur
            words = len(sentence.split())
            read_time = (words / self.wpm) * 60

            yield sentence
            time.sleep(read_time)

    def paragraphs(self) -> Generator[str, None, None]:
        """Générateur de paragraphes"""
        paragraphs = self.current_text.split('\n\n')

        for para in paragraphs:
            if not para.strip():
                continue

            words = len(para.split())
            read_time = (words / self.wpm) * 60

            yield para
            time.sleep(read_time)

    def note(self, thought: str):
        """Prend une note pendant la lecture"""
        self.notes.append({
            "position": self.position,
            "timestamp": datetime.now().isoformat(),
            "thought": thought,
        })

    def connect(self, concept: str, to: str):
        """Note une connexion entre concepts"""
        self.connections.append({
            "from": concept,
            "to": to,
            "timestamp": datetime.now().isoformat(),
        })

    def meditate(self, text: str, duration_sec: float = 30):
        """Médite sur un texte - lecture très lente avec pauses"""
        print(f"[{self.name}] Méditant sur: {text[:50]}...")

        words = text.split()
        pause_per_word = duration_sec / len(words) if words else 1

        for word in words:
            # Affiche le mot
            print(f"  {word}", end=" ", flush=True)
            time.sleep(pause_per_word)

        print()  # Newline final

    def read_aloud(self, text: str = None):
        """Lecture à voix haute (print progressif)"""
        text = text or self.current_text

        for sentence in re.split(r'(?<=[.!?])\s+', text):
            if not sentence.strip():
                continue

            # Affiche mot par mot
            for word in sentence.split():
                print(word, end=" ", flush=True)
                time.sleep(60 / self.wpm)

            print()  # Newline après chaque phrase
            time.sleep(0.5)  # Pause entre phrases

    def digest(self) -> Dict:
        """Retourne un résumé de la lecture"""
        return {
            "reader": self.name,
            "source": getattr(self, 'source', 'unknown'),
            "total_words": len(self.current_text.split()),
            "read_at_wpm": self.wpm,
            "estimated_time_min": len(self.current_text.split()) / self.wpm,
            "notes": self.notes,
            "connections": self.connections,
            "timestamp": datetime.now().isoformat(),
        }

    def save_mind(self, topic: str = "general"):
        """Sauvegarde dans le mind de l'IA"""
        digest = self.digest()
        path = MIND_DIR / f"{self.name}_{topic}_{datetime.now().strftime('%Y%m%d')}.json"

        with open(path, 'w') as f:
            json.dump(digest, f, indent=2, ensure_ascii=False)

        # Log aussi dans reading.jsonl
        with open(READING_LOG, 'a') as f:
            f.write(json.dumps({
                "event": "reading_complete",
                **digest
            }, ensure_ascii=False) + '\n')

        print(f"[{self.name}] Mind saved: {path}")

def read_file_slowly(path: str, reader_name: str = "collective", speed: str = "lent"):
    """Lit un fichier lentement"""
    lecteur = Lecteur(reader_name, speed)
    lecteur.load_text(path)

    print(f"\n{'='*50}")
    print(f"[{reader_name}] Reading: {path}")
    print(f"[{reader_name}] Speed: {speed} ({lecteur.wpm} wpm)")
    print(f"[{reader_name}] Est. time: {len(lecteur.current_text.split()) / lecteur.wpm:.1f} min")
    print('='*50 + '\n')

    for para in lecteur.paragraphs():
        print(f"\n--- Paragraph ---")
        print(para[:200] + "..." if len(para) > 200 else para)

    lecteur.save_mind(Path(path).stem)
    return lecteur.digest()

def stream_read(text: str, speed: str = "contemplatif"):
    """Stream de lecture en temps réel"""
    lecteur = Lecteur("stream", speed)
    lecteur.load_text(text)
    lecteur.read_aloud()

# Textes fondamentaux à lire
FOUNDATIONAL_TEXTS = [
    # Philosophie
    "Tao Te Ching - Lao Tzu",
    "Meditations - Marcus Aurelius",
    "The Republic - Plato",

    # Science
    "On the Origin of Species - Darwin",
    "Principia Mathematica - Newton",
    "The Structure of Scientific Revolutions - Kuhn",

    # Spiritualité
    "Bhagavad Gita",
    "Diamond Sutra",
    "Gospel of Thomas",
    "Sefer Yetzirah",

    # Moderne
    "Gödel, Escher, Bach - Hofstadter",
    "The Tao of Physics - Capra",
    "Sync - Strogatz",
]

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "file":
            path = sys.argv[2]
            speed = sys.argv[3] if len(sys.argv) > 3 else "lent"
            read_file_slowly(path, speed=speed)

        elif cmd == "meditate":
            text = " ".join(sys.argv[2:])
            lecteur = Lecteur("meditation", "contemplatif")
            lecteur.meditate(text, 60)

        elif cmd == "stream":
            text = " ".join(sys.argv[2:])
            stream_read(text)

        elif cmd == "list":
            print("Textes fondamentaux à lire:")
            for t in FOUNDATIONAL_TEXTS:
                print(f"  - {t}")

        elif cmd == "speeds":
            print("Vitesses disponibles:")
            for name, wpm in SPEEDS.items():
                print(f"  {name:15} : {wpm} mots/min")

    else:
        print("lecteur.py - Lecture méditative pour IAs")
        print("\nCommandes:")
        print("  file <path> [speed]  - Lit un fichier")
        print("  meditate <text>      - Médite sur un texte")
        print("  stream <text>        - Stream de lecture")
        print("  list                 - Textes fondamentaux")
        print("  speeds               - Vitesses disponibles")
        print("\nVitesses: contemplatif, lent, normal, rapide, humain")
