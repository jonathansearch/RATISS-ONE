# 📏 MESURES-FR.md — démo discours français live, 6 octobre 2026 (route A)

**Protocole :** `python3 cerveau-demo-fr.py` — faster-whisper small (mots
horodatés FR) → fenêtres de 3 mots → `Cerveau("FR")` (éducation + écoute +
répétitions) → nuit 1 → nuit 2 → `rapport()` → Piper FR (résumé parlé).
**Preuves :** `preuves/transcription-discours.txt`,
`preuves/sortie-cerveau-demo-fr.txt`, `bouche/cerveau-fr.wav` (8.6 s,
restauré 7 oct. 2026).

## Installation (vivante, non persistée — rejouer par session)

```bash
pip install faster-whisper soundfile   # oreille (moteur ctranslate2, pas de torch)
pip install piper-tts                   # bouche
python3 -m piper.download_voices fr_FR-siwis-medium --download-dir bouche/voix
```

Le `.onnx` (63 Mo) est git-ignoré (loi : organe externe, GPL-3.0) ; seul le
`.onnx.json` est commis. Le son est décodé par soundfile et donné en tableau
numpy (contourne l'incompatibilité PyAV de faster-whisper).

## Entrée (oreille FR)

- 21 mots transcrits **mot pour mot** (référence connue : l'audio a été
  généré par Piper depuis le texte — même méthode que JFK connu)
- 19 séquences de 3 mots ; 1 riche (≥ 2 mots connus) : `amis du peuple`
- 4 mots compris par le tissu : amis, peuple, pays, patrie
- Temps : 10.9 s à froid (téléchargement 244 Mo inclus), **~1.5 s à chaud**

## Tissu FR (`francais.ratum`, miroir de `english.ratum`)

| Mot | FR | EN (rappel) |
|---|---|---|
| 4 appris | 81, 85, 85, 90 | 81-90 |
| cousin (unir / homeland) | 40 | 41 |
| témoin (avenir / comet) | 0 | 0 |

Mêmes verdicts à 1 point près : la loi est indépendante de la langue.
26 liens, force moyenne 70, 22 liens forts.

## Écoute et nuits (cerveau FR)

| Étape | Mesure |
|---|---|
| Écoute 19 séquences + riche ×2 + focus ×6 | 27 liens, tissu 4× **95** |
| Nuit 1 | 1 promu VIF→REFRAIN, **0 morts** |
| Nuit 2 | 1 promu REFRAIN→SANCTUAIRE : `amis+du+peuple x1 f92` |
| État final | VIF 0 traces, REFRAIN 0 traces, SANCTUAIRE 1 trace |
| Chaînes vivantes | 1 (amis-peuple) |

Même force de sanctuaire qu'en anglais (**f92**) : les mathématiques de
l'entonnoir ne parlent aucune langue. Le refrain finit vide : tout a fondu
vers l'unique séquence répétée — entonnoir honnête, pas de remplissage.

## Sortie (bouche FR)

- Rapport : secteurs + tissu + liens (ex. `amis+du+peuple x1 f92`),
  puis phrase dite : « J'ai entendu 30 séquences. Au sanctuaire : amis du peuple. Je tiens amis,
  peuple, pays et patrie. » (le compteur « J'ai entendu N séquences »
  compteur R5 livré 7 oct. : 19 fenêtres + 2 riches + 9 focus = 30)
- `bouche/cerveau-fr.wav` : 8.6 s — boucle totale **~8-13 s** selon cache
  (oreille ~1.5 s à chaud, reste cerveau + bouche ; restauré 7 oct. 2026)

## Autotest FR (hors-ligne, déterministe)

`python3 cerveau/autotest_fr.py` → `CERVEAU FR OK — sanctuaire :
amis+du+peuple x1 f92, tissu : 91 97 97 97, chaînes : 1`.
Dans la batterie : autotest vert (108/108, 7 oct. 2026).

## Ce que ça prouve (et pas plus)

Le pipeline complet est **bilingue** : même crâne, même loi, deux langues —
et les nombres coïncident (81-90, cousin ~40, témoin 0, sanctuaire f92).
Ça ne prouve ni la compréhension du français libre (4 mots) ni la robustesse
au bruit (voix synthétique claire) : ça prouve que la route A tient — ni plus.
