#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OREILLE EN DIRECT — tranches live -> Cerveau -> règles (R5).
RATISS Labs · MIT.

Le tissu écoute TRANCHE PAR TRANCHE (2 s) et dit ce qu'il tient AU FUR
ET À MESURE — comme des sous-titres qui comprennent. Les fenêtres de
3 mots chevauchent les tranches (mémoire de 2 mots) : rien ne se perd
aux frontières. Puis 4 nuits (comme le chaos : ×1 écoute + rêve), et
la phrase finale.

Usage :
  python3 porte-voix/direct.py --simuler           # rejoue jfk.wav en direct
  python3 porte-voix/direct.py --simuler --export porte-voix/tranches-jfk.json
  python3 porte-voix/direct.py --micro 10          # 10 s au micro (si présent)
"""
import json
import os
import string
import subprocess
import sys
import tempfile
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bouche.regles import formuler, lire_etat  # noqa: E402
from cerveau.cerveau import Cerveau  # noqa: E402

AUDIO = "porte-voix/audio/jfk.wav"
TRANCHE = 2.0  # secondes de direct par tranche


def normaliser(texte):
    table = str.maketrans("", "", string.punctuation)
    return texte.lower().translate(table)


def decouper(chemin, duree=TRANCHE):
    """Wav mono -> tranches : [(t0, chemin_tranche)]. 100 % stdlib."""
    entree = wave.open(chemin, "rb")
    assert entree.getnchannels() == 1, "wav mono exigé"
    rate = entree.getframerate()
    par_tranche = int(rate * duree)
    n = entree.getnframes()
    tranches, i = [], 0
    dossier = tempfile.mkdtemp(prefix="direct-")
    while i * par_tranche < n:
        bloc = entree.readframes(par_tranche)
        sortie = os.path.join(dossier, f"t{i:02d}.wav")
        with wave.open(sortie, "wb") as wh:
            wh.setnchannels(1)
            wh.setsampwidth(entree.getsampwidth())
            wh.setframerate(rate)
            wh.writeframes(bloc)
        tranches.append((i * duree, sortie))
        i += 1
    entree.close()
    return tranches


def transcrire_tranche(chemin):
    proc = subprocess.run(
        ["phonon", "transcribe", chemin, "--json"],
        capture_output=True, text=True, encoding="utf-8",
    )
    d = json.loads(proc.stdout)
    items = d.get("words") or []
    if not items:
        for seg in d.get("segments", []):
            items += seg.get("words", [])
    mots = []
    for w in items:
        txt = w.get("word", w.get("text", "")) if isinstance(w, dict) else str(w)
        txt = normaliser(txt)
        if txt:
            mots.extend(txt.split())
    return mots


def fenetres_live(mots, report):
    """Fenêtres de 3 sur report + mots ; rend (fenêtres, nouveau report)."""
    suite = report + mots
    fens = [suite[i:i + 3] for i in range(len(suite) - 2)]
    return fens, suite[-2:] if len(suite) >= 2 else suite


def ecouter(mots_par_tranche, silencieux=False):
    """Le direct : nourrit le Cerveau tranche par tranche, dit chaque fois."""
    c = Cerveau()
    report, lignes = [], []
    for t0, mots in mots_par_tranche:
        fens, report = fenetres_live(mots, report)
        for f in fens:
            c.entendre_sequence(list(f))
        phrase = formuler(lire_etat(c))
        lignes.append((t0, mots, phrase))
        if not silencieux:
            print(f"t+{t0:>4.0f}s : « {' '.join(mots)} »")
            print(f"tissu   : {phrase}")
    if not silencieux:
        print("=== 4 NUITS (le rêve consolide, motif chaos) ===")
    for _ in range(4):
        c.nuit()
    finale = formuler(lire_etat(c))
    print(f"dit : {finale}")
    return finale, lignes


def enregistrer_micro(secondes):
    try:
        import sounddevice as sd
    except ImportError:
        print("micro indisponible (sounddevice manquant : pip install sounddevice)")
        return None
    try:
        import numpy as np
    except ImportError:
        print("micro indisponible (numpy manquant)")
        return None
    try:
        cap = sd.rec(int(secondes * 16000), samplerate=16000, channels=1,
                     dtype="int16")
        sd.wait()
    except Exception as exc:  # pas de micro : échec propre, pas de crash
        print(f"micro indisponible ({exc}), simulation impossible")
        return None
    sortie = os.path.join(tempfile.mkdtemp(prefix="direct-"), "micro.wav")
    with wave.open(sortie, "wb") as wh:
        wh.setnchannels(1)
        wh.setsampwidth(2)
        wh.setframerate(16000)
        wh.writeframes(np.asarray(cap).tobytes())
    return sortie


def main(argv):
    if "--micro" in argv:
        secs = float(argv[argv.index("--micro") + 1]) if len(argv) > 2 else 10.0
        print(f"=== MICRO : {secs:.0f} s d'écoute réelle ===")
        audio = enregistrer_micro(secs)
        if audio is None:
            return 2
    else:
        audio = AUDIO
        print(f"=== DIRECT SIMULÉ : {audio} par tranches de {TRANCHE:.0f} s ===")
    tranches = decouper(audio)
    print(f"{len(tranches)} tranches")
    mots_par_tranche = [(t0, transcrire_tranche(ch)) for t0, ch in tranches]
    if "--export" in argv:
        cible = argv[argv.index("--export") + 1]
        with open(cible, "w", encoding="utf-8") as fh:
            json.dump([{"t0": t0, "mots": m} for t0, m in mots_par_tranche],
                      fh, ensure_ascii=False, indent=1)
        print(f"tranches exportées -> {cible}")
    finale, _ = ecouter(mots_par_tranche)
    print(f"DIRECT OK — {sum(len(m) for _, m in mots_par_tranche)} mots cousus")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
