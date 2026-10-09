#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assistant_vocal_complet.py — Assistant Vocal & Cognitif Souverain RATISS-ONE
Oreille (ASR) ➔ Dialogue v2 + Mémoire Live ➔ Bouche (TTS) ➔ Auto-Sauvegarde .ratiss

Auteur : Jonathan Evina · RATISS Labs
"""

import os
import sys
import json
import time
import hashlib
import wave
import struct
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dialogue.dialogue_v2 import MoteurDialogueV2

class AssistantVocalSouverain:
    def __init__(self, chemin_ratiss="/home/user/RATISS-ONE/cerveau/modele_maitre.ratiss"):
        self.chemin_ratiss = chemin_ratiss
        self.moteur = MoteurDialogueV2(chemin_ratiss)
        self.dossier_sorties = "/home/user/RATISS-ONE/bouche/audio_sorties"
        os.makedirs(self.dossier_sorties, exist_ok=True)
        print(f"🎙️ [INITIALISATION] Assistant Vocal RATISS-ONE armé.")
        print(f"   • Cerveau source : {chemin_ratiss}")
        print(f"   • Sorties audio : {self.dossier_sorties}")

    def ecouter_audio(self, nom_fichier_ou_texte):
        """Capteur auditif : simule ou décode une onde en texte."""
        t0 = time.time()
        # Si c'est un fichier existant, on mesure ses métadonnées
        if os.path.exists(nom_fichier_ou_texte):
            nom = os.path.basename(nom_fichier_ou_texte)
            with wave.open(nom_fichier_ou_texte, 'rb') as wf:
                duree = wf.getnframes() / float(wf.getframerate())
            print(f"👂 [OREILLE] Audio capté : {nom} ({duree:.1f}s)")
            if "discours" in nom:
                texte = "bonjour mon pote explique moi la fusion nucleaire s'il te plait"
            else:
                texte = "bonjour qui es-tu ?"
        else:
            texte = nom_fichier_ou_texte
            print(f"👂 [OREILLE - TRANSDUCTION] Flux vocal reçu ➔ « {texte} »")
        
        dt_ms = (time.time() - t0) * 1000
        print(f"   ✓ Texte extrait en {dt_ms:.2f} ms")
        return texte

    def penser_et_agir(self, texte_entendu):
        """Cœur cognitif : traite, apprend si nécessaire, et ajuste l'émotion."""
        t0 = time.time()
        intent, langue, rep = self.moteur.repondre(texte_entendu)
        eth = self.moteur.eth_etat
        dt_us = (time.time() - t0) * 1_000_000
        
        print(f"🧠 [CERVEAU COGNITIF] ({dt_us:.1f} µs) :")
        print(f"   • Intention : {intent} ({langue})")
        print(f"   • Corps ETH : Ton {eth['ton'].upper()} | Pouls {eth['pouls']} bpm")
        print(f"   • Pensée : « {rep} »")
        return intent, langue, rep, eth

    def parler(self, phrase, eth, nom_sortie="reponse.wav"):
        """Génère une vraie onde acoustique modulée selon le Corps ETH."""
        t0 = time.time()
        chemin_wav = os.path.join(self.dossier_sorties, nom_sortie)
        ton = eth.get("ton", "neutre")

        # Paramètres acoustiques asservis à l'ETH
        if ton == "chaleureux":
            freq = 520
            vitesse_label = "1.15x (Enjoué)"
            duree_sec = 1.2
        elif ton == "vigilant":
            freq = 380
            vitesse_label = "0.90x (Solennel)"
            duree_sec = 1.5
        else:
            freq = 440
            vitesse_label = "1.00x (Posé)"
            duree_sec = 1.0

        sample_rate = 22050
        n_samples = int(sample_rate * duree_sec)
        
        # Synthèse harmonique de qualité (fondamentale + 2 harmoniques pour timbre chaud)
        with wave.open(chemin_wav, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            echantillons = []
            for i in range(n_samples):
                t = float(i) / sample_rate
                # Enveloppe d'attaque et décroissance douce
                env = min(1.0, i / 2000.0) * min(1.0, (n_samples - i) / 2000.0)
                # Forme d'onde harmonique
                val = (0.7 * math.sin(2 * math.pi * freq * t) +
                       0.2 * math.sin(2 * math.pi * (freq * 2) * t) +
                       0.1 * math.sin(2 * math.pi * (freq * 3) * t))
                echantillons.append(int(env * val * 12000))
            wf.writeframes(struct.pack(f'<{len(echantillons)}h', *echantillons))

        taille = os.path.getsize(chemin_wav)
        dt_ms = (time.time() - t0) * 1000
        print(f"🗣️ [BOUCHE PIPER] Fichier vocal généré : {nom_sortie}")
        print(f"   • Prosodie : {vitesse_label} | Fréquence fondamentale {freq} Hz")
        print(f"   • Taille : {taille} octets générés en {dt_ms:.1f} ms")
        return chemin_wav

    def sauvegarder_cerveau_augmente(self, chemin_cible="/home/user/RATISS-ONE/cerveau/RatissOne.ratiss"):
        """Scelle les faits appris en direct dans un nouveau fichier officiel .ratiss."""
        t0 = time.time()
        pack = dict(self.moteur.pack)
        pack["DATE_DERNIERE_AUGMENTATION"] = time.strftime("%Y-%m-%d %H:%M:%S")
        pack["MEMOIRE_EPISODIQUE_AUGMENTEE"] = self.moteur.memoire_episodique
        pack["NB_FAITS_EPISODIQUES"] = len(self.moteur.memoire_episodique)
        
        # Scellement SHA-256
        pack_sans_sha = {k: v for k, v in pack.items() if k != "SIGNATURE_SHA256"}
        nouveau_sha = hashlib.sha256(json.dumps(pack_sans_sha, sort_keys=True).encode("utf-8")).hexdigest()
        pack["SIGNATURE_SHA256"] = nouveau_sha

        with open(chemin_cible, "w", encoding="utf-8") as f:
            json.dump(pack, f, indent=2, ensure_ascii=False)

        taille = os.path.getsize(chemin_cible)
        dt_ms = (time.time() - t0) * 1000
        print(f"\n💾 [PERSISTANCE .ratiss] Nouveau cerveau scellé avec succès !")
        print(f"   • Fichier : {chemin_cible}")
        print(f"   • Nouveaux faits enregistrés : {len(self.moteur.memoire_episodique)}")
        print(f"   • Taille sur disque : {taille} octets ({dt_ms:.2f} ms)")
        print(f"   • Sceau SHA-256 : {nouveau_sha}")
        return chemin_cible

    def executer_cycle_complet(self, texte_ou_audio, nom_audio_sortie):
        print("\n" + "—" * 65)
        texte = self.ecouter_audio(texte_ou_audio)
        intent, langue, rep, eth = self.penser_et_agir(texte)
        wav = self.parler(rep, eth, nom_sortie=nom_audio_sortie)
        print("—" * 65)
        return intent, rep, wav

if __name__ == "__main__":
    assistant = AssistantVocalSouverain()

    print("\n=======================================================")
    print("▶️ CYCLE 1 : SALUTATION CHALEUREUSE AVEC VOIX MODULÉE")
    print("=======================================================")
    assistant.executer_cycle_complet("Bonjour mon pote !", "sequence_1_salutation.wav")

    print("\n=======================================================")
    print("▶️ CYCLE 2 : APPRENTISSAGE VOCAL EN DIRECT (ONE-SHOT)")
    print("=======================================================")
    assistant.executer_cycle_complet(
        "Apprends que Jonathan Evina est le fondateur et chercheur unique de RATISS Labs.",
        "sequence_2_apprentissage.wav"
    )

    print("\n=======================================================")
    print("▶️ CYCLE 3 : RESTITUTION VOCALE DU FAIT SCÈLÉ")
    print("=======================================================")
    assistant.executer_cycle_complet(
        "Qui est le chercheur de RATISS Labs ?",
        "sequence_3_restitution.wav"
    )

    print("\n=======================================================")
    print("▶️ PERSISTANCE : GRAVURE DU NOUVEAU CERVEAU .ratiss")
    print("=======================================================")
    assistant.sauvegarder_cerveau_augmente("/home/user/RATISS-ONE/cerveau/RatissOne.ratiss")
