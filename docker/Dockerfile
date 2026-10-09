# Dockerfile — Runtime Souverain RATISS-ONE
# Auteur : Jonathan Evina · RATISS Labs

FROM python:3.11-slim

WORKDIR /app

# Copie du conteneur scellé et du runtime officiel
COPY cerveau/ /app/cerveau/
COPY interfaces/ /app/interfaces/
COPY bouche/ /app/bouche/

# Port d'écoute pour l'interface de chat et API locale
EXPOSE 8080

ENV PYTHONUNBUFFERED=1

# Démarrage du serveur souverain local
CMD ["python3", "interfaces/serveur_local.py"]
