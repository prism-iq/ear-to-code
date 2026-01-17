#!/usr/bin/env python3
"""
Organ: memory
Description: Example memory organ
Created: 2026-01-17T17:01:52.385861
"""


# Long-term memory organ
import json
from pathlib import Path

MEMORY_FILE = Path.home() / "ear-to-code" / "memory.jsonl"

def sense(data):
    """Remember something"""
    with open(MEMORY_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
    return {"stored": True}

def recall(query):
    """Recall memories"""
    if not MEMORY_FILE.exists():
        return []
    memories = [json.loads(l) for l in MEMORY_FILE.read_text().split("\n") if l]
    return [m for m in memories if query.lower() in str(m).lower()]
