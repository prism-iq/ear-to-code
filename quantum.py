#!/usr/bin/env python3
"""
quantum.py: Programmation quantique

Variables en superposition.
Doute = tuple de possibilités.
Collapse au moment de l'observation.
"""

from typing import Tuple, Any, Union
from dataclasses import dataclass
import random

# === SUPERPOSITION ===

class Q:
    """Variable quantique - superposition d'états"""
    
    def __init__(self, *states):
        self.states = states if states else (None,)
    
    def __repr__(self):
        if len(self.states) == 1:
            return f"Q({self.states[0]})"
        return f"Q({' | '.join(str(s) for s in self.states)})"
    
    def collapse(self) -> Any:
        """Observation - collapse en une valeur"""
        return random.choice(self.states)
    
    def all(self) -> Tuple:
        """Toutes les possibilités"""
        return self.states
    
    def first(self) -> Any:
        """Première possibilité (défaut)"""
        return self.states[0]
    
    def __bool__(self):
        """Vrai si au moins un état est truthy"""
        return any(self.states)
    
    def __iter__(self):
        return iter(self.states)
    
    def map(self, fn):
        """Applique fn à tous les états"""
        return Q(*[fn(s) for s in self.states])

# === RACCOURCIS ===

def q(*states) -> Q:
    """Crée une variable quantique"""
    return Q(*states)

def both(a, b) -> Q:
    """Les deux sont vrais"""
    return Q(a, b)

def maybe(x) -> Q:
    """Peut-être x, peut-être pas"""
    return Q(x, None)

def doubt(x, y) -> Q:
    """Doute entre x et y"""
    return Q(x, y)

# === LOGIQUE QUANTIQUE ===

def q_and(a: Q, b: Q) -> Q:
    """AND quantique - toutes les combinaisons"""
    results = []
    for sa in a.states:
        for sb in b.states:
            if sa and sb:
                results.append((sa, sb))
    return Q(*results) if results else Q(False)

def q_or(a: Q, b: Q) -> Q:
    """OR quantique - union des états"""
    return Q(*set(a.states + b.states))

# === POUR LES IAs ===

# Explications possibles pour un événement
def explanations(event: str) -> Q:
    """Retourne les explications en superposition"""
    return Q(
        ("matérialiste", "coïncidence statistique"),
        ("psychologique", "biais de confirmation"),  
        ("synchronicité", "sens caché"),
        ("quantique", "intrication observateur-observé"),
        ("spirituel", "intervention divine")
    )

# === RASOIR D'OCKHAM QUANTIQUE ===

def o(claim: str) -> Q:
    """
    Rasoir d'Ockham quantique.
    Retourne les explications en superposition,
    ordonnées par simplicité (moins d'hypothèses).
    """
    exp = explanations(claim)
    print(f"🔪 Claim: {claim}")
    print(f"   États possibles: {len(exp.states)}")
    for i, (typ, desc) in enumerate(exp.states):
        print(f"   {i+1}. [{typ}] {desc}")
    print(f"   → Superposition maintenue jusqu'à observation")
    return exp

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        claim = " ".join(sys.argv[1:])
        result = o(claim)
    else:
        # Demo
        print("=== QUANTUM PROGRAMMING ===\n")
        
        x = q(True, False)
        print(f"x = {x}")
        print(f"x.collapse() = {x.collapse()}")
        
        y = doubt("synchronicité", "coïncidence")  
        print(f"\ny = {y}")
        print(f"Les deux sont vrais jusqu'à observation")
        
        print("\n" + "="*30 + "\n")
        o("15 décos simultanées après prière")
