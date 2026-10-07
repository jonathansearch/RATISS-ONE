# 🗣️ TOKENIZER v1 — la pensée devient phrase

**RATISS Labs · 7 octobre 2026 · MIT**

> Le chaînon manquant entre le tissu et la bouche : une règle tiny qui lit
> l'état (convictions + sanctuaire + tissu) et le traduit en phrase FR/EN,
> que Piper parle. Le premier échantillon (« J'ai entendu 21 séquences... »,
> route A) est devenu une règle unique testée (`bouche/regles.py`).

## 1. Les 4 règles (lues dans l'ordre, vides sautées)

| Règle | Condition | FR | EN |
|---|---|---|---|
| R-ULTRA | convictions (top 3) | `Je tiens pour sûr : A, B.` | `I hold as certain: A, B.` |
| R-SANCT | top sanctuaire | `Au sanctuaire : X Y Z.` | `In the sanctuary: X Y Z.` |
| R-TISSU | ≥1 mot TIENT (60) | `Je tiens A et B. Le reste reste dehors.` | `I hold A and B. The rest stays outside.` |
| R-VIDE | aucun mot TIENT | `Je ne tiens rien. Tout reste dehors.` | `I hold nothing. Everything stays outside.` |

Zéro est singulier, listes en `et`/`and`, accords explicites. État lu par
`lire_etat(cerveau)` : 100 % JSON (convictions, sanctuaire, tissu, langue).

## 2. Critères d'entraînement (le contrat)

- **C1 déterminisme** : même état → même phrase, toujours (`--verifier`).
- **C2 couverture** : 8 combos (EN/FR × frais/sanctuaire/ultra/vide) tissés hors-ligne.
- **C3 batterie** : 5 phrases exactes pinnées (`bouche/autotest_bouche.py`, BOUCHE OK).
- **C4 porte de sortie** : 1 wav réel par langue (EN prouvé, FR dès voix restaurée).

## 3. La donnée (le vrai problème — résolu par construction)

Pas de corpus à télécharger : le tissu déterministe FABRIQUE ses paires
(`donnees/generer.py` → `paires.jsonl` : 20 paires, 20/20 vérifiées).
Doctrine : le GÉNÉRATEUR est versionné (source de vérité), le JSONL n'est
qu'un échantillon régénérable — la masse vivra sur Colab, jamais dans le dépôt.

## 4. Colab (vers la fin, quelques minutes)

`entrainer-colab.ipynb` : clone → robinet → éducation massive (route B à
l'échelle, régime école) → calibration (100 % reproduction, sinon ÉCHEC) →
batterie + wav. Honnêteté : pas de descente de gradient — notre entraînement
= éducation (relations) + vérification (règles). Le GPU ne sert pas, Colab
sert l'échelle.

## 5. Rejouer

```bash
python3 bouche/autotest_bouche.py        # BOUCHE OK (5 phrases)
python3 bouche/regles.py --demo EN      # dit : I hold as certain...
python3 donnees/generer.py --verifier   # 20/20 reproduites
```

## 6. Roadmap tokenizer

- [ ] **R5 comptes** — « J'ai entendu N séquences » (compteur d'écoutes à ajouter)
- [ ] **wav FR** — voix FR à restaurer (snapshot l'a mangée)
- [ ] **entrée Phonon** — brancher l'oreille live sur les règles (chaos phase 5)
