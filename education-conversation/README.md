# 🗣️ ÉDUCATION-CONVERSATION v1 — le tissu apprend à converser

**RATISS Labs · 8 octobre 2026 · MIT · Vision du chef, protocole du labo.**

> Pas de gros dataset : des **petites scènes** (question → réponse) écoutées
> **plusieurs fois**. Le tissu ne stocke pas les mots (que des forces) donc
> il **ne peut pas halluciner**. Quand il rate, **le coup** : on ré-écoute le
> juste — les bons alliages grandissent. Les faits (l'histoire de Martin en
> petits mots) persistent comme le reste : au SANCTUAIRE.

## Protocole (les deux maisons du chef — école `delie 0`, vie `(10,3)`)

1. **Naissance** : chaque mot neuf = 1 neurone + 1 nerf d'oreille (sans nerf : sourd).
2. **École du matin** : cliques par scène + battements `delie 0` (sanctuarisé).
3. **Journée** : chaque souffle `q0+r` D'UN SOUFFLE en loi réelle (compteur R5).
4. **Nuits** : oubli + faucheuse (`nettoyer`) + secteurs (VIF → REFRAIN → SANCTUAIRE).
5. **Devoirs du soir** : l'école répare ce que la vie a effiloché (re-naissances + `delie 0`).
6. **Sonde pure** : `rencontre Q + propager` (UNE vague), JAMAIS `renforcer` —
   lire sans toucher. Score = allumage de la réponse HORS les mots de la question.
7. **Le coup** (sur raté, max 5) : re-liens + frappe d'école `delie 0`. Le coup est
   un maître, pas la vie : il ne touche jamais aux autres scènes.

Corpus : `scenes.py` — 10 dialogues + 3 faits Martin, chacun q0 (entendue) +
q1 (cliquée) + q2 (combinaison neuve) + réponse. 3 témoins jamais entendus
(silence exigé = preuve anti-hallucination). Seuils écrits AVANT les runs :
TOP ≥ 30, marge ≥ 10, murmure < 20. 42 tests par régime.

## Résultats (preuves : `preuves/conversation-*.txt`)

| Régime | École | 1er passage¹ | Bilan | Coups | Secteurs |
|---|---|---|---|---|---|
| nul | 0 + 0 | 24/42 | **39/42** | 61 (15 rattrapés) | 13 REFRAIN |
| pauvre | 1 + 1 | 25/42 | **40/42** | 48 (15 rattrapés) | 13 REFRAIN |
| canonique | 8 + 8 | 38/42 | **40/42** | 12 (2 rattrapés) | 13 SANCTUAIRE 🏆 |
| **réveil** (cerveau gravé relu) | — | — | **40/42** = bilan, sans coup | 0 | — |

¹ Premier passage = tient sans coup PROPRE, dans l'ordre (les coups précédents
aident les suivants via les mots partagés — effet d'ordre déterministe, publié).

- Témoins : **9/9 silencieux** (3 par régime) — l'inconnu ne s'allume pas. Zéro hallucination.
- Cerveau gravé : **1 839 octets** (`fige-conversation.json.gz`) — les forces, pas les mots.
- Faits Martin : F11 3/3, F12 3/3, F13 2/3 (canonique) + 3 souffles au SANCTUAIRE.

## Les 4 ratés, expliqués (l'échec se publie)

- **Pauvreté = faiblesse** (nul/pauvre) : S1 q0 `[salut]` plafonne à 23-25/30
  (1 mot seul ne porte pas), S2 q1 `[comment]` à **29/30** — à UN point ! 😅
- **Richesse = saturation** (canonique) : S7 q0 `[merci,ami]` → S2 gagne 83-74
  (`merci` appartient à 2 scènes + chaînes des souffles du jour), F13 q0
  `[reve,martin]` → F11 gagne 80-78. Près du plafond, l'élasticité ne creuse
  plus l'écart : 5 coups ne brisent pas la symétrie. Mécanisme prouvé, pas subi.

## Trouvailles (physique honnête, toutes prouvées par les runs)

1. **Le jour efface l'école du matin** : 36 érosions × 3 > 100 (le plafond) —
   d'où les devoirs du soir. Enseigner APRÈS la vie, pas avant (ou figer : CISE).
2. **Les coups cannibales** (v1) : une frappe de loi dans le coup mangeait les
   innocents (−3) pendant que le rival co-actif gagnait → réveil 25/42.
   Coup d'école pur (`delie 0`) : réveil **= bilan**. La loi du chef avait raison.
3. **La pauvreté évite la saturation** : S7 q0 tient en pauvre (34-17), pas en
   canonique (74-83) — les petits liens gardent leurs marges.
4. **Les secteurs persistent vraiment** : 1 nuit → REFRAIN, 4 nuits → SANCTUAIRE,
   13/13 souffles (dialogues + faits Martin) à chaque fois.

## Rejouer

```bash
python3 education-conversation/eduquer_conv.py --regime canonique --graver education-conversation/fige-conversation.json.gz
python3 education-conversation/eduquer_conv.py --regime pauvre|nul
python3 education-conversation/eduquer_conv.py --reveil education-conversation/fige-conversation.json.gz
```

## Greffes du chef (mappées, pas construites)

1. **Secteur CAIRN** (stockage nouvelle génération) : `fige-conversation.json.gz`
   est l'embryon — forces persistantes, mots absents, réveil exact. Le CAIRN =
   des chemins consolidés rappelables, soumis à la même loi (rappelé = renforcé).
2. **Main tendue** (module agentique) : question non tenue → recherche externe →
   retour comme NOUVELLE ÉCOUTE par le tissu (comme un humain qui lit une page).
   La porte « compréhension externe », toujours différée, toujours prévue.
