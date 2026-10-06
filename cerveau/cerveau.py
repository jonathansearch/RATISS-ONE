# -*- coding: utf-8 -*-
"""
LE CERVEAU v1 — crâne Python + pensée Ratum + secteurs de mémoire.
RATISS Labs · MIT.

Architecture :
- Le Python TIENT le graphe (nœuds, liens, forces : la structure persistante).
- Le Ratum le FAIT BATTRE (rencontres, propagation, loi : la dynamique).
- Les secteurs TIENNENT les traces ordonnées (qui suit qui : la mémoire).
- La nuit CONSOLIDE (promotion VIF -> REFRAIN -> SANCTUAIRE + oubli).

Le tissu miroite english.ratum (même vocabulaire anglais). Les liens de
CHAÎNE (mot -> mot suivant) naissent des séquences entendues ; ceux qui
retombent à zéro sont élagués (leçon 4).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ratum import Interprete  # noqa: E402

try:
    from secteurs import Secteur  # exécuté avec cerveau/ dans le chemin
except ImportError:  # importé comme paquet depuis la racine
    from cerveau.secteurs import Secteur

# --- vocabulaire anglais (miroir de english.ratum) ---
CONCEPTS = ["people", "land", "voice", "duty", "together", "future"]
MOTS = {  # mot entendu -> motif
    "americans": "MAMERICANS",
    "country": "MCOUNTRY",
    "fellow": "MFELLOW",
    "ask": "MASK",
    "homeland": "MHOME",
    "comet": "MCOMET",
}
MOTIFS = {
    "MAMERICANS": ["word_americans", "people", "land", "together"],
    "MCOUNTRY": ["word_country", "people", "land", "future"],
    "MFELLOW": ["word_fellow", "people", "together", "voice"],
    "MASK": ["word_ask", "voice", "duty", "future"],
    "MHOME": ["word_homeland", "land", "people", "future"],
    "MCOMET": ["word_comet", "distant"],
    "TOUT": ["word_americans", "word_country", "word_fellow", "word_ask"] + CONCEPTS,
}
LIENS_TISSES = [
    ("word_americans", "people"), ("word_americans", "land"), ("word_americans", "together"),
    ("people", "land"), ("people", "together"), ("land", "together"),
    ("word_country", "people"), ("word_country", "land"), ("word_country", "future"),
    ("people", "future"), ("land", "future"),
    ("word_fellow", "people"), ("word_fellow", "together"), ("word_fellow", "voice"),
    ("people", "voice"), ("together", "voice"),
    ("word_ask", "voice"), ("word_ask", "duty"), ("word_ask", "future"),
    ("voice", "duty"), ("voice", "future"), ("duty", "future"),
    ("word_homeland", "land"), ("word_homeland", "people"), ("word_homeland", "future"),
    ("word_comet", "distant"),
]


def cle(a, b):
    return tuple(sorted((a, b)))


class Cerveau:
    def __init__(self):
        neurones = set(CONCEPTS)
        for mb in MOTIFS.values():
            neurones.update(mb)
        self.graph = {
            "neurones": {n: 50 for n in neurones},
            "liens": {cle(a, b): 10 for a, b in LIENS_TISSES},
        }
        self.chaines = set()  # liens nés des séquences (élaguables)
        self.secteurs = {n: Secteur(n) for n in ("VIF", "REFRAIN", "SANCTUAIRE")}
        self._reconstruire()
        self._exec("répéter 9\nrencontre TOUT\npropager\nrenforcer\nrepos\nfin\n"
                   "répéter 2\noublier\nfin\n")
        self._sync()

    # ----- pont Python <-> Ratum -----
    def _source_tissu(self):
        L = ["tissu Cerveau", ""]
        for n, s in sorted(self.graph["neurones"].items()):
            L.append(f"  neurone {n} seuil {s}")
        L.append("")
        for (a, b), f in sorted(self.graph["liens"].items()):
            L.append(f"  lien {a} {b} force {f}")
        L.append("")
        for nom, mb in MOTIFS.items():
            L.append(f"  motif {nom} : " + " ".join(mb))
        L.append("fin")
        return "\n".join(L) + "\n"

    def _reconstruire(self):
        """Régénère le tissu depuis le graphe (les charges, éphémères, repartent à zéro)."""
        self.itp = Interprete()
        self.itp.bavard = False  # le cerveau garde les verdicts, pas les rouages
        instr = self.itp.decoupage(self._source_tissu().splitlines())
        self.itp.executer(instr, 0, len(instr))

    def _exec(self, source):
        instr = self.itp.decoupage(source.splitlines())
        self.itp.executer(instr, 0, len(instr))

    def _sync(self):
        """Remonte les forces du tissu vers le graphe persistant."""
        for (a, b), f in self.itp.tissu.liens.items():
            self.graph["liens"][cle(a, b)] = f

    def _elaguer(self):
        morts = [c for c in self.chaines if self.graph["liens"].get(c, 0) <= 0]
        for c in morts:
            self.chaines.discard(c)
            self.graph["liens"].pop(c, None)
        return len(morts)

    # ----- vie du cerveau -----
    def entendre_sequence(self, mots):
        """Une mini-séquence entendue : trace au secteur + co-activation au tissu."""
        mots = [m for m in mots if m]
        trace, _ = self.secteurs["VIF"].deposer(mots)
        for nom in ("REFRAIN", "SANCTUAIRE"):  # la trace vit là où elle est déjà
            if tuple(mots) in self.secteurs[nom].traces:
                del self.secteurs["VIF"].traces[tuple(mots)]
                self.secteurs["VIF"].ordre.remove(tuple(mots))
                trace, _ = self.secteurs[nom].deposer(mots)
                break
        connus = [m for m in mots if m in MOTS]
        noeuds = ["word_" + m for m in connus]
        for i in range(len(noeuds) - 1):
            c = cle(noeuds[i], noeuds[i + 1])
            if c not in self.graph["liens"]:
                self.graph["liens"][c] = 10
                self.chaines.add(c)
        self._reconstruire()
        if connus:
            src = "".join(f"rencontre {MOTS[m]}\n" for m in connus)
            src += "propager\nrenforcer\nrepos\n"
            self._exec(src)
        self._sync()
        return trace

    def nuit(self):
        """La nuit : le tissu oublie, les secteurs consolident."""
        self._exec("oublier\n")
        self._sync()
        elagues = self._elaguer()
        r_san = self.secteurs["SANCTUAIRE"].nuit(None)
        r_ref = self.secteurs["REFRAIN"].nuit(self.secteurs["SANCTUAIRE"])
        r_vif = self.secteurs["VIF"].nuit(self.secteurs["REFRAIN"])
        return {"vif": r_vif, "refrain": r_ref, "sanctuaire": r_san, "elagues": elagues}

    def resonance(self, motif):
        return self.itp.resonance(motif)

    def rapport(self):
        lignes = []
        for nom in ("VIF", "REFRAIN", "SANCTUAIRE"):
            s = self.secteurs[nom]
            lignes.append(f"{nom} : {len(s.traces)} traces")
            for t in s.top(3):
                lignes.append(f"  - {t}")
        lignes.append("tissu : " + " ".join(
            f"{m}={self.resonance(MOTS[m])}" for m in ("americans", "country", "fellow", "ask")))
        lignes.append(f"liens : {len(self.graph['liens'])} (chaînes vivantes : {len(self.chaines)})")
        return "\n".join(lignes)
