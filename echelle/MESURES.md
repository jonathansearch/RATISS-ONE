# 📏 MESURES v0.3 — le grand tissu

**RATISS Labs · 6 octobre 2026 · graine 20261006 (déterministe)**

> Régénérer et rejouer : `python3 outils/tisser_grand.py && python3 ratum.py echelle/grand.ratum`
> Preuve : `preuves/sortie-echelle.txt`

## Le tissu

| Mesure | Valeur |
|---|---|
| Neurones | 300 (250 connus + 50 réservés témoins) |
| Liens | 1200 |
| Motifs connus (présentés) | 40 × 5 nœuds |
| Motifs témoins (jamais présentés) | 10 × 5 nœuds |
| Union éduquée | 141 nœuds |
| Éducation | présentation ×2, commune ×8, nuit ×1 |

## Résultats

| Mesure | Valeur |
|---|---|
| Connus qui TIENT (seuil 30) | **40/40** |
| Résonance connus | min 75 · max 85 · moyenne 75 |
| Témoins ROMPT | **10/10, tous à 0** |
| Force moyenne des liens | 39/100 |
| Liens forts (≥ 70) | 630 |
| Durée d'exécution (berceau Python) | **0,1 s** |

## Lecture honnête

1. **La loi passe à l'échelle.** À 300 nœuds comme à 3, la répétition grave
   et l'inconnu reste à zéro. Aucun réglage nouveau n'a été nécessaire.
2. **L'éducation élague.** Les liens que l'éducation commune ne visite pas
   retombent à zéro : le tissu taille tout seul ce qu'on ne lui montre pas.
   C'est émergent, pas programmé.
3. **Le berceau tient.** 1793 lignes, 86 cycles sur 1200 liens : un dixième de
   seconde. L'implémentation bas niveau attendra qu'on en ait vraiment besoin.
