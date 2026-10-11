#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Étape 0. Écrit une bouche sans un seul arc."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ratiss_v3 import main

if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "config/bouche_etape0.json"
    sys.exit(main(["--init-vide", dest]))
