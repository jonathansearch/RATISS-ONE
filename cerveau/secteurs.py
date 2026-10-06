# -*- coding: utf-8 -*-
"""
SECTEURS DE MÉMOIRE RELATIONNELLE v1 — VIF -> REFRAIN -> SANCTUAIRE.
RATISS Labs · MIT.

Inspiré des organes FOCAL (voir SECTEURS.md) :
- CONDENSATEUR -> VIF : l'entrée arrive en charge brute.
- PORTEURS -> REFRAIN : les traces répétées convergent (tranches disjointes :
  chaque séquence n'est portée qu'une fois).
- CONTENEUR -> SANCTUAIRE : le fond garde les boucles stables (longévité).

Doctrine : le secteur stocke la TRACE relationnelle (quels mots ensemble,
dans quel ordre, combien de fois, avec quelle force) — jamais la donnée
brute (ni audio, ni transcrit archivé). Stocker la relation, pas la donnée.
"""

# Régime de chaque secteur : force d'entrée, pas par répétition,
# perte par nuit, capacité (oubli du plus ancien), coups pour promotion.
REGIMES = {
    "VIF":        {"entree": 30, "pas": 20, "nuit": 20, "cap": 20,  "coups": 2,    "vers": "REFRAIN"},
    "REFRAIN":    {"entree": 40, "pas": 15, "nuit": 8,  "cap": 50,  "coups": 4,    "vers": "SANCTUAIRE"},
    "SANCTUAIRE": {"entree": 60, "pas": 10, "nuit": 1,  "cap": 200, "coups": None, "vers": None},
}


class Trace:
    """Une séquence entendue : mots ordonnés + répétitions + force."""

    def __init__(self, mots, force):
        self.mots = tuple(mots)
        self.coups = 1
        self.force = force

    def repeter(self, pas):
        self.coups += 1
        self.force = min(100, self.force + pas)

    def __repr__(self):
        return f"{'+'.join(self.mots)} x{self.coups} f{self.force}"


class Secteur:
    def __init__(self, nom):
        self.nom = nom
        self.regime = REGIMES[nom]
        self.traces = {}   # mots -> Trace (tranches disjointes : une seule fois)
        self.ordre = []    # FIFO pour l'éviction

    def deposer(self, mots):
        """Dépose (ou répète) une séquence. Retourne (trace, est_nouvelle)."""
        mots = tuple(mots)
        if mots in self.traces:
            trace = self.traces[mots]
            trace.repeter(self.regime["pas"])
            return trace, False
        trace = Trace(mots, self.regime["entree"])
        self.traces[mots] = trace
        self.ordre.append(mots)
        while len(self.ordre) > self.regime["cap"]:
            vieux = self.ordre.pop(0)
            del self.traces[vieux]
        return trace, True

    def nuit(self, suivant=None):
        """La nuit passe : tout s'affaiblit, les mûres sont promues."""
        morts, promus = [], []
        for mots in list(self.ordre):
            trace = self.traces[mots]
            trace.force -= self.regime["nuit"]
            if trace.force <= 0:
                morts.append(mots)
                del self.traces[mots]
                self.ordre.remove(mots)
            elif (suivant is not None and self.regime["coups"] is not None
                    and trace.coups >= self.regime["coups"]):
                promus.append(mots)
                del self.traces[mots]
                self.ordre.remove(mots)
                trace.coups = 1
                trace.force = max(trace.force, suivant.regime["entree"])
                suivant.traces[mots] = trace
                suivant.ordre.append(mots)
        return {"morts": morts, "promus": promus}

    def top(self, n=5):
        return sorted(self.traces.values(), key=lambda t: (-t.force, t.mots))[:n]
