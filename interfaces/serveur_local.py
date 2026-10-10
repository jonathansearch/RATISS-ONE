#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serveur_local.py — Serveur Local Web & API pour RATISS-ONE
RATISS Labs · Auteur : Jonathan Evina

Fournit une interface Web locale et des endpoints REST :
- GET  /            ➔ Interface de Chat Web
- POST /api/chat    ➔ Dialogue & Télémétrie ETH
- GET  /api/etat    ➔ État et métadonnées du modèle .ratiss
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, "/home/user/RATISS-FIRST")
from ratiss_v2 import RatissV2

CHEMIN_DEFAULT = "/home/user/RATISS-ONE/colab/RatissOne_Massive_1M.npz"
if not os.path.exists(CHEMIN_DEFAULT):
    CHEMIN_DEFAULT = "/home/user/RATISS-FIRST/data/Descent gradient/RatissOne_Supervise.npz"
if not os.path.exists(CHEMIN_DEFAULT):
    CHEMIN_DEFAULT = "/home/user/RATISS-FIRST/data/RatissOne_Supervise.npz"
if not os.path.exists(CHEMIN_DEFAULT):
    CHEMIN_DEFAULT = "/home/user/RATISS-FIRST/RatissOne.npz"

CHEMIN_MODELE = os.environ.get("RATISS_CERVEAU_PATH", CHEMIN_DEFAULT)
cerveau = RatissV2(CHEMIN_MODELE)

PAGE_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RATISS-ONE — Interface Souveraine</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 12px; margin-bottom: 16px; }
        .title { font-size: 1.4rem; font-weight: bold; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
        .badge { background: #1e293b; border: 1px solid #38bdf8; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; }
        .eth-card { background: #1e293b; border-radius: 8px; padding: 10px 16px; display: flex; gap: 20px; font-size: 0.9rem; margin-bottom: 16px; }
        .eth-val { color: #f43f5e; font-weight: bold; }
        .chat-box { flex: 1; overflow-y: auto; background: #1e293b; border-radius: 8px; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 75%; padding: 10px 14px; border-radius: 8px; line-height: 1.4; font-size: 0.95rem; }
        .msg.user { align-self: flex-end; background: #0284c7; color: white; }
        .msg.bot { align-self: flex-start; background: #334155; color: #f1f5f9; border-left: 3px solid #38bdf8; }
        .input-bar { display: flex; gap: 8px; margin-top: 16px; }
        input[type="text"] { flex: 1; padding: 12px 16px; border-radius: 6px; border: 1px solid #475569; background: #1e293b; color: white; font-size: 1rem; }
        button { background: #0284c7; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 1rem; }
        button:hover { background: #0369a1; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">⚛️ RATISS-ONE <span class="badge">Souverain 2.0</span></div>
        <div>Yaoundé · MIT · Zéro GPU</div>
    </div>
    <div class="eth-card">
        <div>❤️ Pouls ETH : <span id="eth-pouls" class="eth-val">72 bpm</span></div>
        <div>🌡️ Température : <span id="eth-temp" class="eth-val">37.0°C</span></div>
        <div>🎭 Ton Somatique : <span id="eth-ton" class="eth-val">NEUTRE</span></div>
    </div>
    <div class="chat-box" id="chat">
        <div class="msg bot">Bonjour ! Je suis RATISS-ONE, le cerveau souverain scellé en format .ratiss. Je t'écoute. Dis-moi « Apprends que... » pour me transmettre de nouveaux faits en direct !</div>
    </div>
    <form class="input-bar" id="form" onsubmit="envoyer(event)">
        <input type="text" id="prompt" placeholder="Pose une question ou dis « Apprends que... »" autocomplete="off" autofocus />
        <button type="submit">Envoyer</button>
    </form>
    <script>
        async function envoyer(e) {
            e.preventDefault();
            const input = document.getElementById('prompt');
            const texte = input.value.trim();
            if (!texte) return;
            
            const chat = document.getElementById('chat');
            chat.innerHTML += `<div class="msg user">${texte}</div>`;
            input.value = '';
            chat.scrollTop = chat.scrollHeight;
            
            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: texte})
                });
                const data = await res.json();
                chat.innerHTML += `<div class="msg bot"><b>[${data.intent}]</b> : ${data.reponse}</div>`;
                document.getElementById('eth-pouls').innerText = data.eth.pouls + ' bpm';
                document.getElementById('eth-temp').innerText = data.eth.temperature + '°C';
                document.getElementById('eth-ton').innerText = data.eth.ton.toUpperCase();
                chat.scrollTop = chat.scrollHeight;
            } catch(err) {
                chat.innerHTML += `<div class="msg bot" style="color: #f43f5e">Erreur de connexion avec le cerveau.</div>`;
            }
        }
    </script>
</body>
</html>
"""

class GestionnaireRequetes(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PAGE_HTML.encode("utf-8"))
        elif url.path == "/api/etat":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            rep = {
                "nom": cerveau.meta.get("NOM_MODELE"),
                "auteur": cerveau.meta.get("AUTEUR"),
                "sha256": 'SCELLÉ',
                "eth": cerveau.eth
            }
            self.wfile.write(json.dumps(rep).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/chat":
            taille = int(self.headers.get("Content-Length", 0))
            corps = self.rfile.read(taille)
            try:
                donnees = json.loads(corps.decode("utf-8"))
                msg = donnees.get("message", "")
                resultat = cerveau.executer(msg, port="PORT_CHAT_INTERFACE")
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resultat).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"erreur": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def demarrer_serveur(port=8080):
    serveur = HTTPServer(("0.0.0.0", port), GestionnaireRequetes)
    print(f"🚀 [SERVEUR RATISS-ONE] Écoute active sur http://0.0.0.0:{port}")
    print(f"   • Cerveau chargé : {cerveau.meta.get('NOM_MODELE')} (SHA-256: {getattr(cerveau, 'meta', {}).get('AUTEUR', 'Jonathan Evina')}...)")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        serveur.server_close()

if __name__ == "__main__":
    demarrer_serveur()
