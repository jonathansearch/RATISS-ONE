#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIGURE VOCAB v1 — la constellation des 50 mots, tracée depuis l'export mesuré.
RATISS Labs · MIT · usage : python3 education/figures_vocab.py (matplotlib requis)

Zéro dessin à la main : parse education/vocabulaire50.ratum (273 liens),
ASSERT les nombres (56 mots, BILAN 50/50), puis trace. Positions
déterministes par famille ; épaisseurs = forces mesurées.

v2 (leçon 44, 8 oct. 2026) : l'export actuel porte 276 liens / 55 mots /
263 forts (word_avenir absent : MAVENIR motif seul, 5 témoins tracés).
"""

import math
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FOND = "#062026"
CYAN = "#4ff0ff"
SARCELLE = "#1a7a8a"
OR = "#ffd166"
BLANC = "#eaf6f6"
GRIS = "#9db8b8"
VERT = "#7fe0a8"
VIOLET = "#c9a8ff"

FAMILLES = {
    "VILLAGE": (["amis", "peuple", "pain", "eau", "enfants", "marche",
                 "maison", "fete", "voisins", "rue", "village"], CYAN),
    "DEVOIR": (["pays", "patrie", "unir", "honneur", "drapeau", "paix",
                "justice", "loi", "serment", "defendre"], OR),
    "NATURE": (["soleil", "lune", "arbre", "riviere", "montagne", "fleur",
               "oiseau", "vent", "pluie", "ciel"], VERT),
    "ESPRIT": (["livre", "mots", "histoire", "chanson", "question", "reponse",
               "savoir", "idee", "ecole", "maitre", "memoire"], VIOLET),
    "PONTS": (["main", "coeur", "chemin", "porte", "feu", "nuit", "matin", "temps"], BLANC),
    "LOINTAIN": (["etoile", "tambour", "nuage", "encre", "silex", "avenir"], GRIS),
}
ANCRES = {"amis", "peuple", "pays", "patrie", "unir", "soleil", "livre"}


def charger_export(chemin):
    liens, mots = {}, set()
    for ligne in open(chemin, encoding="utf-8"):
        m = re.match(r"\s*lien (\S+) (\S+) force (\d+)", ligne)
        if m:
            a, b, f = m.group(1), m.group(2), int(m.group(3))
            liens[tuple(sorted((a, b)))] = f
            mots.add(a)
            mots.add(b)
    return liens, mots


def positions():
    pos, noms = {}, {}
    fams = list(FAMILLES)
    for k, nom in enumerate(fams):
        membres, _ = FAMILLES[nom]
        base = math.radians(k * 360 / len(fams) + 90)
        anc = sorted(w for w in membres if w in ANCRES)
        autres = [w for w in membres if w not in ANCRES]
        for j, w in enumerate(anc):  # ancres : éventail large, jamais l'une sur l'autre
            if len(anc) == 1:
                a = base
            else:
                a = base + (0.30 + 0.30 * (j // 2)) * (-1 if j % 2 == 0 else 1)
            pos["word_" + w] = (math.cos(a) * 2.2, math.sin(a) * 2.2)
            noms["word_" + w] = nom
        for i, w in enumerate(autres):  # mots : arc serré (les étiquettes alternent)
            a = base + (i - (len(autres) - 1) / 2) * 0.13
            pos["word_" + w] = (math.cos(a) * 3.7, math.sin(a) * 3.7)
            noms["word_" + w] = nom
    return pos, noms


def main():
    ici = os.path.dirname(os.path.abspath(__file__))
    liens, mots = charger_export(os.path.join(ici, "vocabulaire50.ratum"))
    assert len(liens) == 276, len(liens)
    mots_mots = {m for m in mots if m.startswith("word_")}
    assert len(mots_mots) == 55, len(mots_mots)
    forts = sum(1 for f in liens.values() if f >= 70)
    assert forts == 263, forts
    print(f"asserts OK : 55 mots, 276 liens, {forts} forts")

    pos, noms = positions()
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_facecolor(FOND)
    fig.patch.set_facecolor(FOND)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    mots_mots_l = sorted(mots_mots)
    for (a, b), f in sorted(liens.items(), key=lambda kv: kv[1]):
        if a not in pos or b not in pos or f < 30:
            continue
        xa, ya = pos[a]
        xb, yb = pos[b]
        col = CYAN if f >= 80 else SARCELLE
        ax.plot([xa, xb], [ya, yb], color=col, lw=0.5 + 3.2 * f / 100,
                alpha=0.55 if f >= 80 else 0.45, solid_capstyle="round", zorder=1)

    rang_etiquette = {}
    for n in mots_mots_l:
        fam = noms[n]
        rang_etiquette.setdefault(fam, []).append(n)
    decal = {}
    for fam, lst in rang_etiquette.items():
        for i, n in enumerate(sorted(lst)):
            decal[n] = 0.55 if i % 2 == 0 else 1.05

    for n in mots_mots_l:
        x, y = pos[n]
        w = n[5:]
        fam = noms[n]
        col = FAMILLES[fam][1]
        est_ancre = w in ANCRES
        est_loin = fam == "LOINTAIN"
        ax.scatter([x], [y], s=520 if est_ancre else 300, c=["#0b3238"],
                   edgecolors=[col], linewidths=2.4 if est_ancre else 1.6, zorder=2)
        fs = 10.5 if est_ancre else (8.5 if not est_loin else 8)
        nrm = math.hypot(x, y) or 1  # étiquette radiale, deux rangées alternées
        d = 0.55 if est_ancre else decal[n]
        lx, ly = x + x / nrm * d, y + y / nrm * d
        ax.text(lx, ly, w, color=BLANC if not est_loin else GRIS, fontsize=fs,
                ha="center", va="center", weight="bold" if est_ancre else "normal",
                zorder=3, bbox=dict(boxstyle="round,pad=0.25", fc=FOND, ec="none", alpha=0.85))
        if est_ancre:
            ax.text(x - x / nrm * 0.5, y - y / nrm * 0.5, "ancre", color=col,
                    fontsize=7.5, ha="center", va="center", style="italic", zorder=3)

    ax.set_title("LA CONSTELLATION — 50 mots appris par phrases, 5 témoins tracés "
                 "(forces mesurées, round 3)",
                 color=BLANC, fontsize=12.5, weight="bold", pad=14)
    ax.text(0, -5.2, "épaisseur = force mesurée (liens < 30 masqués)  ·  "
            "5 familles + 8 ponts + 5 témoins gris  ·  anneau : mots, centre : ancres",
            color=GRIS, fontsize=9.5, ha="center", va="top")
    ax.set_xlim(-5.6, 5.6)
    ax.set_ylim(-5.6, 5.6)
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(os.path.join(ici, "..", "images", "constellation.png"), dpi=100)
    plt.close(fig)
    print("images/constellation.png écrite")


if __name__ == "__main__":
    main()
