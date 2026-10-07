#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONVERSATION — 12 répliques scriptées FR+EN : on lui parle, il répond.
RATISS Labs · MIT.

Usage : python3 dialogue/conversation.py [--wav bouche/dialogue.wav]
Preuve : preuves/sortie-dialogue.txt (12 Q/R + DIALOGUE OK).
"""
import os
import subprocess
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dialogue"))
from dialogue import repondre  # noqa: E402
from cerveau.cerveau import Cerveau  # noqa: E402

CONVERSATIONS = {
    "FR": ["bonjour", "qui es-tu ?", "tu tiens quoi ?", "tu as entendu combien ?",
           "merci beaucoup", "au revoir"],
    "EN": ["hello", "who are you?", "what do you hold?", "how many did you hear?",
           "thanks a lot", "goodbye"],
}

VOIX = {"FR": "bouche/voix/fr_FR-siwis-medium.onnx",
        "EN": "bouche/voix/en_US-lessac-medium.onnx"}


def parler(phrase, voix):
    proc = subprocess.run(
        [sys.executable, "-m", "piper", "--model", voix, "--output_file", "-"],
        input=phrase, capture_output=True, encoding="utf-8",
    )
    return proc.returncode == 0


def main(argv):
    n = 0
    for langue, questions in CONVERSATIONS.items():
        cerveau = Cerveau(langue)
        print(f"=== DIALOGUE {langue} ===")
        for q in questions:
            intent, lg, rep = repondre(cerveau, q)
            n += 1
            print(f"Q : {q}")
            print(f"R [{intent}/{lg}] : {rep}")
    print(f"DIALOGUE OK — {n} répliques (FR x6, EN x6)")
    if "--wav" in argv:
        cible = argv[argv.index("--wav") + 1]
        morceaux = []
        for langue, questions in CONVERSATIONS.items():
            cerveau = Cerveau(langue)
            for q in questions:
                _, _, rep = repondre(cerveau, q)
                tmp = f"/tmp/dialogue-{len(morceaux)}.wav"
                ok = subprocess.run(
                    [sys.executable, "-m", "piper", "--model", VOIX[langue],
                     "--output_file", tmp],
                    input=rep, capture_output=True, text=True, encoding="utf-8",
                ).returncode == 0
                if not ok:
                    print("ÉCHEC bouche")
                    return 1
                morceaux.append(tmp)
        with wave.open(cible, "wb") as sortie:
            for i, m in enumerate(morceaux):
                with wave.open(m, "rb") as wh:
                    if i == 0:
                        sortie.setparams(wh.getparams())
                    sortie.writeframes(wh.readframes(wh.getnframes()))
                os.remove(m)
        print(f"{cible} écrit ({len(morceaux)} répliques cousues)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
