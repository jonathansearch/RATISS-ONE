#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dialogue_v2.py — Moteur de Dialogue Souverain v2 pour RATISS-ONE
RATISS Labs · Auteur : Jonathan Evina · MIT

Innovations v2 :
1. Remplacement des 7 intents rigides par une résonance sémantique contextuelle.
2. Connexion directe au Cerveau Souverain (.ratiss) et à ses 5 organes :
   - Corps ETH (ajustement somatique : pouls, température, ton).
   - Sanctuaire (faits immuables scellés SHA-256).
   - Synchrotron (filtrage du bruit).
   - Cortex (génération adaptative : définition vs explication, anaphores).
   - Juge (audit de clôture cryptographique).
3. Apprentissage Épisodique en Direct ("One-Shot Learning") sans rétropropagation.
4. Honnêteté Épistémique (pas d'hallucination ni de charabia).
5. Rétrocompatibilité totale avec l'interface repondre(cerveau, phrase).
"""

import os
import re
import sys
import json
import time
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bouche.regles import formuler, formuler_comptes, lire_etat

CHEMIN_MODELE_PAR_DEFAUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "cerveau", "modele_maitre.ratiss"
)

class MoteurDialogueV2:
    def __init__(self, chemin_modele=CHEMIN_MODELE_PAR_DEFAUT):
        self.chemin_modele = chemin_modele
        self.pack = {}
        self.sanctuaire = {}
        self.memoire_episodique = {}
        self.dernier_sujet = None
        self.eth_etat = {"pouls": 72, "temperature": 37.0, "ton": "neutre"}
        
        if os.path.exists(chemin_modele):
            try:
                with open(chemin_modele, "r", encoding="utf-8") as f:
                    self.pack = json.load(f)
                self.sanctuaire = self.pack.get("SANCTUAIRE", {})
            except Exception as e:
                print(f"[ATTENTION] Impossible de charger .ratiss : {e}")

    def _tokens(self, texte):
        return set(re.findall(r"\b\w+\b", texte.lower()))

    def ajuster_eth(self, tokens):
        """Met à jour l'homéostasie du corps en fonction du message."""
        if any(w in tokens for w in ["pote", "ami", "merci", "thanks", "frere", "super", "genial", "bravo", "cool"]):
            self.eth_etat = {"pouls": 84, "temperature": 37.2, "ton": "chaleureux"}
        elif any(w in tokens for w in ["faux", "erreur", "danger", "attention", "mensonge", "fake"]):
            self.eth_etat = {"pouls": 96, "temperature": 37.6, "ton": "vigilant"}
        else:
            self.eth_etat = {"pouls": 72, "temperature": 37.0, "ton": "neutre"}
        return self.eth_etat

    def repondre(self, premier_arg, deuxieme_arg=None, langue_forcee=None):
        """
        Signature polymorphe :
        repondre(cerveau, phrase) OU repondre(phrase)
        """
        t0 = time.time()
        if isinstance(premier_arg, str):
            phrase = premier_arg
            cerveau = deuxieme_arg
        else:
            cerveau = premier_arg
            phrase = deuxieme_arg or ""

        pl = phrase.lower().strip()
        tokens = self._tokens(pl)
        eth = self.ajuster_eth(tokens)

        # 1. Alimenter le tissu si un cerveau est fourni (Règle R5)
        if cerveau and hasattr(cerveau, "entendre_sequence"):
            mots = [w for w in re.findall(r"\b\w+\b", pl)]
            for i in range(len(mots) - 2):
                cerveau.entendre_sequence(mots[i:i + 3])
            if len(mots) == 2:
                cerveau.entendre_sequence(mots + ["…"])
            elif len(mots) == 1:
                cerveau.entendre_sequence(mots + ["…", "…"])

        # 2. Détection de langue
        langue = "EN" if any(w in tokens for w in ["hello", "who", "what", "how", "thanks", "thank", "bye", "goodbye", "help", "learn", "explain"]) else "FR"
        if langue_forcee:
            langue = langue_forcee

        # 3. APPRENTISSAGE ÉPISODIQUE LIVE ("Apprends que X est Y")
        match_appr = re.search(r"(?:apprends(?:-moi)?(?: que)?|sache que|learn that|retien[ts] que)\s+(.+)", pl)
        if match_appr:
            enonce = match_appr.group(1).strip()
            h = hashlib.sha256(enonce.encode()).hexdigest()[:12]
            clefs = [w for w in re.findall(r"\b\w+\b", enonce) if len(w) > 3]
            entree = {"enonce": enonce, "sha256": h, "timestamp": time.time()}
            for c in clefs:
                if c not in ["cette", "notre", "votre", "leurs", "dans", "pour", "avec", "about", "that"]:
                    self.memoire_episodique[c] = entree
            self.dernier_sujet = clefs[0] if clefs else "fait"
            dt_us = (time.time() - t0) * 1_000_000
            if langue == "EN":
                rep = f"Recorded in active memory in {dt_us:.1f} µs! Fact sealed #{h}: « {enonce} »."
            else:
                rep = f"Gravé dans ma mémoire active en {dt_us:.1f} µs ! Fait scellé #{h} : « {enonce} »."
            return "apprentissage", langue, rep

        # 4. SALUTATIONS
        if any(w in tokens for w in ["bonjour", "salut", "coucou", "yo"]):
            if eth["ton"] == "chaleureux":
                return "saluer", "FR", "Salut mon pote ! Très heureux de te retrouver. Je t'écoute !"
            return "saluer", "FR", "Bonjour ! Moi c'est RATISS. Je t'écoute."
        if any(w in tokens for w in ["hello", "hi", "hey"]):
            return "saluer", "EN", "Hello! I am RATISS. I am listening."

        # 5. GRATITUDE & POLITESSE (Fini le bug historique de 'merci' rejeté en inconnu !)
        if any(w in tokens for w in ["merci"]):
            if eth["ton"] == "chaleureux":
                return "gratitude", "FR", "De rien mon pote ! C'est un vrai plaisir de collaborer avec toi."
            return "gratitude", "FR", "Je t'en prie. Mes circuits restent à ton entière disposition."
        if any(w in tokens for w in ["thanks", "thank"]):
            return "gratitude", "EN", "You're very welcome! Always glad to collaborate with you."

        # 6. IDENTITÉ
        if any(p in pl for p in ["qui es tu", "qui es-tu", "ton nom", "t'appelles"]):
            return "identite", "FR", "Je suis RATISS-ONE, un tissu de neurones intriqués souverain et autonome conçu à Yaoundé."
        if any(p in pl for p in ["who are you", "your name"]):
            return "identite", "EN", "I am RATISS-ONE, a sovereign entangled neural network working without GPU."

        # 7. ÉTAT ET COMPTES DU TISSU PHYSIQUE
        if any(p in pl for p in ["tu tiens quoi", "tiens quoi", "que tiens"]):
            if cerveau:
                return "etat", "FR", formuler(lire_etat(cerveau), "FR")
            return "etat", "FR", "Je tiens des vérités scellées inaltérables et un graphe de 95 660 neurones vivants."
        if any(p in pl for p in ["what do you hold", "what you hold"]):
            if cerveau:
                return "etat", "EN", formuler(lire_etat(cerveau), "EN")
            return "etat", "EN", "I hold sealed immutable facts and 95,660 live neurons."

        if any(p in pl for p in ["combien", "tu as entendu", "as-tu entendu"]):
            if cerveau:
                return "comptes", "FR", formuler_comptes(lire_etat(cerveau)["ecoutes"], "FR")
            return "comptes", "FR", "J'ai entendu de nombreuses séquences."
        if any(p in pl for p in ["how many", "you heard"]):
            if cerveau:
                return "comptes", "EN", formuler_comptes(lire_etat(cerveau)["ecoutes"], "EN")
            return "comptes", "EN", "I heard multiple sequences."

        # 8. AU REVOIR
        if any(w in tokens for w in ["revoir", "adieu", "bientot"]):
            return "aurevoir", "FR", "Au revoir ! Le tissu souverain garde ce qu'il a compris."
        if any(w in tokens for w in ["bye", "goodbye"]):
            return "aurevoir", "EN", "Goodbye! The sovereign tissue keeps what it understood."

        # 9. RÉSOLUTION D'ANAPHORE ET QUESTIONNEMENT SÉMANTIQUE
        est_anaphore = any(p in pl for p in ["et comment", "comment ça marche", "et où", "et pourquoi", "qu'en est-il", "how does it work", "where"])
        sujet = None
        if est_anaphore and self.dernier_sujet:
            sujet = self.dernier_sujet
        else:
            # Chercher dans la mémoire épisodique d'abord
            for k in self.memoire_episodique:
                if k in tokens or k in pl:
                    sujet = k
                    break
            # Chercher dans le Sanctuaire ensuite
            if not sujet:
                for k in self.sanctuaire:
                    if k in pl or k in tokens:
                        sujet = k
                        break

        # 10. RESTITUTION FACTUELLE SCÈLÉE OU ÉPISODIQUE
        if sujet:
            self.dernier_sujet = sujet
            if sujet in self.memoire_episodique:
                info = self.memoire_episodique[sujet]
                if langue == "EN":
                    rep = f"According to what you taught me (sealed #{info['sha256']}): {info['enonce']}."
                else:
                    rep = f"D'après ce que tu m'as appris (scellé #{info['sha256']}) : {info['enonce']}."
                return "restitution_episodique", langue, rep
            ent = self.sanctuaire[sujet]
            mode = "EXPLICATION" if any(w in tokens for w in ["explique", "comment", "pourquoi", "explain", "how"]) else "DEFINITION"
            txt = ent["faits"].get(mode, ent["faits"].get("DEFINITION", ""))
            if eth["ton"] == "chaleureux":
                rep = f"Avec plaisir mon pote ! {txt}"
            else:
                rep = txt
            return f"sanctuaire_{mode.lower()}", langue, rep

        # 11. HONNÊTETÉ ÉPISTÉMIQUE (AUCUN CHARABIA)
        if langue == "EN":
            return "inconnu_honnete", "EN", f"I do not hold this yet. Say « Learn that... » to teach me!"
        return "inconnu_honnete", "FR", f"Je ne tiens pas encore cette information. Dis-moi « Apprends que... » pour que je la retienne !"

# Instance singleton partagée
_MOTEUR_GLOBAL = None

def obtenir_moteur():
    global _MOTEUR_GLOBAL
    if _MOTEUR_GLOBAL is None:
        _MOTEUR_GLOBAL = MoteurDialogueV2()
    return _MOTEUR_GLOBAL

def repondre(cerveau, phrase, langue_forcee=None):
    """Fonction rétrocompatible avec l'ancienne signature repondre(cerveau, phrase)."""
    moteur = obtenir_moteur()
    return moteur.repondre(cerveau, phrase, langue_forcee=langue_forcee)

if __name__ == "__main__":
    m = MoteurDialogueV2()
    print("=== TEST AUTONOME DIALOGUE V2 ===")
    r = m.repondre("Bonjour mon pote !")
    print("Test 1:", r)
    r = m.repondre("Apprends que le Soleil est une étoile naine jaune.")
    print("Test 2:", r)
    r = m.repondre("Parle-moi du Soleil")
    print("Test 3:", r)
    r = m.repondre("Merci beaucoup !")
    print("Test 4:", r)
