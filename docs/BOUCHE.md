# La bouche, sans transformeur

## Deux tableaux

```
tissu scellé (.ratiss)          bouche (.bouche)
lien non orienté                arc orienté
force entière 10…100            compte, puis décharge
gelé dans le fichier publié     plastique, sauvé à part
répond à « de quoi on parle »   répond à « quel mot suit »
```

`suit(mer → noire)` n'est pas `intriqué(mer, noire)`.

Le vérificateur tient en trois lignes. Après l'éducation de « la mer noire » puis « la noire nuit » :

- l'arc `mer → noire` existe
- l'arc `noire → nuit` existe
- l'arc `noire → mer` n'existe pas, sauf si un texte l'a vraiment écrit

Le thème, lui, a le droit d'avoir les deux sens. C'est sa définition.

## Le calcul d'un pas

État : la liste des mots déjà dits. Pas un vecteur de 95 660 flottants. La liste.

1. On regarde les successeurs du dernier mot, et ceux de la paire des deux derniers si elle a été vue. Pas les 95 660 neurones.
2. Paire vue : 65 % trigramme, 35 % bigramme. Paire absente : bigramme seul.
3. À côté, le thème : voisins du tissu scellé, plus la fenêtre de 3 apprise pendant l'éducation. Chacun est ramené à un maximum de 1, pour qu'une force 100 ne mange pas un compte de 4.
4. `score = λ · ordre + (1 − λ) · thème`.
5. Softmax **sur les candidats qui ont un score**, pas sur tout le vocabulaire.
6. On pioche. `--glouton` prend le max, pour voir la boucle en face.

Pas de produit matriciel. Pas de RoPE. La position est la distance dans la liste, pas une rotation complexe. Si un jour la lumière fixe (1, 1/2, 1/4) perd contre une lumière apprise, **là** on pourra parler d'apprendre ces quelques coefficients. Pas avant. Et ce ne sera toujours pas 12 couches.

## Ce que le fichier contient

`FORMAT = RATISS_BOUCHE_V3`

```json
{
  "FORMAT": "RATISS_BOUCHE_V3",
  "lam": 0.75,
  "memoire": 8,
  "temperature": 0.7,
  "contraste": true,
  "registre_courant": "conte",
  "registres": {
    "conte": { "mer": { "noire": 4.0 }, "noire": { "nuit": 2.0 } }
  },
  "theme": { "mer": { "noire": 1.0, "la": 1.0 } },
  "chaines": [
    {
      "mots": ["la", "lune", "orbite", "autour", "de", "la", "terre"],
      "gele": true,
      "cles": ["lune", "orbite", "terre"],
      "enonce": "la lune orbite autour de la terre",
      "sha256": "…",
      "registre": "fait"
    }
  ],
  "meta": { "phrases": 0, "tokens": 0, "tours": 0, "decharges": 0 }
}
```

`.json` pour lire. `.bouche` pour le même JSON, gzippé : c'est le format de sortie recommandé. Il reste un texte. On peut l'ouvrir. Un GGUF, non.

Pourquoi pas un seul `.ratiss` qui contiendrait aussi la bouche : parce que le gel et le sceau du tissu disent « cette intrication-là est figée ». Y mélanger l'ordre, c'est re-cacher la panne dans le même fichier. Le berceau complet, c'est un dossier :

```
berceau/
  tissu.ratiss     thème, gelé
  bouche.bouche    ordre, plastique
  config.json      le plan
  top5.json        le chiffre, sur le texte tenu à l'écart
```

## Les registres

Un registre est une famille d'arcs. Pas un secteur.

| Registre | Ce qu'on y met | Comment on l'obtient |
|---|---|---|
| `ordre` | le flux par défaut | `--eduquer` sans précision |
| `conte` | narration | `--registre conte` |
| `dialogue` | tours question / réponse | l'organiseur de corpus insère `_q_` et `_r_` |
| `science` | prose scientifique | `--registre science` |
| `fait` | chemins gelés | `--faits` ou « apprends que » |

Au moment de parler, la bouche somme les registres. Un fait gelé à 100 reste plus fort qu'un compte de conte, sur son propre départ. Si plus tard les registres se marchent dessus (un conte qui répond à une question de physique), on filtrera par registre au lieu d'inventer une couche. Le filtre est une ligne. La couche est une année.

## Les secteurs, et pourquoi on n'en ajoute pas un par corpus

VIF, REFRAIN, SANCTUAIRE, ULTRA décrivent **combien de temps** une trace a le droit de vivre. Pas **de quoi** elle parle.

Ajouter un secteur `SCIENCE` à côté de `VIF` mélangerait une température et un sujet. La nuit ne saurait plus quoi faire.

Ce qui change selon le dataset :

- le **registre** des arcs (sujet)
- la **linéarisation** (comment un dialogue devient une suite)
- le **gel** ou non (un fait court se grave, une narration se compte)

Ce qui ne change pas :

- la loi « un seul arc, du mot vers le suivant »
- le top-5 comme juge
- le tissu scellé, qui n'est pas ré-entraîné ici

Plus tard, un arc très confirmé pourra **monter** de température (être vu souvent, passer une nuit, être gravé). Ce sera le secteur appliqué à l'arc, pas un secteur par fichier source. Ce dépôt ne le fait pas encore : le gel des faits est explicite, pas émergent. Mieux vaut un gel qu'on voit qu'une nuit qu'on devine.

## Le sanctuaire n'est pas la bouche

« explique la fusion » récite le texte écrit dans le `.ratiss`. C'est voulu. C'est un texte de quatre entrées, pas une génération. La v3 ne le fait plus passer pour une onde.

Si tu veux que « fusion » soit aussi un chemin, tu le graves :

```bash
python3 ratiss_v3.py cerveau/RatissOne.ratiss \
  --faits corpus/faits_jouet.txt --sauver bouche.json
```

Là, la bouche peut l'emprunter comme elle emprunte la lune. Le paragraphe du sanctuaire et le chemin gelé cohabitent. Ils ne sont pas la même mémoire.

## Étape 0

`config/bouche_etape0.json` est la bouche avant toute donnée.

Chez un LLM, l'étape 0 est un bruit : des flottants tirés, sinon le gradient est le même partout. Ici il n'y a pas de gradient partagé entre des neurones identiques. Un arc qui n'existe pas est un arc qui n'existe pas. Le mettre à zéro **est** l'initialisation correcte. Inventer des arcs au hasard ferait parler la bouche avant qu'elle ait rien vu, ce qui est précisément la panne qu'on vient de quitter.
