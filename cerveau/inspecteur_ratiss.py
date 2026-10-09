#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inspecteur_ratiss.py — Outil d'Audit & Inspection pour les Cerveaux .ratiss
RATISS Labs · Auteur : Jonathan Evina

Permet d'inspecter un conteneur .ratiss / .rt en mode boîte blanche :
- Vérification du Magic Header
- Audit d'intégrité cryptographique SHA-256
- Décompte des faits du Sanctuaire et de la Mémoire Épisodique
- Affichage des constantes vitales du Corps ETH
- Liste des ports de connectique officiels
"""

import os
import sys
import json
import hashlib

def inspecter_cerveau(chemin):
    print("=" * 68)
    print(f"🔍 AUDIT & INSPECTION BOÎTE BLANCHE DU CONTENEUR .ratiss")
    print(f"📁 Fichier : {chemin}")
    print("=" * 68)

    if not os.path.exists(chemin):
        print(f"❌ Erreur : Le fichier {chemin} n'existe pas.")
        return False

    taille = os.path.getsize(chemin)
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Fichier non décodable : {e}")
        return False

    # 1. Magic Header
    fmt = data.get("FORMAT", "INCONNU")
    print(f"• Format d'entête     : {fmt} {'✅' if 'RATISS' in fmt else '❌'}")

    # 2. Métadonnées
    meta = data.get("META", {})
    print(f"• Nom du Modèle       : {meta.get('NOM_MODELE', 'N/A')}")
    print(f"• Version             : {meta.get('VERSION', 'N/A')}")
    print(f"• Auteur              : {meta.get('AUTEUR', 'N/A')}")
    print(f"• Date de Scellement  : {meta.get('DATE_SCELLEMENT', 'N/A')}")

    # 3. Sceau Cryptographique
    sha_declare = data.get("SIGNATURE_SHA256", "AUCUN")
    data_sans_sha = {k: v for k, v in data.items() if k != "SIGNATURE_SHA256"}
    sha_calcule = hashlib.sha256(json.dumps(data_sans_sha, sort_keys=True).encode("utf-8")).hexdigest()
    
    valide = (sha_declare == sha_calcule)
    print(f"• Sceau Déclaré       : {sha_declare[:20]}...")
    print(f"• Sceau Re-calculé    : {sha_calcule[:20]}...")
    print(f"• Intégrité Cryptog.  : {'✅ INTÈGRE (ZÉRO ALTÉRATION)' if valide else '❌ ALTÉRÉ / CORROMPU'}")

    # 4. Organes Internes
    sanctuaire = data.get("SANCTUAIRE", {})
    episodique = data.get("MEMOIRE_EPISODIQUE", {})
    eth = data.get("BLOC_ETH", {})
    ports = data.get("PORTS_CONNECTIQUE", {})

    print(f"\n📊 ORGANES DU CERVEAU :")
    print(f"   - Faits au Sanctuaire  : {len(sanctuaire)} entités inaltérables")
    for k in sanctuaire:
        print(f"     * [{k.upper()}] : {sanctuaire[k].get('nom', k)}")
    print(f"   - Faits Épisodiques    : {len(episodique)} souvenirs appris en live")
    for k in list(episodique.keys())[:3]:
        print(f"     * [{k}] : « {episodique[k].get('enonce', '')[:40]}... » (#{episodique[k].get('sha256', '')})")
    print(f"   - Constantes Corps ETH : Pouls base={eth.get('pouls_base', 72)} bpm | Temp={eth.get('temperature_base', 37.0)}°C")
    print(f"   - Ports de Connectique : {len(ports)} interfaces standardisées")
    for p in ports:
        print(f"     * {p} ➔ {ports[p].get('nom', 'actif')}")

    print(f"\n💾 Poids total sur disque : {taille} octets")
    print("=" * 68)
    return valide

if __name__ == "__main__":
    cible = sys.argv[1] if len(sys.argv) > 1 else "/home/user/RATISS-ONE/cerveau/RatissOne.ratiss"
    inspecter_cerveau(cible)
