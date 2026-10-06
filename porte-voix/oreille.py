#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OREILLE LIVE v1 — audio -> Phonon-2 -> pont -> tissu Ratum.
RATISS Labs · la boucle sensorielle réelle, de bout en bout.

Prérequis (vivants, non persistés dans ce bac à sable — voir PROTOCOLE-OREILLE.md) :
  pip install --no-deps fermion-research
  pip install --no-deps torch --index-url https://download.pytorch.org/whl/cpu
  pip install safetensors soundfile scipy zstandard huggingface_hub
  pip install --no-deps transformers tokenizers

Usage : python3 porte-voix/oreille.py porte-voix/audio/jfk.wav
Produit : porte-voix/ecoute-live.ratum + verdicts du tissu.
"""

import subprocess
import sys
import time

sys.path.insert(0, "porte-voix")
from pont import construire


def transcrire(chemin_audio):
    t0 = time.time()
    proc = subprocess.run(
        ["phonon", "transcribe", chemin_audio],
        capture_output=True, text=True, encoding="utf-8",
    )
    duree = time.time() - t0
    lignes = [l for l in proc.stdout.strip().splitlines() if l and not l.startswith("[")]
    texte = lignes[-1] if lignes else ""
    return texte, duree, proc.returncode


def ecouter(chemin_ratum):
    proc = subprocess.run(
        [sys.executable, "ratum.py", chemin_ratum],
        capture_output=True, text=True, encoding="utf-8",
    )
    return proc.stdout, proc.returncode


def main():
    if len(sys.argv) != 2:
        print("usage : python3 porte-voix/oreille.py <audio.wav>")
        return 2
    audio = sys.argv[1]
    print(f"=== 1. L'OREILLE ÉCOUTE : {audio} ===")
    texte, duree, code = transcrire(audio)
    if code != 0 or not texte:
        print("ÉCHEC : Phonon-2 n'a pas transcrit (voir PROTOCOLE-OREILLE.md)")
        return 1
    print(f"transcription ({duree:.1f} s) : {texte}")
    print("=== 2. LE PONT CONVERTIT ===")
    with open("porte-voix/ecoute-live.ratum", "w", encoding="utf-8") as fh:
        fh.write(construire(texte))
    print("écoute générée : porte-voix/ecoute-live.ratum")
    print("=== 3. LE TISSU ÉCOUTE ===")
    sortie, code2 = ecouter("porte-voix/ecoute-live.ratum")
    print(sortie, end="")
    return 0 if code2 == 0 else 1


if __name__ == "__main__":
    main()
