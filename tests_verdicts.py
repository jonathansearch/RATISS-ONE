#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATISS-ONE — vérification automatique des verdicts Ratum.
Règle R7 du labo : on ne croit pas, on rejoue ET on vérifie.

Usage : python3 tests_verdicts.py
Sortie 0 = tous les contrôles verts, 1 = écart détecté.
"""

import os
import subprocess
import sys

# programme -> {code attendu, lignes attendues, lignes interdites}
CAS = {
    "rni-simple.ratum": {
        "code": 0,
        "attend": ["JUGEMENT ABC : TIENT", "JUGEMENT ETRANGER : ROMPT"],
    },
    "rni-complexe.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT SOLEIL : TIENT",
            "JUGEMENT LUNE : TIENT",
            "JUGEMENT ORAGE : ROMPT",
            "le premier souvenir a survécu",
            "le tissu ne rêve pas",
        ],
    },
    "rni-interference.ratum": {
        "code": 0,
        "attend": ["JUGEMENT SECOND : TIENT", "le nouveau a chassé l ancien"],
    },
    "jouets/j01-seuil.ratum": {
        "code": 0,
        "attend": ["JUGEMENT VIF : TIENT", "JUGEMENT DUR : ROMPT"],
    },
    "jouets/j02-pas.ratum": {
        "code": 0,
        "attend": ["JUGEMENT M : TIENT", "JUGEMENT M : ROMPT"],
    },
    "jouets/j03-oubli.ratum": {
        "code": 0,
        "attend": ["après la longue nuit : 0 sur 100", "rééduqué : 20 sur 100"],
    },
    "jouets/j04-graver-relire.ratum": {
        "code": 0,
        "attend": ["après relecture : 70 sur 100", "JUGEMENT M : TIENT"],
    },
    "jouets/j05-si-sinon.ratum": {
        "code": 0,
        "attend": [
            "branche alors : la forme apprise tient",
            "branche sinon : l inconnu est rejeté",
        ],
        "absent": ["ERREUR inattendue"],
    },
    "jouets/j06-motif-sans-liens.ratum": {
        "code": 0,
        "attend": ["JUGEMENT SEUL : ROMPT", "JUGEMENT PAIR : ROMPT"],
    },
    "jouets/j07-emboitement-plafond.ratum": {
        "code": 0,
        "attend": ["après 12 rencontres : 100 sur 100", "JUGEMENT M : TIENT"],
    },
    "jouets/j08-repos.ratum": {
        "code": 0,
        "attend": ["après repos puis loi : 40 sur 100", "JUGEMENT M : ROMPT"],
    },
    "jouets/j09-propagation.ratum": {
        "code": 0,
        "attend": ["après une vague : 95 sur 100", "après deux vagues : 100 sur 100"],
    },
    "jouets/j10-erreur.ratum": {
        "code": 1,
        "attend": ["ERREUR RATUM"],
    },
    "vocabulaire.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT MSOLEIL : TIENT",
            "JUGEMENT MVENT : TIENT",
            "JUGEMENT MAURORE : ROMPT",
            "JUGEMENT MCOMETE : ROMPT",
            "l inconnu reste dehors",
            "le cousin est deviné à moitié : 40 sur 100",
        ],
    },
}


def main():
    echecs, controles = 0, 0
    for prog, cas in CAS.items():
        proc = subprocess.run(
            [sys.executable, "ratum.py", prog],
            capture_output=True, text=True, encoding="utf-8",
        )
        sortie = proc.stdout
        print(f"--- {prog} (code {proc.returncode}, attendu {cas['code']}) ---")
        controles += 1
        if proc.returncode != cas["code"]:
            print(f"  ÉCHEC : code {proc.returncode} au lieu de {cas['code']}\n{sortie}")
            echecs += 1
            continue
        print("  OK : code de sortie")
        for attendue in cas.get("attend", []):
            controles += 1
            if attendue in sortie:
                print(f"  OK : « {attendue} »")
            else:
                print(f"  ÉCHEC : « {attendue} » introuvable")
                echecs += 1
        for interdite in cas.get("absent", []):
            controles += 1
            if interdite not in sortie:
                print(f"  OK : « {interdite} » absent")
            else:
                print(f"  ÉCHEC : « {interdite} » présent alors qu'interdit")
                echecs += 1
    try:
        os.remove("jouets/mem.scroll")
    except OSError:
        pass
    print(f"{controles - echecs}/{controles} CONTRÔLES VERTS")
    print("TOUS LES VERDICTS CONFORMES" if echecs == 0 else f"{echecs} ÉCART(S) DÉTECTÉ(S)")
    return 0 if echecs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
