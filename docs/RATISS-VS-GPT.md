# Ratiss et GPT, au fond

Deux machines. Deux questions. On peut les faire se ressembler à la sortie (une suite de mots) et elles restent étrangères à l'intérieur.

## La question

| | GPT, Llama, le petit 1M | Ratiss, avant GI | Ratiss GI |
|---|---|---|---|
| Question posée au fichier | Étant donné tout ce qui vient d'être dit, quel morceau a le droit de suivre ? | Quels mots se sont fréquentés ? | Les deux, **séparées** |
| Où est la mémoire | Dans des matrices de flottants | Dans le lien, un entier de force | Le lien intriqué **et** l'arc dirigé |
| Unité | Token (souvent un bout de mot, BPE) | Mot, neurone `word_*` | Mot |
| Sens de la flèche | Obligatoire : le futur est masqué | Effacé : les deux bouts sont triés | Rétabli, dans la bouche seulement |

Un LLM ne range pas des phrases. Il range une machine à continuer une phrase. Ratiss-ONE range une machine à faire résonner un mot avec ses fréquentations. Les deux peuvent répondre « noire » après « mer ». L'un parce que c'est une suite probable. L'autre parce que les deux ont battu ensemble un jour. Ce n'est pas le même « noire ».

## L'architecture

### GPT

Avant la moindre phrase, quatre choses, et aucune n'est un savoir :

1. Un `config.json` : nombre de couches, largeur, têtes, vocabulaire, contexte. Zéro fait.
2. Le code du réseau. Un GGUF ne stocke pas le graphe de calcul, seulement les tableaux et une petite fiche.
3. Un tokenizer, fabriqué à part. « Once upon a time » devient des entiers. Les mots ne sont pas les flottants.
4. Des poids tirés au hasard (gaussienne, pas des zéros : sinon tous les neurones reçoivent le même gradient). Les normes partent à 1.

Puis, à chaque position, la même bouche bête :  un score par morceau du vocabulaire, un softmax, une probabilité. Les couches ne servent qu'à calculer cette probabilité **en tenant compte de toute la phrase d'avant**, pas seulement du dernier mot. L'attention fabrique Q, K, V, masque le futur, fait une moyenne pondérée dont les poids dépendent du contenu. Le MLP réfléchit sans regarder les autres positions. Une connexion résiduelle ajoute le résultat à l'entrée, pour que le signal ne se perde pas.

Rien, dans le fichier, n'est la règle « après once upon a time, écrire there ». Il y a des tableaux. L'idée « Amy a trois ans » est étalée sur des milliers de poids qui n'ont de sens qu'ensemble. On peut tout lire et ne pas pouvoir lire la règle. C'est ça, la boîte noire : pas un chiffrement. Une règle qui n'est écrite nulle part en clair.

### Ratum, le tissu

Un seul tissu, pas de couches. Un neurone porte une charge éphémère (0–100) et un seuil (50). Il bat quand la charge atteint le seuil. La mémoire n'est pas dans le neurone : elle est dans le **lien**, un entier né à 10.

La loi est unique. Si les deux bouts battent, le lien monte (main qui lie). Sinon il descend (main qui délie). `propager` envoie l'énergie avec une ombre : la moitié se perd à chaque saut. Au-delà d'une vitesse, le neurone se fige en CISE et le lien peut être gelé. Le verdict est `TIENT` ou `ROMPT`. Tout est entier, rejouable. Ce n'est pas une descente de gradient.

Autour, le crâne tient des secteurs. Ce sont des **températures de mémoire**, pas des matières scolaires :

| Secteur | Arrive à | Monte après | La nuit |
|---|---|---|---|
| VIF | 30 | 2 rencontres | −20, meurt |
| REFRAIN | 40 | 4 rencontres | −8 |
| SANCTUAIRE | 60 | sommet | homéostasie, plancher 60 |
| ULTRA | 100 | observé, pas répété | nuit 0 |

Le secteur stocke la trace relationnelle. Jamais la donnée brute.

### Ratiss GI, la bouche

Pas de Q, pas de K, pas de couche. La représentation du « transformeur », chez nous, est une somme écrite avec les ondes qu'on avait déjà :

```
score(candidat) = λ · ordre(candidat) + (1 − λ) · thème(candidat)

ordre(candidat)   = 0,65 · trigramme(mot-2, mot-1 → candidat) + 0,35 · bigramme(mot-1 → candidat)
                    si la paire a été vue, sinon le bigramme seul
thème(candidat)   = résonance du tissu scellé + fenêtre de 3 apprise avec le texte
```

Le trigramme est un compte de paires. Ce n'est pas une phrase rangée dans une synapse, et ce n'est pas un passage sur les 95 660 neurones : seuls les successeurs de la paire, ou du dernier mot, sont candidats. La lumière sur 8 mots reste mesurable (`--memoire`), elle a perdu le top-1 face au repli bigramme.

`λ = 1`, la grammaire sans sujet. `λ = 0`, la nuée actuelle. Le λ qui fait monter le top-5 **et** qui reste sur le sujet, c'est la première bouche. Pas une tête d'attention. Un mélange de deux lois qui sont les tiennes.

Le softmax du LLM est repris, en plus petit : on ne le calcule pas sur 95 660 mots, seulement sur les voisins sortants du mot courant, souvent quelques dizaines. La somme fait 1. On **pioche**. Si on prend toujours le plus fort, la bouche boucle.

Il n'y a pas de boîte noire au sens d'un calcul caché. Chaque arc se lit. `mer → noire : 12` veut dire : douze fois, dans le texte vu, « noire » suivait « mer ». La limite n'est pas le secret. La limite, c'est la portée : le trigramme voit la paire, pas la page. La lumière sur 8 mots a été mesurée, elle ne gagne pas le top-1. On ne l'habille pas en transformeur.

## L'entraînement

### GPT

1. Choisir les tailles.
2. Entraîner le tokenizer sur le texte brut.
3. Tirer les poids au hasard.
4. Pour chaque position, prédire l'id suivant.
5. La perte est `−log(probabilité du vrai token)`.
6. La rétropropagation dit, pour chaque poids, si le bouger un peu fait monter ou descendre la perte.
7. Adam déplace chaque poids d'un pas minuscule. Ses moments **ne sont pas** dans le GGUF final.
8. On recommence sur des millions de bouts.
9. On sauve. Souvent safetensors, puis GGUF.

L'entraînement ne range pas les mots. Il sculpte le bruit de départ jusqu'à ce que le softmax tombe souvent sur la bonne suite. Deux entraînements aussi bons peuvent produire des nombres entièrement différents : le paysage a beaucoup de creux. Changer l'ordre des exemples, la perte, le pas, ou le tirage initial, change le fichier. Le GGUF n'est qu'un emballage.

Et même sans rien changer, un GGUF Q4 ne contient déjà plus les mêmes flottants : il jette de la précision pour tenir dans moins de mémoire.

Pourquoi ça hallucine, y compris un modèle de 500 milliards : l'objectif n'est pas « dire vrai ». C'est « continuer comme les textes vus ». Rien dans la perte ne punit une info fausse si elle ressemble au corpus. Il n'y a pas de case « je ne sais pas », sauf si les textes l'ont, ou si une deuxième phase a poussé les poids dans ce sens. Le tirage au sort peut prendre le 10ᵉ token, puis continuer cette branche de façon cohérente. La cohérence n'est pas la vérité.

### Ratiss GI

1. Le plan est déjà là : `config/config.ratiss.json`. Il ne contient aucun fait.
2. L'oreille découpe en mots. Pas de BPE. `pipeline/01_oreille.py`.
3. L'étape 0 est une bouche **sans un seul arc**. Pas un bruit gaussien : l'absence d'ordre. `config/bouche_etape0.json`.
4. Pour chaque vrai mot suivant, on incrémente **un seul** arc, `mot_i → mot_{i+1}`. Pas la fenêtre de 3. Pas les deux sens.
5. La fenêtre de 3 alimente un **autre** tableau, le thème. Il n'a pas le droit de voter seul pour la parole.
6. La décharge : si la bouche préférait un rival, on monte l'arc vrai et on baisse un peu les rivaux **du même départ**. Hebb dit « ils étaient ensemble ». La décharge dit « celui-là devait venir maintenant ». C'est la seule idée du transformeur qui est indispensable. Le reste, couches, têtes, GPU, est une façon parmi d'autres de calculer ce même écart.
7. On mesure le top-5 sur un fichier jamais donné à `--eduquer`.
8. On sauve la bouche. Les compteurs d'Adam n'existent pas. Il n'y a rien à oublier dans le fichier final, parce qu'il n'y a pas eu de moments cachés.

Un fait (« la lune orbite autour de la terre ») n'est pas un paragraphe dans un dictionnaire. C'est un chemin gelé, force 100, et un index : si la question résonne avec `lune`, la bouche emprunte le chemin jusqu'au bout, puis redevient libre.

## Ce qui ne reviendra pas, même si on change les règles

Chez un LLM, relancer l'entraînement avec une autre perte ou un autre ordre ne fait pas revenir les mêmes flottants. Ici non plus, pour une raison plus simple encore : les arcs **sont** le compte de ce qui a été vu. Un autre corpus, un autre registre, un autre nombre de tours, et le fichier change, lisiblement. On peut diff deux `.bouche`. On ne peut pas diff deux GGUF à l'œil.

Modifier le nombre de « couches » dans le `.bouche` ne veut rien dire : il n'y en a pas. Modifier le `.ratiss` (ajouter un lien, casser une forme) casse le sceau du tissu. Pour obtenir d'autres nombres cohérents, on relance l'éducation de la bouche. On ne réveille pas le gel.

## Hallucination, des deux côtés

La bouche v3 hallucine encore, et il faut le dire clairement.

- Tant qu'elle pioche, elle peut quitter la branche vraie et la continuer de façon cohérente. Même maladie que la température d'un LLM.
- Un arc fréquent n'est pas un fait. « prince → aimait » n'est pas une mémoire d'un prince. C'est un compte.
- Le sanctuaire, lui, ne hallucine pas : il récite ce qui a été écrit. Il ne sait que quatre textes. Le confondre avec la bouche, c'était l'ancienne panne.
- Une chaîne gelée ne sait que ce qu'on a gravé. Elle ne déduit pas. Si on veut une déduction, ce n'est pas encore cette bouche. C'est une question d'après.

La différence utile : quand Ratiss GI ne sait pas, il peut le dire (bouche vide, aucun arc). Un LLM, lui, a presque toujours un token suivant plausible. Le silence est un avantage. Il ne faut pas le reboucher avec un gabarit.
