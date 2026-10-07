# 📚 EDUCATION.md — grandir par phrases, pas par tissage (route B)

**RATISS Labs · 6 octobre 2026 · MIT**

> On ne tisse plus à la main : on RACONTE des phrases, et le tissu grandit.
> 37 phrases, 50 mots appris, 6 témoins dehors — et la preuve que chaque
> régime d'éducation exige son calibrage (leçon 11).

## 1. Le protocole (rejouable en une commande)

```bash
python3 education/eduquer.py   # 37 phrases x3 rounds + 2 nuits -> vocabulaire50.ratum
```

1. **Graine** : le Cerveau FR éduqué (13 neurones, 26 liens, 5 mots tenus).
2. **Naissances** : chaque phrase fait naître ses nœuds et liens manquants
   (force 10, la naissance — jamais renforcé avant d'exister).
3. **Round** : pour chaque phrase, `rencontre PHRASE + propager +
   renforcer lie 10 delie 0 + repos`. Trois rounds.
4. **Nuits** : `oublier` x2 (le seul effacement du protocole).
5. **Motifs hérités** : chaque mot tient à son ancre (paire, verdict) et à
   son compagnon le plus fréquent (triple, richesse). Zéro choix manuel.
6. **Export** : `vocabulaire50.ratum` — le tissu final en pur Ratum,
   régénéré avant chaque batterie (déterministe : tout est trié).

Corpus : `education/corpus.txt` — 5 constellations (VILLAGE, DEVOIR, NATURE,
ESPRIT, PONTS), chaque mot nouveau exactement 3 fois avec son ancre.

## 2. Les mesures

| Expérience | Bilan (seuil 60) | Témoins (seuil 20) |
|---|---|---|
| rounds=1, délie 0 | **38/50** | 6/6 dehors |
| rounds=2, délie 0 | **49/50** (ne manque que MUNIR=58) | 6/6 dehors |
| rounds=3, délie 0 (protocole) | **50/50** | 6/6 dehors |
| rounds=4, délie 0 | 50/50 (plafond atteint) | 6/6 dehors |
| rounds=3, **délie 3** (loi j11) | **0/50** (tout effacé) | 6/6 dehors |
| rounds=3, **délie 10** (défaut) | **0/50** (tout effacé) | 6/6 dehors |
| rounds=3, nuits=5 (érosion) | 49/50 (MUNIR 60→47 tombe) | 6/6 dehors |

Preuves : `preuves/sortie-education.txt` (protocole),
`preuves/sortie-education-controles.txt` (toutes les variantes),
`preuves/sortie-vocabulaire50.txt` (export rejoué).
Tissu final : 63 neurones, 273 liens, force moyenne 86, 261 liens forts.

Courbe d'apprentissage : les mots à ancres partagées (ponts : soleil, livre,
porte, feu, nuit, matin, main, chemin, temps…) apprennent en 2 rounds ; le
cousin MUNIR met 3 rounds (51 → 58 → 60) — *le cousin rejoint les amis*.

## 3. Trois calibrages, trois usages (résultat central)

La loi Ratum n'a pas UNE bonne valeur : chaque régime exige la sienne,
et les contrôles le prouvent par l'échec :

| Calibrage | Usage | Preuve |
|---|---|---|
| `renforcer` 10/10 (défaut) | éducation COMMUNE (tout actif ensemble) | EN/FR : 81-90, témoins 0 |
| `renforcer lie 10 delie 3` | COEXISTENCE de 2 formes (j11) | 52/52 TIENT (leçon 5) |
| `renforcer lie 10 delie 0` | éducation SÉLECTIVE (phrases) | 50/50 (cette route) |

Avec délie 3 ou 10, chaque phrase efface les 36 autres (0/50) : l'oubli
catastrophique, mesuré, pas théorisé. Règle : *le jour grave, la nuit
efface — jamais l'inverse.* La loi j11 (10,3) n'est pas universelle :
c'est le calibrage de SON régime, pas de tous.

## 4. La saturation, publiée telle quelle (honnêteté)

Au round 3, les 50 paires valent EXACTEMENT 90 et les 5 familles aussi :
la propagation (+10 aux voisins actifs) pousse tout au plafond 100, les
2 nuits ramènent à 90. Le tissu juge juste (50/50, témoins 0) mais ne
nuance plus : tout ce qui est appris vaut 90.

Ce n'est pas caché, c'est mesuré (histogramme des forces dans le log :
261 liens à 80-100, 5 à 20-39, 7 à 0-19). Deux causes : corpus uniforme
(chaque mot x3 → mêmes forces) et propagation sans concurrence. Pistes
route C : érosion du marbre, compétition entre liens, fréquences variées.

## 5. Rejouer et voir

```bash
python3 education/eduquer.py --delie 10    # le wipe-out (0/50)
python3 education/eduquer.py --rounds 1    # l'enfance (38/50)
python3 education/figures_vocab.py          # images/constellation.png
```

## 6. Limites dites à voix haute

1. Corpus artisanal (37 phrases écrites à la main) : l'éducation est réelle,
   le monde ne l'est pas encore.
2. Fenêtres = phrases prédécoupées : le découpage libre viendra en route C.
3. Saturation uniforme à 90 (section 4) : le défaut publié de cette route.
4. 50 mots, 1 langue : l'échelle et le bilinguisme restent devant.

## 7. Recalibrage route C (7 oct. 2026) — on ajuste le monde, pas la règle

Le cœur v2 ((10,3) partout, élasticité, ombre, `nettoyer`) a fait tomber B
à 42/50. Règle du chef : on ne touche pas la loi, on ajuste le monde.
Monde ajusté : corpus 39 phrases (+2 COEUR où les 4 ancres + unir battent
ensemble — la sommation multi-sources traverse l'ombre), 5 rounds,
graine 30×TOUT (ponts à 89), seuil 40 pour voix (pont unique),
UNE SEULE vague par phrase (trois vagues = tout co-actif, 45 paires à 94
pile, sélectivité morte), motifs nommés AVANT la nuit (nommer protège de
la faucheuse), nuits via `cerveau.nuit()` (oublier + `nettoyer`).

Résultat : **50/50 + 6/6**, MUNIR 39 → **74**, paires 74-94 (3 à 74,
2 à 76, 40 à 92-94), témoins à 4, familles 12-85, forces 7/0/4/32/235.
Courbe d'apprentissage v2 : 4 → 20 → 43 → 50 (rounds 1/2/3/5 —
progressive, l'élasticité ralentit le départ). Érosion : 5 nuits (oublier 3)
tiennent encore 50/50 — les nuits douces pardonnent. La faucheuse passe :
2 liens morts nuit 1, 0 nuit 2.

**La falaise délie** (mesurée 7 oct., `--delie D`) : délie 0 → 50/50 ;
délie 1 → 0/50 (202 liens fauchés) ; 2, 3, 5, 10 → 0/50. Entre 0 et 1 il
n'y a pas de pente : l'éducation sélective exige délie 0, aucun compromis
« doux » ne survit. Zéro neurones morts même sous délie 10 : tous nommés,
tous protégés. Tranché (a) le 7 oct. : deux maisons (école délie 0, vie (10,3)).

Saturation : atténuée (74-94 au lieu de 90 pile, familles 12-85) mais pas
vaincue — 235 liens au sommet. Le marbre (phase 3) viendra creuser.

## 6. La masse (7 oct., leçon 23)

L'école monte à l'échelle Colab : `education-massive/generer_masse.py`
(50 mots vrais, seed 7) + `eduquer_masse.py` (streaming + nuit/lot).
Mesuré : 250 000 séquences en ~70 s, RAM 12 Mo stables, sanctuaire
« amis peuple enfants ». 5M ≈ 25 min sur Colab (notebook §2b). Les
fichiers lourds ne sont jamais commis (doctrine : la masse vit sur Colab).

## 7. Le programme 1h (7 oct., leçon 24)

`education-massive/masse-5M.jsonl.gz` (5M, 35,7 Mo, sha pinné au
notebook) + `colab-1h.ipynb` : 5M du fichier + 5M fraîches seed 8, lots
200k, ~55 min sur Colab gratuit, bilan parlé en option. Validé 1M en
local (327 s, 13 Mo). Le GPU est déclaré inutile par écrit : CPU pur.

## 8. Le programme puissance 300M (7 oct., leçon 25)

Profilage : 88 % du temps partait dans l'interprète Ratum reconstruit à
chaque séquence. Le battement est fusionné (`Cerveau.rapide` : rencontre /
propager / renforcer calculés directement — MÊMES maths, prouvé identique
sur 50k : `preuves/equivalence-rapide.txt`, pin batterie `305e8b21042704bb`).
Données en binaire (3 octets/séquence, même flux seed 7 : `binaire_masse.py`),
100M en RAM (300 Mo), 3 époques : 300M écoutes ≈ 56 min, ~100 000/s.
Validé 30M : 318 s, 98 Mo (`preuves/sortie-masse-30M.txt`). Fichier lourd
30M (58,3 Mo, sha pinné au rapport) : régénérable, hors dépôt.

## 9. Le cerveau fortifié (7 oct., leçon 26)

Question du chef : où va le résultat ? `Cerveau.graver(chemin)` sauve
graphe + secteurs + tampon + compteur (les charges, éphémères, restent
dehors — doctrine) ; `Cerveau.relire(chemin)` réveille à l'identique
(reprise exacte prouvée : `preuves/graver-relire.txt`). Nos poids : ~1 Ko
(des relations, pas des gigas de sable). L'éducateur grave en fin de run
(`--graver`) et reprend (`--relire`, les écoutes continuent) ; le notebook
télécharge le fortifié (1 clic) ou le pousse sur Drive.

## 10. Le relais (7 oct., leçon 27)

`--relais CHEMIN` : à chaque lot (chaque nuit), le cerveau est gravé à
CHEMIN (écrasé, ~1 Ko). Sur Colab gratuit (coupure possible), le relais
vit sur le Drive : on ne perd jamais plus d'un lot, et `--relire` repart
du dernier. Le notebook monte le Drive, fait `git pull` (maj du code),
photographie chaque lot, puis copie le fortifié daté + bilan + voix.

## 11. Le retour (7 oct., leçon 28)

Le chef pousse `cerveau/cerveau.zip` : le labo réveille le fortifié
(300M pile, sanctuaire « amis patrie pays ») et le relit dans la batterie
(pinné : 300 000 000 + top sanctuaire). La voix du bilan est archivée
(`preuves/bilan-300M.wav`, 9,5 s). Boucle fermée : Colab muscle, le
fichier ramène, le dépôt réveille et vérifie.

## 12. L'école manuelle (7 oct., leçon 30)

Pas de LLM dans le système (décision du chef) : on quantifie nous-mêmes.
`education-manuelle/convertisseur_ud.py` boit 14 450 phrases UD françaises
annotées et sort un fragment CISE sur mesure (238 mots, 222 liens, 12
motifs-relations, loi force = min(100, 10 x rencontres)), poussé au
cerveau figé puis figé à l'éclair : 247 nerfs, 260 filaments, 300M
d'écoutes et sanctuaire intacts. Règles : topk=5/mot, marbre non
réécrit, R5 (pas d'écoutes), pas de nouvelles oreilles.

## 13. Le remix (7 oct., leçon 31)

`--tours 100 --paires 500` : chaque tour brasse TOUT le réservoir UD
(108 855 paires, graine reproductible), en boit 500, soude (motifs en
UNION, marbre épargné) et fige. En 88 s : 15 549 nerfs, 39 785 filaments,
36 % du réservoir bu, 300M et sanctuaire intacts. La saturation (épargnés
croissants) mesure l'absorption. Bonus : R-ULTRA ne nomme que les motifs
nommables (« la bouche ne dit que ce qu'elle peut nommer »).

## 14. Le fond du verre (7 oct., leçon 32)

`--jusquau-fond` : le cerveau est le registre (sue = le lien existe, marbre
respecté), le reste est brassé (graine) puis vidé par vagues jusqu'à 0
restant (terminaison garantie). 33 vagues en 48 s : 24 639 nerfs,
105 349 filaments, 105 313/105 313 recomptées indépendamment. Prouvé :
l'ordre des vagues ne change rien (même graphe final).

## 15. L'école de l'oreille (7 oct., leçon 34)

`--oreille` : le cerveau apprend les mots qu'il a déjà en nerfs
(lemme direct + formes fléchies, la plus fréquente gagne). L'école garde
la priorité (`mots_connus` intact) ; battement par motifs temporaires
(jamais figés, jamais gravés) ; nerf mort = sourd (garde anti-fantôme).
24 638 mots + 16 370 formes en 5 s — et le rêve comprend les nouveaux.

## 16. L'école de la bouche (7 oct., leçon 35)

`--bouche` : le cerveau apprend comment chaque lien tenu se parle
(relation + dépendant + natures), tissu intact. Le constructeur assemble
des noyaux sujet-verbe-objet (+ épithète), ordre français, style
télégraphique (zéro LLM) : R-CONSTRUCTEUR — chaque lien parlé est tenu
(force >= 20), sinon la bouche se tait. 884/2067 verbes parlent.

## 17. L'école de grammaire (7 oct., leçon 36)

`--grammaire` : les articles deviennent de vrais nerfs (injectés + figés,
motif MARTICLES) et les accords s'apprennent en un passage FEATS (genres,
nombres, flexions, adjectifs, présent 3e, déterminants observés). `parler`
habille le noyau tenu : articles, accords, conjugaison — 100 % observé,
sinon règle documentée + flag `appris`. Amendement : l'expansion saute
les petits mots (la colle ne détourne plus les noyaux).
