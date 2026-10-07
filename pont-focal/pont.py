#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PONT FOCAL — le compteur d'émergence : tissu -> bits -> organes FOCAL.
RATISS Labs · MIT.

Trois tissus (frais, chaos, sanctuaire) traversent le VRAI univers FOCAL
(`univers-focal/`, inchangé) : projection neutre sur le fond tore+sphère,
mesure P_sig (persistance H1+H2) + témoin porteurs (la concentration monte
quand on converge). Graines fixées : les nombres sont pinnés.

Dépendances : numpy, ripser (pip install numpy ripser).
Usage : python3 pont-focal/pont.py > preuves/sortie-pont-focal.txt
"""
import importlib.util
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "pont-focal"))
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402

from encodeur import (N_BITS, sha16, tissu_chaos, tissu_frais,  # noqa: E402
                      tissu_sanctuaire, tissu_vers_bits)


def organe(nom):
    chemin = os.path.join(RACINE, "univers-focal", f"focal-{nom}.py")
    spec = importlib.util.spec_from_file_location("focal_" + nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


POINT_FOCAL = (0.0, 0.0, 0.0)  # centre du tore : là où tout converge


def main():
    condensateur = organe("condensateur")
    porteurs_mod = organe("porteurs")
    conteneur = organe("conteneur")

    tissus = {"frais": tissu_frais(), "chaos": tissu_chaos(),
              "sanctuaire": tissu_sanctuaire()}
    bits = {nom: tissu_vers_bits(etat) for nom, etat in tissus.items()}
    assert len({bits[n] for n in bits}) == 3, "collision de bits !"

    fond = conteneur.fond()
    p_fond = conteneur.p_sig(fond)
    print(f"fond seul (tore+sphère) : P_sig = {p_fond:.4f}")
    mesures = {}
    for nom in ("frais", "chaos", "sanctuaire"):
        arr = np.frombuffer(bits[nom], dtype=np.uint8)
        assert len(arr) == N_BITS
        pts = condensateur.injecter(fond, arr)
        mesures[nom] = conteneur.p_sig(pts)
        print(f"tissu {nom:10s} : sha={sha16(bits[nom])} "
              f"P_sig = {mesures[nom]:.4f}")

    porteurs = porteurs_mod.creer_porteurs(N_BITS)
    phi_avant = porteurs_mod.concentration(porteurs, tau=1.0)
    for _ in range(4):
        porteurs_mod.transporter(porteurs, POINT_FOCAL)
    phi_apres = porteurs_mod.concentration(porteurs, tau=1.0)
    assert phi_apres > phi_avant, "les porteurs n'ont pas convergé !"
    print(f"porteurs : Phi {phi_avant:.4f} -> {phi_apres:.4f} "
          f"(x{phi_apres / phi_avant:.1f}, 4 transports)")
    print(f"PONT FOCAL OK — 3 tissus projetés, "
          f"delta max = {max(mesures.values()) - min(mesures.values()):.4f}")


if __name__ == "__main__":
    main()
