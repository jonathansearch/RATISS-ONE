# Entraîner la bouche

La méthode est une. Les datasets changent la **mise en forme**, pas la loi.

L'ordre complet — prose, faits gelés, épisode vif, retouche d'une case, top-5 seulement sur l'écart — est `entrainement/entrainer_langue.py`. Les dix pas, les deux dossiers, et qui a le droit d'écrire où : [ORGANISATION_LANGUE.md](ORGANISATION_LANGUE.md). La boucle plus bas reste le compte seul, quand tu n'as pas besoin des dix pas.

## Le chiffre

Sur un texte que `--eduquer` n'a pas vu :

```
top-5 = (nombre de positions où le vrai mot suivant est dans les 5 candidats) / (nombre de positions)
```

On publie ce chiffre. On ne publie pas une impression.

Le top-5 **sur le texte vu** est un plafond. Il dit si le compte a bien été écrit. Il ne dit pas si la bouche généralise. Le fichier `corpus/tenu_a_lecart.txt` existe pour ça, même dans le jouet.

## La boucle

```bash
# 0. Le plan et la bouche vide sont déjà dans config/

# 1. Mettre le corpus au format attendu
python3 entrainement/organiser_corpus.py \
  --entree mes_dialogues.jsonl --sortie corpus/dialogue.txt --registre dialogue

# 2. Éduquer. CPU. Le .ratiss n'est pas modifié.
python3 pipeline/03_entrainer.py \
  --cerveau cerveau/RatissOne.ratiss \
  --corpus corpus/dialogue.txt \
  --registre dialogue \
  --tours 3 \
  --sortie checkpoints/dialogue.bouche

# 3. Mesurer sur un fichier jamais donné ci-dessus
python3 pipeline/04_evaluer.py \
  --cerveau cerveau/RatissOne.ratiss \
  --bouche checkpoints/dialogue.bouche \
  --texte corpus/tenu_a_lecart.txt

# 4. Écouter
python3 ratiss_v3.py cerveau/RatissOne.ratiss \
  --charger checkpoints/dialogue.bouche --lam 0.75 --memoire 8 \
  "raconte moi une suite"
```

`--tours 3` relit le corpus trois fois. Avec la décharge, un rival qui gagnait à tort descend un peu à chaque passage. `--sans-contraste` refait la même chose en pur compte, pour voir si la décharge sert.

Les faits courts ne passent pas par `--eduquer`. Ils passent par `--faits` : une vérité par ligne, chaîne gelée, force 100.

```bash
python3 ratiss_v3.py cerveau/RatissOne.ratiss \
  --faits corpus/faits_jouet.txt --registre fait --sauver checkpoints/faits.bouche
```

On peut éduquer un registre `conte`, puis graver des faits dans la même bouche. Les familles d'arcs restent séparées dans le JSON.

## Ordre des essais, pas ordre des envies

1. Audit du tissu. Tu dois revoir l'alphabet (`abattu`, `absente`…). Si tu ne le vois pas, tu n'es pas sur ce fichier-là.
2. Jouet `--demo`. Tu dois entendre une suite courte, puis une boucle.
3. Un vrai texte **d'une seule sorte**. Conte, ou dialogue, ou science. Pas les trois le premier jour.
4. Le top-5 tenu à l'écart. S'il reste au niveau du tissu (autour de 10 %), la linéarisation est fausse ou le texte est trop sale. On ne passe pas à la suite.
5. Seulement alors, un deuxième registre.
6. Seulement si le dernier mot seul plafonne et que des tournures longues décrochent, `--memoire 8`, et on **compare**. S'il ne gagne pas, on le retire.

## CPU, GPU, Colab

La bouche est un compte. Le compte va vite sur un CPU. Un million de mots, c'est une boucle Python sur des dictionnaires : de l'ordre de la minute, pas de l'heure, et ça dépend de la machine. Il n'y a pas de matrice à multiplier.

| Machine | Quoi lancer | Quoi ne pas lancer |
|---|---|---|
| CPU local, le tien | `pipeline/03_entrainer.py` | un transformeur « en attendant » |
| Colab, runtime **CPU** | `colab/Entrainement_Bouche_RATISS_GI.ipynb` | le runtime T4 |
| Colab, runtime GPU | rien, pour cette bouche | `scalable_gpt_train.py` |

Le GPU redeviendra une question le jour où tu décideras d'apprendre la lumière (une poignée de coefficients) ou un vrai score continu au-dessus des arcs. Ce jour-là, le tissu et la bouche existent déjà, et le GPU sert à calculer l'écart « le mot suivant », pas à remplacer Ratum. Tant que ce jour n'est pas là, une heure de T4 est une heure perdue. Ce n'est pas le modèle qui est trop faible. C'est l'organe nourri qui n'était pas la bouche.

Le notebook Colab clone ce dépôt, lance la démo, l'audit, puis éduque le fichier que tu déposes à côté. Runtime CPU. Gratuit.

## Datasets : lesquels, et comment on les pose

La loi ne change pas. Trois choses changent : le registre, la linéarisation, le gel.

### 1. Narration, le premier corpus

C'est celui qui fait naître la bouche. Phrases qui se suivent, français écrit, peu de tableaux, peu de code.

À prendre, dans cet ordre :

- **Domaine public français.** Hugo, Maupassant, Verne, Dumas, via Project Gutenberg. Vérifie la date et le pays : le domaine public n'est pas le même partout. Un texte sous droit n'entre pas dans un dépôt public.
- **Wikipédia français** (CC BY-SA). Propre, vaste, un peu raide. Bon deuxième corpus, registre `science` ou `ordre`, pas `conte`.
- **Leipzig Corpora**, français, phrases d'actualité déjà découpées. Bien pour un top-5, parce que les phrases sont courtes.
- **OSCAR** ou **CulturaX**, partie française. Énormes, sales (menus, seo, langues mélangées). On ne commence pas par là. On y va quand le pipeline tient sur un Gutenberg.

À ne pas prendre comme premier texte : un corpus déjà passé par un autre LLM pour être « amélioré », sauf à l'étiqueter `traduit` ou `paraphrase`. Sinon tu mesures le style de l'autre modèle, pas le tien.

Format : un fichier UTF-8. L'organiseur découpe sur `. ! ?` et sur les retours à la ligne. Pas de balise à inventer.

```bash
python3 entrainement/organiser_corpus.py \
  --entree hugo.txt --sortie corpus/hugo.txt --registre conte
```

Dans le cerveau : registre `conte`, arcs libres, pas de gel. Le sanctuaire n'est pas rempli avec des chapitres.

### 2. Conversation

OpenAssistant (`oasst1`, `oasst2`), langue `fr`, licence Apache-2.0. C'est le jeu conversationnel le plus propre pour commencer. La collection Aya a aussi du français, à vérifier licence par sous-ensemble.

À éviter comme socle : ShareGPT et la plupart des exports « share-chat ». La licence est souvent introuvable. Un modèle souverain qui ne peut pas dire d'où vient sa phrase n'est pas souverain.

Linéarisation, faite par l'organiseur :

```
_q_ quelle est la capitale du cameroun _r_ la capitale du cameroun est yaounde
```

`_q_` et `_r_` sont des mots comme les autres. La bouche apprend que `_r_` ouvre une réponse, et que les mots de la question éclairent, via `--memoire`, les mots de la réponse. On n'écrit pas un second algorithme « mode chat ». On écrit une suite.

Le registre est `dialogue`. On ne mélange pas le dialogue et le conte dans le même registre le premier mois : sinon « il était une fois » se met à répondre « bien sûr ».

Le top-5 se calcule sur des dialogues tenus à l'écart, pas sur les mêmes fils.

### 3. Science

Wikipédia déjà cité. Résumés HAL (archives ouvertes françaises) si la licence du jeu que tu télécharges le permet. Pas PubMed comme socle : c'est presque tout en anglais, et l'oreille de ce dépôt ne traduit pas.

Linéarisation : la prose telle quelle, registre `science`.

Les **définitions courtes** que tu veux pouvoir redire sans les inventer ne passent pas dans la prose. Elles passent dans `--faits`, une ligne par vérité, registre `fait`, chaîne gelée :

```
la fusion du deuterium et du tritium produit de l helium et un neutron
yaounde est la capitale politique du cameroun
```

Ça s'implémente comme la lune : des arcs à force 100, et des clés (`fusion`, `yaounde`, `helium`). Une question qui contient la clé emprunte le chemin. Elle ne « résonne » pas vers un voisin alphabétique.

On ne verse pas Wikipédia dans le sanctuaire. Le sanctuaire reste une main. Quatre textes, ou quarante que tu as lus. Pas quatre millions.

### 4. Ce qu'il ne faut pas adapter

- Pas un secteur nouveau par dataset.
- Pas une perte différente. La décharge est la même : monter le vrai arc, baisser les rivaux du même départ.
- Pas un tokenizer différent par corpus. L'oreille est le mot, accents pliés, casse pliée. Si un corpus est anglais, il aura son registre `en`, pas une autre loi. Ce dépôt est fait pour le français du tissu actuel.
- Pas de phase « RLHF » imitée avec un second GPU. Si tu veux que la bouche dise « je ne sais pas », il faut que cette phrase **suive** les questions sans réponse, dans le corpus, ou qu'elle reste le comportement de la bouche vide. Un gabarit collé après coup est l'ancienne panne.

## Fichiers, dans l'ordre où un LLM les ferait naître

| Étape LLM | Fichier LLM | Ici |
|---|---|---|
| Plan | `config.json` | `config/config.ratiss.json` |
| Code du réseau | `model.py` | `ratiss_v3.py` |
| Tokenizer | `tokenizer.json` | `pipeline/01_oreille.py` |
| Étape 0 | poids gaussiens | `config/bouche_etape0.json` |
| Corpus mis en forme | binarisé, ids | `entrainement/organiser_corpus.py` → `.txt` |
| Boucle d'apprentissage | `train.py` | `pipeline/03_entrainer.py` (le compte seul) |
| Méthode langue | le script qui tient l'ordre | `entrainement/entrainer_langue.py` |
| État d'optimiseur | Adam, non publié | rien : le compte est déjà le fichier |
| Validation | loss sur un split | `pipeline/04_evaluer.py`, le top-5 |
| Checkpoint | safetensors | `checkpoints/*.bouche` |
| Export final | GGUF, souvent quantifié | `.bouche` gzippé, non quantifié |

On ne quantifie pas. Une force tient dans un petit entier. Jeter de la précision n'achète presque rien, et ça rendrait le fichier opaque, ce qui est l'inverse du projet. Si un jour le `.bouche` dépasse ce que tu veux copier, on stockera les comptes en entiers 16 bits. Ce sera encore lisible. Ce ne sera pas un Q4.

## Split

Coupe **avant** l'éducation, par document, pas par phrase tirée au hasard dans le même chapitre. Sinon la phrase suivante a été vue, et le top-5 ment.

- 90 % éducation
- 10 % tenus à l'écart, jamais passés à `--eduquer`
- les faits gelés sont tous « vus » : on ne mesure pas un fait gravé comme s'il était deviné. On mesure la prose.

## Arrêt

On s'arrête quand le top-5 tenu à l'écart ne monte plus d'un tour à l'autre. Relire cinquante fois un Gutenberg n'invente pas les phrases qui n'y sont pas. Ça creuse les ornières, et la bouche boucle plus tôt. Trois tours, on mesure, on décide.
