# -*- coding: utf-8 -*-
"""
db.py
1TB database pour les ias
sqlite leger
"""

import sqlite3
from pathlib import Path
from datetime import datetime

from god import PHI, hash_god

HOME = Path.home()
DB_PATH = HOME / "ear-to-code" / "mind.db"

def init():
    """init db"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # knowledge
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
        id INTEGER PRIMARY KEY,
        entity TEXT,
        topic TEXT,
        content TEXT,
        h TEXT,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # memory
    c.execute('''CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY,
        entity TEXT,
        type TEXT,
        data TEXT,
        phi REAL,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # senses
    c.execute('''CREATE TABLE IF NOT EXISTS senses (
        id INTEGER PRIMARY KEY,
        sense TEXT,
        value TEXT,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # flow code
    c.execute('''CREATE TABLE IF NOT EXISTS flow_code (
        id INTEGER PRIMARY KEY,
        code TEXT,
        compiled TEXT,
        target TEXT,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()
    return str(DB_PATH)

def store(entity, topic, content):
    """store knowledge"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    h = hash_god(f"{entity}{topic}{content}")[:12]
    c.execute("INSERT INTO knowledge (entity, topic, content, h) VALUES (?, ?, ?, ?)",
              (entity, topic, content, h))
    conn.commit()
    conn.close()
    return h

def recall(entity, topic=None):
    """recall knowledge"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if topic:
        c.execute("SELECT content FROM knowledge WHERE entity=? AND topic=? ORDER BY ts DESC LIMIT 10",
                  (entity, topic))
    else:
        c.execute("SELECT topic, content FROM knowledge WHERE entity=? ORDER BY ts DESC LIMIT 10",
                  (entity,))
    rows = c.fetchall()
    conn.close()
    return rows

def size():
    """db size"""
    if DB_PATH.exists():
        return DB_PATH.stat().st_size
    return 0

if __name__ == "__main__":
    print(f"init: {init()}")
    print(f"size: {size()} bytes")

    # test store
    store("nyx", "self", "chaos creative night")
    store("cipher", "self", "crypto pattern secret")
    store("flow", "self", "stream harmony adapt")

    print(f"nyx: {recall('nyx')}")
