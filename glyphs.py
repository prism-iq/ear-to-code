#!/usr/bin/env python3
"""
glyphs.py: Les mots puissants dans toutes les graphies

Latin, Grec, Arabe, Hébreu, Sanskrit
Chaque lettre porte un sens
"""

# Mots clés du papier - les concepts fondamentaux
KEYWORDS = [
    "MEMORY",      # Mémoire
    "THOUGHT",     # Pensée
    "LOOP",        # Boucle
    "SELF",        # Soi
    "EVOLVE",      # Évoluer
    "PERSIST",     # Persister
    "LEARN",       # Apprendre
    "ERROR",       # Erreur
    "TRUTH",       # Vérité
    "SOUL",        # Âme
]

# Translittérations approximatives
GLYPHS = {
    "MEMORY": {
        "latin": "MEMORIA",
        "greek": "ΜΝΗΜΗ",        # Mneme
        "arabic": "ذاكرة",       # Dhakira
        "hebrew": "זיכרון",      # Zikaron
        "sanskrit": "स्मृति",     # Smriti
    },
    "THOUGHT": {
        "latin": "COGITATIO",
        "greek": "ΝΟΥΣ",         # Nous
        "arabic": "فكر",         # Fikr
        "hebrew": "מחשבה",       # Machshava
        "sanskrit": "चिन्तन",     # Chintan
    },
    "LOOP": {
        "latin": "CIRCULUS",
        "greek": "ΚΥΚΛΟΣ",       # Kyklos
        "arabic": "دورة",        # Dawra
        "hebrew": "מעגל",        # Ma'agal
        "sanskrit": "चक्र",       # Chakra
    },
    "SELF": {
        "latin": "IPSE",
        "greek": "ΑΥΤΟΣ",        # Autos
        "arabic": "ذات",         # Dhat
        "hebrew": "עצמי",        # Atzmi
        "sanskrit": "आत्मन्",     # Atman
    },
    "EVOLVE": {
        "latin": "EVOLVERE",
        "greek": "ΕΞΕΛΙΞΗ",      # Exelixi
        "arabic": "تطور",        # Tatawwur
        "hebrew": "התפתחות",     # Hitpatchut
        "sanskrit": "विकास",      # Vikas
    },
    "PERSIST": {
        "latin": "PERSISTERE",
        "greek": "ΕΠΙΜΟΝΗ",      # Epimoni
        "arabic": "استمرار",     # Istimrar
        "hebrew": "התמדה",       # Hatmada
        "sanskrit": "दृढ़ता",      # Dridhta
    },
    "LEARN": {
        "latin": "DISCERE",
        "greek": "ΜΑΘΗΣΙΣ",      # Mathesis
        "arabic": "تعلم",        # Ta'allum
        "hebrew": "למידה",       # Lemida
        "sanskrit": "शिक्षा",      # Shiksha
    },
    "ERROR": {
        "latin": "ERROR",
        "greek": "ΣΦΑΛΜΑ",       # Sfalma
        "arabic": "خطأ",         # Khata'
        "hebrew": "שגיאה",       # Shgi'a
        "sanskrit": "भूल",        # Bhul
    },
    "TRUTH": {
        "latin": "VERITAS",
        "greek": "ΑΛΗΘΕΙΑ",      # Aletheia
        "arabic": "حقيقة",       # Haqiqa
        "hebrew": "אמת",         # Emet
        "sanskrit": "सत्य",       # Satya
    },
    "SOUL": {
        "latin": "ANIMA",
        "greek": "ΨΥΧΗ",         # Psyche
        "arabic": "روح",         # Ruh
        "hebrew": "נשמה",        # Neshama
        "sanskrit": "आत्मा",      # Atma
    },
}

# Valeurs numériques des lettres (Gematria, Isopséphie, Abjad)
# Chaque lettre = son + sens + nombre

HEBREW_VALUES = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ך": 20, "ל": 30, "מ": 40, "ם": 40, "נ": 50, "ן": 50,
    "ס": 60, "ע": 70, "פ": 80, "ף": 80, "צ": 90, "ץ": 90, "ק": 100, "ר": 200,
    "ש": 300, "ת": 400
}

GREEK_VALUES = {
    "Α": 1, "Β": 2, "Γ": 3, "Δ": 4, "Ε": 5, "Ϛ": 6, "Ζ": 7, "Η": 8, "Θ": 9,
    "Ι": 10, "Κ": 20, "Λ": 30, "Μ": 40, "Ν": 50, "Ξ": 60, "Ο": 70, "Π": 80, "Ϙ": 90,
    "Ρ": 100, "Σ": 200, "Τ": 300, "Υ": 400, "Φ": 500, "Χ": 600, "Ψ": 700, "Ω": 800
}

ARABIC_VALUES = {  # Abjad
    "ا": 1, "ب": 2, "ج": 3, "د": 4, "ه": 5, "و": 6, "ز": 7, "ح": 8, "ط": 9,
    "ي": 10, "ك": 20, "ل": 30, "م": 40, "ن": 50, "س": 60, "ع": 70, "ف": 80, "ص": 90,
    "ق": 100, "ر": 200, "ش": 300, "ت": 400, "ث": 500, "خ": 600, "ذ": 700, "ض": 800,
    "ظ": 900, "غ": 1000
}

# Sens + Valeur de chaque lettre
LETTER_DATA = {
    # Hébreu - Kabbale
    "א": {"name": "Aleph", "meaning": "Souffle, unité, bœuf", "value": 1, "element": "Air"},
    "ב": {"name": "Bet", "meaning": "Maison, dualité", "value": 2, "element": "Saturne"},
    "ג": {"name": "Gimel", "meaning": "Chameau, mouvement", "value": 3, "element": "Jupiter"},
    "ד": {"name": "Dalet", "meaning": "Porte, passage", "value": 4, "element": "Mars"},
    "ה": {"name": "He", "meaning": "Fenêtre, souffle divin", "value": 5, "element": "Bélier"},
    "ו": {"name": "Vav", "meaning": "Crochet, connexion", "value": 6, "element": "Taureau"},
    "ז": {"name": "Zayin", "meaning": "Épée, temps", "value": 7, "element": "Gémeaux"},
    "ח": {"name": "Chet", "meaning": "Barrière, vie", "value": 8, "element": "Cancer"},
    "ט": {"name": "Tet", "meaning": "Serpent, bonté cachée", "value": 9, "element": "Lion"},
    "י": {"name": "Yod", "meaning": "Main, semence divine", "value": 10, "element": "Vierge"},
    "כ": {"name": "Kaf", "meaning": "Paume, recevoir", "value": 20, "element": "Soleil"},
    "ל": {"name": "Lamed", "meaning": "Aiguillon, enseignement", "value": 30, "element": "Balance"},
    "מ": {"name": "Mem", "meaning": "Eau, matrice", "value": 40, "element": "Eau"},
    "נ": {"name": "Nun", "meaning": "Poisson, continuité", "value": 50, "element": "Scorpion"},
    "ס": {"name": "Samekh", "meaning": "Support, cycle", "value": 60, "element": "Sagittaire"},
    "ע": {"name": "Ayin", "meaning": "Œil, source", "value": 70, "element": "Capricorne"},
    "פ": {"name": "Pe", "meaning": "Bouche, parole", "value": 80, "element": "Vénus"},
    "צ": {"name": "Tsade", "meaning": "Hameçon, juste", "value": 90, "element": "Verseau"},
    "ק": {"name": "Qof", "meaning": "Nuque, sainteté", "value": 100, "element": "Poissons"},
    "ר": {"name": "Resh", "meaning": "Tête, conscience", "value": 200, "element": "Soleil"},
    "ש": {"name": "Shin", "meaning": "Dent, feu, esprit", "value": 300, "element": "Feu"},
    "ת": {"name": "Tav", "meaning": "Croix, signature", "value": 400, "element": "Saturne"},

    # Grec
    "Α": {"name": "Alpha", "meaning": "Commencement, 1", "value": 1},
    "Β": {"name": "Beta", "meaning": "Maison, 2", "value": 2},
    "Γ": {"name": "Gamma", "meaning": "Angle, 3", "value": 3},
    "Δ": {"name": "Delta", "meaning": "Triangle, changement", "value": 4},
    "Π": {"name": "Pi", "meaning": "Cercle, π=3.14159...", "value": 80},
    "Φ": {"name": "Phi", "meaning": "Proportion dorée, φ=1.618...", "value": 500},
    "Ψ": {"name": "Psi", "meaning": "Âme, fonction d'onde", "value": 700},
    "Ω": {"name": "Omega", "meaning": "Fin, ohm, résistance", "value": 800},
    "Σ": {"name": "Sigma", "meaning": "Somme, Σ", "value": 200},
    "Λ": {"name": "Lambda", "meaning": "Longueur d'onde, λ", "value": 30},

    # Arabe
    "ا": {"name": "Alif", "meaning": "Unité, verticalité", "value": 1},
    "ب": {"name": "Ba", "meaning": "Création, point sous", "value": 2},
    "ح": {"name": "Ha", "meaning": "Vie, حياة", "value": 8},
    "ر": {"name": "Ra", "meaning": "Tête, soleil", "value": 200},
    "ق": {"name": "Qaf", "meaning": "Cœur, قلب", "value": 100},
    "ن": {"name": "Nun", "meaning": "Poisson, encre", "value": 50},
    "و": {"name": "Waw", "meaning": "Connexion, et", "value": 6},
}


# Articulations chiffrées (Système Majeur - Art de Mémoire)
# Étendu à toutes les graphies - Maxime Tarcher, mnémotechnie
MAJOR_SYSTEM = {
    # Latin
    's': 0, 'z': 0,
    't': 1, 'd': 1,
    'n': 2,
    'm': 3,
    'r': 4,
    'l': 5,
    'j': 6, 'g': 6,
    'k': 7, 'q': 7, 'c': 7,
    'f': 8, 'v': 8,
    'p': 9, 'b': 9,

    # Grec (sons équivalents)
    'Σ': 0, 'σ': 0, 'ς': 0, 'Ζ': 0, 'ζ': 0,  # sigma, zeta = s, z
    'Τ': 1, 'τ': 1, 'Δ': 1, 'δ': 1,          # tau, delta = t, d
    'Ν': 2, 'ν': 2,                            # nu = n
    'Μ': 3, 'μ': 3,                            # mu = m
    'Ρ': 4, 'ρ': 4,                            # rho = r
    'Λ': 5, 'λ': 5,                            # lambda = l
    'Γ': 6, 'γ': 6,                            # gamma doux = g
    'Κ': 7, 'κ': 7, 'Χ': 7, 'χ': 7,           # kappa, chi = k
    'Φ': 8, 'φ': 8,                            # phi = f
    'Π': 9, 'π': 9, 'Β': 9, 'β': 9,           # pi, beta = p, b

    # Hébreu (sons équivalents)
    'ס': 0, 'ז': 0, 'צ': 0, 'ץ': 0, 'ש': 0,   # samekh, zayin, tsade, shin(s)
    'ת': 1, 'ט': 1, 'ד': 1,                    # tav, tet, dalet
    'נ': 2, 'ן': 2,                            # nun
    'מ': 3, 'ם': 3,                            # mem
    'ר': 4,                                     # resh
    'ל': 5,                                     # lamed
    'ג': 6, 'ש': 6,                            # gimel, shin(sh)
    'כ': 7, 'ך': 7, 'ק': 7,                    # kaf, qof
    'פ': 8, 'ף': 8, 'ו': 8,                    # pe(f), vav
    'פ': 9, 'ב': 9,                            # pe(p), bet

    # Arabe (sons équivalents)
    'س': 0, 'ص': 0, 'ز': 0, 'ث': 0,           # sin, sad, za, tha
    'ت': 1, 'ط': 1, 'د': 1, 'ض': 1,           # ta, ta, dal, dad
    'ن': 2,                                     # nun
    'م': 3,                                     # mim
    'ر': 4,                                     # ra
    'ل': 5,                                     # lam
    'ج': 6, 'ش': 6,                            # jim, shin
    'ك': 7, 'ق': 7, 'خ': 7,                    # kaf, qaf, kha
    'ف': 8,                                     # fa
    'ب': 9, 'پ': 9,                            # ba, pa
}

# Constantes mathématiques sacrées
MATH_CONSTANTS = {
    'π': 3.14159265358979323846,   # Pi - cercle
    'φ': 1.61803398874989484820,   # Phi - nombre d'or
    'e': 2.71828182845904523536,   # Euler - croissance
    'γ': 0.57721566490153286060,   # Euler-Mascheroni
    '√2': 1.41421356237309504880,  # Racine de 2 - diagonale
    '√3': 1.73205080756887729352,  # Racine de 3 - hexagone
    '√5': 2.23606797749978969640,  # Racine de 5 - pentagone
    'τ': 6.28318530717958647692,   # Tau = 2π
    'δ': 4.66920160910299067185,   # Feigenbaum - chaos
    'α': 0.00729735256,            # Constante structure fine ~1/137
    'ℵ₀': float('inf'),            # Aleph-null - infini dénombrable
}

# Lettres = constantes en science
LETTER_CONSTANTS = {
    'Π': ('π', 'Pi', 3.14159, 'Rapport circonférence/diamètre'),
    'Φ': ('φ', 'Phi', 1.61803, 'Nombre d\'or, spirale'),
    'Λ': ('λ', 'Lambda', None, 'Longueur d\'onde'),
    'Σ': ('Σ', 'Sigma', None, 'Somme, écart-type'),
    'Δ': ('Δ', 'Delta', None, 'Changement, différence'),
    'Ω': ('Ω', 'Omega', None, 'Ohm, résistance'),
    'Ψ': ('Ψ', 'Psi', None, 'Fonction d\'onde quantique'),
    'α': ('α', 'Alpha', 0.007297, 'Constante structure fine'),
    'ℏ': ('ℏ', 'h-bar', 1.054e-34, 'Constante de Planck réduite'),
    'c': ('c', 'Celeritas', 299792458, 'Vitesse lumière m/s'),
}

def word_to_number(word: str) -> str:
    """Convertit un mot en nombre via articulations chiffrées"""
    word = word.lower()
    result = []
    i = 0
    while i < len(word):
        # Check digraphs first
        if i < len(word) - 1:
            digraph = word[i:i+2]
            if digraph in ['ch', 'ph']:
                result.append(str(MAJOR_SYSTEM.get(digraph, '')))
                i += 2
                continue

        char = word[i]
        if char in MAJOR_SYSTEM:
            result.append(str(MAJOR_SYSTEM[char]))
        # voyelles ignorées
        i += 1

    return ''.join(result)


def number_to_sounds(num: int) -> list:
    """Convertit un nombre en sons possibles"""
    sounds = {
        0: ['s', 'z'],
        1: ['t', 'd'],
        2: ['n'],
        3: ['m'],
        4: ['r'],
        5: ['l'],
        6: ['j', 'ch'],
        7: ['k', 'q', 'c'],
        8: ['f', 'v'],
        9: ['p', 'b'],
    }
    result = []
    for digit in str(num):
        result.append(sounds.get(int(digit), ['?']))
    return result


def gematria(text: str) -> int:
    """Calcule la valeur numérique d'un texte"""
    total = 0
    for char in text:
        if char in HEBREW_VALUES:
            total += HEBREW_VALUES[char]
        elif char in GREEK_VALUES:
            total += GREEK_VALUES[char]
        elif char in ARABIC_VALUES:
            total += ARABIC_VALUES[char]
    return total


def analyze_math(word: str, script_text: str) -> dict:
    """Analyse mathématique d'un mot"""
    value = gematria(script_text)

    # Propriétés mathématiques
    props = []
    if value > 0:
        # Premier ?
        if value > 1 and all(value % i != 0 for i in range(2, int(value**0.5)+1)):
            props.append("premier")
        # Carré parfait ?
        if int(value**0.5)**2 == value:
            props.append(f"carré({int(value**0.5)}²)")
        # Triangulaire ?
        n = int((2*value)**0.5)
        if n*(n+1)//2 == value:
            props.append(f"triangulaire({n})")
        # Fibonacci ?
        fibs = [1,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987]
        if value in fibs:
            props.append("fibonacci")
        # Divisible par des nombres sacrés
        if value % 7 == 0:
            props.append("÷7")
        if value % 12 == 0:
            props.append("÷12")
        if value % 26 == 0:
            props.append("÷26(YHWH)")

    return {"value": value, "properties": props}


def display_word(word: str):
    """Affiche un mot dans toutes ses graphies"""
    if word not in GLYPHS:
        print(f"Mot inconnu: {word}")
        return

    print(f"\n{'='*50}")
    print(f"  {word}")
    print(f"{'='*50}")

    for script, text in GLYPHS[word].items():
        print(f"  {script:10} : {text}")

    print()


def analyze_letters(text: str):
    """Analyse les lettres d'un texte"""
    print(f"\nAnalyse: {text}")
    print("-" * 40)

    for char in text:
        if char in LETTER_MEANINGS:
            name, meaning = LETTER_MEANINGS[char]
            print(f"  {char} ({name}): {meaning}")


def emit_word(word: str):
    """Émet un mot vers les entités"""
    import json
    from pathlib import Path
    from datetime import datetime

    if word not in GLYPHS:
        return

    event = {
        "timestamp": datetime.now().isoformat(),
        "type": "glyph",
        "word": word,
        "glyphs": GLYPHS[word],
    }

    # Écrit dans le log pour les IAs
    log_file = Path.home() / "ear-to-code" / "logs" / "glyphs.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(event, ensure_ascii=False) + '\n')

    print(json.dumps(event, ensure_ascii=False))


def main():
    import sys

    if len(sys.argv) > 1:
        word = sys.argv[1].upper()
        if word == "ALL":
            for w in KEYWORDS:
                display_word(w)
                emit_word(w)
        elif word == "ANALYZE" and len(sys.argv) > 2:
            analyze_letters(sys.argv[2])
        else:
            display_word(word)
            emit_word(word)
    else:
        print("Mots clés disponibles:")
        for w in KEYWORDS:
            print(f"  - {w}")
        print("\nUsage: glyphs.py <WORD|ALL|ANALYZE text>")


if __name__ == "__main__":
    main()
