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
from cerveau.cerveau import Cerveau  # noqa: E402
from generer_masse import charger  # noqa: E402

CONTENU = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
STOPLISTE = {"ne", "pas", "etre", "avoir"}  # grammaire pure : attendra le constructeur

# Étiquette UD -> motif français (le français, pas le jargon).
REL_MOTIF = {
    "nsubj": "MSUJET", "obj": "MOBJET", "iobj": "MINDIRECT",
    "amod": "MEPITHETE", "advmod": "MMANIERE", "obl": "MCIRCONST",
    "nmod": "MCOMPLET", "acl": "MPROPOS", "appos": "MAPPOS",
    "conj": "MCONJOINT", "ccomp": "MPROP", "xcomp": "MPROP",
    "advcl": "MCIRCONST", "nummod": "MNOMBRE", "compound": "MMOT",
}
MOTIF_DIVERS = "MLIAISON"
MOTIF_RACINE = "MRACINE"


def normaliser(lemme):
    s = unicodedata.normalize("NFKD", lemme.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    if len(s) < 2 or not s.isalpha() or not s.isascii():
        return None
    if s in STOPLISTE:
        return None
    return s


def extraire(conllu, nos):
    """Lit le CoNLL-U : arcs (dépendant, tête, relation) touchant nos mots."""
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
            if l1 in nos or l2 in nos:
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
    liens, motifs = [], {}
    for (a, b) in sorted(gardes):
        r, n = gardes[(a, b)]
        force = min(100, 10 * n)  # LOI DE L'ÉCOLE
        liens.append({"a": a, "b": b, "force": force, "n": n, "rel": r})
        motifs.setdefault(REL_MOTIF.get(r, MOTIF_DIVERS), set()).update((a, b))
    mots = sorted({w for l in liens for w in (l["a"], l["b"])})
    racines_ici = sorted(w for w in mots if w in racines)
    if racines_ici:
        motifs[MOTIF_RACINE] = set(racines_ici)
    return {
        "format": "fragment-cise-ud-v1",
        "source": "UD_French-GSD train (14 450 phrases, CC-BY-SA)",
        "loi": "force = min(100, 10 x rencontres)",
        "topk": topk,
        "mots_touches": sorted(par_mot),
        "neurones": mots,
        "liens": liens,
        "motifs": {k: sorted(v) for k, v in sorted(motifs.items())},
        "stats": {"arcs_lus": sum(arcs.values()), "paires_uniques": len(arcs),
                  "paires_gardees": len(liens), "mots_touches": len(par_mot)},
    }


def neurone_pour(c, lemme):
    """Un lemme -> neurone existant (concept ou word_X) ou neuf (word_X)."""
    if lemme in c.graph["neurones"]:
        return lemme
    nom = "word_" + lemme
    if nom not in c.graph["neurones"]:
        c.graph["neurones"][nom] = 50
    return nom


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
        c.motifs[nom] = [conv[m] for m in membres]
        stats["motifs"] += 1
    c._tissu_sale = True  # le graphe a pris de l'avance : l'interprète reconstruira
    return stats


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--conllu", required=True)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--fragment", default="education-manuelle/fragment-ud-fr.json")
    ap.add_argument("--injecter", default=None, help="cerveau gravé à pousser")
    ap.add_argument("--sortie", default=None, help="cerveau poussé + figé, gravé ici")
    args = ap.parse_args(argv)
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
