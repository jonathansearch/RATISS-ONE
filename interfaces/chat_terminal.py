#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chat_terminal.py — Interface de Chat Interactif pour RATISS-ONE
RATISS Labs · Auteur : Jonathan Evina

Permet de dialoguer en direct avec le Cerveau Souverain .ratiss,
d'observer l'état somatique ETH en temps réel et de lui apprendre des faits.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cerveau.lecteur_ratiss import LecteurRatiss

def demarrer_chat(chemin_modele="/home/user/RATISS-ONE/cerveau/RatissOne.ratiss"):
    if not os.path.exists(chemin_modele):
        print(f"Erreur : Cerveau introuvable à {chemin_modele}")
        return

    cerveau = LecteurRatiss(chemin_modele)
    meta = cerveau.meta
    
    print("\n" + "=" * 68)
    print(f"🤖 RATISS-ONE TERMINAL CHAT — {meta.get('NOM_MODELE')} ({meta.get('VERSION')})")
    print(f"🔬 Auteur : {meta.get('AUTEUR')} · {meta.get('LABO')}")
    print(f"🛡️ Intégrité SHA-256 : {cerveau.modele.get('SIGNATURE_SHA256')[:16]}... (Vérifiée)")
    print(f"💡 Astuce : Dis-lui « Apprends que... » pour lui enseigner un fait en direct !")
    print(f"🚪 Tape « exit » ou « quitter » pour sortir.")
    print("=" * 68 + "\n")

    while True:
        try:
            entree = input("👤 Toi > ").strip()
            if not entree:
                continue
            if entree.lower() in ["exit", "quitter", "q"]:
                print("\n👋 RATISS-ONE : Au revoir ! Le tissu souverain garde ce qu'il a compris.\n")
                break
                
            res = cerveau.executer(entree, port="PORT_CHAT_INTERFACE")
            eth = res["eth"]
            
            print(f"\n🤖 RATISS [{res['intent']}] :")
            print(f"   « {res['reponse']} »")
            print(f"   ❤️ ETH : Ton={eth['ton'].upper()} | Pouls={eth['pouls']} bpm | Tension={eth['tension']}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nSession terminée.")
            break

if __name__ == "__main__":
    chemin = sys.argv[1] if len(sys.argv) > 1 else "/home/user/RATISS-ONE/cerveau/RatissOne.ratiss"
    demarrer_chat(chemin)
