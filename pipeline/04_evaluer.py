#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Top-5 sur un texte que l'éducation n'a pas vu."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ratiss_v3 import main


def cli() -> int:
    p = argparse.ArgumentParser(description="Mesurer le top-5")
    p.add_argument("--cerveau", default="cerveau/RatissOne.ratiss")
    p.add_argument("--bouche", required=True)
    p.add_argument("--texte", required=True)
    p.add_argument("--lam", type=float, default=0.75)
    p.add_argument("--memoire", type=int, default=8)
    a = p.parse_args()
    return main([
        a.cerveau,
        "--charger", a.bouche,
        "--evaluer", a.texte,
        "--lam", str(a.lam),
        "--memoire", str(a.memoire),
    ])


if __name__ == "__main__":
    sys.exit(cli())
