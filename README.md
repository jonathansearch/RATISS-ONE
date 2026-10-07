<div align="center">

<img src="images/logo-ratiss-labs.png" width="220" alt="RATISS Labs"/>

# ⚛️ RATISS-ONE — Réseaux de Neurones Intriqués + langage Ratum

**Un tissu vivant qui apprend par rencontres, un cerveau qui oublie bien, une bouche qui ne dit que ce qu'elle tient.**

[![License: MIT](https://img.shields.io/badge/License-MIT-teal.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-93%2F93-teal.svg)](tests_verdicts.py)
[![Programmes](https://img.shields.io/badge/Programmes-23-teal.svg)](tests_verdicts.py)
[![Ratum](https://img.shields.io/badge/Ratum-v1-teal.svg)](LANGAGE-RATUM.md)
[![Leçons](https://img.shields.io/badge/Le%C3%A7ons-11-teal.svg)](RNI-DEFINITION.md)
[![Données stockées](https://img.shields.io/badge/Donn%C3%A9es%20stock%C3%A9es-z%C3%A9ro-orange.svg)](RNI-DEFINITION.md)

*Par **RATISS Labs** — Jonathan Evina · Yaoundé 🇨🇲 · Licence MIT · reproductibilité publique voulue*

</div>

<img src="images/hero-cerveau.png" width="100%" alt="Le tissu éduqué : 13 neurones, 28 liens"/>

> **Résumé.** *RATISS-ONE est un programme de recherche ouvert : un réseau de
> neurones intriqué (RNI) — ni usine à prédictions, ni entrepôt de données —
> programmé dans un langage à mots français, **Ratum**. Le RNI apprend par
> rencontres sous une seule loi (ce qui se tient ensemble se renforce, ce qui
> se disjoint s'efface), entend le monde par une vraie oreille (Phonon-2),
> range ses souvenirs dans un cerveau à trois secteurs, et ne redit que ce
> qu'il tient — par une vraie bouche (Piper). 23 programmes, 93 contrôles
> verts, 17 leçons mesurées, zéro donnée stockée. Chaque affirmation ci-dessous
> se rejoue en une commande, sinon elle n'existe pas.*
>
> **Abstract (EN).** *RATISS-ONE is an open research program: an entangled
> neural network (RNI) — neither a prediction factory nor a data warehouse —
> programmed in a French-word language, **Ratum**. The RNI learns through
> encounters under a single law (what holds together strengthens, what comes
> apart fades), hears the world through a real ear (Phonon-2), files memories
> in a three-sector brain, and only speaks what it holds — through a real
> mouth (Piper). 23 programs, 93 green checks, 11 measured lessons, zero stored
> data. Every claim below replays in one command, or it does not exist.*

> *« On ne croit pas. On rejoue. » — le chef. (Et quand la mesure déplaît,
> on la publie quand même. 😇)*

---

## 📖 Sommaire

1. [La question](#-la-question) — 2. [En 30 secondes](#-en-30-secondes) —
3. [Le concept](#-le-concept) — 4. [La boucle](#-la-boucle-du-son-au-son) —
4. [Le cerveau](#-le-cerveau-un-entonnoir-qui-oublie-bien) —
6. [Le graphe](#-le-graphe-lire-le-cerveau-penser) —
7. [Démarrage rapide](#-démarrage-rapide) — 8. [Carte du dépôt](#-carte-du-dépôt) —
8. [Chiffres clés](#-chiffres-clés) — 10. [Ordre de lecture](#-ordre-de-lecture) —
9. [La méthode](#-la-méthode) — 12. [Feuille de route](#-feuille-de-route) —
10. [Arborescence](#-arborescence) — 14. [Citation, auteur, licence](#-citation-auteur-licence)

---

## ❓ La question

> **Peut-on comprendre sans stocker ?**

Ni bases de données, ni datasets : un **tissu** où le souvenir EST le chemin —
des neurones au destin lié, une loi d'apprentissage en mots, et des portes
bêtes (une oreille qui transcrit sans comprendre, une bouche qui parle sans
comprendre) autour d'un cœur intelligent (le tissu, qui comprend en résonnant).

Ce dépôt est la réponse mesurée, version par version : du jouet à 3 neurones
jusqu'au cerveau qui écoute JFK et raconte ce qu'il a retenu. Hypothèse de
recherche, pas résultat établi sur l'intelligence — mais chaque étape est
prouvée par des programmes qui tournent.

---

## ⚡ En 30 secondes

| 🧠 | Élément | Verdict mesuré |
|---|---|---|
| 🌱 `rni-simple.ratum` | 3 neurones, 5 rencontres | forme apprise 10 → **60/100**, étrangère **0** |
| 🔥 `rni-complexe.ratum` | 8 neurones, éducation en 4 phases | SOLEIL **90**, LUNE **90**, témoin ORAGE **0** |
| 🌊 `rni-interference.ratum` | 2 formes sans rien en commun | le nouveau **chasse l'ancien** (70 → 10) |
| 🧪 `jouets/` (v0.1) | 10 jouets, un par recoin du langage | seuils, pas, oubli, photo, choix, plafond, vagues, erreur nette |
| 📖 `vocabulaire.ratum` (v0.2) | 12 mots vrais + cousin + inconnu | **12/12 TIENT (80-90)**, cousin 40, inconnu 0 |
| 📏 `echelle/` (v0.3) | 300 neurones, 1200 liens, 50 motifs | **40/40 TIENT (75-85)**, témoins 0, 0,1 s |
| ⚖️ `v1-coexistence` (v1-loi) | symétrique vs asymétrique, même tissu | 10/10 ❌❌ → **52/52 ✅✅**, seuils 50→75→37 |
| 👂 `porte-voix/` (v1) | oreille RÉELLE Phonon-2 + pont → tissu | JFK transcrit **mot pour mot**, tissu : 22× hors vocabulaire (leçon 7) |
| 🦜 `parole.py` + `bouche/` | boucle audio → tissu → audio (Piper) | 4 mots **tenus à 90**, verdicts PARLÉS 4.9 s (leçon 8) |
| 🧠 `cerveau/` + `cerveau-demo.py` | crâne Python + pensée Ratum, secteurs VIF→REFRAIN→SANCTUAIRE | JFK live → 1 sanctuaire **f92**, résumé parlé 6 s (leçon 9) |
| 🇫🇷 `francais.ratum` + `cerveau-demo-fr.py` | route A : tissu + cerveau + bouche FRANÇAIS | 21/21 mot pour mot, sanctuaire **f92**, boucle 8.5 s (leçon 10) |
| 📚 `education/` (route B) | 37 phrases → 50 mots appris, 0 tissage manuel | **50/50 TIENT**, témoins 0, contrôles délie 3/10 → **0/50** (leçon 11) |
| ⚙️ `ratum.py` | interprète de référence | 24/24 programmes, **105/105 contrôles verts** |
| 📜 `LANGAGE-RATUM.md` | spec du langage | 18 relations, chacune expliquée |

---

## 🧵 Le concept

**Le constat** : on entraîne des géants sur des données qu'on stocke par
milliards. Ici, l'inverse : **le transcrit vit en RAM le temps d'un run
(comme une charge) et meurt ; seules les forces des liens persistent (comme
des synapses)**. La mémoire long terme du RNI, c'est le chemin — pas la
cargaison.

**La loi** (une seule, en mots, pas en formules) : *ce qui se tient ensemble
se renforce, ce qui se disjoint s'efface.* En v1 elle est asymétrique et
mesurée : `lie` = +10, `délie` = −3 — calibrés par l'expérience de
coexistence (le symétrique s'effondre 10/10, l'asymétrique tient 52/52).

**Le langage** : **Ratum** parle français (`tissu`, `neurone`, `lien`,
`rencontre`, `propager`, `renforcer`, `oublier`, `juger`…). Un programme
Ratum se lit comme une histoire d'éducation : on tisse, on rencontre, on
renforce, on oublie, on juge — et le verdict tombe : **TIENT** ou **ROMPT**.

**L'honnêteté radicale** : ce n'est PAS de la physique quantique (jamais de
qubits : des compteurs, des seuils et des nuits), PAS de la neurobiologie
(des compteurs à seuil, pas des cellules), et la saturation à 95 visible sur
le graphe est un vrai défaut publié tel quel — voir la section graphe.

---

## 🔁 La boucle : du son au son

<img src="images/boucle.png" width="100%" alt="La boucle : oreille, tissu, cerveau, bouche"/>

JFK parle 11 secondes → l'oreille transcrit mot pour mot → le tissu résonne
(4 mots tenus) → le cerveau trace et consolide (20 séquences → 1 sanctuaire)
→ la bouche dit le résumé (6 s d'audio). Boucle totale : **46 s**, dont
40 s d'oreille, 0.1 s de pensée, 2 s de bouche.

**Des portes bêtes, un cœur intelligent** — comme dans la tête (voir
`CERVEAU.md`) : Phonon transcrit sans comprendre, Piper parle sans
comprendre, **seul le tissu comprend** (leçon 7 : *transcrire n'est pas
comprendre*). Preuves : `preuves/sortie-cerveau-demo.txt`,
`bouche/cerveau.wav`.

---

## 🧠 Le cerveau : un entonnoir qui oublie bien

<img src="images/secteurs.png" width="100%" alt="Les secteurs : VIF, REFRAIN, SANCTUAIRE"/>

Le tissu est enfermé dans un crâne à trois secteurs (décision du chef :
**Python = le crâne** qui tient le graphe, **Ratum = la pensée** qui bat).
Chaque entrée devient une **trace** — quels mots, quel ordre, combien de
fois, quelle force — jamais la donnée brute.

| Secteur | Entrée | +/rencontre | −/nuit | Monte si… |
|---|---|---|---|---|
| **VIF** (l'instant) | 30 | 20 | 20 | 2 rencontres |
| **REFRAIN** (le chant) | 40 | 15 | 8 | 4 rencontres |
| **SANCTUAIRE** (le marbre) | 60 | 10 | 1 | sommet (jamais mort) |

Mesures live : 20 séquences entrent, 4 montent au refrain, **1 atteint le
sanctuaire** (`fellow americans ask`, f92) — la plus répétée, pas la
première ni la dernière. *La nuit ne comprend rien : elle efface — c'est
l'oubli qui fait la mémoire.* Doctrine complète : `cerveau/SECTEURS.md`.

---

## 🕸️ Le graphe : lire le cerveau penser

<img src="images/graphe-jfk.png" width="100%" alt="JFK dans le cerveau : chaque lien porte sa force mesurée"/>

Le graphe ci-dessus n'est pas un schéma : c'est **le tissu réel après la
démo** — 13 neurones (6 concepts au centre, 6 mots en anneau), 28 liens,
chaque lien portant sa force mesurée. En or : les 2 chaînes nées des mots
qui se SUIVENT (`fellow-americans-ask`).

**Lecture honnête** : l'éducation commune a saturé presque tous les liens à
**95** (vrai défaut, piste v2 : érosion même du marbre), tandis que les
liens de `homeland` — mot tissé mais jamais entendu — sont **morts à 0**
(pointillés gris). Le système montre ses forces ET ses morts : c'est ça,
une mesure.

> Ces figures sont régénérées depuis le code, jamais dessinées à la main :
> `python3 outils/figures.py` rejoue la démo hors-ligne, **assert** les
> nombres live (20 séq., 28 liens, sanctuaire f92), puis trace. Si la démo
> change, les figures refusent les vieux nombres.

---

## 🚀 Démarrage rapide

```bash
git clone https://github.com/jonathansearch/RATISS-ONE.git
cd RATISS-ONE
python3 ratum.py rni-simple.ratum        # le minimal : 3 neurones
python3 ratum.py rni-complexe.ratum      # l'éducation complète
python3 ratum.py rni-interference.ratum  # la vraie interférence
python3 tests_verdicts.py               # 93 contrôles (23 programmes + regen + 2 autotests)
python3 cerveau/autotest.py             # le cerveau seul, hors-ligne : CERVEAU OK
```

Zéro dépendance pour le cœur : que du Python standard. Déterministe : mêmes
entrées, mêmes sorties, toujours.

**La démo live** (oreille + bouche, ~46 s, protocole dans
`porte-voix/PROTOCOLE-OREILLE.md`) :

```bash
python3 cerveau-demo.py                 # JFK → secteurs → résumé parlé
```

---

## 🗺️ Carte du dépôt

| Dossier / fichier | Rôle | Preuve |
|---|---|---|
| `ratum.py` | interprète de référence (le berceau Python) | 21/21 programmes |
| `LANGAGE-RATUM.md` | spec : 18 relations expliquées en mots | — |
| `rni-*.ratum`, `jouets/`, `vocabulaire.ratum`, `echelle/` | les 3 âges : minimal → jouets → mots → échelle | `preuves/sortie-*.txt` |
| `porte-voix/` | l'oreille : Phonon-2 (EN) + faster-whisper (FR) + pont → tissu | `preuves/transcription-jfk.txt`, `-discours.txt` |
| `parole.py`, `bouche/` | la bouche : Piper + verdicts parlés | `bouche/verdicts.wav`, `cerveau.wav` |
| `cerveau/`, `cerveau-demo.py`, `-fr.py` | le crâne : graphe + secteurs + nuits (EN + FR) | `preuves/sortie-cerveau-demo(-fr).txt` |
| `education/` | l'école : corpus 37 phrases + éducateur → 50 mots | `vocabulaire50.ratum`, `images/constellation.png` |
| `RNI-DEFINITION.md` | la fiche scientifique : définition + 17 leçons + roadmap | — |
| `CERVEAU.md` | la carte d'inspiration cerveau → organes | — |
| `univers-focal/` | les 4 organes FOCAL (référence d'inspiration) | — |
| `outils/figures.py` | régénère les figures du README depuis les mesures | `images/*.png` |
| `tests_verdicts.py` | la batterie : 105 contrôles | `105/105 CONTRÔLES VERTS` |
| `MANIFESTE.json` | SHA-256 de chaque fichier (sceau du labo) | — |

---

## 📏 Chiffres clés

- **105/105 contrôles verts**, 24 programmes, 17 leçons (v0.1 → chaos v1)
- **Pipeline bilingue** : EN (JFK, boucle 46 s) + FR (discours, 21/21, boucle 8.5 s), sanctuaire f92 des deux côtés
- **50 mots éduqués** : 37 phrases → 63 neurones, 273 liens, courbe 38→49→50, 6 témoins à 0
- **300 neurones / 1200 liens** : 40/40 TIENT à 75-85 en 0,1 s (v0.3)
- **JFK mot pour mot** : 42 s à froid, 15-17 s à chaud, ~0.7× temps réel (oreille)
- **46 s** de son à son : oreille 40 s, pensée 0.1 s, bouche 2 s (cerveau)
- **Organes légers** : Phonon-2 0.16 Go + voix Piper 0.06 Go, zéro dataset
- **Zéro donnée stockée** : le brut meurt en RAM, seules les forces persistent

---

## 📖 Ordre de lecture

1. Ce README (la carte) → 2. `RNI-DEFINITION.md` (la fiche : définition + 17 leçons)
2. `LANGAGE-RATUM.md` (les 18 relations) → 4. `jouets/` (10 histoires d'éducation)
3. `CERVEAU.md` (la carte cerveau → organes) → 6. `cerveau/SECTEURS.md` (la doctrine)
4. `preuves/` (le carnet du labo : chaque sortie rejouable en une commande)

---

## 🔬 La méthode

- **R7 : une commande suffit.** Chaque résultat se rejoue (`python3
  tests_verdicts.py`, `python3 cerveau-demo.py`) — sinon il n'existe pas.
- **Les mots d'abord.** Pas de formules : le langage du labo, ce sont des
  phrases et des verdicts (TIENT/ROMPT).
- **Les échecs se publient.** Vocabulaire séquentiel (marge 0), échelle ×6
  (0 forts), interférence j13 v1 (a-b=10) : tous documentés, tous dépassés.
- **Simulation ≠ matériel.** Tout ici est calcul déterministe sur CPU ; si un
  jour le tissu touche une QPU, ce sera dit à voix haute.
- **Ce qu'on ne prétend PAS** : pas de quantique, pas de neurones
  biologiques, pas de conscience — des compteurs qui tiennent ou qui rompent.

---

## 🗺️ Feuille de route

- [x] **v0.1** — spec stabilisée sur 10 jouets (42/42 verts)
- [x] **v0.2** — vocabulaire tissé à la main (12 mots, cousin 40, inconnu 0)
- [x] **v0.3** — passage à l'échelle mesuré (300 nœuds, 40/40, 0,1 s)
- [x] **v1-loi** — pas asymétriques + seuils adaptatifs (52/52, seuils 50→75→37)
- [x] **v1-voix** — oreille simulée puis RÉELLE (JFK mot pour mot)
- [x] **v1-parole** — tissu anglais + bouche (verdicts parlés 4.9 s)
- [x] **v1-cerveau** — crâne + secteurs + séquences (sanctuaire f92, 81/81 verts)
- [x] **route A : français** — oreille faster-whisper + tissu + bouche FR (21/21, f92, 89/89 verts)
- [x] **route B : vocabulaire** — 37 phrases → 50 mots par éducation, 3 calibrages prouvés (93/93 verts)
- [x] **route C phases 1-2 : cœur v2** — (10,3) + élastique + ombre, nuits faucheuses
- [x] **CISE (vision du chef)** — vitesse = battements + énergie, étincelle, neurones mémoire figés, ULTRA-SECTEUR, (a) deux maisons
- [x] **tokenizer v1** — 4 règles sortie FR/EN, bouche testée, robinet à données, notebook Colab
- [x] **route C phase 3 : marbre + rétroaction** — gravure à la 3e relecture, relief 13, boucle fermée (103/103)
- [x] **route C phase 4 : marée** — tampon 50 + homéostasie (mer 60), tempête 70, relief 35 (104/104)
- [x] **route C phase 5 : chaos + rêve** — oubli honnête, émergence en 4 nuits, double dissociation (105/105)
- [ ] **route C phase 6** — docs
- [ ] **route D : v2 bas niveau** — interprète C, mêmes sorties au caractère près
- [ ] **toujours** — chaque affirmation rejouable en une commande

Feuille détaillée : `RNI-DEFINITION.md` §7.

---

## 📁 Arborescence

```
RATISS-ONE/
├── README.md                  # vous êtes ici
├── RNI-DEFINITION.md          # fiche scientifique + 17 leçons + roadmap
├── LANGAGE-RATUM.md           # spec Ratum : 18 relations
├── CERVEAU.md                 # carte cerveau → organes
├── MANIFESTE.json             # SHA-256 de chaque fichier
├── ratum.py                   # interprète de référence
├── tests_verdicts.py          # batterie : 93 contrôles
├── rni-simple / complexe / interference.ratum
├── vocabulaire.ratum  english.ratum  v1-coexistence.ratum
├── jouets/                    # j01 → j13 (seuils… séquences)
├── echelle/  v1/              # mesures v0.3 et v1-loi
├── porte-voix/                # oreille Phonon-2 + pont (PHONON.md, PROTOCOLE)
├── parole.py  parole-ecoute.ratum
├── bouche/                    # bouche Piper + verdicts.wav + cerveau.wav
├── cerveau/                   # crâne : secteurs.py, cerveau.py, autotest.py…
├── cerveau-demo.py            # démo live JFK → sanctuaire → résumé parlé
├── education/                 # route B : corpus + éducateur + vocabulaire50
├── univers-focal/             # 4 organes FOCAL (référence)
├── outils/                    # tisser_grand.py, figures.py
├── images/                    # logo + 4 figures régénérées
└── preuves/                   # carnet du labo : 13 sorties rejouables
```

---

## 📝 Citation, auteur, licence

```bibtex
@software{ratiss_one_2026,
  author  = {Jonathan Evina and RATISS Labs},
  title   = {RATISS-ONE : entangled neural networks + the Ratum language},
  year    = {2026},
  url     = {https://github.com/jonathansearch/RATISS-ONE},
  license = {MIT}
}
```

**Auteur** : Jonathan Evina — RATISS Labs, Yaoundé 🇨🇲 — ORCID
0009-0000-4092-5313 · **Licence** : MIT (voir `LICENSE`). Les organes
externes gardent leurs licences : poids Phonon-2 (CC-BY-4.0), Piper et voix
(GPL-3.0, organe téléchargeable, `.onnx` non distribué).

*« On ne croit pas. On rejoue. » — RATISS Labs* 🔁
