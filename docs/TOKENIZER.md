# 🗣️ TOKENIZER v1 — la pensée devient phrase

**RATISS Labs · 7 octobre 2026 · MIT**

> Le chaînon manquant entre le tissu et la bouche : une règle tiny qui lit
> l'état (convictions + sanctuaire + tissu) et le traduit en phrase FR/EN,
> que Piper parle. Le premier échantillon (« J'ai entendu 21 séquences... »,
> route A) est devenu une règle unique testée (`bouche/regles.py`).

## 1. Les 5 règles (lues dans l'ordre, vides sautées)

| Règle | Condition | FR | EN |
|---|---|---|---|
| R-COMPTES | toujours (R5) | `J'ai entendu N séquences.` | `I heard N sequences.` |
| R-ULTRA | convictions (top 3) | `Je tiens pour sûr : A, B.` | `I hold as certain: A, B.` |
| R-SANCT | top sanctuaire | `Au sanctuaire : X Y Z.` | `In the sanctuary: X Y Z.` |
| R-TISSU | ≥1 mot TIENT (60) | `Je tiens A et B. Le reste reste dehors.` | `I hold A and B. The rest stays outside.` |
| R-VIDE | aucun mot TIENT | `Je ne tiens rien. Tout reste dehors.` | `I hold nothing. Everything stays outside.` |

Zéro est singulier, listes en `et`/`and`, accords explicites. État lu par
`lire_etat(cerveau)` : 100 % JSON (convictions, sanctuaire, tissu, langue,
écoutes). R5 : le compteur compte les séquences venues du dehors,
répétitions comprises (JFK : 35, discours FR : 30, tempête : 82) ; la voix
intérieure (rêve, `redire`) ne triche pas — 3 relectures, compteur fixe.

## 2. Critères d'entraînement (le contrat)

- **C1 déterminisme** : même état → même phrase, toujours (`--verifier`).
- **C2 couverture** : 8 combos (EN/FR × frais/sanctuaire/ultra/vide) tissés hors-ligne.
- **C3 batterie** : 5 phrases exactes pinnées, comptes inclus (`bouche/autotest_bouche.py`, BOUCHE OK).
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
python3 dialogue/conversation.py        # DIALOGUE OK (12 répliques, 7 intents)
```

## 6. Roadmap tokenizer

- [x] **R5 comptes** — « J'ai entendu N séquences » (compteur `ecoutes`, dehors seul, 7 oct.)
- [x] **⑩ motifs fixes** — noyau gelé 5 EN + 5 FR (choix du labo, `MOTIFS_FIXES`, sha pinné batterie)
- [x] **wav FR** — voix siwis restaurée, `bouche/cerveau-fr.wav` 6.8 s régénéré par le pipeline (7 oct.)
- [x] **entrée Phonon** — direct branché : tranches 2 s → Cerveau → règles, élue retrouvée (7 oct.)

## 7. Les ⑩ motifs fixes (les étiquettes, gelées 7 oct. 2026)

Choix du labo, validé par le chef : le noyau inné ne bougera plus.

| # | EN (mot → motif) | FR (mot → motif) |
|---|---|---|
| 1-4 (innés) | fellow → MFELLOW, americans → MAMERICANS, ask → MASK, country → MCOUNTRY | amis → MAMIS, peuple → MPEUPLE, pays → MPAYS, patrie → MPATRIE |
| 5 (école) | homeland → MHOME | unir → MUNIR |

Pourquoi ces 5es ? `unir` est le mot de l'école (corpus DEVOIR/COEUR,
MUNIR suivi 51→60) et `homeland` son miroir EN câblé au tissu. `comet`
et `avenir` restent dans `MOTS` comme mots d'école libres : ils
grandissent, ils ne sont pas gelés. Pinné : `MOTIFS_FIXES`
(`cerveau/cerveau.py`), sha `3165ae68528bc9d4` vérifié par la batterie
(contrôle 109) — qui touche une étiquette fait échouer le vert.

## 8. L'oreille en direct (branchée 7 oct. 2026)

`porte-voix/direct.py --simuler` rejoue JFK par tranches de 2 s : chaque
tranche est transcrite (Phonon `--json`), cousue en fenêtres de 3 mots
(mémoire de 2 mots aux frontières), entendue par le Cerveau, dite par les
règles — des sous-titres qui comprennent. Mesuré : 6 tranches, 23 mots
cousus (une bavure « custom » à une frontière — le tissu tient quand
même), comptes 3→4→8→13→20→21, puis 4 nuits : l'élue du chaos
« americans ask not » est RETROUVÉE en direct. `--micro N` écoute N
secondes au micro (échec propre sans périphérique). Rejoué sans Phonon
par la batterie (contrôle 110, `tranches-jfk.json` pinnées).

## 9. Le dialogue v1 (les règles répondent)

7 intents pinnés FR+EN (`dialogue/` : DIALOGUE.md) : l'état et les
comptes sortent du vrai tissu, l'inconnu est honnête. Sonde avant
travaux : « bonjour » → « J'ai entendu 1 séquence… » (leçon 22).
