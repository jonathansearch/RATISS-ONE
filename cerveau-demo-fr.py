#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CERVEAU-DEMO-FR v1 — discours FR -> mots horodatés -> séquences -> secteurs -> bouche FR.
RATISS Labs · route A (miroir français de cerveau-demo.py).

Usage : python3 cerveau-demo-fr.py
Produit : preuves (log) + bouche/cerveau-fr.wav (résumé parlé en français).
"""

import subprocess
import sys
import time

sys.path.insert(0, "porte-voix")
from oreille_fr import transcrire_mots
from cerveau.cerveau import Cerveau, MOTS_FR
from bouche.regles import formuler, lire_etat, parler as dire

VOIX_FR = "bouche/voix/fr_FR-siwis-medium.onnx"


def fenetres(timed, n=3):
    return [tuple(w for w, _ in timed[i:i + n]) for i in range(len(timed) - n + 1)]


def main():
    t0 = time.time()
    print("=== 1. OREILLE FR (mots horodatés) ===")
    timed, duree_oreille = transcrire_mots("porte-voix/audio/discours.wav")
    print(f"{len(timed)} mots en {duree_oreille:.1f} s : " + " ".join(w for w, _ in timed))
    wins = fenetres(timed)
    print(f"{len(wins)} séquences de 3 mots")

    print("=== 2. CERVEAU FR (éducation + écoute) ===")
    c = Cerveau("FR")
    for w in wins:
        c.entendre_sequence(list(w))
    riches = [w for w in wins if sum(1 for m in w if m in MOTS_FR) >= 2]
    print(f"{len(riches)} séquence{'s' if len(riches) > 1 else ''} "
          f"riche{'s' if len(riches) > 1 else ''} (>= 2 mots connus), répétée{'s' if len(riches) > 1 else ''} x2")
    for _ in range(2):
        for w in riches:
            c.entendre_sequence(list(w))
    focus = ("amis", "du", "peuple")
    if focus in wins:
        for _ in range(6):
            c.entendre_sequence(list(focus))
        print("focus répété x6 : amis du peuple")

    print("=== 3. NUIT 1 ===")
    n1 = c.nuit()
    print(f"promus VIF->REFRAIN : {len(n1['vif']['promus'])}, morts VIF : {len(n1['vif']['morts'])}")
    if focus in wins:
        for _ in range(3):
            c.entendre_sequence(list(focus))
    print("=== 4. NUIT 2 ===")
    n2 = c.nuit()
    print(f"promus REFRAIN->SANCTUAIRE : {len(n2['refrain']['promus'])}")

    print("=== 5. RAPPORT ===")
    print(c.rapport())
    phrase = formuler(lire_etat(c))  # règle unique v1 (bouche/regles.py)
    print(f"dit : {phrase}")
    print("bouche/cerveau-fr.wav écrit"
          if dire(phrase, VOIX_FR, "bouche/cerveau-fr.wav") else "ÉCHEC bouche")
    print(f"=== boucle totale : {time.time() - t0:.1f} s ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
