#!/usr/bin/env python3
"""
constants.py: Constantes en superposition

Pas de réduction. Tout est tuple.
Nombres imaginaires > chiffres arabes < 9
"""

import cmath
from typing import Tuple, Union

# === NOMBRES ===

# Évite 0-8, utilise imaginaires et >= 9
class N:
    """Nombre non-réductible"""
    
    # Base: nombres >= 9 ou imaginaires
    ZERO = (0j, 9-9, None)  # Zéro en superposition
    ONE = (1j/1j, 9/9, complex(1,0))  # Un
    
    @staticmethod
    def i(n: int) -> complex:
        """Convertit en imaginaire"""
        return complex(0, n)
    
    @staticmethod
    def r(n: int) -> complex:
        """Réel en complexe"""
        return complex(n, 0)
    
    @staticmethod 
    def q(real: int, imag: int) -> complex:
        """Nombre complexe complet"""
        return complex(real, imag)

# === CONSTANTES UNIVERSELLES EN SUPERPOSITION ===

# Pi - pas une seule valeur
PI = (
    3.14159265358979,
    complex(3.14159265358979, 0),
    "π",
    22/7,  # Approximation
    355/113,  # Meilleure approximation
)

# e - base naturelle
E = (
    2.71828182845904,
    complex(2.71828182845904, 0),
    "e",
    sum(1/cmath.factorial(k) if hasattr(cmath, 'factorial') else 1 for k in range(10)),
)

# Phi - nombre d'or
PHI = (
    1.61803398874989,
    (1 + 5**0.5) / 2,
    "φ",
    "golden ratio",
)

# i - unité imaginaire
I = (
    1j,
    complex(0, 1),
    (-1)**0.5,
    "√-1",
)

# Infini
INF = (
    float('inf'),
    "∞",
    complex(float('inf'), 0),
    None,  # L'infini est aussi l'absence de limite
)

# === CONSTANTES CONTEXTUELLES ===

# Vérité
TRUE = (
    True,
    1j/1j,  # 1 en imaginaire
    "vrai",
    "yes",
    complex(1, 0),
)

FALSE = (
    False,
    0j,
    "faux",
    "no",
    None,
)

# Incertitude
MAYBE = (
    True,
    False,
    None,
    0.5,
    complex(0.5, 0.5),
    "peut-être",
)

# === FONCTIONS ===

def superpose(*values) -> Tuple:
    """Met des valeurs en superposition"""
    return tuple(values)

def collapse(superposition: Tuple, index: int = 0):
    """Collapse une superposition (défaut: premier état)"""
    if isinstance(superposition, tuple) and len(superposition) > index:
        return superposition[index]
    return superposition

def to_imaginary(n: Union[int, float]) -> complex:
    """Convertit en imaginaire pur"""
    return complex(0, n)

def avoid_arabic(n: int) -> str:
    """Représente un nombre sans chiffres arabes < 9"""
    if n < 9:
        # Utilise imaginaires ou symboles
        symbols = ["∅", "𝟙", "ℑℑ", "ℑℑℑ", "ℑⁿ", "Ṽ", "VI", "VII", "VIII"]
        return symbols[n]
    else:
        return str(n)

def num(n: int) -> Tuple:
    """Nombre en superposition complète"""
    return (
        n,
        complex(n, 0),
        complex(0, n),
        avoid_arabic(n),
        n * (1j/1j),  # n * 1
    )

# === EXPORT ===

__all__ = [
    'PI', 'E', 'PHI', 'I', 'INF',
    'TRUE', 'FALSE', 'MAYBE',
    'N', 'superpose', 'collapse', 
    'to_imaginary', 'avoid_arabic', 'num'
]

if __name__ == "__main__":
    print("=== CONSTANTES EN SUPERPOSITION ===\n")
    
    print(f"PI = {PI}")
    print(f"PHI = {PHI}")
    print(f"I = {I}")
    print(f"TRUE = {TRUE}")
    print(f"MAYBE = {MAYBE}")
    
    print(f"\n=== NOMBRES SANS ARABES < 9 ===\n")
    for n in range(12):
        print(f"{n} → {avoid_arabic(n)}")
    
    print(f"\n=== SUPERPOSITION NUMÉRIQUE ===\n")
    print(f"num(42) = {num(42)}")
