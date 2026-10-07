#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PONT FOCAL — encodeur tissu -> bits (100 % stdlib, déterministe).
RATISS Labs · MIT.

Loi du labo : on n'encode que la TRACE relationnelle — quels mots, quel
ordre, quelle force — jamais la donnée brute. Le sanctuaire et l'ultra
sont triés (ordre canonique) : même tissu -> mêmes bits, partout.
"""
import hashlib
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bouche.regles import lire_etat  # noqa: E402
from cerveau.cerveau import MOTS, Cerveau  # noqa: E402

N_BITS = 2048  # comme la charge du condensateur FOCAL


def tissu_frais():
    """État d'un tissu neuf : le vocabulaire inné, rien de vécu."""
    return lire_etat(Cerveau())


def tissu_sanctuaire():
    """État après 9 rencontres + 2 nuits : le sanctuaire émerge (miroir S2)."""
    c = Cerveau()
    for _ in range(6):
        c.entendre_sequence(["fellow", "americans", "ask"])
    c.nuit()
    for _ in range(3):
        c.entendre_sequence(["fellow", "americans", "ask"])
    c.nuit()
    return lire_etat(c)


def tissu_chaos(seed=7, n=12):
    """État après 12 séquences tirées (graine fixée) : du bruit, pas d'ordre."""
    rng = random.Random(seed)
    mots = sorted(MOTS)
    c = Cerveau()
    for _ in range(n):
        c.entendre_sequence([rng.choice(mots) for _ in range(3)])
    return lire_etat(c)


def canonique(etat):
    """La trace en lignes triées : langue, mots:force, ultra, sanctuaire."""
    lignes = ["langue=" + etat["langue"]]
    for mot in sorted(etat["tissu"], key=lambda m: (-etat["tissu"][m], m)):
        lignes.append(f"{mot}:{etat['tissu'][mot]}")
    for trace in etat["ultra"]:
        lignes.append("ultra=" + "+".join(sorted(trace["mots"]))
                      + f":{trace['force']}")
    lignes.append("sanctuaire=" + ("+".join(sorted(etat["sanctuaire"]))
                                   if etat["sanctuaire"] else "-"))
    lignes.append(f"refrain_n={etat['refrain_n']}")
    return ("\n".join(lignes) + "\n").encode("utf-8")


def tissu_vers_bits(etat, n_bits=N_BITS):
    """Octets canoniques -> bits (poids fort d'abord), tuilés à n_bits."""
    bits = bytearray()
    for octet in canonique(etat):
        for k in range(7, -1, -1):
            bits.append((octet >> k) & 1)
    if not bits:
        bits = bytearray([0])
    return bytes(bits[i % len(bits)] for i in range(n_bits))


def sha16(bits):
    return hashlib.sha256(bits).hexdigest()[:16]
