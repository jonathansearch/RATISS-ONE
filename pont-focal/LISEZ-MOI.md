# 🌌 PONT FOCAL — le compteur d'émergence

**RATISS Labs · 7 octobre 2026 · MIT**

> Le tissu RNI traverse le vrai univers FOCAL (`univers-focal/`, inchangé)
> et en ressort mesuré : trois tissus, trois projections, trois nombres.

## Rejouer

```bash
pip install numpy ripser   # Colab : numpy déjà là, ajouter ripser
python3 pont-focal/pont.py # PONT FOCAL OK (graines fixées, ~10 s)
```

## Le pont, en clair

1. **Encodeur** (`encodeur.py`, stdlib seule) : l'état du tissu
   (`bouche.regles.lire_etat`) devient 2048 bits — la TRACE relationnelle
   uniquement (quels mots, quel ordre canonique trié, quelle force),
   jamais la donnée brute. Même tissu → mêmes bits, partout.
2. **Projection** : `condensateur.injecter` pose 60 points neutres issus
   des bits sur le fond `conteneur.fond` (tore + sphère).
3. **Mesure** : `conteneur.p_sig` (persistance H1+H2) + témoin porteurs
   (`concentration` avant/après 4 transports vers le centre du tore).

## Première mesure (pinnée, `preuves/sortie-pont-focal.txt`)

| tissu | sha16 des bits | P_sig |
|---|---|---|
| fond seul | — | 5,7599 |
| frais | `e098de14fc25fbed` | 6,3887 |
| chaos | `f29a73ec25dbdb98` | 6,3970 |
| sanctuaire | `f555dd714bc1bf0b` | **6,2301** |
| porteurs | — | Phi 27,10 → 855,64 (×31,6) |

Le compteur bouge (delta max 0,1668) : le pont transporte de l'information.
Et le sanctuaire projette **plus calme** que le chaos — l'ordre fait moins
de vagues. Piste v1 sur 3 points, pas un théorème (voir leçon 19).

## Ce que la batterie vérifie (contrôle 108, sans numpy ni ripser)

- l'encodeur est déterministe (2 passes identiques) et sépare les 3 tissus ;
- les 3 sha16 valent les dorés ci-dessus ;
- la preuve committée contient `PONT FOCAL OK`, les 3 sha et les 3 P_sig.
  (Si l'encodeur change, régénérer la preuve : commande ci-dessus.)

## Limites v1 (honnêtes)

- L'ordre intra-trace n'est pas encodé (tri canonique, déterministe).
- Le couplage tissu→porteurs (`tau` piloté par le tissu) est pour la v2 ;
  ici les porteurs témoignent que les organes convergent (×31,6).
