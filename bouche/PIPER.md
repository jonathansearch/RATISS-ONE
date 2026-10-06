# 🗣️ BOUCHE — Piper TTS, l'organe de sortie

**RATISS Labs · 6 octobre 2026**

## Ce que c'est

Piper : petit moteur neuronal texte → parole, local, CPU seul (tient sur
Raspberry Pi). La bouche ne comprend rien : elle convertit les verdicts du
tissu en ondes — comme le larynx.

## Installation (testée ici)

```bash
pip install piper-tts
cd bouche/voix && python3 -m piper.download_voices en_US-lessac-medium
```

- Voix : `en_US-lessac-medium` (63 Mo, anglais US). Le `.onnx` n'est PAS
  commité (trop gros) : un re-téléchargement = une commande.
- Dire un texte : `echo "I hold the sun" | python3 -m piper --model bouche/voix/en_US-lessac-medium.onnx --output_file out.wav`

## Licence (honnêteté)

`piper-tts` est publié en **GPL-3.0** (maintenu par OHF-Voice). On l'utilise
comme organe EXTERNE qu'on appelle — on ne le copie ni ne le distribue dans
ce dépôt (MIT). Si un jour la bouche doit entrer DANS le système, il faudra
trancher la question de licence avant, pas après.

## Mesures ici

| Texte | Audio produit |
|---|---|
| "the tissue holds the sun" (test) | 1.5 s, 68 Ko |
| "I hold fellow, americans, ask and country. The rest stays outside." (JFK réel) | `bouche/verdicts.wav` (preuve commise) |

Vitesse : quelques secondes sur ce petit CPU — la bouche n'est jamais le
goulot (l'oreille prend 15-40 s, le tissu 0.1 s).
