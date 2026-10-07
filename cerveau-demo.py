#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CERVEAU-DEMO v1 — JFK -> mots horodatés -> séquences -> secteurs -> sanctuaire -> bouche.
RATISS Labs · LIVE (Phonon + Piper requis — voir porte-voix/PROTOCOLE-OREILLE.md).

Usage : python3 cerveau-demo.py
Produit : preuves (log) + bouche/cerveau.wav (résumé parlé).
"""

import json
import string
import subprocess
import sys
import time

from bouche.regles import formuler, lire_etat
from cerveau.cerveau import Cerveau, MOTS  # lancé depuis la racine du dépôt


def mots_horodates(chemin_audio):
    proc = subprocess.run(
        ["phonon", "transcribe", chemin_audio, "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    d = json.loads(proc.stdout)
    print(f"(clés JSON Phonon : {sorted(d.keys())})")
    items = d.get("words") or []
    if not items:
        for seg in d.get("segments", []):
            items += seg.get("words", [])
    table = str.maketrans("", "", string.punctuation)
    timed = []
    for w in items:
        if isinstance(w, dict):
            txt = w.get("word", w.get("text", ""))
            timed.append((txt.lower().translate(table), w.get("start", 0)))
        else:
            timed.append((str(w).lower().translate(table), 0))
    timed = [(t, s) for t, s in timed if t]
    if not timed:  # repli : texte brut sans temps
        timed = [(w.lower().translate(table), i)
                 for i, w in enumerate(d.get("text", "").split())]
        timed = [(t, s) for t, s in timed if t]
    return timed


def fenetres(timed, n=3):
    return [tuple(w for w, _ in timed[i:i + n]) for i in range(len(timed) - n + 1)]


def parler(phrase):
    proc = subprocess.run(
        [sys.executable, "-m", "piper", "--model", "bouche/voix/en_US-lessac-medium.onnx",
         "--output_file", "bouche/cerveau.wav"],
        input=phrase, capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0


def main():
    t0 = time.time()
    print("=== 1. OREILLE (mots horodatés) ===")
    timed = mots_horodates("porte-voix/audio/jfk.wav")
    print(f"{len(timed)} mots : " + " ".join(w for w, _ in timed))
    wins = fenetres(timed)
    print(f"{len(wins)} séquences de 3 mots")

    print("=== 2. CERVEAU (éducation + écoute) ===")
    c = Cerveau()
    for w in wins:
        c.entendre_sequence(list(w))
    riches = [w for w in wins if sum(1 for m in w if m in MOTS) >= 2]
    print(f"{len(riches)} séquences riches (>= 2 mots connus), répétées x2")
    for _ in range(2):
        for w in riches:
            c.entendre_sequence(list(w))
    focus = ("fellow", "americans", "ask")
    if focus in wins:
        for _ in range(6):
            c.entendre_sequence(list(focus))
        print("focus répété x6 : fellow americans ask")

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
    phrase = formuler(lire_etat(c))  # règle unique v1 (R5 : le compteur du tissu)
    print(f"dit : {phrase}")
    print("bouche/cerveau.wav écrit" if parler(phrase) else "ÉCHEC bouche")
    print(f"=== boucle totale : {time.time() - t0:.1f} s ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
