#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Les quatre piliers. Ce qui doit rester vrai, mesuré, pas raconté."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(RACINE))

from ratiss_v3 import Bouche, TissuScelle, parler
from piliers.resonance import raisonner_par_resonance


def _tissu_jouet(dossier: Path) -> tuple[TissuScelle, Path]:
    data = {
        "FORMAT": "RATISS_SOUVERAIN_V2",
        "META": {"NOM_MODELE": "jouet-piliers"},
        "SANCTUAIRE": {},
        "MEMOIRE_EPISODIQUE": {},
        "RNI_MATRICE": {
            "neurones": {
                "word_chat": 50,
                "word_chien": 50,
                "word_dort": 50,
                "word_joue": 50,
                "word_nuit": 50,
                "word_soleil": 50,
                "word_lune": 50,
                "word_maree": 50,
            },
            "liens": [
                ["word_chat", "word_dort", 10],
                ["word_chat", "word_nuit", 8],
                ["word_chien", "word_joue", 30],
                ["word_soleil", "word_lune", 12],
                ["word_maree", "word_lune", 12],
            ],
            "geles": [],
        },
    }
    chemin = dossier / "jouet.ratiss"
    chemin.write_text(json.dumps(data), encoding="utf-8")
    return TissuScelle(str(chemin)), chemin


class TestNeurochirurgie(unittest.TestCase):
    def test_editer_un_arc_ne_touche_pas_les_autres_faits(self):
        b = Bouche()
        b.eduquer("le chat dort\nle chien joue\n", tours=1, contraste=False, registre="ordre")
        chien_avant = dict(b.registres["ordre"]["chien"])
        scores_chien = b.scores(["chien"], lam=1.0)
        b.editer_synapse("chat", "dort", 42)
        self.assertEqual(b.registres["ordre"]["chat"]["dort"], 42.0)
        self.assertEqual(b.registres["ordre"]["chien"], chien_avant)
        self.assertEqual(b.scores(["chien"], lam=1.0), scores_chien)

    def test_supprimer_un_arc_laisse_le_reste_en_place(self):
        b = Bouche()
        b.eduquer("le chat dort\nle chien joue\n", tours=1, contraste=False)
        b.supprimer_synapse("chat", "dort")
        self.assertNotIn("dort", b.registres["ordre"].get("chat", {}))
        self.assertGreater(b.registres["ordre"]["chien"]["joue"], 0)

    def test_overlay_tissu_o1_sans_reconstruire_le_gel(self):
        with tempfile.TemporaryDirectory() as tmp:
            tissu, chemin = _tissu_jouet(Path(tmp))
            avant = hashlib.sha256(chemin.read_bytes()).hexdigest()
            liste_chat = id(tissu.adj["word_chat"])
            contenu = list(tissu.adj["word_chat"])
            n_liens = len(tissu.liens)
            chien_avant = tissu.scores_theme(["chien"], 1)
            tissu.editer_synapse("chat", "dort", 99)
            self.assertEqual(id(tissu.adj["word_chat"]), liste_chat)
            self.assertEqual(list(tissu.adj["word_chat"]), contenu)
            self.assertEqual(len(tissu.liens), n_liens)
            self.assertEqual(tissu.scores_theme(["chien"], 1), chien_avant)
            self.assertEqual(tissu.scores_theme(["chat"], 1)["dort"], 99.0)
            self.assertEqual(tissu.scores_theme(["chat"], 1)["nuit"], 8.0)
            # L'autre sens du lien gelé n'a pas bougé : l'overlay est dirigé.
            self.assertEqual(tissu.scores_theme(["dort"], 1)["chat"], 10.0)
            tissu.supprimer_synapse("chat", "nuit")
            self.assertNotIn("nuit", tissu.scores_theme(["chat"], 1))
            self.assertEqual(tissu.scores_theme(["chien"], 1)["joue"], 30.0)
            delta = tissu.exporter_delta()
            tissu2 = TissuScelle(str(chemin))
            self.assertEqual(tissu2.scores_theme(["chat"], 1)["dort"], 10.0)
            tissu2.appliquer_delta(delta)
            self.assertEqual(tissu2.scores_theme(["chat"], 1)["dort"], 99.0)
            self.assertNotIn("nuit", tissu2.scores_theme(["chat"], 1))
            apres = hashlib.sha256(chemin.read_bytes()).hexdigest()
            self.assertEqual(avant, apres)


class TestAudit(unittest.TestCase):
    def test_la_formule_est_le_score(self):
        b = Bouche()
        b.lam = 0.75
        b.eduquer(
            "la mer noire s etendait\nla nuit noire tombait\n",
            tours=1,
            contraste=False,
        )
        exp = b.expliquer_generation("s", ["la", "mer", "noire"])
        self.assertTrue(exp["identique_au_score"])
        self.assertEqual(exp["ordre"]["mode"], "trigramme")
        self.assertEqual(exp["ordre"]["poids_trigramme"], 0.65)
        self.assertAlmostEqual(exp["ordre"]["poids_bigramme"], 0.35)
        self.assertGreaterEqual(exp["ordre"]["trigramme"]["frequence_brute"], 1.0)
        self.assertGreaterEqual(exp["ordre"]["bigramme"]["frequence_brute"], 1.0)
        self.assertIn("Score = ", exp["resolution"]["formule_resolue"])
        self.assertAlmostEqual(
            exp["resolution"]["score"],
            b.scores(["la", "mer", "noire"], lam=0.75)["s"],
        )

    def test_repli_bigramme_quand_la_paire_est_inconnue(self):
        b = Bouche()
        b.eduquer("le chat dort\n", tours=1, contraste=False)
        exp = b.expliquer_generation("dort", "un chat")
        self.assertEqual(exp["ordre"]["mode"], "bigramme")
        self.assertFalse(exp["ordre"]["trigramme"]["vu"])
        self.assertEqual(exp["ordre"]["poids_bigramme"], 1.0)
        self.assertTrue(exp["identique_au_score"])

    def test_theme_tissu_dans_l_arbre(self):
        with tempfile.TemporaryDirectory() as tmp:
            tissu, _ = _tissu_jouet(Path(tmp))
            b = Bouche()
            b.lam = 0.0
            exp = b.expliquer_generation("dort", ["chat"], tissu=tissu, lam=0.0, memoire=1)
            self.assertTrue(exp["identique_au_score"])
            self.assertGreater(exp["theme"]["brut_tissu"], 0)
            noeuds = [a["noeud"] for a in exp["theme"]["activations"] if a["couche"] == "tissu"]
            self.assertIn("chat", noeuds)
            self.assertEqual(exp["theme"]["activations"][0]["distance"], 0)
            self.assertEqual(exp["theme"]["activations"][0]["lumiere"], 1.0)


class TestEpisodique(unittest.TestCase):
    def test_une_passe_suffit_a_continuer(self):
        b = Bouche()
        b.eduquer("le chat dort\n", tours=1, contraste=False)
        theme_chat = dict(b.theme.get("chat", {}))
        arcs_ordre = json.loads(json.dumps(b.registres["ordre"]))
        ep = b.apprendre_phrase_live("alpha beta gamma", registre="episodique")
        self.assertEqual(ep["decharges"], 0)
        self.assertEqual(ep["mots"], ["alpha", "beta", "gamma"])
        self.assertEqual(b.registres["ordre"], arcs_ordre)
        self.assertEqual(b.theme.get("chat", {}), theme_chat)
        suite = parler(b, "alpha beta", glouton=True, n=2, lam=1.0, memoire=1)
        self.assertEqual(suite.split()[0], "gamma")

    def test_episode_survit_a_la_sauvegarde(self):
        b = Bouche()
        b.apprendre_phrase_live("le soleil brille", registre="episodique")
        with tempfile.TemporaryDirectory() as tmp:
            chemin = str(Path(tmp) / "vive.json")
            b.sauver(chemin)
            relu = Bouche.charger(chemin)
        self.assertEqual(relu.episodique[0]["mots"], ["le", "soleil", "brille"])
        suite = parler(relu, "le soleil", glouton=True, n=1, lam=1.0, memoire=1)
        self.assertEqual(suite, "brille")


class TestResonance(unittest.TestCase):
    def test_soleil_et_maree_se_croisent_sur_la_lune(self):
        # Synapses causales. Aucune phrase d'explication n'est passée à l'algorithme.
        graphe = {
            "soleil": {"lune": 1.0, "chaleur": 1.0},
            "maree": {"lune": 1.0, "ocean": 1.0},
            "lune": {"nuit": 1.0},
            "chaleur": {},
            "ocean": {},
            "nuit": {},
        }
        res = raisonner_par_resonance(
            ["soleil", "maree"],
            seuil_energie=0.1,
            max_sauts=3,
            graphe=graphe,
        )
        self.assertEqual(res["carrefour"], "lune")
        self.assertAlmostEqual(res["energie"]["lune"], 1.0)
        self.assertAlmostEqual(res["energie"]["nuit"], 0.5)
        self.assertNotIn("chaleur", {c["noeud"] for c in res["carrefours"]})
        noms = [c["noeud"] for c in res["carrefours"]]
        self.assertEqual(noms[0], "lune")

    def test_gravite_emerge_si_les_deux_ondes_l_atteignent(self):
        graphe = {
            "soleil": {"lune": 1.0},
            "lune": {"gravite": 1.0},
            "maree": {"gravite": 1.0},
            "gravite": {},
        }
        res = raisonner_par_resonance(["soleil", "maree"], graphe=graphe)
        self.assertIn(res["carrefour"], {"lune", "gravite"})
        self.assertIn("gravite", res["energie"])
        self.assertGreaterEqual(res["energie"]["gravite"], 0.1)

    def test_tissu_jouet_sans_phrase(self):
        with tempfile.TemporaryDirectory() as tmp:
            tissu, _ = _tissu_jouet(Path(tmp))
            res = tissu.raisonner_par_resonance(["soleil", "maree"], seuil_energie=0.1, max_sauts=2)
        self.assertEqual(res["carrefour"], "lune")
        self.assertFalse(res["tronque"])

    def test_normalisation_degre_etouffe_les_hubs(self):
        # Un hub 'de' (50 liens) et une cible sémantique 'lune' (1 lien)
        graphe = {
            "soleil": {"lune": 10.0, "de": 10.0},
            "maree": {"lune": 10.0, "de": 10.0},
            "lune": {"nuit": 1.0},
            "de": {f"mot_{i}": 5.0 for i in range(50)},
        }
        res = raisonner_par_resonance(["soleil", "maree"], graphe=graphe, normaliser_degre=True)
        self.assertEqual(res["carrefour"], "lune")
        self.assertAlmostEqual(res["energie"]["lune"], 1.0)
        self.assertLess(res["energie"]["de"], 0.3)
        self.assertGreater(res["energie"]["lune"], res["energie"]["de"] * 3)


class TestLangageSimple(unittest.TestCase):
    def test_le_chat_mange(self):
        b = Bouche()
        b.eduquer(
            "le chat mange la souris\nla souris grignote le fromage\n",
            tours=1,
            contraste=False,
        )
        suite = parler(b, "le chat", glouton=True, n=3, lam=1.0, memoire=1)
        self.assertTrue(suite.startswith("mange"))

    def test_phrase_vive_puis_explication_du_mot(self):
        b = Bouche()
        b.apprendre_phrase_live("le soleil reveille la rose")
        suite = parler(b, "le soleil", glouton=True, n=3, lam=1.0, memoire=1)
        self.assertTrue(suite.startswith("reveille"))
        exp = b.expliquer_generation("reveille", "le soleil", lam=1.0)
        self.assertTrue(exp["identique_au_score"])
        self.assertGreater(exp["ordre"]["bigramme"]["frequence_brute"], 0)


if __name__ == "__main__":
    unittest.main()
