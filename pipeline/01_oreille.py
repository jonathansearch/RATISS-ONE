#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Oreille de Ratiss GI. Le texte devient des mots. Pas des flottants, pas des BPE."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ratiss_v3 import phrases_de, tokeniser


def main() -> int:
    if len(sys.argv) < 2:
        print("usage : python3 pipeline/01_oreille.py \"il était une fois\"")
        print("        python3 pipeline/01_oreille.py fichier.txt")
        return 2
    src = sys.argv[1]
    texte = Path(src).read_text(encoding="utf-8") if Path(src).is_file() else src
    print("tokens :", " | ".join(tokeniser(texte)))
    for i, ph in enumerate(phrases_de(texte), start=1):
        print(f"phrase {i} : {' '.join(ph)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
