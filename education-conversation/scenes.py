#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCÈNES v1 — le corpus conversation : 10 dialogues + 3 faits (Martin).
RATISS Labs · MIT.

Chaque scène = 1 question apprise (q0) + 1 variante cliquée à l'école (q1)
+ 1 combinaison NEUVE jamais entendue (q2) + 1 réponse fixe (r).
Convention d'école : minuscules, SANS accents (comme education/corpus.txt).
Aucun mot de l'école innée (amis/peuple/pays/patrie/unir/avenir) : tout est neuf.
"""
from collections import Counter

SCENES = {
    "S1_salut":   {"q0": ["salut"],           "q1": ["salut", "ami"],
                   "q2": ["bonjour"],         "r": ["bonjour", "ami"]},
    "S2_vas":     {"q0": ["comment", "vas"],  "q1": ["comment"],
                   "q2": ["vas", "bien"],     "r": ["bien", "merci"]},
    "S3_viens":   {"q0": ["tu", "viens"],     "q1": ["viens", "demain"],
                   "q2": ["tu", "demain"],    "r": ["oui", "demain"]},
    "S4_heure":   {"q0": ["quelle", "heure"], "q1": ["heure", "midi"],
                   "q2": ["quelle", "midi"],  "r": ["midi", "pile"]},
    "S5_pain":    {"q0": ["tu", "veux", "pain"], "q1": ["veux", "pain"],
                   "q2": ["tu", "pain"],      "r": ["oui", "pain"]},
    "S6_marche":  {"q0": ["ou", "vas"],       "q1": ["vas", "marche"],
                   "q2": ["ou", "marche"],    "r": ["marche", "village"]},
    "S7_merci":   {"q0": ["merci", "ami"],    "q1": ["merci", "grand"],
                   "q2": ["grand", "ami"],    "r": ["plaisir", "ami"]},
    "S8_revoir":  {"q0": ["au", "revoir"],    "q1": ["revoir", "demain"],
                   "q2": ["au", "demain"],    "r": ["demain", "ami"]},
    "S9_nuit":    {"q0": ["nuit", "calme"],   "q1": ["dors", "bien"],
                   "q2": ["nuit", "dors"],    "r": ["nuit", "ami"]},
    "S10_chante": {"q0": ["qui", "chante"],   "q1": ["chante", "oiseau"],
                   "q2": ["qui", "oiseau"],   "r": ["oiseau", "ciel"]},
    # --- les FAITS : l'histoire de Martin, en petits mots (vision du chef) ---
    "F11_martin": {"q0": ["qui", "martin"],   "q1": ["martin", "luther"],
                   "q2": ["qui", "luther"],   "r": ["pasteur", "reve"]},
    "F12_mort":   {"q0": ["martin", "mort"],  "q1": ["mort", "avril"],
                   "q2": ["martin", "avril"], "r": ["avril", "memphis"]},
    "F13_reve":   {"q0": ["reve", "martin"],  "q1": ["reve", "liberte"],
                   "q2": ["liberte", "martin"], "r": ["liberte", "droits"]},
}

# Témoins : nés, reliés au lointain, JAMAIS entendus — ils doivent rester sourds.
TEMOINS = ["caillou", "ruisseau", "hibou"]

# Seuils de la sonde (écrits AVANT le premier run — pas ajustés après).
SEUIL_TOP = 30   # la bonne réponse doit s'allumer à 30+
MARGE = 10       # et dépasser la meilleure mauvaise d'au moins 10
MURMURE = 20     # sous 20 : silence (contrôles témoins)
COUPS_MAX = 5    # coups correctifs max par scène ratée

ECOLE_INNEE = ("amis", "peuple", "pays", "patrie", "unir", "avenir")


def valider():
    """Le corpus se vérifie lui-même (design honnête, pas de collision)."""
    assert len(SCENES) == 13, len(SCENES)
    mots = Counter(w for s in SCENES.values() for k in ("q0", "q1", "r") for w in s[k])
    for w in ECOLE_INNEE:
        assert w not in mots, f"mot inné interdit dans le corpus : {w}"
    for t in TEMOINS:
        assert t not in mots, f"témoin entendu par le corpus : {t}"
    q2s = [tuple(sorted(s["q2"])) for s in SCENES.values()]
    assert len(set(q2s)) == 13, "deux q2 identiques !"
    connus = {tuple(sorted(s[k])) for s in SCENES.values() for k in ("q0", "q1", "r")}
    for nom, s in SCENES.items():
        assert tuple(sorted(s["q2"])) not in connus, f"q2 de {nom} déjà entendue !"
        vocab = set(s["q0"]) | set(s["q1"]) | set(s["r"])
        for w in s["q2"]:
            assert w in vocab, f"q2 de {nom} : mot non né : {w}"
    return {"scenes": len(SCENES), "mots": len(mots), "temoins": len(TEMOINS),
            "tests": len(SCENES) * 3 + len(TEMOINS)}


if __name__ == "__main__":
    print(valider())
