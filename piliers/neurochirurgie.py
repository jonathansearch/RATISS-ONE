# -*- coding: utf-8 -*-
"""Neurochirurgie synaptique. Une case de dictionnaire, pas un ré-entraînement.

Le tissu scellé reste une liste. On ne la reconstruit pas.
La bouche est déjà une adjacence. On n'y touche qu'une flèche.
"""

from __future__ import annotations


def editer_bouche(bouche, source: str, cible: str, nouveau_poids: float, registre: str | None = None) -> dict:
    from ratiss_v3 import norm

    src, dst = norm(source), norm(cible)
    if not src or not dst:
        raise ValueError("une synapse a besoin d'une source et d'une cible")
    poids = float(nouveau_poids)
    if poids < 0:
        raise ValueError("poids négatif : appeler supprimer_synapse")
    nom = registre or bouche.registre
    table = bouche._arcs(nom).setdefault(src, {})
    if poids == 0.0:
        table.pop(dst, None)
        if not table:
            bouche._arcs(nom).pop(src, None)
    else:
        table[dst] = poids
    return {
        "couche": "bouche",
        "registre": nom,
        "source": src,
        "cible": dst,
        "poids": poids if poids != 0.0 else None,
    }


def supprimer_bouche(bouche, source: str, cible: str, registre: str | None = None) -> dict:
    from ratiss_v3 import norm

    src, dst = norm(source), norm(cible)
    nom = registre or bouche.registre
    arcs = bouche.registres.get(nom, {})
    table = arcs.get(src, {})
    etait = dst in table
    if etait:
        table.pop(dst, None)
        if not table:
            arcs.pop(src, None)
    return {
        "couche": "bouche",
        "registre": nom,
        "source": src,
        "cible": dst,
        "poids": None,
        "existait": etait,
    }
