# 🧠 SECTEURS.md — les mémoires du cerveau (doctrine v1)

**RATISS Labs · 6 octobre 2026 · MIT**

> Le cerveau n'est pas un disque dur : c'est un **entonnoir qui oublie bien**.
> Tout entre par le VIF, presque tout meurt, ce qui revient chante au REFRAIN,
> ce qui chante assez entre au SANCTUAIRE. Et on ne garde jamais la donnée —
> seulement sa TRACE.

## 1. La trace, pas la donnée (mission permanente)

Chaque entrée devient une **trace** : quels mots, dans quel ordre, entendus
combien de fois, avec quelle force. Le son, le texte brut, les horodatages :
tout ça meurt avec le run (RAM, comme les charges). La trace persiste (comme
les forces). Exemple réel, sanctuaire de la démo JFK :

```
fellow+americans+ask x1 f92
```

Trois mots, un ordre, une force. Rien d'autre. Relire la fiche section 2
de `RNI-DEFINITION.md` : la mémoire long terme du RNI, c'est le chemin,
pas la cargaison.

## 2. Les quatre secteurs (régimes mesurés, pas décrétés)

| Secteur | Entrée (force à l'arrivée) | + par rencontre | − par nuit | Meurt sous | Monte au-dessus de | Coups pour monter |
|---|---|---|---|---|---|---|
| **VIF** (l'instant) | 30 | 20 | 20 | 20 | 20 | 2 rencontres |
| **REFRAIN** (le chant) | 40 | 15 | 8 | 8 | 50 | 4 rencontres |
| **SANCTUAIRE** (le marbre) | 60 | 10 | 1 | — (jamais) | — (sommet) | — |
| **ULTRA-SECTEUR** (le marbre absolu, v3) | 100 | 0 | 0 | — (jamais) | — (absolu) | — |

Lire le tableau : une séquence entendue UNE fois arrive au VIF à 30 et meurt
à la première nuit (30 − 20 = 10 < 20). Entendue DEUX fois (30 + 20 = 50),
elle monte au REFRAIN. Le refrain pardonne (nuit douce : −8) mais exige
(4 rencontres pour monter). Le sanctuaire n'oublie presque plus (−1 par
nuit) et ne meurt jamais.

L'ultra-secteur (v3, CISE) ne se remplit pas par répétition : il OBSERVE.
Chaque étincelle du tissu (`cise`) y dépose sa conviction (`cise + motif +
figés`, force 100, immortelle). C'est le tableau de bord du marbre : les
convictions profondes, listables sans scanner le graphe — un jour, la bouche
y lira l'identité de l'IA. L'ultra-secteur traverse la nuit intact (nuit 0 :
le marbre absolu n'oublie pas).

## 3. La nuit (consolidation)

```
nuit(secteur) :
  pour chaque trace : force = force − nuit_du_secteur
  les traces sous le seuil meurent (sauf sanctuaire : immortel)
  les traces assez fortes ET assez revues montent au secteur suivant
```

La nuit ne comprend rien : elle efface. C'est l'oubli qui fait la mémoire —
comme l'hippocampe qui rejoue la journée pendant le sommeil (voir CERVEAU.md).
Une nuit = un appel à `oublier` sur chaque secteur, dans l'ordre — plus,
depuis v2, la faucheuse côté tissu (`nettoyer` : liens à 0 arrachés,
neurones isolés morts sauf les nommés — *nommer, c'est protéger*).

## 4. Le crâne et la pensée (Ratum + Python, décision du chef)

- **Python = le crâne** (`cerveau/`) : il TIENT le graphe persistant
  (mots → voisins → forces) et les secteurs. Il ne pense pas, il conserve.
- **Ratum = la pensée** (`ratum.py`, inchangé) : à chaque écoute, le crâne
  réécrit le graphe en source Ratum et le fait BATTRE (`juger`). Les verdicts
  (TIENT/ROMPT) sont la pensée du moment ; le graphe est la mémoire de toujours.

Le pont est une fonction pure : `graphe → source Ratum → verdicts`.
Rien d'autre ne traverse. Les programmes `.ratum` restent 100 % Ratum.

## 5. L'ordre est une force (j13)

Les mini-séquences temporelles (option 3) : les mots qui SE SUIVENT se lient
(`a-b`, `b-c`), avec une force qui grandit à chaque rencontre. Preuve jouet
(`jouets/j13-sequences.ratum`, rejouable, dans la batterie) :

```
chaîne liée : a-b=70 b-c=70 d-e=30   (répétée → la chaîne tient)
chaîne déliée : a-b=60 b-c=60 d-e=20 (une fois → le délié s'efface)
```

L'ordre des mots n'est pas une liste : c'est une **chaîne de liens qui tient
ou qui rompt**. Le cerveau lit ces chaînes (`chaines()`) pour savoir ce qui
se suit VRAIMENT — pas ce qui s'est croisé une fois par hasard.

## 6. D'où vient le plan (FOCAL, adapté, pas copié)

L'univers virtuel FOCAL du chef (`univers-focal/`, 172 lignes rapatriées
comme référence) nous a donné quatre mécanismes, chacun adapté au RNI :

| FOCAL (virtuel) | Cerveau (RNI) | Adaptation |
|---|---|---|
| condensateur (charge brute) | **VIF** | la charge devient une trace qui meurt vite |
| porteurs (convergence) | **REFRAIN** | la convergence devient l'exigence : 4 rencontres |
| conteneur (boucles stables) | **SANCTUAIRE** | la boucle devient le marbre : −1, jamais mort |
| couches (mesure par couches) | `rapport()` | la mesure devient le verdict par secteur |

Ce n'est PAS de la physique quantique : pas de qubits, pas de superposition —
des compteurs, des seuils et des nuits. De l'intrication relationnelle
computationnelle, comme écrit dans la fiche RNI.

## 6bis. La gravure et la rétroaction (v4, phase 3 route C — leçon 15 🪨)

Le sanctuaire est le BLOC de marbre, la rétroaction est le CISEAU, la gravure
est la STATUE. `Cerveau.redire()` ferme la boucle : la trace dominante du
sanctuaire est formulée (tokenizer, règle unique) puis RÉ-ENTENDUE — la bouche
parle, l'oreille écoute. Chaque relecture incrémente `redites` ; à la 3e
(`SEUIL_MARBRE = 3`), la trace est GRAVÉE : la nuit ne l'use plus (ni usure,
ni mort, ni promotion). Le répété reste en haut, le reste s'efface : le
RELIEF naît de l'oubli sélectif. Mesuré (`cerveau/autotest_marbre.py`) : A
relue 3 fois = f100 MARBRE après 5 nuits, témoin B = f87, relief 13 ; FR
identique. L'éclair (CISE) fige par la vitesse, la rivière (MARBRE) grave par
la répétition — ne pas confondre avec le « marbre absolu » (ULTRA-SECTEUR,
convictions CISE à 100, sans répétition).

## 7. Rejouer

```bash
python3 cerveau/autotest.py     # hors-ligne, déterministe : CERVEAU OK
python3 cerveau-demo.py         # LIVE : JFK → secteurs → résumé parlé (46 s)
python3 tests_verdicts.py       # batterie : 81/81 dont j13 + autotest cerveau
```

## 8. Limites dites à voix haute

1. Fenêtres de 3 mots fixes : pas encore de vraies phrases à longueur libre.
2. Vocabulaire du tissu : 6 mots anglais — le cerveau entend 22 mots, le tissu
   n'en comprend que 4 (le reste est tracé, pas compris).
3. Régimes calibrés sur UNE démo (JFK) : les nombres (30/20/20…) sont des
   mesures v1, pas des constantes universelles.
4. Le sanctuaire ne meurt jamais : à terme, il faudra une érosion même du
   marbre — sinon le cerveau se remplit. Piste v2, pas résultat.
