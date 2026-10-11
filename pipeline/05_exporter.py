#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export final. Le .bouche est le GGUF de cette bouche : un emballage, pas une autre loi.

Recommandé : un fichier .bouche (JSON gzippé). Le .ratiss reste à côté, intact.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ratiss_v3 import Bouche


def main() -> int:
    p = argparse.ArgumentParser(description="Emballer une bouche")
    p.add_argument("--bouche", required=True, help="bouche.json ou .bouche déjà apprise")
    p.add_argument("--sortie", required=True, help="de préférence un chemin qui finit par .bouche")
    a = p.parse_args()
    b = Bouche.charger(a.bouche)
    Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
    b.sauver(a.sortie)
    print(f"exporté : {a.sortie}")
    print(f"arcs    : {b.n_arcs()}")
    print(f"chaînes : {len(b.chaines)}")
    print("Le tissu scellé n'est pas dans ce fichier. Garde-le à côté.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
