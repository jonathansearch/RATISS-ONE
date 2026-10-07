# -*- coding: utf-8 -*-
"""
LE CONSTRUCTEUR — l'école de la bouche, v1 (leçon 35).
RATISS Labs · MIT.

La bouche assemble, elle n'invente pas (zéro LLM, 100 % interne) :
- R-CONSTRUCTEUR : chaque lien parlé est TENU (lien du tissu, force >= 20 :
  une fois = remarqué, deux fois = tenu).
- Noyau sujet-verbe-objet (+ une épithète par nom), ordre français :
  sujet avant, objet après, épithète après (simplifié, assumé).
- Style télégraphique : lemmes, pas de petits mots (déterminants et
  prépositions attendront leur leçon), pas d'accord — le bébé parle
  vrai, pas joli.
- Un mot seul n'est pas une phrase ; sans noyau, la bouche se tait (None).
- Déterministe : à force égale, le premier alphabétique gagne.
"""

SEUIL_TENU = 20
NOMS = {"NOUN", "PROPN", "PRON"}


def _role(c, noeud, autre):
    """Le rôle de `noeud` face à `autre` : (relation, est_dépendant)."""
    info = c.constructions.get(tuple(sorted((noeud, autre))))
    if info is None:
        return None, False
    rel, dep = info
    return rel, dep == noeud


def _voisins(c, g, seuil):
    """Voisins tenus : [(force, nom)] triés (fort d'abord, puis A-Z)."""
    out = []
    for (a, b), f in c.graph["liens"].items():
        if f < seuil:
            continue
        if a == g:
            out.append((f, b))
        elif b == g:
            out.append((f, a))
    out.sort(key=lambda t: (-t[0], t[1]))
    return out


def _noeud_mot(c, mot):
    """Un mot entendu -> son noeud (école, oreille, formes) ou None."""
    if mot in c.mots_connus:
        return "word_" + mot
    lemme = mot if mot in c.oreille else c.formes.get(mot.lower())
    if lemme in c.oreille:
        return c.oreille[lemme][0]
    return None


def _lemme_de(c, noeud):
    """Un noeud -> le mot à dire (l'oreille sait, sinon on déshabille word_)."""
    for lemme, mb in c.oreille.items():
        if mb and mb[0] == noeud:
            return lemme
    return noeud[5:] if noeud.startswith("word_") else noeud


def _sujet_de(c, v, seuil):
    for _, n in _voisins(c, v, seuil):
        rel, dep = _role(c, n, v)
        if rel == "nsubj" and dep and c.natures.get(n) in NOMS:
            return n
    return None


def _objet_de(c, v, seuil):
    for _, n in _voisins(c, v, seuil):
        rel, dep = _role(c, n, v)
        if rel in ("obj", "iobj") and dep and c.natures.get(n) in NOMS:
            return n
    return None


def _epithete_de(c, n, seuil):
    for _, a in _voisins(c, n, seuil):
        rel, dep = _role(c, a, n)
        if rel == "amod" and dep and c.natures.get(a) == "ADJ":
            return a
    return None


def _noyau(c, g, seuil):
    """Le noyau autour de g : (sujet, verbe, objet) ou None."""
    nat = c.natures.get(g)
    if nat == "VERB":
        s, o = _sujet_de(c, g, seuil), _objet_de(c, g, seuil)
        if s is None and o is None:
            return None
        return (s, g, o)
    if nat in NOMS:
        cands = []
        for f, v in _voisins(c, g, seuil):
            if c.natures.get(v) != "VERB":
                continue
            rel, dep = _role(c, g, v)
            if rel == "nsubj" and dep:
                cands.append((f, v, (g, v, _objet_de(c, v, seuil))))
            elif rel in ("obj", "iobj") and dep:
                cands.append((f, v, (_sujet_de(c, v, seuil), v, g)))
        if not cands:
            return None
        cands.sort(key=lambda t: (t[2][0] is None or t[2][2] is None, -t[0], t[1]))
        return cands[0][2]
    return None


def construire(c, graine, seuil=SEUIL_TENU):
    """Assemble un noyau tenu autour de la graine (mot ou noeud).

    La graine d'abord, sinon UN pas vers le voisin le plus fort (le mot
    qui tient). Retourne le résultat (phrase + preuves) ou None (silence).
    """
    g = graine if graine in c.graph["neurones"] else _noeud_mot(c, graine)
    if g is None:
        return None
    cands = [g]
    forts = _voisins(c, g, 1)
    if forts:
        cands.append(forts[0][1])
    for n in cands:
        noy = _noyau(c, n, seuil)
        if noy is None:
            continue
        s, vb, o = noy
        mots = []
        ep_s, ep_o = None, None
        if s is not None:
            mots.append(_lemme_de(c, s))
            ep_s = _epithete_de(c, s, seuil)
            if ep_s is not None:
                mots.append(_lemme_de(c, ep_s))
        mots.append(_lemme_de(c, vb))
        if o is not None:
            mots.append(_lemme_de(c, o))
            ep_o = _epithete_de(c, o, seuil)
            if ep_o is not None:
                mots.append(_lemme_de(c, ep_o))
        return {"phrase": " ".join(mots), "mots": mots, "sujet": s, "verbe": vb,
                "objet": o, "epithete_sujet": ep_s, "epithete_objet": ep_o,
                "graine": g, "noyau": n}
    return None


def tenue(c, resultat, seuil=SEUIL_TENU):
    """Vérifie R-CONSTRUCTEUR : chaque lien parlé est tenu (lien + force)."""
    if resultat is None:
        return False
    s, v, o = resultat["sujet"], resultat["verbe"], resultat["objet"]
    paires = []
    if s is not None:
        paires.append((s, v))
    if o is not None:
        paires.append((v, o))
    if resultat["epithete_sujet"] is not None:
        paires.append((s, resultat["epithete_sujet"]))
    if resultat["epithete_objet"] is not None:
        paires.append((o, resultat["epithete_objet"]))
    return all(c.graph["liens"].get(tuple(sorted(p)), 0) >= seuil for p in paires)
