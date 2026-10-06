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
| Existence | ✅ modèle ouvert Fermion Research, sept. 2026, 164 Mo |
| Rôle | oreille (reconnaissance vocale), PAS outil d'entraînement |
| Langue | ⚠️ anglais seul — une oreille française reste à trouver/faire |
| Installation ici (6 oct.) | ❌ échec : disque du bac à sable plein ; aucun périphérique audio de toute façon |
| Branchement réel | ⏳ attend une machine avec audio + modèle téléchargé |

## Reste à faire

- [ ] Installer Phonon-2 sur une machine avec de l'audio et rejouer la démo avec un vrai fichier vocal
- [ ] Trouver ou entraîner l'équivalent français (l'oreille du labo parle français)
- [ ] Élargir le vocabulaire du pont au-delà des mots de démo
