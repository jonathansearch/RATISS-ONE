# Quatre piliers

Ce que le dépôt sait faire sans gradient, et ce qu'il ne prétend pas encore.

Stdlib. Python 3.10+. Pas de PyTorch. Le `.ratiss` publié n'est pas ouvert en écriture : un hash avant / après le dit.

Les fonctions vivent dans `piliers/`. `Bouche` et `TissuScelle` les exposent. Les tests sont `tests/test_4piliers.py`.

## 1. Neurochirurgie, O(1)

Corriger un fait ne ré-entraîne pas le reste.

| Hôte | Où va l'écriture | Ce qui ne bouge pas |
|---|---|---|
| Bouche | une case `registres[registre][source][cible]` | les autres sources, les autres cibles |
| Tissu | un overlay `_delta[source][cible]` | la liste `liens`, le fichier, l'autre sens du lien gelé |

```python
bouche.editer_synapse("chat", "dort", 42)
bouche.supprimer_synapse("chat", "dort")

tissu.editer_synapse("chat", "dort", 99)   # n'écrit pas le .ratiss
delta = tissu.exporter_delta()             # à sauver à côté, si on veut le garder
tissu.appliquer_delta(delta)
```

`supprimer` sur le tissu masque l'arc au moment de la lecture (`liens_sortants`). L'adjacence gelée garde le même `id` et le même contenu. La lecture d'un autre mot rend les mêmes scores.

L'overlay est dirigé. `chat → dort` à 99 ne change pas `dort → chat`, qui reste la force gelée.

## 2. Audit du score

`expliquer_generation(token, contexte)` rejoue la même arithmétique que `scores`.

`Score = λ · Ordre + (1 − λ) · Thème`

- Ordre, paire vue : `0.65 · trigramme_norm + 0.35 · bigramme_norm`, avec les fréquences brutes dans l'arbre.
- Ordre, paire absente : le bigramme du dernier mot. Un trigramme manquant ne fait pas taire la bouche.
- Thème : pour chaque mot de la fenêtre, `lumière^distance · poids`. Lumière = 1, puis ½, puis ¼. La liste dit le nœud, la distance, le poids, la couche (`theme_bouche` ou `tissu`).

`resolution.formule_resolue` est l'égalité chiffrée. `identique_au_score` est faux si l'arbre et `scores()` divergent. Le test exige qu'il soit vrai.

Ce n'est pas une explication rédigée après coup. C'est la formule, les tables, et le nombre.

## 3. Épisode vif

`apprendre_phrase_live(phrase, registre="episodique")` fait une passe. Le contraste est coupé pendant cette passe : le fait neuf ne décharge pas les arcs déjà là. Il entre dans son registre, et dans le thème de fenêtre. Les deux sont lus tout de suite, parce que l'ordre somme les registres.

Sur le jouet : après `alpha beta gamma`, la marche gloutonne depuis `alpha beta` donne `gamma`. Aucun second tour, aucun fichier rechargé.

L'épisode est dans la bouche sauvée (`episodique`). Il n'entre pas dans le `.ratiss`.

## 4. Résonance

`raisonner_par_resonance(["soleil", "maree"])`.

Chaque source émet 1. À chaque saut, l'arc le plus fort transmet la moitié. Un arc plus faible transmet `½ × poids / poids_max`. On additionne les ondes. Le carrefour est le nœud qui n'est pas une source, qui a reçu au moins deux ondes, au-dessus du seuil, avec l'énergie la plus haute.

Pas de phrase dans l'appel. Si le graphe a `soleil—lune` et `maree—lune`, le carrefour est `lune` et son énergie vaut 1.0 (½ + ½). C'est `tests/test_4piliers.py`.

Sur `cerveau/RatissOne.ratiss`, ce n'est pas ce qui sort. Les chiffres sont dans `RAPPORT_EXPLORATION_4PILIERS.md`. La loi n'a pas été tordue pour les faire mentir.

## Où ils entrent dans l'entraînement

La méthode langue (`entrainement/entrainer_langue.py`, détaillée dans `docs/ORGANISATION_LANGUE.md`) ne les mélange pas :

| Pilier | Pas | Ce qu'elle refuse |
|---|---|---|
| Neurochirurgie | 7, retouches, après le compte | ré-entraîner pour changer une case |
| Audit | 9, sur l'écart seulement | une phrase écrite après coup |
| Épisode vif | 6, une passe, contraste coupé | un second tour qui décharge les rivaux |
| Résonance | pas dans la boucle | s'en servir comme perte ou comme professeur |
