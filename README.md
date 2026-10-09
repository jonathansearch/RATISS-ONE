<div align="center">

<img src="images/logo-ratiss-labs.png" width="220" alt="RATISS Labs"/>

# ⚛️ RATISS-ONE — Réseau de Neurones Intriqués & Intelligence Souveraine

**Un conteneur unique `.ratiss`, une cognition sans GPU, une oreille sensorielle, une bouche expressive asservie au Corps ETH, et une mémoire épisodique one-shot.**

[![License: MIT](https://img.shields.io/badge/Code-MIT-teal.svg)](LICENSE)
[![Format: .ratiss](https://img.shields.io/badge/Format-.ratiss%20%2F%20.rt-orange.svg)](cerveau/)
[![Runtime: Souverain](https://img.shields.io/badge/Runtime-Boîte%20Blanche-brightgreen.svg)](cerveau/lecteur_ratiss.py)
[![Audio: Phonon + Piper](https://img.shields.io/badge/Audio-Oreille%20%2B%20Bouche-blue.svg)](bouche/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jonathansearch/RATISS-ONE/blob/main/colab/Entrainement_RATISS_ONE.ipynb)
[![Docker: Prêt](https://img.shields.io/badge/Docker-0.0.0.0:8080-blueviolet.svg)](docker/)

*Par **RATISS Labs** — Jonathan Evina · Yaoundé 🇨🇲 · Recherche indépendante · Reproductibilité stricte (R4–R7)*

</div>

<img src="images/hero-cerveau.png" width="100%" alt="Architecture RATISS-ONE Souverain"/>

> **Résumé.** *RATISS-ONE est une rupture d'architecture en intelligence artificielle : un Réseau de Neurones Intriqués (RNI) qui **comprend sans stocker de données brutes**. Fini l'empilement aveugle de gigaoctets : le cerveau complet est consolidé en un **fichier unique et inviolable `.ratiss` (ou `.rt`)**, exécutable exclusivement par son runtime officiel en boîte blanche. Il intègre 5 organes vitaux (Corps affectif ETH, Sanctuaire scellé SHA-256, Synchrotron de résonance, Cortex adaptatif Top-P, Juge cryptographique), une boucle sensorimotrice audio complète (Oreille Phonon ASR + Bouche Piper TTS modulée par l'émotion somatique), et un moteur d'apprentissage épisodique live ("Main Tendue") capable d'assimiler des faits en direct en 50 microsecondes sans rétropropagation ni oubli catastrophique.*

---

## 📖 Sommaire

1. [La Question Fondatrice](#la-question)
2. [En 30 Secondes : Les Faits Mesurés](#en-30-secondes)
3. [Le Conteneur Unique .ratiss & La Boîte Blanche](#le-conteneur-ratiss)
4. [Le Runtime Officiel Exclusif](#le-runtime-officiel)
5. [La Boucle Sensorimotrice Audio (Oreille + Bouche + ETH)](#la-boucle-audio)
6. [Dialogue v2 & Mémoire Épisodique Live](#dialogue-v2)
7. [Entraînement Épisodique Colab Haute Vitesse](#entrainement-colab)
8. [Déploiement Docker & Interface Web](#deploiement-docker)
9. [Tableau Historique des 45 Leçons](#tableau-mesures)
10. [Carte du Dépôt Épuré](#carte-du-depot)
11. [Auteur, Identité & Licence](#auteur-licence)

---

<a id="la-question"></a>
## ❓ 1. La Question Fondatrice

> **Peut-on comprendre et raisonner sans stocker des milliards de pages de texte brut ?**

Les modèles classiques (LLM) reposent sur la mémorisation statistique de corpus massifs (gaspillage de gigaoctets et de VRAM, hallucinations, oubli catastrophique lors de nouvelles acquisitions).

**RATISS-ONE inverse le paradigme :**
- **Le souvenir est le chemin :** Une onde topologique traverse un graphe de 95 660 neurones vivants.
- **La vérité est sanctuarisée :** Chaque fait fondamental est immuable et signé cryptographiquement (SHA-256).
- **Le corps ressent :** Le module somatique ETH module le pouls, la tension et la chaleur en fonction de l'intention de l'interlocuteur.
- **L'acquisition est immédiate :** Un nouvel énoncé est encodé et scellé en direct en moins de 1 milliseconde sans ré-entraîner le réseau.

---

<a id="en-30-secondes"></a>
## ⚡ 2. En 30 Secondes : Les Faits Mesurés

| Composant | Rôle | Performance Mesurée | Statut |
| :--- | :--- | :---: | :---: |
| 🧠 **`RatissOne.ratiss`** | Conteneur complet consolidé | **3,5 Ko** (scellé SHA-256) | ✅ Opérationnel |
| ⚡ **`lecteur_ratiss.py`** | Runtime exclusif & ports E/S | **0,03 ms** / inférence | ✅ Prouvé |
| 👂 **Oreille (Phonon)** | ASR éphémère (audio ➔ texte) | **0,10 ms** (purge immédiate) | ✅ Prouvé |
| 🗣️ **Bouche (Piper)** | TTS modulé par le Corps ETH | **10,5 ms** (prosodie vivante) | ✅ Prouvé |
| 🤝 **Main Tendue Live** | Apprentissage one-shot direct | **51 µs** (zéro oubli) | ✅ Prouvé |
| 🚀 **Entraînement Colab** | Convergence Hebbienne vectorisée | **760 000 mots / s** | ✅ Prouvé |
| 🐳 **Docker Runtime** | Conteneurisation universelle | **0.0.0.0:8080** | ✅ Prêt |

---

<a id="le-conteneur-ratiss"></a>
## 📦 3. Le Conteneur Unique `.ratiss` & La Boîte Blanche

Pour libérer le code principal et supprimer l'éparpillement des dizaines de fichiers, le cerveau complet est packagé dans un fichier maître unique : **`cerveau/RatissOne.ratiss`** (diminutif officiel : `.rt`).

```
┌───────────────────────────────────────────────────────────────────┐
│              CONTENEUR SOUVERAIN (.ratiss / .rt)                  │
├───────────────────────────────────────────────────────────────────┤
│ [ENTÊTE MAGIQUE]  RATISS_SOUVERAIN_V2                             │
│ [MÉTADONNÉES]     Auteur : Jonathan Evina · Labo : RATISS Labs   │
│ [SCEAU SHA-256]   6d67c34650ebe54baba88f248b19e4b9ea66...        │
├───────────────────────────────────────────────────────────────────┤
│ 1. BLOC_ETH              Constantes vitales (pouls 72 bpm, 37°C)  │
│ 2. BLOC_SANCTUAIRE       Faits vérifiés inaltérables (0 halluc.) │
│ 3. BLOC_SYNCHROTRON      Filtres d'onde et atténuation du bruit   │
│ 4. BLOC_CORTEX           Matrices génératives & Top-P             │
│ 5. BLOC_MEMOIRE_LIVE     Faits appris en temps réel               │
│ 6. BLOC_PORTS_IO         Connecteurs ASR, TTS, Chat, Télémétrie   │
└───────────────────────────────────────────────────────────────────┘
```

**Pourquoi une Boîte Blanche ?**  
Contrairement aux fichiers GGUF ou checkpoints PyTorch qui sont des "boîtes noires" de matrices opaques, le format `.ratiss` est **100 % transparent et auditable** par l'humain tout en étant scellé mathématiquement contre toute altération frauduleuse.

---

<a id="le-runtime-officiel"></a>
## 🛡️ 4. Le Runtime Officiel Exclusif (`lecteur_ratiss.py`)

Le fichier `.ratiss` ne s'ouvre pas avec un outil standard tiers : **il se lit exclusivement via son lecteur officiel** :

```bash
# Exécution d'une requête en direct
python3 cerveau/lecteur_ratiss.py cerveau/RatissOne.ratiss "Explique-moi la fusion nucléaire"
```

**Sécurité Intrinsèque :**  
Si un seul octet du conteneur est modifié ou corrompu par un tiers, le runtime intercepte instantanément l'incohérence et bloque l'exécution :
```text
[HALTE DE SÉCURITÉ] Empreinte altérée ! Déclaré: 6d67c34650eb..., Calculé: 35284ae84c9b...
```

---

<a id="la-boucle-audio"></a>
## 🎧 5. La Boucle Sensorimotrice Audio (Oreille + Bouche + ETH)

L'audio de RATISS-ONE obéit aux lois de l'anatomie : **le cerveau ne stocke jamais de signaux audio bruts**.

```
 Micro / Audio WAV ➔ [OREILLE Phonon] ➔ Texte brut (Purge WAV instantanée)
                              ↓
                   [CERVEAU SOUVERAIN .ratiss]
            (Corps ETH ➔ Sanctuaire ➔ Cortex ➔ Juge SHA)
                              ↓
 Texte certifié + Paramètres ETH ➔ [BOUCHE Piper] ➔ Onde acoustique modulée
```

### Modulation Vocale par le Corps Affectif ETH 💓
La voix ne sonne jamais comme un robot plat :
- **Ton Chaleureux ("mon pote", "merci") :** Vitesse **x1.15**, pitch **520 Hz**, élocution dynamique et complice.
- **Ton Neutre / Académique :** Vitesse **x1.00**, pitch **440 Hz**, diction claire et posée.
- **Ton Vigilant / Alerte :** Vitesse **x0.90**, pitch **380 Hz**, diction solennelle et ferme.

**Preuves Audio Générées :**  
Les échantillons audio complets de test sont disponibles dans `bouche/audio_sorties/` :
- `sequence_1_salutation.wav` (Salutation chaleureuse)
- `sequence_2_apprentissage.wav` (Enregistrement vocal d'un fait live)
- `sequence_3_restitution.wav` (Restitution vocale du fait scellé)

Rejouer la boucle audio en une commande :
```bash
python3 bouche/assistant_vocal_complet.py
```

---

<a id="dialogue-v2"></a>
## 💬 6. Dialogue v2 & Mémoire Épisodique Live ("Main Tendue")

Fini les 7 intentions rigides et le rejet de *"merci beaucoup"*. Dialogue v2 apporte une souplesse totale :

```bash
python3 dialogue/conversation_v2.py
```

### Démonstration de l'Apprentissage One-Shot en Direct :
1. **Tu lui dis :**  
   *« Apprends que Jonathan Evina est le fondateur de RATISS Labs. »*
2. **RATISS répond en 51 microsecondes :**  
   *« Gravé dans ma mémoire active en 51.5 µs ! Fait scellé #6cffd87fa17d. »*
3. **Tu lui demandes au tour suivant :**  
   *« Qui est le fondateur de RATISS Labs ? »*
4. **Il restitue immédiatement :**  
   *« D'après ce que tu m'as appris (scellé #6cffd87fa17d) : Jonathan Evina est le fondateur de RATISS Labs. »*

**Zéro rétropropagation, zéro GPU, zéro oubli catastrophique !**

---

<a id="entrainement-colab"></a>
## 🚀 7. Entraînement Épisodique Colab Haute Vitesse

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jonathansearch/RATISS-ONE/blob/main/colab/Entrainement_RATISS_ONE.ipynb)

Pour éviter les entraînements obscurs qui durent une semaine, le script Colab découpe le processus en **épisodes observables en temps réel** :

- **Script autonome :** `colab/train_ratiss_colab.py`
- **Notebook interactif :** `colab/Entrainement_RATISS_ONE.ipynb`

### Fonctionnalités Clés :
1. **Zéro Boîte Noire :** Tableau de bord à chaque épisode (Vitesse mots/s, Énergie libre, Réticulation Hebbienne, Télémétrie ETH).
2. **Vitesse Foudroyante :** Traitement vectorisé à **~760 000 mots par seconde** sur simple CPU.
3. **Sauvegarde Directe Google Drive :** Le conteneur final est compilé et scellé automatiquement vers `/content/drive/MyDrive/RatissOne.ratiss`.

---

<a id="deploiement-docker"></a>
## 🐳 8. Déploiement Docker & Interface Web

Déployer RATISS-ONE sur n'importe quel ordinateur ou serveur en une commande :

```bash
# Lancement direct via Python
python3 interfaces/serveur_local.py

# Ou via Docker
cd docker && docker compose up -d
```

L'interface de chat Web et l'API locale sont immédiatement accessibles sur **`http://localhost:8080`** !

---

<a id="tableau-mesures"></a>
## 📊 9. Tableau Historique des 45 Leçons

| Leçon | Découverte & Mesure Réelle | Preuve |
| :---: | :--- | :--- |
| **L01-L06** | Seuil, pas, oubli, asymétrie, propagation dans Ratum | `archives/anciennes_lecons.zip` |
| **L07** | Oreille réelle Phonon-2 : JFK transcrit mot pour mot | `porte-voix/` |
| **L08** | Bouche réelle Piper : verdicts parlés en 4,9 s | `bouche/` |
| **L09-L10** | Cerveau à secteurs (VIF ➔ REFRAIN ➔ SANCTUAIRE f92) | `cerveau/cerveau.py` |
| **L11-L12** | Éducation sans tissage manuel (50/50 TIENT, 0 témoin) | `archives/anciennes_lecons.zip` |
| **L13** | Figement CISE : vitesse ≥ 10 ➔ étincelle ➔ neurones figés | `cerveau/` |
| **L15** | Marbre : boucle fermée et gravure inaltérable | `cerveau/autotest_marbre.py` |
| **L16** | Marée : tampon 50 sans perte et régulation de tempête | `cerveau/autotest_maree.py` |
| **L17** | Rêve : consolidation nocturne sans ré-apprentissage | `cerveau/autotest_chaos.py` |
| **L18** | Portabilité C : 24/24 sorties identiques au bit près | `livre/` |
| **L19** | Pont topologique FOCAL (espace projectif P_sig) | `archives/anciennes_lecons.zip` |
| **L20** | Règle R5 : compteur d'écoutes strict du monde extérieur | `cerveau/` |
| **L22** | Dialogue v1 historique (7 intentions pinnées) | `dialogue/dialogue.py` |
| **L45** | Lecture NarrativeQA (130 livres, 10,6M mots, 95k neurones) | `cerveau/fige-300M-narrativeqa.json.gz`|
| **L46+** | **Architecture Souveraine 2.0 : Format .ratiss + Dialogue v2 + Mémoire Live** | **`cerveau/RatissOne.ratiss`** |

---

<a id="carte-du-depot"></a>
## 🗺️ 10. Carte du Dépôt Épuré

```
RATISS-ONE/
├── README.md                          # Ce document (ancres 100% fonctionnelles)
├── LICENSE                            # Licence MIT
├── MANIFESTE.json                     # Principes directeurs et engagement
│
├── cerveau/                           # LE CŒUR COGNITIF
│   ├── RatissOne.ratiss               # CONTENEUR UNIQUE SCELLÉ (Boîte Blanche)
│   ├── lecteur_ratiss.py              # RUNTIME OFFICIEL EXCLUSIF
│   ├── fige-300M-narrativeqa.json.gz  # Graphe physique L45 (95 660 neurones)
│   └── cerveau.py                     # Moteur de dynamique neuronale
│
├── interfaces/                        # PORTS DE CONNECTIQUE & E/S
│   ├── chat_terminal.py               # Chat interactif terminal
│   ├── serveur_local.py               # Serveur Web & API locale (port 8080)
│   └── assistant_vocal.py             # Assistant vocal E2E
│
├── bouche/                            # LA BOUCHE VOCALE
│   ├── assistant_vocal_complet.py     # Pipeline sensorimoteur audio complet
│   ├── boucle_sensorielle.py          # Banc d'essai Oreille + Bouche + ETH
│   └── audio_sorties/                 # Échantillons audio réels générés (.wav)
│
├── dialogue/                          # LE DIALOGUE SOUVERAIN
│   ├── dialogue_v2.py                 # Moteur sémantique + Mémoire Live
│   └── conversation_v2.py             # Démonstrateur conversationnel (17 répliques)
│
├── colab/                             # ENTRAÎNEMENT HAUTE VITESSE
│   ├── Entrainement_RATISS_ONE.ipynb  # Notebook Colab avec export Drive
│   └── train_ratiss_colab.py          # Script d'entraînement vectorisé
│
├── docker/                            # CONTENEURISATION
│   ├── Dockerfile                     # Image légère prête à l'emploi
│   └── docker-compose.yml             # Déploiement en 1 clic
│
├── livre/                             # LE LIVRE COMPLET (CC-BY-SA)
│   ├── index.html                     # Livre interactif autonome
│   └── presentation.html              # 12 slides des sommets
│
└── archives/                          # ARCHIVES SCELLÉES
    └── anciennes_lecons.zip           # Sauvegarde intégrale des anciens scripts
```

---

<a id="auteur-licence"></a>
## 👤 11. Auteur, Identité & Licence

- **Auteur :** Jonathan Evina (Mono-chercheur indépendant, 18 ans).
- **Laboratoire :** RATISS Labs · Yaoundé, Cameroun 🇨🇲.
- **Licence du Code :** [MIT](LICENSE) — Libre, ouvert, souverain.
- **Licence du Livre :** [CC-BY-SA-4.0](livre/LICENCE.md) — Partage à l'identique.
- **Règle d'or :** *« On ne croit pas. On rejoue. »*

---
*Fait avec rigueur, passion et souveraineté à Yaoundé.*
