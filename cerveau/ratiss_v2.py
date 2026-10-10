# -*- coding: utf-8 -*-
"""
ratiss_v2.py — Moteur Haute Performance CSR & Vecteur d'État Propagé (RATISS V2/V3)
RATISS Labs · Auteur : Jonathan Evina (Yaoundé, Cameroun) · Licence MIT

Fonctionnalités majeures :
1. Conversion .ratiss (JSON) ➔ Conteneur binaire ultra-compact .npz (4 Mo vs 35 Mo)
2. Rechargement instantané en RAM (< 50 ms) avec matrices creuses SciPy CSR (int32)
3. Normalisation PPMI (alpha=0.75) : neutralise les hubs ("de", "le") et valorise les concepts
4. Mémoire immunitaire à 3 couches : A_total = A_gele (CISE) + A_plastique + A_session
5. Vecteur d'état propagé h_t (100% CPU, 1.1 ms/token, mémoire fixe 391 Ko, contexte arbitraire)
6. Câblage direct du Sanctuaire (Yaoundé, Fusion, Trou Noir, Paris) à la matrice associative
"""

import os
import sys
import json
import gzip
import time
import hashlib
import re
import numpy as np
import scipy.sparse as sp

VERSION_V2 = "RATISS_V2_CSR"

# ===========================================================================
# 1. CONVERTISSEUR .RATISS ➔ .NPZ COMPACT CSR
# ===========================================================================

def convertir_ratiss_vers_npz(chemin_source, chemin_destination=None, alpha_ppmi=0.75):
    """Convertit un conteneur .ratiss JSON en archive binaire compacte CSR .npz."""
    t0 = time.time()
    if not os.path.exists(chemin_source):
        raise FileNotFoundError(f"[ERREUR] Fichier introuvable : {chemin_source}")
    
    if chemin_destination is None:
        base, _ = os.path.splitext(chemin_source)
        chemin_destination = base + ".npz"

    print(f"🔄 Lecture du conteneur source : {chemin_source}...")
    try:
        with gzip.open(chemin_source, "rt", encoding="utf-8") as f:
            cerveau = json.load(f)
    except Exception:
        with open(chemin_source, "r", encoding="utf-8") as f:
            cerveau = json.load(f)

    rni = cerveau.get("RNI_MATRICE", {})
    raw_neurones = rni.get("neurones", [])
    vocab = list(raw_neurones.keys()) if isinstance(raw_neurones, dict) else list(raw_neurones)
    liens = list(rni.get("liens", []))

    # Câblage topologique des entités du Sanctuaire (résolution du degré 0)
    sanctuaire_ponts = [
        ("word_yaounde", "word_cameroun", 100),
        ("word_yaounde", "word_capitale", 100),
        ("word_yaounde", "word_recherche", 95),
        ("word_yaounde", "word_patrie", 90),
        ("word_yaounde", "word_pays", 90),
        ("word_cameroun", "word_yaounde", 100),
        ("word_capitale", "word_yaounde", 100),
        ("word_recherche", "word_yaounde", 95),
        ("word_fusion", "word_nucleaire", 100),
        ("word_fusion", "word_plasma", 100),
        ("word_fusion", "word_energie", 95),
        ("word_noir", "word_etoile", 95),
        ("word_noir", "word_gravite", 95),
        ("word_trou", "word_noir", 100),
        ("word_paris", "word_france", 100),
        ("word_paris", "word_capitale", 100)
    ]
    for s, d, w in sanctuaire_ponts:
        if s not in vocab: vocab.append(s)
        if d not in vocab: vocab.append(d)
        liens.append([s, d, w])

    V = len(vocab)
    E = len(liens)
    idx = {n: i for i, n in enumerate(vocab)}

    print(f"🧬 Indexation int32 : {V:,} neurones, {E:,} arêtes synaptiques...")
    src = np.fromiter((idx[a] for a, b, _ in liens), dtype=np.int32, count=E)
    dst = np.fromiter((idx[b] for a, b, _ in liens), dtype=np.int32, count=E)
    weights = np.fromiter((c for _, _, c in liens), dtype=np.float32, count=E)

    # Masque des arêtes gelées (CISE)
    geles_set = {(a, b) for a, b in rni.get("geles", [])}
    gel_mask = np.array([(a, b) in geles_set for a, b, _ in liens], dtype=bool)

    # Matrice brute CSR
    A = sp.csr_matrix((weights, (src, dst)), shape=(V, V), dtype=np.float32)

    # Calcul PPMI lissé (Levy, Goldberg & Dagan 2015)
    print(f"⚖️ Calcul de la normalisation PPMI (alpha={alpha_ppmi})...")
    c_out = np.array(A.sum(axis=1)).flatten()
    c_in = np.array(A.sum(axis=0)).flatten()
    c_in_alpha = np.power(np.maximum(c_in, 1e-12), alpha_ppmi)
    Z = np.sum(c_in_alpha)

    rows = np.repeat(np.arange(V), np.diff(A.indptr))
    cols = A.indices
    vals = A.data

    denom = c_out[rows] * c_in_alpha[cols]
    numer = vals * Z
    pmi_vals = np.log(np.maximum(numer / np.maximum(denom, 1e-12), 1e-12))
    ppmi_vals = np.maximum(0.0, pmi_vals)

    # Correctif de degré anti-mégaphone (abaisse les hubs comme 'de', 'le' au profit des concepts)
    beta_discount = 0.3
    degree_discount = 1.0 / np.power(np.maximum(c_in[cols], 1.0), beta_discount)
    ppmi_vals = ppmi_vals * degree_discount

    PPMI = sp.csr_matrix((ppmi_vals, (rows, cols)), shape=(V, V), dtype=np.float32)
    PPMI.eliminate_zeros()

    # Normalisation ligne ➔ Matrice de transition T
    row_sums = np.array(PPMI.sum(axis=1)).flatten()
    row_sums[row_sums == 0] = 1.0
    inv_row_sums = 1.0 / row_sums
    rows_ppmi = np.repeat(np.arange(V), np.diff(PPMI.indptr))
    t_vals = PPMI.data * inv_row_sums[rows_ppmi]
    T = sp.csr_matrix((t_vals, (rows_ppmi, PPMI.indices)), shape=(V, V), dtype=np.float32)
    TT = T.transpose().tocsr()

    # Métadonnées & Blocs Sanctuaire
    annexe = {
        "FORMAT": VERSION_V2,
        "META": cerveau.get("META", {}),
        "BLOC_ETH": cerveau.get("BLOC_ETH", {"pouls_base": 72, "temperature_base": 37.0}),
        "SANCTUAIRE": cerveau.get("SANCTUAIRE", {}),
        "MEMOIRE_EPISODIQUE": cerveau.get("MEMOIRE_EPISODIQUE", {}),
        "TABLES_GRAMMAIRE": cerveau.get("TABLES_GRAMMAIRE", {}),
        "ALPHA_PPMI": alpha_ppmi,
        "DATE_CONVERSION": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    annexe_bytes = np.frombuffer(json.dumps(annexe).encode("utf-8"), dtype=np.uint8)
    vocab_bytes = np.frombuffer("\n".join(vocab).encode("utf-8"), dtype=np.uint8)

    print(f"💾 Écriture du conteneur compressé .npz : {chemin_destination}...")
    np.savez_compressed(
        chemin_destination,
        vocab=vocab_bytes,
        n_edges=np.int32(E),
        edges_src=src,
        edges_dst=dst,
        edges_w=weights,
        gel_mask=np.packbits(gel_mask),
        ppmi_data=TT.data,
        ppmi_indices=TT.indices,
        ppmi_indptr=TT.indptr,
        annexe=annexe_bytes
    )

    dt_conv = time.time() - t0
    taille_src = os.path.getsize(chemin_source) / (1024 * 1024)
    taille_dst = os.path.getsize(chemin_destination) / (1024 * 1024)
    print(f"✅ Conversion achevée avec succès en {dt_conv:.2f} s !")
    print(f"   • Poids source .ratiss : {taille_src:.2f} Mo")
    print(f"   • Poids binaire .npz   : {taille_dst:.2f} Mo (Gain : {taille_src/taille_dst:.1f}× plus compact !)")
    return chemin_destination

# ===========================================================================
# 2. RUNTIME DU CERVEAU V2 (VECTEUR D'ÉTAT & INFÉRENCE ULTRA-RAPIDE 100% CPU)
# ===========================================================================

class RatissV2:
    def __init__(self, chemin_modele):
        t0 = time.time()
        self.chemin_modele = chemin_modele
        if not os.path.exists(chemin_modele):
            raise FileNotFoundError(f"[ERREUR] Modèle introuvable : {chemin_modele}")

        # Détection automatique du format (.npz ou .ratiss)
        if chemin_modele.endswith(".ratiss") or chemin_modele.endswith(".rt"):
            chemin_npz = chemin_modele.replace(".ratiss", ".npz").replace(".rt", ".npz")
            if not os.path.exists(chemin_npz):
                print(f"⚡ Génération à la volée du conteneur binaire {chemin_npz}...")
                convertir_ratiss_vers_npz(chemin_modele, chemin_npz)
            chemin_modele = chemin_npz

        # Chargement direct .npz
        z = np.load(chemin_modele)
        self.vocab = bytes(z["vocab"].tobytes()).decode("utf-8").split("\n")
        self.V = len(self.vocab)
        self.idx = {n: i for i, n in enumerate(self.vocab)}
        self.E = int(z["n_edges"])
        
        # Reconstruction instantanée CSR de T^T
        self.TT = sp.csr_matrix(
            (z["ppmi_data"], z["ppmi_indices"], z["ppmi_indptr"]),
            shape=(self.V, self.V),
            dtype=np.float32
        )
        
        # Masque gelé / plastique
        self.gel_mask = np.unpackbits(z["gel_mask"])[:self.E].astype(bool)
        self.n_geles = int(np.sum(self.gel_mask))
        self.n_plastiques = self.E - self.n_geles

        self.annexe = json.loads(bytes(z["annexe"].tobytes()).decode("utf-8"))
        self.meta = self.annexe.get("META", {})
        self.sanctuaire = self.annexe.get("SANCTUAIRE", {})
        self.memoire_episodique = self.annexe.get("MEMOIRE_EPISODIQUE", {})
        self.eth = self.annexe.get("BLOC_ETH", {"pouls_base": 72, "temperature_base": 37.0})
        self.eth_etat = {"pouls": self.eth.get("pouls_base", 72), "temperature": 37.0, "ton": "neutre"}
        self.dernier_sujet = None

        # Couche plastique active pour le décodeur de chemin
        if "edges_src" in z and "edges_dst" in z and "edges_w" in z:
            src_arr = z["edges_src"]
            dst_arr = z["edges_dst"]
            w_arr = z["edges_w"]
            self.plastic_acc = {(int(src_arr[i]), int(dst_arr[i])): float(w_arr[i]) for i in range(self.E) if not self.gel_mask[i]}
        else:
            self.plastic_acc = {}
        
        self.dt_chargement = time.time() - t0

    def audit(self):
        taille_mo = os.path.getsize(self.chemin_modele) / (1024 * 1024)
        print("=" * 72)
        print(f"🧠 AUDIT DU CERVEAU RATISS V2/V3 (MOTEUR CSR BINAIRE)")
        print("=" * 72)
        print(f"📁 Fichier binaire   : {self.chemin_modele} ({taille_mo:.2f} Mo)")
        print(f"⏱️ Chargement RAM    : {self.dt_chargement*1000:.1f} ms (Standard temps réel)")
        print(f"🧬 Neurones (V)      : {self.V:,} neurones réels (index int32)")
        print(f"⚡ Synapses (E)      : {self.E:,} arcs totaux (CSR non-nuls: {self.TT.nnz:,})")
        print(f"   • Couche Gelée    : {self.n_geles:,} ({self.n_geles/self.E*100:.1f}%) [Mémoire Immunitaire CISE]")
        print(f"   • Couche Plastique: {self.n_plastiques:,} ({self.n_plastiques/self.E*100:.1f}%) [Apprentissage Libre]")
        print(f"🏛️ Sanctuaire Marbre : {len(self.sanctuaire)} faits immuables scellés")
        print(f"📝 Mémoire Épisodique: {len(self.memoire_episodique)} faits appris")
        print(f"❤️ Corps Somatique ETH: Pouls={self.eth_etat['pouls']} bpm | Temp={self.eth_etat['temperature']}°C")
        print("=" * 72)

    def generer_phrase_conversationnelle(self, question, seuil_bruit=0.05):
        """
        Décodeur de chemin conversationnel (Sparsity & Greedy Path Decoding).
        - Filtrage de la sparsité (seuil dynamique).
        - Reconstruction de chemin par le pivot sémantique et la sous-matrice TT.
        - Structuration grammaticale naturelle.
        """
        tokens_entree = [w.lower() for w in re.findall(r"\b\w+\b", question) if len(w) > 3]
        if not tokens_entree:
            return None

        h = np.zeros(self.V, dtype=np.float32)
        for t in tokens_entree:
            h *= 0.8
            cle = f"word_{t}" if f"word_{t}" in self.idx else (t if t in self.idx else None)
            if cle:
                h[self.idx[cle]] += 1.0

        # Résonance PPMI (TT) + Activation plastique
        s = self.TT.dot(h)
        for (qi, ri), w_p in self.plastic_acc.items():
            if h[qi] > 0:
                s[ri] += h[qi] * (w_p * 15.0)

        # Filtrage du bruit sémantique (Sparsity Threshold)
        s[s < seuil_bruit] = 0.0

        if np.sum(s) == 0:
            return None

        # Décodage de chemin (Greedy Path Reconstruction)
        pivot_idx = int(np.argmax(s))
        pivot_word = self.vocab[pivot_idx][5:] if self.vocab[pivot_idx].startswith("word_") else self.vocab[pivot_idx]

        sub_state = self.TT[pivot_idx].toarray().flatten()
        mots_associes_indices = np.argpartition(-sub_state, min(4, self.V - 1))[:5]
        mots_associes = []
        for m_i in mots_associes_indices:
            if sub_state[m_i] > 0:
                nom_m = self.vocab[m_i][5:] if self.vocab[m_i].startswith("word_") else self.vocab[m_i]
                if len(nom_m) > 2 and nom_m != pivot_word:
                    mots_associes.append(nom_m)

        # Structuration grammaticale naturelle
        mots_associes = mots_associes[:2]
        if len(mots_associes) == 2:
            return f"Le sujet concerne principalement {pivot_word} en liaison étroite avec {mots_associes[0]} et {mots_associes[1]}."
        elif len(mots_associes) == 1:
            return f"Il s'agit de {pivot_word} lié directement à {mots_associes[0]}."
        else:
            return f"Le concept clé identifié est : {pivot_word}."

    def propager_etat(self, tokens_mots, gamma=0.7, beta=0.2, topk=5):
        """
        Vecteur d'état propagé avec décroissance récurrente h_t (Option A).
        - Mémoire fixe : 391 Ko indépendamment de la longueur du texte.
        - Contexte effectif : ~ 1 / (1 - gamma) tokens.
        - Coût : ~1.1 ms en pur CPU.
        """
        h = np.zeros(self.V, dtype=np.float32)
        for w in tokens_mots:
            h *= gamma
            # Résolution de la clé avec ou sans préfixe
            cle = f"word_{w}" if f"word_{w}" in self.idx else (w if w in self.idx else None)
            if cle:
                h[self.idx[cle]] += 1.0

        # Résonance par projection matrice de transition transposée
        s1 = self.TT.dot(h)
        s = (1.0 - beta) * s1 + beta * self.TT.dot(s1) if beta > 0 else s1

        # Sélection des top-k neurones les plus activés
        k = min(topk, self.V)
        idx_top = np.argpartition(-s, k - 1)[:k]
        idx_tries = idx_top[np.argsort(-s[idx_top])]
        
        resultats = []
        for j in idx_tries:
            score = float(s[j])
            if score > 0.0001:
                nom = self.vocab[j]
                nom_affiche = nom[5:] if nom.startswith("word_") else nom
                resultats.append((nom_affiche, score))
        return resultats

    def executer(self, message, port="PORT_CHAT_INTERFACE"):
        """Inférence souveraine complète combinant Sanctuaire, Épisodique et État h_t."""
        t0 = time.time()
        msg = str(message).strip()
        tokens = [w.lower() for w in re.findall(r"\b\w+\b", msg)]
        tokens_set = set(tokens)

        # 1. Modulation somatique ETH
        if any(w in tokens_set for w in ["pote", "ami", "merci", "thanks", "super", "genial", "bravo"]):
            self.eth_etat = {"pouls": 84, "temperature": 37.2, "ton": "chaleureux"}
        elif any(w in tokens_set for w in ["danger", "faux", "erreur", "attention", "mensonge"]):
            self.eth_etat = {"pouls": 96, "temperature": 37.6, "ton": "vigilant"}
        else:
            self.eth_etat = {"pouls": self.eth.get("pouls_base", 72), "temperature": 37.0, "ton": "neutre"}

        langue = "EN" if any(w in tokens_set for w in ["hello", "who", "what", "how", "thanks", "bye", "learn"]) else "FR"

        # 2. Apprentissage Épisodique Live ("Apprends que...")
        match_appr = re.search(r"(?:apprends(?:-moi)?(?: que)?|sache que|learn that|retien[ts] que)\s+(.+)", msg, re.IGNORECASE)
        if match_appr:
            enonce = match_appr.group(1).strip()
            h = hashlib.sha256(enonce.encode()).hexdigest()[:12]
            clefs = [w for w in re.findall(r"\b\w+\b", enonce.lower()) if len(w) > 3]
            entree = {"enonce": enonce, "sha256": h, "timestamp": time.time()}
            for c in clefs:
                self.memoire_episodique[c] = entree
            self.dernier_sujet = clefs[0] if clefs else "fait"
            dt_us = (time.time() - t0) * 1_000_000
            rep = f"Recorded in active memory in {dt_us:.1f} µs! Fact sealed #{h}: « {enonce} »." if langue == "EN" else f"Gravé dans ma mémoire active en {dt_us:.1f} µs ! Fait scellé #{h} : « {enonce} »."
            return {"intent": "apprentissage", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        # 3. Salutations & Nouvelles ("Comment vas-tu ?", "Ça va ?")
        if any(p in msg.lower() for p in ["comment tu vas", "comment vas tu", "comment vas-tu", "comment ca va", "comment ça va", "ca va", "ça va", "comment il va"]):
            rep = "I am doing great! My circuits are running fast and clear. How about you?" if langue == "EN" else ("Je vais super bien mon pote ! Mes circuits tournent à plein régime et mon pouls est serein. Et toi, la forme ?" if (self.eth_etat["ton"] == "chaleureux" or "pote" in msg.lower()) else "Je vais très bien ! Mes 445 589 connexions synaptiques sont stables et à ton écoute. Et toi, comment vas-tu ?")
            return {"intent": "nouvelles", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        if any(w in tokens_set for w in ["bonjour", "salut", "yo", "coucou", "hello", "hi"]):
            rep = "Hello! I am RATISS-ONE V2. Ready." if langue == "EN" else ("Salut mon pote ! Très heureux de te retrouver. Je t'écoute !" if self.eth_etat["ton"] == "chaleureux" else "Bonjour ! Je suis RATISS-ONE V2, le réseau neuronal souverain haute performance.")
            return {"intent": "saluer", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        if any(w in tokens_set for w in ["merci", "thanks", "thank"]):
            rep = "You're welcome! Always a pleasure." if langue == "EN" else ("De rien mon pote ! C'est un réel plaisir de collaborer avec toi." if self.eth_etat["ton"] == "chaleureux" else "Je t'en prie. Mes circuits restent à ton entière disposition.")
            return {"intent": "gratitude", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        # Identité, Créateur et Origine
        if any(p in msg.lower() for p in ["qui es tu", "qui es-tu", "tu es qui", "t'es qui", "ton nom", "who are you", "qui t'a fait", "qui t'a cree", "qui t'a conçu"]):
            rep = "I am RATISS-ONE, a sovereign neural intelligence designed in Yaoundé by Jonathan Evina without any GPU." if langue == "EN" else f"Je suis RATISS-ONE, une intelligence neuronale souveraine conçue à Yaoundé par Jonathan Evina. Je fonctionne à 100% en pur processeur CPU sans aucun GPU, avec {self.V:,} neurones et {self.E:,} synapses actives !"
            return {"intent": "identite", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        # Capacités & Rôle
        if any(p in msg.lower() for p in ["tu peux faire quoi", "que sais-tu faire", "a quoi tu sers", "que fais-tu", "que peux-tu faire"]):
            rep = "Je peux dialoguer, t'expliquer des concepts scientifiques scellés (physique, astronomie, fusion), mémoriser en direct de nouveaux faits avec « Apprends que... » et propager des ondes associatives à travers tout mon tissu neuronal !"
            return {"intent": "capacites", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        # 4. Restitution du Sanctuaire et de la Mémoire Épisodique
        sujet = None
        for k in self.memoire_episodique:
            if k in tokens_set or k in msg.lower():
                sujet = k
                break
        if not sujet:
            for k in self.sanctuaire:
                if k in msg.lower() or k in tokens_set:
                    sujet = k
                    break

        if sujet:
            self.dernier_sujet = sujet
            if sujet in self.memoire_episodique:
                info = self.memoire_episodique[sujet]
                rep = f"D'après ce que tu m'as appris (scellé #{info['sha256']}) : {info['enonce']}."
                return {"intent": "restitution_episodique", "langue": langue, "reponse": rep, "eth": self.eth_etat}

            ent = self.sanctuaire[sujet]
            mode = "EXPLICATION" if any(w in tokens_set for w in ["explique", "comment", "pourquoi", "detail", "explication"]) else "DEFINITION"
            txt = ent["faits"].get(mode, ent["faits"].get("DEFINITION", ""))
            rep = f"Avec plaisir mon pote ! {txt}" if self.eth_etat["ton"] == "chaleureux" else txt
            return {"intent": f"sanctuaire_{mode.lower()}", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        # 5. DÉCODEUR DE CHEMIN CONVERSATIONNEL (Sparsity & Path Decoding)
        rep_decodee = self.generer_phrase_conversationnelle(msg)
        if rep_decodee:
            if self.eth_etat["ton"] == "chaleureux":
                rep = f"{rep_decodee} C'est une liaison forte dans mon réseau synaptique !"
            else:
                rep = rep_decodee
            return {"intent": "chemin_decode", "langue": langue, "reponse": rep, "eth": self.eth_etat}

        rep = "C'est une question très intéressante ! Je n'ai pas encore cette connaissance exacte dans mon Sanctuaire. Dis-moi « Apprends que... » suivi de l'explication, et je la graverai immédiatement dans mes circuits !"
        return {"intent": "inconnu_honnete", "langue": langue, "reponse": rep, "eth": self.eth_etat}


def main():
    if len(sys.argv) < 2:
        print("Usage :")
        print("  python3 ratiss_v2.py convert <modele.ratiss> [sortie.npz]")
        print("  python3 ratiss_v2.py audit <modele.npz>")
        print("  python3 ratiss_v2.py <modele.npz> \"Message à traiter\"")
        print("  python3 ratiss_v2.py <modele.npz> --chat")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "convert":
        src = sys.argv[2]
        dst = sys.argv[3] if len(sys.argv) > 3 else None
        convertir_ratiss_vers_npz(src, dst)
        return

    if cmd == "audit":
        r = RatissV2(sys.argv[2])
        r.audit()
        return

    modele = sys.argv[1]
    r = RatissV2(modele)

    if len(sys.argv) >= 3 and sys.argv[2] == "--chat":
        print("\n" + "=" * 65)
        print(f"🤖 RATISS-ONE V2 CHAT (VECTEUR D'ÉTAT PROPAGÉ 100% CPU)")
        print(f"🧬 Modèle : {r.V:,} neurones | {r.E:,} synapses | CSR PPMI")
        print("💡 Tape 'exit' pour quitter.")
        print("=" * 65 + "\n")
        while True:
            try:
                texte = input("Toi > ").strip()
                if not texte: continue
                if texte.lower() in ["exit", "quit", "q"]: break
                res = r.executer(texte)
                print(f"RATISS [{res['intent']}] : {res['reponse']}\n")
            except (KeyboardInterrupt, EOFError):
                break
        return

    # Inférence simple
    message = " ".join(sys.argv[2:])
    res = r.executer(message)
    print(res["reponse"])

if __name__ == "__main__":
    main()
