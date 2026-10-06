#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PONT VOIX v1 — transcription (texte) -> motifs Ratum -> écoute du tissu.
RATISS Labs · déterministe : même texte, même programme, toujours.

En production, le texte vient de Phonon-2 (audio -> texte).
Ici, l'oreille est SIMULÉE : on donne le texte avec --texte, le pont
fait tout le reste (génère ecoute.ratum, prêt à tourner).

Usage : python3 porte-voix/pont.py --texte "soleil lune comete banane"
Puis  : python3 ratum.py porte-voix/ecoute.ratum
"""

import argparse
import os

# Vocabulaire du pont : mot entendu -> (motif, membres)
VOCAB = {
    "soleil": ("MSOLEIL", ["mot_soleil", "chaud", "lumiere"]),
    "lune": ("MLUNE", ["mot_lune", "froid", "lumiere"]),
    "comete": ("MCOMETE", ["mot_comete", "lointain"]),
}

LIENS = [
    ("mot_soleil", "chaud"), ("mot_soleil", "lumiere"), ("chaud", "lumiere"),
    ("mot_lune", "froid"), ("mot_lune", "lumiere"), ("froid", "lumiere"),
    ("mot_comete", "lointain"),
]

TOUT = ["mot_soleil", "mot_lune", "chaud", "froid", "lumiere"]


def construire(transcription):
    mots = transcription.strip().lower().split()
    reconnus = [m for m in mots if m in VOCAB]
    inconnus = [m for m in mots if m not in VOCAB]

    neurones = sorted({n for _, membres in VOCAB.values() for n in membres} | set(TOUT))
    L = []
    L.append("# ============================================================")
    L.append("# ECOUTE — généré par porte-voix/pont.py (déterministe)")
    L.append(f"# Transcription reçue : {' '.join(mots) if mots else '(silence)'}")
    L.append("# Régénérer : python3 porte-voix/pont.py --texte \"...\"")
    L.append("# ============================================================")
    L.append("")
    L.append("tissu Ecoute")
    L.append("")
    for n in neurones:
        L.append(f"  neurone {n} seuil 50")
    L.append("")
    for a, b in LIENS:
        L.append(f"  lien {a} {b} force 10")
    L.append("")
    for mot, (motif, membres) in VOCAB.items():
        L.append(f"  motif {motif} : " + " ".join(membres))
    L.append("  motif TOUT : " + " ".join(TOUT))
    L.append("")
    L.append("  dire === EDUCATION (commune x9, nuit x2) ===")
    L.append("  répéter 9")
    L.append("    rencontre TOUT")
    L.append("    propager")
    L.append("    renforcer")
    L.append("    repos")
    L.append("  fin")
    L.append("  répéter 2")
    L.append("    oublier")
    L.append("  fin")
    L.append("")
    L.append("  dire === ECOUTE ===")
    if not reconnus and not inconnus:
        L.append('  dire silence : rien à écouter')
    for mot in reconnus:
        motif, _ = VOCAB[mot]
        L.append(f"  rencontre {motif}")
        L.append("  propager")
        L.append(f"  dire entendu {mot} : le tissu tient à résonance {motif} sur 100")
        L.append("  repos")
        L.append(f"  si {motif} tient 60 alors")
        L.append(f"    dire le tissu comprend {mot}")
        L.append("  sinon")
        L.append(f"    dire le tissu ne comprend pas {mot}")
        L.append("  fin")
    for mot in inconnus:
        L.append(f"  dire mot hors vocabulaire : {mot}")
    L.append("  mesurer")
    L.append("")
    L.append("fin")
    L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Pont voix : texte -> Ratum")
    ap.add_argument("--texte", default="", help="transcription (oreille simulée)")
    args = ap.parse_args()
    base = os.path.dirname(os.path.abspath(__file__))
    cible = os.path.join(base, "ecoute.ratum")
    with open(cible, "w", encoding="utf-8") as fh:
        fh.write(construire(args.texte))
    print(f"écoute générée : {cible}")


if __name__ == "__main__":
    main()
