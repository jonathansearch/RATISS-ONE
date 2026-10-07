# 🛠️ ROUTE D — le second berceau (C)

**RATISS Labs · 7 octobre 2026 · MIT**

> Une spec saine a deux implémentations indépendantes et identiques.
> `ratum.c` rejoue les 24 programmes du corpus et sort **exactement** comme
> `ratum.py` — au caractère près, scroll `mem.scroll` compris.

## Rejouer

```bash
gcc -O2 -Wall -Wextra -o route-d/ratum-c route-d/ratum.c  # zéro warning toléré
python3 route-d/conformite.py   # CONFORMITE OK — 24/24 (+ scroll identique)
./route-d/ratum-c english.ratum # même sortie que python3 ratum.py english.ratum
```

## Périmètre prouvé

- Les **24 programmes** de `tests_verdicts.py` (`CAS`) : sorties + codes
  comparés **octet par octet** (Python : `ratum.py`, C : `ratum-c`).
- Le scroll `jouets/mem.scroll` (j04 : `graver`/`relire`) : JSON comparé
  octet par octet — le C écrit le même `json.dump(indent=1)` que Python
  et relit les deux.
- Sémantique répliquée : loi (10,3), élasticité `max(1, haut*(100-f)//100`,
  ombre `//200`, `borne` à chaque pas **dans l'ordre d'insertion**, tris
  `sorted()` partout (UTF-8 : l'ordre d'octets = l'ordre des points de code),
  pluriels, dédup `dict.fromkeys`, `strtol` à consommation totale (= `int()`).

## Divergences documentées (hors corpus, jamais déclenchées)

1. **Usage / fichier illisible** : le C nomme son binaire (`ratum-c`) et
   utilise `strerror` — messages cosmétiques différents, codes identiques (2).
2. **Gelés ≥ 2 dans le scroll** : Python itère un `set` (ordre de hachage,
   non déterministe) ; le C écrit l'ordre d'insertion. Corpus : 1 gelé max
   (j14, pas de `graver`) et j04 sans gelé — identique partout où ça compte.
3. **`int()` exotiques** : `int("1_0")`, chiffres unicode — acceptés par
   Python, refusés par le C. Corpus : entiers simples uniquement.
4. **Relire/graver en échec** (disque) : Python lève un traceback, le C une
   `ERREUR RATUM` propre. Corpus : jamais en échec.
5. **Mémoire** : programme one-shot, l'OS récupère à la sortie (comme Python).

## Fichiers

- `ratum.c` — le second berceau (~1000 lignes, C17, que la libc).
- `conformite.py` — compile + rejoue + compare (dans la batterie).
- `ratum-c` — binaire construit (non versionné : voir `.gitignore`).
