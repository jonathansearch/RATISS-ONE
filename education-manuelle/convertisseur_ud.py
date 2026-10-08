#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'ÉCOLE MANUELLE — convertisseur UD -> CISE sur mesure (leçon 30).
RATISS Labs · MIT.

Prend des phrases françaises ANNOTÉES (Universal Dependencies : chaque arc
dit QUI fait QUOI à QUI) et les convertit en fragment CISE : neurones,
liens + forces (loi de l'école), motifs par relation. Puis POUSSE le
fragment au cerveau (sans dépenser de puissance : pas de ré-éducation,
que de la soudure), et FIGE les nouveaux nerfs.

Lois (simples, documentées, pinnées par la batterie) :
- force = min(100, 10 x rencontres) — la répétition prouve.
- topk arcs par mot de nos 50 (sur mesure, le tissu reste petit).
- le marbre ne se réécrit pas : lien existant = on ne touche pas.
- R5 : l'injection manuelle n'est pas une écoute (compteur inchangé).
- l'école ajoute du savoir (neurones), pas des oreilles (mots_connus intacts).
- l'école de l'oreille (leçon 34) apprend à part (oreille + formes),
  mots_connus intact, priorité à l'école.
- l'école de la bouche (leçon 35) apprend à part (constructions + natures),
  tissu intact : comment chaque lien tenu se parle.
- l'école de grammaire (leçon 36) injecte les articles (vrais nerfs) et
  apprend les accords à part (genres, nombres, flexions, conjugaison,
  déterminants) : tout observé, sinon règle documentée + flag.
- l'école des bases (leçon 37) injecte TOUTE la structure (pronoms,
  prépositions, adverbes, conjonctions, nombres, auxiliaires, réfugiés)
  et complète les tables (conjugaison totale, participes, auxiliaires,
  places, personnes, négations) : les bases, pas de hasard.

Usage :
  python3 education-manuelle/convertisseur_ud.py --conllu fr.conllu --topk 5
  python3 education-manuelle/convertisseur_ud.py --conllu fr.conllu --injecter cerveau/fige-300M.json.gz --sortie cerveau/fige-300M-ecole.json.gz
"""
import argparse
import json
import os
import sys
import unicodedata
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "education-massive"))
from cerveau.cerveau import Cerveau, noeud_pour  # noqa: E402
from generer_masse import charger  # noqa: E402

CONTENU = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
STOPLISTE = {"ne", "pas", "etre", "avoir"}  # grammaire pure : attendra le constructeur
# Leçon 37 : la stopliste REND ses mots (réfugiés) + les 1-lettre (à, y).
REFUGIES = {"etre", "avoir", "ne", "pas"}
POS_STRUCTURE = {"PRON", "ADP", "ADV", "CCONJ", "SCONJ", "NUM", "PART", "AUX"}

# Étiquette UD -> motif français (le français, pas le jargon).
REL_MOTIF = {
    "nsubj": "MSUJET", "obj": "MOBJET", "iobj": "MINDIRECT",
    "amod": "MEPITHETE", "advmod": "MMANIERE", "obl": "MCIRCONST",
    "nmod": "MCOMPLET", "acl": "MPROPOS", "appos": "MAPPOS",
    "conj": "MCONJOINT", "ccomp": "MPROP", "xcomp": "MPROP",
    "advcl": "MCIRCONST", "nummod": "MNOMBRE", "compound": "MMOT",
    "det": "MARTICLE",
    "case": "MPREPO", "aux": "MAUX", "cop": "METRE",
    "mark": "MMARQUE", "expl": "MEXPLETIF",
}
MOTIF_DIVERS = "MLIAISON"
MOTIF_RACINE = "MRACINE"


def normaliser(lemme):
    s = lemme.lower().replace("œ", "oe").replace("æ", "ae")  # leçon 45 : ligatures
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    if len(s) < 2 or not s.isalpha() or not s.isascii():
        return None
    if s in STOPLISTE:
        return None
    return s


def normaliser_structure(lemme):
    """Comme normaliser, mais la stopliste rend ses mots et les 1-lettre
    (à, y) passent : la structure n'a pas peur des petits. Réservé aux
    chemins neufs (leçon 37) — les vieux chemins gardent normaliser."""
    s = lemme.lower().replace("œ", "oe").replace("æ", "ae")  # leçon 45 : ligatures
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    if len(s) < 1 or not s.isalpha() or not s.isascii():
        return None
    return s


def extraire(conllu, nos):
    """Lit le CoNLL-U : arcs (dépendant, tête, relation).

    nos = ensemble de mots (secteur : arcs qui les touchent) ou None
    (TOUT le réservoir, pour le remix)."""
    arcs, racines = Counter(), set()
    toks = []

    def vider():
        idx = {t[0]: t for t in toks}
        for (i, lem, pos, head, rel) in toks:
            if head == 0:
                r = normaliser(lem)
                if r and pos in CONTENU:
                    racines.add(r)
                continue
            if head not in idx:
                continue
            l1, l2 = normaliser(lem), normaliser(idx[head][1])
            if not l1 or not l2:
                continue
            if pos not in CONTENU or idx[head][2] not in CONTENU:
                continue
            if nos is None or l1 in nos or l2 in nos:
                arcs[(l1, l2, rel.split(":")[0])] += 1

    with open(conllu, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne:
                if toks:
                    vider()
                    toks = []
                continue
            if ligne.startswith("#"):
                continue
            p = ligne.split("\t")
            if "-" in p[0] or "." in p[0]:
                continue
            toks.append((int(p[0]), p[2], p[3], int(p[6]), p[7]))
    if toks:
        vider()
    return arcs, racines


def _fragment(gardes, racines, source, **extra):
    """Gardes {(a,b): (rel, n)} -> fragment CISE (UN seul bâtisseur)."""
    liens, motifs = [], {}
    for (a, b) in sorted(gardes):
        r, n = gardes[(a, b)]
        liens.append({"a": a, "b": b, "force": min(100, 10 * n), "n": n, "rel": r})
        motifs.setdefault(REL_MOTIF.get(r, MOTIF_DIVERS), set()).update((a, b))
    mots = sorted({w for l in liens for w in (l["a"], l["b"])})
    racines_ici = sorted(w for w in mots if w in racines)
    if racines_ici:
        motifs[MOTIF_RACINE] = set(racines_ici)
    frag = {
        "format": "fragment-cise-ud-v1",
        "source": source,
        "loi": "force = min(100, 10 x rencontres)",
        "mots_touches": mots,
        "neurones": mots,
        "liens": liens,
        "motifs": {k: sorted(v) for k, v in sorted(motifs.items())},
        "stats": {"paires_gardees": len(liens)},
    }
    frag.update(extra)
    return frag


def convertir(arcs, racines, nos, topk):
    """Arcs -> fragment CISE (déterministe : trié partout)."""
    par_mot = {}
    for (a, b, r), n in arcs.items():
        for m in (a, b):
            if m in nos:
                par_mot.setdefault(m, []).append((a, b, r, n))
    gardes = {}
    for m, lst in par_mot.items():
        lst.sort(key=lambda t: (-t[3], t[0], t[1], t[2]))
        for (a, b, r, n) in lst[:topk]:
            cle = (a, b)
            if cle not in gardes or gardes[cle][1] < n:
                gardes[cle] = (r, n)
    frag = _fragment(gardes, racines, "UD_French-GSD train (14 450 phrases, CC-BY-SA)",
                     topk=topk)
    frag["mots_touches"] = sorted(par_mot)
    frag["stats"] = {"arcs_lus": sum(arcs.values()), "paires_uniques": len(arcs),
                     "paires_gardees": len(frag["liens"]), "mots_touches": len(par_mot)}
    return frag


def neurone_pour(c, lemme):
    """Un lemme -> neurone existant (concept ou word_X) ou neuf (word_X)."""
    nom = noeud_pour(c.graph["neurones"], lemme)
    if nom is None:
        nom = "word_" + lemme
        c.graph["neurones"][nom] = 50
    return nom


def extraire_formes(conllu):
    """Lit le CoNLL-U : formes fléchies -> lemme (le plus fréquent gagne),
    + l'ensemble des lemmes normalisés vus. Mêmes gardes qu'extraire
    (commentaires, vides, mots composés sautés)."""
    from collections import Counter, defaultdict
    votes = defaultdict(Counter)
    lemmes = set()
    with open(conllu, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            p = ligne.split("\t")
            if "-" in p[0] or "." in p[0]:
                continue
            lemme = normaliser(p[2])
            if not lemme:
                continue
            lemmes.add(lemme)
            forme = p[1].lower()
            if forme != lemme:
                votes[forme][lemme] += 1
    formes = {}
    for forme, cpt in votes.items():
        formes[forme] = sorted(cpt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    return formes, lemmes


def ecole_oreille(c, conllu):
    """L'ÉCOLE DE L'OREILLE (leçon 34) : le cerveau apprend les mots qu'il
    a déjà en nerfs — lemme direct + formes fléchies (la plus fréquente
    gagne, égalité -> premier alphabétique). Un lemme sans nerf reste
    sourd (on n'apprend que ce qu'on porte). Idempotent."""
    formes, lemmes = extraire_formes(conllu)
    mots, sourds = 0, 0
    for lemme in sorted(lemmes):
        noeud = noeud_pour(c.graph["neurones"], lemme)
        if noeud is None:
            sourds += 1
            continue
        c.oreille[lemme] = [noeud]
        mots += 1
    gardees = {f: l for f, l in formes.items() if l in c.oreille}
    c.formes.update(gardees)
    return {"mots": mots, "sourds": sourds, "formes": len(gardees)}


def ecole_cli(args):
    c = Cerveau.relire(args.injecter)
    stats = ecole_oreille(c, args.conllu)
    c.graver(args.sortie)
    print(f"OREILLE — {stats['mots']} mots appris, {stats['sourds']} sourds (sans nerf), "
          f"{stats['formes']} formes fléchies")
    print(f"GRAVÉ — {args.sortie}")
    return 0


def extraire_natures_pos(conllu, structure=False):
    """Lit le CoNLL-U : lemme -> Counter(POS). structure=True : avec
    normaliser_structure (réfugiés + 1-lettre — chemins neufs only)."""
    from collections import Counter, defaultdict
    norm = normaliser_structure if structure else normaliser
    votes = defaultdict(Counter)
    with open(conllu, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#"):
                continue
            p = ligne.split("\t")
            if "-" in p[0] or "." in p[0]:
                continue
            lemme = norm(p[2])
            if lemme:
                votes[lemme][p[3]] += 1
    return votes


def extraire_natures(conllu):
    """Lit le CoNLL-U : lemme -> nature (POS le plus fréquent, égalité -> A-Z)."""
    votes = extraire_natures_pos(conllu)
    return {l: sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            for l, c in votes.items()}


def ecole_bouche(c, conllu):
    """L'ÉCOLE DE LA BOUCHE (leçon 35) : comment chaque lien tenu se parle.

    constructions : paire de noeuds -> (relation la plus prouvée, dépendant)
    (même règle que le fond du verre) ; natures : noeud -> POS. Que du tenu :
    paire sans lien au tissu = non apprise. Idempotent."""
    arcs, _ = extraire(conllu, None)
    reserve = {}
    for (a, b, r), n in arcs.items():
        clef = tuple(sorted((a, b)))
        if clef not in reserve or reserve[clef][2] < n:
            reserve[clef] = (r, a, n)
    paires, sans_lien = 0, 0
    for (a, b), (r, dep, n) in sorted(reserve.items()):
        na = noeud_pour(c.graph["neurones"], a)
        nb = noeud_pour(c.graph["neurones"], b)
        paire = tuple(sorted((na, nb))) if na is not None and nb is not None else None
        if paire is None or paire not in c.graph["liens"]:
            sans_lien += 1
            continue
        c.constructions[paire] = (r, noeud_pour(c.graph["neurones"], dep))
        paires += 1
    natures = extraire_natures(conllu)
    mots = 0
    for lemme, pos in sorted(natures.items()):
        noeud = noeud_pour(c.graph["neurones"], lemme)
        if noeud is not None:
            c.natures[noeud] = pos
            mots += 1
    return {"paires": paires, "sans_lien": sans_lien, "natures": mots}


def bouche_cli(args):
    c = Cerveau.relire(args.injecter)
    stats = ecole_bouche(c, args.conllu)
    c.graver(args.sortie)
    print(f"BOUCHE — {stats['paires']} paires parlables, {stats['sans_lien']} sans lien, "
          f"{stats['natures']} natures")
    print(f"GRAVÉ — {args.sortie}")
    return 0


TETES_ARTICLE = {"NOUN", "PROPN", "ADJ"}


def lire_traits(p5):
    """FEATS (colonne 6) -> dict : Gender, Number, Person, Mood, Tense..."""
    if p5 == "_":
        return {}
    d = {}
    for morceau in p5.split("|"):
        if "=" in morceau:
            k, v = morceau.split("=", 1)
            d[k] = v
    return d


def extraire_articles(conllu):
    """Arcs (déterminant, tête, det) : le DET dépend de son nom."""
    arcs = Counter()
    toks = []

    def vider():
        idx = {t[0]: t for t in toks}
        for (i, lem, pos, head) in toks:
            if head == 0 or head not in idx:
                continue
            if pos != "DET" or idx[head][2] not in TETES_ARTICLE:
                continue
            l1, l2 = normaliser(lem), normaliser(idx[head][1])
            if not l1 or not l2:
                continue
            arcs[(l1, l2, "det")] += 1

    with open(conllu, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne:
                if toks:
                    vider()
                    toks = []
                continue
            if ligne.startswith("#"):
                continue
            p = ligne.split("\t")
            if "-" in p[0] or "." in p[0]:
                continue
            toks.append((int(p[0]), p[2], p[3], int(p[6])))
    if toks:
        vider()
    return arcs


TENSES = {"Pres": "present", "Imp": "imparfait", "Fut": "futur",
          "Past": "passe_simple"}


def passer_accords(c, conllu, complet=False):
    """Un passage FEATS : genres, nombres, flexions, adjectifs, conjugaison,
    déterminants (+ complet : conjugaison totale, participes, auxiliaires,
    places, personnes, négations). Idempotent (mêmes votes -> mêmes tables).
    complet=False : comportement leçon 36 à l'identique."""
    from collections import Counter, defaultdict
    norm = normaliser_structure if complet else normaliser

    def top(cpt):
        return sorted(cpt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    vg, vn = defaultdict(Counter), defaultdict(Counter)
    vf, va, vv, vd = defaultdict(lambda: defaultdict(Counter)), defaultdict(
        lambda: defaultdict(Counter)), defaultdict(lambda: defaultdict(Counter)), defaultdict(
        lambda: defaultdict(Counter))
    vv2, vp = defaultdict(lambda: defaultdict(Counter)), defaultdict(
        lambda: defaultdict(Counter))
    vaux, vplaces, vpers, vneg = defaultdict(Counter), defaultdict(Counter), defaultdict(
        Counter), defaultdict(Counter)
    toks = []

    def vider():
        idx = {t[0]: t for t in toks}
        for (i, lem, pos, head, ft, forme, rel) in toks:
            nl = norm(lem)
            if not nl:
                continue
            noeud = noeud_pour(c.graph["neurones"], nl)
            if noeud is None:
                continue
            g, nb = ft.get("Gender"), ft.get("Number")
            if g in ("Masc", "Fem") and pos in ("NOUN", "PROPN", "ADJ", "PRON", "DET"):
                vg[noeud][g] += 1
            if nb in ("Sing", "Plur"):
                if pos in ("NOUN", "PROPN", "ADJ", "PRON", "VERB", "DET"):
                    vn[noeud][nb] += 1
                if pos in ("NOUN", "PROPN", "ADJ") and len(forme) >= 2:
                    vf[noeud][nb][forme.lower()] += 1
                if pos == "ADJ" and g in ("Masc", "Fem"):
                    va[noeud][g + nb][forme.lower()] += 1
            if (pos in ("VERB", "AUX") and ft.get("Person") == "3"
                    and ft.get("Mood") == "Ind" and ft.get("Tense") == "Pres"
                    and nb in ("Sing", "Plur")):
                vv[noeud][nb][forme.lower()] += 1
            if (pos == "DET" and head in idx and forme.lower() in ("le", "la", "les", "l'")
                    and nb in ("Sing", "Plur")):
                hl = norm(idx[head][1])
                hn = noeud_pour(c.graph["neurones"], hl) if hl else None
                if hn is not None:
                    vd[hn][nb][forme.lower()] += 1
            if complet:
                tense = ft.get("Tense")
                if (pos in ("VERB", "AUX") and ft.get("Mood") == "Ind"
                        and tense in TENSES and ft.get("VerbForm") != "Part"
                        and ft.get("Person") in ("1", "2", "3") and nb in ("Sing", "Plur")):
                    clef = TENSES[tense] + "-" + ft["Person"] + "-" + ("S" if nb == "Sing" else "P")
                    vv2[noeud][clef][forme.lower()] += 1
                if (pos in ("VERB", "AUX") and ft.get("VerbForm") == "Part"
                        and tense != "Pres" and g in ("Masc", "Fem") and nb in ("Sing", "Plur")):
                    vp[noeud][g + nb][forme.lower()] += 1
                if pos == "PRON" and ft.get("Person") in ("1", "2", "3"):
                    vpers[noeud][ft["Person"]] += 1
                r0 = rel.split(":")[0]
                if r0 == "aux" and head in idx:
                    dl = normaliser_structure(lem)
                    if dl in ("avoir", "etre"):
                        hl = norm(idx[head][1])
                        hn = noeud_pour(c.graph["neurones"], hl) if hl else None
                        if hn is not None:
                            vaux[hn][dl] += 1
                if r0 == "amod" and pos == "ADJ" and head in idx \
                        and idx[head][2] in ("NOUN", "PROPN"):
                    vplaces[noeud]["avant" if i < idx[head][0] else "apres"] += 1
                if r0 == "advmod" and head in idx and idx[head][2] in ("VERB", "AUX"):
                    dl = normaliser_structure(lem)
                    if dl in ("pas", "plus", "jamais"):
                        hl = norm(idx[head][1])
                        hn = noeud_pour(c.graph["neurones"], hl) if hl else None
                        if hn is not None:
                            vneg[hn][dl] += 1

    with open(conllu, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne:
                if toks:
                    vider()
                    toks = []
                continue
            if ligne.startswith("#"):
                continue
            p = ligne.split("\t")
            if "-" in p[0] or "." in p[0]:
                continue
            toks.append((int(p[0]), p[2], p[3], int(p[6]), lire_traits(p[5]), p[1], p[7]))
    if toks:
        vider()
    for noeud, cpt in vg.items():
        c.genres[noeud] = "M" if top(cpt) == "Masc" else "F"
    for noeud, cpt in vn.items():
        c.nombres[noeud] = "S" if top(cpt) == "Sing" else "P"
    for noeud, par_nb in vf.items():
        c.flexions[noeud] = {("S" if nb == "Sing" else "P"): top(cpt)
                             for nb, cpt in par_nb.items()}
    for noeud, par_gn in va.items():
        conv = {"MascSing": "MS", "FemSing": "FS", "MascPlur": "MP", "FemPlur": "FP"}
        c.adjectifs[noeud] = {conv[gn]: top(cpt) for gn, cpt in par_gn.items()}
    for noeud, par_nb in vv.items():
        c.conjugue[noeud] = {("S" if nb == "Sing" else "P"): top(cpt)
                             for nb, cpt in par_nb.items()}
    for noeud, par_nb in vd.items():
        c.determinants[noeud] = {("S" if nb == "Sing" else "P"): top(cpt)
                                 for nb, cpt in par_nb.items()}
    if complet:
        for noeud, par_tpn in vv2.items():
            c.conjugue[noeud] = {k: top(cpt) for k, cpt in par_tpn.items()}
        for noeud, par_gn in vp.items():
            conv = {"MascSing": "MS", "FemSing": "FS", "MascPlur": "MP", "FemPlur": "FP"}
            c.participes[noeud] = {conv[gn]: top(cpt) for gn, cpt in par_gn.items()}
        for noeud, cpt in vaux.items():
            c.auxiliaires[noeud] = max(cpt.items(),
                key=lambda kv: (kv[1], kv[0] == "avoir"))[0]  # avoir gagne les égalités (défaut 90 %+ des verbes)
        for noeud, cpt in vplaces.items():
            c.places[noeud] = top(cpt)
        for noeud, cpt in vpers.items():
            c.personnes[noeud] = top(cpt)
        for noeud, cpt in vneg.items():
            c.negations[noeud] = top(cpt)


def extraire_structure(conllu, structure):
    """Arcs qui touchent la structure (un bout suffit), toutes relations.
    normaliser_structure : réfugiés + 1-lettre (le contenu garde son filtre)."""
    arcs = Counter()
    toks = []

    def vider():
        idx = {t[0]: t for t in toks}
        for (i, lem, pos, head, rel) in toks:
            if head == 0 or head not in idx:
                continue
            l1 = normaliser_structure(lem)
            l2 = normaliser_structure(idx[head][1])
            if not l1 or not l2:
                continue
            if l1 in structure or l2 in structure:
                arcs[(l1, l2, rel.split(":")[0])] += 1

    with open(conllu, encoding="utf-8") as fh:
        for ligne in fh:
            ligne = ligne.strip()
            if not ligne:
                if toks:
                    vider()
                    toks = []
                continue
            if ligne.startswith("#"):
                continue
            p = ligne.split("\t")
            if "-" in p[0] or "." in p[0]:
                continue
            toks.append((int(p[0]), p[2], p[3], int(p[6]), p[7]))
    if toks:
        vider()
    return arcs


def ecole_grammaire(c, conllu):
    """L'ÉCOLE DE GRAMMAIRE (leçon 36) : les articles + les accords.

    1. Les articles sont de vrais nerfs (injectés + figés, motif MARTICLES).
    2. Leurs constructions (le contenu d'abord : pas d'écrasement).
    3. L'oreille + la bouche repassent (idempotents : que du neuf).
    4. Les accords en un passage FEATS : genres, nombres, flexions,
       adjectifs, conjugaison (présent 3e), déterminants observés.
    """
    import contextlib
    import io
    arts = extraire_articles(conllu)
    gardes = {}
    for (a, b, r), n in arts.items():
        if (a, b) not in gardes or gardes[(a, b)][1] < n:
            gardes[(a, b)] = (r, n)
    frag = _fragment(gardes, set(), "UD_French-GSD train (articles)")
    st_inject = injecter(c, frag)
    with contextlib.redirect_stdout(io.StringIO()):
        res_figer = c.figer()
    for l in frag["liens"]:
        na = neurone_pour(c, l["a"])
        nb = neurone_pour(c, l["b"])
        paire = tuple(sorted((na, nb)))
        dep = l["a"] if (l["a"], l["b"], "det") in arts else l["b"]
        c.constructions.setdefault(paire, ("det", neurone_pour(c, dep)))
    st_or = ecole_oreille(c, conllu)
    st_bou = ecole_bouche(c, conllu)
    passer_accords(c, conllu)
    return {"articles": {"neurones": st_inject["neurones"], "liens": st_inject["liens"],
                         "epargnes": st_inject["marbre_epargne"],
                         "figes": len(res_figer["figes"])},
            "oreille": st_or, "bouche": st_bou, "genres": len(c.genres),
            "nombres": len(c.nombres), "flexions": len(c.flexions),
            "adjectifs": len(c.adjectifs), "conjugue": len(c.conjugue),
            "determinants": len(c.determinants)}


def grammaire_cli(args):
    c = Cerveau.relire(args.injecter)
    stats = ecole_grammaire(c, args.conllu)
    c.graver(args.sortie)
    a = stats["articles"]
    print(f"GRAMMAIRE — articles : +{a['neurones']} nerfs +{a['liens']} liens "
          f"({a['epargnes']} épargnés), {a['figes']} figés")
    print(f"GRAMMAIRE — accords : {stats['genres']} genres, {stats['nombres']} nombres, "
          f"{stats['flexions']} flexions, {stats['adjectifs']} adjectifs, "
          f"{stats['conjugue']} verbes, {stats['determinants']} déterminants")
    print(f"GRAVÉ — {args.sortie}")
    return 0


def ecole_bases(c, conllu):
    """L'ÉCOLE DES BASES (leçon 37) : TOUTE la structure, une fois.

    1. La structure = lemmes à nature de structure (POS majoritaire) +
       réfugiés (la stopliste rend ne/pas/être/avoir).
    2. Vrais nerfs + vrais liens (toutes relations, le plus prouvé gagne),
       figés ; constructions en setdefault (contenu > articles > structure).
    3. L'oreille + la bouche repassent (idempotents : que du neuf).
    4. passer_accords complet : conjugaison totale, participes, auxiliaires,
       places, personnes, négations (+ genres/nombres des nouveaux).
    """
    import contextlib
    import io
    pos_votes = extraire_natures_pos(conllu, structure=True)
    structure = {l for l, cpt in pos_votes.items()
                 if sorted(cpt.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
                 in POS_STRUCTURE}
    structure |= REFUGIES
    arcs = extraire_structure(conllu, structure)
    gardes = {}
    for (a, b, r), n in arcs.items():
        if (a, b) not in gardes or gardes[(a, b)][1] < n:
            gardes[(a, b)] = (r, n)
    frag = _fragment(gardes, set(), "UD_French-GSD train (structure)")
    st_inject = injecter(c, frag)
    with contextlib.redirect_stdout(io.StringIO()):
        res_figer = c.figer()
    for l in frag["liens"]:
        na = neurone_pour(c, l["a"])
        nb = neurone_pour(c, l["b"])
        paire = tuple(sorted((na, nb)))
        # gardes ordonnés : a = le dépendant (direction préservée).
        c.constructions.setdefault(paire, (l["rel"], neurone_pour(c, l["a"])))
    st_or = ecole_oreille(c, conllu)
    st_bou = ecole_bouche(c, conllu)
    passer_accords(c, conllu, complet=True)
    return {"structure": {"mots": len(structure), "neurones": st_inject["neurones"],
                          "liens": st_inject["liens"],
                          "epargnes": st_inject["marbre_epargne"],
                          "figes": len(res_figer["figes"])},
            "oreille": st_or, "bouche": st_bou, "genres": len(c.genres),
            "nombres": len(c.nombres), "flexions": len(c.flexions),
            "adjectifs": len(c.adjectifs), "conjugue": len(c.conjugue),
            "determinants": len(c.determinants), "participes": len(c.participes),
            "auxiliaires": len(c.auxiliaires), "places": len(c.places),
            "personnes": len(c.personnes), "negations": len(c.negations)}


def bases_cli(args):
    c = Cerveau.relire(args.injecter)
    stats = ecole_bases(c, args.conllu)
    c.graver(args.sortie)
    s = stats["structure"]
    print(f"BASES — structure : {s['mots']} mots, +{s['neurones']} nerfs "
          f"+{s['liens']} liens ({s['epargnes']} épargnés), {s['figes']} figés")
    print(f"BASES — tables : {stats['conjugue']} conjugaisons, {stats['participes']} participes, "
          f"{stats['auxiliaires']} auxiliaires, {stats['places']} places, "
          f"{stats['personnes']} personnes, {stats['negations']} négations")
    print(f"GRAVÉ — {args.sortie}")
    return 0


def injecter(c, fragment):
    """Pousse le fragment au cerveau (soudure, pas d'écoutes)."""
    stats = {"neurones": 0, "liens": 0, "motifs": 0, "marbre_epargne": 0}
    c.motifs = dict(c.motifs)  # copie : on ne touche pas au pack partagé
    conv = {}
    for lemme in fragment["neurones"]:
        avant = len(c.graph["neurones"])
        conv[lemme] = neurone_pour(c, lemme)
        stats["neurones"] += len(c.graph["neurones"]) - avant
    for l in fragment["liens"]:
        a, b = conv[l["a"]], conv[l["b"]]
        cle = tuple(sorted((a, b)))
        if cle in c.graph["liens"]:
            stats["marbre_epargne"] += 1  # le marbre ne se réécrit pas
            continue
        c.graph["liens"][cle] = l["force"]
        c.chaines.add(cle)
        stats["liens"] += 1
    for nom, membres in fragment["motifs"].items():
        vieux = set(c.motifs.get(nom, []))
        c.motifs[nom] = sorted(vieux | {conv[m] for m in membres})
        stats["motifs"] += 1
    c._tissu_sale = True  # le graphe a pris de l'avance : l'interprète reconstruira
    return stats


def echantillonner(arcs, racines, graine, k):
    """Un tour de remix : K paires brassées (graine -> reproductible).

    Même schéma que convertir (liens, loi 10x, motifs-relations) : le tour
    est un fragment comme un autre, la graine change, le code non."""
    import random
    items = sorted(arcs.items())
    ordre = list(range(len(items)))
    random.Random(graine).shuffle(ordre)
    gardes = {}
    for i in ordre[:k]:
        (a, b, r), n = items[i]
        if (a, b) not in gardes or gardes[(a, b)][1] < n:
            gardes[(a, b)] = (r, n)
    return _fragment(gardes, racines, "UD_French-GSD train (remix)", graine=graine)


def remix(args):
    """LE REMIX : N tours graineés sur tout le réservoir, figé à chaque tour."""
    import contextlib
    import io
    arcs, racines = extraire(args.conllu, None)
    print(f"RÉSERVOIR — {sum(arcs.values())} arcs, {len(arcs)} paires uniques")
    c = Cerveau.relire(args.injecter)
    absorbees = set()
    for r in range(args.tours):
        frag = echantillonner(arcs, racines, args.graines + r, args.paires)
        stats = injecter(c, frag)
        with contextlib.redirect_stdout(io.StringIO()):
            res = c.figer()
        for l in frag["liens"]:
            absorbees.add((l["a"], l["b"]))
        print(f"tour {r + 1}/{args.tours} : +{stats['neurones']} neurones "
              f"+{stats['liens']} liens (épargné {stats['marbre_epargne']}) | "
              f"total {len(c.graph['neurones'])} neurones {len(c.graph['liens'])} liens, "
              f"{len(res['figes'])} figés", flush=True)
    c.graver(args.sortie)
    print(f"REMIX FINI — {len(c.graph['neurones'])} neurones, {len(c.graph['liens'])} liens, "
          f"{len(c.motifs)} motifs, écoutes {c.ecoutes}")
    print(f"COUVERTURE — {len(absorbees)}/{len(arcs)} paires bues "
          f"({100 * len(absorbees) // len(arcs)} % du réservoir)")
    print(f"GRAVÉ — {args.sortie}")
    return 0


def lemme_de(neurone):
    return neurone[5:] if neurone.startswith("word_") else neurone


def tout_boire(args):
    """JUSQU'AU FOND : vide le réservoir (brassé, par vagues) jusqu'à 0 restant.

    Le cerveau EST le registre : sue = le lien existe (marbre respecté, on
    ne réécrit pas). Terminaison garantie : la liste du reste est fixée
    d'avance, chaque vague la vide. Boucles X->X : soudées comme le reste
    (précédent : 198 déjà en marbre)."""
    import contextlib
    import io
    import random
    arcs, racines = extraire(args.conllu, None)
    reserve = {}
    for (a, b, r), n in arcs.items():
        cle = tuple(sorted((a, b)))
        if cle not in reserve or reserve[cle][1] < n:
            reserve[cle] = (r, n)
    c = Cerveau.relire(args.injecter)
    sues = {tuple(sorted((lemme_de(a), lemme_de(b)))) for a, b in c.graph["liens"]}
    sues &= set(reserve)
    print(f"RÉSERVOIR — {len(reserve)} paires (déjà sues : {len(sues)})")
    reste = sorted(set(reserve) - sues)
    random.Random(args.graines).shuffle(reste)
    vagues = [reste[i:i + args.paires] for i in range(0, len(reste), args.paires)]
    for i, vague in enumerate(vagues):
        gardes = {p: reserve[p] for p in vague}
        frag = _fragment(gardes, racines, "UD_French-GSD train (fond du verre)",
                         vague=i + 1)
        stats = injecter(c, frag)
        with contextlib.redirect_stdout(io.StringIO()):
            res = c.figer()
        restant = len(reste) - min((i + 1) * args.paires, len(reste))
        print(f"vague {i + 1}/{len(vagues)} : +{stats['neurones']} neurones "
              f"+{stats['liens']} liens | total {len(c.graph['neurones'])} neurones "
              f"{len(c.graph['liens'])} liens, {len(res['figes'])} figés | "
              f"reste {restant}", flush=True)
    c.graver(args.sortie)
    print(f"RÉSERVOIR VIDE — {len(c.graph['neurones'])} neurones, {len(c.graph['liens'])} "
          f"liens, {len(c.motifs)} motifs, écoutes {c.ecoutes} (100 % bu ✅)")
    print(f"GRAVÉ — {args.sortie}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--conllu", required=True)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--fragment", default="education-manuelle/fragment-ud-fr.json")
    ap.add_argument("--injecter", default=None, help="cerveau gravé à pousser")
    ap.add_argument("--sortie", default=None, help="cerveau poussé + figé, gravé ici")
    ap.add_argument("--tours", type=int, default=0,
                    help="remix : N tours sur TOUT le réservoir (0 = un seul fragment topk)")
    ap.add_argument("--graines", type=int, default=1000, help="graine de base des tours")
    ap.add_argument("--paires", type=int, default=500, help="paires brassées par tour")
    ap.add_argument("--jusquau-fond", action="store_true",
                    help="vide TOUT le réservoir par vagues (s'arrête à 0 restant)")
    ap.add_argument("--oreille", action="store_true",
                    help="école de l'oreille : apprend les mots du conllu déjà en nerfs")
    ap.add_argument("--bouche", action="store_true",
                    help="école de la bouche : apprend comment chaque lien tenu se parle")
    ap.add_argument("--grammaire", action="store_true",
                    help="école de grammaire : articles + accords (genres, nombres, présent)")
    ap.add_argument("--bases", action="store_true",
                    help="école des bases : TOUTE la structure + tables complètes, une fois")
    args = ap.parse_args(argv)
    if args.bases:
        assert args.tours == 0 and not args.jusquau_fond and not args.oreille \
            and not args.bouche and not args.grammaire, "--bases seul"
        assert args.injecter and args.sortie, "--injecter + --sortie exigés"
        return bases_cli(args)
    if args.grammaire:
        assert args.tours == 0 and not args.jusquau_fond and not args.oreille \
            and not args.bouche, "--grammaire seul"
        assert args.injecter and args.sortie, "--injecter + --sortie exigés"
        return grammaire_cli(args)
    if args.bouche:
        assert args.tours == 0 and not args.jusquau_fond and not args.oreille, "--bouche seul"
        assert args.injecter and args.sortie, "--injecter + --sortie exigés"
        return bouche_cli(args)
    if args.oreille:
        assert args.tours == 0 and not args.jusquau_fond, "--oreille seul"
        assert args.injecter and args.sortie, "--injecter + --sortie exigés"
        return ecole_cli(args)
    if args.jusquau_fond:
        assert args.tours == 0, "--tours et --jusquau-fond sont exclusifs"
        assert args.injecter and args.sortie, "--injecter + --sortie exigés"
        return tout_boire(args)
    if args.tours > 0:
        assert args.injecter and args.sortie, "--injecter + --sortie exigés avec --tours"
        return remix(args)
    _, mots = charger()
    nos = set(mots)
    arcs, racines = extraire(args.conllu, nos)
    fragment = convertir(arcs, racines, nos, args.topk)
    with open(args.fragment, "w", encoding="utf-8") as fh:
        json.dump(fragment, fh, ensure_ascii=False, indent=1)
    print(f"FRAGMENT — {len(fragment['neurones'])} mots, {len(fragment['liens'])} liens, "
          f"{len(fragment['motifs'])} motifs -> {args.fragment}")
    if args.injecter:
        assert args.sortie, "--sortie exigé avec --injecter"
        c = Cerveau.relire(args.injecter)
        avant = (len(c.graph["neurones"]), len(c.graph["liens"]))
        stats = injecter(c, fragment)
        res = c.figer()
        c.graver(args.sortie)
        print(f"POUSSÉ — +{stats['neurones']} neurones, +{stats['liens']} liens, "
              f"+{stats['motifs']} motifs ({stats['marbre_epargne']} marbre épargné)")
        print(f"CERVEAU — {avant[0]}->{len(c.graph['neurones'])} neurones, "
              f"{avant[1]}->{len(c.graph['liens'])} liens, {len(res['figes'])} figés, "
              f"{res['filaments']} filaments, écoutes {c.ecoutes} (R5 : intactes)")
        print(f"GRAVÉ — {args.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
