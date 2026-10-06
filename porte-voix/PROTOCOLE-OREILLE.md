# 🎙️ PROTOCOLE OREILLE LIVE — rejouer la boucle réelle

**RATISS Labs · testé le 6 octobre 2026**

> La batterie `tests_verdicts.py` reste 100 % hors-ligne (oreille simulée).
> Ce protocole est le test LIVE, avec le vrai modèle : il télécharge 0.16 Go
> et demande ~1 Go d'outils (torch CPU surtout). Attendu : quelques minutes.

## 1. Installer l'oreille (léger : sans le paquet CUDA)

```bash
export TMPDIR=$HOME/.tmp-pip && mkdir -p $TMPDIR   # /tmp trop petit (1 Go)
pip install --no-deps fermion-research
pip install --no-deps torch --index-url https://download.pytorch.org/whl/cpu
pip install safetensors soundfile scipy zstandard huggingface_hub
pip install --no-deps transformers tokenizers
```

## 2. Transcrire (le modèle se télécharge seul au 1er passage)

```bash
phonon transcribe porte-voix/audio/jfk.wav
# attendu : "And so, my fellow Americans, ask not what your country..."
```

## 3. Boucler sur le tissu

```bash
python3 porte-voix/oreille.py porte-voix/audio/jfk.wav
# attendu : transcription parfaite, puis 22x "mot hors vocabulaire"
# (l'oreille anglaise transcrit, le tissu français ne comprend pas : leçon 7)
```

## 4. Nettoyer (le modèle n'a pas besoin de rester)

```bash
rm -rf ~/.cache/fermion $HOME/.tmp-pip
# les preuves texte restent : preuves/transcription-jfk.txt + preuves/sortie-ecoute-live.txt
```
