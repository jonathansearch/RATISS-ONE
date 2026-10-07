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


# v5 (MARÉE, phase 4) : le tampon tient 50 écoutes — une grosse journée.
# Au-delà, soupape : le plus ancien entre au VIF (zéro perte, jamais).
TAMPON_CAP = 50


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
        self.tampon = []  # v5 : l'antichambre — le jour écoute, la nuit consolide
        self.reve = True  # v6 : on rêve chaque nuit (désactivable : chaos témoin)
        self.secteurs = {n: Secteur(n) for n in ("VIF", "REFRAIN", "SANCTUAIRE", "ULTRA-SECTEUR")}
        self._cise_lus = 0  # v3 : étincelles déjà lues au journal du tissu
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
        self._cise_lus = 0  # journal neuf : tout relire depuis le début
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
        # v3 (CISE) : le crâne observe — chaque étincelle dépose sa conviction.
        for e in t.journal_cise[self._cise_lus:]:
            self.secteurs["ULTRA-SECTEUR"].deposer(["cise", e["motif"]] + sorted(e["figes"]))
        self._cise_lus = len(t.journal_cise)

    def _elaguer(self):
        morts = [c for c in self.chaines if self.graph["liens"].get(c, 0) <= 0]
        for c in morts:
            self.chaines.discard(c)
            self.graph["liens"].pop(c, None)
        return len(morts)

    # ----- vie du cerveau -----
    def entendre_sequence(self, mots, interne=False):
        """Une mini-séquence entendue : co-activation immédiate au tissu
        (on entend tout de suite) + trace au TAMPON (on consolide la nuit).
        v5 : `interne=True` (voix intérieure, rétroaction) dépose directement
        au secteur — elle ne passe pas par les oreilles. Retourne la trace
        (interne) ou None (tamponnée : elle n'existe qu'à la nuit)."""
        mots = [m for m in mots if m]
        self._entendre_tissu(mots)
        if interne:
            return self._deposer_trace(mots)
        if len(self.tampon) >= TAMPON_CAP:
            self._deposer_trace(self.tampon.pop(0))  # soupape : zéro perte
        self.tampon.append(mots)
        return None

    def _deposer_trace(self, mots):
        """Dépose une séquence au secteur où elle vit déjà (VIF par défaut)."""
        trace, _ = self.secteurs["VIF"].deposer(mots)
        for nom in ("REFRAIN", "SANCTUAIRE"):  # la trace vit là où elle est déjà
            if tuple(mots) in self.secteurs[nom].traces:
                del self.secteurs["VIF"].traces[tuple(mots)]
                self.secteurs["VIF"].ordre.remove(tuple(mots))
                trace, _ = self.secteurs[nom].deposer(mots)
                break
        return trace

    def _entendre_tissu(self, mots):
        """Co-activation immédiate : chaînes mot-à-mot + battement Ratum."""
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

    def redire(self):
        """RÉTROACTION (v4, phase 3) : la boucle se ferme — le crâne formule
        sa trace dominante (tokenizer, règle unique) puis la RÉ-ENTEND :
        la bouche parle, l'oreille écoute, le répété se grave.
        Retourne (phrase, trace) ou (None, None) si le sanctuaire est vide.
        Import paresseux : la bouche dépend du crâne au chargement, pas l'inverse."""
        tops = self.secteurs["SANCTUAIRE"].top(1)
        if not tops:
            return None, None
        from bouche.regles import formuler, lire_etat
        phrase = formuler(lire_etat(self))
        trace = self.entendre_sequence(list(tops[0].mots), interne=True)
        trace.redire()
        return phrase, trace

    def rever(self):
        """LE RÊVE (v6, phase 5) : l'hippocampe rejoue ce que le tissu a compris.
        Chaque trace VIF/REFRAIN riche (≥ 2 mots connus) est ravivée sur place
        (+1 coup, +pas) — on ne rêve que de ce qu'on comprend. Le rêve ravive,
        la nuit promeut : ni promotion ni gonflement du sanctuaire ici.
        Retourne le nombre de ravives (la sélectivité du rêve)."""
        n = 0
        for nom in ("VIF", "REFRAIN"):
            for mots in list(self.secteurs[nom].traces):
                if sum(1 for m in mots if m in self.mots_connus) >= 2:
                    self.secteurs[nom].deposer(list(mots))
                    n += 1
        return n

    def nuit(self):
        """La nuit : le tampon se vide (dans l'ordre), on rêve de ce qu'on a
        compris, puis le tissu oublie, la faucheuse élague, les secteurs consolident."""
        videes = 0
        while self.tampon:  # v5 : le soir, l'antichambre se vide au VIF
            self._deposer_trace(self.tampon.pop(0))
            videes += 1
        reves = self.rever() if self.reve else 0  # v6 : le rêve avant l'oubli
        self._exec("oublier\n")
        self._exec("nettoyer\n")
        self._sync()
        elagues = self._elaguer()
        r_san = self.secteurs["SANCTUAIRE"].nuit(None)
        r_ref = self.secteurs["REFRAIN"].nuit(self.secteurs["SANCTUAIRE"])
        r_vif = self.secteurs["VIF"].nuit(self.secteurs["REFRAIN"])
        r_ult = self.secteurs["ULTRA-SECTEUR"].nuit(None)
        return {"vif": r_vif, "refrain": r_ref, "sanctuaire": r_san, "ultra": r_ult,
                "elagues": elagues, "videes": videes, "reves": reves}

    def resonance(self, motif):
        return self.itp.resonance(motif)

    def rapport(self):
        lignes = []
        for nom in ("VIF", "REFRAIN", "SANCTUAIRE", "ULTRA-SECTEUR"):
            s = self.secteurs[nom]
            lignes.append(f"{nom} : {len(s.traces)} traces")
            for t in s.top(3):
                lignes.append(f"  - {t}")
        lignes.append(f"tampon : {len(self.tampon)} en attente"
                        + (" (PRESSION : la soupape coule)" if self.tampon and len(self.tampon) >= TAMPON_CAP else ""))
        lignes.append("tissu : " + " ".join(
            f"{m}={self.resonance(self.mots_connus[m])}" for m in self.entendus))
        lignes.append(f"liens : {len(self.graph['liens'])} (chaînes vivantes : {len(self.chaines)})")
        return "\n".join(lignes)
