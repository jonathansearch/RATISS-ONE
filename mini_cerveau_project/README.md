# 🧠 Projet RATISS - Micro-Cerveau Sémantique & ScalableGPT (GPU T4)

[![Licence](https://img.shields.io/badge/Licence-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-ee4c2c.svg)](https://pytorch.org/)
[![Hardware](https://img.shields.io/badge/Hardware-NVIDIA%20T4%20GPU-orange.svg)](https://www.nvidia.com/)

Ce dépôt héberge le prototype ultra-purifié développé au sein du laboratoire **RATISS** à Yaoundé (Cameroun) sous la direction de **Jonathan Evina**. Ce projet valide le principe d'émergence sémantique par association d'idées et modélise de façon modulaire et scalable un réseau génératif de type Transformer (Decoder-only) entraîné sur des données littéraires francophones de référence.

---

## 📋 Table des Matières
1. [Architecture & Spécifications du Micro-Cerveau](#1-architecture--spécifications-du-micro-cerveau)
2. [Modèle Génératif ScalableGPT (85M+)](#2-modèle-génératif-scalablegpt-85m)
3. [Performance & Vitesse d'Inférence GPU](#3-performance--vitesse-dinférence-gpu)
4. [Contenu des Fichiers Exportés](#4-contenu-des-fichiers-exportés)
5. [Instructions d'Utilisation en Local](#5-instructions-dutilisation-en-local)

---

## 1. Architecture & Spécifications du Micro-Cerveau

Le modèle synaptique d'association Hebbienne a été conçu pour structurer de façon autonome des relations logiques complexes entre concepts sans le bruit sémantique usuel (mots de liaison, ponctuations parasites).

### Fiche technique de l'audit tensoriel :
- **Base conceptuelle (Vocabulaire)** : `957` concepts clés rigoureusement filtrés.
- **Densité Synaptique** : `5.47%`.
- **Nombre total de connexions actives** : `50 060` synapses actives chargées directement en mémoire GPU.
- **Format physique** : `mini_cerveau_gpu.pt` (3.52 Mo).
- **Méthode d'émergence** : Projection par produit matriciel tensoriel :  
  $$\mathbf{s} = \mathbf{W}^T \cdot \mathbf{h}$$
  Où $\mathbf{h}$ représente le vecteur d'activation sémantique d'entrée, et $\mathbf{W}$ est le tenseur d'adjacence synaptique.

---

## 2. Modèle Génératif ScalableGPT (85M+)

Pour propulser ce projet vers des capacités de génération textuelle de pointe, nous avons implémenté et entraîné de bout en bout un grand modèle de langue **ScalableGPT** de **85 194 284 paramètres**.

### Caractéristiques de l'entraînement :
- **Dataset source** : Corpus public et libre issu du Projet Gutenberg (littérature française classique).
- **Tokeniseur** : BERT Base French Europeana (`dbmdz/bert-base-french-europeana-cased` - vocabulaire de 32 000 tokens).
- **Hyperparamètres d'Architecture** :
  - Dimension d'embedding ($d_{model}$) : `768`
  - Têtes d'auto-attention ($n_{head}$) : `12`
  - Couches de blocs de décodage ($n_{layer}$) : `12`
  - Contexte d'attention ($block\_size$) : `256` tokens
- **Métriques de convergence** :
  - Perte initiale (cross-entropy) : `10.51`
  - Perte finale après convergence : `2.46`

---

## 3. Performance & Vitesse d'Inférence GPU

Grâce aux optimisations PyTorch sur l'accélérateur matériel NVIDIA T4, les temps de traitement sont d'une vélocité remarquable :

- **Temps de chargement du Tenseur** : `~270.50 ms`
- **Inférence Sémantique pure** : `~394 µs` (Moins de 1 milliseconde)
- **Inférence générative (ScalableGPT)** : Autorégressive pure sur GPU T4.

---

## 4. Contenu des Fichiers Exportés

Tous les scripts ont été développés selon des standards d'ingénierie stricts, isolant la configuration du modèle pour un usage clé en main :

- **`mini_cerveau_gpu.pt`** : Le tenseur unifié contenant les poids synaptiques de 957 concepts.
- **`mini_cerveau_gpu.py`** : Script d'interrogation du réseau par activation sémantique à haute vitesse.
- **`scalable_gpt_train.py`** : Implémentation complète de l'architecture du Transformer décodeur pour la réplication et le fine-tuning.
- **`README_PRO.md`** : Cette documentation complète d'ingénierie.

---

## 5. Instructions d'Utilisation en Local

Pour exécuter l'inférence locale de votre modèle, clonez le dépôt et lancez l'interrogation dans votre terminal :

```python
from mini_cerveau_gpu import interroger_mini_cerveau

# Exemple d'appel
reponse = interroger_mini_cerveau("Parle moi de situation et de politique")
print(reponse)
```
