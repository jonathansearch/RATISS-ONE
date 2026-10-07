#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUIRE LE LIVRE — génère les courbes (depuis les mesures réelles) puis
assemble le livre + la présentation (tout en ligne : zéro internet requis).
RATISS Labs · Le livre est sous CC-BY-SA-4.0 (voir LICENCE.md).

Usage : python3 livre/construire.py
Sortie : LIVRE OK — figures, livre et présentation reconstruits.
Loi du labo : pas de chiffres inventés — chaque point cite sa preuve.
"""
import base64
import os

RACINE = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(RACINE)
FIG = os.path.join(RACINE, "figures")
FONT = "font-family=\"Segoe UI, Verdana, sans-serif\""

# --- palette du livre ---
CREME, ENCRE, OR = "#FAF7F0", "#1A1A2E", "#C9A227"
MER, VIOLET, VERT = "#1B6CA8", "#7C3AED", "#1E9E6A"
PIERRE, ROUGE = "#6B7280", "#D64545"


def cadre(w, h, titre):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" {FONT}>',
            f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="16" fill="{CREME}" stroke="#E8E0D0" stroke-width="2"/>',
            f'<text x="{w // 2}" y="34" font-size="19" font-weight="bold" fill="{ENCRE}" text-anchor="middle">{titre}</text>']


def courbe(points, x0, y0, x1, y1, vmax, couleur, largeur=3, points_ronds=True, etiquettes=None):
    """Une courbe + ses points. points = [(label, valeur)]."""
    n = len(points)
    L = []
    for i, (label, v) in enumerate(points):
        x = x0 if n == 1 else x0 + (x1 - x0) * i / (n - 1)
        y = y1 - (y1 - y0) * v / vmax
        if i:
            L.append(f'<line x1="{px}" y1="{py}" x2="{x:.1f}" y2="{y:.1f}" stroke="{couleur}" stroke-width="{largeur}"/>')
        if points_ronds:
            L.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{couleur}" stroke="#fff" stroke-width="2"/>')
        L.append(f'<text x="{x:.1f}" y="{y - 10:.1f}" font-size="11" font-weight="bold" fill="{couleur}" text-anchor="middle">{v}</text>')
        L.append(f'<text x="{x:.1f}" y="{y1 + 18}" font-size="10" fill="{ENCRE}" text-anchor="middle">{label}</text>')
        px, py = f"{x:.1f}", f"{y:.1f}"
    if etiquettes:
        for i, t in enumerate(etiquettes):
            x = x0 if n == 1 else x0 + (x1 - x0) * i / (n - 1)
            L.append(f'<text x="{x:.1f}" y="{y1 + 32}" font-size="9" fill="{PIERRE}" text-anchor="middle">{t}</text>')
    return L


def g_batterie():
    # Sources : roadmap RNI-DEFINITION.md §7 + sorties batterie (42 → 114).
    L = cadre(780, 320, "📈 La batterie : 42 → 114 contrôles (avec le creux honnête)")
    pts = [("v0.1", 42), ("cerveau", 81), ("route A", 89), ("route B", 93),
           ("creux C", 62), ("route C", 93), ("CISE", 101), ("tok", 102),
           ("marbre", 103), ("marée", 104), ("chaos", 105), ("livre", 106),
           ("route D", 107), ("pont FOCAL", 108),
           ("R5", 109), ("direct", 110),
           ("dialogue", 111), ("masse", 112),
           ("colab1h", 113),
           ("puissance", 114)]
    L += courbe(pts, 50, 60, 730, 250, 110, VERT, etiquettes=
                ["6 oct."] * 5 + ["7 oct."] * 15)
    L.append(f'<text x="390" y="300" font-size="11" font-style="italic" fill="{PIERRE}" text-anchor="middle">'
             "Le creux (62/93) : la loi v2 casse tout, le monde s'ajuste, tout remonte — sans toucher une règle.</text>")
    return L


def g_ecole():
    # Sources : EDUCATION.md + leçon 11 (courbe 38→49→50, MUNIR 51→58→60).
    L = cadre(660, 300, "📚 L'école : 38 → 49 → 50 mots en 3 rounds")
    L += courbe([("round 1", 38), ("round 2", 49), ("round 3", 50)],
                70, 60, 590, 220, 60, VERT, etiquettes=["37 phrases", "+ éducation", "50/50 TIENT"])
    L += courbe([("r1", 51), ("r2", 58), ("r3", 60)], 70, 60, 590, 220, 60, VIOLET)
    L.append(f'<rect x="460" y="70" width="150" height="52" rx="8" fill="#fff" stroke="#E8E0D0"/>')
    L.append(f'<text x="470" y="90" font-size="11" fill="{VERT}">● mots qui tiennent</text>')
    L.append(f'<text x="470" y="110" font-size="11" fill="{VIOLET}">● cousin MUNIR (deviné)</text>')
    L.append(f'<text x="330" y="280" font-size="11" font-style="italic" fill="{PIERRE}" text-anchor="middle">'
             "6 témoins à 0 tout du long — l'école n'invente rien (route B, 93/93).</text>")
    return L


def g_relief():
    # Sources : sortie-marbre.txt (relief 13) + sortie-maree.txt (relief 35).
    L = cadre(560, 290, "🗻 Le relief : 13 → 35 (le creusement)")
    for i, (quoi, v, coul, sous) in enumerate([("marbre (v4)", 13, PIERRE, "A f100 · B f87"),
                                               ("marée (v5)", 35, OR, "A f100 · B f65")]):
        x = 90 + i * 220
        h = 150 * v / 40
        L.append(f'<rect x="{x}" y="{220 - h:.0f}" width="130" height="{h:.0f}" rx="10" fill="{coul}"/>')
        L.append(f'<text x="{x + 65}" y="{208 - h:.0f}" font-size="22" font-weight="bold" fill="{ENCRE}" text-anchor="middle">{v}</text>')
        L.append(f'<text x="{x + 65}" y="242" font-size="12" font-weight="bold" fill="{ENCRE}" text-anchor="middle">{quoi}</text>')
        L.append(f'<text x="{x + 65}" y="260" font-size="11" fill="{PIERRE}" text-anchor="middle">{sous}</text>')
    return L


def g_mer():
    # Source : la LOI elle-même (rejouée ici) + sortie-maree.txt (B f65 à 5 nuits).
    L = cadre(720, 310, "🌊 L'homéostasie : le témoin coule à la mer, la statue reste")
    b, f = [92], 92
    for _ in range(8):  # perte = 1 + (f-60)//4, plancher 60 (secteurs.py)
        f = max(60, f - (1 + (f - 60) // 4))
        b.append(f)
    assert b[5] == 65, b  # la mesure témoin : f65 après 5 nuits
    L += courbe([(f"n{i}", v) for i, v in enumerate(b)], 60, 60, 660, 230, 110, MER,
                etiquettes=[""] * 9)
    L += courbe([(f"n{i}", 100) for i in range(9)], 60, 60, 660, 230, 110, OR, points_ronds=False)
    L.append(f'<line x1="60" y1="{230 - 170 * 60 / 110:.0f}" x2="660" y2="{230 - 170 * 60 / 110:.0f}" stroke="{VERT}" stroke-width="2" stroke-dasharray="7 5"/>')
    for txt, y, coul in [("★ statue gravée f100 (nuit 0)", 76, OR),
                         ("● témoin B : 92 → 60 (la mer)", 96, MER),
                         ("- - niveau de la mer : 60, jamais en dessous", 116, VERT)]:
        L.append(f'<text x="480" y="{y}" font-size="11" font-weight="bold" fill="{coul}">{txt}</text>')
    L.append(f'<text x="360" y="292" font-size="11" font-style="italic" fill="{PIERRE}" text-anchor="middle">'
             "Courbe rejouée depuis la loi (pas de chiffres tapés à la main) — B touche la mer à la 8e nuit.</text>")
    return L


def g_saturation():
    # Sources : leçon 11 (90 uniforme) → leçon 12 (74-94) → leçon 16 (100 / 60).
    L = cadre(660, 290, "⚖️ La saturation : du désert plat au paysage")
    L.append(f'<rect x="70" y="{200 - 150 * 90 / 110:.0f}" width="120" height="{150 * 90 / 110:.0f}" rx="10" fill="{ROUGE}"/>')
    L.append(f'<text x="130" y="60" font-size="13" font-weight="bold" fill="{ENCRE}" text-anchor="middle">v1 : 90 partout</text>')
    L.append(f'<text x="130" y="222" font-size="11" fill="{PIERRE}" text-anchor="middle">le désert plat</text>')
    y74, y94 = 200 - 150 * 74 / 110, 200 - 150 * 94 / 110
    L.append(f'<rect x="270" y="{y94:.0f}" width="120" height="{y74 - y94:.0f}" rx="10" fill="{VIOLET}"/>')
    L.append(f'<text x="330" y="60" font-size="13" font-weight="bold" fill="{ENCRE}" text-anchor="middle">v2 : 74 – 94</text>')
    L.append(f'<text x="330" y="222" font-size="11" fill="{PIERRE}" text-anchor="middle">atténuée, pas vaincue</text>')
    for x, v, coul in [(470, 100, OR), (540, 60, MER)]:
        h = 150 * v / 110
        L.append(f'<rect x="{x}" y="{200 - h:.0f}" width="60" height="{h:.0f}" rx="8" fill="{coul}"/>')
        L.append(f'<text x="{x + 30}" y="{190 - h:.0f}" font-size="12" font-weight="bold" fill="{ENCRE}" text-anchor="middle">{v}</text>')
    L.append(f'<text x="530" y="60" font-size="13" font-weight="bold" fill="{ENCRE}" text-anchor="middle">v5 : 100 / 60</text>')
    L.append(f'<text x="530" y="222" font-size="11" fill="{PIERRE}" text-anchor="middle">la statue + la mer</text>')
    L.append(f'<text x="330" y="268" font-size="11" font-style="italic" fill="{PIERRE}" text-anchor="middle">'
             "Le relief naît de l'oubli sélectif, pas d'un réglage (leçons 11 → 12 → 16).</text>")
    return L


GENERER = {"g_batterie": g_batterie, "g_ecole": g_ecole, "g_relief": g_relief,
           "g_mer": g_mer, "g_saturation": g_saturation}


def construire():
    os.makedirs(FIG, exist_ok=True)
    for nom, fn in GENERER.items():
        with open(os.path.join(FIG, nom + ".svg"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(fn()) + "\n</svg>\n")

    def image(nom):
        with open(os.path.join(DEPOT, "images", nom + ".png"), "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        return (f'<img src="data:image/png;base64,{b64}" alt="{nom}" '
                f'style="max-width:100%;border-radius:12px"/>')

    def audio(nom, legende):
        with open(os.path.join(DEPOT, "bouche", nom + ".wav"), "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        return (f'<div class="audio"><p>🔊 {legende}</p><audio controls '
                f'src="data:audio/wav;base64,{b64}"></audio></div>')

    audios = {
        "tokenizer": "Le tokenizer v1 dit sa première phrase (EN).",
        "marbre": "Le gravé parle après 5 nuits (EN).",
        "tempete": "La statue parle après la tempête — même phrase (EN).",
        "chaos": "L'élue du chaos, sauvée par le rêve (EN).",
    }
    n_fig = 0
    for modele, sortie in [("modele-livre.html", "index.html"),
                           ("modele-pres.html", "presentation.html")]:
        with open(os.path.join(RACINE, modele), encoding="utf-8") as fh:
            page = fh.read()
        while "{{FIG:" in page:
            deb = page.index("{{FIG:")
            fin = page.index("}}", deb)
            nom = page[deb + 6:fin]
            with open(os.path.join(FIG, nom + ".svg"), encoding="utf-8") as fh:
                page = page[:deb] + fh.read() + page[fin + 2:]
            n_fig += 1
        while "{{IMG:" in page:
            deb = page.index("{{IMG:")
            fin = page.index("}}", deb)
            page = page[:deb] + image(page[deb + 6:fin]) + page[fin + 2:]
            n_fig += 1
        while "{{WAV:" in page:
            deb = page.index("{{WAV:")
            fin = page.index("}}", deb)
            nom = page[deb + 6:fin]
            page = page[:deb] + audio("preuve-" + nom, audios[nom]) + page[fin + 2:]
            n_fig += 1
        with open(os.path.join(RACINE, sortie), "w", encoding="utf-8") as fh:
            fh.write(page)
    print(f"LIVRE OK — {len(GENERER)} courbes générées, {n_fig} figures cousues, livre + présentation construits")
    return 0


if __name__ == "__main__":
    raise SystemExit(construire())
