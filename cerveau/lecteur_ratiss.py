#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lecteur_ratiss.py — Lecteur & Runtime Exclusif du Cerveau Souverain (.ratiss)
RATISS Labs · Auteur : Jonathan Evina (Mono-chercheur, Yaoundé)

Ce fichier est le SEUL runtime officiel capable d'ouvrir, d'auditer et
d'exécuter un cerveau scellé .ratiss / .rt en mode boîte blanche.
"""

import os
import sys
import json
import time
import hashlib
import re

MAGIC_HEADER = "RATISS_SOUVERAIN_V2"

class LecteurRatiss:
    def __init__(self, chemin_fichier):
        self.chemin_fichier = chemin_fichier
        self.modele = self._charger_et_valider(chemin_fichier)
        self.meta = self.modele.get("META", {})
        self.sanctuaire = self.modele.get("SANCTUAIRE", {})
        self.synchrotron = self.modele.get("SYNCHROTRON", {})
        self.memoire_episodique = self.modele.get("MEMOIRE_EPISODIQUE", {})
        self.ports = self.modele.get("PORTS_CONNECTIQUE", {})
        self.eth = {"pouls": 72, "temperature": 37.0, "tension": "stable", "ton": "neutre"}
        self.dernier_sujet = None

    def _charger_et_valider(self, chemin):
        """Ouvre le conteneur et vérifie le sceau cryptographique SHA-256."""
        if not os.path.exists(chemin):
            raise FileNotFoundError(f"[ERREUR RUNTIME] Cerveau introuvable : {chemin}")
        
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)

        if data.get("FORMAT") != MAGIC_HEADER:
            raise ValueError(f"[ERREUR SÉCURITÉ] Format invalide. Attendu {MAGIC_HEADER}, reçu {data.get('FORMAT')}")

        sha_declare = data.get("SIGNATURE_SHA256")
        data_sans_sha = {k: v for k, v in data.items() if k != "SIGNATURE_SHA256"}
        sha_calcule = hashlib.sha256(json.dumps(data_sans_sha, sort_keys=True).encode("utf-8")).hexdigest()

        if sha_declare and sha_declare != sha_calcule:
            raise PermissionError(f"[HALTE DE SÉCURITÉ] Empreinte altérée ! Déclaré: {sha_declare[:12]}..., Calculé: {sha_calcule[:12]}...")

        return data

    def ajuster_eth(self, tokens):
        """Module 1 : Résonance du Corps ETH."""
        if any(w in tokens for w in ["pote", "ami", "merci", "thanks", "super", "bravo", "genial"]):
            self.eth = {"pouls": 84, "temperature": 37.2, "tension": "detendue", "ton": "chaleureux"}
        elif any(w in tokens for w in ["faux", "erreur", "danger", "attention", "mensonge"]):
            self.eth = {"pouls": 96, "temperature": 37.6, "tension": "vigilante", "ton": "vigilant"}
        else:
            self.eth = {"pouls": 72, "temperature": 37.0, "tension": "stable", "ton": "neutre"}
        return self.eth

    def apprendre_live(self, enonce):
        """Module Épisodique : Apprentissage one-shot immédiat scellé."""
        t0 = time.time()
        enonce_clean = enonce.strip()
        h = hashlib.sha256(enonce_clean.encode("utf-8")).hexdigest()[:12]
        mots_clefs = [w for w in re.findall(r"\b\w+\b", enonce_clean.lower()) if len(w) > 3]
        entree = {"enonce": enonce_clean, "sha256": h, "timestamp": time.time()}
        
        for c in mots_clefs:
            if c not in ["cette", "notre", "votre", "leurs", "dans", "pour", "avec", "about", "that", "cameroun"]:
                self.memoire_episodique[c] = entree
        if "cameroun" in mots_clefs:
            self.memoire_episodique["cameroun"] = entree

        self.dernier_sujet = mots_clefs[0] if mots_clefs else "fait"
        dt_us = (time.time() - t0) * 1_000_000
        return h, dt_us

    def executer(self, message, port="PORT_CHAT_INTERFACE"):
        """Exécute l'inférence via un port de connectique officiel."""
        t0 = time.time()
        msg_str = str(message).strip()
        tokens = set(re.findall(r"\b\w+\b", msg_str.lower()))
        eth = self.ajuster_eth(tokens)
        langue = "EN" if any(w in tokens for w in ["hello", "who", "what", "how", "thanks", "bye", "learn"]) else "FR"

        # 1. Détection d'Apprentissage Live ("Apprends que...")
        match_appr = re.search(r"(?:apprends(?:-moi)?(?: que)?|sache que|learn that|retien[ts] que)\s+(.+)", msg_str, re.IGNORECASE)
        if match_appr:
            enonce = match_appr.group(1).strip()
            h, dt_us = self.apprendre_live(enonce)
            if langue == "EN":
                rep = f"Recorded in active memory in {dt_us:.1f} µs! Fact sealed #{h}: « {enonce} »."
            else:
                rep = f"Gravé dans ma mémoire active en {dt_us:.1f} µs ! Fait scellé #{h} : « {enonce} »."
            return {"port": port, "intent": "apprentissage", "langue": langue, "reponse": rep, "eth": eth}

        # 2. Salutations & Gratitude
        if any(w in tokens for w in ["bonjour", "salut", "coucou", "yo", "hello", "hi"]):
            rep = "Hello! I am RATISS-ONE. Ready." if langue == "EN" else ("Salut mon pote ! Très heureux de te retrouver. Je t'écoute !" if eth["ton"] == "chaleureux" else "Bonjour ! Je suis RATISS-ONE, le réseau neuronal souverain. Je t'écoute.")
            return {"port": port, "intent": "saluer", "langue": langue, "reponse": rep, "eth": eth}

        if any(w in tokens for w in ["merci", "thanks", "thank"]):
            rep = "You're very welcome! Always glad to collaborate." if langue == "EN" else ("De rien mon pote ! C'est un réel plaisir de collaborer avec toi." if eth["ton"] == "chaleureux" else "Je t'en prie. Mes circuits restent à ton entière disposition.")
            return {"port": port, "intent": "gratitude", "langue": langue, "reponse": rep, "eth": eth}

        if any(p in msg_str.lower() for p in ["qui es tu", "qui es-tu", "ton nom", "who are you"]):
            rep = "I am RATISS-ONE, a sovereign entangled neural network working without GPU." if langue == "EN" else "Je suis RATISS-ONE, un tissu de neurones intriqués souverain et autonome conçu à Yaoundé."
            return {"port": port, "intent": "identite", "langue": langue, "reponse": rep, "eth": eth}

        # 3. Résolution de Faits (Épisodique + Sanctuaire)
        est_anaphore = any(p in msg_str.lower() for p in ["et comment", "comment ça marche", "et où", "how does it work", "where"])
        sujet = self.dernier_sujet if (est_anaphore and self.dernier_sujet) else None
        
        if not sujet:
            for k in self.memoire_episodique:
                if k in tokens or k in msg_str.lower():
                    sujet = k
                    break
        if not sujet:
            for k in self.sanctuaire:
                if k in msg_str.lower() or k in tokens:
                    sujet = k
                    break

        if sujet:
            self.dernier_sujet = sujet
            if sujet in self.memoire_episodique:
                info = self.memoire_episodique[sujet]
                rep = f"According to what you taught me (sealed #{info['sha256']}): {info['enonce']}." if langue == "EN" else f"D'après ce que tu m'as appris (scellé #{info['sha256']}) : {info['enonce']}."
                return {"port": port, "intent": "restitution_episodique", "langue": langue, "reponse": rep, "eth": eth}

            ent = self.sanctuaire[sujet]
            mode = "EXPLICATION" if any(w in tokens for w in ["explique", "comment", "pourquoi", "explain", "how"]) else "DEFINITION"
            txt = ent["faits"].get(mode, ent["faits"].get("DEFINITION", ""))
            rep = f"Avec plaisir mon pote ! {txt}" if eth["ton"] == "chaleureux" else txt
            return {"port": port, "intent": f"sanctuaire_{mode.lower()}", "langue": langue, "reponse": rep, "eth": eth}

        # 4. Inconnu Honnête
        rep = "I do not hold this fact yet. Say « Learn that... » to teach me!" if langue == "EN" else "Je ne tiens pas encore cette information. Dis-moi « Apprends que... » pour que je la retienne !"
        return {"port": port, "intent": "inconnu_honnete", "langue": langue, "reponse": rep, "eth": eth}

    def exporter_boite_blanche(self, chemin_sortie):
        """Reconstruit et scelle le conteneur complet avec les nouveaux faits acquis."""
        contenu = dict(self.modele)
        contenu["MEMOIRE_EPISODIQUE"] = self.memoire_episodique
        contenu["DATE_EXPORT"] = time.strftime("%Y-%m-%d %H:%M:%S")
        sans_sha = {k: v for k, v in contenu.items() if k != "SIGNATURE_SHA256"}
        contenu["SIGNATURE_SHA256"] = hashlib.sha256(json.dumps(sans_sha, sort_keys=True).encode("utf-8")).hexdigest()
        
        with open(chemin_sortie, "w", encoding="utf-8") as f:
            json.dump(contenu, f, indent=2, ensure_ascii=False)
        return chemin_sortie

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python3 lecteur_ratiss.py <chemin_vers.ratiss> [message optionnel]")
        sys.exit(1)
        
    lecteur = LecteurRatiss(sys.argv[1])
    print(f"✓ Cerveau chargé : {lecteur.meta.get('NOM_MODELE')} ({lecteur.meta.get('AUTEUR')})")
    print(f"✓ Sceau SHA-256 : {lecteur.modele.get('SIGNATURE_SHA256')}")
    
    msg = sys.argv[2] if len(sys.argv) > 2 else "Bonjour mon pote !"
    res = lecteur.executer(msg)
    print(f"\n[ENTRÉE] : « {msg} »")
    print(f"[SORTIE ({res['port']})] : « {res['reponse']} »")
    print(f"[ETH] : Ton={res['eth']['ton']} | Pouls={res['eth']['pouls']} bpm")
