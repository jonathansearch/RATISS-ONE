# ⚛️ RATISS-ONE — Réseaux de Neurones Intriqués + langage Ratum

**RATISS Labs · Jonathan Evina · Yaoundé 🇨🇲 · MIT**
*« On ne croit pas. On rejoue. »* 🔁

> Un réseau de neurones intriqué (RNI) n'est ni une usine à prédictions,
> ni un entrepôt de données : c'est un **tissu vivant** où des neurones au
> destin lié apprennent par rencontres, sous une seule loi —
> *ce qui se tient ensemble se renforce, ce qui se disjoint s'efface.*
> Le langage **Ratum** est la langue de ce tissu : des mots, pas de formules.

---

## ⚡ En 30 secondes

| 🧠 | Élément | Verdict mesuré |
|---|---|---|
| 🌱 `rni-simple.ratum` | 3 neurones, 5 rencontres | forme apprise 10 → **60/100**, étrangère **0** |
| 🔥 `rni-complexe.ratum` | 8 neurones, éducation en 4 phases | SOLEIL **90**, LUNE **90**, témoin ORAGE **0** |
| 🌊 `rni-interference.ratum` | 2 formes sans rien en commun | le nouveau **chasse l'ancien** (70 → 10) |
| 🧪 `jouets/` (v0.1) | 10 jouets, un par recoin du langage | seuils, pas, oubli, photo, choix, plafond, vagues, erreur nette |
| 📖 `vocabulaire.ratum` (v0.2) | 12 mots vrais + cousin + inconnu | **12/12 TIENT (80-90)**, cousin 40, inconnu 0 |
| 📏 `echelle/` (v0.3) | 300 neurones, 1200 liens, 50 motifs | **40/40 TIENT (75-85)**, témoins 0, 0,1 s |
| ⚖️ `v1-coexistence` (v1) | symétrique vs asymétrique, même tissu | 10/10 ❌❌ → **52/52 ✅✅**, seuils 50→75→37 |
| 👂 `porte-voix/` (v1) | pont transcription → motifs, oreille simulée | soleil/lune **compris (90)**, comete 0, banane hors vocabulaire |
| ⚙️ `ratum.py` | interprète de référence | 19/19 programmes, **70/70 contrôles verts** |
| 📜 `LANGAGE-RATUM.md` | spec du langage | 17 relations, chacune expliquée |

---

## 🚀 Rejouer (règle R7 : une commande suffit)

```bash
git clone https://github.com/jonathansearch/RATISS-ONE.git
cd RATISS-ONE
python3 ratum.py rni-simple.ratum        # le minimal
python3 ratum.py rni-complexe.ratum      # l'éducation complète
python3 ratum.py rni-interference.ratum  # la vraie interférence
python3 tests_verdicts.py               # vérifie les 70 contrôles (19 programmes)
```

Zéro dépendance : que du Python standard. Déterministe : mêmes entrées, mêmes sorties, toujours.

---

## 🗺️ Lire dans l'ordre

| Ordre | Fichier | Pourquoi |
|---|---|---|
| **1** | [`RNI-DEFINITION.md`](RNI-DEFINITION.md) | Ce qu'est un RNI, ce qu'il n'est pas, les 2 leçons mesurées |
| **2** | [`LANGAGE-RATUM.md`](LANGAGE-RATUM.md) | La spec : chaque relation du langage, expliquée |
| **3** | `rni-simple.ratum` | L'algorithme simplifié, en Ratum pur |
| **4** | `rni-complexe.ratum` | L'algorithme ultra-complexe, en Ratum pur |
| **5** | `rni-interference.ratum` | La preuve de l'interférence vraie |
| **6** | `preuves/` | Les sorties rejouées le 6 octobre 2026 |

---

## 🛡️ Honnêteté scientifique (lire avant de citer)

1. **Intrication computationnelle, PAS quantique.** Dans un RNI, « intriqué » veut dire :
   des neurones dont les destins sont liés par des liens à force variable, sous la loi
   du renforcement. Aucun phénomène quantique n'est invoqué ni simulé ici.
2. **Le berceau n'est pas le langage.** `ratum.py` est l'établi qui exécute le Ratum
   (comme un four cuit le pain — le four n'est pas le pain). Les programmes `.ratum`
   sont 100 % Ratum : aucune ligne de Python déguisée. Une implémentation bas niveau
   viendra quand la spec sera stable.
3. **Simulation, pas mesure physique.** Tous les chiffres sont des sorties du modèle
   Ratum v0, rejouables. Aucune puce, aucun cerveau, aucun QPU n'est mesuré ici.
4. **Ce qui est prouvé / ce qui ne l'est pas.** Prouvé (dans le modèle) : la répétition
   creuse les chemins, le partage d'un nœud lie les formes, le disjoint s'efface,
   l'inconnu est rejeté. Pas prouvé : que cela passe à l'échelle du langage réel —
   c'est la suite du chantier, pas un résultat.

---

## 🧱 Architecture du dépôt

```
RATISS-ONE/
├── README.md               # ce manifeste
├── RNI-DEFINITION.md       # définition scientifique + leçons + feuille de route
├── LANGAGE-RATUM.md        # spec Ratum v0 : les 17 relations expliquées
├── rni-simple.ratum        # algorithme simplifié (RNI minimal)
├── rni-complexe.ratum      # algorithme ultra-complexe (éducation complète)
├── rni-interference.ratum  # preuve de l'interférence vraie
├── vocabulaire.ratum       # v0.2 : 12 mots tissés à la main
├── echelle/                # v0.3 : grand tissu + MESURES.md
├── v1/                     # v1 : MESURES-V1.md (loi à deux mains)
├── v1-coexistence.ratum    # v1 : symétrique vs asymétrique
├── porte-voix/             # v1 : pont.py + PHONON.md + ecoute.ratum
├── outils/                 # tisseurs déterministes
├── jouets/                 # batterie : j01..j12
├── ratum.py                # interprète de référence (le berceau)
├── tests_verdicts.py       # vérification automatique des 42 contrôles
├── preuves/                # sorties d'exécution datées
├── MANIFESTE.json          # empreintes SHA-256 de chaque fichier
└── LICENSE                 # MIT
```

---

## 👂 Phonon-2 : l'oreille future

Phonon-2 (Fermion Research, sept. 2026) est un modèle ouvert de reconnaissance
vocale locale (164 Mo, anglais). Ce n'est pas un outil d'entraînement : ce sera
la **porte « voix »** du tissu — l'oreille qui convertira la parole en motifs,
branchée sur les mêmes nœuds que le texte (intrication naturelle).
Voir la feuille de route dans `RNI-DEFINITION.md`.

---

*RATISS Labs · auteur unique : Jonathan Evina · ORCID 0009-0000-4092-5313*
*« On ne croit pas. On rejoue. »*
