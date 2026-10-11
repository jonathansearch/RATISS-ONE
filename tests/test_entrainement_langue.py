#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La méthode langue. L'ordre, l'écart, l'épisode, la case. Pas une impression."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from ratiss_v3 import Bouche, parler
from entrainement.entrainer_langue import entrainer_langue, separer_queue


class TestOrganisation(unittest.TestCase):
    def test_la_queue_ne_entre_pas_dans_le_compte(self):
        lignes = [f"mot{i} suite{i}" for i in range(10)]
        edu, ecart = separer_queue(lignes, 0.2)
        self.assertEqual(len(ecart), 2)
        self.assertEqual(ecart, lignes[-2:])
        self.assertEqual(edu, lignes[:-2])

    def test_ecart_episode_retouche_et_sceau(self):
        with tempfile.TemporaryDirectory() as tmp:
            racine = Path(tmp)
            education = racine / "edu.txt"
            ecart = racine / "ecart.txt"
            faits = racine / "faits.txt"
            episodes = racine / "epi.txt"
            retouches = racine / "ret.txt"
            cerveau = racine / "sceau.ratiss"
            education.write_text(
                "# registre: conte\nle chat dort\nle chien joue\n",
                encoding="utf-8",
            )
            ecart.write_text("zzunique zzzuite\n", encoding="utf-8")
            faits.write_text("la lune orbite autour de la terre\n", encoding="utf-8")
            episodes.write_text("alpha beta gamma\n", encoding="utf-8")
            retouches.write_text("editer chat dort 42 conte\n", encoding="utf-8")
            cerveau.write_bytes(b"gel-qui-ne-doit-pas-changer")
            avant = hashlib.sha256(cerveau.read_bytes()).hexdigest()

            sortie = racine / "berceau"
            mesures = entrainer_langue(
                education=education,
                ecart=ecart,
                faits=faits,
                episodes=episodes,
                retouches=retouches,
                cerveau=cerveau,
                sortie=sortie,
                registre="conte",
                tours=2,
                contraste=True,
            )

            self.assertEqual(mesures["tissu_sha256"], avant)
            self.assertTrue(mesures["tissu_intact"])
            self.assertEqual(hashlib.sha256(cerveau.read_bytes()).hexdigest(), avant)
            self.assertEqual(mesures["faits"], 1)
            self.assertEqual(mesures["episodes"], 1)
            self.assertEqual(mesures["retouches"], 1)
            self.assertIn("zzunique", (sortie / "02_ecart.txt").read_text(encoding="utf-8"))
            self.assertNotIn("zzunique", (sortie / "01_education.txt").read_text(encoding="utf-8"))

            bouche = Bouche.charger(str(sortie / "bouche.bouche"))
            self.assertNotIn("zzunique", bouche.registres.get("conte", {}))
            self.assertNotIn("zzunique", bouche.registres.get("episodique", {}))
            self.assertEqual(bouche.registres["conte"]["chat"]["dort"], 42.0)
            self.assertGreater(bouche.registres["conte"]["chien"]["joue"], 0)
            self.assertNotEqual(bouche.registres["conte"]["chien"]["joue"], 42.0)
            self.assertTrue(bouche.chaines[0]["gele"])
            suite = parler(bouche, "alpha beta", glouton=True, n=1, lam=1.0, memoire=1)
            self.assertEqual(suite, "gamma")

            org = (sortie / "ORGANISATION.txt").read_text(encoding="utf-8")
            for nom in ("oreille", "separation", "prose", "faits", "episodes", "retouches", "top5", "audit", "depot"):
                self.assertIn(nom, org)
            audits = [
                json.loads(ln)
                for ln in (sortie / "audit.jsonl").read_text(encoding="utf-8").splitlines()
                if ln.strip()
            ]
            self.assertTrue(audits)
            self.assertTrue(all(a["identique_au_score"] for a in audits))
            self.assertIn("top5", json.loads((sortie / "mesures.json").read_text(encoding="utf-8"))["modes"]["trigramme"] or {})

    def test_fraction_ecrit_la_queue_a_part(self):
        with tempfile.TemporaryDirectory() as tmp:
            racine = Path(tmp)
            education = racine / "tout.txt"
            lignes = [f"ligne{i} suivante{i} encore{i}" for i in range(10)]
            education.write_text("\n".join(lignes) + "\n", encoding="utf-8")
            sortie = racine / "out"
            mesures = entrainer_langue(
                education=education,
                fraction=0.2,
                sortie=sortie,
                registre="ordre",
                tours=1,
                contraste=False,
            )
            self.assertEqual(mesures["education_lignes"], 8)
            self.assertEqual(mesures["ecart_lignes"], 2)
            bouche = Bouche.charger(str(sortie / "bouche.bouche"))
            self.assertNotIn("ligne8", bouche.registres.get("ordre", {}))
            self.assertIn("ligne0", bouche.registres.get("ordre", {}))

    def test_jouet_du_depot_sans_ouvrir_le_tissu(self):
        with tempfile.TemporaryDirectory() as tmp:
            berceau = Path(tmp) / "langue_jouet"
            mesures = entrainer_langue(
                education=RACINE / "corpus" / "prince_jouet.txt",
                ecart=RACINE / "corpus" / "tenu_a_lecart.txt",
                faits=RACINE / "corpus" / "faits_jouet.txt",
                episodes=RACINE / "corpus" / "episodes_jouet.txt",
                retouches=RACINE / "corpus" / "retouches_jouet.txt",
                sortie=berceau,
                registre="conte",
                tours=3,
                contraste=True,
                cerveau=None,
            )
            bouche = Bouche.charger(str(berceau / "bouche.bouche"))
            self.assertEqual(bouche.registres["conte"]["globe"]["verre"], 5.0)
            suite = parler(bouche, "le soleil", glouton=True, n=2, lam=1.0, memoire=1)
            self.assertTrue(suite.startswith("reveille"))
        self.assertGreater(mesures["modes"]["trigramme"]["total"], 0)
        self.assertGreater(mesures["arcs"], 0)
        self.assertEqual(mesures["episodes"], 2)
        self.assertEqual(mesures["faits"], 3)
        self.assertEqual(mesures["retouches"], 1)
        self.assertIsNone(mesures["tissu"])


    def test_entrainement_avec_tissu_reel_et_normalisation(self):
        with tempfile.TemporaryDirectory() as tmp:
            berceau = Path(tmp) / "langue_avec_tissu"
            cerveau = RACINE / "cerveau" / "RatissOne.ratiss"
            if not cerveau.exists():
                return
            mesures = entrainer_langue(
                education=RACINE / "corpus" / "prince_jouet.txt",
                ecart=RACINE / "corpus" / "tenu_a_lecart.txt",
                sortie=berceau,
                registre="conte",
                tours=1,
                contraste=False,
                cerveau=cerveau,
                normaliser_degre=True,
            )
            self.assertTrue(mesures["tissu_intact"])
            self.assertIn("mixte_tissu", mesures["modes"])
            self.assertIn("tissu", mesures["modes"])
            # Vérification du fichier de mesures
            data = json.loads((berceau / "mesures.json").read_text(encoding="utf-8"))
            self.assertIn("mixte_tissu", data["modes"])
            self.assertTrue(data["tissu_intact"])


if __name__ == "__main__":
    unittest.main()
