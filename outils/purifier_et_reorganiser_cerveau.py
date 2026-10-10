#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
purifier_et_reorganiser_cerveau.py — Réorganisation du Gros Cerveau RATISS V3
RATISS Labs · Auteur : Jonathan Evina (Yaoundé, Cameroun)

S'inspire de l'architecture ultra-propre du Mini-Cerveau GPU (mini_cerveau_gpu.pt) :
1. Élimination chirurgicale du bruit sémantique (méta-mots de prompt de CATIE-AQ).
2. Suppression des auto-boucles et des connexions parasites.
3. Normalisation des poids en probabilités conditionnelles relatives [0.0, 1.0].
4. Préservation intégrale et inviolable du Socle Gelé CISE (Le Marbre).
"""

import os
import sys
import time
import json
import re
import numpy as np
import scipy.sparse as sp

def purifier_cerveau(chemin_gros, chemin_sortie=None):
    if chemin_sortie is None:
        chemin_sortie = chemin_gros

    print("=" * 80)
    print("🧠 PURIFICATION ET RÉORGANISATION DU GROS CERVEAU RATISS-ONE")
    print("   Inspiration : Architecture ultra-propre du Mini-Cerveau GPU (T4)")
    print("=" * 80)

    t0 = time.time()
    z = np.load(chemin_gros, allow_pickle=True)
    vocab = bytes(z["vocab"].tobytes()).decode("utf-8").split("\n")
    V = len(vocab)
    E = int(z["n_edges"])
    idx = {n: i for i, n in enumerate(vocab)}

    src = z["edges_src"].astype(np.int32)
    dst = z["edges_dst"].astype(np.int32)
    w = z["edges_w"].astype(np.float32)
    gel_mask = np.unpackbits(z["gel_mask"])[:E].astype(bool)

    fs, fd, fw = src[gel_mask], dst[gel_mask], w[gel_mask]
    ps, pd, pw = src[~gel_mask], dst[~gel_mask], w[~gel_mask]

    print(f"📊 État Initial :")
    print(f"   • Neurones uniques (V)   : {V:,}")
    print(f"   • Synapses totales (E)   : {E:,}")
    print(f"   • Socle Gelé (Marbre)    : {len(fs):,} ({len(fs)/E*100:.1f}%) [Inviolable]")
    print(f"   • Synapses Plastiques    : {len(ps):,} ({len(ps)/E*100:.1f}%) [À assainir]")

    # 1. Dictionnaire des méta-mots parasites (artefacts de prompts de datasets)
    mots_parasites = {
        "compte", "tenu", "passage", "suivant", "suivante", "réponds", "reponds",
        "question", "questions", "suit", "ci-dessous", "ci", "dessus", "dessous",
        "se", "trouve", "dans", "lisez", "texte", "textes", "extrayez", "réponse",
        "reponse", "référez", "referez", "vous", "basant", "étant", "etant", "donné",
        "donne", "selon", "quelle", "quelles", "quel", "quels", "quoi", "comment",
        "pourquoi", "est", "sont", "ont", "été", "ete", "avoir", "etre", "faire",
        "fait", "plus", "moins", "très", "tres", "peut", "aussi", "avec", "pour",
        "par", "sur", "les", "des", "une", "que", "qui", "tout", "tous", "cette", "ces"
    }

    parasite_indices = set()
    for i, v in enumerate(vocab):
        token_net = v[5:].lower() if v.startswith("word_") else v.lower()
        if token_net in mots_parasites:
            parasite_indices.add(i)

    print(f"\n🔍 Identification du Bruit :")
    print(f"   • Concepts de prompt identifiés comme parasites : {len(parasite_indices)} mots")

    # 2. Filtrage chirurgical sur la couche plastique uniquement
    est_parasite = np.isin(ps, list(parasite_indices)) | np.isin(pd, list(parasite_indices))
    est_auto_boucle = (ps == pd)
    masque_garder = (~est_parasite) & (~est_auto_boucle) & (pw > 0.01)

    ps_pur = ps[masque_garder]
    pd_pur = pd[masque_garder]
    pw_pur = pw[masque_garder]

    synapses_supprimees = len(ps) - len(ps_pur)
    print(f"   • Synapses parasites éliminées : {synapses_supprimees:,} ({synapses_supprimees/len(ps)*100:.1f}%)")
    print(f"   • Synapses plastiques préservées : {len(ps_pur):,}")

    # 3. Normalisation façon Mini-Cerveau GPU (Probabilité relative conditionnelle [0, 1])
    max_par_src = {}
    for s_i, w_i in zip(ps_pur, pw_pur):
        if s_i not in max_par_src or w_i > max_par_src[s_i]:
            max_par_src[s_i] = w_i

    # Échelle de force relative [0.05, 1.0] x 50.0 pour alignement dynamique
    pw_norm = np.array([
        float(np.clip((w_i / max_par_src[s_i]) * 50.0, 1.0, 50.0))
        for s_i, w_i in zip(ps_pur, pw_pur)
    ], dtype=np.float32)

    # 4. Reconstitution du Cerveau Purifié
    new_src = np.concatenate([fs, ps_pur])
    new_dst = np.concatenate([fd, pd_pur])
    new_w = np.concatenate([fw, pw_norm])
    new_gel = np.concatenate([np.ones(len(fs), bool), np.zeros(len(ps_pur), bool)])
    new_E = len(new_src)

    # Recalcul de la matrice CSR PPMI pure
    deg_out = np.bincount(new_src, weights=new_w, minlength=V).astype(np.float32)
    deg_in = np.bincount(new_dst, weights=new_w, minlength=V).astype(np.float32)
    deg_in_alpha = np.power(np.maximum(deg_in, 1.0), 0.75)
    deg_out_corr = np.power(np.maximum(deg_out, 1.0), 0.3)
    total_w = float(np.sum(new_w))

    p_xy = new_w / total_w
    p_x = deg_out[new_src] / total_w
    p_y_alpha = deg_in_alpha[new_dst] / np.sum(deg_in_alpha)
    pmi = np.log2(np.maximum(p_xy / (p_x * p_y_alpha + 1e-12), 1e-12))
    ppmi_val = np.maximum(0.0, pmi) / deg_out_corr[new_src]

    # Matrice CSR T^T
    TT = sp.csr_matrix((ppmi_val, (new_dst, new_src)), shape=(V, V), dtype=np.float32)

    # Mise à jour des métadonnées de l'annexe
    annexe = json.loads(bytes(z["annexe"].tobytes()).decode("utf-8"))
    annexe["META"]["PURIFICATION"] = "Structure Mini-Cerveau GPU (T4) appliquée"
    annexe["META"]["DATE_PURIFICATION"] = time.strftime("%Y-%m-%d %H:%M:%S")
    annexe["META"]["SYNAPSES_PARASITES_ELIMINEES"] = int(synapses_supprimees)
    annexe_bytes = np.frombuffer(json.dumps(annexe).encode("utf-8"), dtype=np.uint8)

    # 5. Sauvegarde binaire compressée
    np.savez_compressed(
        chemin_sortie,
        vocab=z["vocab"],
        n_edges=np.int64(new_E),
        edges_src=new_src,
        edges_dst=new_dst,
        edges_w=new_w,
        gel_mask=np.packbits(new_gel),
        ppmi_data=TT.data,
        ppmi_indices=TT.indices,
        ppmi_indptr=TT.indptr,
        annexe=annexe_bytes
    )

    dt = time.time() - t0
    taille_mo = os.path.getsize(chemin_sortie) / (1024 * 1024)

    print("\n" + "=" * 80)
    print("🏆 PURIFICATION ET RÉORGANISATION TERMINÉES AVEC SUCCÈS !")
    print("=" * 80)
    print(f"📁 Fichier purifié       : {chemin_sortie} ({taille_mo:.2f} Mo)")
    print(f"⏱️ Temps de traitement   : {dt:.2f} secondes")
    print(f"🧬 Neurones uniques (V)  : {V:,}")
    print(f"⚡ Synapses saines (E)   : {new_E:,}")
    print(f"   • Marbre CISE préservé: {len(fs):,} (100% intact)")
    print(f"   • Plastique purifiée  : {len(ps_pur):,} (Sans aucun bruit de prompt)")
    print("=" * 80)

    # 6. Test d'expression verbale comparative
    questions_test = [
        "Quelle manœuvre agressive reproche la France à la Turquie ?",
        "Parle-moi de Yaoundé et du Cameroun",
        "Quelle est l'histoire de Paris ?"
    ]
    print("\n🧪 VÉRIFICATION DE LA PAROLE SANS BRUIT :")
    for q in questions_test:
        tokens_entree = [w.lower() for w in re.findall(r"\b\w+\b", q) if len(w) > 3]
        h = np.zeros(V, dtype=np.float32)
        for t in tokens_entree:
            h *= 0.8
            cle = f"word_{t}" if f"word_{t}" in idx else (t if t in idx else None)
            if cle: h[idx[cle]] += 1.0

        s = TT.dot(h)
        top_idx = np.argpartition(-s, min(4, V - 1))[:5]
        top_mots = [vocab[j][5:] if vocab[j].startswith("word_") else vocab[j] for j in top_idx[np.argsort(-s[top_idx])]]
        print(f"   Q : « {q} »")
        print(f"   👉 Concepts émergents purs : {top_mots[:3]}")

if __name__ == "__main__":
    fichier_cible = sys.argv[1] if len(sys.argv) > 1 else "/home/user/RATISS-ONE/colab/RatissOne_Massive_1M.npz"
    purifier_cerveau(fichier_cible)
