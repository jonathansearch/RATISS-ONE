#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ce qui doit rester vrai. Pas une impression."""

import hashlib
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

from ratiss_v3 import Bouche, TissuScelle, audit_tissu, executer, marcher_fige, parler


class TestBouche(unittest.TestCase):
    def test_les_deux_sens_ne_sont_pas_le_meme_arc(self):
        b = Bouche()
        b.eduquer("la mer noire\nla noire nuit", tours=1, contraste=False)
        arcs = b.registres["ordre"]
        self.assertGreater(arcs["mer"]["noire"], 0)
        self.assertGreater(arcs["noire"]["nuit"], 0)
        self.assertNotIn("mer", arcs.get("noire", {}))

    def test_trigramme_separe_mer_noire_de_nuit_noire(self):
        b = Bouche()
        b.eduquer(
            "la mer noire s etendait\nla nuit noire tombait\n",
            tours=1,
            contraste=False,
        )
        mer = max(b.scores_trigramme(["la", "mer", "noire"]).items(), key=lambda kv: kv[1])[0]
        nuit = max(b.scores_trigramme(["la", "nuit", "noire"]).items(), key=lambda kv: kv[1])[0]
        self.assertEqual(mer, "s")
        self.assertEqual(nuit, "tombait")
        # Le bigramme voit les deux suites et ne peut pas choisir pour la bonne raison.
        big = b.scores_ordre(["noire"], memoire=1)
        self.assertIn("s", big)
        self.assertIn("tombait", big)

    def test_gel_ne_boucle_pas_sur_la(self):
        mots = ["la", "lune", "orbite", "autour", "de", "la", "terre"]
        self.assertEqual(
            marcher_fige(mots, "lune"),
            ["lune", "orbite", "autour", "de", "la", "terre"],
        )

    def test_sanctuaire_ne_remplit_pas_les_synapses(self):
        chemin = RACINE / "cerveau" / "RatissOne.ratiss"
        if not chemin.is_file():
            self.skipTest("cerveau absent")
        b = Bouche()
        rep = executer("explique la fusion", b, TissuScelle(str(chemin)))["reponse"]
        self.assertIn("plasma", rep)
        self.assertTrue(b.vide())
        self.assertEqual(b.n_trigrammes(), 0)

    def test_bouche_vide_ne_fabrique_pas_un_gabarit(self):
        rep = executer("parle moi de la mer", Bouche(), None)["reponse"]
        self.assertIn("Bouche vide", rep)
        self.assertNotIn("principalement", rep)
        self.assertNotIn("en liaison", rep)

    def test_chaine_gelee_puis_empruntee(self):
        b = Bouche()
        executer("Apprends que la lune orbite autour de la terre", b, None)
        rep = executer("parle moi de la lune", b, None)["reponse"]
        self.assertIn("lune orbite", rep.lower())
        self.assertTrue(b.chaines[0]["gele"])

    def test_glouton_dit_quelques_mots_francais(self):
        texte = (RACINE / "corpus" / "prince_jouet.txt").read_text(encoding="utf-8")
        b = Bouche()
        b.eduquer(texte, tours=3, registre="conte")
        suite = parler(b, "un", glouton=True, n=12, lam=1.0, memoire=1)
        self.assertTrue(suite.startswith("jardin le petit prince"))

    def test_tissu_scelle_est_alphabetique_et_intact(self):
        chemin = RACINE / "cerveau" / "RatissOne.ratiss"
        if not chemin.is_file():
            self.skipTest("cerveau absent")
        avant = hashlib.sha256(chemin.read_bytes()).hexdigest()
        tissu = TissuScelle(str(chemin))
        audit = audit_tissu(tissu)
        self.assertEqual(audit["inverses"], 0)
        self.assertEqual(audit["neurones"], 95660)
        self.assertEqual(audit["liens"], 428471)
        self.assertLess(audit["top5"], 0.25)
        # « il » ne propose pas « etait ». Il propose l'alphabet.
        ligne_il = [l for l in audit["lignes"] if l[0] == "il"][0]
        self.assertNotIn("etait", ligne_il[2])
        self.assertIn("abattu", [l for l in audit["lignes"] if l[0] == "etait"][0][2])
        rep = executer("explique la fusion", Bouche(), tissu)["reponse"]
        self.assertIn("plasma", rep)
        apres = hashlib.sha256(chemin.read_bytes()).hexdigest()
        self.assertEqual(avant, apres)


if __name__ == "__main__":
    unittest.main()
