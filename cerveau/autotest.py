# -*- coding: utf-8 -*-
"""Autotest du cerveau — 100 % hors-ligne, séquences simulées, déterministe."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cerveau.cerveau import Cerveau


def main():
    c = Cerveau()
    # éducation vérifiée : les 4 mots tiennent comme dans english.ratum
    for m in ("MAMERICANS", "MCOUNTRY", "MFELLOW", "MASK"):
        assert c.resonance(m) >= 60, f"tissu faible : {m}={c.resonance(m)}"
    # écoute : 6 séquences factices
    seqs = [["fellow", "americans", "ask"], ["ask", "country", "fellow"],
            ["country", "ask", "now"], ["long", "time", "ago"],
            ["fellow", "citizens", "here"], ["ask", "again", "later"]]
    for s in seqs:
        c.entendre_sequence(s)
    assert len(c.secteurs["VIF"].traces) == 6, "VIF devrait tenir 6 traces"
    # répétition ciblée -> promotion à la nuit
    for _ in range(6):
        c.entendre_sequence(["fellow", "americans", "ask"])
    c.nuit()
    assert ("fellow", "americans", "ask") in c.secteurs["REFRAIN"].traces, "pas promu au REFRAIN"
    for _ in range(3):
        c.entendre_sequence(["fellow", "americans", "ask"])
    c.nuit()
    assert ("fellow", "americans", "ask") in c.secteurs["SANCTUAIRE"].traces, "pas consolidé au SANCTUAIRE"
    # le tissu tient toujours, les chaînes vivent
    assert c.resonance("MAMERICANS") >= 60
    assert len(c.chaines) >= 1, "aucune chaîne mot-à-mot née"
    print(f"CERVEAU OK — sanctuaire : {len(c.secteurs['SANCTUAIRE'].traces)} trace(s), "
          f"chaînes : {len(c.chaines)}, MAMERICANS={c.resonance('MAMERICANS')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
