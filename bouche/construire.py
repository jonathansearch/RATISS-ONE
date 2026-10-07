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
    for _, n in _voisins(c, g, 1):  # un pas vers le mot qui tient : les petits
        if c.natures.get(n) in NOMS or c.natures.get(n) == "VERB":
            cands.append(n)  # mots (DET...) sont de la colle, pas du noyau
            break
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


# ----- leçon 36 : le français accordé (articles, genre, nombre, présent) -----
VOYELLES = set("aeiouyàâäéèêëîïôöùûüœæh")  # h muet supposé ; les h aspirés
# rares passent par les déterminants observés, sinon on se trompe (documenté).


def _det(c, noeud, nombre, fallbacks):
    tab = c.determinants.get(noeud, {})
    if nombre in tab:
        return tab[nombre]
    fallbacks.append(("det", noeud))
    g = c.genres.get(noeud, "M")
    lemme = _lemme_de(c, noeud)
    if nombre == "P":
        return "les"
    if lemme[:1] in VOYELLES:
        return "l'"
    return "la" if g == "F" else "le"


def _nom(c, noeud, nombre, fallbacks):
    tab = c.flexions.get(noeud, {})
    if nombre in tab:
        return tab[nombre]
    fallbacks.append(("flexion", noeud))
    return _lemme_de(c, noeud)


def _adjectif(c, noeud, genre, nombre, fallbacks):
    tab = c.adjectifs.get(noeud, {})
    if genre + nombre in tab:
        return tab[genre + nombre]
    fallbacks.append(("adjectif", noeud))
    return _lemme_de(c, noeud)


def _verbe(c, noeud, nombre, fallbacks):
    tab = c.conjugue.get(noeud, {})
    if nombre in tab:
        return tab[nombre]
    fallbacks.append(("conjugaison", noeud))
    return _lemme_de(c, noeud)


def _groupe_nominal(c, noeud, epithete, fallbacks):
    """Un nom habillé : [article] nom [épithète accordée]."""
    nombre = c.nombres.get(noeud, "S")
    genre = c.genres.get(noeud, "M")
    mots = []
    if c.natures.get(noeud) != "PROPN":
        mots.append(_det(c, noeud, nombre, fallbacks))
    nom = _nom(c, noeud, nombre, fallbacks)
    mots.append(nom.capitalize() if c.natures.get(noeud) == "PROPN" else nom)
    if epithete is not None:
        mots.append(_adjectif(c, epithete, genre, nombre, fallbacks))
    return mots, nombre


def parler(c, graine, seuil=SEUIL_TENU):
    """Le français accordé : même noyau tenu que `construire`, habillé
    (articles, genre, nombre, présent 3e — le verbe s'accorde au sujet).
    Majuscule + point. `appris` = zéro règle de secours (tout observé)."""
    res = construire(c, graine, seuil=seuil)
    if res is None:
        return None
    fallbacks = []
    mots = []
    ns = "S"
    if res["sujet"] is not None:
        gn, ns = _groupe_nominal(c, res["sujet"], res["epithete_sujet"], fallbacks)
        mots += gn
    mots.append(_verbe(c, res["verbe"], ns, fallbacks))
    if res["objet"] is not None:
        gn, _ = _groupe_nominal(c, res["objet"], res["epithete_objet"], fallbacks)
        mots += gn
    phrase = " ".join(mots).replace("l' ", "l'")
    phrase = phrase[0].upper() + phrase[1:] + "."
    return {"phrase": phrase, "mots": mots, "tenu": tenue(c, res, seuil),
            "appris": not fallbacks, "fallbacks": fallbacks,
            "sujet": res["sujet"], "verbe": res["verbe"], "objet": res["objet"],
            "epithete_sujet": res["epithete_sujet"],
            "epithete_objet": res["epithete_objet"], "graine": res["graine"],
            "noyau": res["noyau"]}
