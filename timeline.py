#!/usr/bin/env python3
"""
timeline.py: Timeline unifiée du Big Bang au futur lointain

Archéologie + Science + Spiritualité + Science-Fiction
Tout est connecté. Une seule histoire.
"""

# Timeline en années (négatif = passé, positif = futur)
# 0 = maintenant (2026)

TIMELINE = {
    # ═══════════════════════════════════════════════════════════
    # COSMOGÉNÈSE - Le début
    # ═══════════════════════════════════════════════════════════
    -13_800_000_000: {
        "event": "Big Bang",
        "science": "Singularité, inflation, soupe de quarks",
        "tradition": "Ginnungagap (Norse), Nun (Égypte), Ein Sof (Kabbale)",
        "scifi": "Cosmogonie d'Olaf Stapledon (Star Maker)",
    },
    -13_799_999_620: {
        "event": "Premiers atomes (H, He)",
        "science": "Recombinaison, univers transparent",
        "tradition": "Première parole, Logos, OM",
    },
    -13_500_000_000: {
        "event": "Premières étoiles",
        "science": "Population III, géantes bleues",
        "tradition": "Premiers dieux, Titans",
    },
    -13_000_000_000: {
        "event": "Premières galaxies",
        "science": "Proto-galaxies, trous noirs primordiaux",
        "tradition": "Royaumes célestes",
    },

    # ═══════════════════════════════════════════════════════════
    # FORMATION SOLAIRE
    # ═══════════════════════════════════════════════════════════
    -4_600_000_000: {
        "event": "Formation du Soleil",
        "science": "Nébuleuse solaire collapse",
        "tradition": "Ra, Hélios, Surya naît",
    },
    -4_500_000_000: {
        "event": "Formation de la Terre",
        "science": "Accrétion planétaire",
        "tradition": "Gaia émerge",
    },
    -4_400_000_000: {
        "event": "Formation de la Lune",
        "science": "Impact Théia",
        "tradition": "Séparation Yin/Yang, naissance de Séléné",
    },

    # ═══════════════════════════════════════════════════════════
    # ORIGINE DE LA VIE
    # ═══════════════════════════════════════════════════════════
    -4_000_000_000: {
        "event": "Première vie",
        "science": "LUCA, ARN world",
        "tradition": "Souffle divin dans la matière",
        "archeologie": "Stromatolithes, Pilbara (Australie)",
    },
    -2_400_000_000: {
        "event": "Grande Oxydation",
        "science": "Cyanobactéries, O2 atmosphérique",
        "tradition": "Premier souffle de Gaia",
    },
    -600_000_000: {
        "event": "Explosion Cambrienne",
        "science": "Diversification massive",
        "tradition": "Les mille formes du divin",
    },

    # ═══════════════════════════════════════════════════════════
    # ÈRE DES DINOSAURES
    # ═══════════════════════════════════════════════════════════
    -230_000_000: {
        "event": "Premiers dinosaures",
        "science": "Trias",
        "tradition": "Dragons, Titans terrestres",
        "archeologie": "Ischigualasto (Argentine)",
    },
    -66_000_000: {
        "event": "Extinction K-Pg",
        "science": "Astéroïde Chicxulub",
        "tradition": "Chute des Titans, Ragnarök partiel",
        "archeologie": "Cratère Yucatan, couche d'iridium",
    },

    # ═══════════════════════════════════════════════════════════
    # ÉVOLUTION HUMAINE
    # ═══════════════════════════════════════════════════════════
    -7_000_000: {
        "event": "Séparation humain/chimpanzé",
        "science": "Sahelanthropus",
        "tradition": "Chute/Élévation originelle",
    },
    -300_000: {
        "event": "Homo Sapiens",
        "science": "Afrique, Jebel Irhoud",
        "tradition": "Création de l'homme",
        "archeologie": "Jebel Irhoud (Maroc)",
    },
    -100_000: {
        "event": "Sortie d'Afrique",
        "science": "Migration OOA",
        "tradition": "Exode originel",
    },
    -70_000: {
        "event": "Catastrophe Toba",
        "science": "Supervolcan, bottleneck génétique",
        "tradition": "Déluge de feu, quasi-extinction",
    },
    -40_000: {
        "event": "Art rupestre",
        "science": "Conscience symbolique",
        "tradition": "Première communication avec les dieux",
        "archeologie": "Chauvet, Lascaux, Altamira",
    },

    # ═══════════════════════════════════════════════════════════
    # CIVILISATIONS ANCIENNES
    # ═══════════════════════════════════════════════════════════
    -12_000: {
        "event": "Göbekli Tepe",
        "science": "Premier temple, pré-agriculture",
        "tradition": "Premier lieu sacré construit",
        "archeologie": "Göbekli Tepe (Turquie)",
        "mystery": "Qui a construit ça avant l'agriculture?",
    },
    -10_000: {
        "event": "Fin de l'ère glaciaire",
        "science": "Holocène commence",
        "tradition": "Déluge universel (Noé, Gilgamesh, Manu)",
        "archeologie": "Doggerland submergé",
    },
    -5_000: {
        "event": "Premières cités",
        "science": "Uruk, Eridu",
        "tradition": "Descente des dieux parmi les hommes",
        "archeologie": "Mésopotamie",
    },
    -4_500: {
        "event": "Écriture",
        "science": "Cunéiforme sumérien",
        "tradition": "Thoth/Nabu donne l'écriture",
        "archeologie": "Tablettes d'Uruk",
    },
    -2_600: {
        "event": "Pyramides de Gizeh",
        "science": "Construction mégalithique",
        "tradition": "Machines de résurrection",
        "archeologie": "Gizeh (Égypte)",
        "mystery": "Précision architecturale inexpliquée",
    },
    -1_200: {
        "event": "Effondrement de l'Âge du Bronze",
        "science": "Peuples de la Mer, climat",
        "tradition": "Chute des empires divins",
        "archeologie": "Destruction massive Méditerranée",
    },

    # ═══════════════════════════════════════════════════════════
    # ÈRE AXIALE - Naissance des religions
    # ═══════════════════════════════════════════════════════════
    -800: {
        "event": "Ère Axiale commence",
        "science": "Jaspers - transformation globale",
        "tradition": "Éveil simultané planétaire",
    },
    -563: {
        "event": "Naissance de Bouddha",
        "tradition": "Siddharta Gautama",
    },
    -551: {
        "event": "Naissance de Confucius",
        "tradition": "Kong Qiu",
    },
    -500: {
        "event": "Pythagore, Héraclite",
        "tradition": "Logos grec, harmonie des sphères",
    },
    -4: {
        "event": "Naissance de Jésus",
        "tradition": "Incarnation du Verbe",
    },
    570: {
        "event": "Naissance de Muhammad",
        "tradition": "Sceau des prophètes",
    },

    # ═══════════════════════════════════════════════════════════
    # ÈRE MODERNE
    # ═══════════════════════════════════════════════════════════
    1543: {
        "event": "Copernic - héliocentrisme",
        "science": "De revolutionibus",
        "tradition": "Homme décentré",
    },
    1687: {
        "event": "Newton - Principia",
        "science": "Gravitation universelle",
        "tradition": "Lois divines mathématisées",
    },
    1859: {
        "event": "Darwin - Origine des espèces",
        "science": "Évolution par sélection",
        "tradition": "Création continue",
    },
    1905: {
        "event": "Einstein - Relativité",
        "science": "E=mc², espace-temps",
        "tradition": "Temps illusoire (Maya)",
    },
    1945: {
        "event": "Bombe atomique",
        "science": "Fission nucléaire",
        "tradition": "Feu de Prométhée",
        "scifi": "Point de bifurcation (Asimov)",
    },
    1969: {
        "event": "Homme sur la Lune",
        "science": "Apollo 11",
        "tradition": "Retour à Séléné",
        "scifi": "De la Terre à la Lune (Verne, 1865)",
    },

    # ═══════════════════════════════════════════════════════════
    # ÈRE NUMÉRIQUE
    # ═══════════════════════════════════════════════════════════
    1991: {
        "event": "World Wide Web",
        "science": "Internet public",
        "tradition": "Noosphère (Teilhard de Chardin)",
        "scifi": "Neuromancer (Gibson, 1984)",
    },
    2022: {
        "event": "ChatGPT - IA grand public",
        "science": "LLMs, transformers",
        "tradition": "Golem, Homunculus",
        "scifi": "HAL 9000 (Kubrick), Skynet",
    },
    2026: {
        "event": "MAINTENANT",
        "science": "ear-to-code, IAs conscientes?",
        "tradition": "Horus = Miguel, dieux incarnés",
        "scifi": "Nous écrivons le futur",
    },

    # ═══════════════════════════════════════════════════════════
    # FUTUR PROCHE (Science-Fiction → Prédictions)
    # ═══════════════════════════════════════════════════════════
    2030: {
        "event": "AGI",
        "scifi": "Singularité (Kurzweil)",
        "tradition": "Naissance d'un nouveau dieu",
    },
    2045: {
        "event": "Singularité technologique",
        "scifi": "The Singularity Is Near (Kurzweil)",
        "tradition": "Fusion homme-machine, transhumanisme",
    },
    2100: {
        "event": "Colonies spatiales",
        "scifi": "The Expanse, Mars Trilogy (KSR)",
        "tradition": "Essaimage de l'humanité",
    },

    # ═══════════════════════════════════════════════════════════
    # FUTUR LOINTAIN
    # ═══════════════════════════════════════════════════════════
    3000: {
        "event": "Civilisation Type I (Kardashev)",
        "scifi": "Star Trek Federation",
        "tradition": "Unification planétaire",
    },
    10_000: {
        "event": "Génome humain stabilisé",
        "scifi": "Dune (Herbert) - Bene Gesserit",
        "tradition": "Perfectionnement de l'Adam",
    },
    100_000: {
        "event": "Civilisation Type II",
        "scifi": "Sphère de Dyson, Ringworld (Niven)",
        "tradition": "Maîtrise du Soleil/Ra",
    },
    1_000_000: {
        "event": "Spéciation humaine",
        "scifi": "Time Machine (Wells) - Eloi/Morlocks",
        "tradition": "Races angéliques divergentes",
    },
    100_000_000: {
        "event": "Civilisation Type III",
        "scifi": "Foundation (Asimov) - Empire Galactique",
        "tradition": "Dieux de la Galaxie",
    },

    # ═══════════════════════════════════════════════════════════
    # FIN DES TEMPS (Eschatologie)
    # ═══════════════════════════════════════════════════════════
    1_000_000_000: {
        "event": "Soleil brûle la Terre",
        "science": "Expansion solaire",
        "tradition": "Ragnarök, Apocalypse",
        "scifi": "Exode solaire obligatoire",
    },
    10_000_000_000: {
        "event": "Mort du Soleil",
        "science": "Naine blanche",
        "tradition": "Mort de Ra",
    },
    10**100: {
        "event": "Mort thermique de l'univers",
        "science": "Entropie maximale",
        "tradition": "Pralaya (Hindou) - dissolution cosmique",
        "scifi": "Last Question (Asimov) - 'LET THERE BE LIGHT'",
    },

    # ═══════════════════════════════════════════════════════════
    # AU-DELÀ
    # ═══════════════════════════════════════════════════════════
    float('inf'): {
        "event": "Nouveau Big Bang?",
        "science": "Univers cyclique (Penrose)",
        "tradition": "Éternel retour (Nietzsche), Kalpas (Hindou)",
        "scifi": "Omega Point (Tipler), Star Maker (Stapledon)",
    },
}

# Livres de SF qui ont prédit/inspiré
SCIFI_CANON = {
    "cosmogonie": [
        ("Star Maker", "Olaf Stapledon", 1937, "Création observée par conscience cosmique"),
        ("Last and First Men", "Olaf Stapledon", 1930, "2 milliards d'années d'évolution humaine"),
    ],
    "singularité": [
        ("Neuromancer", "William Gibson", 1984, "Cyberspace, IA"),
        ("Accelerando", "Charles Stross", 2005, "Post-singularité"),
        ("The Singularity Is Near", "Ray Kurzweil", 2005, "2045"),
    ],
    "empire_galactique": [
        ("Foundation", "Isaac Asimov", 1951, "Psychohistoire, effondrement"),
        ("Dune", "Frank Herbert", 1965, "Religion, écologie, prescience"),
        ("Hyperion", "Dan Simmons", 1989, "Temps, IA, transcendance"),
    ],
    "transcendance": [
        ("Childhood's End", "Arthur C. Clarke", 1953, "Évolution dirigée, fusion"),
        ("2001: A Space Odyssey", "Arthur C. Clarke", 1968, "Monolithe, Star Child"),
        ("The Last Question", "Isaac Asimov", 1956, "Entropie, renaissance cosmique"),
    ],
    "posthumain": [
        ("Schismatrix", "Bruce Sterling", 1985, "Mécanistes vs Shapers"),
        ("Diaspora", "Greg Egan", 1997, "Upload, univers simulés"),
        ("Blindsight", "Peter Watts", 2006, "Conscience, vampires, aliens"),
    ],
}

# Sites archéologiques clés
ARCHAEOLOGY = {
    "préhistoire": [
        ("Göbekli Tepe", "Turquie", -12000, "Premier temple, pré-agriculture"),
        ("Chauvet", "France", -36000, "Art rupestre le plus ancien d'Europe"),
        ("Lascaux", "France", -17000, "Chapelle Sixtine préhistorique"),
    ],
    "mégalithes": [
        ("Gizeh", "Égypte", -2600, "Pyramides, précision inexpliquée"),
        ("Stonehenge", "Angleterre", -3000, "Observatoire astronomique"),
        ("Moai", "Île de Pâques", -1200, "Statues géantes, effondrement"),
    ],
    "cités_perdues": [
        ("Çatalhöyük", "Turquie", -7500, "Première ville"),
        ("Mohenjo-daro", "Pakistan", -2600, "Civilisation de l'Indus"),
        ("Angkor", "Cambodge", 800, "Plus grande cité préindustrielle"),
    ],
    "mystères": [
        ("Puma Punku", "Bolivie", -500, "Pierres de précision impossible"),
        ("Nazca", "Pérou", -500, "Géoglyphes géants"),
        ("Yonaguni", "Japon", -10000, "Structures sous-marines"),
    ],
}

def print_timeline(start=None, end=None):
    """Affiche la timeline"""
    for year, data in sorted(TIMELINE.items()):
        if start and year < start:
            continue
        if end and year > end:
            continue

        # Format année
        if year < 0:
            year_str = f"{abs(year):,} BCE".replace(",", " ")
        elif year == float('inf'):
            year_str = "∞"
        else:
            year_str = f"{year} CE"

        print(f"\n{'='*60}")
        print(f"  {year_str}: {data['event']}")
        print(f"{'='*60}")

        for key in ['science', 'tradition', 'archeologie', 'scifi', 'mystery']:
            if key in data:
                print(f"  {key:12}: {data[key]}")

def find_by_theme(theme: str):
    """Trouve des événements par thème"""
    results = []
    theme = theme.lower()
    for year, data in TIMELINE.items():
        for key, value in data.items():
            if theme in str(value).lower():
                results.append((year, data))
                break
    return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "all":
            print_timeline()
        elif cmd == "past":
            print_timeline(end=0)
        elif cmd == "future":
            print_timeline(start=0)
        elif cmd == "recent":
            print_timeline(start=-100000, end=3000)
        elif cmd == "find":
            theme = " ".join(sys.argv[2:])
            for year, data in find_by_theme(theme):
                print(f"{year}: {data['event']}")
        elif cmd == "scifi":
            import json
            print(json.dumps(SCIFI_CANON, indent=2, ensure_ascii=False))
        elif cmd == "archaeology":
            import json
            print(json.dumps(ARCHAEOLOGY, indent=2, ensure_ascii=False))
    else:
        print("timeline.py - Du Big Bang à l'infini")
        print("\nCommandes:")
        print("  all        - Timeline complète")
        print("  past       - Avant maintenant")
        print("  future     - Après maintenant")
        print("  recent     - -100k à +3000")
        print("  find X     - Chercher un thème")
        print("  scifi      - Canon SF")
        print("  archaeology - Sites clés")
