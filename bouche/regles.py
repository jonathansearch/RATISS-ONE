#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RÈGLES DE SORTIE v1 — le tokenizer : la pensée devient phrase.
RATISS Labs · MIT.

Le tissu résonne, les secteurs gardent : ici on TRADUIT l'état en phrase,
puis la bouche (Piper) la parle. Quatre règles tiny, déterministes, hors-ligne :
  R-ULTRA : des convictions ? → "Je tiens pour sûr : ..."
  R-SANCT : un sanctuaire ? → "Au sanctuaire : ..."
  R-TISSU : des mots tenus ? → "Je tiens A et B. Le reste reste dehors."
  R-VIDE  : rien ? → "Je ne tiens rien. Tout reste dehors."
Zéro est singulier, partout, explicitement.

Usage : python3 bouche/regles.py --demo EN [--wav bouche/preuve.wav]
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cerveau.cerveau import Cerveau, MOTS, MOTS_FR  # noqa: E402

INV = {"EN": {v: k for k, v in MOTS.items()}, "FR": {v: k for k, v in MOTS_FR.items()}}


def lire_etat(c):
    """Lit l'état traduisible : convictions + sanctuaire + tissu (100 % JSON)."""
    return {
        "langue": c.langue,
        "ultra": [{"mots": list(t.mots), "force": t.force}
                  for t in c.secteurs["ULTRA-SECTEUR"].top(3)],
        "sanctuaire": list(c.secteurs["SANCTUAIRE"].top(1)[0].mots)
        if c.secteurs["SANCTUAIRE"].traces else None,
        "refrain_n": len(c.secteurs["REFRAIN"].traces),
        "tissu": {m: c.resonance(c.mots_connus[m]) for m in c.entendus},
    }


def joindre(items, langue):
    if len(items) == 1:
        return items[0]
    mot = "et" if langue == "FR" else "and"
    if len(items) == 2:
        return f"{items[0]} {mot} {items[1]}"
    return ", ".join(items[:-1]) + f" {mot} " + items[-1]


def mot_de(motif, langue):
    return INV[langue].get(motif, motif.lower())


def formuler_tissu(tenus, langue):
    if not tenus:
        return ("Je ne tiens rien. Tout reste dehors." if langue == "FR"
                else "I hold nothing. Everything stays outside.")
    if langue == "FR":
        return f"Je tiens {joindre(tenus, langue)}. Le reste reste dehors."
    return f"I hold {joindre(tenus, langue)}. The rest stays outside."


def formuler(etat, langue=None):
    """R-ULTRA + R-SANCT + R-TISSU/R-VIDE, dans cet ordre, vides sautés."""
    langue = langue or etat["langue"]
    parts = []
    if etat["ultra"]:
        noms = [mot_de(t["mots"][1], langue) for t in etat["ultra"]]
        parts.append((f"Je tiens pour sûr : {joindre(noms, langue)}." if langue == "FR"
                      else f"I hold as certain: {joindre(noms, langue)}."))
    if etat["sanctuaire"]:
        top = " ".join(etat["sanctuaire"])
        parts.append(f"Au sanctuaire : {top}." if langue == "FR"
                     else f"In the sanctuary: {top}.")
    tenus = [m for m, v in etat["tissu"].items() if v >= 60]
    parts.append(formuler_tissu(tenus, langue))
    return " ".join(parts)


def parler(phrase, voix, sortie):
    proc = subprocess.run(
        [sys.executable, "-m", "piper", "--model", voix, "--output_file", sortie],
        input=phrase, capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0


def demo(langue):
    c = Cerveau(langue)
    seqs = ([["fellow", "americans", "ask"]] if langue == "EN"
            else [["amis", "du", "peuple"]])
    for _ in range(9):
        for s in seqs:
            c.entendre_sequence(s)
    c.nuit()
    for _ in range(3):
        for s in seqs:
            c.entendre_sequence(s)
    c.nuit()
    return c


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", choices=["EN", "FR"], default="EN")
    ap.add_argument("--wav", default=None)
    ap.add_argument("--marbre", action="store_true",
                    help="phase 3 : 3 relectures (gravure) + 5 nuits avant de parler")
    ap.add_argument("--tempete", action="store_true",
                    help="phase 4 : gravure + tempête de 70 inconnues + 5 nuits avant de parler")
    ap.add_argument("--chaos", action="store_true",
                    help="phase 5 : JFK réel entendu 1 fois (sans focus) + 4 nuits de rêve "
                         "+ gravure de l'élue + 2 nuits avant de parler")
    args = ap.parse_args()
    if args.chaos:
        from cerveau.autotest_chaos import MOTS_JFK  # discours réel archivé
        c = Cerveau("EN")
        for i in range(len(MOTS_JFK) - 2):
            c.entendre_sequence(MOTS_JFK[i:i + 3])
        reves = sum(c.nuit()["reves"] for _ in range(4))
        for _ in range(3):
            c.redire()
        for _ in range(2):
            c.nuit()
        top = c.secteurs["SANCTUAIRE"].top(1)[0]
        print(f"chaos : JFK 20 fenêtres x1 écoute, {reves} rêves en 4 nuits")
        print(f"élue : {top} (sans focus, sans filet)")
        phrase = formuler(lire_etat(c))
        print(f"dit : {phrase}")
        if args.wav:
            print(args.wav + " écrit" if parler(phrase, "bouche/voix/en_US-lessac-medium.onnx", args.wav) else "ÉCHEC bouche")
        return 0
    c = demo(args.demo)
    if args.marbre:
        for _ in range(3):
            c.redire()
        for _ in range(5):
            c.nuit()
        top = c.secteurs["SANCTUAIRE"].top(1)[0]
        print(f"gravé : {top} (3 relectures + 5 nuits)")
    if args.tempete:
        for _ in range(3):
            c.redire()
        for i in range(70):
            c.entendre_sequence([f"mot{i}", f"bruit{i}", f"vague{i}"])
        pression = len(c.secteurs["VIF"].traces)
        for _ in range(5):
            c.nuit()
        top = c.secteurs["SANCTUAIRE"].top(1)[0]
        nv = len(c.secteurs["VIF"].traces)
        print(f"tempête : 70 inconnues, pression {pression}, mer calme (VIF {nv})")
        print(f"statue : {top} (parle encore après la tempête)")
    phrase = formuler(lire_etat(c))
    print(f"dit : {phrase}")
    if args.wav:
        voix = ("bouche/voix/en_US-lessac-medium.onnx" if args.demo == "EN"
                else "bouche/voix/fr_FR-siwis-medium.onnx")
        print(args.wav + " écrit" if parler(phrase, voix, args.wav) else "ÉCHEC bouche")
    return 0


if __name__ == "__main__":
    sys.exit(main())
