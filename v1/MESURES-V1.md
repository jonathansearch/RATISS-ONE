# ⚖️ MESURES v1 — la loi à deux mains + les seuils vivants

**RATISS Labs · 6 octobre 2026**

> Rejouer : `python3 ratum.py v1-coexistence.ratum` (+ `jouets/j11`, `jouets/j12`)
> Preuves : `preuves/sortie-coexistence.txt`, `preuves/sortie-jouets.txt`

## L'expérience : même tissu, deux lois, 6 tours d'alternance

Deux formes disjointes A et B, alternées tour à tour (6 tours).

| Régime | A | B | Verdict (seuil 40) |
|---|---|---|---|
| Symétrique (lier 10, délier 10) | 10 | 10 | ROMPT, ROMPT — stagnation |
| Asymétrique (lier 10, délier 3) | 52 | 52 | TIENT, TIENT — coexistence |

## Les seuils vivants (`adapter`)

| Moment | Seuils observés |
|---|---|
| Naissance | 50, 50 |
| Après le feu (charge 100) | 75, 75 |
| Après le calme (charge 0) | 37, 37 |

Règle : le seuil rejoint la charge à mi-chemin.

## Calibration honnête

La paire (lier 10, délier 3) est la PREMIÈRE paire essayée qui fait coexister
avec marge (52 contre seuil 40). Elle n'est pas optimisée : le balayage
systématique des paires (lier × délier) est une piste ouverte, pas un résultat.
De même, `adapter` est la règle la plus simple (mi-chemin entier) — d'autres
rythmes d'adaptation restent à mesurer.
