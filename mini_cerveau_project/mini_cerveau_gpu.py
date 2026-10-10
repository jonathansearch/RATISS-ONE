# -*- coding: utf-8 -*-
# Architecture du Micro-Cerveau RATISS GPU T4
# Laboratoire de recherche RATISS, Yaoundé, Cameroun
# Auteur : Jonathan Evina

import torch
import re

def interroger_mini_cerveau(message, model_path="mini_cerveau_gpu.pt", device="cuda", top_k=2):
    device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
    modele = torch.load(model_path, map_location=device)
    vocab = modele["vocabulaire"]
    idx = modele["index"]
    W = modele["matrice_synaptique"]
    
    if not isinstance(W, torch.Tensor):
        W = torch.tensor(W, dtype=torch.float32, device=device)
    else:
        W = W.to(device)
        
    tokens = [w.lower() for w in re.findall(r"\b\w+\b", message) if len(w) > 2]
    h = torch.zeros(len(vocab), dtype=torch.float32, device=device)
    mots_reconnus = [t for t in tokens if t in idx]
    for t in mots_reconnus:
        h[idx[t]] += 2.0
        
    if not mots_reconnus:
        return "Concepts non trouvés dans les 957 mots clés."
        
    s = torch.matmul(W.t(), h)
    pivot_idx = torch.argmax(s).item()
    pivot_mot = vocab[pivot_idx]
    
    liens = W[pivot_idx]
    top_indices = torch.topk(liens, k=min(top_k + 3, len(vocab))).indices.tolist()
    
    mots_voisins = []
    for j in top_indices:
        if liens[j] > 0 and vocab[j] != pivot_mot and vocab[j] not in mots_voisins:
            mots_voisins.append(vocab[j])
            if len(mots_voisins) >= top_k:
                break
                
    if len(mots_voisins) >= 2:
        return f"Sur le sujet de « {pivot_mot} », connexions avec « {mots_voisins[0]} » et « {mots_voisins[1]} »."
    return f"Concept central : « {pivot_mot} »."
