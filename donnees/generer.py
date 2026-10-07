#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROBINET À DONNÉES v1 — le tissu déterministe fabrique ses paires (état -> phrase).
RATISS Labs · MIT.

Pas de corpus géant à télécharger : on rejoue des scénarios fixés (frais,
sanctuaire, ultra) dans les deux langues et on capture (état JSON, phrase).
Le générateur est la source de vérité ; le JSONL versionné n'est qu'un
échantillon (la masse vivra sur Colab — mission : éviter de stocker).

Usage :
  python3 donnees/generer.py [--sortie donnees/paires.jsonl] [--verifier]
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bouche.regles import Cerveau, formuler, lire_etat  # noqa: E402

# (langue, focus x9, motif à figer ou None)
SCENARIOS = [
    ("EN", ("fellow", "americans", "ask"), None),
    ("EN", ("fellow", "americans", "ask"), "MAMERICANS"),
    ("EN", ("ask", "country", "fellow"), None),
    ("EN", ("ask", "country", "fellow"), "MASK"),
    ("FR", ("amis", "du", "peuple"), None),
    ("FR", ("amis", "du", "peuple"), "MAMIS"),
    ("FR", ("demandez", "ce", "que"), None),
    ("FR", ("demandez", "ce", "que"), "MPAYS"),
]


def jouer(langue, focus, motif_cise):
    c = Cerveau(langue)
    yield ("frais", c)
    for _ in range(9):
        c.entendre_sequence(list(focus))
    c.nuit()
    for _ in range(3):
        c.entendre_sequence(list(focus))
    c.nuit()
    yield ("sanctuaire", c)
    if motif_cise:
        c._exec("répéter 6\nrencontre %s\npropager\nrenforcer\nrepos\nfin\n"
                "rencontre %s\npropager\nrenforcer\ncise %s\nrepos\n"
                % (motif_cise, motif_cise, motif_cise))
        c._sync()
        yield ("ultra", c)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default=os.path.join(os.path.dirname(__file__), "paires.jsonl"))
    ap.add_argument("--verifier", action="store_true")
    args = ap.parse_args()
    paires = []
    for langue, focus, motif in SCENARIOS:
        for etape, c in jouer(langue, focus, motif):
            etat = lire_etat(c)
            nom = f"{langue}-{'focus' + str(SCENARIOS.index((langue, focus, motif)))}-{etape}"
            paires.append({"scenario": nom, "etat": etat, "phrase": formuler(etat)})
    # déduplique sur le contenu complet (frais/sanctuaire rejoués à l'identique)
    vues, uniques = set(), []
    for p in paires:
        cle = json.dumps(p, ensure_ascii=False, sort_keys=True)
        if cle not in vues:
            vues.add(cle)
            uniques.append(p)
    with open(args.sortie, "w", encoding="utf-8") as fh:
        for p in uniques:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{len(uniques)} paires -> {args.sortie}")
    if args.verifier:
        n = 0
        for ligne in open(args.sortie, encoding="utf-8"):
            p = json.loads(ligne)
            assert formuler(p["etat"]) == p["phrase"], p["scenario"]
            n += 1
        print(f"vérifié : {n}/{n} phrases reproduites à l'identique")
    return 0


if __name__ == "__main__":
    sys.exit(main())
