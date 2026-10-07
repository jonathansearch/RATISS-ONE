# -*- coding: utf-8 -*-
"""Autotest MARBRE + RÉTROACTION (phase 3 route C) — hors-ligne, déterministe.

Le répété se grave, le reste s'efface : le relief apparaît.
A (relue 3 fois) traverse 5 nuits intacte, B (témoin) perd 5.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cerveau.cerveau import Cerveau


def sanctuaire(c, mots):
    return c.secteurs["SANCTUAIRE"].traces[tuple(mots)]


def main():
    c = Cerveau("EN")
    a = ["fellow", "americans", "ask"]
    b = ["ask", "country", "fellow"]
    for _ in range(9):
        c.entendre_sequence(a)
        c.entendre_sequence(b)
    c.nuit()
    for _ in range(3):
        c.entendre_sequence(a)
        c.entendre_sequence(b)
    c.nuit()
    assert sanctuaire(c, a).force == 92, sanctuaire(c, a)
    assert sanctuaire(c, b).force == 92, sanctuaire(c, b)
    c.entendre_sequence(a)  # A revient une fois de plus : strictement au sommet
    assert sanctuaire(c, a).force == 100, sanctuaire(c, a)
    phrases = [c.redire()[0] for _ in range(3)]
    assert all(p.startswith("In the sanctuary: fellow americans ask.") for p in phrases), phrases
    gravee = sanctuaire(c, a)
    assert gravee.grave and gravee.redites == 3, gravee
    assert not sanctuaire(c, b).grave, "le témoin ne doit pas graver !"
    for _ in range(5):
        c.nuit()
    fa, fb = sanctuaire(c, a).force, sanctuaire(c, b).force
    assert fa == 100, gravee
    assert fb == 87, sanctuaire(c, b)
    assert c.resonance("MAMERICANS") >= 60
    # FR : la gravure ne parle aucune langue
    f = Cerveau("FR")
    s = ["amis", "du", "peuple"]
    for _ in range(9):
        f.entendre_sequence(s)
    f.nuit()
    for _ in range(3):
        f.entendre_sequence(s)
    f.nuit()
    for _ in range(3):
        pf, tf = f.redire()
    assert pf.startswith("Au sanctuaire : amis du peuple."), pf
    assert tf.grave and tf.force == 100, tf
    for _ in range(2):
        f.nuit()
    assert sanctuaire(f, s).force == 100, sanctuaire(f, s)
    print(f"MARBRE OK — EN : A {gravee} (5 nuits), B f{fb}, relief {fa - fb} · "
          f"FR : {sanctuaire(f, s)} (2 nuits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
