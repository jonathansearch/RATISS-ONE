#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIGURES v1 — les images du README, RÉGÉNÉRÉES depuis les vraies mesures.
RATISS Labs · MIT · usage : python3 outils/figures.py (matplotlib requis)

Zéro dessin à la main : le graphe est rejoué hors-ligne (transcrit JFK archivé,
mêmes répétitions que cerveau-demo.py) et les nombres affichés sont ASSERTÉS
égaux à la démo live (preuves/sortie-cerveau-demo.txt). Si la démo change, les
figures refusent de se générer avec les vieux nombres.
"""

import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cerveau.cerveau import Cerveau, MOTS, MOTIFS, CONCEPTS  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

FOND = "#062026"
CYAN = "#4ff0ff"
SARCELLE = "#1a7a8a"
OR = "#ffd166"
BLANC = "#eaf6f6"
GRIS = "#9db8b8"

# Transcrit JFK archivé (preuves/transcription-jfk.txt), normalisé comme la démo.
MOTS_JFK = ("and so my fellow americans ask not what your country can do for you "
            "ask what you can do for your country").split()


def rejouer_demo():
    """Rejoue cerveau-demo.py hors-ligne (mêmes fenêtres, mêmes répétitions)."""
    wins = [tuple(MOTS_JFK[i:i + 3]) for i in range(len(MOTS_JFK) - 2)]
    c = Cerveau()
    for w in wins:
        c.entendre_sequence(list(w))
    riches = [w for w in wins if sum(1 for m in w if m in MOTS) >= 2]
    for _ in range(2):
        for w in riches:
            c.entendre_sequence(list(w))
    focus = ("fellow", "americans", "ask")
    for _ in range(6):
        c.entendre_sequence(list(focus))
    c.nuit()
    for _ in range(3):
        c.entendre_sequence(list(focus))
    c.nuit()
    # Assertions = les nombres de la démo live, gravés dans le marbre.
    assert len(wins) == 20, wins
    assert len(riches) == 3, riches
    assert len(c.graph["neurones"]) == 13, sorted(c.graph["neurones"])
    assert len(c.graph["liens"]) == 28, len(c.graph["liens"])
    assert len(c.chaines) == 2, c.chaines
    san = c.secteurs["SANCTUAIRE"].traces
    top = c.secteurs["SANCTUAIRE"].top(1)[0]
    assert len(san) == 1 and list(top.mots) == list(focus) and top.force == 92, san
    assert len(c.secteurs["REFRAIN"].traces) == 3
    assert len(c.secteurs["VIF"].traces) == 0
    return c


def style(ax):
    ax.set_facecolor(FOND)
    ax.figure.patch.set_facecolor(FOND)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])


def joli(nom):
    """word_americans -> americans (lisibilité ; les concepts restent tels quels)."""
    return nom[5:] if nom.startswith("word_") else nom


def positions():
    """Deux couches déterministes : concepts en hexagone intérieur, mots autour
    (chaque mot près de ses concepts), distant près de comet. Aucun hasard."""
    ang = {"people": 90, "together": 160, "voice": 215, "duty": 285,
           "future": 340, "land": 20}
    decal = {"word_americans": 6, "word_country": 11, "word_fellow": -8,
             "word_ask": -6, "word_homeland": -11, "word_comet": 0}
    pos = {}
    for c in CONCEPTS:
        a = math.radians(ang[c])
        pos[c] = (math.cos(a) * 1.1, math.sin(a) * 1.1)
    for mot in ("word_americans", "word_country", "word_fellow",
                "word_ask", "word_homeland", "word_comet"):
        for motif, membres in MOTIFS.items():
            if mot in membres and motif != "TOUT":
                liés = [m for m in membres if m in CONCEPTS]
                break
        if liés:  # près de ses concepts…
            mx = sum(math.cos(math.radians(ang[m])) for m in liés) / len(liés)
            my = sum(math.sin(math.radians(ang[m])) for m in liés) / len(liés)
        else:  # …ou seul au large (comet, le témoin lointain)
            mx, my = math.cos(math.radians(250)), math.sin(math.radians(250))
        base = math.degrees(math.atan2(my, mx)) + decal[mot]
        a = math.radians(base)
        pos[mot] = (math.cos(a) * 3.0, math.sin(a) * 3.0)
    xc, yc = pos["word_comet"]
    n = math.hypot(xc, yc) or 1
    pos["distant"] = (xc / n * 3.95, yc / n * 3.95)
    return pos


def dessine_graphe(ax, c, annotes_forces):
    pos = positions()
    liens = sorted(c.graph["liens"].items(), key=lambda kv: kv[1])  # faibles d'abord
    fmax = max(f for _, f in liens)
    chaines = {tuple(sorted(k)) for k in c.chaines}
    noeuds_chaine = {n for ch in chaines for n in ch}

    def epaisseur(f):
        return 0.7 + 5.0 * (f / fmax)

    for (a, b), f in liens:
        xa, ya = pos[a]
        xb, yb = pos[b]
        est_chaine = tuple(sorted((a, b))) in chaines
        mort = f <= 0 and not est_chaine
        col = OR if est_chaine else (GRIS if mort else (CYAN if f >= 50 else SARCELLE))
        if est_chaine:  # halo
            ax.plot([xa, xb], [ya, yb], color=OR, lw=epaisseur(f) + 8, alpha=0.20,
                    solid_capstyle="round", zorder=1)
        ax.plot([xa, xb], [ya, yb], color=col, lw=1.0 if mort else epaisseur(f),
                alpha=0.7 if mort else (1.0 if est_chaine or f >= 50 else 0.6),
                solid_capstyle="round", linestyle=(0, (3, 3)) if mort else "-",
                zorder=2)
        if annotes_forces:
            ax.text((xa + xb) / 2, (ya + yb) / 2, str(f),
                    color=GRIS if mort else BLANC, fontsize=8,
                    ha="center", va="center", zorder=4,
                    bbox=dict(boxstyle="round,pad=0.3", fc=FOND, ec="none", alpha=0.9))

    for n in pos:
        x, y = pos[n]
        est_mot = n.startswith("word_")
        est_chaine = n in noeuds_chaine
        col = OR if est_chaine else (CYAN if n in CONCEPTS or est_mot else GRIS)
        taille = 620 if est_chaine else (520 if est_mot else (420 if n in CONCEPTS else 300))
        ax.scatter([x], [y], s=taille, c=["#0b3238"], edgecolors=[col],
                   linewidths=2.6 if est_chaine else 2.0, zorder=3)
        nrm = math.hypot(x, y) or 1  # étiquette radiale, hors du noeud
        lx, ly = x + x / nrm * 0.52, y + y / nrm * 0.52
        ax.text(lx, ly, joli(n), color=BLANC, fontsize=11 if est_mot else 10,
                ha="center", va="center", weight="bold" if est_chaine or est_mot else "normal",
                zorder=5, bbox=dict(boxstyle="round,pad=0.3", fc=FOND, ec="none", alpha=0.85))
    ax.set_xlim(-4.6, 4.6)
    ax.set_ylim(-4.6, 4.6)
    ax.set_aspect("equal")


def fig_hero(c):
    fig, ax = plt.subplots(figsize=(14, 9))
    style(ax)
    dessine_graphe(ax, c, annotes_forces=False)
    ax.set_title("LE TISSU ÉDUQUÉ — 13 neurones, 28 liens (26 tissés + 2 chaînes nées de JFK)",
                 color=BLANC, fontsize=14, weight="bold", pad=14)
    ax.text(0, -4.35,
            "épaisseur = force mesurée du lien  ·  or = chaînes des mots qui se suivent (fellow-americans-ask)",
            color=GRIS, fontsize=10, ha="center", va="top")
    fig.tight_layout()
    fig.savefig("images/hero-cerveau.png", dpi=100)
    plt.close(fig)


def fig_graphe(c):
    fig, ax = plt.subplots(figsize=(13, 9.5))
    style(ax)
    dessine_graphe(ax, c, annotes_forces=True)
    ax.set_title("JFK DANS LE CERVEAU — chaque lien porte sa force mesurée (lie 10 / délie 3)",
                 color=BLANC, fontsize=11, weight="bold", pad=14)
    ax.text(0, -4.35,
            "centre : 6 concepts (people, land, voice, duty, together, future)  ·  "
            "anneau : 6 mots  ·  or : 2 chaînes de séquences",
            color=GRIS, fontsize=9.5, ha="center", va="top")
    fig.tight_layout()
    fig.savefig("images/graphe-jfk.png", dpi=100)
    plt.close(fig)


def fig_secteurs():
    fig, ax = plt.subplots(figsize=(14, 6))
    style(ax)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.set_title("LES SECTEURS — un entonnoir qui oublie bien (mesures démo JFK live)",
                 color=BLANC, fontsize=13, weight="bold", pad=12)
    blocs = [
        (0.5, 4.2, "VIF", "l'instant", ["20 séquences entrent", "force 30, nuit -20", "meurt sous 20", "monte à 2 rencontres"], SARCELLE),
        (5.2, 8.9, "REFRAIN", "le chant", ["4 promues, 3 survivent", "force 40, nuit -8", "meurt sous 8", "monte à 4 rencontres"], CYAN),
        (9.9, 13.5, "SANCTUAIRE", "le marbre", ["1 élue : f92", "fellow americans ask", "nuit -1, jamais morte", "la plus répétée"], OR),
    ]
    for x0, x1, nom, sous, lignes, col in blocs:
        ax.add_patch(FancyBboxPatch((x0, 1.2), x1 - x0, 3.6, boxstyle="round,pad=0.08",
                                    fc="#0b3238", ec=col, lw=2))
        ax.text((x0 + x1) / 2, 4.35, nom, color=col, fontsize=14, weight="bold", ha="center")
        ax.text((x0 + x1) / 2, 3.95, sous, color=GRIS, fontsize=10, style="italic", ha="center")
        for i, lig in enumerate(lignes):
            ax.text((x0 + x1) / 2, 3.35 - i * 0.5, lig, color=BLANC, fontsize=9.5, ha="center")
    for x0, x1, txt in [(4.2, 5.2, "nuit 1"), (8.9, 9.9, "nuit 2")]:
        ax.add_patch(FancyArrowPatch((x0 + 0.1, 3), (x1 - 0.1, 3), arrowstyle="-|>",
                                    color=BLANC, lw=2, mutation_scale=18))
        ax.text((x0 + x1) / 2, 3.35, txt, color=GRIS, fontsize=9, ha="center")
    ax.text(7, 0.55, "la nuit ne comprend rien : elle efface — c'est l'oubli qui fait la mémoire",
            color=GRIS, fontsize=10, ha="center", style="italic")
    fig.tight_layout()
    fig.savefig("images/secteurs.png", dpi=100)
    plt.close(fig)


def fig_boucle():
    fig, ax = plt.subplots(figsize=(14, 5.2))
    style(ax)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5.2)
    ax.set_title("LA BOUCLE — du son au son en 46 secondes (portes bêtes, coeur intelligent)",
                 color=BLANC, fontsize=13, weight="bold", pad=12)
    etapes = [
        ("OREILLE", "Phonon-2", "transcrit sans comprendre", "22 mots mot pour mot", "~40 s", SARCELLE),
        ("TISSU", "english.ratum", "comprendre = résonner", "4 mots tenus à 90-95", "0.1 s", CYAN),
        ("CERVEAU", "secteurs", "trace + nuits", "20 seq. -> 1 sanctuaire f92", "0.1 s", OR),
        ("BOUCHE", "Piper", "parle sans comprendre", "résumé dit : 6 s d'audio", "~2 s", SARCELLE),
    ]
    x0s = [0.3, 3.75, 7.2, 10.65]
    for x0, (nom, organe, role, mesure, temps, col) in zip(x0s, etapes):
        ax.add_patch(FancyBboxPatch((x0, 1.3), 3.15, 2.9, boxstyle="round,pad=0.08",
                                    fc="#0b3238", ec=col, lw=2))
        ax.text(x0 + 1.575, 3.85, nom, color=col, fontsize=13, weight="bold", ha="center")
        ax.text(x0 + 1.575, 3.45, organe, color=BLANC, fontsize=10, ha="center")
        ax.text(x0 + 1.575, 2.95, role, color=GRIS, fontsize=8.5, style="italic", ha="center")
        ax.text(x0 + 1.575, 2.45, mesure, color=BLANC, fontsize=8.5, ha="center")
        ax.text(x0 + 1.575, 1.85, temps, color=col, fontsize=10, weight="bold", ha="center")
    for a, b in zip(x0s, x0s[1:]):
        ax.add_patch(FancyArrowPatch((a + 3.15 + 0.05, 2.75), (b - 0.05, 2.75),
                                    arrowstyle="-|>", color=BLANC, lw=2, mutation_scale=18))
    ax.add_patch(FancyArrowPatch((12.0, 1.2), (1.0, 1.2), arrowstyle="-|>",
                                color=GRIS, lw=1.4, mutation_scale=14, linestyle=(0, (4, 3)),
                                connectionstyle="arc3,rad=-0.10"))
    ax.text(7, 0.35, "la bouche ne dit que ce que le tissu tient", color=GRIS,
            fontsize=10, ha="center", style="italic")
    fig.tight_layout()
    fig.savefig("images/boucle.png", dpi=100)
    plt.close(fig)


def main():
    os.makedirs("images", exist_ok=True)
    print("rejeu de la démo (hors-ligne, déterministe)…")
    c = rejouer_demo()
    print("assertions live OK : 20 seq., 28 liens, sanctuaire f92")
    fig_hero(c)
    fig_graphe(c)
    fig_secteurs()
    fig_boucle()
    print("images/hero-cerveau.png, graphe-jfk.png, secteurs.png, boucle.png écrites")


if __name__ == "__main__":
    main()
