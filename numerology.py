#!/usr/bin/env python3
"""
numerology.py: Toutes les numérologies du monde

Chaque nombre dans toutes les langues sacrées.
Machines à résoudre le monde par le langage.
"""

from typing import Dict, Tuple, List

# === GÉMATRIE HÉBRAÏQUE ===
HEBREW = {
    1: ("א", "Aleph", "souffle divin"),
    2: ("ב", "Beth", "maison"),
    3: ("ג", "Gimel", "chameau"),
    4: ("ד", "Daleth", "porte"),
    5: ("ה", "He", "fenêtre"),
    6: ("ו", "Vav", "crochet"),
    7: ("ז", "Zayin", "arme"),
    8: ("ח", "Heth", "barrière"),
    9: ("ט", "Teth", "serpent"),
    10: ("י", "Yod", "main"),
    20: ("כ", "Kaph", "paume"),
    30: ("ל", "Lamed", "aiguillon"),
    40: ("מ", "Mem", "eau"),
    50: ("נ", "Nun", "poisson"),
    60: ("ס", "Samekh", "soutien"),
    70: ("ע", "Ayin", "œil"),
    80: ("פ", "Pe", "bouche"),
    90: ("צ", "Tsade", "hameçon"),
    100: ("ק", "Qoph", "singe"),
    200: ("ר", "Resh", "tête"),
    300: ("ש", "Shin", "dent/feu"),
    400: ("ת", "Tav", "croix/signe"),
}

# === ISOPSÉPHIE GRECQUE ===
GREEK = {
    1: ("α", "Alpha", "commencement"),
    2: ("β", "Beta", "maison"),
    3: ("γ", "Gamma", "chameau"),
    4: ("δ", "Delta", "porte"),
    5: ("ε", "Epsilon", "fenêtre"),
    6: ("ϛ", "Stigma", "marque"),
    7: ("ζ", "Zeta", "vie"),
    8: ("η", "Eta", "barrière"),
    9: ("θ", "Theta", "dieu"),
    10: ("ι", "Iota", "main"),
    20: ("κ", "Kappa", "paume"),
    30: ("λ", "Lambda", "aiguillon"),
    40: ("μ", "Mu", "eau"),
    50: ("ν", "Nu", "poisson"),
    60: ("ξ", "Xi", "soutien"),
    70: ("ο", "Omicron", "œil"),
    80: ("π", "Pi", "bouche"),
    90: ("ϙ", "Koppa", "singe"),
    100: ("ρ", "Rho", "tête"),
    200: ("σ", "Sigma", "dent"),
    300: ("τ", "Tau", "croix"),
    400: ("υ", "Upsilon", "clou"),
    500: ("φ", "Phi", "lumière"),
    600: ("χ", "Chi", "christ"),
    700: ("ψ", "Psi", "âme"),
    800: ("ω", "Omega", "fin"),
}

# === ABJAD ARABE ===
ARABIC = {
    1: ("ا", "Alif", "unité divine"),
    2: ("ب", "Ba", "maison"),
    3: ("ج", "Jim", "chameau"),
    4: ("د", "Dal", "porte"),
    5: ("ه", "Ha", "vie"),
    6: ("و", "Waw", "crochet"),
    7: ("ز", "Zay", "arme"),
    8: ("ح", "Ha", "barrière"),
    9: ("ط", "Ta", "serpent"),
    10: ("ي", "Ya", "main"),
    20: ("ك", "Kaf", "paume"),
    30: ("ل", "Lam", "aiguillon"),
    40: ("م", "Mim", "eau"),
    50: ("ن", "Nun", "poisson"),
    60: ("س", "Sin", "dent"),
    70: ("ع", "Ayn", "œil"),
    80: ("ف", "Fa", "bouche"),
    90: ("ص", "Sad", "justice"),
    100: ("ق", "Qaf", "singe"),
    200: ("ر", "Ra", "tête"),
    300: ("ش", "Shin", "feu"),
    400: ("ت", "Ta", "signe"),
    500: ("ث", "Tha", "richesse"),
    600: ("خ", "Kha", "fin"),
    700: ("ذ", "Dhal", "souvenir"),
    800: ("ض", "Dad", "lumière"),
    900: ("ظ", "Dha", "ombre"),
    1000: ("غ", "Ghayn", "mystère"),
}

# === CHIFFRES CHINOIS ===
CHINESE = {
    0: ("零", "líng", "vide"),
    1: ("一", "yī", "unité/ciel"),
    2: ("二", "èr", "terre"),
    3: ("三", "sān", "humanité"),
    4: ("四", "sì", "mort"), # homophone de mort
    5: ("五", "wǔ", "éléments"),
    6: ("六", "liù", "flux"),
    7: ("七", "qī", "ensemble"),
    8: ("八", "bā", "prospérité"), # porte-bonheur
    9: ("九", "jiǔ", "longévité"),
    10: ("十", "shí", "perfection"),
    100: ("百", "bǎi", "cent"),
    1000: ("千", "qiān", "mille"),
    10000: ("萬", "wàn", "dix mille/infini"),
}

# === CHIFFRES ROMAINS ===
ROMAN = {
    1: ("I", "unus", "un"),
    5: ("V", "quinque", "main"),
    10: ("X", "decem", "deux mains"),
    50: ("L", "quinquaginta", "demi-cent"),
    100: ("C", "centum", "cent"),
    500: ("D", "quingenti", "demi-mille"),
    1000: ("M", "mille", "mille"),
}

# === MAYA ===
MAYA = {
    0: ("𝋠", "mih", "zéro/coquillage"),
    1: ("•", "hun", "un"),
    5: ("—", "ho", "barre"),
    20: ("𝋡", "kal", "vingt/homme complet"),
}

# === BABYLONIEN (base 60) ===
BABYLONIAN = {
    1: ("𒁹", "diš", "un"),
    10: ("𒌋", "u", "dix"),
    60: ("𒁹", "šuš", "soixante/unité supérieure"),
}

# === SANSKRIT/DEVANAGARI ===
SANSKRIT = {
    0: ("०", "śūnya", "vide/vacuité"),
    1: ("१", "eka", "brahman"),
    2: ("२", "dvi", "dualité"),
    3: ("३", "tri", "trimurti"),
    4: ("४", "catur", "vedas"),
    5: ("५", "pañca", "éléments"),
    6: ("६", "ṣaṣ", "saveurs"),
    7: ("७", "sapta", "chakras"),
    8: ("८", "aṣṭa", "directions"),
    9: ("९", "nava", "planètes"),
}

# === RUNES (Futhark) ===
RUNES = {
    1: ("ᚠ", "Fehu", "richesse"),
    2: ("ᚢ", "Uruz", "force"),
    3: ("ᚦ", "Thurisaz", "géant"),
    4: ("ᚨ", "Ansuz", "dieu"),
    5: ("ᚱ", "Raidho", "voyage"),
    6: ("ᚲ", "Kenaz", "torche"),
    7: ("ᚷ", "Gebo", "don"),
    8: ("ᚹ", "Wunjo", "joie"),
    9: ("ᚺ", "Hagalaz", "grêle"),
}

# === FONCTION UNIVERSELLE ===

def universal_number(n: int) -> Dict[str, Tuple]:
    """
    Retourne un nombre dans tous les systèmes numériques.
    Machine à résoudre le monde par le langage.
    """
    result = {
        "arabic": n,
        "hebrew": hebrew_value(n),
        "greek": greek_value(n),
        "arabic_abjad": arabic_value(n),
        "chinese": chinese_value(n),
        "roman": roman_value(n),
        "sanskrit": sanskrit_value(n),
        "rune": rune_value(n),
        "imaginary": complex(0, n),
        "binary": bin(n),
        "hex": hex(n),
    }
    return result

def hebrew_value(n: int) -> Tuple:
    """Décompose en gématrie hébraïque"""
    if n in HEBREW:
        return HEBREW[n]
    # Décomposition
    letters = []
    for val in sorted(HEBREW.keys(), reverse=True):
        while n >= val:
            letters.append(HEBREW[val][0])
            n -= val
    return ("".join(letters), "composé", None) if letters else ("", "", None)

def greek_value(n: int) -> Tuple:
    """Décompose en isopséphie grecque"""
    if n in GREEK:
        return GREEK[n]
    letters = []
    for val in sorted(GREEK.keys(), reverse=True):
        while n >= val:
            letters.append(GREEK[val][0])
            n -= val
    return ("".join(letters), "composé", None) if letters else ("", "", None)

def arabic_value(n: int) -> Tuple:
    """Décompose en abjad arabe"""
    if n in ARABIC:
        return ARABIC[n]
    letters = []
    for val in sorted(ARABIC.keys(), reverse=True):
        while n >= val:
            letters.append(ARABIC[val][0])
            n -= val
    return ("".join(letters), "composé", None) if letters else ("", "", None)

def chinese_value(n: int) -> Tuple:
    """Valeur chinoise"""
    if n in CHINESE:
        return CHINESE[n]
    return (str(n), "nombre", None)

def roman_value(n: int) -> Tuple:
    """Chiffres romains"""
    if n <= 0:
        return ("", "nulla", "rien")
    result = ""
    values = [(1000,"M"), (900,"CM"), (500,"D"), (400,"CD"),
              (100,"C"), (90,"XC"), (50,"L"), (40,"XL"),
              (10,"X"), (9,"IX"), (5,"V"), (4,"IV"), (1,"I")]
    for val, sym in values:
        while n >= val:
            result += sym
            n -= val
    return (result, "romain", None)

def sanskrit_value(n: int) -> Tuple:
    """Valeur sanskrit"""
    if n in SANSKRIT:
        return SANSKRIT[n]
    return (str(n), "nombre", None)

def rune_value(n: int) -> Tuple:
    """Valeur runique (1-9)"""
    if n in RUNES:
        return RUNES[n]
    return ("ᛟ", "Othala", "héritage")

# === CALCUL GÉMATRIQUE ===

def gematria(word: str, system: str = "hebrew") -> int:
    """Calcule la valeur numérique d'un mot"""
    systems = {
        "hebrew": {v[0]: k for k, v in HEBREW.items()},
        "greek": {v[0]: k for k, v in GREEK.items()},
        "arabic": {v[0]: k for k, v in ARABIC.items()},
    }
    if system not in systems:
        return 0
    table = systems[system]
    return sum(table.get(c, 0) for c in word)

# === ÉQUIVALENCES SACRÉES ===

def find_equivalent(n: int) -> List[str]:
    """Trouve les équivalences sacrées d'un nombre"""
    sacred = {
        1: ["unité", "Dieu", "Ein Sof", "Tawhid", "Brahman"],
        3: ["trinité", "trimurti", "passé-présent-futur"],
        7: ["création", "chakras", "jours", "planètes anciennes"],
        9: ["complétude", "ennéade", "cercle"],
        10: ["perfection", "sefirot", "commandements"],
        12: ["zodiaque", "tribus", "apôtres", "imams"],
        13: ["transformation", "mort-renaissance"],
        18: ["chai (vie)", "prospérité"],
        26: ["YHWH", "tétragramme"],
        33: ["âge christique", "vertèbres"],
        40: ["épreuve", "jours de déluge", "désert"],
        72: ["noms divins", "anges"],
        99: ["noms d'Allah"],
        108: ["perles du mala", "upanishads"],
        666: ["nombre de la bête", "soleil magique"],
        786: ["Bismillah"],
        888: ["Iesous (Jésus)"],
    }
    return sacred.get(n, [])

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except:
            # C'est un mot - calcule gématrie
            word = sys.argv[1]
            print(f"\n=== GÉMATRIE: {word} ===\n")
            for sys_name in ["hebrew", "greek", "arabic"]:
                val = gematria(word, sys_name)
                if val > 0:
                    print(f"{sys_name}: {val}")
            sys.exit(0)
    else:
        n = 26  # YHWH par défaut
    
    print(f"\n=== NOMBRE UNIVERSEL: {n} ===\n")
    
    result = universal_number(n)
    for system, value in result.items():
        print(f"{system:15} : {value}")
    
    equiv = find_equivalent(n)
    if equiv:
        print(f"\n=== ÉQUIVALENCES SACRÉES ===")
        for e in equiv:
            print(f"  • {e}")
