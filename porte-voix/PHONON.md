# 👂 PORTE VOIX — protocole + statut Phonon-2

**RATISS Labs · 6 octobre 2026**

## Le protocole (la socket est prête)

```
micro / fichier audio
        ↓  Phonon-2 (audio → texte, local, 164 Mo)
transcription texte
        ↓  pont.py (texte → motifs Ratum, déterministe)
porte-voix/ecoute.ratum
        ↓  ratum.py
verdicts : compris / non compris / hors vocabulaire
```

Rejouer la démo (oreille simulée) :
`python3 porte-voix/pont.py --texte "soleil lune comete banane" && python3 ratum.py porte-voix/ecoute.ratum`

## Preuve oreille simulée (6 oct. 2026)

| Entendu | Résonance | Verdict |
|---|---|---|
| soleil | 90 | le tissu comprend soleil |
| lune | 90 | le tissu comprend lune |
| comete | 0 | le tissu ne comprend pas comete |
| banane | — | mot hors vocabulaire : banane |

Preuve : `preuves/sortie-ecoute.txt`. Ce qui est prouvé : le pont texte → motifs →
résonance fonctionne de bout en bout. Ce qui ne l'est pas : la transcription
audio elle-même (voir statut).

## Statut Phonon-2 (vérifié, pas supposé)

| Point | Statut |
|---|---|
| Existence | ✅ modèle ouvert Fermion Research, sept. 2026, 0.16 Go |
| Rôle | oreille (reconnaissance vocale), PAS outil d'entraînement |
| Langue | ⚠️ anglais seul — une oreille française reste à trouver/faire |
| Installation minimale | ✅ fermion-research --no-deps + torch CPU + 6 petites libs (pas de CUDA) |
| Transcription réelle (6 oct.) | ✅ JFK 11 s transcrit mot pour mot (preuve : `preuves/transcription-jfk.txt`) |
| Vitesse mesurée ici | 42 s au 1er passage (téléchargement + compilation), 15-17 s à chaud |
| Boucle live complète | ✅ `oreille.py` : audio → Phonon-2 → pont → tissu (protocole : `PROTOCOLE-OREILLE.md`) |

## Reste à faire

- [ ] Trouver ou entraîner l'équivalent français (l'oreille du labo parle français)
- [ ] Élargir le vocabulaire du pont au-delà des mots de démo
- [ ] Tester sur micro live quand une machine avec audio sera disponible
