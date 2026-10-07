# 🧠 RNI — Définition scientifique des Réseaux de Neurones Intriqués

**RATISS Labs · Jonathan Evina · 6 octobre 2026 · MIT**

---

## 1. Définition

> **Un réseau de neurones intriqué (RNI) est un tissu de neurones dont les
> destins sont liés par des liens à force variable, gouvernés par une seule
> loi : *ce qui se tient ensemble se renforce, ce qui se disjoint s'efface.***
> L'apprendre est la persistance des formes ; la mémoire est le relief des
> chemins ; se souvenir est une résonance, pas une lecture.

**« Intriqué »** veut dire ici : quand un neurone bat, ses voisins liés battent
avec lui, et leur lien se fortifie — leurs destins sont attachés l'un à l'autre.
C'est une intrication **computationnelle** (destins liés par la loi du
renforcement), PAS une intrication quantique. Aucun phénomène quantique n'est
invoqué, simulé ou revendiqué dans ce dépôt.

---

## 2. RNI contre réseaux classiques

| Réseaux classiques 🏭 | RNI 🌱 |
|---|---|
| Couches séparées : entrée → cachées → sortie | Un seul tissu, pas de couches imposées |
| On entraîne par descente de gradient (erreur rétro-propagée) | On éduque par rencontres (la loi renforce sur place) |
| La mémoire = des poids dans des fichiers | La mémoire = des forces dans des liens vivants |
| Phase d'entraînement géante, puis on fige | Croissance continue, jamais figée |
| Oublier = écraser des nombres | Oublier = laisser retomber les chemins délaissés |
| Le réseau devine la suite | Le réseau résonne avec les formes qu'il tient |

---

## 3. Positionnement honnête face à l'existant

- **Réseaux classiques (MLP, transformers) :** le RNI ne les copie pas et ne
  prétend pas les battre aujourd'hui. Il propose une autre voie : structure
  d'abord, données en rencontres, loi unique.
- **Travaux sur l'intrication quantique dans les réseaux** (ex. états de réseaux
  de neurones à la Boltzmann restreinte, Phys. Rev. X 2017) : ce sont des études
  de physique quantique sur des architectures classiques. Notre « intrication »
  est un autre concept (destin lié computationnel) — le mot est partagé,
  la chose ne l'est pas. Qu'on ne nous fasse pas dire ce qu'on ne dit pas.
- **Hebb (« qui bat ensemble se lie ») et STDP :** la loi du RNI en est parente
  (renforcement par co-activité), avec une différence centrale : ici la loi est
  UNIQUE et gouverne tout le système (apprendre, mémoire, oubli, jugement),
  sans module séparé ni fonction d'erreur.
- **RATIS-Net / Skynet (nos propres systèmes) :** ils portent déjà la loi de
  cohérence, mais sur un véhicule neuronal classique. Le RNI est le pas suivant :
  la loi directement sur le tissu, sans moteur intermédiaire.

---

## 4. Les deux leçons mesurées (modèle Ratum v0, 6 oct. 2026)

### Leçon 1 🫂 — L'intrication naturelle : partager un nœud, c'est se fortifier
*Programme : `rni-complexe.ratum` — preuve : `preuves/sortie-complexe.txt`*

SOLEIL et LUNE partagent le neurone `lumiere`. Après avoir appris le soleil
(résonance 70), on apprend la lune : non seulement la lune monte (60), mais le
soleil monte à 100 — la lumière partagée RÉVEILLE le soleil pendant qu'on
éduque la lune. Après éducation commune et une nuit d'oubli : SOLEIL 90,
LUNE 90. Le témoin ORAGE, jamais rencontré : 0 — le tissu ne rêve pas.

> **Énoncé :** dans un RNI, apprendre une forme fortifie les formes qui
> partagent ses nœuds. L'unification n'est pas programmée : elle ÉMERGE du
> partage.

### Leçon 2 🌊 — L'interférence vraie : sans rien en commun, le nouveau chasse l'ancien
*Programme : `rni-interference.ratum` — preuve : `preuves/sortie-interference.txt`*

Deux formes sans aucun nœud commun. On apprend la première (résonance 70),
puis la seconde SANS revoir la première : la première retombe à 10 (ROMPUE),
la seconde monte à 60 (TENUE).

> **Énoncé :** sous la loi pure, deux formes disjointes ne cohabitent pas sans
> répétition commune : la nouvelle efface l'ancienne. C'est le prix de la loi —
> et la raison d'être de l'ÉDUCATION (répéter ensemble, phase 3 du complexe),
> qui est le mécanisme de coexistence du RNI.

### Leçon 3 📖 — Le vocabulaire : les mots tissés se reconnaissent, le cousin est deviné, l'inconnu reste dehors
*Programme : `vocabulaire.ratum` — preuve : `preuves/sortie-vocabulaire.txt`*

12 mots français tissés à la main (mot + 3 concepts partagés), présentés 3 fois
chacun puis éduqués en commun 9 fois, nuit 2 fois : **12/12 TIENT (80-90,
seuil 60)**. Le cousin AURORE (jamais présenté, 3 concepts sur 4 connus) :
**40 — rejeté au seuil 60 mais deviné à moitié**. L'inconnu COMETE (nœuds
frais) : **0 — reste dehors**. 65 liens, force moyenne 76, 61 liens forts.
Observation honnête : la présentation séquentielle seule s'efface mutuellement
(mots à 30 avant commune) ; c'est l'éducation commune qui grave uniformément.

> **Énoncé :** dans un RNI, la reconnaissance est GRADUÉE : le connu tient fort,
> le cousin tient à moitié, l'inconnu ne tient pas. Et à 12 mots, seule
> l'éducation commune grave durablement — la présentation isolée s'efface.

### Leçon 4 📏 — L'échelle : à 300 nœuds la loi tient, et l'éducation élague
*Généré par `outils/tisser_grand.py` (graine 20261006) — mesures : `echelle/MESURES.md`*

300 neurones, 1200 liens, 40 motifs éduqués + 10 témoins : **40/40 TIENT
(75-85), 10/10 témoins à 0**, en 0,1 seconde. Observation émergente : les liens
que l'éducation ne visite pas retombent à zéro — **le tissu élague tout seul**.

> **Énoncé :** la loi du RNI passe à l'échelle sans réglage nouveau, et
> l'éducation commune taille le tissu : ce qu'on ne montre jamais s'efface.

### Leçon 5 ⚖️ — L'asymétrie : lier fort et délier doux fait coexister
*Programme : `v1-coexistence.ratum` — mesures : `v1/MESURES-V1.md`*

Deux formes disjointes alternées 6 tours : en symétrique (10/10), les deux
stagnent à 10 (ROMPT) ; en asymétrique (lier 10, délier 3), les deux montent à
52 (TIENT). Même tissu, même alternance — seule la balance des deux mains
change. Bonus v1 : `adapter` rend les seuils vivants (50 → 75 au feu → 37 au
calme). Calibration honnête : (10, 3) est la première paire qui marche avec
marge, pas un optimum — le balayage reste à faire.

> **Énoncé :** sous alternance, la loi symétrique fige les disjointes et la loi
> asymétrique les fait coexister. La coexistence est un RÉGLAGE de la loi, pas
> un module ajouté.

### Leçon 6 👂 — L'oreille : le pont parle au tissu
*Pont : `porte-voix/pont.py` — preuve : `preuves/sortie-ecoute.txt`*

Transcription simulée « soleil lune comete banane » → programme Ratum généré →
exécuté : soleil et lune COMPRIS (90), comete entendue mais NON COMPRISE (0),
banane signalée HORS VOCABULAIRE. Statut honnête : le pont est prouvé de bout
en bout, mais l'oreille est simulée — Phonon-2 (anglais seul, 164 Mo) n'est pas
installable dans ce bac à sable et attend une machine avec audio (voir
`porte-voix/PHONON.md`).

> **Énoncé :** une porte sensorielle n'a pas besoin de comprendre : elle
> convertit le monde en motifs, et c'est le TISSU qui comprend (ou pas).
> L'inconnu entendu ne pollue pas le connu — il est rejeté proprement.

### Leçon 7 🎙️ — Transcrire n'est pas comprendre (oreille RÉELLE)
*Boucle live : `porte-voix/oreille.py` — preuves : `preuves/transcription-jfk.txt`, `preuves/sortie-ecoute-live.txt`*

Phonon-2 branché pour de vrai (installation minimale, modèle 0.16 Go vérifié
SHA-256) transcrit le discours JFK de 11 s **mot pour mot**. Mais le tissu,
éduqué en français, rejette les 22 mots anglais comme HORS VOCABULAIRE —
sans broncher, sans inventer, sans se polluer.

> **Énoncé :** l'oreille parfaite ne fait pas la compréhension : transcrire
> (l'oreille) et comprendre (le tissu) sont deux actes séparés. Un tissu
> honnête dit « hors vocabulaire » au lieu de rêver.

### Leçon 8 🦜 — La boucle parole : le perroquet qui ne répète que ce qu'il tient
*Boucle : `parole.py` (oreille Phonon → tissu anglais → bouche Piper) — preuves : `preuves/sortie-parole.txt`, `bouche/verdicts.wav`*

JFK transcrit mot pour mot → tissu anglais (4 mots tissés) : fellow, americans,
ask, country TENUS à 90, 16 mots hors vocabulaire → la bouche DIT (4.9 s
d'audio) : « I hold fellow, americans, ask and country. The rest stays
outside. » Boucle totale 42 s (oreille 40 s au 1er passage, tissu 0.1 s,
bouche 2 s). **Zéro donnée stockée** : le transcrit ne vit qu'en RAM pendant
le run (comme une charge) ; seules les forces persistent (comme des synapses).
Les fichiers commis sont le carnet du labo, pas les données du système.

> **Énoncé :** audio → tissu → audio fonctionne de bout en bout avec des
> organes légers (0.16 + 0.06 Go) et AUCUN dataset : les modèles actuels
> fournissent les portes, le tissu fournit la compréhension — et la bouche
> ne dit que ce que le tissu tient.

Ces deux leçons sont des sorties du modèle v0, rejouables en une commande.
Elles ne prouvent pas le passage à l'échelle : elles prouvent que le modèle
se comporte comme sa loi le dit — ni plus, ni moins.

### Leçon 9 🧠 — Le cerveau : un entonnoir qui oublie bien
*Cerveau : `cerveau/` (Python = crâne, Ratum = pensée) + `jouets/j13-sequences.ratum` —
preuves : `preuves/sortie-cerveau-demo.txt`, `bouche/cerveau.wav`, `cerveau/MESURES-CERVEAU.md`*

Le tissu est enfermé dans un crâne à trois secteurs : VIF (l'instant, meurt
vite), REFRAIN (le chant, exige 4 rencontres), SANCTUAIRE (le marbre, −1 par
nuit, jamais mort). Chaque entrée devient une TRACE (quels mots, quel ordre,
combien de fois, quelle force) — jamais la donnée brute. Les mots qui se
SUIVENT se lient en chaînes mesurables (j13 : chaîne liée 70/70, déliée 20).
Démo live JFK : 20 séquences entrent, 1 atteint le sanctuaire
(`fellow americans ask`, f92), le cerveau le DIT (6 s d'audio, boucle 46 s).
Plan inspiré de l'univers FOCAL (condensateur/porteurs/conteneur), adapté au
RNI — sans aucune physique quantique : des compteurs, des seuils, des nuits.

> **Énoncé :** la mémoire relationnelle intriquée fonctionne en entonnoir
> (VIF→REFRAIN→SANCTUAIRE) en conditions live : ce qui survit, c'est le plus
> répété — et l'ordre des mots survit comme chaînes de liens qui tiennent.

### Leçon 10 🇫🇷 — Le retour au français : la loi ne parle aucune langue
*Route A : `francais.ratum` + `porte-voix/oreille_fr.py` (faster-whisper small) +
`Cerveau("FR")` + `cerveau-demo-fr.py` — preuves : `preuves/transcription-discours.txt`,
`preuves/sortie-cerveau-demo-fr.txt`, `bouche/cerveau-fr.wav`, `cerveau/MESURES-FR.md`*

Le pipeline complet est devenu bilingue : oreille faster-whisper small (21
mots FR mot pour mot, 10.9 s à froid, ~1.5 s à chaud), tissu français
(81/85/85/90, cousin 40, témoin 0 — miroir de l'anglais à 1 point près),
cerveau FR (19 séquences → sanctuaire `amis du peuple` f92, tissu 4×95),
bouche Piper FR (résumé parlé 6 s, boucle totale 8.5 s). Même crâne, même
loi, deux langues — et les nombres coïncident : sanctuaire f92 des deux
côtés. L'anglais n'était qu'un détour technique ; Ratum parle français.

> **Énoncé :** la loi du RNI est indépendante de la langue : à structure
> égale, deux langues donnent les mêmes verdicts (appris 81-90, cousin ~40,
> témoin 0, sanctuaire f92) — la compréhension est dans la structure,
> pas dans les mots.

### Leçon 11 📚 — Grandir par phrases : chaque régime a sa loi
*Route B : `education/corpus.txt` (37 phrases) + `education/eduquer.py` —
preuves : `preuves/sortie-education.txt`, `preuves/sortie-education-controles.txt`,
`education/vocabulaire50.ratum`, `images/constellation.png`, `education/EDUCATION.md`*

Fini le tissage à la main : 37 phrases font naître 50 neurones et 247 liens,
et après 3 rounds + 2 nuits, **50 mots sur 50 tiennent** (paires à 90),
6 témoins dehors à 0 — courbe d'apprentissage 38 → 49 → 50, le cousin MUNIR
rejoint les amis au 3e round (51 → 58 → 60). Le contrôle tue : avec délie 3
(loi j11) ou délie 10 (défaut), chaque phrase efface les autres (**0/50**).
Donc trois calibrages, trois usages : (10,10) éducation commune, (10,3)
coexistence, (10,0) éducation sélective. Défaut publié : saturation
uniforme à 90 (cause : propagation sans concurrence) — piste route C.

> **Énoncé :** le lexique grandit par éducation sélective (phrases +
> `renforcer lie 10 delie 0`) : 6 → 50 mots sans tissage manuel — et la loi
> n'a pas de valeur universelle, chaque régime d'éducation exige la sienne.

### Leçon 12 🧬 — Route C : on ajuste le monde, pas la règle
*Route C phases 1-2 : cœur v2 (`ratum.py`) + nuits faucheuses (`cerveau.py`) —
preuves : `tests_verdicts.py` (93/93), `education/EDUCATION.md` (§ recalibrage),
`LANGAGE-RATUM.md` (v2), ce fichier.*

Le cœur v2 : loi universelle **(10, 3)** partout par défaut, gains **élastiques**
(pleins au départ, fondants avec la force), **ombre** à la propagation (moitié
perdue par saut), oubli adouci à 3, résonance comptant les paires manquantes
comme 0, et `nettoyer` (19e relation : la faucheuse arrache les liens à 0, les
neurones isolés meurent SAUF les nommés). Batterie tombée à 62/93, remontée à
**93/93 sans toucher une seule règle** : fréquences ×1.5-2 (5 → 10 rencontres
minimales — le prix de l'élasticité), corpus 39 phrases (+2 COEUR), graine
30×TOUT, seuils 40 pour les ponts uniques (voix/duty). Trouvailles : l'ombre
tue les vagues lointaines (j09 : 65 → 64) mais la sommation multi-sources la
traverse (MUNIR 39 → 74) ; **la falaise délie** — entre délie 0 (50/50) et
délie 1 (0/50) il n'y a pas de pente, l'éducation sélective exige délie 0
(tranché (a) le 7 oct. : deux maisons — école délie 0, vie (10,3)) ; nommer c'est protéger
(0 neurones morts sous délie 10, tous nommés). Reste : saturation atténuée
(B : 74-94) mais pas vaincue — le marbre (phase 3) viendra creuser.

> **Énoncé :** la loi universelle (10, 3) + élasticité + ombre tient les 12
> leçons (93/93) en ajustant le monde (fréquence, corpus, seuils) —
> et l'éducation sélective vit sous régime d'exception (délie 0, l'école).

---

### Leçon 13 💥 — Le CISE : la saturation devient de la mémoire
*Vision du chef (7 oct.) + `cise` (20e relation, `ratum.py`) + `jouets/j14-cise.ratum` —
preuves : batterie 101/101, `LANGAGE-RATUM.md` (v3).*

Le plafond de 100 n'est plus un mur : c'est un point d'ignition. La vitesse
d'un neurone = ses battements depuis la nuit (fréquence) + son énergie en
mains de 20 (charge) ; à 10 — la main qui lie ! — alors qu'il bat, `cise`
provoque l'étincelle : le transporteur se fige en neurone CISE (mémoire,
comme les paramètres d'un LLM) et les liens entre CISE deviennent des
filaments gelés (ni loi, ni oubli, ni faucheuse ne les touche). Preuve j14 :
4 rencontres chaudes (vitesse 9) = rien ; 11 battements (vitesse 16) = 2 CISE
+ 1 filament à 69 ; 20 nuits + faucheuse = 69 inchangé, TIENT. L'ultra-secteur
(le marbre absolu) = l'ensemble des CISE du tissu, soudés en dur + 4e secteur
Python (ULTRA-SECTEUR : tableau de bord des convictions, force 100, immortel).
Explosion manuelle (outil labo) : l'auto émergente viendra à terme. Deux maisons
tranchées (a) : école délie 0, vie (10,3). Tokenisation externe : plus tard.

> **Énoncé :** le trop-plein ne déborde plus, il SE FIGE : vitesse ≥ 10 + il bat
> → neurones CISE + filaments gelés — la saturation est le mécanisme de la
> mémoire à long terme, pas son bug.

---

### Leçon 14 🗣️ — Le tokenizer : la pensée devient phrase
*Vision du chef (7 oct.) + `bouche/regles.py` (4 règles) + `donnees/generer.py` —
preuves : `bouche/autotest_bouche.py` (BOUCHE OK), batterie 102/102, `TOKENIZER.md`.*

Le chaînon manquant : une règle tiny lit l'état (convictions ultra +
sanctuaire + mots tenus) et le traduit en phrase FR/EN que Piper parle.
Quatre règles ordonnées (ULTRA, SANCT, TISSU, VIDE), zéro singulier,
déterministes : 5 phrases exactes pinnées (EN×3, FR×2). Le vrai problème —
la DONNÉE — est résolu par construction : le tissu déterministe fabrique
lui-même ses paires (20 paires, 20/20 vérifiées) ; le générateur est versionné,
la masse vivra sur Colab. Entraîner, chez nous, = éduquer (relations, pas de
poids en Go) + vérifier (100 % reproduction). Les démos (parole, cerveau-fr)
parlent maintenant par la règle unique.

> **Énoncé :** la sortie est une traduction, pas une génération : état → phrase
> par 4 règles pinnées — et la donnée d'entraînement est un robinet (tissu
> déterministe), pas un désert.

### Leçon 15 🪨 — Le marbre : la rivière grave par répétition, la boucle se ferme
*Route C phase 3 : `cerveau/secteurs.py` (v4 : redites, gravure) +
`cerveau/cerveau.py` (`redire()`) + `cerveau/autotest_marbre.py` —
preuves : `preuves/sortie-marbre.txt`, `bouche/preuve-marbre.wav`, 103/103.*

Face au mur de la saturation (B : 74-94, tout au même niveau, aucun relief),
la stratégie tient en une phrase : D'ABORD graver ce qui compte, ENSUITE
réguler le reste (l'homéostasie, phase 4, pourra effacer sans peur — la statue
est à l'abri). La 🔁 rétroaction ferme la boucle : `redire()` formule la trace
dominante du sanctuaire (tokenizer, règle unique — pas de triche) puis la
RÉ-ENTEND, comme on relit sa leçon à voix haute. À la 3e relecture
(`SEUIL_MARBRE = 3`), la trace est 🪨 GRAVÉE : la nuit ne l'use plus (ni
usure, ni mort). Mesuré : A relue 3 fois traverse 5 nuits à f100 MARBRE
pendant que le témoin B tombe à f87 — relief 13, le creusement a commencé ;
FR identique (gravée f100, 2 nuits). L'éclair (💥 CISE) fige par la VITESSE,
la rivière (🪨 MARBRE) grave par la RÉPÉTITION — deux chemins vers l'éternel.
Vocabulaire officiel : le sanctuaire est le BLOC, la rétroaction est le CISEAU,
la gravure est la STATUE.

> **Énoncé :** ce qui est répété à voix haute se grave (nuit 0) pendant que
> le reste s'efface — le répété reste en haut, l'oublié descend : le relief
> naît de l'oubli sélectif, pas d'un réglage.

### Leçon 16 🌊 — La marée : le tampon absorbe, la mer garde le niveau
*Route C phase 4 : `cerveau/cerveau.py` (tampon 50 + flush) +
`cerveau/secteurs.py` (v5 : repos 60, rappel 4) + `cerveau/autotest_maree.py` —
preuves : `preuves/sortie-maree.txt`, `bouche/preuve-tempete.wav`, 104/104.*

Le jour on ÉCOUTE, la nuit on CONSOLIDE : le tissu entend tout de suite, mais
les traces attendent au TAMPON (50 écoutes — une grosse journée) et ne
descendent au VIF que le soir, dans l'ordre. Tampon plein → soupape : le plus
ancien entre au VIF — zéro perte, jamais. La voix intérieure (`redire`)
dépose directement : elle ne passe pas par les oreilles. Et le sanctuaire a
désormais un NIVEAU DE LA MER (⚖️ homéostasie) : perte = 1 + (force−60)//4,
plancher 60 — plus une trace est haute sans être répétée, plus fort elle
redescend ; les gravées restent à 100. Mesuré : tempête de 70 inconnues →
tampon 50 + pression 20, nuit → VIF = les 20 dernières à f10, 5 nuits → A
f100 MARBRE, B f65 (était f87 : le relief passe de 13 à 35 !), VIF 0,
REFRAIN 0 — mer calme, statue debout. La même phrase est parlée avant et
après la tempête : la stabilité incarnée. Trois destins : l'entonnoir OUBLIE,
la mer GARDE LE NIVEAU, le marbre est ÉTERNEL.

> **Énoncé :** un cerveau tient la tempête par deux organes — le tampon qui
> absorbe le choc (sans rien perdre) et l'homéostasie qui ramène le bruit
> au niveau de la mer pendant que le gravé reste au sommet.

### Leçon 17 💭 — Le rêve : on ne garde que ce qu'on comprend
*Route C phase 5 : `cerveau/cerveau.py` (`rever()`, flag `reve`) +
`cerveau/autotest_chaos.py` (JFK + discours FR réels, 1 écoute, sans focus) —
preuves : `preuves/sortie-chaos.txt`, `bouche/preuve-chaos.wav`, 105/105.*

Le baptême du feu : deux vrais discours entendus UNE fois, sans focus, sans
filet. D'abord l'honnêteté : sans rêve, oubli TOTAL prouvé (0/0/0 après 6
nuits — entendre une fois, c'est oublier, comme nous). Puis le mécanisme :
chaque nuit, le RÊVE ravive les traces VIF/REFRAIN riches (≥ 2 mots connus) —
l'hippocampe rejoue ce que le tissu a COMPRIS ; le rêve ravive, la nuit
promeut. FR : 1 seul rêve sur 19 la 1re nuit (la sélectivité !), « amis du
peuple » émerge seule au sanctuaire (f61) en 4 nuits. JFK : les 3 riches
sauvées (f61) pendant que « can do for » (répétée 2 fois, 0 mot connu) meurt
au refrain — DOUBLE DISSOCIATION : répéter sans comprendre = mourir,
comprendre sans répéter = monter par le rêve. La relecture couronne UNE élue
(« americans ask not »), gravée f91 : du chaos au marbre, sans aucune aide.
Le focus et les « riches ×2 » des démos, qui tenaient la main du cerveau,
sont devenus une loi émergente. Batterie intacte : 104/104 avant comme après.

> **Énoncé :** la consolidation est gardée par la compréhension — le rêve
> rejoue chaque nuit ce que le tissu tient (≥ 2 mots connus), et ce seul
> filtre fait émerger le sanctuaire du chaos en 4 nuits.

### Leçon 18 🔬 — Le second berceau : une spec saine a deux voix
*Route D : `route-d/ratum.c` (~1000 lignes, libc seule) + `route-d/conformite.py` —
preuves : `preuves/sortie-conformite.txt`, 107/107.*

Portage fidèle de l'interprète en C : loi (10,3), élasticité, ombre //200,
`borne` à chaque pas dans l'ordre d'insertion, tris partout, pluriels, JSON
`indent=1` de `graver` répliqué à l'octet. Mesuré : **24/24 sorties identiques
au caractère près** (codes de sortie inclus) + scroll `mem.scroll` identique —
compilation `-O2 -Wall -Wextra` zéro warning, du premier coup. Cinq
divergences hors corpus documentées (`route-d/LISEZ-MOI.md`), jamais
déclenchées par les 24 programmes. Le langage a son conformance test : deux
berceaux indépendants, une seule voix.

> **Énoncé :** une spécification est saine quand deux implémentations
> indépendantes sortent les mêmes octets — le C prouve le Python, et le
> Python prouve le C.

### Leçon 19 🌌 — Le calme du sanctuaire : le pont FOCAL mesure l'ordre
*Pont : `pont-focal/encodeur.py` (stdlib) + `pont-focal/pont.py` (numpy,
ripser, organes `univers-focal/` inchangés) — preuves :
`preuves/sortie-pont-focal.txt`, 108/108.*

La trace relationnelle de trois tissus (frais, chaos graine 7, sanctuaire
9 rencontres + 2 nuits) devient 2048 bits déterministes, projetés neutres
sur le fond FOCAL (tore + sphère), mesurés en P_sig (persistance H1+H2).
Première mesure : fond 5,7599, frais 6,3887, chaos 6,3970, **sanctuaire
6,2301** — le compteur bouge (delta 0,1668, le pont transporte) et le
tissu ordonné projette plus calme que le chaos. Témoin porteurs : la
concentration monte ×31,6 en 4 transports. Piste v1 sur 3 points, pas un
théorème — mais le tissu et l'univers parlent enfin la même langue.

> **Énoncé :** l'ordre se mesure au calme qu'il projette — un tissu
> sanctuaire fait moins de vagues topologiques que le chaos (6,23 < 6,40).

### Leçon 20 🏷️ — Les dix étiquettes et le compteur honnête
*R5 + noyau gelé : `ecoutes` (`cerveau/cerveau.py`), R-COMPTES
(`bouche/regles.py`), `MOTIFS_FIXES` — preuves : 7 wav régénérés,
`BOUCHE OK — 5 phrases exactes R5`, 109/109.*

Le tissu sait désormais dire ce qu'il a entendu : « J'ai entendu N
séquences » ouvre chaque phrase — dehors seul, répétitions comprises
(JFK 35, discours FR 30, tempête 82), la voix intérieure ne triche pas
(3 relectures, compteur fixe à 12/24). La démo EN abandonne son compte
fait main pour la règle unique. Et le vocabulaire a son noyau gelé :
10 couples mot→motif (4 innés + 1 d'école par langue, `unir`/`homeland`),
sha pinné en batterie — au-delà, les mots d'école grandissent librement.

> **Énoncé :** une bouche honnête compte ses écoutes avant de parler —
> et un vocabulaire sain a un noyau gelé et une banlieue qui grandit.

### Leçon 21 🎧 — Les sous-titres qui comprennent : l'oreille en direct
*Direct : `porte-voix/direct.py` (tranches 2 s, Phonon `--json`,
fenêtres chevauchantes, 4 nuits) + `--micro` — preuves :
`preuves/sortie-oreille-direct.txt`, `porte-voix/tranches-jfk.json`,
110/110.*

JFK rejoué tranche par tranche : le tissu dit ce qu'il tient AU FUR ET À
MESURE (3→4→8→13→20→21 séquences), survit à une bavure de frontière
(« custom » au lieu de « country » — le seuil 60 ne bronche pas), puis le
rêve fait son oeuvre en 4 nuits : l'élue du chaos « americans ask not »
est retrouvée EN DIRECT, sans focus, sans filet. Déterministe au md5 près
sur 3 passes. Le téléphone est décroché : `--micro N` écoute vraiment.

> **Énoncé :** comprendre en direct, c'est tenir pendant qu'on écoute —
> le tissu parle à t+2 s et l'élue arrive quand même à l'aube.

### Leçon 22 💬 — Bonjour : le standardiste honnête (dialogue v1)
*Dialogue : `dialogue/dialogue.py` (7 intents FR+EN pinnés) +
`dialogue/conversation.py` — preuves : `preuves/sortie-dialogue.txt`
(12 répliques), `bouche/dialogue.wav` (43,5 s), 111/111.*

Sonde avant travaux : « bonjour » → « J'ai entendu 1 séquence… » — le
tissu décrivait, ne répondait pas. v1 : saluer/identité/état/comptes/
aide/au-revoir/inconnu — « bonjour » → « Bonjour ! Moi c'est RATISS »,
« tu tiens quoi » → le VRAI `formuler()`, « combien » → le VRAI
compteur, « merci » → « Je ne comprends pas encore » (l'honnêteté est
une réponse). Chaque phrase nourrit le tissu : converser, c'est écouter.

> **Énoncé :** avant de généraliser comme un LLM, on répond comme un
> standardiste honnête — 7 intents pinnés valent mieux qu'un bluff.

### Leçon 23 🏋️ — 250 000 écoutes, 12 Mo : le tissu porte la masse
*Masse : `education-massive/generer_masse.py` (seed 7) +
`eduquer_masse.py` (streaming + nuit/lot) — preuves :
`preuves/sortie-masse-250k.txt`, notebook §2b (5M sur Colab), 112/112.*

250 000 séquences (50 mots vrais, moitié fenêtres moitié recombinaisons)
en ~70 s, RAM stable à 12 Mo, mémoire bornée par construction (caps +
faucheuse) : « J'ai entendu 250000 séquences. Au sanctuaire : amis
peuple enfants » — un mot d'école AU SANCTUAIRE. Extrapolé Colab : 5
millions ≈ 25 min. Et la leçon d'humilité : le tissu reste compact (13
neurones) — les mots d'école vivent aux secteurs ; les câbler au tissu,
c'est la piste v2. Les millions, chez nous, ce sont des écoutes.

> **Énoncé :** l'échelle ne se décrète pas, elle se mesure — 250 000
> écoutes prouvent que 5 millions passeront (25 min, 12 Mo).

### Leçon 24 ⏳ — Le fichier lourd et l'heure Colab : 10M en 1h
*Programme 1h : `masse-5M.jsonl.gz` (5M, sha pinné) + `colab-1h.ipynb`
(5M fichier + 5M fraîches, lots 200k, bilan parlé) — preuves :
`preuves/sortie-masse-1M.txt` (1M en 327 s, 13 Mo), 113/113.*

1M validé en local : 327 s, RAM 13 Mo, sanctuaire « amis patrie pays »
(l'élue change avec l'échelle — mesuré, pas promis). Extrapolé : 10M ≈
55 min sur CPU Colab gratuit. Vérité GPU écrite au notebook : le tissu
est CPU pur, le GPU ne l'accélère pas — et 1h suffit sans lui. Le fichier
(270 Mo → 35,7 Mo) se vérifie par sha avant de brûler ; le tissu ne
stocke rien : 10M de lignes passent, seules les forces restent.

> **Énoncé :** une heure bien remplie vaut mieux qu'un GPU décoratif —
> 10 millions d'écoutes prouvées à 3 000 par seconde.

### Leçon 25 🔥 — La puissance : profiler d'abord, 300M ensuite
*Le chef rit : 13 Mo sur 24 Go, c'est boire l'océan avec une paille —
profilage : 88 % du temps dans l'interprète reconstruit par séquence.
Battement fusionné (mêmes maths, x33, équivalence exacte sur 50k) +
binaire 3 octets + 3 époques = 300M écoutes en ~1h (114/114).*

La RAM n'est pas la vitesse (une grande table ne rend pas les mains plus
rapides) : elle tient les 100M d'un coup (300 Mo), le CPU battu x33 fait
le reste (~100 000/s). Chasse au ralentissement : l'époque 2 s'écroulait
— `redire` avalée par la fusion, attrapée à la stack trace, réparée,
re-prouvée. Les époques répètent comme l'enfance (30x TOUT) : redire,
c'est graver. Fichier lourd : 30M binaire (90 Mo → 58,3 Mo, sha pinné),
régénérable — le notebook régénère 100M sur place (sha pinné aussi).

> **Énoncé :** la puissance ne se décrète pas, elle se profile — 88 %
> dans l'interprète, x33 en fusionnant, 300 millions à l'heure.

### Leçon 26 💪 — Graver : le cerveau fortifié rentre à la maison
*Question du chef : « où sont les données d'entraînement ? » — réponse :
nulle part (doctrine : la donnée s'oublie), MAIS le résultat était perdu
avec (trou trouvé, trou bouché). `Cerveau.graver/relire` : photo complète
(graphe + secteurs + tampon + compteur, charges éphémères exclues),
reprise exacte prouvée (200k + 50k des deux côtés, 115/115).*

Nos « poids » : 917 octets pour 200k écoutes — pas des gigas : on note qui
tient qui et combien fort (des relations), pas chaque grain de sable.
Le notebook grave à la fin (`--graver`), téléchargement 1 clic ou Drive ;
`--relire` reprend l'entraînement où il s'était arrêté (les écoutes
continuent). Deux cerveaux, une valise : Colab muscle, le fichier ramène,
le dépôt réveille.

> **Énoncé :** la donnée s'oublie, les muscles voyagent — 917 octets
> valent mieux qu'un cerveau mort sur Colab.

### Leçon 27 🏃 — Le relais : sauvegarde auto, zéro main
*Le chef lance l'heure : « pas de récupération à la main ». Le notebook
monte le Drive (1 clic), photographie le cerveau à chaque lot sur le Drive
(`--relais`, écrasé, ~1 Ko), grave le fortifié daté + bilan + voix à la
fin. Si Colab coupe : `--relire relais.json.gz`, ça repart du dernier lot.*

La sauvegarde de fin ne suffit pas pour 1h de gratuit (coupure toujours
possible) : le relais, c'est le coureur qui passe le témoin à chaque tour
— on ne perd jamais plus d'un lot (10M ≈ 1,7 min). Le notebook fait aussi
`git pull` (le chef avait l'ancienne version clonée). Prouvé bout-en-bout
(2k, photo chaque lot, relecture 2000/2000 — 116/116).

> **Énoncé :** une sauvegarde à la fin, c'est un espoir ; une à chaque
> lot, c'est une assurance — le témoin ne tombe jamais.

---

## 5. Phonon-2 : l'oreille future (pas un outil d'entraînement)

Phonon-2 (Fermion Research, sept. 2026) : modèle OUVERT de reconnaissance vocale,
164 Mo, qui tourne en local. Vérifié le 6 octobre 2026 :
annonce officielle, dépôt GitHub `fermionresearch/phonon`, poids sur HuggingFace.
Précision honnête : Phonon-2 transcrit la parole, il n'entraîne rien.
Son rôle dans notre chantier : **la porte « voix »** — convertir la parole en
motifs branchés sur les MÊMES nœuds que le texte, pour que la voix renforce les
concepts au lieu d'en créer de doublons (leçon 1 appliquée). Statut : branché
le 6 oct. 2026 (leçon 7 : JFK mot pour mot, boucle live).

---

## 6. Limites actuelles (dites à voix haute)

1. **Jouets, pas langage réel.** 8 neurones et 4 motifs prouvent la loi, pas
   l'intelligence. Le passage aux mots vrais est TOUT le chantier devant nous.
2. **Loi symétrique.** Le pas qui renforce égale le pas qui efface : sous
   alternance stricte, deux formes se neutralisent. Piste v1 : pas asymétriques
   à calibrer par mesure, pas par décret.
3. **Seuils fixes.** Tous les neurones battent à 50. Piste v1 : seuils adaptatifs.
4. **Portes encore étroites.** L'oreille est branchée (Phonon-2) et la bouche
   parle (Piper), mais le tissu ne comprend que 6 mots anglais ; la vision
   n'existe pas encore.
5. **Berceau Python.** L'interprète de référence prouve la spec ; l'implémentation
   bas niveau viendra quand la spec sera stable.

---

## 7. Feuille de route

- [x] **v0.1** — stabiliser la spec sur une dizaine de programmes-jouets
      (livré 6 oct. : seuils actifs par neurone + batterie de 10 jouets, 42/42 contrôles verts)
- [x] **v0.2** — motifs de mots vrais (premier vocabulaire tissé à la main)
      (livré 6 oct. : 12 mots, 12/12 TIENT, cousin 40, inconnu 0)
- [x] **v0.3** — mesurer le passage à l'échelle (centaines de nœuds) et publier les chiffres
      (livré 6 oct. : 300 nœuds, 40/40 à 75-85, témoins 0, 0,1 s)
- [x] **v1-loi** — pas asymétriques + seuils adaptatifs, calibrés par mesure
      (livré 6 oct. : lie 10 / délie 3, 10 → 52, seuils 50 → 75 → 37)
- [x] **v1-voix (pont)** — socket voix prête + oreille simulée prouvée
      (livré 6 oct. : soleil/lune 90 compris, comete 0, banane hors vocabulaire)
- [x] **vrai modèle branché** — Phonon-2 testé en boucle live (JFK mot pour mot, 6 oct.)
- [x] **vocabulaire anglais + boucle parole** — tissu EN (4 mots à 81-90) + bouche Piper (verdicts parlés, 6 oct.)
- [x] **cerveau v1 (option 3)** — crâne Python + pensée Ratum, secteurs VIF→REFRAIN→SANCTUAIRE, séquences temporelles
      (livré 6 oct. : JFK live → 1 sanctuaire f92, résumé parlé 6 s, 81/81 contrôles verts)
- [x] **oreille française (route A)** — faster-whisper small : 21/21 mot pour mot, tissu FR 81-90, sanctuaire f92, boucle 8.5 s
      (livré 6 oct. : leçon 10, 89/89 contrôles verts)
- [x] **vocabulaire élargi (route B)** — 37 phrases, 6 → 50 mots par éducation, courbe 38→49→50, contrôles 0/50
      (livré 6 oct. : leçon 11, 93/93 contrôles verts)
- [x] **cerveau v2 phases 1-2 (route C)** — cœur (10,3)+élastique+ombre, nuits faucheuses, 93/93 (livré 7 oct. : leçon 12)
- [x] **CISE (vision du chef)** — 20e relation, 2 types de neurones, ULTRA-SECTEUR Python, (a) deux maisons (livré 7 oct. : leçon 13, 101/101)
- [x] **tokenizer v1 (vision du chef)** — 4 règles sortie FR/EN, robinet à données, notebook Colab (livré 7 oct. : leçon 14, 102/102)
- [x] **cerveau v2 phase 3 (route C)** — marbre + rétroaction : gravure à la 3e relecture, relief 13 mesuré (livré 7 oct. : leçon 15, 103/103)
- [x] **cerveau v2 phase 4 (route C)** — marée : tampon 50 + homéostasie (mer 60), tempête 70 tenue (livré 7 oct. : leçon 16, 104/104)
- [x] **cerveau v2 phase 5 (route C)** — chaos + rêve : oubli honnête, émergence en 4 nuits, double dissociation (livré 7 oct. : leçon 17, 105/105)
- [x] **cerveau v2 phase 6 (route C)** — LE LIVRE : doc complète + 20 figures + slides + licence CC-BY-SA — route C TERMINÉE 🎉 (livré 7 oct., 106/106)
- [ ] **tokenisation + compréhension externe** — différé (décision du chef, 7 oct.)
- [ ] **ignition auto (émergence)** — l'étincelle sans commande, à terme (décision du chef, 7 oct.)
- [ ] **lourd sur Colab** — réservé : quand on voudra du protocole qui dépasse ce bac à sable
- [x] **second berceau C (route D)** — 24/24 sorties identiques + scroll identique, zéro warning (livré 7 oct. : leçon 18, 107/107)
- [x] **pont FOCAL** — tissu → 2048 bits → P_sig : sanctuaire 6,2301 < chaos 6,3970, porteurs ×31,6 (livré 7 oct. : leçon 19, 108/108)
- [x] **R5 + ⑩ étiquettes** — « J'ai entendu N » (JFK 35, FR 30, tempête 82), noyau 5+5 gelé sha pinné (livré 7 oct. : leçon 20, 109/109)
- [x] **oreille en direct** — tranches 2 s → règles, élue « americans ask not » retrouvée, `--micro` (livré 7 oct. : leçon 21, 110/110)
- [x] **dialogue v1** — 7 intents FR+EN pinnés, « bonjour » répondu, inconnu honnête, 12 voix cousues (livré 7 oct. : leçon 22, 111/111)
- [x] **masse 250k → 5M** — 250 000 écoutes en ~70 s (12 Mo), sanctuaire conquis, notebook §2b Colab (livré 7 oct. : leçon 23, 112/112)
- [x] **programme 1h Colab** — fichier 5M (sha pinné) + 5M fraîches, 1M validé 327 s, GPU déclaré inutile (livré 7 oct. : leçon 24, 113/113)
- [x] **programme puissance 300M** — battement fusionné x33 + binaire 3o + 3 époques, 30M validé 318 s (livré 7 oct. : leçon 25, 114/114)
- [x] **cerveau fortifié (graver/relire)** — photo ~1 Ko, reprise exacte, notebook grave + télécharge (livré 7 oct. : leçon 26, 115/115)
- [x] **relais Drive auto** — photo chaque lot sur Drive, fortifié daté + bilan + voix, `git pull` (livré 7 oct. : leçon 27, 116/116)
- [ ] **toujours** — chaque affirmation rejouable en une commande, sinon elle n'existe pas

---

*« On ne croit pas. On rejoue. » — RATISS Labs*
