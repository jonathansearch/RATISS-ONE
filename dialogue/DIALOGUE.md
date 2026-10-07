# 💬 DIALOGUE v1 — on lui parle, il répond

**RATISS Labs · 7 octobre 2026 · MIT**

> Avant : le tissu DÉCRIVAIT (« J'ai entendu 1 séquence. Je tiens… »).
> Maintenant : on lui dit bonjour, il dit bonjour — et quand la question
> porte sur lui, la réponse sort du VRAI tissu (état, compteur R5).

## Rejouer

```bash
python3 dialogue/conversation.py [--wav bouche/dialogue.wav]
```

## Les 7 intents (pinnés, FR + EN)

| Intent | Exemples FR | Exemples EN | Réponse |
|---|---|---|---|
| saluer | bonjour, salut, coucou | hello, hi, hey | « Bonjour ! Moi c'est RATISS… » |
| identite | qui es-tu, ton nom | your name, who are you | « Je suis RATISS-ONE… » |
| etat | tu tiens quoi | what do you hold | **le vrai `formuler()` du tissu** |
| comptes | combien, tu as entendu | how many, you heard | **le vrai compteur R5** |
| aide | aide, sais-tu faire | help, what can you | mode d'emploi |
| aurevoir | au revoir, adieu | bye, goodbye | « Le tissu garde… » |
| inconnu | (le reste) | (the rest) | « Je ne comprends pas encore… » (honnête) |

Chaque phrase entendue nourrit le tissu (fenêtres de 3, compteur R5) :
la conversation EST une écoute. Preuve : `preuves/sortie-dialogue.txt`
(12 répliques) + `bouche/dialogue.wav` (12 voix cousues, FR+EN).

## Limites v1 (honnêtes, écrites avant l'entraînement)

- **Motifs pinnés, pas de généralisation** : « yo » ou « comment vas-tu »
  tombent en `inconnu` — ce n'est PAS un LLM, c'est un standardiste
  honnête qui dit quand il ne sait pas.
- La route vers la généralisation : l'entraînement massif (Colab) fait
  grandir le tissu (milliers de mots tenus) ; les intents v2 liront le
  tissu au lieu des motifs (une question = une résonance, pas un `if`).
- Une langue par cerveau : FR avec `Cerveau("FR")`, EN avec `Cerveau("EN")`.
