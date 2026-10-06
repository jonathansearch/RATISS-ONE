#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tisseur grande échelle — génère echelle/grand.ratum de façon DÉTERMINISTE.
RATISS Labs · graine fixée : même graine, même tissu, toujours.

Usage : python3 outils/tisser_grand.py
"""

import random

SEED = 20261006
N_APPRENTIS = 250        # n000..n249 : le monde connu
N_TEMOINS = 50           # n250..n299 : réservés aux témoins jamais présentés
MOTIFS_APPRIS = 40
MOTIFS_TEMOINS = 10
TAILLE_MOTIF = 5
LIENS_VISES = 1200
COMMUNE = 8
NUIT = 1


def main():
    rng = random.Random(SEED)
    connus = [f"n{i:03d}" for i in range(N_APPRENTIS)]
    frais = [f"n{i:03d}" for i in range(N_APPRENTIS, N_APPRENTIS + N_TEMOINS)]

    motifs = {}   # nom -> [neurones]
    for m in range(MOTIFS_APPRIS):
        motifs[f"C{m:02d}"] = rng.sample(connus, TAILLE_MOTIF)
    for m in range(MOTIFS_TEMOINS):
        bloc = frais[m * TAILLE_MOTIF:(m + 1) * TAILLE_MOTIF]
        motifs[f"T{m:02d}"] = bloc

    liens = set()
    for membres in motifs.values():
        for i in range(len(membres)):
            for j in range(i + 1, len(membres)):
                liens.add(tuple(sorted((membres[i], membres[j]))))
    while len(liens) < LIENS_VISES:  # densification dans le monde connu seul
        a, b = rng.sample(connus, 2)
        liens.add(tuple(sorted((a, b))))

    union = sorted({n for m in range(MOTIFS_APPRIS) for n in motifs[f"C{m:02d}"]})

    lignes = []
    lignes.append("# ============================================================")
    lignes.append("# GRAND TISSU v0.3 — généré par outils/tisser_grand.py (graine 20261006)")
    lignes.append(f"# {N_APPRENTIS + N_TEMOINS} neurones, {len(liens)} liens, "
                  f"{MOTIFS_APPRIS} motifs connus + {MOTIFS_TEMOINS} témoins")
    lignes.append("# Régénérer : python3 outils/tisser_grand.py")
    lignes.append("# ============================================================")
    lignes.append("")
    lignes.append("tissu Echelle")
    lignes.append("")
    for n in connus + frais:
        lignes.append(f"  neurone {n} seuil 50")
    lignes.append("")
    for a, b in sorted(liens):
        lignes.append(f"  lien {a} {b} force 10")
    lignes.append("")
    for nom, membres in motifs.items():
        lignes.append(f"  motif {nom} : " + " ".join(membres))
    lignes.append("  motif TOUT : " + " ".join(union))
    lignes.append("")
    lignes.append("  dire === PHASE 1 : présentation (2 fois chaque connu) ===")
    lignes.append("  répéter 2")
    for m in range(MOTIFS_APPRIS):
        lignes.append(f"    rencontre C{m:02d}")
        lignes.append("    propager")
        lignes.append("    renforcer")
        lignes.append("    repos")
    lignes.append("  fin")
    lignes.append("")
    lignes.append(f"  dire === PHASE 2 : éducation commune ({COMMUNE} fois) ===")
    lignes.append(f"  répéter {COMMUNE}")
    lignes.append("    rencontre TOUT")
    lignes.append("    propager")
    lignes.append("    renforcer")
    lignes.append("    repos")
    lignes.append("  fin")
    lignes.append("")
    lignes.append(f"  dire === PHASE 3 : nuit ({NUIT} fois) ===")
    lignes.append(f"  répéter {NUIT}")
    lignes.append("    oublier")
    lignes.append("  fin")
    lignes.append("")
    lignes.append("  dire === VERDICTS ===")
    for m in range(MOTIFS_APPRIS):
        lignes.append(f"  juger C{m:02d} 30")
    for m in range(MOTIFS_TEMOINS):
        lignes.append(f"  juger T{m:02d} 30")
    lignes.append("  mesurer")
    lignes.append("")
    lignes.append("fin")
    lignes.append("")

    with open("echelle/grand.ratum", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lignes))
    print(f"tissé : {N_APPRENTIS + N_TEMOINS} neurones, {len(liens)} liens, "
          f"union {len(union)} nœuds")


if __name__ == "__main__":
    main()
