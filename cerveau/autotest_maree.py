# -*- coding: utf-8 -*-
"""Autotest MARÉE (phase 4 route C) — hors-ligne, déterministe.

La tempête : 70 séquences inconnues en un jour. Le tampon absorbe
(50 en attente + soupape : VIF sous pression), la nuit consolide,
puis 5 nuits passent : la statue (A gravée) parle encore, le bruit
est mort, la mer est calme (VIF 0, REFRAIN 0), le témoin B a coulé
au niveau de la mer. Zéro perte au tampon, jamais.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cerveau.cerveau import Cerveau


def main():
    c = Cerveau("EN")
    a = ["fellow", "americans", "ask"]
    b = ["fellow", "country", "ask"]
    for _ in range(9):
        c.entendre_sequence(a)
        c.entendre_sequence(b)
    c.nuit()
    for _ in range(3):
        c.entendre_sequence(a)
        c.entendre_sequence(b)
    c.nuit()
    san = c.secteurs["SANCTUAIRE"].traces
    assert san[tuple(a)].force == 92 and san[tuple(b)].force == 92
    for _ in range(3):
        phrase, _ = c.redire()
    assert phrase.startswith("I heard 24 sequences. In the sanctuary: fellow americans ask."), phrase
    assert san[tuple(a)].grave, "A devrait être gravée !"
    # LA TEMPÊTE : 70 inconnues en un jour
    tempete = [[f"mot{i}", f"bruit{i}", f"vague{i}"] for i in range(70)]
    for s in tempete:
        c.entendre_sequence(s)
    assert len(c.tampon) == 50, f"tampon : {len(c.tampon)}"
    assert len(c.secteurs["VIF"].traces) == 20, "pas de pression au VIF !"
    n3 = c.nuit()
    assert n3["videes"] == 50, n3
    # le VIF garde les 20 dernières, à f10 — les 50 premières noyées par FIFO
    atten = {tuple(s) for s in tempete[50:]}
    vif = c.secteurs["VIF"].traces
    assert set(vif) == atten, "le VIF ne garde pas les dernières !"
    assert all(t.force == 10 for t in vif.values()), "le bruit devrait être à f10"
    for _ in range(4):
        c.nuit()
    fa, fb = san[tuple(a)].force, san[tuple(b)].force
    assert fa == 100 and san[tuple(a)].grave, san[tuple(a)]
    assert fb == 65, san[tuple(b)]
    assert len(c.secteurs["VIF"].traces) == 0, "le bruit devrait être mort !"
    assert len(c.secteurs["REFRAIN"].traces) == 0, "le refrain devrait être vide !"
    assert c.resonance("MAMERICANS") >= 60
    print(f"MAREE OK — tempête 70 : tampon 50 + pression 20, vidées 50 · "
          f"A {san[tuple(a)]} (5 nuits), B f{fb}, relief {fa - fb} · "
          f"mer calme : VIF 0, REFRAIN 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
