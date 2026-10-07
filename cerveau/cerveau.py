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
ENTENDUS_EN = ("americans", "country", "fellow", "ask")

# --- vocabulaire français (miroir de francais.ratum, route A) ---
CONCEPTS_FR = ["monde", "terre", "voix", "devoir", "ensemble", "destin"]
MOTS_FR = {
    "amis": "MAMIS",
    "peuple": "MPEUPLE",
    "pays": "MPAYS",
    "patrie": "MPATRIE",
    "unir": "MUNIR",
    "avenir": "MAVENIR",
}
MOTIFS_FR = {
    "MAMIS": ["word_amis", "monde", "ensemble", "voix"],
    "MPEUPLE": ["word_peuple", "monde", "terre", "ensemble"],
    "MPAYS": ["word_pays", "monde", "terre", "destin"],
    "MPATRIE": ["word_patrie", "terre", "monde", "destin"],
    "MUNIR": ["word_unir", "voix", "devoir", "destin"],
    "MAVENIR": ["word_avenir", "lointain"],
    "TOUT": ["word_amis", "word_peuple", "word_pays", "word_patrie"] + CONCEPTS_FR,
}
LIENS_TISSES_FR = [
    ("word_amis", "monde"), ("word_amis", "ensemble"), ("word_amis", "voix"),
    ("monde", "ensemble"), ("monde", "voix"), ("ensemble", "voix"),
    ("word_peuple", "monde"), ("word_peuple", "terre"), ("word_peuple", "ensemble"),
    ("monde", "terre"), ("monde", "ensemble"), ("terre", "ensemble"),
    ("word_pays", "monde"), ("word_pays", "terre"), ("word_pays", "destin"),
    ("monde", "terre"), ("monde", "destin"), ("terre", "destin"),
    ("word_patrie", "terre"), ("word_patrie", "monde"), ("word_patrie", "destin"),
    ("terre", "monde"), ("terre", "destin"), ("monde", "destin"),
    ("word_unir", "voix"), ("word_unir", "devoir"), ("word_unir", "destin"),
    ("voix", "devoir"), ("voix", "destin"), ("devoir", "destin"),
    ("word_avenir", "lointain"),
]
ENTENDUS_FR = ("amis", "peuple", "pays", "patrie")

# v2, principe des ponts uniques : un concept porté par UN SEUL mot ne reçoit
# qu'un seul écho (moitié perdue dans l'ombre, 44 < 50, à jamais sourd).
# On abaisse son seuil à 40 — pas la règle, le monde : il écoute plus fort.
# FR : voix (amis seul la porte). EN : duty (ask seul la porte).
SEUILS_EN = {"duty": 40}
SEUILS_FR = {"voix": 40}

LANGUES = {
    "EN": {"concepts": CONCEPTS, "mots": MOTS, "motifs": MOTIFS,
           "liens": LIENS_TISSES, "entendus": ENTENDUS_EN, "seuils": SEUILS_EN},
    "FR": {"concepts": CONCEPTS_FR, "mots": MOTS_FR, "motifs": MOTIFS_FR,
           "liens": LIENS_TISSES_FR, "entendus": ENTENDUS_FR, "seuils": SEUILS_FR},
}


def cle(a, b):
    return tuple(sorted((a, b)))


class Cerveau:
    def __init__(self, langue="EN"):
        pack = LANGUES[langue]
        self.langue = langue
        self.mots_connus = pack["mots"]
        self.motifs = pack["motifs"]
        self.entendus = pack["entendus"]
        neurones = set(pack["concepts"])
        for mb in self.motifs.values():
            neurones.update(mb)
        self.graph = {
            "neurones": {n: pack["seuils"].get(n, 50) for n in neurones},
            "liens": {cle(a, b): 10 for a, b in pack["liens"]},
            "types": set(),   # v3 (CISE) : noms des neurones figés
            "geles": set(),   # v3 (CISE) : clés des filaments
        }
        self.chaines = set()  # liens nés des séquences (élaguables)
        self.secteurs = {n: Secteur(n) for n in ("VIF", "REFRAIN", "SANCTUAIRE")}
        self._reconstruire()
        # v2 : enfance longue (30 x TOUT) — l'ombre exige des ponts solides :
        # un lien à 90 porte l'écho à 45, deux ponts à 90 rallument un concept.
        self._exec("répéter 30\nrencontre TOUT\npropager\nrenforcer\nrepos\nfin\n"
                   "répéter 2\noublier\nfin\n")
        self._sync()

    # ----- pont Python <-> Ratum -----
    def _source_tissu(self):
        L = ["tissu Cerveau", ""]
        for n, s in sorted(self.graph["neurones"].items()):
            L.append(f"  neurone {n} seuil {s}" + (" cise" if n in self.graph["types"] else ""))
        L.append("")
        for (a, b), f in sorted(self.graph["liens"].items()):
            L.append(f"  lien {a} {b} force {f}" + (" gelé" if (a, b) in self.graph["geles"] else ""))
        L.append("")
        for nom, mb in self.motifs.items():
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
        """Remonte le tissu vers le graphe persistant (miroir complet :
        forces, seuils adaptés, ET suppressions de `nettoyer`)."""
        t = self.itp.tissu
        self.graph["liens"] = {cle(a, b): f for (a, b), f in t.liens.items()}
        self.graph["types"] = {n for n, v in t.neurones.items() if v.get("type") == "cise"}
        self.graph["geles"] = {cle(a, b) for (a, b) in t.geles if (a, b) in t.liens}
        for n, v in t.neurones.items():
            if n in self.graph["neurones"]:
                self.graph["neurones"][n] = v["seuil"]
        for c in list(self.chaines):
            if c not in self.graph["liens"]:
                self.chaines.discard(c)

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
        connus = [m for m in mots if m in self.mots_connus]
        noeuds = ["word_" + m for m in connus]
        for i in range(len(noeuds) - 1):
            c = cle(noeuds[i], noeuds[i + 1])
            if c not in self.graph["liens"]:
                self.graph["liens"][c] = 10
                self.chaines.add(c)
        self._reconstruire()
        if connus:
            src = "".join(f"rencontre {self.mots_connus[m]}\n" for m in connus)
            src += "propager\nrenforcer\nrepos\n"
            self._exec(src)
        self._sync()
        return trace

    def nuit(self):
        """La nuit : le tissu oublie, la faucheuse élague, les secteurs consolident."""
        self._exec("oublier\n")
        self._exec("nettoyer\n")
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
            f"{m}={self.resonance(self.mots_connus[m])}" for m in self.entendus))
        lignes.append(f"liens : {len(self.graph['liens'])} (chaînes vivantes : {len(self.chaines)})")
        return "\n".join(lignes)
