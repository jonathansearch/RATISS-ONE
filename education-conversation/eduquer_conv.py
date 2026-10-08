#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ÉDUQUER-CONVERSATION v1 — le tissu apprend à converser par petits morceaux.
RATISS Labs · MIT.

Vision du chef : pas de gros dataset — des petites scènes écoutées PLUSIEURS
fois. Le tissu ne stocke pas les mots (que des forces) donc il ne peut pas
halluciner ; quand il rate, LE COUP (on ré-écoute le juste, la loi efface le
faux) maximise les bons alliages.

Protocole : naissance des mots (neurone + nerf d'oreille) → ÉCOLE (cliques +
battements `delie 0`, régime sanctuarisé) → JOURNÉE (souffles q0+r en loi
réelle (10,3), compteur R5) → NUITS (oubli + faucheuse + secteurs) →
RACCOMMODAGE (l'école répare ce que la vie a effiloché — re-naissances,
re-liens, battements delie 0) → SONDE pure (rencontre Q + UNE vague, JAMAIS
renforcer : lire sans toucher, hors les mots de la question elle-même) →
COUPS sur les ratés (re-lien + frappe d'école, delie 0 sanctuarisé).

Usage :
  python3 education-conversation/eduquer_conv.py --regime canonique [--graver F]
  python3 education-conversation/eduquer_conv.py --regime pauvre|nul
  python3 education-conversation/eduquer_conv.py --reveil F (cerveau gravé re-testé)
"""
import argparse
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)
sys.path.insert(0, ICI)
from cerveau.cerveau import Cerveau, cle  # noqa: E402
from scenes import SCENES, TEMOINS, valider  # noqa: E402
import scenes as CONF  # noqa: E402

NAISSANCE = 10
REGIMES = {
    # Physique honnête : une journée de N battements en loi (10,3) efface
    # l'école du matin (36 érosions x 3 > 100, le plafond). D'où les DEVOIRS
    # du soir : l'école répare à la même dose — école le matin, vie le jour,
    # devoirs le soir, nuit qui consolide. Le nul (zéro école) meurt : normal.
    # nul : aucune école (ni avant ni après) — l'échec honnête, coups seuls.
    "nul":       {"rounds": 0, "fois": 1, "nuits": 1, "raccommode": 0},
    # pauvre : 1 round + devoirs x1 — la preuve que le coup rattrape.
    "pauvre":    {"rounds": 1, "fois": 1, "nuits": 1, "raccommode": 1},
    # canonique : 8 rounds + jour x3 + 4 nuits (SANCTUAIRE) + devoirs x8.
    "canonique": {"rounds": 8, "fois": 3, "nuits": 4, "raccommode": 8},
}


def noeud(mot):
    return "word_" + mot


class Eleve:
    """Le tissu-élève : naissances suivies au GRAPHE (piège documenté :
    la reconstruction ne voit que le graphe — tout ce qui naît au tissu
    doit être enregistré au graphe, sinon ça meurt à la première nuit)."""

    def __init__(self):
        self.c = Cerveau("FR")
        self.noeuds = set(self.c.itp.tissu.neurones)
        self.liens = set(self.c.itp.tissu.liens)
        self.naiss_n = 0
        self.naiss_l = 0

    def naitre(self, mot):
        n = noeud(mot)
        if n not in self.noeuds:
            self.c._exec(f"neurone {n} seuil 50\n")
            self.c.graph["neurones"][n] = 50
            self.noeuds.add(n)
            self.naiss_n += 1
        if mot not in self.c.oreille:
            self.c.oreille[mot] = [n]  # le nerf : sans lui, sourd

    def relier(self, a, b, force=NAISSANCE):
        k = cle(a, b)
        if k not in self.liens:
            self.c._exec(f"lien {a} {b} force {force}\n")
            self.c.graph["liens"][k] = force
            self.liens.add(k)
            self.naiss_l += 1

    def motif(self, nom, membres):
        """Motif miroir : crâne ET tissu (la reconstruction ne lit que le crâne)."""
        viv = [m for m in dict.fromkeys(membres) if m in self.noeuds]
        self.c.motifs[nom] = list(viv)
        if viv:
            self.c._exec(f"motif {nom} : {' '.join(viv)}\n")
        return viv

    def ecole(self, rounds):
        for _ in range(rounds):
            for nom, s in SCENES.items():
                mots = list(dict.fromkeys(s["q0"] + s["q1"] + s["r"]))
                for w in mots:
                    self.naitre(w)
                ns = [noeud(w) for w in mots]
                for i in range(len(ns)):
                    for j in range(i + 1, len(ns)):
                        self.relier(ns[i], ns[j])
                # v2 (école massive) : UNE SEULE vague — la sélectivité vit de l'ombre.
                self.motif("SCENE_" + nom, ns)
                self.c._exec(f"rencontre SCENE_{nom}\npropager\n"
                             "renforcer lie 10 delie 0\nrepos\n")
            self.c._sync()

    def journee(self, fois):
        """Les souffles du jour : q0+r D'UN SOUFFLE, loi réelle (10,3)."""
        for _ in range(fois):
            for nom, s in SCENES.items():
                self.c.entendre_sequence(s["q0"] + s["r"])

    def tailler(self):
        """Après la nuit : le graphe oublie les morts du tissu (pas de zombies).
        Les DEUX registres suivent (nœuds ET liens) — sinon `relier` croit
        les liens morts encore vivants et ne les ressuscite jamais."""
        viv = set(self.c.itp.tissu.neurones)
        for n in list(self.c.graph["neurones"]):
            if n not in viv:
                del self.c.graph["neurones"][n]
                self.noeuds.discard(n)
        for a, b in list(self.c.graph["liens"]):
            if a not in viv or b not in viv:
                del self.c.graph["liens"][(a, b)]
        self.liens = set(self.c.graph["liens"])  # les morts de `nettoyer` aussi
        for lemme in list(self.c.oreille):
            if self.c.oreille[lemme][0] not in viv:
                del self.c.oreille[lemme]
        for m in list(self.c.motifs):
            if m.startswith(("SCENE_", "R_", "Q_", "SONDE")):
                reste = [n for n in self.c.motifs[m] if n in viv]
                if reste:
                    self.c.motifs[m] = reste
                else:
                    del self.c.motifs[m]

    def sonder(self, q_mots):
        """SONDE PURE : rencontre Q + UNE vague, JAMAIS renforcer.
        La sonde mesure ce que la question ALLUME — hors ses propres mots
        (pas de points gratuits pour l'écho : R∩Q exclus du score).
        Rend {scene: allumage} (mort = 0 : le silence)."""
        c = self.c
        exclus = {noeud(w) for w in q_mots}
        viv = self.motif("SONDE", [noeud(w) for w in q_mots])
        if not viv:  # question morte : personne ne s'allume (silence honnête)
            return {nom: 0.0 for nom in SCENES}
        c._exec("rencontre SONDE\npropager\n")
        tiss = c.itp.tissu
        scores = {}
        for nom, s in SCENES.items():
            cibles = [noeud(w) for w in s["r"] if noeud(w) not in exclus]
            if not cibles:
                scores[nom] = 0.0
                continue
            ch = [tiss.neurones.get(n, {}).get("charge", 0) for n in cibles]
            scores[nom] = sum(ch) / len(ch)
        c._exec("repos\n")  # les charges, éphémères, ne persistent pas
        return scores

    def coup(self, nom):
        """LE COUP (ordre du chef) : on RÉ-ÉCOUTE le juste —
        1) re-liens (naissance des alliages morts), 2) frappe d'école
        (delie 0 : le juste se lie). JAMAIS de frappe de loi ici : le coup
        est un maître, pas la vie — décision (a) du chef, école delie 0
        sanctuarisée. (v1 avait une frappe de loi : les coups se mangeaient
        entre eux, −3 aux innocents pendant que le rival co-actif gagnait —
        le réveil tombait à 25/42. Coup d'école pur : plus de cannibalisme.)"""
        s = SCENES[nom]
        mots = list(dict.fromkeys(s["q0"] + s["q1"] + s["r"]))
        for w in mots:
            self.naitre(w)
        ns = [noeud(w) for w in mots]
        for i in range(len(ns)):
            for j in range(i + 1, len(ns)):
                self.relier(ns[i], ns[j])
        self.motif("SCENE_" + nom, ns)
        self.c._exec(f"rencontre SCENE_{nom}\npropager\n"
                     "renforcer lie 10 delie 0\nrepos\n")
        self.c._sync()


def juger(scores, attendu):
    trie = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    (top1, v1), (top2, v2) = trie[0], trie[1]
    if v1 == 0:
        top1 = "silence"
    ok = top1 == attendu and v1 >= CONF.SEUIL_TOP and (v1 - v2) >= CONF.MARGE
    return ok, top1, v1, top2, v2


def interroger(el, avec_coups=True, verbeux=True):
    """42 tests : q0/q1/q2 x 13 scènes + 3 témoins (silence exigé)."""
    bilan = {"tests": [], "coups": 0, "rattrapes": 0, "premier": 0}
    for nom, s in SCENES.items():
        for var in ("q0", "q1", "q2"):
            scores = el.sonder(s[var])
            ok, top1, v1, top2, v2 = juger(scores, nom)
            if ok:
                bilan["premier"] += 1
            coups = 0
            while not ok and avec_coups and coups < CONF.COUPS_MAX:
                el.coup(nom)
                coups += 1
                bilan["coups"] += 1
                scores = el.sonder(s[var])
                ok, top1, v1, top2, v2 = juger(scores, nom)
            if coups and ok:
                bilan["rattrapes"] += 1
            bilan["tests"].append((nom, var, ok, top1, v1, top2, v2, coups))
            if verbeux:
                marque = "✅" if ok else "❌"
                coup_txt = f" +{coups}coup{'s' if coups > 1 else ''}" if coups else ""
                print(f"  {nom:11s} {var} {'+'.join(s[var]):16s} -> "
                      f"{top1:11s} {v1:5.1f} vs {top2:11s} {v2:5.1f} {marque}{coup_txt}")
    for t in TEMOINS:
        scores = el.sonder([t])
        top1, v1 = max(scores.items(), key=lambda kv: (kv[1], kv[0]))
        ok = v1 < CONF.MURMURE
        if ok:
            bilan["premier"] += 1
        bilan["tests"].append((t, "témoin", ok, top1, v1, "-", 0.0, 0))
        if verbeux:
            print(f"  {t:11s} témoin {'':16s} -> silence exigé : max {v1:5.1f} "
                  f"({'✅' if ok else '❌ HALLUCINE !'})")
    return bilan


def run(regime, graver=None, verbeux=True):
    conf = REGIMES[regime]
    info = valider()
    if verbeux:
        print(f"corpus : {info['scenes']} scènes, {info['mots']} mots, "
              f"{info['temoins']} témoins, {info['tests']} tests")
    el = Eleve()
    for nom, s in SCENES.items():  # naissance AVANT l'école (même en nul)
        mots = list(dict.fromkeys(s["q0"] + s["q1"] + s["r"]))
        for w in mots:
            el.naitre(w)
        ns = [noeud(w) for w in mots]
        for i in range(len(ns)):
            for j in range(i + 1, len(ns)):
                el.relier(ns[i], ns[j])
        el.motif("SCENE_" + nom, ns)
        el.motif("R_" + nom, [noeud(w) for w in s["r"]])
    for t in TEMOINS:
        el.naitre(t)
        el.relier(noeud(t), "lointain")
    el.c._sync()
    if verbeux:
        print(f"naissances : {el.naiss_n} neurones, {el.naiss_l} liens")
    el.ecole(conf["rounds"])
    el.journee(conf["fois"])
    morts_n = morts_l = 0
    for _ in range(conf["nuits"]):
        avant_n = len(el.c.itp.tissu.neurones)
        avant_l = len(el.c.itp.tissu.liens)
        el.c.nuit()
        el.tailler()
        morts_n += avant_n - len(el.c.itp.tissu.neurones)
        morts_l += avant_l - len(el.c.itp.tissu.liens)
    if verbeux:
        print(f"école x{conf['rounds']} + jour x{conf['fois']} + "
              f"{conf['nuits']} nuit(s) : {morts_n} neurones morts, {morts_l} liens morts, "
              f"écoutes R5 = {el.c.ecoutes}")
    el.ecole(conf["raccommode"])  # l'école raccommode ce que la vie a effiloché
    if verbeux:
        print(f"raccommodage x{conf['raccommode']}")
        print("--- interrogation (sonde pure, coups sur ratés) ---")
    bilan = interroger(el, avec_coups=True, verbeux=verbeux)
    ok = sum(1 for t in bilan["tests"] if t[2])
    total = len(bilan["tests"])
    if verbeux:
        print(f"PREMIER PASSAGE {regime} : {bilan['premier']}/{total} (avant coups)")
        print(f"BILAN {regime} : {ok}/{total} tiennent "
              f"({bilan['coups']} coups, {bilan['rattrapes']} rattrapés)")
        for sec in ("VIF", "REFRAIN", "SANCTUAIRE"):
            s = el.c.secteurs[sec]
            tops = ", ".join(str(t) for t in s.top(3)) or "—"
            print(f"  {sec:11s} : {len(s.traces)} traces | {tops}")
    taille = el.c.graver(graver) if graver else 0
    if graver and verbeux:
        print(f"gravé : {graver} ({taille} octets — les forces, pas les mots)")
    return el, bilan


def reveil(chemin):
    print(f"réveil depuis {chemin} …")
    el = Eleve.__new__(Eleve)
    el.c = Cerveau.relire(chemin)
    el.noeuds = set(el.c.graph["neurones"])
    el.liens = set(el.c.graph["liens"])
    el.naiss_n = el.naiss_l = 0
    bilan = interroger(el, avec_coups=False, verbeux=True)
    ok = sum(1 for t in bilan["tests"] if t[2])
    print(f"BILAN réveil : {ok}/{len(bilan['tests'])} tiennent (sans coup — la persistance pure)")
    return el, bilan


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime", default="canonique", choices=tuple(REGIMES))
    ap.add_argument("--graver", default=None)
    ap.add_argument("--reveil", default=None)
    args = ap.parse_args(argv)
    if args.reveil:
        reveil(args.reveil)
    else:
        run(args.regime, graver=args.graver)
    return 0


if __name__ == "__main__":
    sys.exit(main())
