#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASSE — générateur du fichier d'entraînement ultra-lourd (déterministe).
RATISS Labs · MIT.

50 mots vrais du corpus (education/corpus.txt), zéro mot inventé :
moitié vraies fenêtres (mélangées), moitié recombinaisons. Graine fixée :
même graine -> mêmes lignes, sur Colab comme ici.

Usage : python3 education-massive/generer_masse.py --n 5000000 --seed 7 --sortie masse.jsonl
"""
import argparse
import json
import os
import random
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(RACINE, "education", "corpus.txt")


def charger():
    phrases, mots = [], set()
    with open(CORPUS, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if ligne and not ligne.startswith("#"):
                dec = ligne.split()
                phrases.append(dec)
                mots.update(dec)
    fenetres = [p[i:i + 3] for p in phrases for i in range(len(p) - 2)]
    return fenetres, sorted(mots)


def generer(n, seed=7):
    fenetres, mots = charger()
    rng = random.Random(seed)
    lignes = []
    for i in range(n):
        if rng.random() < 0.5:
            seq = list(rng.choice(fenetres))
        else:
            seq = [rng.choice(mots) for _ in range(3)]
        lignes.append({"id": i, "mots": seq})
    return lignes


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--sortie", default="masse.jsonl")
    args = ap.parse_args(argv)
    fenetres, mots = charger()
    rng = random.Random(args.seed)
    with open(args.sortie, "w", encoding="utf-8") as fh:
        for i in range(args.n):
            if rng.random() < 0.5:
                seq = list(rng.choice(fenetres))
            else:
                seq = [rng.choice(mots) for _ in range(3)]
            fh.write(json.dumps({"id": i, "mots": seq}, ensure_ascii=False) + "\n")
    print(f"MASSE ÉCRITE — {args.n} séquences -> {args.sortie} "
          f"(seed {args.seed}, {len(mots)} mots vrais)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
