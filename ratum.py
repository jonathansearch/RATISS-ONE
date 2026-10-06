#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATUM v0 — interprète de référence (LE BERCEAU).
RATISS Labs · Jonathan Evina · MIT.

Ce fichier n'est PAS le langage : c'est l'établi qui exécute les programmes
écrits en Ratum. Le langage lui-même est défini dans LANGAGE-RATUM.md :
mots français, niveaux entiers 0..100, sémantique déterministe.

Usage : python3 ratum.py programme.ratum
"""

import json
import sys


def norm(mot):
    """Normalise un mot-clé (casse + accents) pour la comparaison."""
    return (mot.lower().replace("é", "e").replace("è", "e").replace("ê", "e"))


class ErreurRatum(Exception):
    pass


def borne(n):
    """Tout niveau Ratum vit entre 0 et 100."""
    return max(0, min(100, int(n)))


class Tissu:
    def __init__(self, nom):
        self.nom = nom
        self.neurones = {}   # nom -> {"seuil": int, "charge": int}
        self.liens = {}      # (a, b) trié -> force int
        self.motifs = {}     # nom -> [neurones]


class Interprete:
    PAS_RENFORCER = 10
    PAS_OUBLIER = 5
    SEUIL_DEFAUT = 50
    FORCE_NAISSANCE = 10
    MOITIE = 50  # charge minimale pour "battre"

    def __init__(self):
        self.tissu = None

    # ---------- utilitaires ----------

    def erreur(self, noligne, message):
        raise ErreurRatum(f"ligne {noligne} : {message}")

    def cle_lien(self, a, b):
        return tuple(sorted((a, b)))

    def actif(self, nom):
        n = self.tissu.neurones[nom]
        return n["charge"] >= n["seuil"]

    # ---------- analyse des blocs ----------

    def decoupage(self, lignes):
        """Découpe le source en (noligne, [mots]) en retirant commentaires."""
        instr = []
        for i, brute in enumerate(lignes, start=1):
            code = brute.split("#", 1)[0].strip()
            if not code:
                continue
            instr.append((i, code.split()))
        return instr

    def bloc_fin(self, instr, debut):
        """Trouve le 'fin' qui ferme le bloc ouvert en [debut]."""
        prof = 0
        for k in range(debut, len(instr)):
            mot = norm(instr[k][1][0])
            if mot in ("tissu", "repeter", "si"):
                prof += 1
            elif mot == "fin":
                prof -= 1
                if prof == 0:
                    return k
        self.erreur(instr[debut][0], "bloc ouvert mais jamais fermé par 'fin'")

    def bloc_sinon(self, instr, debut, fin):
        """Trouve le 'sinon' de premier niveau d'un bloc si (ou None)."""
        prof = 0
        for k in range(debut, fin):
            mot = norm(instr[k][1][0])
            if mot in ("tissu", "repeter", "si"):
                prof += 1
            elif mot == "fin":
                prof -= 1
            elif mot == "sinon" and prof == 1:
                return k
        return None

    # ---------- exécution ----------

    def executer(self, instr, debut, fin):
        k = debut
        while k < fin:
            noligne, mots = instr[k]
            mot = norm(mots[0])
            if mot == "tissu":
                finb = self.bloc_fin(instr, k)
                self.cmd_tissu(noligne, mots)
                self.executer(instr, k + 1, finb)
                k = finb + 1
            elif mot == "repeter":
                finb = self.bloc_fin(instr, k)
                n = self.entier(noligne, mots, 1, "répéter <nombre>")
                for _ in range(n):
                    self.executer(instr, k + 1, finb)
                k = finb + 1
            elif mot == "si":
                finb = self.bloc_fin(instr, k)
                cond = self.condition_si(noligne, mots)
                sin = self.bloc_sinon(instr, k, finb)
                if cond:
                    self.executer(instr, k + 1, sin if sin is not None else finb)
                elif sin is not None:
                    self.executer(instr, sin + 1, finb)
                k = finb + 1
            elif mot in ("fin", "sinon"):
                self.erreur(noligne, f"'{mots[0]}' sans bloc ouvert")
            else:
                self.commande(noligne, mots)
                k += 1

    def entier(self, noligne, mots, pos, usage):
        if len(mots) <= pos:
            self.erreur(noligne, f"il manque un nombre — usage : {usage}")
        try:
            return int(mots[pos])
        except ValueError:
            self.erreur(noligne, f"'{mots[pos]}' n'est pas un nombre — usage : {usage}")

    def condition_si(self, noligne, mots):
        # si <motif> tient <seuil> alors
        if len(mots) != 5 or norm(mots[2]) != "tient" or norm(mots[4]) != "alors":
            self.erreur(noligne, "usage : si <motif> tient <seuil> alors")
        return self.resonance(mots[1]) >= self.entier(noligne, mots, 3, "si <motif> tient <seuil> alors")

    # ---------- commandes ----------

    def commande(self, noligne, mots):
        mot = norm(mots[0])
        fns = {
            "neurone": self.cmd_neurone, "lien": self.cmd_lien,
            "motif": self.cmd_motif, "rencontre": self.cmd_rencontre,
            "propager": self.cmd_propager, "renforcer": self.cmd_renforcer,
            "oublier": self.cmd_oublier, "repos": self.cmd_repos,
            "resonance": self.cmd_resonance, "mesurer": self.cmd_mesurer,
            "juger": self.cmd_juger, "dire": self.cmd_dire,
            "graver": self.cmd_graver, "relire": self.cmd_relire,
        }
        if mot not in fns:
            self.erreur(noligne, f"mot inconnu '{mots[0]}' — voir LANGAGE-RATUM.md")
        fns[mot](noligne, mots)

    def exige_tissu(self, noligne):
        if self.tissu is None:
            self.erreur(noligne, "aucun tissu ouvert — commence par 'tissu <nom>'")

    def exige_neurone(self, noligne, nom):
        if nom not in self.tissu.neurones:
            self.erreur(noligne, f"neurone inconnu '{nom}' — déclare-le d'abord")

    def cmd_tissu(self, noligne, mots):
        if len(mots) != 2:
            self.erreur(noligne, "usage : tissu <nom>")
        if self.tissu is not None:
            self.erreur(noligne, "v0 : un seul tissu par programme")
        self.tissu = Tissu(mots[1])
        print(f"=== tissu {mots[1]} ===")

    def cmd_neurone(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) not in (2, 4) or (len(mots) == 4 and norm(mots[2]) != "seuil"):
            self.erreur(noligne, "usage : neurone <nom> [seuil <n>]")
        nom = mots[1]
        seuil = borne(self.entier(noligne, mots, 3, "neurone <nom> seuil <n>")) if len(mots) == 4 else self.SEUIL_DEFAUT
        self.tissu.neurones[nom] = {"seuil": seuil, "charge": 0}

    def cmd_lien(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) not in (3, 5) or (len(mots) == 5 and norm(mots[3]) != "force"):
            self.erreur(noligne, "usage : lien <a> <b> [force <n>]")
        a, b = mots[1], mots[2]
        self.exige_neurone(noligne, a)
        self.exige_neurone(noligne, b)
        force = borne(self.entier(noligne, mots, 4, "lien <a> <b> force <n>")) if len(mots) == 5 else self.FORCE_NAISSANCE
        self.tissu.liens[self.cle_lien(a, b)] = force

    def cmd_motif(self, noligne, mots):
        self.exige_tissu(noligne)
        reste = [m for m in mots[2:] if m != ":"]
        if len(mots) < 3 or not reste:
            self.erreur(noligne, "usage : motif <NOM> : <neurone> <neurone> ...")
        for n in reste:
            self.exige_neurone(noligne, n)
        self.tissu.motifs[mots[1]] = reste

    def cmd_rencontre(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) != 2 or mots[1] not in self.tissu.motifs:
            self.erreur(noligne, "usage : rencontre <motif> (motif déclaré)")
        for n in self.tissu.motifs[mots[1]]:
            self.tissu.neurones[n]["charge"] = 100

    def cmd_propager(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) != 1:
            self.erreur(noligne, "usage : propager")
        t = self.tissu
        nouv = {n: v["charge"] for n, v in t.neurones.items()}
        for (a, b), force in t.liens.items():
            nouv[b] = borne(nouv[b] + force * t.neurones[a]["charge"] // 100)
            nouv[a] = borne(nouv[a] + force * t.neurones[b]["charge"] // 100)
        for n, c in nouv.items():
            t.neurones[n]["charge"] = c

    def cmd_renforcer(self, noligne, mots):
        self.exige_tissu(noligne)
        pas = self.PAS_RENFORCER
        if len(mots) == 3 and norm(mots[1]) == "pas":
            pas = self.entier(noligne, mots, 2, "renforcer [pas <n>]")
        elif len(mots) != 1:
            self.erreur(noligne, "usage : renforcer [pas <n>]")
        for cle in self.tissu.liens:
            a, b = cle
            if self.actif(a) and self.actif(b):
                self.tissu.liens[cle] = borne(self.tissu.liens[cle] + pas)
            else:
                self.tissu.liens[cle] = borne(self.tissu.liens[cle] - pas)

    def cmd_oublier(self, noligne, mots):
        self.exige_tissu(noligne)
        pas = self.PAS_OUBLIER
        if len(mots) == 3 and norm(mots[1]) == "pas":
            pas = self.entier(noligne, mots, 2, "oublier [pas <n>]")
        elif len(mots) != 1:
            self.erreur(noligne, "usage : oublier [pas <n>]")
        for cle in self.tissu.liens:
            self.tissu.liens[cle] = borne(self.tissu.liens[cle] - pas)

    def cmd_repos(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) != 1:
            self.erreur(noligne, "usage : repos")
        for v in self.tissu.neurones.values():
            v["charge"] = 0

    def resonance(self, motif):
        t = self.tissu
        if motif not in t.motifs:
            raise ErreurRatum(f"motif inconnu '{motif}'")
        dedans = set(t.motifs[motif])
        internes = [f for (a, b), f in t.liens.items() if a in dedans and b in dedans]
        return sum(internes) // len(internes) if internes else 0

    def cmd_resonance(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) != 2:
            self.erreur(noligne, "usage : résonance <motif>")
        print(f"résonance {mots[1]} = {self.resonance(mots[1])}/100")

    def cmd_mesurer(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) != 1:
            self.erreur(noligne, "usage : mesurer")
        forces = list(self.tissu.liens.values())
        moy = sum(forces) // len(forces) if forces else 0
        forts = sum(1 for f in forces if f >= 70)
        print(f"liens : {len(forces)}")
        print(f"force moyenne : {moy}/100")
        print(f"liens forts : {forts}")

    def cmd_juger(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) != 3:
            self.erreur(noligne, "usage : juger <motif> <seuil>")
        r = self.resonance(mots[1])
        seuil = self.entier(noligne, mots, 2, "juger <motif> <seuil>")
        verdict = "TIENT" if r >= seuil else "ROMPT"
        print(f"JUGEMENT {mots[1]} : {verdict} ({r}/100, seuil {seuil})")

    def txt_forces(self):
        if not self.tissu.liens:
            return "(aucun lien)"
        return " ".join(f"{a}-{b}={f}" for (a, b), f in sorted(self.tissu.liens.items()))

    def cmd_dire(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) < 2:
            self.erreur(noligne, "usage : dire <mots...> (avec résonance <motif> ou forces)")
        out, i = [], 1
        while i < len(mots):
            if norm(mots[i]) == "resonance" and i + 1 < len(mots):
                out.append(str(self.resonance(mots[i + 1])))
                i += 2
            elif norm(mots[i]) == "forces":
                out.append(self.txt_forces())
                i += 1
            else:
                out.append(mots[i])
                i += 1
        print(" ".join(out))

    def cmd_graver(self, noligne, mots):
        self.exige_tissu(noligne)
        if len(mots) != 2:
            self.erreur(noligne, "usage : graver <fichier>")
        t = self.tissu
        photo = {
            "tissu": t.nom,
            "neurones": {n: {"seuil": v["seuil"], "charge": v["charge"]} for n, v in t.neurones.items()},
            "liens": [{"a": a, "b": b, "force": f} for (a, b), f in t.liens.items()],
            "motifs": t.motifs,
        }
        with open(mots[1], "w", encoding="utf-8") as fh:
            json.dump(photo, fh, ensure_ascii=False, indent=1)
        print(f"tissu gravé dans {mots[1]}")

    def cmd_relire(self, noligne, mots):
        if len(mots) != 2:
            self.erreur(noligne, "usage : relire <fichier>")
        with open(mots[1], encoding="utf-8") as fh:
            photo = json.load(fh)
        t = Tissu(photo["tissu"])
        t.neurones = {n: {"seuil": v["seuil"], "charge": v["charge"]} for n, v in photo["neurones"].items()}
        t.liens = {self.cle_lien(l["a"], l["b"]): l["force"] for l in photo["liens"]}
        t.motifs = photo["motifs"]
        self.tissu = t
        print(f"tissu relu depuis {mots[1]}")


def main():
    if len(sys.argv) != 2:
        print("usage : python3 ratum.py programme.ratum")
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as fh:
            lignes = fh.read().splitlines()
    except OSError as exc:
        print(f"impossible de lire {sys.argv[1]} : {exc}")
        return 2
    try:
        itp = Interprete()
        instr = itp.decoupage(lignes)
        itp.executer(instr, 0, len(instr))
    except ErreurRatum as exc:
        print(f"ERREUR RATUM — {exc}")
        return 1
    print("=== fin du programme ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
