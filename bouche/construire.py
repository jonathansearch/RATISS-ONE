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


# ----- leçon 37 : TOUTES les bases, une fois (raconter) -----
# `dire` (35) et `parler` (36) sont GELÉS : on ajoute, on ne réécrit pas.
TEMPS = ("present", "imparfait", "futur", "passe_simple", "passe_compose")
NEG_ADV = ("pas", "plus", "jamais")
NOMINATIFS = {"je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles"}
NOMINAUX = {"NOUN", "PROPN"}  # NOMS (gelé leçon 35) contient PRON : pas lui ici
TONIQUES_OBJ = {"moi", "toi", "lui", "eux", "soi", "ca", "cela", "ceci"}
TONIQUES_PREP = TONIQUES_OBJ | {"elle", "elles", "nous", "vous"}
CONJOINTS = NOMINATIFS | {"moi", "toi", "lui", "eux"}
DEICTIQUES = ("cela", "ceci")  # pronoms qu'on montre (pas d'antécédent requis)
ELIDE = {"je": "j'", "ce": "c'", "ne": "n'", "de": "d'", "le": "l'", "la": "l'",
         "que": "qu'"}  # + voyelle -> élision (règle d'écriture)
CONTRACTIONS = {("de", "le"): "du", ("de", "les"): "des",
                ("à", "le"): "au", ("à", "les"): "aux"}


def _sujets2(c, v, seuil):
    """Candidats sujets ordonnés (nominaux + nominatifs + explétif).

    Liste (pas un seul) : le premier dont le verbe se conjugue gagne
    (nous/vous bloqueraient sinon les nominaux : prenons* -> employé)."""
    out = []
    for _, n in _voisins(c, v, seuil):
        rel, dep = _role(c, n, v)
        if not dep:
            continue
        if rel == "nsubj" and (c.natures.get(n) in NOMINAUX or (
                c.natures.get(n) == "PRON" and _lemme_de(c, n) in NOMINATIFS)):
            out.append(n)
        elif rel == "expl" and c.natures.get(n) == "PRON" \
                and _lemme_de(c, n) in NOMINATIFS:
            out.append(n)
        if len(out) >= 4:
            break
    return out


def _objet2(c, v, seuil):
    """Objet direct + toniques (manger ça, voir lui). Anaphoriques : attendent."""
    for _, n in _voisins(c, v, seuil):
        rel, dep = _role(c, n, v)
        if rel == "obj" and dep:
            if c.natures.get(n) in NOMINAUX:
                return n
            if c.natures.get(n) == "PRON" and _lemme_de(c, n) in TONIQUES_OBJ:
                return n
    return None


def _noyau2(c, g, seuil):
    """_noyau + pronoms (copie — _noyau gelé leçon 35)."""
    nat = c.natures.get(g)
    if nat == "VERB":
        sujets, o = _sujets2(c, g, seuil), _objet2(c, g, seuil)
        if not sujets and o is None:
            return []
        sujets = [s for s in sujets if s != o]
        if not sujets:
            return [(None, g, o)] if o is not None else []
        return [(s, g, o) for s in sujets]
    if nat in NOMS or nat == "PRON":
        cands = []
        for f, v in _voisins(c, g, seuil):
            if c.natures.get(v) != "VERB":
                continue
            rel, dep = _role(c, g, v)
            if rel == "nsubj" and dep and (
                    nat != "PRON" or _lemme_de(c, g) in NOMINATIFS):
                cands.append((f, v, (g, v, _objet2(c, v, seuil))))
            elif rel == "obj" and dep:
                for s in _sujets2(c, v, seuil)[:2]:
                    if s != g:
                        cands.append((f, v, (s, v, g)))
                if not _sujets2(c, v, seuil):
                    cands.append((f, v, (None, v, g)))
        if not cands:
            return []
        cands.sort(key=lambda t: (t[2][0] is None or t[2][2] is None, -t[0], t[1]))
        return [c[2] for c in cands[:4]]
    return []


def _noyau_copule(c, g, seuil):
    """(sujet, copule, attribut) : être + ADJ/nom/participe (passives incluses).
    La copule, c'est être (documenté)."""
    pool = [g] + [n for _, n in _voisins(c, g, 1)]
    cands = []
    for a in dict.fromkeys(pool):
        if c.natures.get(a) not in NOMINAUX and c.natures.get(a) not in ("ADJ", "VERB"):
            continue
        for fe, e in _voisins(c, a, seuil):
            rel, dep = _role(c, e, a)
            if rel != "cop" or not dep or _lemme_de(c, e) != "etre":
                continue
            for fs, s in _voisins(c, a, seuil):
                rs, ds = _role(c, s, a)
                if not ds:
                    continue
                if s != a and ((rs == "nsubj" and (c.natures.get(s) in NOMINAUX
                                       or (c.natures.get(s) == "PRON"
                                           and _lemme_de(c, s) in NOMINATIFS)))
                        or (rs == "expl" and c.natures.get(s) == "PRON"
                                and _lemme_de(c, s) in NOMINATIFS)):
                    cands.append((fe + fs, e, (s, e, a)))
    if not cands:
        return None
    cands.sort(key=lambda t: (-t[0], t[1], t[2][0]))
    return cands[0][2]


def _conjugue(c, noeud, temps, personne, nombre, fallbacks):
    """Forme (temps, personne, nombre) ; vieux présent 3e en secours ;
    sinon None (temps non tenu : silence, pas de hasard)."""
    tab = c.conjugue.get(noeud, {})
    clef = temps + "-" + personne + "-" + nombre
    if clef in tab:
        return tab[clef]
    if temps == "present" and personne == "3" and nombre in tab:
        return tab[nombre]  # vieux présent (leçon 36) : compat
    fallbacks.append(("conjugaison", noeud))
    return None


def _participe(c, noeud, genre, nombre):
    return c.participes.get(noeud, {}).get(genre + nombre)


def _cardinal(c, noeud, seuil, paires):
    for _, m in _voisins(c, noeud, seuil):
        rel, dep = _role(c, m, noeud)
        if rel == "nummod" and dep and c.natures.get(m) == "NUM":
            paires.append((noeud, m))
            return _lemme_de(c, m)
    return None


PREP_DE = {"lors", "afin", "pres"}  # ... + de (les deux ponts observés)


def _prep_de(c, comp, seuil):
    for _, p in _voisins(c, comp, seuil):
        rel, dep = _role(c, p, comp)
        if rel == "case" and dep and c.natures.get(p) == "ADP":
            return p
    return None


def _prep_groupe(c, prep, comp, epithete, fallbacks, paires, seuil):
    """préposition + groupe (lors de, contractions, élision d')."""
    paires.append((prep, comp))
    plemme = _lemme_de(c, prep)
    if plemme == "a" and c.natures.get(prep) == "ADP":
        plemme = "à"  # a-préposition s'écrit à (règle d'écriture)
    mots_pre = [plemme] + (["de"] if plemme in PREP_DE else [])
    g = _groupe2(c, comp, epithete, fallbacks, paires, seuil)
    noyau = "de" if plemme in PREP_DE else plemme
    if g["det"] in ("le", "les") and noyau in ("de", "à"):
        g["mots"][0] = CONTRACTIONS[(noyau, g["det"])]
        return mots_pre + g["mots"] if mots_pre[1:] else g["mots"]
    if noyau == "de" and g["mots"] and g["det"] is None \
            and g["mots"][0][:1] in VOYELLES:
        g["mots"][0] = "d'" + g["mots"][0]
        return mots_pre + g["mots"] if mots_pre[1:] else g["mots"]
    return mots_pre + g["mots"]


def _det2(c, noeud, nombre, premier, fallbacks):
    """L'article dépend du PREMIER mot (adjectif avant ou nom).

    Pluriel : les. Voyelle : l' (règle d'écriture, comme les
    contractions). Consonne : le/la observé, sinon genre + flag.
    (`_det` reste gelé pour `parler`, leçon 36.)"""
    obs = c.determinants.get(noeud, {})
    if nombre == "P":
        if obs.get("P"):
            return obs["P"]
        fallbacks.append(("det", noeud))
        return "les"
    if premier[:1] in VOYELLES:
        return "l'"
    if obs.get("S") in ("le", "la"):
        return obs["S"]
    fallbacks.append(("det", noeud))
    return "la" if c.genres.get(noeud, "M") == "F" else "le"


def _groupe2(c, noeud, epithete, fallbacks, paires, seuil):
    """[num] [det] [epith-avant] nom [epith-après] [de-comp]. PRON : nu."""
    nombre = c.nombres.get(noeud, "S")
    genre = c.genres.get(noeud, "M")
    nat = c.natures.get(noeud)
    mots = []
    det = None
    if nat == "PRON":
        mots.append(_lemme_de(c, noeud))
        return {"mots": mots, "nombre": nombre, "genre": genre, "det": None}
    num = _cardinal(c, noeud, seuil, paires)
    if num is not None and num not in ("un", "zero"):
        nombre = "P"  # deux, trois... -> pluriel (règle + flag)
        fallbacks.append(("nombre", noeud))
    nom = _nom(c, noeud, nombre, fallbacks)
    if nat == "PROPN":
        nom = nom.capitalize()
    if epithete is not None and _lemme_de(c, epithete) == "tout":
        if num is not None:
            epithete = None  # totalité + cardinal : collision (un seul survit)
        else:
            tout = _adjectif(c, epithete, genre, nombre, fallbacks)
            paires.append((noeud, epithete))
            epithete = None
            mots.append(tout)  # tout le monde (jamais *le tout monde)
    adj, avant = None, False
    if epithete is not None:
        adj = _adjectif(c, epithete, genre, nombre, fallbacks)
        paires.append((noeud, epithete))
        avant = c.places.get(epithete, "apres") == "avant"
    if num is not None:
        mots.append(num)  # cardinal nu (pas d'article : trois enfants)
    elif nat != "PROPN":
        det = _det2(c, noeud, nombre, adj if avant else nom, fallbacks)
        mots.append(det)
    if avant:
        mots.append(adj)
    mots.append(nom)
    if epithete is not None and not avant:
        mots.append(adj)
    for _, n2 in _voisins(c, noeud, seuil):
        rel, dep = _role(c, n2, noeud)
        if rel != "nmod" or not dep:
            continue
        if c.natures.get(n2) not in NOMINAUX and not (
                c.natures.get(n2) == "PRON" and _lemme_de(c, n2) in TONIQUES_PREP):
            continue
        prep = _prep_de(c, n2, seuil)
        if prep is None:
            continue  # pas de pont, pas de complément
        paires.append((noeud, n2))
        mots += _prep_groupe(c, prep, n2, _epithete_de(c, n2, seuil),
                             fallbacks, paires, seuil)
        break  # un seul complément du nom (les bases)
    return {"mots": mots, "nombre": nombre, "genre": genre, "det": det}


def _compl_verbe(c, v, rels, seuil, fallbacks, paires):
    """Compléments prépositionnels du verbe (indirect, circonstanciel)."""
    out = []
    for _, n in _voisins(c, v, seuil):
        rel, dep = _role(c, n, v)
        if rel not in rels or not dep:
            continue
        if c.natures.get(n) not in NOMINAUX and not (
                c.natures.get(n) == "PRON" and _lemme_de(c, n) in TONIQUES_PREP):
            continue
        prep = _prep_de(c, n, seuil)
        if prep is None:
            continue
        paires.append((v, n))
        out += _prep_groupe(c, prep, n, _epithete_de(c, n, seuil),
                            fallbacks, paires, seuil)
        break  # un seul par rôle (les bases)
    return out


def _infinitif(c, v, seuil, paires):
    for _, m in _voisins(c, v, seuil):
        rel, dep = _role(c, m, v)
        if rel == "xcomp" and dep and c.natures.get(m) == "VERB":
            paires.append((v, m))
            return _lemme_de(c, m)
    return None


def _adverbe(c, v, seuil, paires):
    for _, m in _voisins(c, v, seuil):
        rel, dep = _role(c, m, v)
        if rel == "advmod" and dep and c.natures.get(m) == "ADV" \
                and _lemme_de(c, m) not in NEG_ADV:
            paires.append((v, m))
            return _lemme_de(c, m)
    return None


def _coordonnes(c, noeud, seuil, paires, fallbacks):
    """Second conjoint + mot (et/ou observé, et par défaut + flag)."""
    for _, m in _voisins(c, noeud, seuil):
        if m == noeud:
            continue  # jamais X et X (tautologie)
        rel, dep = _role(c, m, noeud)
        if rel != "conj" or not dep:
            continue
        if c.natures.get(m) not in NOMINAUX and not (
                c.natures.get(m) == "PRON" and _lemme_de(c, m) in CONJOINTS):
            continue
        mot = None
        for _, w in _voisins(c, m, seuil):
            rw, dw = _role(c, w, m)
            if rw == "cc" and dw and _lemme_de(c, w) in ("et", "ou"):
                mot = _lemme_de(c, w)
                paires.append((w, m))
                break
        if mot is None:
            mot = "et"
            fallbacks.append(("conjonction", m))
        paires.append((noeud, m))
        g2 = _groupe2(c, m, _epithete_de(c, m, seuil), fallbacks, paires, seuil)
        return (mot, g2["mots"])
    return (None, [])


def _negation(c, v, fallbacks):
    neg = c.negations.get(v)
    if neg is None:
        neg = "pas"
        fallbacks.append(("negation", v))
    return neg


def tenue2(c, paires, seuil=SEUIL_TENU):
    """R-CONSTRUCTEUR étendu : TOUTES les paires parlées sont tenues."""
    return all(c.graph["liens"].get(tuple(sorted(p)), 0) >= seuil for p in paires)


def _assembler(c, noy, cop, temps, negatif, seuil, g, n):
    fallbacks, paires = [], []
    if cop is not None:
        s, e, a = cop
        pers = c.personnes.get(s, "3") if c.natures.get(s) == "PRON" else "3"
        gs = _groupe2(c, s, _epithete_de(c, s, seuil), fallbacks, paires, seuil)
        nb, genre_s = gs["nombre"], gs["genre"]
        paires.append((s, a))
        paires.append((e, a))
        mots = list(gs["mots"])
        if negatif:
            mots.append("ne")
        if temps == "passe_compose":
            forme = _conjugue(c, e, "present", pers, nb, fallbacks)
            if forme is None:
                return None
            mots.append(forme)
            if negatif:
                mots.append(_negation(c, e, fallbacks))
            part = _participe(c, e, genre_s, nb)
            if part is None:
                return None
            mots.append(part)
        else:
            forme = _conjugue(c, e, temps, pers, nb, fallbacks)
            if forme is None:
                return None
            mots.append(forme)
            if negatif:
                mots.append(_negation(c, e, fallbacks))
        nat_a = c.natures.get(a)
        if nat_a == "ADJ":
            mots.append(_adjectif(c, a, genre_s, nb, fallbacks))
        elif nat_a == "VERB":
            part = _participe(c, a, genre_s, nb)
            if part is None:
                return None
            mots.append(part)  # passive : est + participe accordé
        else:
            lemme = _lemme_de(c, a)
            mots.append(lemme.capitalize() if nat_a == "PROPN" else lemme)
        mots += _compl_verbe(c, a, ("iobj",), seuil, fallbacks, paires)
        mots += _compl_verbe(c, a, ("obl",), seuil, fallbacks, paires)
        sujet, verbe, attribut = s, e, a
    else:
        s, v, o = noy
        pers, nb, genre_s = "3", "S", "M"
        mots = []
        if s is not None:
            pers = c.personnes.get(s, "3") if c.natures.get(s) == "PRON" else "3"
            gs = _groupe2(c, s, _epithete_de(c, s, seuil), fallbacks, paires, seuil)
            nb, genre_s = gs["nombre"], gs["genre"]
            paires.append((s, v))
            mots += gs["mots"]
            mc, m2 = _coordonnes(c, s, seuil, paires, fallbacks)
            if mc is not None:
                mots += [mc] + m2
                nb = "P" if mc == "et" else "S"
        if negatif:
            mots.append("ne")
        if temps == "passe_compose":
            aux = c.auxiliaires.get(v)
            if aux is None:
                aux = "avoir"
                fallbacks.append(("auxiliaire", v))
            aux_noeud = "word_" + aux
            if aux_noeud not in c.graph["neurones"]:
                return None
            forme = _conjugue(c, aux_noeud, "present", pers, nb, fallbacks)
            if forme is None:
                return None
            paires.append((aux_noeud, v))
            mots.append(forme)
            if negatif:
                mots.append(_negation(c, v, fallbacks))
            adv = _adverbe(c, v, seuil, paires)
            if adv is not None:
                mots.append(adv)
            part = _participe(c, v, genre_s if aux == "etre" else "M",
                              nb if aux == "etre" else "S")
            if part is None:
                return None
            mots.append(part)
            inf = _infinitif(c, v, seuil, paires) if o is None else None
            if inf is not None:
                mots.append(inf)
        else:
            forme = _conjugue(c, v, temps, pers, nb, fallbacks)
            if forme is None:
                return None
            mots.append(forme)
            if negatif:
                mots.append(_negation(c, v, fallbacks))
            adv = _adverbe(c, v, seuil, paires)
            if adv is not None:
                mots.append(adv)
            inf = _infinitif(c, v, seuil, paires) if o is None else None
            if inf is not None:
                mots.append(inf)
        if o is not None:
            go = _groupe2(c, o, _epithete_de(c, o, seuil), fallbacks, paires, seuil)
            paires.append((v, o))
            mots += go["mots"]
            mc, m2 = _coordonnes(c, o, seuil, paires, fallbacks)
            if mc is not None:
                mots += [mc] + m2
        mots += _compl_verbe(c, v, ("iobj",), seuil, fallbacks, paires)
        mots += _compl_verbe(c, v, ("obl",), seuil, fallbacks, paires)
        sujet, verbe, attribut = s, v, None
    if not tenue2(c, paires, seuil):
        return None  # R-CONSTRUCTEUR : sinon silence
    joints = []
    i = 0
    while i < len(mots):
        if mots[i] in ELIDE and i + 1 < len(mots) \
                and mots[i + 1][:1].lower() in VOYELLES:
            joints.append(ELIDE[mots[i]] + mots[i + 1])
            i += 2
        else:
            joints.append(mots[i])
            i += 1
    phrase = " ".join(joints).replace("l' ", "l'")
    phrase = phrase[0].upper() + phrase[1:] + "."
    return {"phrase": phrase, "mots": joints, "tenu": True, "appris": not fallbacks,
            "fallbacks": fallbacks, "temps": temps, "negatif": negatif,
            "paires": len(paires), "sujet": sujet, "verbe": verbe,
            "attribut": attribut, "graine": g, "noyau": n}


def raconter(c, graine, temps="present", negatif=False, seuil=SEUIL_TENU):
    """TOUTES les bases, une fois : pronoms, prépositions, négation,
    adverbes, infinitifs, et/ou, nombres, 4 temps + passé composé, copules.
    Même noyau tenu, compléments tenus, R-CONSTRUCTEUR imposé (sinon None).
    `dire`/`parler` intacts (gelés leçons 35-36)."""
    if temps not in TEMPS:
        return None
    g = graine if graine in c.graph["neurones"] else _noeud_mot(c, graine)
    if g is None:
        return None
    cands = [g]
    for _, n in _voisins(c, g, 1):
        if c.natures.get(n) in NOMS or c.natures.get(n) == "VERB":
            cands.append(n)
            break
    verbe_graine = c.natures.get(g) == "VERB"
    for n in cands:
        for noy in _noyau2(c, n, seuil):
            res = _assembler(c, noy, None, temps, negatif, seuil, g, n)
            if res is not None and not (
                    verbe_graine and res["verbe"] != g):
                return res
        cop = _noyau_copule(c, n, seuil)
        if cop is not None:
            res = _assembler(c, None, cop, temps, negatif, seuil, g, n)
            if res is not None and not (
                    verbe_graine and res["attribut"] != g
                    and res["verbe"] != g):
                return res
    return None
