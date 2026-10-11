# Organisation de l'entraînement de la langue

Une méthode. Dix pas. Le dataset change les fichiers, pas l'ordre.

Le script est `entrainement/entrainer_langue.py`. Il ne charge pas le graphe scellé. Il ne lance pas de GPU. Il n'écrit pas dans le `.ratiss`.

Les quatre piliers sont déjà dans la bouche. Cette page dit **où** chacun a le droit d'agir pendant l'entraînement, et où il n'a pas le droit.

## Les dix pas

Ils sont exécutés dans cet ordre, ou pas du tout. On n'échange pas 7 et 4.

| Pas | Nom | Fichier lu | Ce qui est écrit | Loi |
|---|---|---|---|---|
| 1 | oreille | la prose | des lignes, commentaires `#` ôtés | le mot, pas un BPE |
| 2 | séparation | `--ecart`, ou la queue si `--fraction` | `02_ecart.txt` | l'écart n'entre pas dans `eduquer` |
| 3 | étape 0 | `--charger` ou rien | une bouche vide | zéro arc, pas un bruit |
| 4 | prose | `01_education.txt` | registre demandé (`conte`, `dialogue`, `science`, `ordre`) | compte, N tours, décharge si elle est allumée |
| 5 | faits | `--faits` | registre `fait`, chaînes gelées | force 100, pas de décharge |
| 6 | épisodes | `--episodes` | registre `episodique` | **une** passe, contraste **coupé** |
| 7 | retouches | `--retouches` | une case `source → cible` | O(1), après le compte, le reste des cases ne bouge pas |
| 8 | top-5 | seulement `02_ecart.txt` | `mesures.json` | le texte vu n'est pas le juge |
| 9 | audit | les premières positions de l'écart | `audit.jsonl` | `Score = λ·Ordre + (1−λ)·Thème`, relu |
| 10 | dépôt | — | `bouche.bouche` et `ORGANISATION.txt` | le tissu n'est pas dans ce dossier |

`pipeline/03_entrainer.py` reste le pas 4 seul, si tu ne veux que le compte. La méthode est le pas 4 plus ce qui doit l'entourer pour que le chiffre et les piliers ne se marchent pas dessus.

## Deux dossiers, deux rôles

Le **corpus** est chez toi. Le **berceau** est ce que la méthode écrit. On ne mélange pas les deux.

```
corpus/                          ce que tu prépares, avant
  prince_jouet.txt               prose, registre conte
  tenu_a_lecart.txt              juge, jamais passé à eduquer
  faits_jouet.txt                vérités courtes, une par ligne
  episodes_jouet.txt             phrases vives, une par ligne
  retouches_jouet.txt            cases, après le compte
  dialogue_jouet.jsonl           tours, à linéariser avant

sortie/langue_jouet/             ce que la méthode dépose, après
  ORGANISATION.txt               l'ordre réel de cette exécution
  01_education.txt               les lignes comptées, pas une de plus
  02_ecart.txt                   les lignes jugées
  03_faits.txt                   les lignes gravées
  04_episodes.txt                les lignes vives
  05_retouches.txt               les cases
  bouche.bouche                  arcs, trigrammes, thème, chaînes, épisodes
  mesures.json                   top-5 par mode, hash du tissu
  audit.jsonl                    une formule par mot suivant
```

`01` à `05` sont des copies de travail. Si tu dois redire ce qui a été appris, tu lis ces fichiers, pas ta mémoire. Un commentaire d'en-tête dans le corpus (`# registre: conte`) n'est pas une phrase : l'oreille le jette.

Le tissu scellé reste où il était :

```
cerveau/RatissOne.ratiss         lecture seule
```

La méthode hash ce fichier avant et après si tu passes `--cerveau` (garantie R4-R7 d'immuabilité). Si le fichier est présent et valide, elle évalue également le mode `mixte_tissu` avec la loi de normalisation par le degré `ln(degre)` (qui étouffe les hubs syntaxiques comme `de`/`le`), permettant de mesurer conjointement la Bouche et le Tissu scellé purifié.

## Qui a le droit d'écrire où

| Mémoire | Qui l'écrit | Pendant quel pas | Interdit |
|---|---|---|---|
| arcs du registre de prose | `eduquer` | 4 | y verser un fait gelé ou un épisode |
| trigrammes du même registre | `eduquer` | 4 | les recalculer à part |
| thème de fenêtre | prose, et aussi l'épisode | 4 et 6 | le prendre pour un ordre |
| chaînes `fait` | `graver_chaine` | 5 | les passer dans la décharge |
| arcs `episodique` | `apprendre_phrase_live` | 6 | un second tour, une décharge |
| une case | `editer_synapse` / `supprimer_synapse` | 7 | un ré-entraînement pour corriger un mot |
| `.ratiss` | personne, ici | — | overlay, nuit, sanctuaire automatique |
| sanctuaire | la main, dans le tissu | — | un chapitre de roman |

L'épisode vif écrit aussi deux sens dans le thème, sur une fenêtre de 3. C'est voulu : le fait neuf est visible tout de suite. Comme le contraste est coupé, il n'abaisse pas les rivaux d'un autre départ. Un vocabulaire disjoint laisse les anciens scores bit à bit identiques. Un mot déjà vu peut monter d'un cran dans le thème : c'est l'ajout, pas l'oubli du reste.

La retouche arrive **après**. Elle gagne contre le compte. `editer globe verre 5` pose 5, même si le conte avait écrit autre chose. Elle ne relit pas les voisins.

## Séparation

Deux façons, une seule est la bonne quand tu as le choix.

1. **Deux fichiers.** `--education` et `--ecart`. C'est le cas du jouet : `prince_jouet.txt` et `tenu_a_lecart.txt`. Aucune ligne de l'un n'est dans l'autre.
2. **Une queue.** `--fraction 0.1` sans `--ecart`. Les dernières lignes du fichier sont l'écart, les premières sont l'éducation. Pas de tirage : un tirage dans le même chapitre fait mentir le top-5, parce que la phrase d'après a été vue.

On coupe avant le compte. On ne retire pas des phrases après coup.

Moins de 5 lignes : la méthode refuse la fraction. Elle ne devine pas un juge dans trois phrases.

## Registres

| Registre | Pas | Exemple de fichier |
|---|---|---|
| `conte` | 4, narration | Gutenberg, le prince |
| `dialogue` | 4, après l'organiseur | `_q_ … _r_ …` |
| `science` | 4, prose | Wikipédia, pas le sanctuaire |
| `ordre` | 4, si tu ne sais pas encore | le flux par défaut |
| `fait` | 5 seulement | `faits_jouet.txt` |
| `episodique` | 6 seulement | `episodes_jouet.txt` |

Au moment de parler, la bouche **somme** les registres. Un épisode est donc visible sans relancer le pas 4. Un fait gelé à 100 reste plus fort qu'un compte, sur son propre départ. On ne fusionne pas les familles dans un seul dictionnaire pour « simplifier ».

Le dialogue se linéarise avant, par `entrainement/organiser_corpus.py`. La méthode langue ne relit pas le JSONL. Elle lit le texte déjà en lignes. Voir `docs/ENTRAINEMENT.md` pour Gutenberg, OpenAssistant, et ce qu'on ne mélange pas le premier mois.

## Retouches

Une ligne, un verbe, des mots déjà coupés (l'oreille n'est pas rappelée ici : un mot, pas une phrase).

```
editer globe verre 5 conte
supprimer chat nuit
```

`editer SOURCE CIBLE POIDS [registre]`
`supprimer SOURCE CIBLE [registre]`

Le registre manquant est celui de `--registre` (la prose). Cinq sur `globe → verre` dans `conte` ne touche pas `episodique`, ni `chien → joue`.

Ce n'est pas le pas pour apprendre une phrase. Une phrase est un épisode, ou de la prose. Une retouche est une correction d'une case que tu as déjà décidé.

## Audit

Chaque ligne de `audit.jsonl` est un vrai mot suivant de l'écart, avec :

- le contexte (`hist`)
- le mot (`vrai`)
- `formule_resolue`, les nombres déjà substitués
- `identique_au_score` : faux si l'arbre et `scores()` divergent
- `mode_ordre` : `trigramme` (65 % / 35 %) ou `bigramme` (repli)

Les tables brutes de tous les successeurs ne sont pas recopiées dans ce fichier. Les fréquences du mot jugé, oui. C'est le certificat, pas un dump.

## Commande

Jouet du dépôt, sans ouvrir les 428 471 liens :

```bash
python3 entrainement/entrainer_langue.py \
  --education corpus/prince_jouet.txt \
  --ecart corpus/tenu_a_lecart.txt \
  --faits corpus/faits_jouet.txt \
  --episodes corpus/episodes_jouet.txt \
  --retouches corpus/retouches_jouet.txt \
  --registre conte \
  --tours 3 \
  --cerveau cerveau/RatissOne.ratiss \
  --sortie sortie/langue_jouet
```

`--cerveau` ne sert qu'au hash. Tu peux l'omettre.

Un seul fichier, queue de 10 % :

```bash
python3 entrainement/entrainer_langue.py \
  --education mon_texte.txt \
  --fraction 0.1 \
  --registre science \
  --tours 3 \
  --sortie sortie/science
```

Reprendre une bouche, sans remettre les tours à zéro dans un autre registre :

```bash
python3 entrainement/entrainer_langue.py \
  --charger sortie/langue_jouet/bouche.bouche \
  --education corpus/autre_prose.txt \
  --ecart corpus/autre_ecart.txt \
  --registre science \
  --tours 1 \
  --sortie sortie/langue_suite
```

`--charger` reprend les arcs. Le pas 4 ajoute. Il ne reconstruit pas le fichier depuis rien, et il ne réécrit pas le gel.

## Ce que cette méthode ne fait pas

- Elle ne choisit pas le dataset. Ça reste `docs/ENTRAINEMENT.md`.
- Elle ne crée pas un secteur par corpus.
- Elle ne met pas la résonance dans la boucle d'apprentissage. La résonance lit un graphe. Elle ne compte pas des mots. Sur le tissu scellé, la normalisation par le degré relègue les hubs (`de` passe derrière `lune`, `lune` au rang #2) : la résonance reste un mécanisme d'exploration conceptuelle et d'audit, pas un gradient d'apprentissage.
- Elle ne lance pas le contraste sur un épisode. Sinon le fait neuf déchargerait des rivaux qu'il n'a pas le droit de juger.
- Elle ne publie pas le top-5 du texte vu comme si c'était le juge.
- Elle s'arrête quand tu le décides, en relisant `mesures.json`. Trois tours, on mesure, on ne relit pas cinquante fois.

## Arrêt

Le chiffre qui compte est `modes.trigramme.top5` et `modes.mixte.top5` dans `mesures.json`, sur l'écart. S'ils ne montent plus d'un tour à l'autre, on s'arrête. Creuser la même prose fait boucler plus tôt. Ça n'invente pas les phrases qui n'y sont pas.
