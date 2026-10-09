#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conversation_v2.py — Démonstrateur de Dialogue Industriel v2
RATISS Labs · Auteur : Jonathan Evina · MIT

Démontre :
1. Politesse et reconnaissance d'intention enrichie (FR + EN).
2. Apprentissage one-shot en direct (Live Memory) sans rétropropagation.
3. Restitution instantanée certifiée avec signature SHA-256.
4. Modulation somatique du Corps ETH (pouls, ton).
5. Rétrocompatibilité avec les comptes et états physiques du tissu.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dialogue"))

from dialogue_v2 import repondre, obtenir_moteur
from cerveau.cerveau import Cerveau

SCENARIO = [
    # --- Volet Français ---
    ("FR", "bonjour mon pote"),
    ("FR", "qui es-tu ?"),
    ("FR", "tu tiens quoi ?"),
    ("FR", "combien as-tu entendu ?"),
    ("FR", "merci beaucoup"),
    ("FR", "explique-moi la fusion"),
    ("FR", "Apprends que Jonathan Evina a inventé l'architecture RATISS."),
    ("FR", "Qui a inventé l'architecture RATISS ?"),
    ("FR", "au revoir"),
    
    # --- Volet Anglais ---
    ("EN", "hello"),
    ("EN", "who are you?"),
    ("EN", "what do you hold?"),
    ("EN", "how many did you hear?"),
    ("EN", "thanks a lot"),
    ("EN", "Learn that Yaounde is the capital of Cameroon."),
    ("EN", "What is the capital of Cameroon?"),
    ("EN", "goodbye")
]

def main():
    print("=" * 72)
    print("🚀 RATISS-ONE : DÉMONSTRATION DU DIALOGUE v2 AVEC MÉMOIRE LIVE")
    print("=" * 72)
    
    c_fr = Cerveau("FR")
    c_en = Cerveau("EN")
    moteur = obtenir_moteur()
    
    t_global = time.time()
    for lg, question in SCENARIO:
        c = c_fr if lg == "FR" else c_en
        t0 = time.time()
        intent, langue, reponse = repondre(c, question)
        dt_ms = (time.time() - t0) * 1000
        
        print(f"\n👤 [{lg}] : « {question} »")
        print(f"🤖 RATISS [{intent}/{langue}] ({dt_ms:.2f} ms) :")
        print(f"   « {reponse} »")
        print(f"   ❤️ ETH : Ton={moteur.eth_etat['ton'].upper()} | Pouls={moteur.eth_etat['pouls']} bpm")

    duree_totale = (time.time() - t_global) * 1000
    print("\n" + "=" * 72)
    print(f"✅ 17 RÉPLIQUES TRAITÉES AVEC SUCCÈS EN {duree_totale:.2f} ms !")
    print("=" * 72)

if __name__ == "__main__":
    main()
