#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
assistant_vocal.py — Interface Principale Assistant Vocal & Cognitif
RATISS Labs · Auteur : Jonathan Evina

Permet de lancer l'assistant vocal de RATISS-ONE directement depuis le dossier interfaces/.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bouche.assistant_vocal_complet import AssistantVocalSouverain

def main():
    chemin_cerveau = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "cerveau", "RatissOne.ratiss"
    )
    assistant = AssistantVocalSouverain(chemin_cerveau)
    
    print("\n" + "=" * 65)
    print("🎙️ BIENVENUE DANS L'ASSISTANT VOCAL SOUVERAIN RATISS-ONE")
    print("=" * 65)
    print("Commandes vocales de test pré-configurées ou saisie libre.")
    print("Tape 'quit' pour quitter.\n")
    
    while True:
        try:
            msg = input("🎙️ Parler / Taper > ").strip()
            if not msg:
                continue
            if msg.lower() in ["quit", "exit", "q"]:
                print("Arrêt de l'assistant.")
                break
                
            assistant.executer_cycle_complet(msg, "derniere_reponse.wav")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
