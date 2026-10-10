# Fiche Technique : Naissance du Micro-Cerveau RATISS GPU T4

Ce modèle a été conçu au laboratoire de recherche RATISS à Yaoundé (Cameroun) sous la supervision de Jonathan Evina pour valider le principe d'émergence sémantique par rapport au gros modèle RATISS-ONE.

## Caractéristiques Techniques
- **Vocabulaire** : 957 concepts clés uniques filtrés contre le bruit sémantique (stop-words).
- **Architecture** : Matrice synaptique d'adjacence active gérée par PyTorch sur T4 GPU.
- **Entraînement** : Association Hebbienne auto-supervisée accélérée par GPU T4 sur 10 000 paires conversationnelles.
- **Vitesse de génération** : Moins de 1 ms par inférence grâce à l'implémentation de tenseurs GPU.
- **Format** : Fichier unifié `mini_cerveau_gpu.pt` sérialisé pour la recherche cognitive.
