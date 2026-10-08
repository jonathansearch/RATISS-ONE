#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'ÉCOLE MANUELLE — convertisseur dialogues -> CISE sur mesure (leçon 38).
RATISS Labs · MIT.

Prend des dialogues BRUTS (tours de parole, zéro annotation : pas de lemmes,
ni natures, ni traits) et les convertit en fragment CISE : paires de mots
qui SE SUIVENT (MSUITE, dans un tour) ou SE RÉPONDENT (MREPONSE, d'un tour
à l'autre quand le locuteur change). Même moteur que convertisseur_ud
(injecter, Cerveau, figer) : seul l'extracteur change.

Format lu (v1, style Accueil_UBS) : lignes "X: texte" (X = une lettre,
le locuteur) ; le reste est ignoré. Fichiers *.txt, triés. Encodage :
utf-8 essayé, repli latin-1 (les vieux corpus scolaires).

Règles du tokeniseur (simples, documentées, pinnées par la batterie) :
- groupes de lettres uniquement (chiffres et ponctuation tombent, les
  apostrophes et traits d'union COUPENT : "aujourd'hui" -> aujourd + hui).
- forme accentuée d'abord (tables de la leçon 34 : c.formes), sinon
  normalisation simple (minuscules, accents retirés).
- 1-lettre : seuls "a" (à/a) et "y" passent (comme la leçon 37).
- les HÉSITATIONS ("e") et les BRUITS (liste ci-dessous, repérés à la
  main : morceaux de mots coupés, coquilles du transcripteur, bruits
  de bouche, intrusions anglaises) ne sont pas appris ET coupent le
  tour : pas de paire à travers (pas de faux voisins).

Lois (mêmes que l'école UD) :
- force = min(100, 10 x rencontres) — la répétition prouve.
- le marbre ne se réécrit pas : lien existant = on ne touche pas.
- R5 : l'injection manuelle n'est pas une écoute (compteur inchangé).
- la bouche dialogue ne REMPLACE pas la bouche UD (setdefault : la
  grammaire garde la priorité, le dialogue n'apprend que le neuf).
- PAS d'école de grammaire ici : sans traits annotés, ni genres ni
  tables (l'école UD les porte déjà) — assumé, pas oublié.

Usage :
  python3 education-manuelle/convertisseur_dialogues.py --dialogues DIR
  python3 education-manuelle/convertisseur_dialogues.py --dialogues DIR --injecter cerveau/fige-300M-bases.json.gz --sortie cerveau/fige-300M-accueil.json.gz
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cerveau.cerveau import Cerveau, noeud_pour  # noqa: E402
from convertisseur_ud import injecter, normaliser_structure  # noqa: E402

LETTRES = re.compile(r"[a-zàâäéèêëîïôöùûüç]+")
TOUR = re.compile(r"^([a-zA-Z])\s*:\s*(.*)$")
HESITATIONS = {"e"}
BRUITS = {
    # morceaux de mots coupés (transcription orale, repérés à la main)
    "aujourd", "hui", "jusqu", "teleph", "automati", "entrepri", "remerc",
    "rmations", "scolar", "scora", "reun", "repro", "ouvir", "pelez", "rap",
    "rep", "pers", "ie", "int", "ite", "lle", "men", "mie", "iger", "idation",
    "oir", "oit", "utes", "pi", "pmo", "onne", "madam", "ernet", "quelqu",
    "voye",
    # coquilles du transcripteur
    "boujour", "rapeler",
    # bruits de bouche / marques
    "bb", "pf", "mps", "xx",
    # intrusions anglaises (corpus FR : on ne garde que le français)
    "beans", "cheese", "pronounce",
    # inclassables
    "ohannic", "tohannic",
}
UNE_LETTRE = {"a", "y"}
MOTIF_SUITE = "MSUITE"
MOTIF_REPONSE = "MREPONSE"


def lire_fichier(chemin):
    """Un fichier -> [(locuteur, texte)] (utf-8, repli latin-1)."""
    brut = open(chemin, "rb").read()
    try:
        texte = brut.decode("utf-8")
    except UnicodeDecodeError:
        texte = brut.decode("latin-1")
    tours = []
    for ligne in texte.splitlines():
        m = TOUR.match(ligne.strip().strip("\ufeff"))
        if m:
            tours.append((m.group(1).lower(), m.group(2)))
    return tours


def tokeniser(texte, formes):
    """Un tour -> [segments] (un segment = [lemmes], coupé aux bruits)."""
    segments, courant = [], []
    for morceau in LETTRES.findall(texte.lower()):
        if morceau in HESITATIONS or morceau in BRUITS:
            if courant:
                segments.append(courant)
                courant = []
            continue
        if len(morceau) < 2 and morceau not in UNE_LETTRE:
            continue
        lemme = formes.get(morceau) or normaliser_structure(morceau)
        if lemme:
            courant.append(lemme)
    if courant:
        segments.append(courant)
    return segments


def extraire(chemin, formes=None):
    """Un dossier (ou fichier) de dialogues -> (arcs, stats).

    arcs : Counter (mot1, mot2, relation) ; relations = "suite" (mots
    voisins dans un segment) ou "reponse" (fin d'un tour -> début du
    suivant, locuteur changé) ; même locuteur de suite = "suite".
    formes : dict forme -> lemme (celui du cerveau, ou {} = normalisé)."""
    from collections import Counter
    formes = formes or {}
    if os.path.isdir(chemin):
        fichiers = sorted(f for f in os.listdir(chemin) if f.endswith(".txt"))
        fichiers = [os.path.join(chemin, f) for f in fichiers]
    else:
        fichiers = [chemin]
    arcs = Counter()
    dialogues, tours, mots = 0, 0, 0
    for f in fichiers:
        tours_f = lire_fichier(f)
        if not tours_f:
            continue
        dialogues += 1
        precedent = None  # (locuteur, dernier lemme)
        for loc, texte in tours_f:
            segments = tokeniser(texte, formes)
            tours += 1
            mots += sum(len(s) for s in segments)
            for seg in segments:
                for x, y in zip(seg, seg[1:]):
                    arcs[(x, y, "suite")] += 1
            plats = [w for s in segments for w in s]
            if precedent is not None and plats:
                rel = "reponse" if loc != precedent[0] else "suite"
                arcs[(precedent[1], plats[0], rel)] += 1
            if plats:
                precedent = (loc, plats[-1])
    stats = {"dialogues": dialogues, "tours": tours, "mots": mots,
             "paires_uniques": len(arcs), "rencontres": sum(arcs.values())}
    return arcs, stats


def convertir(arcs, source, topk=0):
    """Arcs -> fragment CISE (déterministe : trié partout).

    topk = 0 : TOUT (petits corpus) ; topk > 0 : topk paires par mot
    (gros corpus : le tissu reste petit, comme la leçon 30)."""
    if topk and topk > 0:
        par_mot = {}
        for (a, b, r), n in arcs.items():
            par_mot.setdefault(a, []).append((a, b, r, n))
            par_mot.setdefault(b, []).append((a, b, r, n))
        gardes = {}
        for m, lst in par_mot.items():
            lst.sort(key=lambda t: (-t[3], t[0], t[1], t[2]))
            for (a, b, r, n) in lst[:topk]:
                if (a, b) not in gardes or gardes[(a, b)][1] < n:
                    gardes[(a, b)] = (r, n)
    else:
        gardes = {}
        for (a, b, r), n in arcs.items():
            if (a, b) not in gardes or gardes[(a, b)][1] < n:
                gardes[(a, b)] = (r, n)
    liens, motifs = [], {MOTIF_SUITE: set(), MOTIF_REPONSE: set()}
    for (a, b) in sorted(gardes):
        r, n = gardes[(a, b)]
        liens.append({"a": a, "b": b, "force": min(100, 10 * n),
                      "n": n, "rel": r})
        motifs[MOTIF_REPONSE if r == "reponse" else MOTIF_SUITE].update((a, b))
    mots = sorted({w for l in liens for w in (l["a"], l["b"])})
    return {
        "format": "fragment-cise-dialogues-v1",
        "source": source,
        "loi": "force = min(100, 10 x rencontres)",
        "mots_touches": mots,
        "neurones": mots,
        "liens": liens,
        "motifs": {k: sorted(v) for k, v in sorted(motifs.items()) if v},
        "stats": {"rencontres": sum(arcs.values()),
                  "paires_uniques": len(arcs),
                  "paires_gardees": len(liens),
                  "mots_touches": len(mots)},
    }


def ecole_oreille_dial(c, lemmes):
    """L'oreille apprend les mots du dialogue déjà en nerfs (idempotent)."""
    mots, sourds = 0, 0
    for lemme in sorted(lemmes):
        noeud = noeud_pour(c.graph["neurones"], lemme)
        if noeud is None:
            sourds += 1
            continue
        c.oreille[lemme] = [noeud]
        mots += 1
    return {"mots": mots, "sourds": sourds}


def ecole_bouche_dial(c, arcs):
    """La bouche apprend comment chaque lien tenu se parle : paire ->
    (relation la plus prouvée, second mot). setdefault : l'UD garde
    la priorité, le dialogue n'apprend que le neuf. Idempotent."""
    reserve = {}
    for (a, b, r), n in arcs.items():
        clef = tuple(sorted((a, b)))
        if clef not in reserve or reserve[clef][2] < n:
            reserve[clef] = (r, b, n)
    paires, sans_lien = 0, 0
    for (a, b), (r, dep, n) in sorted(reserve.items()):
        na = noeud_pour(c.graph["neurones"], a)
        nb = noeud_pour(c.graph["neurones"], b)
        paire = tuple(sorted((na, nb))) if na is not None and nb is not None else None
        if paire is None or paire not in c.graph["liens"]:
            sans_lien += 1
            continue
        c.constructions.setdefault(paire, (r, noeud_pour(c.graph["neurones"], dep)))
        paires += 1
    return {"paires": paires, "sans_lien": sans_lien}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dialogues", required=True)
    ap.add_argument("--fragment", default=None)
    ap.add_argument("--topk", type=int, default=0)
    ap.add_argument("--injecter", default=None, help="cerveau gravé à pousser")
    ap.add_argument("--sortie", default=None, help="cerveau poussé + figé, gravé ici")
    args = ap.parse_args(argv)
    c = Cerveau.relire(args.injecter) if args.injecter else None
    formes = c.formes if c is not None else {}
    arcs, stats = extraire(args.dialogues, formes)
    print(f"DIALOGUES — {stats['dialogues']} dialogues, {stats['tours']} tours, "
          f"{stats['mots']} mots, {stats['paires_uniques']} paires uniques, "
          f"{stats['rencontres']} rencontres")
    fragment = convertir(arcs, args.dialogues, args.topk)
    print(f"FRAGMENT — {len(fragment['neurones'])} mots, {len(fragment['liens'])} liens, "
          f"{len(fragment['motifs'])} motifs")
    if args.fragment:
        with open(args.fragment, "w", encoding="utf-8") as fh:
            json.dump(fragment, fh, ensure_ascii=False, indent=1)
        print(f"FRAGMENT GRAVÉ — {args.fragment}")
    if args.injecter:
        assert args.sortie, "--sortie exigé avec --injecter"
        avant = (len(c.graph["neurones"]), len(c.graph["liens"]))
        stats_i = injecter(c, fragment)
        res = c.figer()
        st_bou = ecole_bouche_dial(c, arcs)
        st_or = ecole_oreille_dial(c, fragment["neurones"])
        c.graver(args.sortie)
        print(f"POUSSÉ — +{stats_i['neurones']} neurones, +{stats_i['liens']} liens, "
              f"+{stats_i['motifs']} motifs ({stats_i['marbre_epargne']} marbre épargné)")
        print(f"BOUCHE — {st_bou['paires']} paires parlables, {st_bou['sans_lien']} sans lien")
        print(f"OREILLE — {st_or['mots']} mots appris, {st_or['sourds']} sourds")
        print(f"CERVEAU — {avant[0]}->{len(c.graph['neurones'])} neurones, "
              f"{avant[1]}->{len(c.graph['liens'])} liens, {len(res['figes'])} figés, "
              f"écoutes {c.ecoutes} (R5 : intactes)")
        print(f"GRAVÉ — {args.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
