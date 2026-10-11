# Rapport d'exploration — 4 piliers

Jonathan Evina · RATISS Labs · mesure du 2026-10-11. CPU, stdlib, `python3 -m unittest tests.test_4piliers tests.test_bouche` : 21 tests, OK, 3,3 s.

Le `.ratiss` n'a pas été réécrit. Les piliers 1 à 3 tiennent. Le pilier 4 tient sur un graphe causal, et il ne fait pas sortir `lune` en tête sur le tissu scellé. On ne change pas la loi pour le forcer.

## Ce qui tient

| Pilier | Preuve | Chiffre |
|---|---|---|
| Synapse O(1), bouche | `chat → dort` passe à 42. `chien → joue` et `scores(["chien"])` restent égaux | 0 arc voisin modifié |
| Synapse O(1), tissu | overlay. `id` de la liste d'adjacence inchangé, `len(liens)` inchangé, SHA-256 du fichier inchangé. `chien` inchangé. `chat → nuit` reste 8 quand `chat → dort` passe à 99. Le sens inverse `dort → chat` reste 10 | 1 case de delta |
| Audit | `identique_au_score` vrai. Trigramme vu : 65 % / 35 % et fréquences brutes. Paire absente : repli bigramme, poids bigramme 1 | écart ≤ 1e-9 |
| Épisode vif | `alpha beta gamma` en une passe, 0 décharge. Le registre `ordre` et le thème de `chat` sont intacts. Glouton depuis `alpha beta` → `gamma`. Relecture du JSON : pareil | 1 passe |
| Résonance, graphe causal | `soleil—lune`, `maree—lune`, sans phrase. Carrefour `lune`, énergie 1.0. `nuit` reçoit 0.5 par les deux ondes et arrive deuxième. `chaleur`, une seule onde, n'est pas un carrefour | ½ + ½ |
| Langue, jouet | `le chat` → `mange`. Petit Prince glouton depuis `le petit prince` : `aimait sa rose vivait sous un globe` | top local du conte |

`apprendre_phrase_live("le soleil reveille la rose du prince")` puis glouton depuis `le soleil` : `reveille la rose du prince etait`. Le `etait` n'est pas inventé : il est déjà dans le conte (`la rose du prince etait unique`). Les registres se somment. C'est la loi déjà écrite, pas un nouveau miracle.

## Ce qui coince

Pilier 4, sur `cerveau/RatissOne.ratiss` (95 660 neurones, 428 471 liens), appel :

```text
raisonner_par_resonance(["soleil", "maree"], seuil=0.1, max_sauts=2)
```

Mesure : 0,95 s, 97 expansions, pas de troncature, 23 915 nœuds au-dessus du seuil touchés par les deux ondes.

| Rang | Nœud | Énergie | Sauts |
|---|---|---|---|
| 1 | de | 2,405 | 1 |
| 2 | le | 1,874 | 1 |
| 77 | la | 1,258 | 2 |
| 943 | lune | 0,793 | 2 |
| 5867 | gravite | 0,405 | 2 |

`lune` et `gravite` reçoivent bien les deux ondes. Elles ne gagnent pas.

Le goulet est topologique, pas une boucle infinie.

- Il n'y a pas d'arc direct `soleil—lune` ni `maree—lune` dans le gel. Les chemins de longueur 2 passent par `de`, `le`, `a`, `la` (degrés de 2 000 à 20 000).
- La loi transmet `½ × poids / poids_max` et **ne divise pas par le degré**. C'est la même ombre que la lumière du tissu : chaque voisin du plus fort arc reçoit la moitié, les hubs compris.
- À un saut, le carrefour est déjà `le` (0,65), puis `a` et `de` (0,35). `lune` n'est pas voisine. Aucun seuil ne la fera passer devant un hub atteint plus tôt et plus fort.
- À deux sauts, l'énergie des hubs reflue dans presque tout le lexique. 23 915 carrefours : le signal est noyé, pas absent.

Forcer un filtre de mots grammaticaux dans le défaut aurait fait gagner un autre nœud et aurait caché la mesure. Ce n'est pas fait.

## Options, sans en habiller une en résultat

1. **Graphe causal séparé.** Le pilier 4 est déjà vrai dès que les arcs existent (`soleil—lune`, `maree—lune` ou `lune—gravite`). On les pose avec le pilier 1 (overlay) ou le pilier 3 (une phrase vive, contraste coupé). On ne les déduit pas du gel cooccurrent.
2. **Liste fermée explicite, en regard, pas à la place.** Recalculer le carrefour en ignorant `de le la un a et au du`. Le publier comme seconde colonne. Seulement si, sur un texte tenu à l'écart, le rang des noms pleins monte sans faire apparaître le mot qu'on espérait par construction.
3. **Poids ÷ log(degré), en seconde onde.** Même parcours, autre transmission. À comparer au chiffre brut ci-dessus. Pas un remplacement silencieux : le degré 20 644 de `de` est une donnée, pas un bug de boucle.
4. **Ne pas dépasser deux sauts sur ce fichier** tant que les hubs ne sont pas traités. À 2 sauts le budget (50 000 expansions) n'a pas cassé. À 3 sauts la vague part des voisins de `de` et le dictionnaire devient le vocabulaire entier. Le retour porte `tronque` si le budget saute : ne pas lire un carrefour tronqué comme un verdict.

Les piliers 1 à 3 n'ont pas ce goulet. Ils sont dans `docs/QUATRE_PILIERS.md`.


## Mise à jour — Résolution des Hubs par Normalisation du Degré (2026-10-11)

L'implémentation de la loi `poids / ln(max(e, degre(cible)))` dans `piliers/resonance.py` permet d'étouffer les hubs syntaxiques :

1. **Sur le graphe avec overlay causal (Pilier 1 ou 3) :**
   - Sans normalisation : `de` (2,565), `un` (2,157), `le` (2,154), `lune` (#8, 1,592).
   - Avec normalisation de degré :
     * `#1 brille` (0,378, degré 4)
     * `#2 lune` (0,252, degré 34) — **Podium direct !**
     * `#3 de` (0,194, degré 20 644)
     * `#8 le` (0,138, degré 16 922)
     * `gravite` passe du rang #5 867 au rang **#21**.
   - Le hub `de` est relégué derrière `lune`, et `le` s'effondre au 8e rang.

2. **Sur le test unitaire `test_normalisation_degre_etouffe_les_hubs` :**
   - Face à un hub artificiel de 50 liens, `lune` (1 lien) conserve 1,0 d'énergie tandis que le hub est étouffé à 0,255 (rapport supérieur à 3,9x).
   - 26 tests au vert sur CPU stdlib (3,2 s).
