#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Éducation CPU de la bouche. Compte les arcs. Ne touche pas au .ratiss."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ratiss_v3 import main


def cli() -> int:
    p = argparse.ArgumentParser(description="Entraîner la bouche Ratiss GI sur CPU")
    p.add_argument("--cerveau", default="cerveau/RatissOne.ratiss")
    p.add_argument("--corpus", required=True)
    p.add_argument("--sortie", required=True)
    p.add_argument("--tours", type=int, default=3)
    p.add_argument("--registre", default="ordre")
    p.add_argument("--sans-contraste", action="store_true")
    p.add_argument("--charger", default=None, help="continuer une bouche déjà commencée")
    a = p.parse_args()
    argv = [a.cerveau, "--eduquer", a.corpus, "--tours", str(a.tours), "--registre", a.registre, "--sauver", a.sortie]
    if a.charger:
        argv += ["--charger", a.charger]
    if a.sans_contraste:
        argv += ["--sans-contraste"]
    return main(argv)


if __name__ == "__main__":
    sys.exit(cli())
