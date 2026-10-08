#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIGURE ÉCOLE v1 — la croissance du cerveau, leçon par leçon (38 -> 44).
RATISS Labs · MIT · usage : python3 outils/figures_ecole.py (matplotlib requis)

Zéro dessin à la main : les nombres sont ceux pinnés par la batterie
(tests_verdicts.py : contrôles dialogues/ding/cefr/frenchqa/piaf/fquad2/
wildchat) et les mots bus ceux des preuves. Si la batterie change, les
asserts refusent et la figure doit être mise à jour avec elle.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FOND = "#062026"
CYAN = "#4ff0ff"
OR = "#ffd166"
BLANC = "#eaf6f6"
GRIS = "#9db8b8"

# (leçon, base, neurones, liens, mots bus) — pinnés batterie + preuves.
LECONS = [
    (38, "accueil", 25272, 161454, 6295),
    (39, "ding", 25803, 173556, 70274),
    (40, "cefr", 31374, 211888, 109486),
    (41, "frenchQA", 64277, 304561, 2398744),
    (42, "piaf", 64325, 314097, 52658),
    (43, "fquad2", 64539, 316963, 11700),
    (44, "wildchat", 90666, 404043, 19556414),
]


def main():
    assert [l[0] for l in LECONS] == [38, 39, 40, 41, 42, 43, 44]
    assert LECONS[-1][2:] == (90666, 404043, 19556414), "recaler sur la batterie !"
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_facecolor(FOND)
    fig.patch.set_facecolor(FOND)
    xs = [l[0] for l in LECONS]
    ns = [l[2] for l in LECONS]
    ls = [l[3] for l in LECONS]
    ax.plot(xs, ns, color=CYAN, lw=2.5, marker="o", markersize=7, label="neurones")
    ax.plot(xs, ls, color=OR, lw=2.5, marker="s", markersize=6, label="liens")
    for x, n, l, b in [(l[0], l[2], l[3], l[1]) for l in LECONS]:
        ax.text(x, n + 6000, f"{n}", color=CYAN, fontsize=8.5, ha="center")
        ax.text(x, l + 9000, f"{l}", color=OR, fontsize=8.5, ha="center")
        ax.text(x, 8000, b, color=GRIS, fontsize=9, ha="center", style="italic")
    ax.set_title("L'ÉCOLE MANUELLE — le cerveau grandit leçon par leçon "
                 "(38 -> 44, nombres pinnés par la batterie)",
                 color=BLANC, fontsize=13, weight="bold", pad=14)
    ax.set_xlabel("leçon", color=GRIS, fontsize=11)
    ax.set_ylabel("neurones / liens", color=GRIS, fontsize=11)
    ax.set_xticks(xs)
    ax.tick_params(colors=GRIS)
    for sp in ax.spines.values():
        sp.set_color(GRIS)
    leg = ax.legend(frameon=True, fontsize=10)
    leg.get_frame().set_facecolor("#0b3238")
    leg.get_frame().set_edgecolor(GRIS)
    for t in leg.get_texts():
        t.set_color(BLANC)
    ax.text(43.4, 150000, "wildchat : 19,5M mots bus,\n+26 127 neurones / +87 080 liens",
            color=BLANC, fontsize=10, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.4", fc="#0b3238", ec=CYAN, alpha=0.9))
    fig.tight_layout()
    fig.savefig("images/croissance-ecole.png", dpi=100)
    plt.close(fig)
    print("images/croissance-ecole.png écrite")


if __name__ == "__main__":
    main()
