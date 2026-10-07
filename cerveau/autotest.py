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
    # écoute : 6 séquences factices (v5 : elles attendent au tampon,
    # le VIF reste vide — le jour écoute, la nuit consolide)
    seqs = [["fellow", "americans", "ask"], ["ask", "country", "fellow"],
            ["country", "ask", "now"], ["long", "time", "ago"],
            ["fellow", "citizens", "here"], ["ask", "again", "later"]]
    for s in seqs:
        c.entendre_sequence(s)
    assert len(c.tampon) == 6, "le tampon devrait tenir 6 écoutes"
    assert len(c.secteurs["VIF"].traces) == 0, "le VIF devrait rester vide le jour"
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
    # ULTRA-SECTEUR (v3) : le tissu fige, le crâne note la conviction.
    c._exec("répéter 6\nrencontre MAMERICANS\npropager\nrenforcer\nrepos\nfin\n"
            "rencontre MAMERICANS\npropager\nrenforcer\ncise MAMERICANS\nrepos\n")
    c._sync()
    ultra = c.secteurs["ULTRA-SECTEUR"].traces
    cle = ("cise", "MAMERICANS", "land", "people", "together", "word_americans")
    assert len(ultra) == 1 and cle in ultra and ultra[cle].force == 100, ultra
    for _ in range(3):
        c.nuit()
    assert cle in ultra and ultra[cle].force == 100, "l'ultra-secteur a oublié !"
    assert c.resonance("MAMERICANS") >= 60
    print(f"CERVEAU OK — sanctuaire : {len(c.secteurs['SANCTUAIRE'].traces)} trace(s), "
          f"ultra : {len(ultra)} conviction(s), chaînes : {len(c.chaines)}, "
          f"MAMERICANS={c.resonance('MAMERICANS')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
