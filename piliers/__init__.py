# -*- coding: utf-8 -*-
"""Quatre opérations que le tissu sait faire, et qu'une matrice dense ne sait pas.

Stdlib seulement. Pas de PyTorch. Pas de GPU.
Les fonctions prennent l'objet déjà construit (Bouche ou TissuScelle)
et délèguent à sa méthode : une seule loi, pas deux implémentations.
"""

from __future__ import annotations


def editer_synapse(hote, source, cible, nouveau_poids, **kwargs):
    return hote.editer_synapse(source, cible, nouveau_poids, **kwargs)


def supprimer_synapse(hote, source, cible, **kwargs):
    return hote.supprimer_synapse(source, cible, **kwargs)


def expliquer_generation(hote, token_choisi, contexte, **kwargs):
    return hote.expliquer_generation(token_choisi, contexte, **kwargs)


def apprendre_phrase_live(hote, phrase, registre="episodique"):
    return hote.apprendre_phrase_live(phrase, registre)


def raisonner_par_resonance(hote, concepts_sources, seuil_energie=0.1, max_sauts=3, **kwargs):
    return hote.raisonner_par_resonance(
        concepts_sources,
        seuil_energie=seuil_energie,
        max_sauts=max_sauts,
        **kwargs,
    )
