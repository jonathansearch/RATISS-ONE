#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Met un corpus au format que la bouche sait lire.

La loi ne change pas selon le dataset. Seule la mise en ligne change.

Formats d'entrée :
  .txt                         prose, laissée telle quelle
  .jsonl {text}                une ligne JSON, champ text ou texte
  .jsonl {user, assistant}     devient : _q_ ... _r_ ...
  .jsonl {prompt, completion}  idem
  .jsonl {instruction, output} idem
  .jsonl {messages:[...]}      rôles user/assistant alternés

Sortie : UTF-8, une phrase ou un tour par ligne, prêt pour --eduquer.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def ligne_dialogue(question: str, reponse: str) -> str:
    q = " ".join(question.split())
    r = " ".join(reponse.split())
    return f"_q_ {q} _r_ {r}"


def depuis_obj(obj: dict) -> str | None:
    if not isinstance(obj, dict):
        return None
    if "text" in obj and isinstance(obj["text"], str):
        return obj["text"].strip()
    if "texte" in obj and isinstance(obj["texte"], str):
        return obj["texte"].strip()
    if "user" in obj and "assistant" in obj:
        return ligne_dialogue(str(obj["user"]), str(obj["assistant"]))
    if "prompt" in obj and "completion" in obj:
        return ligne_dialogue(str(obj["prompt"]), str(obj["completion"]))
    if "instruction" in obj and "output" in obj:
        entree = str(obj.get("input") or "").strip()
        question = str(obj["instruction"]).strip()
        if entree:
            question = question + " " + entree
        return ligne_dialogue(question, str(obj["output"]))
    msgs = obj.get("messages")
    if isinstance(msgs, list):
        morceaux = []
        for m in msgs:
            if not isinstance(m, dict):
                continue
            role = str(m.get("role", "")).lower()
            contenu = " ".join(str(m.get("content", "")).split())
            if not contenu:
                continue
            if role in {"user", "human"}:
                morceaux.append("_q_ " + contenu)
            elif role in {"assistant", "gpt", "bot"}:
                morceaux.append("_r_ " + contenu)
        if morceaux:
            return " ".join(morceaux)
    return None


def convertir(entree: Path) -> list[str]:
    if entree.suffix == ".txt":
        return [ln.strip() for ln in entree.read_text(encoding="utf-8").splitlines() if ln.strip()]
    lignes = []
    with entree.open(encoding="utf-8") as f:
        for brut in f:
            brut = brut.strip()
            if not brut:
                continue
            try:
                obj = json.loads(brut)
            except json.JSONDecodeError:
                lignes.append(brut)
                continue
            rendu = depuis_obj(obj)
            if rendu:
                lignes.append(rendu)
    return lignes


def main() -> int:
    p = argparse.ArgumentParser(description="Préparer un corpus pour la bouche")
    p.add_argument("--entree", required=True)
    p.add_argument("--sortie", required=True)
    p.add_argument("--registre", default="ordre", help="écrit en commentaire d'en-tête, pour toi. La bouche le reçoit par --registre")
    a = p.parse_args()
    entree = Path(a.entree)
    if not entree.is_file():
        print(f"introuvable : {entree}", file=sys.stderr)
        return 2
    lignes = convertir(entree)
    if not lignes:
        print("rien à écrire", file=sys.stderr)
        return 2
    sortie = Path(a.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    tete = f"# registre: {a.registre}\n# source: {entree.name}\n# lignes: {len(lignes)}\n"
    sortie.write_text(tete + "\n".join(lignes) + "\n", encoding="utf-8")
    print(f"{len(lignes)} lignes → {sortie}  (registre {a.registre})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
