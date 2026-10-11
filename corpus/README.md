# Corpus

Les fichiers ici sont des **jouets**. Ils servent à vérifier que le pipeline tourne. Ils ne font pas une bouche.

| Fichier | Rôle |
|---|---|
| `prince_jouet.txt` | 8 phrases, registre `conte`. Prose du pas 4 |
| `tenu_a_lecart.txt` | phrases cousines, **non** données à l'éducation. C'est le juge |
| `faits_jouet.txt` | vérités courtes, pas 5, registre `fait` |
| `episodes_jouet.txt` | deux phrases vives, pas 6, une passe |
| `retouches_jouet.txt` | une case `globe → verre`, pas 7, après le compte |
| `dialogue_jouet.jsonl` | trois tours, pour tester l'organiseur |

Le vrai texte reste chez toi. Voir `docs/ENTRAINEMENT.md` pour Gutenberg, Wikipédia, OpenAssistant, et ce qu'il ne faut pas mélanger.

```bash
python3 entrainement/organiser_corpus.py \
  --entree corpus/dialogue_jouet.jsonl \
  --sortie corpus/dialogue_jouet.txt \
  --registre dialogue

python3 entrainement/entrainer_langue.py \
  --education corpus/prince_jouet.txt \
  --ecart corpus/tenu_a_lecart.txt \
  --faits corpus/faits_jouet.txt \
  --episodes corpus/episodes_jouet.txt \
  --retouches corpus/retouches_jouet.txt \
  --registre conte --tours 3 \
  --sortie sortie/langue_jouet
```

Le deuxième écrit un dossier. Il ne modifie pas ces jouets. L'organisation du dossier est `docs/ORGANISATION_LANGUE.md`.
