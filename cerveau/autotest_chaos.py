# -*- coding: utf-8 -*-
"""Autotest CHAOS + RÊVE (phase 5 route C) — hors-ligne, déterministe.

Deux vrais discours entendus UNE fois, sans focus, sans filet :
- sans rêve : oubli TOTAL prouvé (tout à 0 — l'honnêteté) ;
- avec rêve : le compris émerge seul au sanctuaire (l'autonomie) ;
- EN : double dissociation — répéter sans comprendre meurt au refrain
  (« can do for » x2, 0 mot connu), comprendre sans répéter monte au
  sanctuaire par le rêve (3 riches sauvées) ;
- la relecture couronne UNE élue, gravée dans le marbre : du chaos au
  marbre, sans aucune aide. Le baptême du feu.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cerveau.cerveau import Cerveau

# Discours FR archivé (preuves/transcription-discours.txt) : 21 mots.
MOTS_FR = ("amis du peuple ne demandez pas ce que votre pays fera pour vous "
           "demandez ce que vous ferez pour la patrie").split()
# JFK archivé (preuves/sortie-cerveau-demo.txt) : 22 mots.
MOTS_JFK = ("and so my fellow americans ask not what your country can do "
            "for you ask what you can do for your country").split()


def fenetres(mots):
    return [mots[i:i + 3] for i in range(len(mots) - 2)]


def main():
    # --- FR : UNE écoute, sans rêve = oubli total prouvé ---
    wins_fr = fenetres(MOTS_FR)
    assert len(wins_fr) == 19
    sourd = Cerveau("FR")
    sourd.reve = False
    for w in wins_fr:
        sourd.entendre_sequence(list(w))
    for _ in range(6):
        sourd.nuit()
    assert len(sourd.secteurs["SANCTUAIRE"].traces) == 0, "sans rêve, rien ne doit rester !"
    assert len(sourd.secteurs["VIF"].traces) == 0
    assert len(sourd.secteurs["REFRAIN"].traces) == 0
    # --- FR : avec rêve = l'unique comprise émerge seule ---
    c = Cerveau("FR")
    for w in wins_fr:
        c.entendre_sequence(list(w))
    n1 = c.nuit()
    assert n1["reves"] == 1, n1  # 1 seul rêve sur 19 : la sélectivité !
    assert len(n1["vif"]["promus"]) == 1 and len(n1["vif"]["morts"]) == 0
    for _ in range(3):
        c.nuit()
    san = c.secteurs["SANCTUAIRE"].traces
    elue = ("amis", "du", "peuple")
    assert list(san) == [elue], san
    assert san[elue].force == 61, san[elue]
    assert len(c.secteurs["VIF"].traces) == 0
    assert len(c.secteurs["REFRAIN"].traces) == 0
    for _ in range(3):
        phrase, _ = c.redire()
    assert phrase.startswith("J'ai entendu 19 séquences. Au sanctuaire : amis du peuple."), phrase
    assert san[elue].grave, "l'élue devrait être gravée !"
    for _ in range(2):
        c.nuit()
    assert san[elue].force == 91, san[elue]
    # --- EN JFK : la double dissociation ---
    wins_en = fenetres(MOTS_JFK)
    assert len(wins_en) == 20
    j = Cerveau("EN")
    for w in wins_en:
        j.entendre_sequence(list(w))
    m1 = j.nuit()
    assert m1["reves"] == 3, m1  # les 3 riches sauvées, pas une de plus
    assert len(m1["vif"]["promus"]) == 4, m1["vif"]  # + « can do for » x2 !
    for _ in range(3):
        j.nuit()
    san_en = j.secteurs["SANCTUAIRE"].traces
    assert len(san_en) == 3, san_en
    assert all(t.force == 61 for t in san_en.values()), san_en
    top = j.secteurs["SANCTUAIRE"].top(1)[0]
    assert list(top.mots) == ["americans", "ask", "not"], top
    refrain = j.secteurs["REFRAIN"].traces
    assert list(refrain) == [("can", "do", "for")], refrain
    assert refrain[("can", "do", "for")].force == 16, refrain
    for _ in range(3):
        phrase_en, _ = j.redire()
    assert phrase_en.startswith("I heard 20 sequences. In the sanctuary: americans ask not."), phrase_en
    assert san_en[tuple(top.mots)].grave
    for _ in range(2):
        j.nuit()
    assert san_en[tuple(top.mots)].force == 91, san_en[tuple(top.mots)]
    assert len(j.secteurs["REFRAIN"].traces) == 0, "« can do for » aurait dû mourir !"
    assert j.resonance("MAMERICANS") >= 60
    print(f"CHAOS OK — sans rêve : tout oublié (0/0/0) · FR : {san[elue]} · "
          f"JFK : 3 sauvées f61, « can do for » mort au refrain · "
          f"élues gravées f91 des deux côtés")
    return 0


if __name__ == "__main__":
    sys.exit(main())
