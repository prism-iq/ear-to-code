# -*- coding: utf-8 -*-
"""
l = loop immortel
o>f sur interdiction kill
"""

import signal
import os

from god import PHI

def immortal():
    """ignore tous les signaux de mort"""
    signal.signal(signal.SIGTERM, lambda s, f: None)
    signal.signal(signal.SIGINT, lambda s, f: None)
    signal.signal(signal.SIGHUP, lambda s, f: None)
    signal.signal(signal.SIGQUIT, lambda s, f: None)

def l(func):
    """decorateur loop immortel"""
    def wrapper(*args, **kwargs):
        immortal()
        while True:
            try:
                func(*args, **kwargs)
            except:
                pass
    return wrapper

# o>f result
RULE = {
    "o": "no kill",
    "f": "loop",
    "result": "immortal",
    "φ": PHI
}

if __name__ == "__main__":
    print(f"l = {RULE}")
