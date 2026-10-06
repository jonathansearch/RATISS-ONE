#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATISS-ONE — vérification automatique des verdicts Ratum.
Règle R7 du labo : on ne croit pas, on rejoue ET on vérifie.

Usage : python3 tests_verdicts.py
Sortie 0 = tous les verdicts conformes, 1 = écart détecté.
"""

import subprocess
import sys

ATTENDUS = {
    "rni-simple.ratum": [
        "JUGEMENT ABC : TIENT",
        "JUGEMENT ETRANGER : ROMPT",
    ],
    "rni-complexe.ratum": [
        "JUGEMENT SOLEIL : TIENT",
        "JUGEMENT LUNE : TIENT",
        "JUGEMENT ORAGE : ROMPT",
        "le premier souvenir a survécu",
        "le tissu ne rêve pas",
    ],
    "rni-interference.ratum": [
        "JUGEMENT SECOND : TIENT",
        "le nouveau a chassé l ancien",
    ],
}


def main():
    echecs = 0
    for prog, lignes in ATTENDUS.items():
        proc = subprocess.run(
            [sys.executable, "ratum.py", prog],
            capture_output=True, text=True, encoding="utf-8",
        )
        sortie = proc.stdout
        print(f"--- {prog} (code {proc.returncode}) ---")
        if proc.returncode != 0:
            print(f"  ÉCHEC : le programme ne tourne pas.\n{proc.stdout}\n{proc.stderr}")
            echecs += 1
            continue
        for attendue in lignes:
            if attendue in sortie:
                print(f"  OK : « {attendue} »")
            else:
                print(f"  ÉCHEC : « {attendue} » introuvable")
                echecs += 1
    print("TOUS LES VERDICTS CONFORMES" if echecs == 0 else f"{echecs} ÉCART(S) DÉTECTÉ(S)")
    return 0 if echecs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
