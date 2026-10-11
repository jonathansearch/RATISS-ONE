# -*- coding: utf-8 -*-
"""Un fait, une passe, le CPU. Pas de rétropropagation.

La phrase entre dans un registre à part. Le contraste est coupé :
apprendre « alpha beta gamma » ne doit pas décharger « chat → dort ».
La bouche peut continuer la suite au pas suivant.
"""

from __future__ import annotations


def apprendre_phrase_live(bouche, phrase, registre: str = "episodique") -> dict:
    from ratiss_v3 import norm, tokeniser

    if isinstance(phrase, str):
        mots = tokeniser(phrase)
        surface = phrase.strip()
    else:
        mots = [norm(m) for m in phrase if norm(m)]
        surface = " ".join(mots)
    if len(mots) < 2:
        raise ValueError("une phrase vive a besoin d'au moins deux mots")

    ancien_registre = bouche.registre
    ancien_contraste = bouche.contraste
    bouche.registre = registre
    bouche.contraste = False
    try:
        decharges = bouche._apprendre_phrase(mots, fenetre_theme=3)
    finally:
        bouche.contraste = ancien_contraste
        bouche.registre = ancien_registre

    episode = {
        "phrase": surface,
        "mots": list(mots),
        "registre": registre,
        "decharges": int(decharges),
    }
    bouche.episodique.append(episode)
    bouche.meta["episodes"] = int(bouche.meta.get("episodes", 0)) + 1
    return episode
