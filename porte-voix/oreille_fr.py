#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OREILLE FR v1 — audio -> faster-whisper (small, FR) -> mots horodatés.
RATISS Labs · route A : le retour au français.

Prérequis : pip install faster-whisper soundfile (modèle small ~244 Mo,
téléchargé au 1er usage ; pas de torch : moteur ctranslate2).
Le son est décodé par soundfile et donné en tableau numpy (contourne
l'incompatibilité PyAV de faster-whisper dans ce bac à sable).

Usage : python3 porte-voix/oreille_fr.py porte-voix/audio/discours.wav
"""

import string
import sys
import time

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

TABLE = str.maketrans("", "", string.punctuation + "«»‘’“”")


def normaliser(mot):
    return mot.lower().translate(TABLE).strip()


def transcrire_mots(chemin_audio, modele="small"):
    """Rend [(mot, début_secondes)] + durée de transcription."""
    sig, sr = sf.read(chemin_audio)
    if sig.ndim > 1:
        sig = sig.mean(axis=1)
    if sr != 16000:
        x = np.linspace(0, len(sig), int(len(sig) * 16000 / sr))
        sig = np.interp(x, np.arange(len(sig)), sig).astype(np.float32)
    t0 = time.time()
    m = WhisperModel(modele, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(sig, language="fr", word_timestamps=True)
    duree = time.time() - t0
    timed = []
    for s in segs:
        for w in (s.words or []):
            mot = normaliser(w.word)
            if mot:
                timed.append((mot, round(w.start, 2)))
    return timed, duree


def main():
    if len(sys.argv) != 2:
        print("usage : python3 porte-voix/oreille_fr.py <audio.wav>")
        return 2
    timed, duree = transcrire_mots(sys.argv[1])
    print(f"{len(timed)} mots en {duree:.1f} s : " + " ".join(w for w, _ in timed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
