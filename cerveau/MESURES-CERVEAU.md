# 📏 MESURES-CERVEAU.md — démo JFK live, 6 octobre 2026

**Protocole :** `python3 cerveau-demo.py` — Phonon-2 (mots horodatés) →
fenêtres de 3 mots → `Cerveau` (éducation + écoute + répétitions) →
nuit 1 → nuit 2 → `rapport()` → Piper (résumé parlé).
**Preuves :** `preuves/sortie-cerveau-demo.txt`, `bouche/cerveau.wav` (6.0 s).

## Entrée (oreille)

- 22 mots transcrits mot pour mot (clés JSON : backend, segments, text, words…)
- 20 séquences de 3 mots ; 3 riches (≥ 2 mots connus du tissu)
- 4 mots compris par le tissu : fellow, americans, ask, country

## Écoute et nuits (cerveau)

| Étape | Mesure |
|---|---|
| Écoute 20 séquences + riches ×2 + focus ×6 | 28 liens tissés, tissu 4× **95** |
| Nuit 1 | 4 promus VIF→REFRAIN, **0 morts** (les répétitions ont tout sauvé) |
| Nuit 2 | 1 promu REFRAIN→SANCTUAIRE : `fellow+americans+ask x1 f92` |
| État final | VIF 0 traces, REFRAIN 3 traces, SANCTUAIRE 1 trace |
| Chaînes vivantes (liens ≥ 50) | 2 |

Refrain final : `americans+ask+not f42`, `my+fellow+americans f42`,
`can+do+for f32` — que des séquences VRAIES de JFK, aucune hallucination.

## Sortie (bouche)

- Phrase : « I heard 20 sequences. 3 sleep in the refrain. 1 reached the
  sanctuary : fellow americans ask. »
- `bouche/cerveau.wav` : 6.0 s, 22050 Hz, mono — boucle totale **46.3 s**
  (oreille ~40 s à chaud, cerveau 0.1 s, bouche ~2 s).

## Autotest (hors-ligne, déterministe)

`python3 cerveau/autotest.py` → `CERVEAU OK — sanctuaire : 1 trace(s),
chaînes : 4, MAMERICANS=95` — éducation titi/toto/tata, focus ×9,
2 nuits, sanctuaire atteint, tissu à 95, chaîne frère intacte.
Dans la batterie : 81/81 verts.

## Ce que ça prouve (et pas plus)

L'entonnoir fonctionne en conditions live : 20 séquences entrent, 1 sort
au sanctuaire, et c'est la plus répétée — pas la première, pas la dernière.
L'ordre des mots survit comme chaînes de liens mesurables. Ça ne prouve ni
le passage à l'échelle ni la compréhension de phrases libres : ça prouve
que le crâne tient et que la pensée bat — ni plus.
