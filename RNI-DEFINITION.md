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
- [ ] **vocabulaire élargi (route B)** — grandir le lexique par éducation, 6 → 50 mots (choix du chef, 6 oct.)
- [ ] **cerveau v2 (route C)** — érosion du marbre, phrases libres, anti-saturation (choix du chef, 6 oct.)
- [ ] **lourd sur Colab** — réservé : quand on voudra du protocole qui dépasse ce bac à sable
- [ ] **v2 bas niveau (route D)** — implémentation C de l'interprète, mêmes sorties au caractère près (choix du chef, 6 oct.)
- [ ] **toujours** — chaque affirmation rejouable en une commande, sinon elle n'existe pas

---

*« On ne croit pas. On rejoue. » — RATISS Labs*
