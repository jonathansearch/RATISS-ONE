# GPU

Il n'y a pas de script GPU dans ce dépôt.

La bouche v3 additionne des comptes entiers. Une carte graphique n'accélère pas ce geste de façon utile, et elle a déjà coûté du temps sur un autre organe : le mini-GPT de `scalable_gpt_train.py`, qui n'est pas branché sur les arcs `suit`.

On rouvrira ce dossier le jour où une mesure l'exigera. La mesure : `--memoire 8` bat le dernier mot seul, sur un texte non vu, et on veut alors **apprendre** la lumière au lieu de la fixer à 1, 1/2, 1/4. Ce jour-là, le GPU calculera cet écart-là. Pas avant.

D'ici là : runtime CPU, local ou Colab.
