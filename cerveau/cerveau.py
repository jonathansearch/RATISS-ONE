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
    from secteurs import Secteur, Trace  # exécuté avec cerveau/ dans le chemin
except ImportError:  # importé comme paquet depuis la racine
    from cerveau.secteurs import Secteur, Trace

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

# ⑩ ÉTIQUETTES (gelées 7 oct. 2026 — choix du labo, validé par le chef) :
# le noyau inné, 5 EN + 5 FR : (mot entendu, motif). Au-delà (comet,
# avenir...) : mots d'école — ils grandissent, ils ne sont pas gelés.
MOTIFS_FIXES = (
    ("EN", (("fellow", "MFELLOW"), ("americans", "MAMERICANS"),
            ("ask", "MASK"), ("country", "MCOUNTRY"),
            ("homeland", "MHOME"))),
    ("FR", (("amis", "MAMIS"), ("peuple", "MPEUPLE"),
            ("pays", "MPAYS"), ("patrie", "MPATRIE"),
            ("unir", "MUNIR"))),
)

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
        self.ecoutes = 0  # R5 : séquences venues du dehors (le rêve ne compte pas)
        self.rapide = False  # PUISSANCE : battement fusionné (même maths, sans interprète)
        self._tissu_sale = False  # le graphe a bougé sans l'interprète -> reconstruire avant _exec
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
        if self._tissu_sale:  # le graphe a pris de l'avance : on resynchronise l'interprète
            self._reconstruire()
            self._tissu_sale = False
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
        if mots and not interne:
            self.ecoutes += 1  # R5 : seules les oreilles font tourner le compteur
        if self.rapide and not interne:
            self._entendre_tissu_rapide(mots)
        else:
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

    def _entendre_tissu_rapide(self, mots):
        """PUISSANCE : le même battement que _entendre_tissu, sans interprète.

        Équivalence exacte (prouvée 7 oct., preuves/equivalence-rapide.txt) :
        charges et coups repartent de zéro à chaque séquence (reconstruire),
        aucun `cise` sur ce chemin, `oublier`/`nettoyer` ne lisent jamais les
        coups — le cycle (rencontre/propager/renforcer/repos) est donc une
        fonction pure du graphe, recalculée ici directement. La nuit appelle
        _exec, qui reconstruit si le graphe a pris de l'avance (_tissu_sale).
        """
        L = self.graph["liens"]
        S = self.graph["neurones"]
        G = self.graph["geles"]
        connus = [m for m in mots if m in self.mots_connus]
        noeuds = ["word_" + m for m in connus]
        for i in range(len(noeuds) - 1):  # chaînes mot-à-mot (naissance à 10)
            c = cle(noeuds[i], noeuds[i + 1])
            if c not in L:
                L[c] = 10
                self.chaines.add(c)
        if connus:
            ch = {}
            for m in connus:  # rencontre : chaque motif battu à 100
                for n in self.motifs[self.mots_connus[m]]:
                    ch[n] = 100
            old = dict(ch)  # propager lit les charges D'AVANT (un seul saut, pas de cascade)
            for (a, b), f in L.items():  # l'ombre divise par 2 (//200)
                ca = old.get(a, 0)
                cb = old.get(b, 0)
                if ca:
                    ch[b] = min(100, ch.get(b, 0) + f * ca // 200)
                if cb:
                    ch[a] = min(100, ch.get(a, 0) + f * cb // 200)
            for c, f in L.items():  # renforcer : loi (10, 3) + élasticité
                if c in G:
                    continue
                a, b = c
                if ch.get(a, 0) >= S[a] and ch.get(b, 0) >= S[b]:
                    L[c] = min(100, f + max(1, 10 * (100 - f) // 100))
                else:
                    L[c] = f - 3 if f > 3 else 0
            self._tissu_sale = True

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

    def figer(self, motifs=None):
        """L'ÉCLAIR MANUEL (décision du chef, 7 oct.) : bombarde chaque motif
        (11 rencontres à chaud, vitesse 16 — leçon 13) puis `cise` : les
        neurones qui battent se figent en CISE, les liens entre figés
        deviennent des filaments (gelés : la loi ne les touche plus, les
        nuits non plus). Les forces entraînées ne bougent PAS (ni propager
        ni renforcer sur ce chemin — prouvé par assert). Idempotent :
        re-figer un figé ne fait rien. Retourne le résumé."""
        if motifs is None:
            motifs = list(self.motifs)
        forces_avant = dict(self.graph["liens"])
        src = ""
        for m in motifs:
            src += f"rencontre {m}\n" * 11
            src += f"cise {m}\n"
        self._exec(src)  # reconstruit si sale, bombarde, fait exploser
        self._sync()  # remonte types/gelés + convictions ULTRA-SECTEUR
        assert dict(self.graph["liens"]) == forces_avant, "le figement a bougé les forces !"
        return {"figes": sorted(self.graph["types"]),
                "filaments": len(self.graph["geles"]),
                "forces_intactes": True}

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
        if self._tissu_sale:
            self._reconstruire()
            self._tissu_sale = False
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
        lignes.append(f"écoutes : {self.ecoutes} séquences entendues (R5)")
        lignes.append(f"liens : {len(self.graph['liens'])} (chaînes vivantes : {len(self.chaines)})")
        return "\n".join(lignes)

    # ----- le cerveau fortifié rentre à la maison (leçon 26) -----
    def graver(self, chemin):
        """Photo complète : graphe + secteurs + tampon + compteur.

        Les charges et les coups, éphémères, ne sont PAS sauvés (doctrine :
        seules les forces persistent) — le cerveau relu repart charges à
        zéro, comme après une nuit. `.gz` = compressé, sinon JSON brut.
        Retourne la taille en octets.
        """
        import gzip
        import json
        import time
        photo = {
            "format": "cerveau-fortifie-v1",
            "langue": self.langue,
            "ecoutes": self.ecoutes,
            "reve": self.reve,
            "tampon": [list(m) for m in self.tampon],
            "graph": {
                "neurones": dict(self.graph["neurones"]),
                "liens": [[a, b, f] for (a, b), f in self.graph["liens"].items()],
                "types": sorted(self.graph["types"]),
                "geles": [[a, b] for a, b in self.graph["geles"]],
            },
            "chaines": [[a, b] for a, b in self.chaines],
            "secteurs": {
                nom: [{"mots": list(t.mots), "coups": t.coups, "force": t.force,
                       "redites": t.redites, "grave": t.grave}
                      for t in s.traces.values()]
                for nom, s in self.secteurs.items()},
            "ordres": {nom: [list(m) for m in s.ordre]
                       for nom, s in self.secteurs.items()},
            "meta": {"logiciel": "RATISS-ONE",
                     "date": time.strftime("%Y-%m-%d %H:%M:%S")},
        }
        brut = json.dumps(photo, ensure_ascii=False).encode("utf-8")
        if str(chemin).endswith(".gz"):
            with gzip.open(chemin, "wb") as fh:
                fh.write(brut)
        else:
            with open(chemin, "wb") as fh:
                fh.write(brut)
        return os.path.getsize(chemin)

    @classmethod
    def relire(cls, chemin):
        """Réveille un cerveau depuis sa photo (graver). Reprise exacte :
        le graphe relu a de l'avance sur l'interprète neuf (_tissu_sale)."""
        import gzip
        import json
        ouvrir = gzip.open if str(chemin).endswith(".gz") else open
        with ouvrir(chemin, "rb") as fh:
            photo = json.loads(fh.read().decode("utf-8"))
        assert photo.get("format") == "cerveau-fortifie-v1", "pas une photo de cerveau"
        c = cls(photo.get("langue", "FR"))
        c.ecoutes = photo["ecoutes"]
        c.reve = photo["reve"]
        c.tampon = [list(m) for m in photo["tampon"]]
        c.graph["neurones"] = dict(photo["graph"]["neurones"])
        c.graph["liens"] = {(a, b): f for a, b, f in photo["graph"]["liens"]}
        c.graph["types"] = set(photo["graph"]["types"])
        c.graph["geles"] = {(a, b) for a, b in photo["graph"]["geles"]}
        c.chaines = {(a, b) for a, b in photo["chaines"]}
        for nom, traces in photo["secteurs"].items():
            s = c.secteurs[nom]
            s.traces = {}
            for t in traces:
                tr = Trace(t["mots"], t["force"])
                tr.coups = t["coups"]
                tr.redites = t["redites"]
                tr.grave = t["grave"]
                s.traces[tr.mots] = tr
            s.ordre = [tuple(m) for m in photo["ordres"][nom]]
        c._tissu_sale = True  # le graphe relu devance l'interprète neuf
        return c
