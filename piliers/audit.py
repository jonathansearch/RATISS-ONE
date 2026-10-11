# -*- coding: utf-8 -*-
"""Le score, déplié. Chaque terme est un nombre lu dans une table, pas une justification après coup."""

from __future__ import annotations


def expliquer_generation(bouche, token_choisi, contexte, tissu=None, lam=None, memoire=None) -> dict:
    from ratiss_v3 import LUMIERE, POIDS_TRIGRAMME, melanger, norm, normaliser, tokeniser

    if isinstance(contexte, str):
        hist = tokeniser(contexte)
    else:
        hist = [norm(t) for t in contexte if norm(t)]
    token = norm(token_choisi)
    lam_v = bouche.lam if lam is None else float(lam)
    mem = bouche.memoire if memoire is None else int(memoire)
    mem = max(1, int(mem))

    bigram_brut: dict[str, float] = {}
    if hist:
        for table in (bouche.registres.values() or [{}]):
            for cand, force in table.get(hist[-1], {}).items():
                if force > 0:
                    bigram_brut[cand] = bigram_brut.get(cand, 0.0) + float(force)
    # Même repli que scores_trigramme : la lumière à 8 n'entre pas dans l'ordre.
    ordre_bigram = bouche.scores_ordre(hist, memoire=1)

    tri_brut: dict[str, float] = {}
    paire = None
    if len(hist) >= 2:
        gauche, src = hist[-2], hist[-1]
        paire = [gauche, src]
        for table in bouche._tables_trigrammes(None):
            for cand, force in table.get(gauche, {}).get(src, {}).items():
                if force > 0:
                    tri_brut[cand] = tri_brut.get(cand, 0.0) + float(force)

    if tri_brut:
        mode = "trigramme"
        poids_tri = POIDS_TRIGRAMME
        poids_bi = 1.0 - POIDS_TRIGRAMME
        tg = normaliser(tri_brut)
        nb = normaliser(ordre_bigram)
    else:
        mode = "bigramme"
        poids_tri = 0.0
        poids_bi = 1.0
        tg = {}
        nb = normaliser(ordre_bigram)

    ordre = bouche.scores_trigramme(hist)
    theme_bouche = bouche.scores_theme_bouche(hist, memoire=mem)
    theme_tissu: dict[str, float] = {}
    if tissu is not None:
        theme_tissu = tissu.scores_theme(hist, mem)
        theme = melanger(theme_bouche, theme_tissu, 0.5 if theme_bouche else 0.0)
    else:
        theme = theme_bouche

    na = normaliser(ordre)
    nt = normaliser(theme)
    score = lam_v * na.get(token, 0.0) + (1.0 - lam_v) * nt.get(token, 0.0)
    if score <= 0:
        score = 0.0
    attendu = bouche.scores(hist, tissu=tissu, lam=lam_v, memoire=mem).get(token, 0.0)

    activations = []
    fenetre = hist[-mem:]
    for dist, mot in enumerate(reversed(fenetre)):
        lum = LUMIERE ** dist
        force_b = float(bouche.theme.get(mot, {}).get(token, 0.0))
        if force_b > 0:
            activations.append(
                {
                    "noeud": mot,
                    "distance": dist,
                    "lumiere": lum,
                    "poids": force_b,
                    "contribution": lum * force_b,
                    "couche": "theme_bouche",
                }
            )
        if tissu is not None:
            cle = tissu.cle(mot)
            if not cle:
                continue
            import math
            for nom, force in tissu.liens_sortants(cle):
                if tissu.afficher(nom) != token:
                    continue
                deg = len(tissu.liens_sortants(nom))
                denom = math.log(max(math.e, float(deg)))
                poids_eff = float(force) / denom
                activations.append(
                    {
                        "noeud": mot,
                        "distance": dist,
                        "lumiere": lum,
                        "poids": float(force),
                        "degre": deg,
                        "contribution": lum * poids_eff,
                        "couche": "tissu",
                    }
                )
    activations.sort(key=lambda a: (a["distance"], a["couche"], a["noeud"]))

    def _argmax(scores: dict[str, float]) -> dict | None:
        if not scores:
            return None
        meilleur = max(scores.items(), key=lambda kv: (kv[1], kv[0]))
        return {"token": meilleur[0], "brut": meilleur[1]}

    formule_resolue = (
        f"Score = {lam_v:.6f} * {na.get(token, 0.0):.6f}"
        f" + {1.0 - lam_v:.6f} * {nt.get(token, 0.0):.6f}"
        f" = {score:.6f}"
    )
    return {
        "token": token,
        "contexte": hist,
        "formule": "Score = λ * Ordre + (1 - λ) * Thème",
        "ordre": {
            "mode": mode,
            "poids_trigramme": poids_tri,
            "poids_bigramme": poids_bi,
            "bigramme": {
                "source": hist[-1] if hist else None,
                "frequence_brute": float(bigram_brut.get(token, 0.0)),
                "frequence_normalisee": float(nb.get(token, 0.0)),
                "table_brute": bigram_brut,
            },
            "trigramme": {
                "paire": paire,
                "vu": bool(tri_brut),
                "frequence_brute": float(tri_brut.get(token, 0.0)),
                "frequence_normalisee": float(tg.get(token, 0.0)),
                "table_brute": tri_brut,
            },
            "mixte_65_35": (
                poids_tri * tg.get(token, 0.0) + poids_bi * nb.get(token, 0.0)
                if mode == "trigramme"
                else float(ordre_bigram.get(token, 0.0))
            ),
            "score_ordre_normalise": float(na.get(token, 0.0)),
        },
        "theme": {
            "activations": activations,
            "score_theme_normalise": float(nt.get(token, 0.0)),
            "brut_bouche": float(theme_bouche.get(token, 0.0)),
            "brut_tissu": float(theme_tissu.get(token, 0.0)),
        },
        "normalisation": {
            "max_ordre": _argmax(ordre),
            "max_theme": _argmax(theme),
        },
        "resolution": {
            "lambda": lam_v,
            "ordre": float(na.get(token, 0.0)),
            "theme": float(nt.get(token, 0.0)),
            "score": score,
            "formule_resolue": formule_resolue,
        },
        "score_modele": float(attendu),
        "identique_au_score": abs(score - float(attendu)) <= 1e-9,
    }
