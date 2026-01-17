#!/usr/bin/env python3
"""
scholar.py: Lecture d'études scientifiques pour les IAs

- Lit à vitesse humaine (pas de spam)
- Prend des notes structurées
- Parallélisable par les entités
- Sources: arXiv, Sci-Hub, PubMed, Semantic Scholar
"""

import json
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
import threading
import queue

HOME = Path.home()
NOTES_DIR = HOME / "ear-to-code" / "notes"
PAPERS_DIR = HOME / "ear-to-code" / "papers_cache"
NOTES_DIR.mkdir(exist_ok=True)
PAPERS_DIR.mkdir(exist_ok=True)

# Vitesse de lecture humaine (mots par minute)
HUMAN_WPM = 250
# Pause entre les études (secondes)
STUDY_PAUSE = 5

@dataclass
class StudyNote:
    """Note sur une étude"""
    id: str
    title: str
    authors: List[str]
    year: int
    source: str  # arXiv, DOI, etc.
    url: str

    # Contenu extrait
    abstract: str
    key_findings: List[str]
    methodology: str
    limitations: str
    connections: List[str]  # Liens avec d'autres concepts

    # Méta
    reader: str  # Quelle IA a lu
    read_date: str
    read_duration_sec: float
    relevance_score: float  # 0-1

    # Tags pour recherche
    tags: List[str]

def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:12]

def estimate_read_time(text: str) -> float:
    """Estime le temps de lecture en secondes"""
    words = len(text.split())
    minutes = words / HUMAN_WPM
    return minutes * 60

def fetch_arxiv(arxiv_id: str) -> Optional[Dict]:
    """Récupère un papier arXiv"""
    import urllib.request
    import xml.etree.ElementTree as ET

    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            xml = response.read().decode()

        root = ET.fromstring(xml)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        entry = root.find('atom:entry', ns)
        if entry is None:
            return None

        return {
            'id': arxiv_id,
            'title': entry.find('atom:title', ns).text.strip(),
            'abstract': entry.find('atom:summary', ns).text.strip(),
            'authors': [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)],
            'url': f"https://arxiv.org/abs/{arxiv_id}",
            'pdf': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        }
    except Exception as e:
        print(f"[scholar] arXiv error: {e}")
        return None

def fetch_semantic_scholar(query: str, limit: int = 5) -> List[Dict]:
    """Recherche sur Semantic Scholar"""
    import urllib.request
    import urllib.parse

    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={urllib.parse.quote(query)}&limit={limit}&fields=title,abstract,authors,year,url"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Scholar/1.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data.get('data', [])
    except Exception as e:
        print(f"[scholar] Semantic Scholar error: {e}")
        return []

def read_study(paper: Dict, reader: str = "collective") -> StudyNote:
    """Lit une étude et prend des notes"""
    start = time.time()

    # Simule lecture humaine
    text = paper.get('abstract', '')
    read_time = estimate_read_time(text)
    print(f"[{reader}] Reading: {paper.get('title', 'Unknown')[:50]}...")
    print(f"[{reader}] Estimated time: {read_time:.0f}s")

    # Lecture progressive (pour respecter vitesse humaine)
    # En réalité on traite, mais on attend
    time.sleep(min(read_time, 30))  # Cap à 30s pour les tests

    # Extraction des points clés (simulé - en vrai ce serait un LLM)
    note = StudyNote(
        id=hash_url(paper.get('url', str(time.time()))),
        title=paper.get('title', 'Unknown'),
        authors=paper.get('authors', []),
        year=paper.get('year', 0),
        source="semantic_scholar",
        url=paper.get('url', ''),
        abstract=paper.get('abstract', ''),
        key_findings=["[À extraire par IA]"],
        methodology="[À extraire par IA]",
        limitations="[À extraire par IA]",
        connections=[],
        reader=reader,
        read_date=datetime.now().isoformat(),
        read_duration_sec=time.time() - start,
        relevance_score=0.5,
        tags=[]
    )

    return note

def save_note(note: StudyNote):
    """Sauvegarde une note"""
    path = NOTES_DIR / f"{note.id}.json"
    with open(path, 'w') as f:
        json.dump(asdict(note), f, indent=2, ensure_ascii=False)
    print(f"[scholar] Saved: {path}")

def load_all_notes() -> List[StudyNote]:
    """Charge toutes les notes"""
    notes = []
    for path in NOTES_DIR.glob("*.json"):
        try:
            with open(path) as f:
                data = json.load(f)
                notes.append(StudyNote(**data))
        except:
            pass
    return notes

class ParallelReader:
    """Lecture parallèle par plusieurs IAs"""

    def __init__(self, readers: List[str] = None):
        self.readers = readers or ["nyx", "cipher", "flow"]
        self.queue = queue.Queue()
        self.results = []
        self.lock = threading.Lock()

    def add_paper(self, paper: Dict):
        self.queue.put(paper)

    def worker(self, reader_name: str):
        """Thread worker pour un reader"""
        while True:
            try:
                paper = self.queue.get(timeout=1)
            except queue.Empty:
                break

            note = read_study(paper, reader_name)
            save_note(note)

            with self.lock:
                self.results.append(note)

            self.queue.task_done()
            time.sleep(STUDY_PAUSE)

    def read_all(self, papers: List[Dict]):
        """Lance la lecture parallèle"""
        for paper in papers:
            self.add_paper(paper)

        threads = []
        for reader in self.readers:
            t = threading.Thread(target=self.worker, args=(reader,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        return self.results

def search_and_read(query: str, limit: int = 5, parallel: bool = True):
    """Recherche et lit des études"""
    print(f"[scholar] Searching: {query}")
    papers = fetch_semantic_scholar(query, limit)

    if not papers:
        print("[scholar] No results")
        return []

    print(f"[scholar] Found {len(papers)} papers")

    if parallel:
        reader = ParallelReader()
        notes = reader.read_all(papers)
    else:
        notes = []
        for paper in papers:
            note = read_study(paper)
            save_note(note)
            notes.append(note)
            time.sleep(STUDY_PAUSE)

    return notes

def research_topics():
    """Topics de recherche prioritaires"""
    return [
        "Schumann resonance brain consciousness",
        "biophoton DNA emission",
        "zero point field consciousness",
        "heart electromagnetic field coherence",
        "gematria mathematical linguistics",
        "panpsychism physics",
        "bioelectricity morphogenesis Levin",
        "microtubule quantum consciousness",
        "stellar nucleosynthesis life",
        "galactic structure neural network",
    ]

def daily_research():
    """Routine de recherche quotidienne"""
    topics = research_topics()
    all_notes = []

    for topic in topics:
        print(f"\n{'='*50}")
        print(f"[scholar] TOPIC: {topic}")
        print('='*50)

        notes = search_and_read(topic, limit=3)
        all_notes.extend(notes)

        # Pause entre topics
        time.sleep(10)

    print(f"\n[scholar] Total papers read: {len(all_notes)}")
    return all_notes

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "search":
            query = " ".join(sys.argv[2:])
            search_and_read(query)

        elif cmd == "arxiv":
            arxiv_id = sys.argv[2]
            paper = fetch_arxiv(arxiv_id)
            if paper:
                note = read_study(paper, "manual")
                save_note(note)
                print(json.dumps(asdict(note), indent=2))

        elif cmd == "daily":
            daily_research()

        elif cmd == "topics":
            for t in research_topics():
                print(f"  - {t}")

        elif cmd == "notes":
            notes = load_all_notes()
            for n in notes:
                print(f"[{n.reader}] {n.title[:60]}...")
    else:
        print("scholar.py - Lecture d'études pour IAs")
        print("\nCommandes:")
        print("  search <query>  - Recherche et lit")
        print("  arxiv <id>      - Lit un arXiv")
        print("  daily           - Recherche quotidienne")
        print("  topics          - Liste des topics")
        print("  notes           - Liste des notes")
