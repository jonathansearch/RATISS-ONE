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
        "attend": ["après la longue nuit : 0 sur 100", "rééduqué : 19 sur 100"],
    },
    "jouets/j04-graver-relire.ratum": {
        "code": 0,
        "attend": ["après relecture : 66 sur 100", "JUGEMENT M : TIENT"],
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
        "attend": ["après 12 rencontres : 72 sur 100", "JUGEMENT M : ROMPT"],
    },
    "jouets/j08-repos.ratum": {
        "code": 0,
        "attend": ["après repos puis loi : 47 sur 100", "JUGEMENT M : ROMPT"],
    },
    "jouets/j09-propagation.ratum": {
        "code": 0,
        "attend": ["après une vague : 65 sur 100", "après deux vagues : 64 sur 100"],
    },
    "jouets/j10-erreur.ratum": {
        "code": 1,
        "attend": ["ERREUR RATUM"],
    },
    "english.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT MAMERICANS : TIENT",
            "JUGEMENT MASK : TIENT",
            "JUGEMENT MHOME : ROMPT",
            "JUGEMENT MCOMET : ROMPT",
            "the stranger stays outside",
            "the cousin is half guessed : 36 sur 100",
        ],
    },
    "porte-voix/ecoute.ratum": {
        "code": 0,
        "attend": [
            "le tissu comprend soleil",
            "le tissu comprend lune",
            "le tissu ne comprend pas comete",
            "mot hors vocabulaire : banane",
        ],
    },
    "jouets/j11-asymetrie.ratum": {
        "code": 0,
        "attend": ["JUGEMENT A : TIENT", "JUGEMENT B : TIENT"],
    },
    "jouets/j12-adapter.ratum": {
        "code": 0,
        "attend": ["après le calme : a=37 b=37"],
    },
    "v1-coexistence.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT A : ROMPT",
            "JUGEMENT A : TIENT",
            "JUGEMENT B : TIENT",
            "l asymétrie fait coexister",
        ],
    },
    "echelle/grand.ratum": {
        "code": 0,
        "attend": ["JUGEMENT C00 : TIENT", "JUGEMENT T09 : ROMPT", "=== fin du programme ==="],
        "absent": ["ERREUR"],
    },
    "vocabulaire.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT MSOLEIL : TIENT",
            "JUGEMENT MVENT : TIENT",
            "JUGEMENT MAURORE : ROMPT",
            "JUGEMENT MCOMETE : ROMPT",
            "l inconnu reste dehors",
            "le cousin est deviné à moitié : 35 sur 100",
        ],
    },
    "francais.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT MAMIS : TIENT",
            "JUGEMENT MPATRIE : TIENT",
            "JUGEMENT MUNIR : ROMPT",
            "JUGEMENT MAVENIR : ROMPT",
            "l etranger reste dehors",
            "le cousin est devine a moitie : 35 sur 100",
        ],
    },
    "education/vocabulaire50.ratum": {
        "code": 0,
        "attend": [
            "BILAN : 50 mots sur 50 tiennent (seuil 60)",
            "TEMOINS : 6 dehors sur 6 (seuil 20)",
        ],
    },
    "jouets/j13-sequences.ratum": {
        "code": 0,
        "attend": [
            "chaîne liée : a-b=52 b-c=52 d-e=44",
            "chaîne déliée : a-b=43 b-c=43 d-e=35",
        ],
    },
    "jouets/j14-cise.ratum": {
        "code": 0,
        "attend": [
            "étincelle : rien d'assez rapide",
            "trop tôt : a-b=40 c-d=0",
            "étincelle : a b figés, 1 filament",
            "cise : 2 neurones, 1 filament",
            "nettoyage : 1 liens morts, 2 neurones morts",
            "après 20 nuits : a-b=69!",
            "JUGEMENT M : TIENT",
        ],
    },
}


def reconstruire_ecoute():
    """Régénère ecoute.ratum via le pont (déterministe) avant les contrôles."""
    proc = subprocess.run(
        [sys.executable, "porte-voix/pont.py", "--texte", "soleil lune comete banane"],
        capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0


def regenerer_vocabulaire():
    """Régénère vocabulaire50.ratum via l'éducateur (déterministe) avant les contrôles."""
    proc = subprocess.run(
        [sys.executable, "education/eduquer.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0


def autotest_cerveau():
    """L'autotest du cerveau est déterministe et hors-ligne : un contrôle comme les autres."""
    proc = subprocess.run(
        [sys.executable, "cerveau/autotest.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0 and "CERVEAU OK" in proc.stdout


def main():
    echecs, controles = 0, 0
    controles += 1
    if reconstruire_ecoute():
        print("OK : pont voix régénéré (ecoute.ratum)")
    else:
        print("ÉCHEC : le pont voix ne tourne pas")
        return 1
    controles += 1
    if regenerer_vocabulaire():
        print("OK : vocabulaire régénéré (vocabulaire50.ratum)")
    else:
        print("ÉCHEC : l'éducateur ne tourne pas")
        return 1
    controles += 1
    if autotest_cerveau():
        print("OK : autotest du cerveau (secteurs + sanctuaire + chaînes)")
    else:
        print("ÉCHEC : l'autotest du cerveau ne passe pas")
        echecs += 1
    controles += 1
    proc_fr = subprocess.run(
        [sys.executable, "cerveau/autotest_fr.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_fr.returncode == 0 and "CERVEAU FR OK" in proc_fr.stdout:
        print("OK : autotest du cerveau FR (discours rejoué hors-ligne)")
    else:
        print("ÉCHEC : l'autotest du cerveau FR ne passe pas")
        echecs += 1
    controles += 1
    proc_bouche = subprocess.run(
        [sys.executable, "bouche/autotest_bouche.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_bouche.returncode == 0 and "BOUCHE OK" in proc_bouche.stdout:
        print("OK : autotest de la bouche (5 phrases exactes FR/EN)")
    else:
        print("ÉCHEC : l'autotest de la bouche ne passe pas")
        echecs += 1
    controles += 1
    proc_marbre = subprocess.run(
        [sys.executable, "cerveau/autotest_marbre.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_marbre.returncode == 0 and "MARBRE OK" in proc_marbre.stdout:
        print("OK : autotest du marbre (gravure + relief + rétroaction FR/EN)")
    else:
        print("ÉCHEC : l'autotest du marbre ne passe pas")
        echecs += 1
    controles += 1
    proc_maree = subprocess.run(
        [sys.executable, "cerveau/autotest_maree.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_maree.returncode == 0 and "MAREE OK" in proc_maree.stdout:
        print("OK : autotest de la marée (tampon + tempête + homéostasie)")
    else:
        print("ÉCHEC : l'autotest de la marée ne passe pas")
        echecs += 1
    controles += 1
    proc_chaos = subprocess.run(
        [sys.executable, "cerveau/autotest_chaos.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_chaos.returncode == 0 and "CHAOS OK" in proc_chaos.stdout:
        print("OK : autotest du chaos (oubli honnête + rêve + double dissociation)")
    else:
        print("ÉCHEC : l'autotest du chaos ne passe pas")
        echecs += 1
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
