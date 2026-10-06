#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTOTEST FR v1 — rejoue la démo française hors-ligne (transcrit archivé).
RATISS Labs · route A · déterministe, zéro modèle : dans la batterie.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from cerveau.cerveau import Cerveau, MOTS_FR
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from cerveau import Cerveau, MOTS_FR

# Transcrit archivé (preuves/transcription-discours.txt), normalisé comme la démo.
MOTS_DISCOURS = ("amis du peuple ne demandez pas ce que votre pays fera pour vous "
                  "demandez ce que vous ferez pour la patrie").split()


def main():
    wins = [tuple(MOTS_DISCOURS[i:i + 3]) for i in range(len(MOTS_DISCOURS) - 2)]
    assert len(wins) == 19, wins
    c = Cerveau("FR")
    assert len(c.graph["neurones"]) == 13 and len(c.graph["liens"]) == 26
    for w in wins:
        c.entendre_sequence(list(w))
    riches = [w for w in wins if sum(1 for m in w if m in MOTS_FR) >= 2]
    assert len(riches) == 1 and riches[0] == ("amis", "du", "peuple"), riches
    for _ in range(2):
        for w in riches:
            c.entendre_sequence(list(w))
    for _ in range(6):
        c.entendre_sequence(["amis", "du", "peuple"])
    n1 = c.nuit()
    assert len(n1["vif"]["promus"]) == 1 and len(n1["vif"]["morts"]) == 0, n1["vif"]
    for _ in range(3):
        c.entendre_sequence(["amis", "du", "peuple"])
    n2 = c.nuit()
    assert len(n2["refrain"]["promus"]) == 1, n2["refrain"]
    top = c.secteurs["SANCTUAIRE"].top(1)[0]
    assert list(top.mots) == ["amis", "du", "peuple"] and top.force == 92, top
    tissus = [c.resonance(MOTS_FR[m]) for m in ("amis", "peuple", "pays", "patrie")]
    assert tissus == [95, 95, 95, 95], tissus
    assert len(c.graph["liens"]) == 27 and len(c.chaines) == 1
    print(f"CERVEAU FR OK — sanctuaire : {top}, tissu : {' '.join(map(str, tissus))}, "
          f"chaînes : {len(c.chaines)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
