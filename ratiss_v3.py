#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ratiss_v3.py — la bouche dirigée de RATISS.

RATISS Labs · Jonathan Evina · Yaoundé · MIT.

Le tissu scellé (.ratiss) répond à « qui fréquente qui ».
Cette bouche répond à « quel mot a le droit de suivre ».

Elle ne touche jamais au gel du .ratiss. Elle s'enregistre à part,
dans un fichier RATISS_BOUCHE_V3 (.json lisible, ou .bouche gzippé).

    python3 ratiss_v3.py --demo
    python3 ratiss_v3.py cerveau/RatissOne.ratiss --audit
    python3 ratiss_v3.py cerveau/RatissOne.ratiss --eduquer corpus/prince_jouet.txt --tours 3 --sauver bouche.json
    python3 ratiss_v3.py cerveau/RatissOne.ratiss --charger bouche.json --evaluer corpus/tenu_a_lecart.txt
    python3 ratiss_v3.py cerveau/RatissOne.ratiss --charger bouche.json --lam 0.75 --memoire 8 "il etait une fois"
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import random
import re
import sys
import time
from collections import defaultdict

FORMAT_BOUCHE = "RATISS_BOUCHE_V3"
FORMAT_TISSU = "RATISS_SOUVERAIN_V2"

# Lumière causale : le dernier mot éclaire à 1, le précédent à 1/2, puis 1/4…
LUMIERE = 0.5
# Part du trigramme quand la paire (mot-2, mot-1) a été vue.
# Le reste reste au bigramme : un trigramme jamais vu ne doit pas faire taire la bouche.
# Mesuré, décharge allumée, texte tenu à l'écart où « noire » a deux suites :
# top-1 bigramme 33 %, lumière 30 %, trigramme avec repli 39 %. Le top-5 ne bouge pas.
POIDS_TRIGRAMME = 0.65

_ACCENTS = str.maketrans(
    {
        "à": "a", "â": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "ï": "i", "î": "i",
        "ô": "o", "ö": "o",
        "ù": "u", "û": "u", "ü": "u",
        "ç": "c", "œ": "oe", "æ": "ae",
        "’": "'",
    }
)

# Sonde fixe : 16 vrais mots suivants, pour l'audit du tissu scellé.
# Ce ne sont pas des phrases du sanctuaire. Ce sont des suites françaises
# ordinaires. Le tissu, lui, n'a pas appris l'ordre : seulement la cooccurrence,
# et ses liens sont triés par ordre alphabétique.
SONDE_16 = [
    ("il", "etait"),
    ("etait", "une"),
    ("une", "fois"),
    ("fois", "une"),
    ("une", "petite"),
    ("petite", "fille"),
    ("fille", "qui"),
    ("qui", "aimait"),
    ("aimait", "la"),
    ("la", "mer"),
    ("mer", "noire"),
    ("noire", "et"),
    ("et", "le"),
    ("le", "roi"),
    ("roi", "dit"),
    ("dit", "au"),
]

CORPUS_DEMO = """\
le petit prince aimait sa rose
le petit prince habitait une petite planete
il y avait un jardin
dans le jardin le petit prince regardait les etoiles
la rose du prince etait unique
un jardin le petit prince aimait sa rose
sa rose vivait sous un globe
le prince quittait sa planete
""".strip()

TENU_A_LECART_DEMO = """\
le petit prince aimait les etoiles
un jardin gardait la rose
""".strip()


def norm(mot: str) -> str:
    """Casse, accents. Le mot reste un mot : il ne devient pas un flottant."""
    mot = mot.lower().translate(_ACCENTS)
    mot = mot.replace("œ", "oe").replace("æ", "ae")
    return mot.strip()


def tokeniser(texte: str) -> list[str]:
    brut = re.findall(r"[0-9A-Za-zàâäéèêëïîôùûüçœæ'_-]+", texte.lower())
    mots = []
    for b in brut:
        m = norm(b)
        if m and m not in {"-", "_"}:
            mots.append(m)
    return mots


def phrases_de(texte: str) -> list[list[str]]:
    gardées = []
    for ligne in texte.splitlines():
        if ligne.strip().startswith("#"):
            continue
        gardées.append(ligne)
    morceaux = re.split(r"[\n\r.!?;]+", "\n".join(gardées))
    sortie = []
    for m in morceaux:
        toks = tokeniser(m)
        if len(toks) >= 2:
            sortie.append(toks)
    return sortie


def softmax(poids: list[float], temperature: float) -> list[float]:
    t = max(float(temperature), 1e-6)
    if not poids:
        return []
    m = max(poids)
    exps = [math.exp((p - m) / t) for p in poids]
    z = sum(exps) or 1.0
    return [e / z for e in exps]


def normaliser(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    m = max(scores.values())
    if m <= 0:
        return {}
    return {k: v / m for k, v in scores.items() if v > 0}


def top(scores: dict[str, float], k: int) -> list[tuple[str, float]]:
    return sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def melanger(a: dict[str, float], b: dict[str, float], lam: float) -> dict[str, float]:
    """λ = 1 : seulement l'ordre. λ = 0 : seulement le thème."""
    lam = min(1.0, max(0.0, float(lam)))
    na, nb = normaliser(a), normaliser(b)
    cles = set(na) | set(nb)
    out = {}
    for c in cles:
        s = lam * na.get(c, 0.0) + (1.0 - lam) * nb.get(c, 0.0)
        if s > 0:
            out[c] = s
    return out


class TissuScelle:
    """Lecteur du .ratiss. Lecture seule. Le gel n'est pas une bouche."""

    def __init__(self, chemin: str):
        self.chemin = chemin
        t0 = time.time()
        data = self._lire(chemin)
        if data.get("FORMAT") != FORMAT_TISSU:
            raise ValueError(
                f"format inattendu : {data.get('FORMAT')!r} (attendu {FORMAT_TISSU})"
            )
        self.data = data
        self.meta = data.get("META", {})
        self.sanctuaire = data.get("SANCTUAIRE", {})
        self.memoire = dict(data.get("MEMOIRE_EPISODIQUE", {}))
        rni = data.get("RNI_MATRICE", {})
        self.neurones = rni.get("neurones", {})
        self.liens = rni.get("liens", [])
        self.geles = rni.get("geles", [])
        self.adj: dict[str, list[tuple[str, int]]] = defaultdict(list)
        self.paires_triees = 0
        self.paires_inversees = 0
        for lien in self.liens:
            a, b, force = lien[0], lien[1], int(lien[2])
            if isinstance(a, str) and isinstance(b, str) and a > b:
                self.paires_inversees += 1
            else:
                self.paires_triees += 1
            self.adj[a].append((b, force))
            if a != b:
                self.adj[b].append((a, force))
        # Différentiel de session. Une case, pas une reconstruction du gel.
        self._delta: dict[str, dict[str, float | None]] = {}
        self.dt = time.time() - t0

    @staticmethod
    def _lire(chemin: str) -> dict:
        try:
            with gzip.open(chemin, "rt", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            with open(chemin, "r", encoding="utf-8") as f:
                return json.load(f)

    def cle(self, mot: str) -> str | None:
        m = norm(mot)
        if m in self.neurones:
            return m
        pref = "word_" + m
        if pref in self.neurones:
            return pref
        return None

    @staticmethod
    def afficher(cle: str) -> str:
        return cle[5:] if cle.startswith("word_") else cle

    def voisins(self, mot: str, k: int = 8) -> list[tuple[str, int]]:
        cle = self.cle(mot)
        if not cle:
            return []
        brut = self.liens_sortants(cle)
        # Force d'abord, puis l'alphabet : c'est exactement ce que le tri du
        # lien produit quand des centaines de forces valent 100.
        rang = sorted(brut, key=lambda kv: (-kv[1], kv[0]))
        vus = set()
        out = []
        for nom, force in rang:
            if nom in vus or nom == cle:
                continue
            vus.add(nom)
            out.append((self.afficher(nom), force))
            if len(out) >= k:
                break
        return out

    def _resoudre_cle(self, mot: str) -> str:
        m = norm(mot)
        trouvee = self.cle(m)
        return trouvee if trouvee is not None else m

    def editer_synapse(self, source: str, cible: str, nouveau_poids: float) -> dict:
        """Pose un poids dans l'overlay. N'itère pas les 428 471 liens."""
        poids = float(nouveau_poids)
        if poids < 0:
            raise ValueError("poids négatif : appeler supprimer_synapse")
        a = self._resoudre_cle(source)
        b = self._resoudre_cle(cible)
        slot = self._delta.setdefault(a, {})
        if poids == 0.0:
            slot[b] = None
        else:
            slot[b] = poids
        return {
            "couche": "overlay",
            "source": a,
            "cible": b,
            "poids": None if poids == 0.0 else poids,
        }

    def supprimer_synapse(self, source: str, cible: str) -> dict:
        """Masque un arc. La liste gelée reste en mémoire, elle n'est plus lue."""
        a = self._resoudre_cle(source)
        b = self._resoudre_cle(cible)
        self._delta.setdefault(a, {})[b] = None
        return {"couche": "overlay", "source": a, "cible": b, "poids": None}

    def exporter_delta(self) -> dict:
        """Le gel reste dans le .ratiss. Le delta, s'il doit vivre, s'écrit à côté."""
        return {
            a: {b: (None if p is None else float(p)) for b, p in dest.items()}
            for a, dest in self._delta.items()
        }

    def appliquer_delta(self, delta: dict) -> int:
        n = 0
        for a, dest in delta.items():
            slot = self._delta.setdefault(str(a), {})
            for b, poids in dest.items():
                slot[str(b)] = None if poids is None else float(poids)
                n += 1
        return n

    def liens_sortants(self, cle: str) -> list[tuple[str, float]]:
        """Adjacence locale : le gel, puis le delta de cette source seulement."""
        fusion: dict[str, float] = {}
        for nom, force in self.adj.get(cle, []):
            fusion[nom] = float(force)
        for nom, force in self._delta.get(cle, {}).items():
            if force is None:
                fusion.pop(nom, None)
            else:
                fusion[nom] = float(force)
        return list(fusion.items())

    def raisonner_par_resonance(
        self,
        concepts_sources: list,
        seuil_energie: float = 0.1,
        max_sauts: int = 3,
        **kwargs,
    ) -> dict:
        from piliers.resonance import raisonner_par_resonance as _resonner

        def _voisins(nom: str):
            cle = self.cle(nom) or nom
            return [
                (self.afficher(cible), float(poids))
                for cible, poids in self.liens_sortants(cle)
                if cible != cle and poids > 0
            ]

        def _degre(nom: str):
            cle = self.cle(nom) or nom
            return len(self.liens_sortants(cle))

        sources = []
        for s in concepts_sources:
            cle = self.cle(s)
            sources.append(self.afficher(cle) if cle else norm(s))
        return _resonner(
            sources,
            seuil_energie=seuil_energie,
            max_sauts=max_sauts,
            voisins=_voisins,
            degre=_degre,
            **kwargs,
        )

    def scores_theme(self, historique: list[str], memoire: int, normaliser_degre: bool = True) -> dict[str, float]:
        """Résonance du tissu : qui fréquente les mots déjà dits. Pas un ordre.
        
        Si normaliser_degre=True (défaut), divise chaque apport par ln(max(e, degre(cible)))
        pour étouffer l'accumulation artificielle dans les hubs syntaxiques (de, le, a...).
        """
        import math
        scores: dict[str, float] = defaultdict(float)
        fenetre = historique[-max(1, memoire):]
        for dist, mot in enumerate(reversed(fenetre)):
            lum = LUMIERE ** dist
            cle = self.cle(mot)
            if not cle:
                continue
            sortants = self.liens_sortants(cle)
            for nom, force in sortants:
                if nom == cle:
                    continue
                cible = self.afficher(nom)
                if normaliser_degre:
                    deg = len(self.liens_sortants(nom))
                    denom = math.log(max(math.e, float(deg)))
                    scores[cible] += lum * (float(force) / denom)
                else:
                    scores[cible] += lum * float(force)
        return dict(scores)

    def sujet_sanctuaire(self, texte: str, tokens: list[str]) -> str | None:
        bas = norm(texte)
        ensemble = set(tokens)
        # Les clés à deux mots (« trou noir ») d'abord.
        cles = sorted(self.sanctuaire.keys(), key=lambda s: -len(s))
        for cle in cles:
            pieces = tokeniser(cle)
            if not pieces:
                continue
            if all(p in ensemble for p in pieces) or norm(cle) in bas:
                return cle
        return None


class Bouche:
    """Arcs dirigés + thème de fenêtre + chaînes gelées. Jamais le .ratiss."""

    def __init__(self):
        self.registres: dict[str, dict[str, dict[str, float]]] = {}
        # Ordre à deux mots de contexte. Pas une phrase. Le sanctuaire n'entre pas ici.
        self.trigrammes: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
        self.theme: dict[str, dict[str, float]] = {}
        self.chaines: list[dict] = []
        self.episodique: list[dict] = []
        self.lam = 0.75
        self.memoire = 8
        self.temperature = 0.7
        self.contraste = True
        self.registre = "ordre"
        self.meta: dict = {
            "phrases": 0,
            "tokens": 0,
            "tours": 0,
            "decharges": 0,
        }

    # ---------- persistance ----------

    def vers_dict(self) -> dict:
        return {
            "FORMAT": FORMAT_BOUCHE,
            "lam": self.lam,
            "memoire": self.memoire,
            "temperature": self.temperature,
            "contraste": self.contraste,
            "registre_courant": self.registre,
            "registres": self.registres,
            "trigrammes": self.trigrammes,
            "theme": self.theme,
            "chaines": self.chaines,
            "episodique": self.episodique,
            "meta": self.meta,
        }

    def sauver(self, chemin: str) -> None:
        payload = json.dumps(self.vers_dict(), ensure_ascii=False)
        if chemin.endswith(".bouche") or chemin.endswith(".gz"):
            with gzip.open(chemin, "wt", encoding="utf-8") as f:
                f.write(payload)
        else:
            with open(chemin, "w", encoding="utf-8") as f:
                json.dump(self.vers_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def charger(cls, chemin: str) -> "Bouche":
        try:
            with gzip.open(chemin, "rt", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            with open(chemin, "r", encoding="utf-8") as f:
                data = json.load(f)
        if data.get("FORMAT") != FORMAT_BOUCHE:
            raise ValueError(f"pas une bouche RATISS : {data.get('FORMAT')!r}")
        b = cls()
        b.lam = float(data.get("lam", 0.75))
        b.memoire = int(data.get("memoire", 8))
        b.temperature = float(data.get("temperature", 0.7))
        b.contraste = bool(data.get("contraste", True))
        b.registre = data.get("registre_courant", "ordre")
        b.registres = data.get("registres", {})
        b.trigrammes = data.get("trigrammes", {})
        b.theme = data.get("theme", {})
        b.chaines = data.get("chaines", [])
        b.episodique = data.get("episodique", [])
        b.meta = data.get("meta", b.meta)
        return b

    def vide(self) -> bool:
        return not any(self.registres.values()) and not self.chaines

    def _arcs(self, registre: str | None = None) -> dict[str, dict[str, float]]:
        nom = registre or self.registre
        return self.registres.setdefault(nom, {})

    def _tris(self, registre: str | None = None) -> dict[str, dict[str, dict[str, float]]]:
        nom = registre or self.registre
        return self.trigrammes.setdefault(nom, {})

    def n_arcs(self) -> int:
        return sum(len(dst) for reg in self.registres.values() for dst in reg.values())

    def n_trigrammes(self) -> int:
        return sum(
            len(suite)
            for reg in self.trigrammes.values()
            for milieu in reg.values()
            for suite in milieu.values()
        )

    def editer_synapse(self, source: str, cible: str, nouveau_poids: float, registre: str | None = None) -> dict:
        from piliers.neurochirurgie import editer_bouche

        return editer_bouche(self, source, cible, nouveau_poids, registre)

    def supprimer_synapse(self, source: str, cible: str, registre: str | None = None) -> dict:
        from piliers.neurochirurgie import supprimer_bouche

        return supprimer_bouche(self, source, cible, registre)

    def apprendre_phrase_live(self, phrase, registre: str = "episodique") -> dict:
        from piliers.episodique import apprendre_phrase_live as _apprendre

        return _apprendre(self, phrase, registre)

    def expliquer_generation(self, token_choisi, contexte, tissu: TissuScelle | None = None, lam: float | None = None, memoire: int | None = None) -> dict:
        from piliers.audit import expliquer_generation as _expliquer

        return _expliquer(self, token_choisi, contexte, tissu=tissu, lam=lam, memoire=memoire)

    def raisonner_par_resonance(
        self,
        concepts_sources: list,
        seuil_energie: float = 0.1,
        max_sauts: int = 3,
        **kwargs,
    ) -> dict:
        from piliers.resonance import raisonner_par_resonance as _resonner

        return _resonner(
            concepts_sources,
            seuil_energie=seuil_energie,
            max_sauts=max_sauts,
            graphe=self.theme,
            **kwargs,
        )

    # ---------- apprentissage ----------

    def eduquer(
        self,
        texte: str,
        tours: int = 1,
        registre: str | None = None,
        contraste: bool | None = None,
        fenetre_theme: int = 3,
    ) -> dict:
        if registre:
            self.registre = registre
        if contraste is not None:
            self.contraste = contraste
        phrases = phrases_de(texte)
        if not phrases:
            raise ValueError("le corpus ne contient aucune phrase d'au moins 2 mots")
        decharges = 0
        tokens = 0
        for _ in range(max(1, tours)):
            for ph in phrases:
                decharges += self._apprendre_phrase(ph, fenetre_theme)
                tokens += len(ph)
        self.meta["phrases"] = self.meta.get("phrases", 0) + len(phrases) * max(1, tours)
        self.meta["tokens"] = self.meta.get("tokens", 0) + tokens
        self.meta["tours"] = self.meta.get("tours", 0) + max(1, tours)
        self.meta["decharges"] = self.meta.get("decharges", 0) + decharges
        self.meta["registre"] = self.registre
        self.meta["sha_corpus"] = hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]
        return {
            "phrases": len(phrases),
            "tokens": tokens // max(1, tours),
            "tours": max(1, tours),
            "arcs": self.n_arcs(),
            "decharges": decharges,
        }

    def _apprendre_phrase(self, ph: list[str], fenetre_theme: int) -> int:
        arcs = self._arcs()
        tris = self._tris()
        decharges = 0
        for i, mot in enumerate(ph):
            # Thème : fenêtre, les deux sens, « ces mots se sont vus ».
            for j in range(i + 1, min(len(ph), i + fenetre_theme)):
                autre = ph[j]
                if autre == mot:
                    continue
                self._ajouter_theme(mot, autre, 1.0)
                self._ajouter_theme(autre, mot, 1.0)
            if i == 0:
                continue
            src = ph[i - 1]
            # Prédiction AVANT le coup, pour savoir qui était le coupable.
            scores = dict(arcs.get(src, {}))
            table = arcs.setdefault(src, {})
            table[mot] = table.get(mot, 0.0) + 1.0
            if i >= 2:
                # La paire décide. Compte seul : la décharge reste sur le bigramme.
                gauche = ph[i - 2]
                milieu = tris.setdefault(gauche, {}).setdefault(src, {})
                milieu[mot] = milieu.get(mot, 0.0) + 1.0
            if self.contraste and scores:
                meilleur = max(scores.items(), key=lambda kv: (kv[1], kv[0]))[0]
                if meilleur != mot:
                    decharges += 1
                    table[mot] = table.get(mot, 0.0) + 1.0
                    seuil = scores.get(mot, 0.0)
                    for cand, sc in scores.items():
                        if cand == mot:
                            continue
                        if sc >= seuil and sc > 0:
                            table[cand] = max(0.0, table.get(cand, 0.0) - 0.35)
        return decharges

    def _ajouter_theme(self, a: str, b: str, pas: float) -> None:
        self.theme.setdefault(a, {})
        self.theme[a][b] = self.theme[a].get(b, 0.0) + pas

    def graver_chaine(self, enonce: str, registre: str = "fait") -> dict:
        """Un fait devient un chemin gelé, pas un paragraphe relu."""
        mots = tokeniser(enonce)
        if len(mots) < 2:
            raise ValueError("un fait a besoin d'au moins deux mots")
        arcs = self._arcs(registre)
        tris = self._tris(registre)
        for i, (a, b) in enumerate(zip(mots, mots[1:])):
            arcs.setdefault(a, {})
            # Gel : une force haute, que l'éducation libre ne doit pas manger.
            arcs[a][b] = max(arcs[a].get(b, 0.0), 100.0)
            if i >= 1:
                gauche = mots[i - 1]
                milieu = tris.setdefault(gauche, {}).setdefault(a, {})
                milieu[b] = max(milieu.get(b, 0.0), 100.0)
        cles = []
        for m in mots:
            if len(m) > 3 and m not in cles and m not in {
                "dans", "avec", "pour", "cette", "comme", "plus", "tout", "tous",
                "elle", "elles", "leur", "leurs", "dont", "chez", "vers", "sous",
                "entre", "apres", "avant", "ainsi", "alors", "aussi",
            }:
                cles.append(m)
        if not cles:
            cles = [mots[0]]
        h = hashlib.sha256(enonce.encode("utf-8")).hexdigest()[:12]
        chaine = {
            "mots": mots,
            "gele": True,
            "cles": cles,
            "enonce": enonce.strip(),
            "sha256": h,
            "registre": registre,
        }
        self.chaines.append(chaine)
        self.registre = registre
        return chaine

    def chaine_pour(self, tokens: list[str]) -> dict | None:
        ensemble = set(tokens)
        meilleure = None
        score = 0
        for ch in self.chaines:
            if not ch.get("gele", True):
                continue
            n = sum(1 for c in ch.get("cles", []) if c in ensemble)
            if n > score:
                score = n
                meilleure = ch
        return meilleure if score > 0 else None

    # ---------- scores ----------

    def scores_ordre(self, historique: list[str], memoire: int | None = None, registre: str | None = None) -> dict[str, float]:
        mem = self.memoire if memoire is None else memoire
        mem = max(1, int(mem))
        scores: dict[str, float] = defaultdict(float)
        if registre:
            tables = [self.registres.get(registre, {})]
        else:
            tables = list(self.registres.values()) or [{}]
        fenetre = historique[-mem:]
        for dist, mot in enumerate(reversed(fenetre)):
            lum = LUMIERE ** dist
            for table in tables:
                for cand, force in table.get(mot, {}).items():
                    if force > 0:
                        scores[cand] += lum * float(force)
        return dict(scores)

    def _tables_trigrammes(self, registre: str | None = None) -> list[dict]:
        if registre:
            return [self.trigrammes.get(registre, {})]
        return list(self.trigrammes.values()) or [{}]

    def scores_trigramme(
        self,
        historique: list[str],
        memoire: int | None = None,
        registre: str | None = None,
    ) -> dict[str, float]:
        """Paire si on l'a vue, sinon le bigramme du dernier mot.

        On ne parcourt pas les 95 660 neurones. Les candidats sont les
        successeurs déjà écrits sous cette paire, ou à défaut sous ce mot.
        """
        del memoire  # le repli est le dernier mot : la lumière à 8 a perdu le top-1
        base = self.scores_ordre(historique, memoire=1, registre=registre)
        if len(historique) < 2:
            return base
        gauche, src = historique[-2], historique[-1]
        brut: dict[str, float] = defaultdict(float)
        for table in self._tables_trigrammes(registre):
            for cand, force in table.get(gauche, {}).get(src, {}).items():
                if force > 0:
                    brut[cand] += float(force)
        if not brut:
            return base
        tg = normaliser(brut)
        nb = normaliser(base)
        out = {}
        for c in set(tg) | set(nb):
            s = POIDS_TRIGRAMME * tg.get(c, 0.0) + (1.0 - POIDS_TRIGRAMME) * nb.get(c, 0.0)
            if s > 0:
                out[c] = s
        return out

    def scores_theme_bouche(self, historique: list[str], memoire: int | None = None) -> dict[str, float]:
        mem = self.memoire if memoire is None else memoire
        scores: dict[str, float] = defaultdict(float)
        fenetre = historique[-max(1, int(mem)):]
        for dist, mot in enumerate(reversed(fenetre)):
            lum = LUMIERE ** dist
            for cand, force in self.theme.get(mot, {}).items():
                if force > 0:
                    scores[cand] += lum * float(force)
        return dict(scores)

    def scores(
        self,
        historique: list[str],
        tissu: TissuScelle | None = None,
        lam: float | None = None,
        memoire: int | None = None,
    ) -> dict[str, float]:
        lam = self.lam if lam is None else lam
        # Ordre = trigramme avec repli. Thème = l'autre loi. Deux secteurs.
        ordre = self.scores_trigramme(historique, memoire=memoire)
        theme = self.scores_theme_bouche(historique, memoire=memoire)
        if tissu is not None:
            theme_tissu = tissu.scores_theme(historique, memoire or self.memoire)
            theme = melanger(theme, theme_tissu, 0.5 if theme else 0.0)
        return melanger(ordre, theme, lam)

    # ---------- mesure ----------

    def evaluer(
        self,
        texte: str,
        tissu: TissuScelle | None = None,
        lam: float | None = None,
        memoire: int | None = None,
        mode: str = "mixte",
    ) -> dict:
        """top5 : sur les positions, le vrai mot suivant est-il dans les 5 ?"""
        phrases = phrases_de(texte)
        hits = 0
        total = 0
        details = []
        for ph in phrases:
            for i in range(1, len(ph)):
                hist = ph[:i]
                vrai = ph[i]
                if mode == "ordre":
                    scores = self.scores_ordre(hist, memoire=1)
                elif mode == "lumiere":
                    scores = self.scores_ordre(hist, memoire=memoire or 8)
                elif mode == "trigramme":
                    scores = self.scores_trigramme(hist)
                elif mode == "theme":
                    scores = self.scores_theme_bouche(hist, memoire=1)
                elif mode == "tissu" and tissu is not None:
                    scores = tissu.scores_theme(hist, 1)
                else:
                    scores = self.scores(hist, tissu=tissu, lam=lam, memoire=memoire)
                rang = [m for m, _ in top(scores, 5)]
                ok = vrai in rang
                hits += int(ok)
                total += 1
                if len(details) < 12:
                    details.append({"hist": " ".join(hist[-4:]), "vrai": vrai, "top": rang, "ok": ok})
        return {
            "top5": (hits / total) if total else 0.0,
            "hits": hits,
            "total": total,
            "details": details,
            "mode": mode,
        }


def audit_tissu(tissu: TissuScelle) -> dict:
    hits = 0
    lignes = []
    for src, vrai in SONDE_16:
        voisins = tissu.voisins(src, k=5)
        noms = [n for n, _ in voisins]
        ok = vrai in noms
        hits += int(ok)
        lignes.append((src, vrai, noms, ok))
    total_paires = tissu.paires_triees + tissu.paires_inversees
    return {
        "neurones": len(tissu.neurones),
        "liens": len(tissu.liens),
        "geles": len(tissu.geles),
        "tries": tissu.paires_triees,
        "inverses": tissu.paires_inversees,
        "part_triee": (tissu.paires_triees / total_paires) if total_paires else 0.0,
        "top5": hits / len(SONDE_16),
        "hits": hits,
        "lignes": lignes,
        "dt": tissu.dt,
        "sanctuaire": list(tissu.sanctuaire.keys()),
        "meta": tissu.meta,
    }


def marcher_fige(mots: list[str], ancre: str | None = None) -> list[str]:
    """Secteur figé : une suite ordonnée, pas un sac de bigrammes.

    « la » revient dans « la lune orbite autour de la terre ».
    Un bigramme gelé boucle (la → lune, puis de nouveau la → lune).
    L'ancre choisit où l'on monte sur le chemin, l'indice fait le reste.
    Ce chemin n'est pas recopié dans les synapses plastiques.
    """
    if not mots:
        return []
    if ancre and ancre in mots:
        return list(mots[mots.index(ancre):])
    return list(mots)


def _ancre(mots: list[str], cles: list[str], tokens: list[str]) -> str | None:
    ensemble = set(tokens)
    for c in cles:
        if c in ensemble and c in mots:
            return c
    for t in tokens:
        if t in mots and t not in {"dans", "avec", "pour", "cette", "comme", "plus"}:
            return t
    return None


def _reponse_chemin(mots: list[str], surface: str, ancre: str | None) -> str:
    marche = marcher_fige(mots, ancre=ancre)
    if len(marche) < 2:
        return surface
    if marche == list(mots) and surface.strip():
        texte = surface.strip()
        return texte[0].upper() + texte[1:] if texte[0].islower() else texte
    return " ".join(marche)


def parler(
    bouche: Bouche,
    prompt: str,
    tissu: TissuScelle | None = None,
    n: int = 18,
    lam: float | None = None,
    memoire: int | None = None,
    temperature: float | None = None,
    graine: int = 0,
    glouton: bool = False,
) -> str:
    """Pioche le mot suivant. Ne prend pas toujours le plus fort : sinon ça boucle."""
    rng = random.Random(graine)
    hist = tokeniser(prompt)
    if not hist:
        # Départ : le mot qui a le plus d'arcs sortants.
        table = bouche._arcs()
        if not table:
            return ""
        hist = [max(table, key=lambda m: sum(table[m].values()))]
    temp = bouche.temperature if temperature is None else temperature
    if glouton:
        temp = 1e-6
    produits = []
    vu_recent = []
    bigrams_vus = set()
    for _ in range(n):
        scores = bouche.scores(hist, tissu=tissu, lam=lam, memoire=memoire)
        # On évite de recracher tout de suite le mot qu'on vient de dire.
        for vieux in vu_recent[-2:]:
            if vieux in scores and len(scores) > 1:
                scores[vieux] *= 0.15
        rang = [(m, s) for m, s in scores.items() if s > 0 and m != hist[-1]]
        if not rang:
            break
        mots = [m for m, _ in rang]
        poids = [s for _, s in rang]
        probs = softmax(poids, temp)
        seuil = rng.random()
        acc = 0.0
        choix = mots[-1]
        for m, p in zip(mots, probs):
            acc += p
            if seuil <= acc:
                choix = m
                break
        paire = (hist[-1], choix)
        if paire in bigrams_vus:
            break
        bigrams_vus.add(paire)
        produits.append(choix)
        hist.append(choix)
        vu_recent.append(choix)
    return " ".join(produits)


# ---------------------------------------------------------------------------
# Dialogue : sanctuaire, faits gelés, bouche, ou aveu de bouche vide.
# ---------------------------------------------------------------------------

_APPRENDRE = re.compile(
    r"(?:apprends(?:-moi)?(?: que)?|sache que|learn that|retien[st] que)\s+(.+)",
    re.IGNORECASE,
)


def executer(message: str, bouche: Bouche, tissu: TissuScelle | None = None, **opts) -> dict:
    msg = str(message).strip()
    tokens = tokeniser(msg)
    ensemble = set(tokens)

    m = _APPRENDRE.search(msg)
    if m:
        enonce = m.group(1).strip().rstrip(".")
        ch = bouche.graver_chaine(enonce, registre="fait")
        if tissu is not None:
            tissu.memoire[ch["cles"][0]] = {"enonce": ch["enonce"], "sha256": ch["sha256"]}
        fleche = " → ".join(ch["mots"])
        return {
            "intent": "chaine_gelee",
            "reponse": (
                f"Chaîne dirigée gravée et gelée (sceau #{ch['sha256']}) : {fleche}. "
                "Ce n'est plus un paragraphe rangé à part : la bouche peut l'emprunter."
            ),
        }

    if any(w in ensemble for w in ("bonjour", "salut", "coucou", "hello", "bonsoir")):
        return {
            "intent": "saluer",
            "reponse": "Salut. Je suis Ratiss GI. Le tissu se souvient des fréquentations, la bouche apprend l'ordre.",
        }

    if any(p in norm(msg) for p in ("qui es tu", "qui es-tu", "ton nom", "who are you")):
        return {
            "intent": "identite",
            "reponse": (
                "Je suis Ratiss GI, la bouche dirigée posée sur le tissu de Jonathan Evina. "
                "Je ne suis pas un transformeur. Je marche d'un mot vers le suivant."
            ),
        }

    if tissu is not None:
        cle = tissu.sujet_sanctuaire(msg, tokens)
        if cle and any(w in ensemble for w in ("explique", "comment", "pourquoi", "definition", "definir", "cest", "quoi", "parle", "raconte")):
            ent = tissu.sanctuaire[cle]
            faits = ent.get("faits", {})
            if any(w in ensemble for w in ("explique", "comment", "pourquoi")):
                mode = "EXPLICATION"
            else:
                mode = "DEFINITION"
            txt = faits.get(mode) or faits.get("DEFINITION") or ""
            nom = ent.get("nom", cle)
            # Le paragraphe scellé n'entre pas dans la bouche plastique.
            # On le compile en chemin, on le marche, on rend la graphie d'origine
            # seulement si le chemin tient.
            mots = tokeniser(txt)
            rendu = _reponse_chemin(mots, txt, None)
            return {"intent": "sanctuaire", "reponse": f"{nom}. {rendu}"}

    ch = bouche.chaine_pour(tokens)
    if ch and any(w in ensemble for w in ("parle", "raconte", "explique", "qui", "quoi", "ou", "comment", "pourquoi", "quel", "quelle")):
        ancre = _ancre(ch.get("mots", []), ch.get("cles", []), tokens)
        rendu = _reponse_chemin(ch.get("mots", []), ch.get("enonce", ""), ancre)
        return {"intent": "chemin_gele", "reponse": rendu}

    if bouche.vide() or bouche.n_arcs() == 0:
        diag = ""
        if tissu is not None and tokens:
            # Le plus long mot connu : on montre la nuée, et on dit que ce n'est pas une phrase.
            connu = [t for t in tokens if tissu.cle(t)]
            if connu:
                mot = max(connu, key=len)
                voisins = [n for n, _ in tissu.voisins(mot, 6)]
                if voisins:
                    diag = (
                        f" Le tissu, lui, fait résonner « {mot} » avec : "
                        + ", ".join(voisins)
                        + ". C'est une nuée, pas une suite."
                    )
        return {
            "intent": "bouche_vide",
            "reponse": (
                "Bouche vide. Je n'ai pas encore appris quel mot a le droit de suivre. "
                "Le fichier scellé ne sera pas forcé de parler à ma place."
                + diag
            ),
        }

    suite = parler(bouche, msg, tissu=tissu, **opts)
    if not suite:
        return {
            "intent": "silence",
            "reponse": "Je n'ai aucune flèche sortante depuis ces mots. La bouche se tait plutôt que d'inventer un gabarit.",
        }
    return {"intent": "marche", "reponse": suite}


def pct(x: float) -> str:
    return f"{100.0 * x:.0f} %"


def cmd_demo() -> int:
    print("=" * 72)
    print("RATISS GI · démo de la bouche (aucun GPU, aucun .ratiss requis)")
    print("=" * 72)
    b_theme = Bouche()
    b_theme.contraste = False
    b_theme.eduquer(CORPUS_DEMO, tours=3, registre="conte")
    # Le thème seul : on évalue le graphe de fenêtre, pas les arcs.
    ev_theme = b_theme.evaluer(CORPUS_DEMO, mode="theme")

    b = Bouche()
    b.eduquer(CORPUS_DEMO, tours=3, registre="conte", contraste=True)
    ev_ordre = b.evaluer(CORPUS_DEMO, mode="ordre")
    ev_tri = b.evaluer(CORPUS_DEMO, mode="trigramme")
    ev_lum = b.evaluer(CORPUS_DEMO, mode="lumiere", memoire=8)
    ev_hors = b.evaluer(TENU_A_LECART_DEMO, mode="lumiere", memoire=8)
    ev_hors_tri = b.evaluer(TENU_A_LECART_DEMO, mode="trigramme")
    glouton = parler(b, "un", glouton=True, n=16, lam=1.0, memoire=1)
    pioche = parler(b, "le petit prince", n=16, lam=0.75, memoire=8, graine=3)

    print(f"corpus jouet          : {len(phrases_de(CORPUS_DEMO))} phrases")
    print(f"arcs dirigés          : {b.n_arcs()}")
    print()
    print(f"{'mesure':<42} {'top-5':>8}")
    print("-" * 52)
    print(f"{'thème, fenêtre de 3 (les deux sens)':<42} {pct(ev_theme['top5']):>8}")
    print(f"{'arcs dirigés, dernier mot seulement':<42} {pct(ev_ordre['top5']):>8}")
    print(f"{'trigramme + repli bigramme':<42} {pct(ev_tri['top5']):>8}")
    print(f"{'arcs dirigés, lumière sur 8 mots':<42} {pct(ev_lum['top5']):>8}")
    print(f"{'tenu à l écart, lumière (2 phrases)':<42} {pct(ev_hors['top5']):>8}")
    print(f"{'tenu à l écart, trigramme':<42} {pct(ev_hors_tri['top5']):>8}")
    print()
    print("marche gloutonne depuis « un » :")
    print("  ", glouton)
    print("pioche depuis « le petit prince » :")
    print("  ", pioche)
    print()
    vide = Bouche()
    rep = executer("parle moi de la mer", vide, None)
    print("sans éducation :")
    print(" ", rep["reponse"])
    print()
    executer("Apprends que la lune orbite autour de la terre", b, None)
    rep2 = executer("parle moi de la lune", b, None)
    print("après une chaîne gelée :")
    print(" ", rep2["reponse"])
    print()
    print("Le jouet tourne en rond dès que les phrases vues sont épuisées.")
    print("C'est une naissance, pas un sommet. Branche un vrai texte.")
    return 0


def cmd_audit(chemin: str) -> int:
    tissu = TissuScelle(chemin)
    a = audit_tissu(tissu)
    print("=" * 72)
    print("AUDIT · le tissu scellé n'est pas une bouche")
    print("=" * 72)
    print(f"fichier              : {chemin}")
    print(f"modèle               : {a['meta'].get('NOM_MODELE', '?')}")
    print(f"neurones             : {a['neurones']:,}")
    print(f"liens                : {a['liens']:,}")
    print(f"gelés                : {a['geles']:,}")
    print(f"paires déjà triées   : {a['tries']:,}    paires inversées : {a['inverses']:,}")
    print(f"part triée a<=b      : {pct(a['part_triee'])}")
    print(f"chargement           : {a['dt']*1000:.0f} ms")
    print(f"sanctuaire           : {', '.join(a['sanctuaire'])}")
    print()
    print(f"top-5 du mot suivant sur {len(SONDE_16)} suites françaises : {pct(a['top5'])}  ({a['hits']}/{len(SONDE_16)})")
    print("Le hasard, si chaque mot avait 30 voisins utiles, serait plus haut.")
    print("Ici le sommet est souvent l'alphabet des forces à 100.")
    print()
    for src, vrai, noms, ok in a["lignes"]:
        marque = "oui" if ok else "non"
        print(f"  {src:>10} → {vrai:<10} dans le top5 ? {marque:<3}  vu : {', '.join(noms[:5])}")
    print()
    if a["inverses"] == 0:
        print("Verdict : 0 lien n'est orienté. La v3 refuse d'apprendre à marcher là-dessus.")
        print("Le gel du fichier n'est pas modifié. La bouche s'écrit à côté.")
    return 0


def construire_argparse() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ratiss_v3.py",
        description="Bouche dirigée RATISS GI. Le tissu résonne. La bouche marche vers l'avant.",
    )
    p.add_argument("cerveau", nargs="?", help="fichier .ratiss (lecture seule)")
    p.add_argument("message", nargs="*", help="phrase à continuer ou question")
    p.add_argument("--demo", action="store_true", help="jouet Petit Prince, sans cerveau")
    p.add_argument("--audit", action="store_true", help="diagnostique le tissu scellé")
    p.add_argument("--eduquer", metavar="FICHIER", help="texte, une phrase par ligne ou ponctuée")
    p.add_argument("--faits", metavar="FICHIER", help="une vérité par ligne, gravée comme chaîne gelée")
    p.add_argument("--evaluer", metavar="FICHIER", help="texte tenu à l'écart, pour le top-5")
    p.add_argument("--charger", metavar="BOUCHE", help="bouche.json ou .bouche déjà apprise")
    p.add_argument("--sauver", metavar="BOUCHE", help="où écrire la bouche (le .ratiss n'est pas touché)")
    p.add_argument("--tours", type=int, default=1)
    p.add_argument("--lam", type=float, default=None, help="1 = ordre seul, 0 = thème seul")
    p.add_argument("--memoire", type=int, default=None, help="combien de mots passés éclairent")
    p.add_argument("--registre", default=None, help="conte, dialogue, fait, science, ordre")
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--sans-contraste", action="store_true")
    p.add_argument("--glouton", action="store_true", help="toujours le mot le plus fort")
    p.add_argument("--mots", type=int, default=18)
    p.add_argument("--graine", type=int, default=0)
    p.add_argument("--init-vide", metavar="BOUCHE", help="écrit une bouche à l'étape 0, zéro arc")
    return p


def main(argv: list[str] | None = None) -> int:
    args = construire_argparse().parse_intermixed_args(argv)

    if args.init_vide:
        b = Bouche()
        b.registre = args.registre
        b.sauver(args.init_vide)
        print(f"bouche vide écrite : {args.init_vide}")
        print("Zéro arc. Ce n'est pas un bruit gaussien : c'est l'absence d'ordre.")
        return 0

    if args.demo:
        return cmd_demo()

    if args.audit:
        if not args.cerveau:
            print("il faut le chemin du .ratiss", file=sys.stderr)
            return 2
        return cmd_audit(args.cerveau)

    tissu = None
    if args.cerveau and os.path.exists(args.cerveau):
        # Empreinte : on vérifie à la fin que le fichier scellé n'a pas bougé.
        h_avant = hashlib.sha256(open(args.cerveau, "rb").read()).hexdigest()
        tissu = TissuScelle(args.cerveau)
    else:
        h_avant = None
        if args.cerveau and not args.message:
            print(f"fichier introuvable : {args.cerveau}", file=sys.stderr)
            return 2

    if args.charger:
        bouche = Bouche.charger(args.charger)
    else:
        bouche = Bouche()
    if args.lam is not None:
        bouche.lam = args.lam
    if args.memoire is not None:
        bouche.memoire = args.memoire
    if args.temperature is not None:
        bouche.temperature = args.temperature
    if args.sans_contraste:
        bouche.contraste = False
    if args.registre:
        bouche.registre = args.registre

    if args.eduquer:
        with open(args.eduquer, "r", encoding="utf-8") as f:
            texte = f.read()
        stats = bouche.eduquer(
            texte,
            tours=args.tours,
            registre=args.registre or bouche.registre or "ordre",
            contraste=not args.sans_contraste,
        )
        print(
            f"éducation · registre={args.registre or bouche.registre or 'ordre'} · {stats['phrases']} phrases · "
            f"{stats['tokens']} tokens/tour · {stats['tours']} tours · "
            f"{stats['arcs']} arcs · {stats['decharges']} décharges"
        )
        ev = bouche.evaluer(texte, tissu=tissu, mode="lumiere", memoire=bouche.memoire)
        print(f"top-5 sur le texte vu (ne suffit pas) : {pct(ev['top5'])}  ({ev['hits']}/{ev['total']})")
        print("le chiffre qui compte est celui de --evaluer, sur un fichier non donné ici.")

    if args.faits:
        with open(args.faits, "r", encoding="utf-8") as f:
            lignes = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        for ligne in lignes:
            ch = bouche.graver_chaine(ligne, registre=args.registre or "fait")
            print(f"gelé #{ch['sha256']}  {' → '.join(ch['mots'])}")
        print(f"{len(lignes)} chaînes gelées dans le registre {args.registre or 'fait'}")

    if args.evaluer:
        with open(args.evaluer, "r", encoding="utf-8") as f:
            texte = f.read()
        print()
        print(f"{'mode':<28} {'top-5':>8}   détail")
        for mode, mem in (
            ("theme", 1),
            ("ordre", 1),
            ("lumiere", bouche.memoire),
            ("trigramme", 1),
            ("mixte", bouche.memoire),
        ):
            ev = bouche.evaluer(texte, tissu=tissu, mode=mode, lam=bouche.lam, memoire=mem)
            print(f"{mode:<28} {pct(ev['top5']):>8}   {ev['hits']}/{ev['total']}")
        if tissu is not None:
            ev = bouche.evaluer(texte, tissu=tissu, mode="tissu")
            print(f"{'tissu scellé seul':<28} {pct(ev['top5']):>8}   {ev['hits']}/{ev['total']}")

    message = " ".join(args.message).strip()
    if message:
        opts = dict(
            n=args.mots,
            lam=bouche.lam,
            memoire=bouche.memoire,
            temperature=bouche.temperature,
            graine=args.graine,
            glouton=args.glouton,
        )
        res = executer(message, bouche, tissu, **opts)
        print()
        print(res["reponse"])

    if args.sauver:
        bouche.sauver(args.sauver)
        print(f"bouche sauvée : {args.sauver}  (le .ratiss n'a pas été ouvert en écriture)")

    if h_avant is not None:
        h_apres = hashlib.sha256(open(args.cerveau, "rb").read()).hexdigest()
        if h_avant != h_apres:
            print("ALERTE : le fichier scellé a changé. Ce n'est pas prévu.", file=sys.stderr)
            return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
