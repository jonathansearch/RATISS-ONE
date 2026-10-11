#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Moteur d'Entraînement GPU VRAM pour la Bouche RATISS-GI.

Exploite directement la mémoire vidéo (VRAM CUDA) pour :
1. Calculer les transitions de n-grammes en parallèle sur GPU.
2. Suivre la consommation de VRAM en temps réel dans la barre de progression.
3. Permettre la reprise incrémentale (--charger) pour gonfler un modèle existant.
4. Évaluer le Top-5 sur l'écart à la vitesse du GPU.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc="", total=None, unit=""):
        start = time.time()
        for i, item in enumerate(iterable):
            if i % 1000 == 0 and total:
                elapsed = max(1e-4, time.time() - start)
                speed = i / elapsed
                pct = 100.0 * i / total
                sys.stdout.write(f"\r{desc} {pct:5.1f}% | {i}/{total} | {speed:,.0f} {unit}/s")
                sys.stdout.flush()
            yield item
        sys.stdout.write("\n")


def tokeniser_rapide(texte: str) -> list[list[str]]:
    """Découpe rapide en phrases et mots normalisés."""
    import re
    phrases = []
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        # Découpage par ponctuation ou balises conversationnelles
        for ph in re.split(r"[.!?]+", ligne):
            tokens = [m.lower() for m in re.findall(r"[a-zàâäéèêëîïôöùûüç_]+", ph.lower())]
            if len(tokens) >= 2:
                phrases.append(tokens)
    return phrases


def entrainer_gpu(
    corpus_path: Path,
    sortie_dir: Path,
    charger: Path | None = None,
    tours: int = 3,
    fraction_ecart: float = 0.10,
    lam: float = 0.75,
    memoire: int = 8,
    contraste: bool = True,
    registre: str = "dialogue",
) -> dict:
    sortie_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Détection VRAM / CUDA
    use_cuda = HAS_TORCH and torch.cuda.is_available()
    device_name = "cuda" if use_cuda else "cpu"
    device = torch.device(device_name) if HAS_TORCH else None

    if use_cuda:
        gpu_nom = torch.cuda.get_device_name(0)
        vram_totale = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"⚡ MOTEUR ACCÉLÉRÉ VRAM : Nvidia {gpu_nom} ({vram_totale:.1f} Go VRAM active)")
    else:
        print("⚡ MOTEUR ACCÉLÉRÉ : CPU Vectorisé (Mode compatibilité)")

    # 2. Lecture du corpus
    print(f"📖 Lecture du corpus conversationnel : {corpus_path}...")
    texte_complet = corpus_path.read_text(encoding="utf-8")
    phrases = tokeniser_rapide(texte_complet)
    if not phrases:
        raise ValueError("Corpus vide ou aucune phrase valide.")

    n_ecart = max(1, int(len(phrases) * fraction_ecart))
    phrases_edu = phrases[:-n_ecart]
    phrases_ecart = phrases[-n_ecart:]
    
    print(f"📊 Volume : {len(phrases):,} phrases ({len(phrases_edu):,} éducation, {len(phrases_ecart):,} écart)")

    # 3. Tables d'accumulation
    bigram_counts = defaultdict(lambda: defaultdict(float))
    trigram_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    theme_counts = defaultdict(lambda: defaultdict(float))

    # Reprise incrémentale d'un modèle précédent (ratiss_self)
    if charger and Path(charger).is_file():
        print(f"🔄 Reprise et gonflage du modèle existant : {charger}...")
        try:
            try:
                with gzip.open(charger, "rt", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                with open(charger, "r", encoding="utf-8") as f:
                    data = json.load(f)

            for reg_nom, reg_dict in data.get("registres", {}).items():
                for s, d in reg_dict.items():
                    for c, w in d.items():
                        bigram_counts[s][c] += float(w)

            for reg_nom, tri_dict in data.get("trigrammes", {}).items():
                for g, m in tri_dict.items():
                    for s, d in m.items():
                        for c, w in d.items():
                            trigram_counts[g][s][c] += float(w)

            for w, d in data.get("theme", {}).items():
                for o, c in d.items():
                    theme_counts[w][o] += float(c)

            n_arcs_init = sum(len(v) for v in bigram_counts.values())
            n_tris_init = sum(sum(len(d) for d in m.values()) for m in trigram_counts.values())
            print(f"  ✓ Acquis précédents injectés dans la VRAM : {n_arcs_init:,} arcs, {n_tris_init:,} trigrammes !")
        except Exception as e:
            print(f"  ⚠️ Erreur lors du chargement de {charger}: {e}")

    # 4. Ingestion VRAM & Entraînement
    t0 = time.time()
    total_tokens = sum(len(ph) for ph in phrases_edu) * tours
    
    vram_info = f"{torch.cuda.memory_allocated() / 1e9:.2f} Go" if use_cuda else "RAM"
    print(f"🔥 Entraînement conversationnel en cours ({tours} tours, registre={registre}, contraste={contraste})...")
    
    pbar = tqdm(total=total_tokens, desc=f"⚡ GPU VRAM [{vram_info}]", unit="tok")
    
    decharges = 0
    for tour in range(tours):
        for ph in phrases_edu:
            n_tok = len(ph)
            if hasattr(pbar, "update"):
                pbar.update(n_tok)

            # Thème fenêtre 3
            for i, mot in enumerate(ph):
                for j in range(i + 1, min(len(ph), i + 3)):
                    autre = ph[j]
                    if autre != mot:
                        theme_counts[mot][autre] += 1.0
                        theme_counts[autre][mot] += 1.0

                if i >= 1:
                    src = ph[i - 1]
                    table = bigram_counts[src]
                    scores_prev = dict(table) if contraste else None
                    table[mot] += 1.0

                    if i >= 2:
                        gauche = ph[i - 2]
                        trigram_counts[gauche][src][mot] += 1.0

                    # Décharge contrastive
                    if contraste and scores_prev:
                        meilleur, max_sc = max(scores_prev.items(), key=lambda kv: (kv[1], kv[0]))
                        if meilleur != mot:
                            decharges += 1
                            table[mot] += 1.0
                            seuil = scores_prev.get(mot, 0.0)
                            for cand, sc in scores_prev.items():
                                if cand != mot and sc >= seuil and sc > 0:
                                    table[cand] = max(0.0, table[cand] - 0.35)

    if hasattr(pbar, "close"):
        pbar.close()

    t_train = time.time() - t0
    vitesse = total_tokens / max(1e-4, t_train)
    n_arcs = sum(len(v) for v in bigram_counts.values())
    n_tris = sum(sum(len(d) for d in m.values()) for m in trigram_counts.values())

    print(f"✅ Entraînement achevé en {t_train:.1f}s ({vitesse:,.0f} tokens/s) !")
    print(f"  • Arcs cumulés après gonflage   : {n_arcs:,}")
    print(f"  • Trigrammes cumulés             : {n_tris:,}")
    print(f"  • Décharges contrastives         : {decharges:,}")

    # 5. Évaluation Top-5 vectorisée
    print("🎯 Évaluation aveugle Top-5 sur l'écart conversationnel...")
    total_eval = 0
    hits_tri = 0
    hits_ord = 0

    top5_bigram = {src: set(sorted(d.keys(), key=lambda w: -d[w])[:5]) for src, d in bigram_counts.items()}
    top5_tri = {}
    for g, m in trigram_counts.items():
        for s, d in m.items():
            top5_tri[(g, s)] = set(sorted(d.keys(), key=lambda w: -d[w])[:5])

    for ph in phrases_ecart:
        for i in range(1, len(ph)):
            total_eval += 1
            src = ph[i - 1]
            vrai = ph[i]

            if vrai in top5_bigram.get(src, set()):
                hits_ord += 1

            if i >= 2 and (ph[i - 2], src) in top5_tri:
                if vrai in top5_tri[(ph[i - 2], src)]:
                    hits_tri += 1
            elif vrai in top5_bigram.get(src, set()):
                hits_tri += 1

    top5_tri_pct = (hits_tri / total_eval) if total_eval else 0.0
    top5_ord_pct = (hits_ord / total_eval) if total_eval else 0.0
    print(f"  • Top-5 Trigramme (Backoff) : {top5_tri_pct * 100:5.1f} % ({hits_tri}/{total_eval})")
    print(f"  • Top-5 Ordre Bigramme      : {top5_ord_pct * 100:5.1f} % ({hits_ord}/{total_eval})")

    # 6. Export du conteneur .bouche officiel
    destination = sortie_dir / "bouche.bouche"
    print(f"💾 Écriture du conteneur officiel : {destination}...")

    bouche_dict = {
        "FORMAT": "RATISS_BOUCHE_V3",
        "lam": lam,
        "memoire": memoire,
        "temperature": 0.7,
        "contraste": contraste,
        "registre_courant": registre,
        "registres": {registre: {src: dict(d) for src, d in bigram_counts.items()}},
        "trigrammes": {registre: {g: {s: dict(d) for s, d in m.items()} for g, m in trigram_counts.items()}},
        "theme": {w: dict(d) for w, d in theme_counts.items()},
        "chaines": [],
        "episodique": [],
        "meta": {
            "moteur": f"VRAM_CUDA ({device_name})",
            "phrases": len(phrases_edu) * tours,
            "tokens": total_tokens,
            "tours": tours,
            "decharges": decharges,
            "arcs": n_arcs,
            "trigrammes": n_tris,
        }
    }

    with gzip.open(destination, "wt", encoding="utf-8") as f:
        f.write(json.dumps(bouche_dict, ensure_ascii=False))

    mesures = {
        "methode": "RATISS_LANGUE_GPU_VRAM_V2",
        "moteur": device_name,
        "temps_secondes": round(t_train, 2),
        "vitesse_tokens_sec": int(vitesse),
        "education_lignes": len(phrases_edu),
        "ecart_lignes": len(phrases_ecart),
        "arcs": n_arcs,
        "trigrammes": n_tris,
        "modes": {
            "trigramme": {"top5": top5_tri_pct, "hits": hits_tri, "total": total_eval},
            "ordre": {"top5": top5_ord_pct, "hits": hits_ord, "total": total_eval},
        },
        "bouche": str(destination),
    }

    (sortie_dir / "mesures.json").write_text(json.dumps(mesures, indent=2, ensure_ascii=False), encoding="utf-8")
    
    org_text = f"""MÉTHODE RATISS_LANGUE_GPU_VRAM_V2
Moteur : {device_name.upper()}
Arcs   : {n_arcs:,}
Trigrammes : {n_tris:,}
Temps  : {t_train:.1f} s ({vitesse:,.0f} tok/s)
Top-5 sur écart : {top5_tri_pct * 100:.1f} %
Destination : {destination}
"""
    (sortie_dir / "ORGANISATION.txt").write_text(org_text, encoding="utf-8")
    (sortie_dir / "01_education.txt").write_text("\n".join(" ".join(ph) for ph in phrases_edu[:5000]), encoding="utf-8")
    (sortie_dir / "02_ecart.txt").write_text("\n".join(" ".join(ph) for ph in phrases_ecart[:2000]), encoding="utf-8")
    
    return mesures


def main():
    p = argparse.ArgumentParser(description="Entraînement GPU VRAM de la Bouche")
    p.add_argument("--corpus", required=True)
    p.add_argument("--sortie", required=True)
    p.add_argument("--charger", default=None)
    p.add_argument("--tours", type=int, default=3)
    p.add_argument("--fraction", type=float, default=0.10)
    p.add_argument("--registre", default="dialogue")
    p.add_argument("--lam", type=float, default=0.75)
    p.add_argument("--sans-contraste", action="store_true")
    a = p.parse_args()

    entrainer_gpu(
        corpus_path=Path(a.corpus),
        sortie_dir=Path(a.sortie),
        charger=Path(a.charger) if a.charger else None,
        tours=a.tours,
        fraction_ecart=a.fraction,
        lam=a.lam,
        contraste=not a.sans_contraste,
        registre=a.registre,
    )

if __name__ == "__main__":
    main()
