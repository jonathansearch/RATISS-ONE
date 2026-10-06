#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ÉDUQUER v1 — l'éducateur : des phrases, pas du tissage à la main (route B).
RATISS Labs · MIT.

Protocole : graine = Cerveau FR éduqué (13 neurones) ; chaque phrase fait
naître ses nœuds/liens manquants (force 10, la naissance), puis
rencontre + propager + `renforcer lie 10 delie D` + repos. D = 0 par défaut :
l'éducation SÉLECTIVE exige délie 0 (sinon chaque phrase efface les autres —
le prouver : --delie 10, le témoin catastrophique). Nuits : oublier x2.

Motifs hérités : chaque mot nouveau tient à son ancre (motif paire) et à son
compagnon le plus fréquent (motif triple). Zéro tissage manuel au-delà.

Usage : python3 education/eduquer.py [--export F] [--delie D] [--rounds R] [--nuits N]
"""

import argparse
import os
import sys
from collections import Counter

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)
from ratum import Interprete  # noqa: E402
from cerveau.cerveau import Cerveau, LANGUES  # noqa: E402

NAISSANCE = 10
ANCIENS = ("amis", "peuple", "pays", "patrie", "unir")
TEMOINS = ("etoile", "tambour", "nuage", "encre", "silex")
CANDIDATS_ANCRE = ANCIENS + ("soleil", "livre")


def charger_corpus(chemin):
    phrases = []
    for ligne in open(chemin, encoding="utf-8"):
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#"):
            phrases.append(ligne.split())
    return phrases


def max_deterministe(compteurs, candidats):
    return sorted(candidats, key=lambda w: (-compteurs.get(w, 0), w))[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", default=os.path.join(ICI, "vocabulaire50.ratum"))
    ap.add_argument("--delie", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--nuits", type=int, default=2)
    args = ap.parse_args()

    phrases = charger_corpus(os.path.join(ICI, "corpus.txt"))
    couv = Counter(w for p in phrases for w in p)
    mots = sorted(couv)
    assert len(phrases) == 37 and len(mots) == 50, (len(phrases), len(mots))
    for w in mots:
        if w not in ANCIENS and w not in ("soleil", "livre"):
            assert couv[w] == 3, (w, couv[w])
    print(f"corpus : {len(phrases)} phrases, {len(mots)} mots (45 nouveaux x3)")

    # co-occurrences (pour les motifs hérités)
    cooc = {w: Counter() for w in mots}
    for p in phrases:
        for a in p:
            for b in p:
                if a != b:
                    cooc[a][b] += 1

    print("graine : Cerveau FR éduqué…")
    c = Cerveau("FR")
    tiss = c.itp.tissu
    noeuds = set(tiss.neurones)
    liens = set(tiss.liens)
    naiss_n, naiss_l = 0, 0

    def naitre(mot):
        nonlocal naiss_n, naiss_l
        n = "word_" + mot
        if n not in noeuds:
            c._exec(f"neurone {n} seuil 50\n")
            noeuds.add(n)
            naiss_n += 1

    def relier(a, b):
        nonlocal naiss_l
        cle = tuple(sorted((a, b)))
        if cle not in liens:
            c._exec(f"lien {a} {b} force {NAISSANCE}\n")
            liens.add(cle)
            naiss_l += 1

    for t in TEMOINS:  # les témoins naissent mais n'entendront jamais rien
        naitre(t)
        relier("word_" + t, "lointain")

    for r in range(args.rounds):
        for p in phrases:
            ns = ["word_" + w for w in p]
            for w in p:
                naitre(w)
            for i in range(len(ns)):
                for j in range(i + 1, len(ns)):
                    relier(ns[i], ns[j])
            c._exec(f"motif PHRASE : {' '.join(ns)}\nrencontre PHRASE\npropager\n"
                    f"renforcer lie 10 delie {args.delie}\nrepos\n")
        c._sync()
    for _ in range(args.nuits):
        c._exec("oublier\n")
    c._sync()
    print(f"naissances : {naiss_n} neurones, {naiss_l} liens "
          f"(rounds={args.rounds}, delie={args.delie}, nuits={args.nuits})")

    # motifs hérités : ancre + compagnon les plus fréquents
    ancres, compagnons = {}, {}
    for w in mots:
        if w in ANCIENS:
            continue
        a = max_deterministe(cooc[w], [x for x in CANDIDATS_ANCRE if x != w])
        k = max_deterministe(cooc[w], [x for x in mots if x not in (w, a)])
        ancres[w], compagnons[w] = a, k
        c._exec(f"motif M_{w.upper()} : word_{w} word_{a}\n"
                f"motif T_{w.upper()} : word_{w} word_{a} word_{k}\n")
    for t in TEMOINS:
        c._exec(f"motif TEMOIN_{t.upper()} : word_{t} lointain\n")

    # verdicts
    paires, triples = {}, {}
    for w in sorted(set(mots) - set(ANCIENS)):
        paires[w] = c.resonance(f"M_{w.upper()}")
        triples[w] = c.resonance(f"T_{w.upper()}")
    vieux = {m: c.resonance(m) for m in
             ("MAMIS", "MPEUPLE", "MPAYS", "MPATRIE", "MUNIR")}
    tem = {t: c.resonance(f"TEMOIN_{t.upper()}") for t in TEMOINS}
    tem["avenir"] = c.resonance("MAVENIR")

    n_tiennent = sum(1 for v in paires.values() if v >= 60)
    n_vieux = sum(1 for v in vieux.values() if v >= 60)
    n_dehors = sum(1 for v in tem.values() if v < 20)
    print(f"--- paires (mot-ancre, seuil 60) : {n_tiennent}/45 ---")
    for w in sorted(paires):
        print(f"  {w:9s} + {ancres[w]:9s} = {paires[w]:3d} "
              f"(triple {compagnons[w]:9s} : {triples[w]:3d})")
    print(f"--- anciens : {n_vieux}/5 " +
          " ".join(f"{m}={v}" for m, v in sorted(vieux.items())) + " ---")
    print("--- témoins (seuil 20) : " +
          " ".join(f"{t}={v}" for t, v in sorted(tem.items())) + " ---")
    # familles : la cohésion des constellations (richesse, pas verdict)
    familles = {
        "VILLAGE": ["amis", "peuple", "pain", "eau", "enfants", "marche",
                    "maison", "fete", "voisins", "rue", "village"],
        "DEVOIR": ["pays", "patrie", "unir", "honneur", "drapeau", "paix",
                   "justice", "loi", "serment", "defendre"],
        "NATURE": ["soleil", "lune", "arbre", "riviere", "montagne", "fleur",
                   "oiseau", "vent", "pluie", "ciel"],
        "ESPRIT": ["livre", "mots", "histoire", "chanson", "question", "reponse",
                   "savoir", "idee", "ecole", "maitre", "memoire"],
        "PONTS": ["main", "coeur", "chemin", "porte", "feu", "nuit", "matin", "temps"],
    }
    res_fam = {}
    for nom, membres in familles.items():
        c._exec(f"motif F_{nom} : {' '.join('word_' + w for w in membres)}\n")
        res_fam[nom] = c.resonance(f"F_{nom}")
    print("--- familles (cohésion) : " +
          " ".join(f"{n}={v}" for n, v in sorted(res_fam.items())) + " ---")
    forces = list(c.graph["liens"].values())
    buckets = Counter(min(f // 20 * 20, 80) for f in forces)
    print("--- forces : " + " ".join(
        f"{b}-{b + 19 if b < 80 else 100}:{buckets.get(b, 0)}" for b in (0, 20, 40, 60, 80)) + " ---")
    bilan = f"BILAN : {n_tiennent + n_vieux} mots sur 50 tiennent (seuil 60)"
    temoin = f"TEMOINS : {n_dehors} dehors sur 6 (seuil 20)"
    print(bilan)
    print(temoin)

    # export déterministe : le tissu final rejouable en pur Ratum
    # (neurones lus sur le tissu VIVANT — le graphe Python ne suit pas les naissances)
    L = ["# VOCABULAIRE50 — tissu éduqué par phrases (généré, voir education/eduquer.py)",
         "# graine FR + 37 phrases x3 rounds + 2 nuits. Régénéré avant chaque batterie.",
         "", "tissu Vocabulaire", ""]
    for n in sorted(tiss.neurones):
        L.append(f"  neurone {n} seuil {tiss.neurones[n]['seuil']}")
    L.append("")
    for (a, b) in sorted(c.graph["liens"]):
        L.append(f"  lien {a} {b} force {c.graph['liens'][(a, b)]}")
    L.append("")
    for nom in sorted(tiss.motifs):
        if nom == "PHRASE":
            continue
        L.append(f"  motif {nom} : " + " ".join(tiss.motifs[nom]))
    L.append("")
    L.append("  dire === VERDICTS (45 paires + 5 anciens + 6 témoins) ===")
    for w in sorted(paires):
        L.append(f"  juger M_{w.upper()} 60")
    for m in ("MAMIS", "MPEUPLE", "MPAYS", "MPATRIE", "MUNIR"):
        L.append(f"  juger {m} 60")
    for t in sorted(tem):
        nom = "MAVENIR" if t == "avenir" else f"TEMOIN_{t.upper()}"
        L.append(f"  juger {nom} 20")
    L.append("  mesurer")
    L.append(f"  dire {bilan}")
    L.append(f"  dire {temoin}")
    L.append("")
    L.append("fin")
    with open(args.export, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"exporté : {args.export} "
          f"({len(tiss.neurones)} neurones, {len(c.graph['liens'])} liens)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
