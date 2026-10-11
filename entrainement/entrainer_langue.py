#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Méthode d'entraînement de la langue. Dix pas, toujours dans le même ordre.

Ce n'est pas un autre modèle. C'est l'ordre dans lequel on a le droit
de nourrir la bouche après les quatre piliers :

  1. oreille          le fichier devient des lignes
  2. séparation       éducation d'un côté, écart de l'autre
  3. étape 0          bouche vide, ou une bouche déjà commencée
  4. prose            compte, registre, tours, décharge
  5. faits            chaînes gelées, hors décharge
  6. épisodes         une passe, contraste coupé
  7. retouches        une case, après le compte
  8. top-5            seulement sur l'écart
  9. audit            la formule, sur quelques vrais mots suivants
  10. dépôt           .bouche, mesures, audit. Pas le .ratiss.

Le tissu, s'il est nommé, n'est pas parsé. On hash ses octets avant
et après. S'ils diffèrent, on s'arrête.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from ratiss_v3 import Bouche, phrases_de

METHODE = "RATISS_LANGUE_V1"
PAS = (
    "oreille",
    "separation",
    "etape_0",
    "prose",
    "faits",
    "episodes",
    "retouches",
    "top5",
    "audit",
    "depot",
)


def sha256_fichier(chemin: Path) -> str | None:
    if not chemin.is_file():
        return None
    h = hashlib.sha256()
    with chemin.open("rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def lignes_utiles(chemin: Path) -> list[str]:
    if not chemin.is_file():
        raise FileNotFoundError(str(chemin))
    out = []
    for brut in chemin.read_text(encoding="utf-8").splitlines():
        ligne = brut.strip()
        if not ligne or ligne.startswith("#"):
            continue
        out.append(ligne)
    return out


def separer_queue(lignes: list[str], fraction: float) -> tuple[list[str], list[str]]:
    """La queue du fichier est l'écart. Pas un tirage. L'ordre des lignes reste."""
    if not 0.0 < fraction < 0.5:
        raise ValueError("la fraction tenue à l'écart doit être entre 0 et 0,5")
    if len(lignes) < 5:
        raise ValueError("au moins 5 lignes pour couper une queue sans vider l'éducation")
    n_ecart = max(1, int(round(len(lignes) * fraction)))
    if n_ecart >= len(lignes):
        n_ecart = len(lignes) // 5 or 1
    return lignes[:-n_ecart], lignes[-n_ecart:]


def ecrire_lignes(chemin: Path, titre: str, lignes: list[str]) -> None:
    corps = "\n".join(lignes)
    chemin.write_text(f"# {titre}\n# lignes: {len(lignes)}\n{corps}\n", encoding="utf-8")


def lire_retouches(chemin: Path, registre_defaut: str) -> list[dict]:
    ops = []
    for i, ligne in enumerate(lignes_utiles(chemin), start=1):
        morceaux = ligne.split()
        verbe = morceaux[0].lower()
        if verbe == "editer":
            if len(morceaux) not in (4, 5):
                raise ValueError(f"retouche {i} : editer SOURCE CIBLE POIDS [registre]")
            ops.append(
                {
                    "op": "editer",
                    "source": morceaux[1],
                    "cible": morceaux[2],
                    "poids": float(morceaux[3]),
                    "registre": morceaux[4] if len(morceaux) == 5 else registre_defaut,
                }
            )
        elif verbe == "supprimer":
            if len(morceaux) not in (3, 4):
                raise ValueError(f"retouche {i} : supprimer SOURCE CIBLE [registre]")
            ops.append(
                {
                    "op": "supprimer",
                    "source": morceaux[1],
                    "cible": morceaux[2],
                    "registre": morceaux[3] if len(morceaux) == 4 else registre_defaut,
                }
            )
        else:
            raise ValueError(f"retouche {i} : verbe inconnu {verbe!r} (editer ou supprimer)")
    return ops


def appliquer_retouches(bouche: Bouche, ops: list[dict]) -> list[dict]:
    faits = []
    for op in ops:
        if op["op"] == "editer":
            recu = bouche.editer_synapse(op["source"], op["cible"], op["poids"], registre=op["registre"])
        else:
            recu = bouche.supprimer_synapse(op["source"], op["cible"], registre=op["registre"])
        faits.append(recu)
    return faits


def positions_audit(texte: str, limite: int) -> list[tuple[list[str], str]]:
    pris = []
    for ph in phrases_de(texte):
        for i in range(1, len(ph)):
            pris.append((ph[:i], ph[i]))
            if len(pris) >= limite:
                return pris
    return pris


def alleger(explication: dict) -> dict:
    ordre = explication.get("ordre", {})
    for cle in ("bigramme", "trigramme"):
        if isinstance(ordre.get(cle), dict):
            ordre[cle].pop("table_brute", None)
    return explication


def entrainer_langue(
    *,
    education: Path,
    sortie: Path,
    registre: str = "conte",
    tours: int = 3,
    contraste: bool = True,
    ecart: Path | None = None,
    fraction: float | None = None,
    faits: Path | None = None,
    episodes: Path | None = None,
    retouches: Path | None = None,
    charger: Path | None = None,
    cerveau: Path | None = None,
    lam: float = 0.75,
    memoire: int = 8,
    audit_max: int = 5,
    normaliser_degre: bool = True,
) -> dict:
    sortie.mkdir(parents=True, exist_ok=True)
    journal = []

    def pas(nom: str, detail: str) -> None:
        journal.append(f"{len(journal) + 1}. {nom} — {detail}")

    h_avant = sha256_fichier(cerveau) if cerveau else None
    pas("oreille", f"lecture de {education}")
    lignes_edu = lignes_utiles(education)

    if ecart is not None:
        lignes_ecart = lignes_utiles(ecart)
        pas("separation", f"écart fourni à part : {len(lignes_ecart)} lignes, non mélangées")
    elif fraction is not None:
        lignes_edu, lignes_ecart = separer_queue(lignes_edu, fraction)
        pas("separation", f"queue {fraction:.0%} tenue à l'écart : {len(lignes_ecart)} lignes, tête {len(lignes_edu)}")
    else:
        lignes_ecart = []
        pas("separation", "pas d'écart : le top-5 ne sera pas publié")

    ecrire_lignes(sortie / "01_education.txt", "prose réellement comptée", lignes_edu)
    ecrire_lignes(sortie / "02_ecart.txt", "texte non donné à eduquer", lignes_ecart)

    if charger is not None:
        bouche = Bouche.charger(str(charger))
        pas("etape_0", f"reprise de {charger}")
    else:
        bouche = Bouche()
        pas("etape_0", "bouche vide, zéro arc")
    bouche.registre = registre
    bouche.lam = lam
    bouche.memoire = memoire
    bouche.contraste = contraste

    texte_edu = "\n".join(lignes_edu)
    stats = bouche.eduquer(texte_edu, tours=tours, registre=registre, contraste=contraste)
    pas(
        "prose",
        f"registre {registre}, {stats['phrases']} phrases, {stats['tours']} tours, "
        f"{stats['arcs']} arcs, {stats['decharges']} décharges, contraste={contraste}",
    )

    n_faits = 0
    lignes_faits: list[str] = []
    if faits is not None:
        lignes_faits = lignes_utiles(faits)
        for ligne in lignes_faits:
            bouche.graver_chaine(ligne, registre="fait")
            n_faits += 1
        pas("faits", f"{n_faits} chaînes gelées, registre fait, hors décharge")
    else:
        pas("faits", "aucun")
    ecrire_lignes(sortie / "03_faits.txt", "chaînes gelées", lignes_faits)

    n_episodes = 0
    lignes_epi: list[str] = []
    if episodes is not None:
        lignes_epi = lignes_utiles(episodes)
        for ligne in lignes_epi:
            bouche.apprendre_phrase_live(ligne, registre="episodique")
            n_episodes += 1
        pas("episodes", f"{n_episodes} phrases, une passe, contraste coupé, registre episodique")
    else:
        pas("episodes", "aucun")
    ecrire_lignes(sortie / "04_episodes.txt", "épisodes vifs", lignes_epi)

    n_retouches = 0
    lignes_ret: list[str] = []
    if retouches is not None:
        lignes_ret = lignes_utiles(retouches)
        ops = lire_retouches(retouches, registre)
        appliquer_retouches(bouche, ops)
        n_retouches = len(ops)
        pas("retouches", f"{n_retouches} cases, après le compte, registre par défaut {registre}")
    else:
        pas("retouches", "aucune")
    ecrire_lignes(sortie / "05_retouches.txt", "cases écrites après le compte", lignes_ret)

    # graver_chaine a pu laisser le registre courant sur « fait ».
    bouche.registre = registre

    tissu = None
    if cerveau and Path(cerveau).is_file():
        try:
            from ratiss_v3 import TissuScelle
            tissu = TissuScelle(str(cerveau))
            tissu.normaliser_degre = normaliser_degre
        except Exception:
            tissu = None

    mesures_modes = {}
    if lignes_ecart:
        texte_ecart = "\n".join(lignes_ecart)
        eval_modes = [
            ("theme", 1, None),
            ("ordre", 1, None),
            ("trigramme", 1, None),
            ("lumiere", memoire, None),
            ("mixte", memoire, None),
        ]
        if tissu is not None:
            eval_modes.append(("tissu", 1, tissu))
            eval_modes.append(("mixte_tissu", memoire, tissu))

        for mode, mem, t_inst in eval_modes:
            mode_eval = "mixte" if mode == "mixte_tissu" else mode
            ev = bouche.evaluer(texte_ecart, tissu=t_inst, mode=mode_eval, lam=lam, memoire=mem)
            mesures_modes[mode] = {
                "top5": ev["top5"],
                "hits": ev["hits"],
                "total": ev["total"],
                "details": ev["details"],
            }
        pas("top5", "écart seulement" + (" (avec tissu scellé normalisé)" if tissu else ", tissu non mélangé"))
    else:
        texte_ecart = ""
        pas("top5", "omis")

    audits = []
    if texte_ecart and audit_max > 0:
        for hist, vrai in positions_audit(texte_ecart, audit_max):
            exp = alleger(bouche.expliquer_generation(vrai, hist, tissu=tissu, lam=lam, memoire=memoire))
            audits.append(
                {
                    "hist": hist,
                    "vrai": vrai,
                    "formule_resolue": exp["resolution"]["formule_resolue"],
                    "identique_au_score": exp["identique_au_score"],
                    "mode_ordre": exp["ordre"]["mode"],
                    "explication": exp,
                }
            )
        pas("audit", f"{len(audits)} mots suivants, formule relue")
    else:
        pas("audit", "omis")

    h_apres = sha256_fichier(cerveau) if cerveau else None
    if h_avant is not None and h_avant != h_apres:
        raise RuntimeError("le fichier scellé a changé pendant l'entraînement")

    destination = sortie / "bouche.bouche"
    bouche.sauver(str(destination))
    mesures = {
        "methode": METHODE,
        "registre": registre,
        "tours": tours,
        "contraste": contraste,
        "lam": lam,
        "memoire": memoire,
        "education_lignes": len(lignes_edu),
        "ecart_lignes": len(lignes_ecart),
        "faits": n_faits,
        "episodes": n_episodes,
        "retouches": n_retouches,
        "arcs": bouche.n_arcs(),
        "trigrammes": bouche.n_trigrammes(),
        "chaines": len(bouche.chaines),
        "modes": {
            k: {"top5": v["top5"], "hits": v["hits"], "total": v["total"]}
            for k, v in mesures_modes.items()
        },
        "tissu": str(cerveau) if cerveau else None,
        "tissu_sha256": h_avant,
        "tissu_intact": h_avant == h_apres,
        "bouche": str(destination),
    }
    (sortie / "mesures.json").write_text(
        json.dumps(mesures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with (sortie / "audit.jsonl").open("w", encoding="utf-8") as f:
        for ligne in audits:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")

    organisation = [
        f"méthode {METHODE}",
        "ordre fixe : " + ", ".join(PAS),
        "",
        "ce dépôt :",
        f"  éducation comptée     {sortie / '01_education.txt'}",
        f"  écart, non compté     {sortie / '02_ecart.txt'}",
        f"  faits gelés           {sortie / '03_faits.txt'}",
        f"  épisodes, une passe   {sortie / '04_episodes.txt'}",
        f"  retouches O(1)        {sortie / '05_retouches.txt'}",
        f"  bouche                {destination}",
        f"  mesures               {sortie / 'mesures.json'}",
        f"  audit                 {sortie / 'audit.jsonl'}",
        "",
        "le .ratiss n'est pas dans ce dossier.",
        f"tissu intact : {mesures['tissu_intact']}",
        "",
        "pas exécutés :",
        *journal,
    ]
    (sortie / "ORGANISATION.txt").write_text("\n".join(organisation) + "\n", encoding="utf-8")
    pas("depot", str(destination))
    mesures["journal"] = journal
    return mesures


def _chemin(valeur: str | None) -> Path | None:
    if valeur is None:
        return None
    return Path(valeur)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Entraîner la langue Ratiss GI, dans l'ordre, sur CPU")
    p.add_argument("--education", required=True, help="prose à compter")
    p.add_argument("--sortie", required=True, help="dossier du berceau de langue")
    p.add_argument("--registre", default="conte")
    p.add_argument("--tours", type=int, default=3)
    p.add_argument("--sans-contraste", action="store_true")
    p.add_argument("--ecart", default=None, help="texte jamais donné à l'éducation")
    p.add_argument("--fraction", type=float, default=None, help="si --ecart est omis, queue du fichier")
    p.add_argument("--faits", default=None)
    p.add_argument("--episodes", default=None)
    p.add_argument("--retouches", default=None)
    p.add_argument("--charger", default=None)
    p.add_argument("--cerveau", default=None, help="seulement pour le hash. Le graphe n'est pas chargé")
    p.add_argument("--sans-normalisation-degre", action="store_true", help="désactiver la normalisation par ln(degre)")
    p.add_argument("--lam", type=float, default=0.75)
    p.add_argument("--memoire", type=int, default=8)
    p.add_argument("--audit", type=int, default=5)
    a = p.parse_args(argv)
    try:
        mesures = entrainer_langue(
            education=Path(a.education),
            sortie=Path(a.sortie),
            registre=a.registre,
            tours=a.tours,
            contraste=not a.sans_contraste,
            ecart=_chemin(a.ecart),
            fraction=a.fraction,
            faits=_chemin(a.faits),
            episodes=_chemin(a.episodes),
            retouches=_chemin(a.retouches),
            charger=_chemin(a.charger),
            cerveau=_chemin(a.cerveau),
            lam=a.lam,
            memoire=a.memoire,
            audit_max=a.audit,
            normaliser_degre=not a.sans_normalisation_degre,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"méthode {METHODE}")
    print(f"arcs {mesures['arcs']}  faits {mesures['faits']}  épisodes {mesures['episodes']}  retouches {mesures['retouches']}")
    for mode, ev in mesures["modes"].items():
        pct = 100.0 * ev["top5"]
        print(f"top-5 {mode:<12} {pct:5.1f} %   {ev['hits']}/{ev['total']}")
    if not mesures["modes"]:
        print("top-5 non publié : aucun écart")
    print(f"bouche : {mesures['bouche']}")
    if mesures["tissu"]:
        etat = "intact" if mesures["tissu_intact"] else "MODIFIÉ"
        print(f"tissu {etat}  {mesures['tissu_sha256']}")
    print(f"organisation : {Path(a.sortie) / 'ORGANISATION.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
