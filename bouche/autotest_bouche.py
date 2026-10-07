#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Autotest de la bouche — 100 % hors-ligne : états tissés -> phrases exactes."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bouche.regles import Cerveau, formuler, lire_etat  # noqa: E402


def main():
    # S1 : EN frais — tissu seul, 4 tenus
    c = Cerveau()
    p1 = formuler(lire_etat(c))
    assert p1 == "I heard 0 sequences. I hold americans, country, fellow and ask. The rest stays outside.", p1
    # S2 : EN + sanctuaire
    seqs = [["fellow", "americans", "ask"], ["ask", "country", "fellow"],
            ["country", "ask", "now"], ["long", "time", "ago"],
            ["fellow", "citizens", "here"], ["ask", "again", "later"]]
    for s in seqs:
        c.entendre_sequence(s)
    for _ in range(6):
        c.entendre_sequence(["fellow", "americans", "ask"])
    c.nuit()
    for _ in range(3):
        c.entendre_sequence(["fellow", "americans", "ask"])
    c.nuit()
    p2 = formuler(lire_etat(c))
    assert p2 == ("I heard 15 sequences. In the sanctuary: fellow americans ask. "
                  "I hold americans, country, fellow and ask. The rest stays outside."), p2
    # S3 : EN + ultra-conviction
    c._exec("répéter 6\nrencontre MAMERICANS\npropager\nrenforcer\nrepos\nfin\n"
            "rencontre MAMERICANS\npropager\nrenforcer\ncise MAMERICANS\nrepos\n")
    c._sync()
    p3 = formuler(lire_etat(c))
    assert p3 == ("I heard 15 sequences. I hold as certain: americans. In the sanctuary: fellow americans ask. "
                  "I hold americans, country, fellow and ask. The rest stays outside."), p3
    # S4 : FR frais
    f = Cerveau("FR")
    p4 = formuler(lire_etat(f))
    assert p4 == "J'ai entendu 0 séquence. Je tiens amis, peuple, pays et patrie. Le reste reste dehors.", p4
    # S5 : FR + sanctuaire
    for _ in range(9):
        f.entendre_sequence(["amis", "du", "peuple"])
    f.nuit()
    for _ in range(3):
        f.entendre_sequence(["amis", "du", "peuple"])
    f.nuit()
    p5 = formuler(lire_etat(f))
    assert p5 == ("J'ai entendu 12 séquences. Au sanctuaire : amis du peuple. "
                  "Je tiens amis, peuple, pays et patrie. Le reste reste dehors."), p5
    print("BOUCHE OK — 5 phrases exactes R5 (EN x3, FR x2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
