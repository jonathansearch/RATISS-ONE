#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOUCLE PAROLE v1 — audio -> oreille (Phonon) -> tissu (Ratum) -> bouche (Piper).
RATISS Labs · le perroquet qui ne répète que ce qu'il tient.

Le transcrit ne vit qu'en mémoire pendant le run (comme les charges) :
zéro donnée stockée — seules les forces du tissu persistent (mission).

Usage : python3 parole.py porte-voix/audio/jfk.wav
Produit : parole-ecoute.ratum + bouche/verdicts.wav + log.
"""

import string
import subprocess
import sys
import time

sys.path.insert(0, "porte-voix")
from oreille import transcrire
from bouche.regles import formuler_tissu, parler as parler_regle

# Vocabulaire anglais du tissu : mot entendu -> (motif, membres)
VOCAB = {
    "americans": ("MAMERICANS", ["word_americans", "people", "land", "together"]),
    "country": ("MCOUNTRY", ["word_country", "people", "land", "future"]),
    "fellow": ("MFELLOW", ["word_fellow", "people", "together", "voice"]),
    "ask": ("MASK", ["word_ask", "voice", "duty", "future"]),
    "homeland": ("MHOME", ["word_homeland", "land", "people", "future"]),
    "comet": ("MCOMET", ["word_comet", "distant"]),
}

LIENS = [
    ("word_americans", "people"), ("word_americans", "land"), ("word_americans", "together"),
    ("people", "land"), ("people", "together"), ("land", "together"),
    ("word_country", "people"), ("word_country", "land"), ("word_country", "future"),
    ("people", "future"), ("land", "future"),
    ("word_fellow", "people"), ("word_fellow", "together"), ("word_fellow", "voice"),
    ("people", "voice"), ("together", "voice"),
    ("word_ask", "voice"), ("word_ask", "duty"), ("word_ask", "future"),
    ("voice", "duty"), ("voice", "future"), ("duty", "future"),
    ("word_homeland", "land"), ("word_homeland", "people"), ("word_homeland", "future"),
    ("word_comet", "distant"),
]

TOUT = ["word_americans", "word_country", "word_fellow", "word_ask",
        "people", "land", "voice", "duty", "together", "future"]


def mots(texte):
    table = str.maketrans("", "", string.punctuation)
    return texte.lower().translate(table).split()


def construire(transcription):
    entendus = mots(transcription)
    reconnus = [m for m in entendus if m in VOCAB]
    dehors = [m for m in entendus if m not in VOCAB]
    neurones = sorted({n for _, mb in VOCAB.values() for n in mb} | set(TOUT))
    L = []
    L.append("# PAROLE-ECOUTE — généré par parole.py (déterministe)")
    L.append(f"# Transcription reçue : {transcription}")
    L.append("tissu Parole")
    L.append("")
    for n in neurones:
        L.append(f"  neurone {n} seuil 50")
    L.append("")
    for a, b in LIENS:
        L.append(f"  lien {a} {b} force 10")
    L.append("")
    for _, (motif, mb) in VOCAB.items():
        L.append(f"  motif {motif} : " + " ".join(mb))
    L.append("  motif TOUT : " + " ".join(TOUT))
    L.append("")
    L.append("  répéter 15")  # v2 : le monde, pas la règle
    L.append("    rencontre TOUT")
    L.append("    propager")
    L.append("    renforcer")
    L.append("    repos")
    L.append("  fin")
    L.append("  répéter 2")
    L.append("    oublier")
    L.append("  fin")
    L.append("")
    for mot in reconnus:
        motif, _ = VOCAB[mot]
        L.append(f"  rencontre {motif}")
        L.append("  propager")
        L.append(f"  dire heard {mot} : holds at résonance {motif} sur 100")
        L.append("  repos")
        L.append(f"  si {motif} tient 60 alors")
        L.append(f"    dire holds {mot}")
        L.append("  sinon")
        L.append(f"    dire does not hold {mot}")
        L.append("  fin")
    for mot in dehors:
        L.append(f"  dire out of vocabulary : {mot}")
    L.append("  mesurer")
    L.append("")
    L.append("fin")
    L.append("")
    return "\n".join(L)


parler = parler_regle  # la bouche unique vit dans bouche/regles.py


def main():
    if len(sys.argv) != 2:
        print("usage : python3 parole.py <audio.wav>")
        return 2
    t0 = time.time()
    print(f"=== 1. OREILLE : {sys.argv[1]} ===")
    texte, duree, code = transcrire(sys.argv[1])
    if code != 0 or not texte:
        print("ÉCHEC oreille (voir porte-voix/PROTOCOLE-OREILLE.md)")
        return 1
    print(f"transcrit ({duree:.1f} s) : {texte}")
    print("=== 2. TISSU ===")
    with open("parole-ecoute.ratum", "w", encoding="utf-8") as fh:
        fh.write(construire(texte))
    proc = subprocess.run([sys.executable, "ratum.py", "parole-ecoute.ratum"],
                          capture_output=True, text=True, encoding="utf-8")
    print(proc.stdout, end="")
    tenus = []
    for ligne in proc.stdout.splitlines():
        if ligne.startswith("holds ") and "does not" not in ligne:
            tenus.append(ligne[6:])
    print("=== 3. BOUCHE ===")
    phrase = formuler_tissu(list(dict.fromkeys(tenus)), "EN")  # règle unique v1
    print(f"dit : {phrase}")
    ok = parler(phrase, "bouche/voix/en_US-lessac-medium.onnx", "bouche/verdicts.wav")
    print("bouche/verdicts.wav écrit" if ok else "ÉCHEC bouche")
    print(f"=== boucle totale : {time.time() - t0:.1f} s ===")
    return 0 if (proc.returncode == 0 and ok) else 1


if __name__ == "__main__":
    sys.exit(main())
