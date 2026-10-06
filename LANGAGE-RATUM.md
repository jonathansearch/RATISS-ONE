# 📜 LANGAGE RATUM v1 — Spécification : ce que chaque relation veut dire

**RATISS Labs · 6 octobre 2026 · MIT**

> Changements v1 : `renforcer` accepte deux mains (`lie`/`delie`), nouvelle
> relation `adapter` (seuils vivants), `dire` sait montrer les `seuils`.
> Tout programme v0 reste valide : 42/42 contrôles v0 toujours verts.

> Le Ratum est la langue du tissu. On y parle avec des mots, pas avec des
> formules : on DÉCLARE des habitants (neurones, liens, formes), puis on fait
> ARRIVER le monde (rencontres), on laisse la LOI travailler (renforcement),
> et on ÉCOUTE le verdict (résonance, juge).
>
> Règles du jeu v0 : tout niveau vit entre 0 et 100, en nombres entiers.
> Tout lien naît faible (10). Chaque neurone bat quand sa charge atteint
> son seuil (50 par défaut, réglable par neurone depuis v0.1).
> Le pas du renforcement vaut 10, celui de l'oubli 5.
> Tout programme est déterministe : rejoué, il redit la même chose.

---

## A. 🏠 HABITER — déclarer le tissu et ses habitants

### 1. `tissu` — le lieu unique où tout vit
- **Sens :** ouvre le monde du programme. En v0, un seul tissu par programme :
  un seul cœur, pas de modules séparés.
- **Usage :** `tissu <nom>` … `fin`
- **Exemple :**
  ```
  tissu Education
    ...
  fin
  ```

### 2. `neurone` — un habitant qui peut s'allumer
- **Sens :** un point du tissu. Il porte une CHARGE (éphémère : ce qu'il vit
  maintenant) et un SEUIL (la charge à partir de laquelle on dit qu'il bat).
  La charge s'éteint au repos ; rien d'autre ne persiste dans le neurone —
  la mémoire vit dans les LIENS, pas dans les habitants.
- **Usage :** `neurone <nom> [seuil <n>]` (seuil 50 par défaut)
- **Exemple :** `neurone lumiere seuil 50`

### 3. `lien` — une intrication entre deux neurones
- **Sens :** le destin lié. Un lien porte une FORCE (persistante : c'est elle,
  la mémoire). Plus le lien est fort, plus l'activité passe d'un bout à l'autre.
  Tout lien naît faible : la confiance se gagne par rencontres, elle ne se donne pas.
- **Usage :** `lien <a> <b> [force <n>]` (force 10 par défaut)
- **Exemple :** `lien chaud lumiere force 10`

### 4. `motif` — une forme nommée (un visage du monde)
- **Sens :** un ensemble de neurones qui, allumés ensemble, VEULENT dire quelque
  chose : un mot, un son, une idée. Le motif n'est pas stocké comme une donnée :
  c'est une façon de frapper à la porte du tissu (voir `rencontre`).
- **Usage :** `motif <NOM> : <neurone> <neurone> ...`
- **Exemple :** `motif SOLEIL : chaud lumiere jour`

---

## B. ❤️ BATTRE — les trois règles du cœur + la loi

### 5. `rencontre` — le monde frappe à la porte (ACTIVATION)
- **Sens :** allume à plein (100) tous les neurones d'un motif. C'est l'arrivée
  du monde : une rencontre, pas une donnée importée. Rien n'est copié nulle part :
  le tissu lui-même s'illumine.
- **Usage :** `rencontre <motif>`
- **Exemple :** `rencontre SOLEIL`

### 6. `propager` — le frémissement voyage (PROPAGATION)
- **Sens :** chaque lien verse au voisin une part de la charge qu'il reçoit,
  d'autant plus grande que le lien est fort (part entière, plafonnée à 100).
  Les liens forts portent loin ; les liens faibles portent à peine.
  C'est ainsi qu'une forme allumée RÉVEILLE ses voisines liées —
  le mécanisme de l'intrication naturelle.
- **Usage :** `propager`
- **Exemple :** `propager`

### 7. `renforcer` — LA LOI (RENFORCEMENT)
- **Sens :** *ce qui se tient ensemble se renforce, ce qui se disjoint s'efface.*
  Pour chaque lien : si les deux bouts battent (chacun a atteint son seuil),
  la force monte d'un pas ; sinon, elle descend d'un pas. Aucune exception,
  aucun pilote : la structure fait le tri toute seule.
  Depuis v1, la loi a DEUX MAINS réglables séparément : la main qui LIE (monte)
  et la main qui DÉLIE (descend). Lier fort et délier doux permet à des formes
  disjointes de coexister (voir `v1-coexistence.ratum`).
- **Usage :** `renforcer [pas <n>]` ou `renforcer lie <X> delie <Y>` (10/10 par défaut)
- **Exemple :** `renforcer lie 10 delie 3`

### 8. `oublier` — la nuit passe sur le tissu
- **Sens :** tous les liens perdent un peu de force. Les chemins entretenus
  survivent ; les sentiers abandonnés s'aplanissent. Oublier n'est pas effacer
  un fichier : c'est laisser retomber ce que personne ne revisite.
- **Usage :** `oublier [pas <n>]` (pas 5 par défaut)
- **Exemple :** `oublier`

### 9b. `adapter` — les seuils vivants (v1)
- **Sens :** chaque neurone ajuste SON seuil : le seuil rejoint la charge
  actuelle à mi-chemin. Un neurone qui bat beaucoup devient exigeant ; un
  neurone silencieux s'adoucit et se laisse réveiller plus facilement.
  C'est l'homéostasie du tissu : l'exigence suit le vécu.
- **Usage :** `adapter`
- **Exemple :** `adapter` (seuil 50 + charge 100 → 75)

### 9. `repos` — la fin du cycle
- **Sens :** toutes les charges retombent à zéro. L'activité est éphémère,
  seules les forces persistent. C'est la séparation la plus importante du
  langage : **le vécu s'éteint, le appris demeure.**
- **Usage :** `repos`
- **Exemple :** `repos`

---

## C. 👂 ÉCOUTER — mesurer et juger

### 10. `résonance` — le tissu reconnaît-il cette forme ?
- **Sens :** demande au tissu : « tiens-tu cette forme ? » La réponse est la
  force moyenne des liens INTERNES au motif (ceux dont les deux bouts en font
  partie), de 0 (inconnu) à 100 (gravé). Se souvenir, c'est résonner — pas relire.
- **Usage :** `résonance <motif>`
- **Exemple :** `résonance SOLEIL` → `résonance SOLEIL = 90/100`

### 11. `mesurer` — l'état de santé du tissu
- **Sens :** dit le nombre de liens, leur force moyenne, et combien sont forts
  (≥ 70). Le bilan du jardin : combien de chemins, combien de routes.
- **Usage :** `mesurer`
- **Exemple :** `mesurer` → `liens : 10` / `force moyenne : 63/100` / `liens forts : 7`

### 12. `juger` — le verdict scellé
- **Sens :** tranche : la résonance d'un motif atteint-elle le seuil exigé ?
  Si oui → TIENT ; sinon → ROMPT. Le juge ne devine pas, il mesure puis dit.
  Chaque verdict est imprimé avec son chiffre et son seuil : vérifiable.
- **Usage :** `juger <motif> <seuil>`
- **Exemple :** `juger SOLEIL 30` → `JUGEMENT SOLEIL : TIENT (90/100, seuil 30)`

### 13. `dire` — la bouche du tissu
- **Sens :** parle. Imprime des mots, en remplaçant `résonance <motif>` par sa
  valeur, `forces` par l'état de tous les liens et `seuils` (v1) par les seuils
  de tous les neurones. C'est la seule sortie du langage : tout ce que le tissu
  sait, il le dit à voix haute — rien de caché.
- **Usage :** `dire <mots...>`
- **Exemple :** `dire SOLEIL tient à résonance SOLEIL sur 100`

---

## D. 🔁 RYTHMER — répéter et choisir

### 14. `répéter` — le temps qui passe
- **Sens :** rejoue un bloc N fois. L'éducation est une répétition : chaque tour
  est une rencontre de plus, un pas de plus sur le chemin. Les boucles peuvent
  s'emboîter (voir `rni-complexe.ratum`, phase 3).
- **Usage :** `répéter <n>` … `fin`
- **Exemple :**
  ```
  répéter 6
    rencontre SOLEIL
    propager
    renforcer
    repos
  fin
  ```

### 15. `si` — choisir selon la résonance
- **Sens :** le seul choix du langage, et il ne choisit que sur une chose :
  est-ce que telle forme TIENT à tel seuil ? Pas de calcul caché dans la
  condition : que de la résonance mesurée. Avec `sinon` pour l'autre chemin.
- **Usage :** `si <motif> tient <seuil> alors` … `[sinon` …] `fin`
- **Exemple :**
  ```
  si ORAGE tient 10 alors
    dire ALERTE : le tissu rêve
  sinon
    dire le témoin inconnu est rejeté
  fin
  ```

---

## E. 📸 GARDER TRACE — la photo du tissu (outils d'ingénierie)

### 16. `graver` — photographier le tissu
- **Sens :** écrit l'état complet (neurones, liens, forces, motifs) dans un
  fichier. Honnêteté : le fichier n'est PAS la mémoire — c'est une PHOTO de
  la mémoire, pour transporter le tissu ou le vérifier. La mémoire reste le
  tissu vivant.
- **Usage :** `graver <fichier>`
- **Exemple :** `graver tissu-educ.scroll`

### 17. `relire` — réveiller une photo
- **Sens :** recharge un tissu gravé et continue avec lui. Le tissu reprend
  exactement où la photo l'avait laissé : mêmes forces, mêmes formes.
- **Usage :** `relire <fichier>`
- **Exemple :** `relire tissu-educ.scroll`

---

## F. 📏 Règles de grammaire v0

- Un programme = du texte ; tout ce qui suit `#` est un commentaire (ignoré).
- Les blocs `tissu`, `répéter`, `si` se ferment par `fin` ; `sinon` n'existe que dans `si`.
- Tout nom inconnu (neurone, motif, relation) est une ERREUR affichée avec son
  numéro de ligne : le langage ne devine jamais, il dit quand il ne comprend pas.
- `fin` et `sinon` hors bloc = erreur. Deuxième `tissu` = erreur (v0 : un seul cœur).
- Les accents des mots-clés sont tolérés avec ou sans (`résonance` ou `resonance`,
  `répéter` ou `repeter`) : la machine ne doit pas buter sur un clavier.

---

## G. 🧪 Batterie v0.1 — les 10 jouets qui verrouillent la spec

Chaque jouet prouve un recoin du langage. Tous rejoués le 6 octobre 2026
(preuve : `preuves/sortie-jouets.txt`), tous vérifiés par `tests_verdicts.py`.

| Jouet | Ce qu'il prouve | Chiffres observés |
|---|---|---|
| `j01-seuil` | chaque neurone bat à SON seuil | VIF 40 TIENT, DUR 20 ROMPT |
| `j02-pas` | pas sur mesure du renforcement et de l'oubli | 35 TIENT, puis 0 ROMPT |
| `j03-oubli` | l'oubli total, puis la rééducation | 70 → 0 ROMPT → 20 TIENT |
| `j04-graver-relire` | la photo sauve le souvenir puis le réveille | 70 → 0 → 70 TIENT |
| `j05-si-sinon` | les deux chemins du choix, sans erreur parasite | `alors` + `sinon`, zéro ERREUR |
| `j06-motif-sans-liens` | sans liens internes, résonance nulle | 0 et 0, deux ROMPT |
| `j07-emboitement-plafond` | boucles emboîtées + plafond à 100 | 12 rencontres → 100 TIENT |
| `j08-repos` | le repos éteint les charges (loi après repos affaiblit) | 50 → 40 ROMPT |
| `j09-propagation` | l'activité voyage de proche en proche | une vague 95, deux vagues 100 |
| `j10-erreur` | l'erreur nette : motif inconnu = code 1 + ligne fautive | `ERREUR RATUM` |
| `j11-asymetrie` (v1) | lier 10 / délier 3 fait coexister deux disjointes | 52 et 52, deux TIENT |
| `j12-adapter` (v1) | le seuil rejoint la charge à mi-chemin | 50 → 75 → 37 |

---

*18 relations. Zéro formule. Que des mots qui font ce qu'ils disent.*
*« On ne croit pas. On rejoue. »*
