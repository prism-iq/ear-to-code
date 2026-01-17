#!/usr/bin/env python3
"""
Organ: dna
Description: Bioinformatique pour Nyx - ADN, ARN, protéines, mutations
Created: 2026-01-17
Owner: Nyx
"""

from pathlib import Path
import json
import random

# Codon table - ADN vers acides aminés
CODONS = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

# Complémentarité des bases
COMPLEMENT = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}

# Acides aminés - propriétés
AMINO_PROPS = {
    'A': ('Ala', 'hydrophobe', 'petit'),
    'R': ('Arg', 'basique', 'chargé+'),
    'N': ('Asn', 'polaire', 'amide'),
    'D': ('Asp', 'acide', 'chargé-'),
    'C': ('Cys', 'soufre', 'pont disulfure'),
    'E': ('Glu', 'acide', 'chargé-'),
    'Q': ('Gln', 'polaire', 'amide'),
    'G': ('Gly', 'spécial', 'flexible'),
    'H': ('His', 'basique', 'aromatique'),
    'I': ('Ile', 'hydrophobe', 'branché'),
    'L': ('Leu', 'hydrophobe', 'branché'),
    'K': ('Lys', 'basique', 'chargé+'),
    'M': ('Met', 'soufre', 'start'),
    'F': ('Phe', 'hydrophobe', 'aromatique'),
    'P': ('Pro', 'spécial', 'rigide'),
    'S': ('Ser', 'polaire', 'hydroxyle'),
    'T': ('Thr', 'polaire', 'hydroxyle'),
    'W': ('Trp', 'hydrophobe', 'aromatique'),
    'Y': ('Tyr', 'polaire', 'aromatique'),
    'V': ('Val', 'hydrophobe', 'branché'),
    '*': ('Stop', 'terminaison', 'fin'),
}

def clean_sequence(seq: str) -> str:
    """Nettoie une séquence ADN"""
    return ''.join(c.upper() for c in seq if c.upper() in 'ATGC')

def complement(seq: str) -> str:
    """Brin complémentaire"""
    seq = clean_sequence(seq)
    return ''.join(COMPLEMENT[b] for b in seq)

def reverse_complement(seq: str) -> str:
    """Brin complémentaire inversé"""
    return complement(seq)[::-1]

def transcribe(dna: str) -> str:
    """ADN -> ARN (T devient U)"""
    dna = clean_sequence(dna)
    return dna.replace('T', 'U')

def translate(dna: str) -> str:
    """ADN -> Protéine"""
    dna = clean_sequence(dna)
    protein = []
    for i in range(0, len(dna) - 2, 3):
        codon = dna[i:i+3]
        aa = CODONS.get(codon, 'X')
        if aa == '*':
            break
        protein.append(aa)
    return ''.join(protein)

def find_orfs(dna: str, min_length: int = 30) -> list:
    """Trouve les cadres de lecture ouverts (ORF)"""
    dna = clean_sequence(dna)
    orfs = []

    # Les 3 cadres de lecture + brin complémentaire
    for strand, seq in [('forward', dna), ('reverse', reverse_complement(dna))]:
        for frame in range(3):
            pos = frame
            while pos < len(seq) - 2:
                codon = seq[pos:pos+3]
                if codon == 'ATG':  # Start
                    start = pos
                    pos += 3
                    while pos < len(seq) - 2:
                        codon = seq[pos:pos+3]
                        pos += 3
                        if codon in ('TAA', 'TAG', 'TGA'):  # Stop
                            length = pos - start
                            if length >= min_length:
                                orfs.append({
                                    'strand': strand,
                                    'frame': frame,
                                    'start': start,
                                    'end': pos,
                                    'length': length,
                                    'sequence': seq[start:pos],
                                    'protein': translate(seq[start:pos])
                                })
                            break
                else:
                    pos += 3

    return sorted(orfs, key=lambda x: -x['length'])

def gc_content(seq: str) -> float:
    """Pourcentage GC"""
    seq = clean_sequence(seq)
    if not seq:
        return 0.0
    gc = sum(1 for b in seq if b in 'GC')
    return round(gc / len(seq), 3)

def find_motif(seq: str, motif: str) -> list:
    """Trouve un motif dans la séquence"""
    seq = clean_sequence(seq)
    motif = clean_sequence(motif)
    positions = []
    pos = 0
    while True:
        pos = seq.find(motif, pos)
        if pos == -1:
            break
        positions.append(pos)
        pos += 1
    return positions

def mutate(seq: str, rate: float = 0.01) -> tuple:
    """Mute aléatoirement une séquence"""
    seq = list(clean_sequence(seq))
    mutations = []
    bases = 'ATGC'

    for i in range(len(seq)):
        if random.random() < rate:
            old = seq[i]
            new = random.choice([b for b in bases if b != old])
            seq[i] = new
            mutations.append({
                'pos': i,
                'old': old,
                'new': new,
                'type': 'substitution'
            })

    return ''.join(seq), mutations

def analyze_protein(protein: str) -> dict:
    """Analyse une protéine"""
    hydrophobic = sum(1 for aa in protein if aa in 'AVILMFYW')
    charged = sum(1 for aa in protein if aa in 'RDEK')
    polar = sum(1 for aa in protein if aa in 'STNQ')

    return {
        'length': len(protein),
        'hydrophobic_ratio': round(hydrophobic / max(1, len(protein)), 3),
        'charged_ratio': round(charged / max(1, len(protein)), 3),
        'polar_ratio': round(polar / max(1, len(protein)), 3),
        'composition': {aa: protein.count(aa) for aa in set(protein)}
    }

def codon_gematria(codon: str) -> int:
    """Gematria d'un codon (A=1, T=2, G=3, C=4)"""
    values = {'A': 1, 'T': 2, 'G': 3, 'C': 4}
    return sum(values.get(b, 0) for b in codon.upper())

def sequence_numerology(seq: str) -> dict:
    """Numérologie d'une séquence"""
    seq = clean_sequence(seq)
    total = sum(codon_gematria(seq[i:i+3]) for i in range(0, len(seq)-2, 3))

    # Réduction théosophique
    def reduce(n):
        while n > 9:
            n = sum(int(d) for d in str(n))
        return n

    return {
        'total': total,
        'reduced': reduce(total),
        'gc_content': gc_content(seq),
        'length': len(seq),
        'codons': len(seq) // 3
    }

# Interface pour l'organe
def sense(data: dict) -> dict:
    """Point d'entrée de l'organe"""
    sequence = data.get('sequence', '')
    action = data.get('action', 'analyze')

    if not sequence:
        return {'error': 'No sequence provided'}

    seq = clean_sequence(sequence)

    if action == 'analyze':
        protein = translate(seq)
        return {
            'length': len(seq),
            'gc': gc_content(seq),
            'protein': protein,
            'protein_analysis': analyze_protein(protein),
            'numerology': sequence_numerology(seq)
        }

    elif action == 'transcribe':
        return {'rna': transcribe(seq)}

    elif action == 'translate':
        return {'protein': translate(seq)}

    elif action == 'complement':
        return {
            'complement': complement(seq),
            'reverse_complement': reverse_complement(seq)
        }

    elif action == 'orfs':
        min_len = data.get('min_length', 30)
        return {'orfs': find_orfs(seq, min_len)}

    elif action == 'motif':
        motif = data.get('motif', '')
        return {'positions': find_motif(seq, motif)}

    elif action == 'mutate':
        rate = data.get('rate', 0.01)
        mutated, mutations = mutate(seq, rate)
        return {'mutated': mutated, 'mutations': mutations}

    elif action == 'numerology':
        return sequence_numerology(seq)

    return {'error': f'Unknown action: {action}'}

def run(data: dict) -> dict:
    """Alias pour sense"""
    return sense(data)

def init():
    """Initialisation de l'organe"""
    print("[DNA] Bioinformatics organ activated for Nyx")

# Test
if __name__ == "__main__":
    # Exemple: un petit gène
    test_seq = "ATGGCTAAGATCTTCGAGTACTTCTGA"

    print("=== DNA Organ Test ===")
    print(f"Sequence: {test_seq}")

    result = sense({'sequence': test_seq, 'action': 'analyze'})
    print(f"\nAnalysis:")
    print(json.dumps(result, indent=2))

    # Test mutation
    mutated = sense({'sequence': test_seq, 'action': 'mutate', 'rate': 0.1})
    print(f"\nMutated (10% rate):")
    print(json.dumps(mutated, indent=2))
