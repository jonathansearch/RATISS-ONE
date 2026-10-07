#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASSE — éducateur en streaming : millions de séquences -> un tissu debout.
RATISS Labs · MIT.

Lit le JSONL au fil de l'eau (jamais tout en RAM), entend par lots,
une nuit par lot (consolidation), mesure tout : liens, neurones,
écoutes, RAM, temps. Mémoire bornée (caps secteurs + paires de mots).

PUISSANCE : --rapide (battement fusionné, équivalence exacte prouvée),
--binaire (3 octets/séquence), --ram (tout en mémoire d'un coup).

Usage : python3 education-massive/eduquer_masse.py --entree masse.jsonl --lot 50000
"""
import argparse
import json
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from binaire_masse import lire_iter, lire_ram, table  # noqa: E402
from bouche.regles import formuler, lire_etat  # noqa: E402
from cerveau.cerveau import Cerveau  # noqa: E402
from generer_masse import iterer  # noqa: E402


def memoir_mo():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def entendre_lot(c, seqs, n, lot, t0):
    for seq in seqs:
        c.entendre_sequence(seq)
        n += 1
        if n % lot == 0:
            c.nuit()
            print(f"lot {n} : liens={len(c.graph['liens'])} "
                  f"neurones={len(c.graph['neurones'])} "
                  f"écoutes={c.ecoutes} RAM={memoir_mo():.0f} Mo "
                  f"t={time.time() - t0:.0f}s", flush=True)
    return n


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--entree", required=True)
    ap.add_argument("--lot", type=int, default=100000)
    ap.add_argument("--complement", type=int, default=0,
                    help="séquences fraîches générées sur place (seed 8, sans disque)")
    ap.add_argument("--bilan", default=None,
                    help="fichier où écrire la phrase finale (pour la faire parler)")
    ap.add_argument("--rapide", action="store_true",
                    help="battement fusionné (même maths, x35, équivalence prouvée)")
    ap.add_argument("--binaire", action="store_true",
                    help="l'entrée est un .bin (3 octets/séquence, même flux que JSONL)")
    ap.add_argument("--ram", action="store_true",
                    help="charge le binaire en RAM d'un coup (100M = 300 Mo)")
    ap.add_argument("--epoques", type=int, default=1,
                    help="nombre de passages sur les données (la répétition grave, comme l'enfance)")
    ap.add_argument("--relire", default=None,
                    help="repart d'un cerveau gravé (reprise exacte, les écoutes continuent)")
    ap.add_argument("--graver", default=None,
                    help="grave le cerveau fortifié en fin d'éducation (.json ou .json.gz : nos poids)")
    args = ap.parse_args(argv)
    t0 = time.time()
    if args.relire:
        c = Cerveau.relire(args.relire)
        print(f"CERVEAU RELU — {c.ecoutes} écoutes déjà, le fortifié se réveille")
    else:
        c = Cerveau("FR")
    c.rapide = args.rapide
    n = c.ecoutes
    print(f"=== ÉDUCATION MASSIVE ({'RAPIDE' if args.rapide else 'lent'}, "
          f"{'binaire' + ('+RAM' if args.ram else '') if args.binaire else 'JSONL'}, "
          f"{args.epoques} époque(s), une nuit par lot) ===")
    for ep in range(1, args.epoques + 1):
        if args.epoques > 1:
            print(f"--- époque {ep}/{args.epoques} ---", flush=True)
        if args.binaire:
            mots, _ = table()
            if args.ram:
                n = entendre_lot(c, lire_ram(args.entree, mots), n, args.lot, t0)
            else:
                n = entendre_lot(c, lire_iter(args.entree, mots), n, args.lot, t0)
        else:
            with open(args.entree, encoding="utf-8") as fh:
                n = entendre_lot(c, (json.loads(l)["mots"] for l in fh), n, args.lot, t0)
        if args.complement:
            print(f"=== COMPLÉMENT : {args.complement} fraîches (seed 8) ===")
            n = entendre_lot(c, (s["mots"] for s in iterer(args.complement, seed=8)),
                             n, args.lot, t0)
    print("=== BILAN ===")
    phrase = formuler(lire_etat(c))
    print(f"dit : {phrase}")
    if args.bilan:
        with open(args.bilan, "w", encoding="utf-8") as fh:
            fh.write(phrase + "\n")
    extra = ""
    if args.graver:
        octets = c.graver(args.graver)
        extra = f", cerveau gravé {args.graver} ({octets} octets)"
        print(f"CERVEAU GRAVÉ — {args.graver} ({octets} octets : nos poids) 💪")
    print(f"MASSE OK — {n} séquences, {len(c.graph['liens'])} liens, "
          f"{len(c.graph['neurones'])} neurones, RAM max {memoir_mo():.0f} Mo, "
          f"{time.time() - t0:.0f} s{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
