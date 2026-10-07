#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figures du README — générées, pas dessinées à la main (loi du labo).
RATISS Labs · MIT.

Sources : preuves/sortie-conformite.txt (24/24),
preuves/sortie-pont-focal.txt (P_sig, porteurs).
Usage : python3 README-figures/fabriquer.py
"""
import os

FIG = os.path.dirname(os.path.abspath(__file__))
FONT = "font-family=\"Segoe UI, Verdana, sans-serif\""
CREME, ENCRE, OR = "#FAF7F0", "#1A1A2E", "#C9A227"
MER, VIOLET, VERT = "#1B6CA8", "#7C3AED", "#1E9E6A"
PIERRE, ROUGE = "#6B7280", "#D64545"

# 24 programmes du corpus, ordre de tests_verdicts.CAS (labels courts).
PROGS = ["rni-s", "rni-c", "rni-i", "j01", "j02", "j03", "j04", "j05",
         "j06", "j07", "j08", "j09", "j10", "EN", "écoute", "j11",
         "j12", "v1-coex", "grand", "vocab", "FR", "voc50", "j13", "j14"]

# P_sig — source : preuves/sortie-pont-focal.txt.
PSIG = [("fond seul", 5.7599, PIERRE, ""), ("frais", 6.3887, MER, ""),
        ("chaos", 6.3970, ROUGE, ""), ("sanctuaire", 6.2301, VERT, " ★")]


def cadre(w, h, titre):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" {FONT}>',
            f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="16" fill="{CREME}" stroke="#E8E0D0" stroke-width="2"/>',
            f'<text x="{w // 2}" y="36" font-size="20" font-weight="bold" fill="{ENCRE}" text-anchor="middle">{titre}</text>']


def berceau():
    L = cadre(760, 380, "🔬 24/24 — deux berceaux, une seule voix")
    L.append(f'<rect x="60" y="58" width="280" height="44" rx="12" fill="{MER}"/>'
             f'<text x="200" y="86" font-size="17" fill="white" text-anchor="middle">🐍 python3 ratum.py</text>')
    L.append(f'<text x="380" y="88" font-size="26" font-weight="bold" fill="{VERT}" text-anchor="middle">=</text>')
    L.append(f'<rect x="420" y="58" width="280" height="44" rx="12" fill="{VIOLET}"/>'
             f'<text x="560" y="86" font-size="17" fill="white" text-anchor="middle">⚙️ route-d/ratum-c</text>')
    assert len(PROGS) == 24
    for i, nom in enumerate(PROGS):
        x = 52 + (i % 6) * 110
        y = 118 + (i // 6) * 48
        L.append(f'<rect x="{x}" y="{y}" width="100" height="36" rx="10" fill="{VERT}"/>'
                 f'<text x="{x + 50}" y="{y + 24}" font-size="15" fill="white" text-anchor="middle">✓ {nom}</text>')
    L.append(f'<text x="380" y="326" font-size="13" fill="{ENCRE}" text-anchor="middle">sorties + codes + mem.scroll identiques au caractère près</text>')
    L.append(f'<text x="380" y="348" font-size="13" fill="{PIERRE}" text-anchor="middle">gcc -O2 -Wall -Wextra · zéro warning · preuve : sortie-conformite.txt</text>')
    L.append('</svg>')
    return "\n".join(L)


def focal():
    L = cadre(760, 460, "🌌 P_sig — le sanctuaire projette plus calme que le chaos")
    lo, hi, x0, x1 = 5.5, 6.5, 210, 640
    for g in (5.5, 5.75, 6.0, 6.25, 6.5):
        gx = x0 + (g - lo) / (hi - lo) * (x1 - x0)
        L.append(f'<line x1="{gx:.0f}" y1="60" x2="{gx:.0f}" y2="290" stroke="#E8E0D0" stroke-width="1"/>'
                 f'<text x="{gx:.0f}" y="306" font-size="11" fill="{PIERRE}" text-anchor="middle">{str(g).replace(".", ",")}</text>')
    for i, (nom, val, coul, etoile) in enumerate(PSIG):
        y = 80 + i * 52
        bw = (val - lo) / (hi - lo) * (x1 - x0)
        L.append(f'<text x="195" y="{y + 21}" font-size="15" fill="{ENCRE}" text-anchor="end">{nom}{etoile}</text>')
        L.append(f'<rect x="{x0}" y="{y}" width="{bw:.0f}" height="30" rx="8" fill="{coul}"/>'
                 f'<text x="{x0 + bw + 8:.0f}" y="{y + 21}" font-size="14" font-weight="bold" fill="{ENCRE}">{f"{val:.2f}".replace(".", ",")}</text>')
    L.append(f'<text x="380" y="336" font-size="12" fill="{PIERRE}" text-anchor="middle">axe 5,5 → 6,5 (zoom gradué) · delta max 0,17 · source : sortie-pont-focal.txt</text>')
    L.append(f'<rect x="90" y="356" width="220" height="44" rx="12" fill="{MER}"/>'
             f'<text x="200" y="384" font-size="16" fill="white" text-anchor="middle">Φ avant : 27,1</text>')
    L.append(f'<text x="380" y="386" font-size="24" font-weight="bold" fill="{VERT}" text-anchor="middle">→ ×31,6</text>')
    L.append(f'<rect x="450" y="356" width="220" height="44" rx="12" fill="{VERT}"/>'
             f'<text x="560" y="384" font-size="16" fill="white" text-anchor="middle">Φ après : 855,6</text>')
    L.append(f'<text x="380" y="428" font-size="12" fill="{PIERRE}" text-anchor="middle">porteurs : 4 transports vers le centre du tore</text>')
    L.append('</svg>')
    return "\n".join(L)


def main():
    for nom, svg in (("second-berceau.svg", berceau()), ("pont-focal.svg", focal())):
        with open(os.path.join(FIG, nom), "w", encoding="utf-8") as fh:
            fh.write(svg + "\n")
        print(f"OK : {nom}")
    print("FIGURES README OK — 2 images générées")


if __name__ == "__main__":
    main()
