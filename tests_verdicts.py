#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RATISS-ONE — vérification automatique des verdicts Ratum.
Règle R7 du labo : on ne croit pas, on rejoue ET on vérifie.

Usage : python3 tests_verdicts.py
Sortie 0 = tous les contrôles verts, 1 = écart détecté.
"""

import hashlib
import json
import os
import subprocess
import sys

# programme -> {code attendu, lignes attendues, lignes interdites}
CAS = {
    "rni-simple.ratum": {
        "code": 0,
        "attend": ["JUGEMENT ABC : TIENT", "JUGEMENT ETRANGER : ROMPT"],
    },
    "rni-complexe.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT SOLEIL : TIENT",
            "JUGEMENT LUNE : TIENT",
            "JUGEMENT ORAGE : ROMPT",
            "le premier souvenir a survécu",
            "le tissu ne rêve pas",
        ],
    },
    "rni-interference.ratum": {
        "code": 0,
        "attend": ["JUGEMENT SECOND : TIENT", "le nouveau a chassé l ancien"],
    },
    "jouets/j01-seuil.ratum": {
        "code": 0,
        "attend": ["JUGEMENT VIF : TIENT", "JUGEMENT DUR : ROMPT"],
    },
    "jouets/j02-pas.ratum": {
        "code": 0,
        "attend": ["JUGEMENT M : TIENT", "JUGEMENT M : ROMPT"],
    },
    "jouets/j03-oubli.ratum": {
        "code": 0,
        "attend": ["après la longue nuit : 0 sur 100", "rééduqué : 19 sur 100"],
    },
    "jouets/j04-graver-relire.ratum": {
        "code": 0,
        "attend": ["après relecture : 66 sur 100", "JUGEMENT M : TIENT"],
    },
    "jouets/j05-si-sinon.ratum": {
        "code": 0,
        "attend": [
            "branche alors : la forme apprise tient",
            "branche sinon : l inconnu est rejeté",
        ],
        "absent": ["ERREUR inattendue"],
    },
    "jouets/j06-motif-sans-liens.ratum": {
        "code": 0,
        "attend": ["JUGEMENT SEUL : ROMPT", "JUGEMENT PAIR : ROMPT"],
    },
    "jouets/j07-emboitement-plafond.ratum": {
        "code": 0,
        "attend": ["après 12 rencontres : 72 sur 100", "JUGEMENT M : ROMPT"],
    },
    "jouets/j08-repos.ratum": {
        "code": 0,
        "attend": ["après repos puis loi : 47 sur 100", "JUGEMENT M : ROMPT"],
    },
    "jouets/j09-propagation.ratum": {
        "code": 0,
        "attend": ["après une vague : 65 sur 100", "après deux vagues : 64 sur 100"],
    },
    "jouets/j10-erreur.ratum": {
        "code": 1,
        "attend": ["ERREUR RATUM"],
    },
    "english.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT MAMERICANS : TIENT",
            "JUGEMENT MASK : TIENT",
            "JUGEMENT MHOME : ROMPT",
            "JUGEMENT MCOMET : ROMPT",
            "the stranger stays outside",
            "the cousin is half guessed : 36 sur 100",
        ],
    },
    "porte-voix/ecoute.ratum": {
        "code": 0,
        "attend": [
            "le tissu comprend soleil",
            "le tissu comprend lune",
            "le tissu ne comprend pas comete",
            "mot hors vocabulaire : banane",
        ],
    },
    "jouets/j11-asymetrie.ratum": {
        "code": 0,
        "attend": ["JUGEMENT A : TIENT", "JUGEMENT B : TIENT"],
    },
    "jouets/j12-adapter.ratum": {
        "code": 0,
        "attend": ["après le calme : a=37 b=37"],
    },
    "v1-coexistence.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT A : ROMPT",
            "JUGEMENT A : TIENT",
            "JUGEMENT B : TIENT",
            "l asymétrie fait coexister",
        ],
    },
    "echelle/grand.ratum": {
        "code": 0,
        "attend": ["JUGEMENT C00 : TIENT", "JUGEMENT T09 : ROMPT", "=== fin du programme ==="],
        "absent": ["ERREUR"],
    },
    "vocabulaire.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT MSOLEIL : TIENT",
            "JUGEMENT MVENT : TIENT",
            "JUGEMENT MAURORE : ROMPT",
            "JUGEMENT MCOMETE : ROMPT",
            "l inconnu reste dehors",
            "le cousin est deviné à moitié : 35 sur 100",
        ],
    },
    "francais.ratum": {
        "code": 0,
        "attend": [
            "JUGEMENT MAMIS : TIENT",
            "JUGEMENT MPATRIE : TIENT",
            "JUGEMENT MUNIR : ROMPT",
            "JUGEMENT MAVENIR : ROMPT",
            "l etranger reste dehors",
            "le cousin est devine a moitie : 35 sur 100",
        ],
    },
    "education/vocabulaire50.ratum": {
        "code": 0,
        "attend": [
            "BILAN : 50 mots sur 50 tiennent (seuil 60)",
            "TEMOINS : 6 dehors sur 6 (seuil 20)",
        ],
    },
    "jouets/j13-sequences.ratum": {
        "code": 0,
        "attend": [
            "chaîne liée : a-b=52 b-c=52 d-e=44",
            "chaîne déliée : a-b=43 b-c=43 d-e=35",
        ],
    },
    "jouets/j14-cise.ratum": {
        "code": 0,
        "attend": [
            "étincelle : rien d'assez rapide",
            "trop tôt : a-b=40 c-d=0",
            "étincelle : a b figés, 1 filament",
            "cise : 2 neurones, 1 filament",
            "nettoyage : 1 liens morts, 2 neurones morts",
            "après 20 nuits : a-b=69!",
            "JUGEMENT M : TIENT",
        ],
    },
}


def reconstruire_ecoute():
    """Régénère ecoute.ratum via le pont (déterministe) avant les contrôles."""
    proc = subprocess.run(
        [sys.executable, "porte-voix/pont.py", "--texte", "soleil lune comete banane"],
        capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0


def regenerer_vocabulaire():
    """Régénère vocabulaire50.ratum via l'éducateur (déterministe) avant les contrôles."""
    proc = subprocess.run(
        [sys.executable, "education/eduquer.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0


def autotest_cerveau():
    """L'autotest du cerveau est déterministe et hors-ligne : un contrôle comme les autres."""
    proc = subprocess.run(
        [sys.executable, "cerveau/autotest.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    return proc.returncode == 0 and "CERVEAU OK" in proc.stdout


def main():
    echecs, controles = 0, 0
    controles += 1
    if reconstruire_ecoute():
        print("OK : pont voix régénéré (ecoute.ratum)")
    else:
        print("ÉCHEC : le pont voix ne tourne pas")
        return 1
    controles += 1
    if regenerer_vocabulaire():
        print("OK : vocabulaire régénéré (vocabulaire50.ratum)")
    else:
        print("ÉCHEC : l'éducateur ne tourne pas")
        return 1
    controles += 1
    if autotest_cerveau():
        print("OK : autotest du cerveau (secteurs + sanctuaire + chaînes)")
    else:
        print("ÉCHEC : l'autotest du cerveau ne passe pas")
        echecs += 1
    controles += 1
    proc_fr = subprocess.run(
        [sys.executable, "cerveau/autotest_fr.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_fr.returncode == 0 and "CERVEAU FR OK" in proc_fr.stdout:
        print("OK : autotest du cerveau FR (discours rejoué hors-ligne)")
    else:
        print("ÉCHEC : l'autotest du cerveau FR ne passe pas")
        echecs += 1
    controles += 1
    proc_bouche = subprocess.run(
        [sys.executable, "bouche/autotest_bouche.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_bouche.returncode == 0 and "BOUCHE OK" in proc_bouche.stdout:
        print("OK : autotest de la bouche (5 phrases exactes FR/EN)")
    else:
        print("ÉCHEC : l'autotest de la bouche ne passe pas")
        echecs += 1
    controles += 1
    proc_marbre = subprocess.run(
        [sys.executable, "cerveau/autotest_marbre.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_marbre.returncode == 0 and "MARBRE OK" in proc_marbre.stdout:
        print("OK : autotest du marbre (gravure + relief + rétroaction FR/EN)")
    else:
        print("ÉCHEC : l'autotest du marbre ne passe pas")
        echecs += 1
    controles += 1
    proc_maree = subprocess.run(
        [sys.executable, "cerveau/autotest_maree.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_maree.returncode == 0 and "MAREE OK" in proc_maree.stdout:
        print("OK : autotest de la marée (tampon + tempête + homéostasie)")
    else:
        print("ÉCHEC : l'autotest de la marée ne passe pas")
        echecs += 1
    controles += 1
    proc_chaos = subprocess.run(
        [sys.executable, "cerveau/autotest_chaos.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_chaos.returncode == 0 and "CHAOS OK" in proc_chaos.stdout:
        print("OK : autotest du chaos (oubli honnête + rêve + double dissociation)")
    else:
        print("ÉCHEC : l'autotest du chaos ne passe pas")
        echecs += 1
    controles += 1
    proc_livre = subprocess.run(
        [sys.executable, "livre/construire.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if (proc_livre.returncode == 0 and "LIVRE OK" in proc_livre.stdout
            and os.path.exists("livre/index.html")):
        print("OK : le livre se reconstruit (courbes + livre + présentation)")
    else:
        print("ÉCHEC : le livre ne se construit pas")
        echecs += 1
    controles += 1
    proc_conf = subprocess.run(
        [sys.executable, "route-d/conformite.py"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc_conf.returncode == 0 and "CONFORMITE OK" in proc_conf.stdout:
        print("OK : conformité C (24/24 sorties identiques + scroll)")
    else:
        print("ÉCHEC : le second berceau diverge du premier")
        echecs += 1
    controles += 1
    sys.path.insert(0, "pont-focal")
    from encodeur import (sha16, tissu_chaos, tissu_frais,  # noqa: E402
                          tissu_sanctuaire, tissu_vers_bits)
    etats = {"frais": tissu_frais(), "chaos": tissu_chaos(),
             "sanctuaire": tissu_sanctuaire()}
    bits = {nom: tissu_vers_bits(etat) for nom, etat in etats.items()}
    dores = {"frais": "e098de14fc25fbed", "chaos": "f29a73ec25dbdb98",
             "sanctuaire": "f555dd714bc1bf0b"}
    try:
        with open("preuves/sortie-pont-focal.txt", encoding="utf-8") as fh:
            preuve_pont = fh.read()
    except OSError:
        preuve_pont = ""
    if (all(tissu_vers_bits(etat) == bits[nom] for nom, etat in etats.items())
            and len(set(bits.values())) == 3
            and all(sha16(bits[n]) == d for n, d in dores.items())
            and "PONT FOCAL OK" in preuve_pont
            and all(d in preuve_pont for d in dores.values())
            and "P_sig = 6.3887" in preuve_pont
            and "P_sig = 6.3970" in preuve_pont
            and "P_sig = 6.2301" in preuve_pont):
        print("OK : pont FOCAL (3 tissus -> bits stables + preuve P_sig)")
    else:
        print("ÉCHEC : le pont FOCAL ne tient pas (régénérer la preuve ?)")
        echecs += 1
    controles += 1
    from cerveau.cerveau import MOTIFS_FIXES, MOTS, MOTS_FR  # noqa: E402
    canon_etiquettes = json.dumps(MOTIFS_FIXES, ensure_ascii=False).encode()
    sha_etiquettes = hashlib.sha256(canon_etiquettes).hexdigest()[:16]
    tables = {"EN": MOTS, "FR": MOTS_FR}
    if (sha_etiquettes == "3165ae68528bc9d4"
            and sum(len(m) for _, m in MOTIFS_FIXES) == 10
            and all(tables[lg][mot] == motif for lg, mots in MOTIFS_FIXES
                    for mot, motif in mots)):
        print("OK : 10 étiquettes gelées (5 EN + 5 FR, sha pinné)")
    else:
        print("ÉCHEC : le noyau des motifs a bougé")
        echecs += 1
    controles += 1
    sys.path.insert(0, "porte-voix")
    from direct import ecouter  # noqa: E402 — rejouable sans phonon
    tranches = json.load(open("porte-voix/tranches-jfk.json", encoding="utf-8"))
    finale_directe, lignes_directes = ecouter(
        [(t["t0"], t["mots"]) for t in tranches], silencieux=True)
    try:
        with open("preuves/sortie-oreille-direct.txt", encoding="utf-8") as fh:
            preuve_direct = fh.read()
    except OSError:
        preuve_direct = ""
    comptes_direct = [3, 4, 8, 13, 20, 21]
    if (len(lignes_directes) == 6
            and all(p.startswith(f"I heard {n} sequences.")
                    for (_, _, p), n in zip(lignes_directes, comptes_direct))
            and finale_directe == ("I heard 21 sequences. In the sanctuary: "
                                    "americans ask not. I hold americans, country, "
                                    "fellow and ask. The rest stays outside.")
            and "DIRECT OK" in preuve_direct
            and finale_directe in preuve_direct):
        print("OK : oreille en direct (6 tranches rejouées + élue retrouvée)")
    else:
        print("ÉCHEC : le direct ne se rejoue pas (régénérer la preuve ?)")
        echecs += 1
    controles += 1
    sys.path.insert(0, "dialogue")
    from conversation import CONVERSATIONS  # noqa: E402
    from dialogue import repondre  # noqa: E402
    from cerveau.cerveau import Cerveau as CerveauDialogue  # noqa: E402
    dores_dialogue = {
        "FR": ["Bonjour ! Moi c'est RATISS. Je t'écoute.",
               "Je suis RATISS-ONE, un tissu de neurones intriqués. Je tiens ce que je comprends.",
               "J'ai entendu 3 séquences. Je tiens amis, peuple, pays et patrie. Le reste reste dehors.",
               "J'ai entendu 5 séquences.",
               "Je ne comprends pas encore « merci beaucoup ». Apprends-moi des mots !",
               "Au revoir ! Le tissu garde ce qu'il a compris."],
        "EN": ["Hello! I am RATISS. I am listening.",
               "I am RATISS-ONE, a tissue of entangled neurons. I hold what I understand.",
               "I heard 4 sequences. I hold americans, country, fellow and ask. The rest stays outside.",
               "I heard 7 sequences.",
               "I do not understand « thanks a lot » yet. Teach me words!",
               "Goodbye! The tissue keeps what it understood."],
    }
    ok_dialogue = True
    for langue, questions in CONVERSATIONS.items():
        cerveau = CerveauDialogue(langue)
        for q, attendu in zip(questions, dores_dialogue[langue]):
            if repondre(cerveau, q)[2] != attendu:
                ok_dialogue = False
    try:
        with open("preuves/sortie-dialogue.txt", encoding="utf-8") as fh:
            preuve_dialogue = fh.read()
    except OSError:
        preuve_dialogue = ""
    if ok_dialogue and "DIALOGUE OK" in preuve_dialogue:
        print("OK : dialogue (12 répliques FR+EN + preuve)")
    else:
        print("ÉCHEC : le dialogue ne répond plus pareil")
        echecs += 1
    controles += 1
    sys.path.insert(0, "education-massive")
    from generer_masse import generer  # noqa: E402
    canon_masse = json.dumps(generer(2000, seed=7), ensure_ascii=False).encode()
    sha_masse = hashlib.sha256(canon_masse).hexdigest()[:16]
    if sha_masse == "cd1f94780dd2dd49":
        print("OK : générateur de masse déterministe (seed 7 pinné)")
    else:
        print("ÉCHEC : le générateur de masse a changé")
        echecs += 1
    controles += 1
    try:
        nb_lourd = json.load(open("colab-1h.ipynb", encoding="utf-8"))
        src_lourd = json.dumps(nb_lourd)
        ok_lourd = (len(nb_lourd["cells"]) == 8
                    and "epoques 3" in src_lourd
                    and "100000000" in src_lourd
                    and "11c17ba5948c4e6f5a486dad2014782bb9f6d70dfff714dd2c3d90d4738080ad" in src_lourd
                    and "--rapide --binaire --ram" in src_lourd
                    and "cerveau-fortifie.json.gz" in src_lourd
                    and "drive.mount" in src_lourd
                    and "--relais" in src_lourd)
    except (OSError, ValueError):
        ok_lourd = False
    if ok_lourd:
        print("OK : notebook puissance valide (8 cellules, sha 100M, 3 époques, graver)")
    else:
        print("ÉCHEC : le notebook puissance est cassé")
        echecs += 1
    controles += 1
    sys.path.insert(0, ".")
    import contextlib as _ctx
    import io as _io
    from cerveau.cerveau import Cerveau as _Cerveau
    from generer_masse import iterer as _iterer
    _c = _Cerveau("FR")
    _c.rapide = True
    with _ctx.redirect_stdout(_io.StringIO()):
        for _s in _iterer(1000, seed=7):
            _c.entendre_sequence(_s["mots"])
        _c.nuit()
    _h = hashlib.sha256(repr(sorted(_c.graph["liens"].items())).encode()).hexdigest()[:16]
    if _h == "305e8b21042704bb" and _c.ecoutes == 1000:
        print("OK : battement rapide pinné (1k seed 7 = 305e8b21042704bb)")
    else:
        print(f"ÉCHEC : le battement rapide a changé ({_h})")
        echecs += 1
    controles += 1
    import tempfile as _tf
    _tmp = _tf.mktemp(suffix=".json.gz")
    with _ctx.redirect_stdout(_io.StringIO()):
        _c.graver(_tmp)
        _r = _Cerveau.relire(_tmp)
    _same = (dict(_r.graph["liens"]) == dict(_c.graph["liens"])
             and _r.ecoutes == _c.ecoutes == 1000
             and [list(m) for m in _r.tampon] == [list(m) for m in _c.tampon])
    os.remove(_tmp)
    if _same:
        print("OK : graver/relire exact (1k seed 7, reprise parfaite)")
    else:
        print("ÉCHEC : le cerveau relu diffère")
        echecs += 1
    controles += 1
    _bin = _tf.mktemp(suffix=".bin")
    _rel = _tf.mktemp(suffix=".json.gz")
    subprocess.run([sys.executable, "education-massive/binaire_masse.py",
                    "--n", "2000", "--seed", "7", "--sortie", _bin],
                   capture_output=True, text=True, check=True)
    _p = subprocess.run(
        [sys.executable, "education-massive/eduquer_masse.py",
         "--entree", _bin, "--lot", "1000", "--rapide", "--binaire",
         "--relais", _rel],
        capture_output=True, text=True, encoding="utf-8")
    _ok_rel = False
    if _p.returncode == 0 and os.path.exists(_rel):
        with _ctx.redirect_stdout(_io.StringIO()):
            _rr = _Cerveau.relire(_rel)
        _ok_rel = (_rr.ecoutes == 2000 and len(_rr.graph["liens"]) > 0)
    os.remove(_bin)
    if os.path.exists(_rel):
        os.remove(_rel)
    if _ok_rel:
        print("OK : relais bout-en-bout (photo chaque lot, 2k relues)")
    else:
        print("ÉCHEC : le relais ne survit pas")
        echecs += 1
    controles += 1
    import zipfile as _zp
    _ok_ret, _top_ret = False, ""
    try:
        with _zp.ZipFile("cerveau/cerveau.zip") as _z:
            _noms = [n for n in _z.namelist() if n.startswith("fortifie-")]
            if len(_noms) == 1:
                _tmpf = _tf.mktemp(suffix=".json.gz")
                with open(_tmpf, "wb") as _fh:
                    _fh.write(_z.read(_noms[0]))
                with _ctx.redirect_stdout(_io.StringIO()):
                    _rf = _Cerveau.relire(_tmpf)
                os.remove(_tmpf)
                _tops = _rf.secteurs["SANCTUAIRE"].top(1)
                _top_ret = "+".join(_tops[0].mots) if _tops else ""
                _ok_ret = (_rf.ecoutes == 300000000 and _top_ret == "amis+patrie+pays")
    except Exception:
        _ok_ret = False
    if _ok_ret:
        print("OK : retour Colab (300M, sanctuaire amis+patrie+pays)")
    else:
        print(f"ÉCHEC : le cerveau revenu de Colab est mauvais ({_top_ret})")
        echecs += 1
    controles += 1
    _ok_fig = False
    try:
        with _zp.ZipFile("cerveau/cerveau.zip") as _z:
            _noms = [n for n in _z.namelist() if n.startswith("fortifie-")]
            _tmpf = _tf.mktemp(suffix=".json.gz")
            with open(_tmpf, "wb") as _fh:
                _fh.write(_z.read(_noms[0]))
            with _ctx.redirect_stdout(_io.StringIO()):
                _fc = _Cerveau.relire(_tmpf)
                _res = _fc.figer()
                _tmpg = _tf.mktemp(suffix=".json.gz")
                _fc.graver(_tmpg)
                _fr = _Cerveau.relire(_tmpg)
            os.remove(_tmpf)
            os.remove(_tmpg)
            _ok_fig = (len(_res["figes"]) == 13 and _res["filaments"] == 40
                       and _res["forces_intactes"]
                       and len(_fc.secteurs["ULTRA-SECTEUR"].top(10)) == 6
                       and set(_fr.graph["types"]) == set(_fc.graph["types"])
                       and set(_fr.graph["geles"]) == set(_fc.graph["geles"]))
    except Exception:
        _ok_fig = False
    if _ok_fig:
        print("OK : figement CISE (13 nerfs, 40 filaments, marbre reverrouillé)")
    else:
        print("ÉCHEC : le figement CISE est mauvais")
        echecs += 1
    controles += 1
    sys.path.insert(0, "education-manuelle")
    from convertisseur_ud import injecter as _injecter
    _ok_ec = False
    try:
        _frag = json.load(open("education-manuelle/fragment-ud-fr.json", encoding="utf-8"))
        _loi = all(l["force"] == min(100, 10 * l["n"]) for l in _frag["liens"])
        _n = (len(_frag["neurones"]), len(_frag["liens"]), len(_frag["motifs"]))
        with _ctx.redirect_stdout(_io.StringIO()):
            _ce = _Cerveau("FR")
            _st = _injecter(_ce, _frag)
            _re = _ce.figer()
        _ok_ec = (_frag.get("format") == "fragment-cise-ud-v1"
                  and _n == (238, 222, 12) and _loi
                  and _st["liens"] == 220 and _st["marbre_epargne"] == 2
                  and _st["motifs"] == 12
                  and len(_re["figes"]) == len(_ce.graph["neurones"])
                  and _ce.ecoutes == 0)
    except Exception:
        _ok_ec = False
    if _ok_ec:
        print("OK : école manuelle (fragment 238/222/12, loi vérifiée, tout figé)")
    else:
        print("ÉCHEC : le convertisseur UD est mauvais")
        echecs += 1
    controles += 1
    from convertisseur_dialogues import (extraire as _dx, convertir as _dc,
        ecole_oreille_dial as _dor, ecole_bouche_dial as _dbo)
    _ok_dial = False
    try:
        _arcs, _st = _dx("education-manuelle/echantillon-dialogues.txt")
        _f1 = _dc(_arcs, "test")
        _f2 = _dc(_arcs, "test")
        _loi = all(l["force"] == min(100, 10 * l["n"]) for l in _f1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cd = _Cerveau("FR")
            _si = _injecter(_cd, _f1)
            _si2 = _injecter(_cd, _f1)
            _rf = _cd.figer()
            _bo = _dbo(_cd, _arcs)
            _od = _dor(_cd, _f1["neurones"])
            _acc = _Cerveau.relire("cerveau/fige-300M-accueil.json.gz")
        _ok_dial = (_f1 == _f2 and _loi
                  and (_st["dialogues"], _st["tours"], _st["mots"],
                       _st["paires_uniques"]) == (1, 6, 34, 33)
                  and (len(_f1["neurones"]), len(_f1["liens"]),
                       len(_f1["motifs"])) == (30, 33, 2)
                  and _f1.get("format") == "fragment-cise-dialogues-v1"
                  and _cd.ecoutes == 0 and _od["sourds"] == 0
                  and _si2["neurones"] == 0 and _si2["liens"] == 0
                  and len(_rf["figes"]) == len(_cd.graph["neurones"])
                  and (len(_acc.graph["neurones"]), len(_acc.graph["liens"]),
                       len(_acc.motifs)) == (25272, 161454, 30)
                  and _acc.ecoutes == 300000000
                  and (len(_acc.motifs["MSUITE"]),
                       len(_acc.motifs["MREPONSE"])) == (592, 244))
    except Exception:
        _ok_dial = False
    if _ok_dial:
        print("OK : dialogues (fixture 1/6/34/33, accueil 25272/161454/30, rejoué +0, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur dialogues est mauvais")
        echecs += 1
    controles += 1
    _ok_ding = False
    try:
        try:
            del _cd, _acc  # libère le contrôle précédent (pics mémoire)
        except NameError:
            pass
        _arcsd, _std = _dx("education-manuelle/echantillon-ding.txt")
        _fd1 = _dc(_arcsd, "test")
        _fd2 = _dc(_arcsd, "test")
        _loid = all(l["force"] == min(100, 10 * l["n"]) for l in _fd1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cdd = _Cerveau("FR")
            _sid = _injecter(_cdd, _fd1)
            _si2d = _injecter(_cdd, _fd1)
            _rfd = _cdd.figer()
            _bod = _dbo(_cdd, _arcsd)
            _odd = _dor(_cdd, _fd1["neurones"])
            _din = _Cerveau.relire("cerveau/fige-300M-ding.json.gz")
        _ok_ding = (_fd1 == _fd2 and _loid
                  and (_std["dialogues"], _std["tours"], _std["mots"],
                       _std["paires_uniques"]) == (1, 5, 30, 25)
                  and (len(_fd1["neurones"]), len(_fd1["liens"]),
                       len(_fd1["motifs"])) == (22, 25, 2)
                  and _fd1.get("format") == "fragment-cise-dialogues-v1"
                  and _cdd.ecoutes == 0 and _odd["sourds"] == 0
                  and _si2d["neurones"] == 0 and _si2d["liens"] == 0
                  and len(_rfd["figes"]) == len(_cdd.graph["neurones"])
                  and (len(_din.graph["neurones"]), len(_din.graph["liens"]),
                       len(_din.motifs)) == (25803, 173556, 30)
                  and _din.ecoutes == 300000000
                  and (len(_din.motifs["MSUITE"]),
                       len(_din.motifs["MREPONSE"])) == (2053, 1035))
        try:
            del _cdd, _din  # libère (pics mémoire : les cerveaux s'accumulent)
        except NameError:
            pass
    except Exception:
        _ok_ding = False
    if _ok_ding:
        print("OK : ding (fixture 1/5/30/25, 25803/173556/30, rejoué +0, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur ding est mauvais")
        echecs += 1
    controles += 1
    _ok_cefr = False
    try:
        try:
            del _cdd, _din  # libère le contrôle précédent (pics mémoire)
        except NameError:
            pass
        _arcsc, _stc = _dx("education-manuelle/echantillon-cefr.csv")
        _fc1 = _dc(_arcsc, "test", 0, _stc["mots_niveau"])
        _fc2 = _dc(_arcsc, "test", 0, _stc["mots_niveau"])
        _loic = all(l["force"] == min(100, 10 * l["n"]) for l in _fc1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cdc = _Cerveau("FR")
            _sic = _injecter(_cdc, _fc1)
            _si2c = _injecter(_cdc, _fc1)
            _rfc = _cdc.figer()
            _boc = _dbo(_cdc, _arcsc)
            _odc = _dor(_cdc, _fc1["neurones"])
            _cef = _Cerveau.relire("cerveau/fige-300M-cefr.json.gz")
        _ok_cefr = (_fc1 == _fc2 and _loic
                  and (_stc["dialogues"], _stc["tours"], _stc["mots"],
                       _stc["paires_uniques"]) == (3, 3, 24, 21)
                  and (len(_fc1["neurones"]), len(_fc1["liens"]),
                       len(_fc1["motifs"])) == (24, 21, 3)
                  and _fc1.get("format") == "fragment-cise-dialogues-v1"
                  and _cdc.ecoutes == 0 and _odc["sourds"] == 0
                  and _si2c["neurones"] == 0 and _si2c["liens"] == 0
                  and len(_rfc["figes"]) == len(_cdc.graph["neurones"])
                  and (len(_cef.graph["neurones"]), len(_cef.graph["liens"]),
                       len(_cef.motifs)) == (31374, 211888, 36)
                  and _cef.ecoutes == 300000000
                  and (len(_cef.motifs["MSUITE"]),
                       len(_cef.motifs["MA1"]), len(_cef.motifs["MA2"]),
                       len(_cef.motifs["MB1"]), len(_cef.motifs["MB2"]),
                       len(_cef.motifs["MC1"]),
                       len(_cef.motifs["MC2"])) == (12789, 1061, 1505, 2245,
                       3753, 4675, 5827))
        try:
            del _cdc, _cef  # libère (pics mémoire)
        except NameError:
            pass
    except Exception:
        _ok_cefr = False
    if _ok_cefr:
        print("OK : cefr (fixture 3/3/24/21, 31374/211888/36, MA1..MC2, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur cefr est mauvais")
        echecs += 1
    controles += 1
    _ok_fqa = False
    try:
        _arcsq, _stq = _dx("education-manuelle/echantillon-frenchqa.parquet")
        _fq1 = _dc(_arcsq, "test")
        _fq2 = _dc(_arcsq, "test")
        _loiq = all(l["force"] == min(100, 10 * l["n"]) for l in _fq1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cdq = _Cerveau("FR")
            _siq = _injecter(_cdq, _fq1)
            _si2q = _injecter(_cdq, _fq1)
            _rfq = _cdq.figer()
            _boq = _dbo(_cdq, _arcsq)
            _odq = _dor(_cdq, _fq1["neurones"])
            _fqa = _Cerveau.relire("cerveau/fige-300M-frenchqa.json.gz")
        _ok_fqa = (_fq1 == _fq2 and _loiq
                  and (_stq["dialogues"], _stq["tours"], _stq["mots"],
                       _stq["paires_uniques"]) == (5, 9, 24, 19)
                  and _stq["qa"] == {"multiples_ignorees": 1,
                                     "sans_reponse": 1, "contextes_ignores": 5}
                  and (len(_fq1["neurones"]), len(_fq1["liens"]),
                       len(_fq1["motifs"])) == (22, 19, 2)
                  and _fq1.get("format") == "fragment-cise-dialogues-v1"
                  and _cdq.ecoutes == 0 and _odq["sourds"] == 0
                  and _si2q["neurones"] == 0 and _si2q["liens"] == 0
                  and len(_rfq["figes"]) == len(_cdq.graph["neurones"])
                  and (len(_fqa.graph["neurones"]), len(_fqa.graph["liens"]),
                       len(_fqa.motifs)) == (64277, 304561, 36)
                  and _fqa.ecoutes == 300000000
                  and (len(_fqa.motifs["MSUITE"]),
                       len(_fqa.motifs["MREPONSE"])) == (51156, 15418))
        try:
            del _cdq, _fqa  # libère (pics mémoire)
        except NameError:
            pass
    except Exception:
        _ok_fqa = False
    if _ok_fqa:
        print("OK : frenchqa (fixture 5/9/24/19, 64277/304561/36, Q&R, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur frenchqa est mauvais")
        echecs += 1
    controles += 1
    _ok_piaf = False
    try:
        _arcsp, _stp = _dx("education-manuelle/echantillon-piaf.parquet")
        _fp1 = _dc(_arcsp, "test")
        _fp2 = _dc(_arcsp, "test")
        _loip = all(l["force"] == min(100, 10 * l["n"]) for l in _fp1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cdp = _Cerveau("FR")
            _sip = _injecter(_cdp, _fp1)
            _si2p = _injecter(_cdp, _fp1)
            _rfp = _cdp.figer()
            _bop = _dbo(_cdp, _arcsp)
            _odp = _dor(_cdp, _fp1["neurones"])
            _piaf = _Cerveau.relire("cerveau/fige-300M-piaf.json.gz")
        _ok_piaf = (_fp1 == _fp2 and _loip
                  and (_stp["dialogues"], _stp["tours"], _stp["mots"],
                       _stp["paires_uniques"]) == (5, 10, 55, 46)
                  and _stp["qa"] == {"multiples_ignorees": 0,
                                     "sans_reponse": 0, "contextes_ignores": 5}
                  and (len(_fp1["neurones"]), len(_fp1["liens"]),
                       len(_fp1["motifs"])) == (45, 46, 2)
                  and _fp1.get("format") == "fragment-cise-dialogues-v1"
                  and _cdp.ecoutes == 0 and _odp["sourds"] == 0
                  and _si2p["neurones"] == 0 and _si2p["liens"] == 0
                  and len(_rfp["figes"]) == len(_cdp.graph["neurones"])
                  and (len(_piaf.graph["neurones"]), len(_piaf.graph["liens"]),
                       len(_piaf.motifs)) == (64325, 314097, 36)
                  and _piaf.ecoutes == 300000000
                  and (len(_piaf.motifs["MSUITE"]),
                       len(_piaf.motifs["MREPONSE"])) == (51219, 16334))
        try:
            del _cdp, _piaf  # libère (pics mémoire)
        except NameError:
            pass
    except Exception:
        _ok_piaf = False
    if _ok_piaf:
        print("OK : piaf (fixture 5/10/55/46, 64325/314097/36, Q&R natif, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur piaf est mauvais")
        echecs += 1
    controles += 1
    _ok_fq2 = False
    try:
        _arcs2, _st2 = _dx("education-manuelle/echantillon-fquad2.parquet")
        _f21 = _dc(_arcs2, "test")
        _f22 = _dc(_arcs2, "test")
        _loi2 = all(l["force"] == min(100, 10 * l["n"]) for l in _f21["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cd2 = _Cerveau("FR")
            _si2 = _injecter(_cd2, _f21)
            _si22 = _injecter(_cd2, _f21)
            _rf2 = _cd2.figer()
            _bo2 = _dbo(_cd2, _arcs2)
            _od2 = _dor(_cd2, _f21["neurones"])
            _fq2 = _Cerveau.relire("cerveau/fige-300M-fquad2.json.gz")
        _ok_fq2 = (_f21 == _f22 and _loi2
                  and (_st2["dialogues"], _st2["tours"], _st2["mots"],
                       _st2["paires_uniques"]) == (5, 8, 65, 59)
                  and _st2["qa"] == {"multiples_ignorees": 6,
                                     "sans_reponse": 2, "contextes_ignores": 5}
                  and (len(_f21["neurones"]), len(_f21["liens"]),
                       len(_f21["motifs"])) == (53, 59, 2)
                  and _f21.get("format") == "fragment-cise-dialogues-v1"
                  and _cd2.ecoutes == 0 and _od2["sourds"] == 0
                  and _si22["neurones"] == 0 and _si22["liens"] == 0
                  and len(_rf2["figes"]) == len(_cd2.graph["neurones"])
                  and (len(_fq2.graph["neurones"]), len(_fq2.graph["liens"]),
                       len(_fq2.motifs)) == (64539, 316963, 36)
                  and _fq2.ecoutes == 300000000
                  and (len(_fq2.motifs["MSUITE"]),
                       len(_fq2.motifs["MREPONSE"])) == (51466, 16570))
        try:
            del _cd2, _fq2  # libère (pics mémoire)
        except NameError:
            pass
    except Exception:
        _ok_fq2 = False
    if _ok_fq2:
        print("OK : fquad2 (fixture 5/8/65/59, 64539/316963/36, Q&R natif, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur fquad2 est mauvais")
        echecs += 1
    controles += 1
    _ok_wc = False
    try:
        _arcsw, _stw = _dx("education-manuelle/echantillon-wildchat.parquet")
        _arcst, _stt = _dx("education-manuelle/echantillon-wildchat.txt")
        _fw1 = _dc(_arcsw, "test")
        _fw2 = _dc(_arcsw, "test")
        _loiw = all(l["force"] == min(100, 10 * l["n"]) for l in _fw1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cdw = _Cerveau("FR")
            _siw = _injecter(_cdw, _fw1)
            _si2w = _injecter(_cdw, _fw1)
            _rfw = _cdw.figer()
            _bow = _dbo(_cdw, _arcsw)
            _odw = _dor(_cdw, _fw1["neurones"])
            _wc = _Cerveau.relire("cerveau/fige-300M-wildchat.json.gz")
        _ok_wc = (_fw1 == _fw2 and _loiw
                  and dict(_arcst) == dict(_arcsw) and _stt == _stw
                  and (_stw["dialogues"], _stw["tours"], _stw["mots"],
                       _stw["paires_uniques"]) == (5, 20, 4233, 2702)
                  and _stw["qa"] == {"multiples_ignorees": 0,
                                     "sans_reponse": 0, "contextes_ignores": 5}
                  and (len(_fw1["neurones"]), len(_fw1["liens"]),
                       len(_fw1["motifs"])) == (1003, 2702, 2)
                  and _fw1.get("format") == "fragment-cise-dialogues-v1"
                  and _cdw.ecoutes == 0 and _odw["sourds"] == 0
                  and _si2w["neurones"] == 0 and _si2w["liens"] == 0
                  and len(_rfw["figes"]) == len(_cdw.graph["neurones"])
                  and (len(_wc.graph["neurones"]), len(_wc.graph["liens"]),
                       len(_wc.motifs)) == (90666, 404043, 36)
                  and _wc.ecoutes == 300000000
                  and (len(_wc.motifs["MSUITE"]),
                       len(_wc.motifs["MREPONSE"])) == (79178, 16607))
        try:
            del _cdw, _wc  # libère (pics mémoire)
        except NameError:
            pass
    except Exception:
        _ok_wc = False
    if _ok_wc:
        print("OK : wildchat (fixture 5/20/4233/2702, 90666/404043/36, txt=parquet, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur wildchat est mauvais")
        echecs += 1
    controles += 1
    _ok_nq = False
    try:
        _arcsn, _stn = _dx("education-manuelle/echantillon-narrativeqa.csv")
        _fn1 = _dc(_arcsn, "test")
        _fn2 = _dc(_arcsn, "test")
        _loin = all(l["force"] == min(100, 10 * l["n"]) for l in _fn1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cdn = _Cerveau("FR")
            _sin = _injecter(_cdn, _fn1)
            _si2n = _injecter(_cdn, _fn1)
            _rfn = _cdn.figer()
            _bon = _dbo(_cdn, _arcsn)
            _odn = _dor(_cdn, _fn1["neurones"])
            _nq = _Cerveau.relire("cerveau/fige-300M-narrativeqa.json.gz")
        _ok_nq = (_fn1 == _fn2 and _loin
                  and (_stn["dialogues"], _stn["tours"], _stn["mots"],
                       _stn["paires_uniques"]) == (4163, 4168, 142654, 78356)
                  and _stn["qa"] == {"multiples_ignorees": 4,
                                     "sans_reponse": 0, "contextes_ignores": 3}
                  and (len(_fn1["neurones"]), len(_fn1["liens"]),
                       len(_fn1["motifs"])) == (17671, 78356, 2)
                  and _fn1.get("format") == "fragment-cise-dialogues-v1"
                  and _cdn.ecoutes == 0 and _odn["sourds"] == 0
                  and _si2n["neurones"] == 0 and _si2n["liens"] == 0
                  and len(_rfn["figes"]) == len(_cdn.graph["neurones"])
                  and (len(_nq.graph["neurones"]), len(_nq.graph["liens"]),
                       len(_nq.motifs)) == (95660, 428471, 36)
                  and _nq.ecoutes == 300000000
                  and (len(_nq.motifs["MSUITE"]),
                       len(_nq.motifs["MREPONSE"])) == (84491, 16607))
        try:
            del _cdn, _nq  # libère (pics mémoire)
        except NameError:
            pass
    except Exception:
        _ok_nq = False
    if _ok_nq:
        print("OK : narrativeqa (fixture 4163/4168/142654/78356, 95660/428471/36, livres n>=8, R5 OK)")
    else:
        print("ÉCHEC : le convertisseur narrativeqa est mauvais")
        echecs += 1
    controles += 1
    from convertisseur_ud import echantillonner as _ech, extraire as _ext
    _ok_rx = False
    try:
        _arcs, _rac = _ext("education-manuelle/echantillon-ud.conllu", None)
        _t1 = _ech(_arcs, _rac, 7, 30)
        _t2 = _ech(_arcs, _rac, 7, 30)
        _t3 = _ech(_arcs, _rac, 8, 30)
        _loi3 = all(l["force"] == min(100, 10 * l["n"])
                    for _t in (_t1, _t3) for l in _t["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cr = _Cerveau("FR")
            for _g in (7, 8, 9):
                _injecter(_cr, _ech(_arcs, _rac, _g, 30))
            _rr = _cr.figer()
            _rx = _Cerveau.relire("cerveau/fige-300M-remix100.json.gz")
        _ok_rx = (_t1["liens"] == _t2["liens"] and _t1["liens"] != _t3["liens"]
                  and _loi3 and _cr.ecoutes == 0
                  and len(_rr["figes"]) == len(_cr.graph["neurones"])
                  and (len(_rx.graph["neurones"]), len(_rx.graph["liens"]),
                       len(_rx.motifs)) == (15549, 39785, 19)
                  and _rx.ecoutes == 300000000
                  and len(_rx.graph["types"]) == 15549)
    except Exception:
        _ok_rx = False
    if _ok_rx:
        print("OK : remix (tours déterministes, 15549/39785/19 pinnés)")
    else:
        print("ÉCHEC : le remix est mauvais")
        echecs += 1
    controles += 1
    from convertisseur_ud import tout_boire as _boire
    _ok_fd = False
    try:
        class _A:
            pass
        with _ctx.redirect_stdout(_io.StringIO()):
            _vi = _tf.mktemp(suffix=".json.gz")
            _Cerveau("FR").graver(_vi)
            _outs = []
            for _g, _k in ((7, 500), (99, 700)):
                _a = _A()
                _a.conllu = "education-manuelle/echantillon-ud.conllu"
                _a.graines = _g
                _a.paires = _k
                _a.injecter = _vi
                _a.sortie = _tf.mktemp(suffix=".json.gz")
                _boire(_a)
                _outs.append(_Cerveau.relire(_a.sortie))
                os.remove(_a.sortie)
            os.remove(_vi)
            _fd = _Cerveau.relire("cerveau/fige-300M-tout.json.gz")
        _ok_fd = (dict(_outs[0].graph["liens"]) == dict(_outs[1].graph["liens"])
                  and dict(_outs[0].graph["neurones"]) == dict(_outs[1].graph["neurones"])
                  and _outs[0].motifs == _outs[1].motifs
                  and (len(_fd.graph["neurones"]), len(_fd.graph["liens"]),
                       len(_fd.motifs)) == (24639, 105349, 20)
                  and _fd.ecoutes == 300000000
                  and len(_fd.graph["types"]) == 24639)
    except Exception:
        _ok_fd = False
    if _ok_fd:
        print("OK : fond du verre (ordre indifférent, 24639/105349/20 pinnés)")
    else:
        print("ÉCHEC : le fond du verre est mauvais")
        echecs += 1
    controles += 1
    _ok_sd = False
    try:
        with _ctx.redirect_stdout(_io.StringIO()):
            _pre = _Cerveau.relire("cerveau/fige-300M-tout.json.gz")
            _pre._exec("rencontre MAMIS\npropager\n")
            _ch_pre = _pre.itp.tissu.neurones["word_ami"]["charge"]
            _post = _Cerveau.relire("cerveau/fige-300M-soude.json.gz")
            _post._exec("rencontre MAMIS\npropager\n")
            _ch_post = _post.itp.tissu.neurones["word_ami"]["charge"]
            _post.nuit()
        _pont = ("word_ami", "word_amis")
        _ok_sd = (_ch_pre == 0 and _ch_post == 50
                  and _post.graph["liens"].get(_pont) == 100
                  and _pont in _post.graph["geles"]
                  and (len(_post.graph["neurones"]), len(_post.graph["liens"]),
                       len(_post.motifs)) == (24639, 105350, 20)
                  and _post.ecoutes == 300000000
                  and len(_post.graph["types"]) == 24639
                  and all(_post.graph["liens"].get(k) == v
                          for k, v in _pre.graph["liens"].items()))
    except Exception:
        _ok_sd = False
    if _ok_sd:
        print("OK : soudure-amis (pont 100 figé, écho 0->50, 105350 liens)")
    else:
        print("ÉCHEC : la soudure est mauvaise")
        echecs += 1
    controles += 1
    from convertisseur_ud import ecole_oreille as _ecole
    _ok_or = False
    try:
        with _ctx.redirect_stdout(_io.StringIO()):
            _vi = _tf.mktemp(suffix=".json.gz")
            _Cerveau("FR").graver(_vi)
            _a = _A()
            _a.conllu = "education-manuelle/echantillon-ud.conllu"
            _a.graines = 7
            _a.paires = 500
            _a.injecter = _vi
            _a.sortie = _tf.mktemp(suffix=".json.gz")
            _boire(_a)
            os.remove(_vi)
            _seqs = [["amis", "aborder"], ["absides", "peuple"], ["blorpt"],
                     ["unir", "aborder", "aborder"]]
            _fx = []
            for _rap in (False, True):
                _x = _Cerveau.relire(_a.sortie)
                _st = _ecole(_x, "education-manuelle/echantillon-ud.conllu")
                _x.rapide = _rap
                for _s in _seqs:
                    _x.entendre_sequence(_s)
                _fx.append(_x)
            _xr = _Cerveau.relire(_a.sortie)
            _ecole(_xr, "education-manuelle/echantillon-ud.conllu")
            _xr.entendre_sequence(["abordable", "aborder"], interne=True)
            _xr.entendre_sequence(["abordable", "aborder"], interne=True)
            _reves = _xr.rever()
            os.remove(_a.sortie)
            _or = _Cerveau.relire("cerveau/fige-300M-oreille.json.gz")
            _sd = _Cerveau.relire("cerveau/fige-300M-soude.json.gz")
        _x0 = _fx[0]
        _nd = _x0.oreille["abordable"][0]
        _x0.graph["neurones"].pop(_nd)
        _ok_or = (_st == {"mots": 1423, "sourds": 142, "formes": 831}
                  and _x0.formes.get("amis") == "ami"
                  and _x0.formes.get("absides") == "abside"
                  and _x0._oreille(["amis"]) == (["amis"], [], ["word_amis"])
                  and dict(_fx[0].graph["liens"]) == dict(_fx[1].graph["liens"])
                  and _fx[0].chaines == _fx[1].chaines
                  and _reves == 1
                  and _x0._oreille(["abordable"])[1] == []
                  and (len(_or.graph["neurones"]), len(_or.graph["liens"]),
                       len(_or.motifs)) == (24639, 105350, 20)
                  and _or.ecoutes == 300000000
                  and len(_or.oreille) == 24638 and len(_or.formes) == 16370
                  and _or.formes.get("chevaux") == "cheval"
                  and "amis" not in _or.oreille
                  and dict(_or.graph["liens"]) == dict(_sd.graph["liens"])
                  and dict(_or.graph["neurones"]) == dict(_sd.graph["neurones"])
                  and _or.motifs == _sd.motifs)
    except Exception:
        _ok_or = False
    if _ok_or:
        print("OK : oreille (1423 mots, lent=rapide, 24638/16370 pinnés)")
    else:
        print("ÉCHEC : l'oreille est mauvaise")
        echecs += 1
    controles += 1
    from convertisseur_ud import ecole_bouche as _bouche
    from bouche.construire import construire as _construire, tenue as _tenue
    _ok_bou = False
    try:
        with _ctx.redirect_stdout(_io.StringIO()):
            _vi = _tf.mktemp(suffix=".json.gz")
            _Cerveau("FR").graver(_vi)
            _a = _A()
            _a.conllu = "education-manuelle/echantillon-ud.conllu"
            _a.graines = 7
            _a.paires = 500
            _a.injecter = _vi
            _a.sortie = _tf.mktemp(suffix=".json.gz")
            _boire(_a)
            os.remove(_vi)
            _x = _Cerveau.relire(_a.sortie)
            os.remove(_a.sortie)
            _ecole(_x, "education-manuelle/echantillon-ud.conllu")
            _stb = _bouche(_x, "education-manuelle/echantillon-ud.conllu")
            _ph10 = _construire(_x, "accuser", seuil=10)
            _cb = _Cerveau.relire("cerveau/fige-300M-bouche.json.gz")
            _ph = _cb.dire("dire")
            _phm = _cb.dire("manger")
            _or2 = _Cerveau.relire("cerveau/fige-300M-oreille.json.gz")
            _sd2 = _Cerveau.relire("cerveau/fige-300M-soude.json.gz")
        _ok_bou = (_stb == {"paires": 1750, "sans_lien": 0, "natures": 1423}
                   and _ph10 is not None and _ph10["phrase"] == "stephen accuser adeang"
                   and _tenue(_x, _ph10, seuil=10)
                   and _x.dire("aborder") is None
                   and _construire(_x, "blorpt", seuil=10) is None
                   and (len(_cb.graph["neurones"]), len(_cb.graph["liens"]),
                        len(_cb.motifs)) == (24639, 105350, 20)
                   and len(_cb.oreille) == 24638 and len(_cb.formes) == 16370
                   and len(_cb.constructions) == 105313 and len(_cb.natures) == 24638
                   and _cb.ecoutes == 300000000
                   and _ph is not None
                   and _ph["phrase"] == "empereur byzantin dire verite tout"
                   and _tenue(_cb, _ph)
                   and _phm is not None and _phm["phrase"] == "enfant autre pouvoir"
                   and _tenue(_cb, _phm)
                   and _cb.dire("blorpt") is None
                   and _or2.dire("dire") is None and _sd2.dire("manger") is None
                   and _sd2.dire("amis") is None)
    except Exception:
        _ok_bou = False
    if _ok_bou:
        print("OK : bouche (SVO tenu, empereur pinné, silences honnêtes)")
    else:
        print("ÉCHEC : la bouche est mauvaise")
        echecs += 1
    controles += 1
    from convertisseur_ud import ecole_grammaire as _gramm
    _ok_gr = False
    try:
        with _ctx.redirect_stdout(_io.StringIO()):
            _vi = _tf.mktemp(suffix=".json.gz")
            _Cerveau("FR").graver(_vi)
            _a = _A()
            _a.conllu = "education-manuelle/echantillon-ud.conllu"
            _a.graines = 7
            _a.paires = 500
            _a.injecter = _vi
            _a.sortie = _tf.mktemp(suffix=".json.gz")
            _boire(_a)
            os.remove(_vi)
            _x = _Cerveau.relire(_a.sortie)
            os.remove(_a.sortie)
            _ecole(_x, "education-manuelle/echantillon-ud.conllu")
            _bouche(_x, "education-manuelle/echantillon-ud.conllu")
            _stg = _gramm(_x, "education-manuelle/echantillon-ud.conllu")
            _pg10 = _x.parler("accuser", seuil=10)
            _cg = _Cerveau.relire("cerveau/fige-300M-grammaire.json.gz")
            _pg = _cg.parler("dire")
            _pg2 = _cg.parler("chien")
            _pg3 = _cg.parler("manger")
            _cb2 = _Cerveau.relire("cerveau/fige-300M-bouche.json.gz")
            _pb = _cb2.parler("dire")
            _or3 = _Cerveau.relire("cerveau/fige-300M-oreille.json.gz")
        _ok_gr = (_stg["articles"]["neurones"] == 19
                  and _stg["articles"]["liens"] == 628
                  and _stg["articles"]["epargnes"] == 1
                  and _stg["articles"]["figes"] == 1449
                  and (_stg["genres"], _stg["nombres"], _stg["flexions"],
                       _stg["adjectifs"], _stg["conjugue"], _stg["determinants"])
                  == (904, 1133, 910, 195, 102, 431)
                  and len(_x.motifs) == 22 and "MARTICLE" in _x.motifs  # leçon 37 : + MMARQUE (mark, les juxtaposées "que" nommées dès le fixture)
                  and "MMARQUE" in _x.motifs
                  and _pg10 is not None
                  and _pg10["phrase"] == "Stephen accuse Adeang."
                  and _pg10["appris"] is False and _pg10["tenu"] is True
                  and _construire(_x, "accuser", seuil=10)["phrase"] == "stephen accuser adeang"
                  and _x.parler("blorpt") is None
                  and (len(_cg.graph["neurones"]), len(_cg.graph["liens"]),
                       len(_cg.motifs)) == (24721, 119112, 21)
                  and _cg.ecoutes == 300000000
                  and len(_cg.oreille) == 24720 and len(_cg.formes) == 16406
                  and len(_cg.constructions) == 119075 and len(_cg.natures) == 24720
                  and (len(_cg.genres), len(_cg.nombres), len(_cg.flexions),
                       len(_cg.adjectifs), len(_cg.conjugue), len(_cg.determinants))
                  == (11953, 14536, 12727, 3175, 1119, 7725)
                  and _pg is not None
                  and _pg["phrase"] == "L'empereur byzantin dit la vérité toute."
                  and _pg["appris"] is True and _pg["tenu"] is True
                  and _pg2 is not None
                  and _pg2["phrase"] == "La population active élève les animaux domestiques."
                  and _pg2["appris"] is True
                  and (_cg.dire("chien") or {}).get("phrase") == "population actif elever animal domestique"
                  and _pg3 is not None
                  and _pg3["phrase"] == "Les enfants autres peuvent."
                  and _pg3["appris"] is True and _pg3["tenu"] is True
                  and _cg.parler("blorpt") is None
                  and _pb is not None
                  and _pb["phrase"] == "L'empereur byzantin dire le verite tout."
                  and _pb["appris"] is False and _pb["tenu"] is True
                  and _or3.parler("dire") is None)
    except Exception:
        _ok_gr = False
    if _ok_gr:
        print("OK : grammaire (articles + accords, empereur pinné, 119112 liens)")
    else:
        print("ÉCHEC : la grammaire est mauvaise")
        echecs += 1
    controles += 1
    from convertisseur_ud import ecole_bases as _bases
    _ok_ba = False
    try:
        try:
            del _cg, _cb2, _or3, _x  # la leçon 36 rend ses géants (RAM)
        except NameError:
            pass
        import gc as _gc
        _gc.collect()
        with _ctx.redirect_stdout(_io.StringIO()):
            _vi2 = _tf.mktemp(suffix=".json.gz")
            _Cerveau("FR").graver(_vi2)
            _a2 = _A()
            _a2.conllu = "education-manuelle/echantillon-ud.conllu"
            _a2.graines = 7
            _a2.paires = 500
            _a2.injecter = _vi2
            _a2.sortie = _tf.mktemp(suffix=".json.gz")
            _boire(_a2)
            os.remove(_vi2)
            _xb = _Cerveau.relire(_a2.sortie)
            os.remove(_a2.sortie)
            _ecole(_xb, "education-manuelle/echantillon-ud.conllu")
            _bouche(_xb, "education-manuelle/echantillon-ud.conllu")
            _gramm(_xb, "education-manuelle/echantillon-ud.conllu")
            _stb = _bases(_xb, "education-manuelle/echantillon-ud.conllu")
            _rb10 = _xb.raconter("accuser", seuil=10)
            _cb = _Cerveau.relire("cerveau/fige-300M-bases.json.gz")
            _r_man = _cb.raconter("manger")
            _r_pc = _cb.raconter("manger", temps="passe_compose")
            _r_neg = _cb.raconter("manger", temps="present", negatif=True)
            _r_vou = _cb.raconter("vouloir")
            _r_mer = _cb.raconter("mere")
            _r_ami = _cb.raconter("ami")
            _r_ps = _cb.raconter("prendre", temps="passe_simple")
            _r_fut = _cb.raconter("faire", temps="futur")
        _ok_ba = (_stb["structure"]["mots"] == 120
                  and _stb["structure"]["neurones"] == 79
                  and _stb["structure"]["liens"] == 1287
                  and _stb["structure"]["epargnes"] == 159
                  and _stb["structure"]["figes"] == 1528
                  and (_stb["participes"], _stb["auxiliaires"], _stb["places"],
                       _stb["personnes"], _stb["negations"]) == (110, 67, 164, 15, 10)
                  and len(_xb.motifs) == 28
                  and all(m in _xb.motifs for m in ("MPREPO", "MINDIRECT", "MAUX",
                       "METRE", "MEXPLETIF", "MNOMBRE", "MMARQUE"))
                  and _rb10 is not None
                  and _rb10["phrase"] == "Stephen accuse Adeang et les autres députés de l'opposition."
                  and _rb10["appris"] is False and _rb10["tenu"] is True
                  and _xb.raconter("blorpt") is None
                  and (len(_cb.graph["neurones"]), len(_cb.graph["liens"]),
                       len(_cb.motifs)) == (25171, 159288, 28)
                  and _cb.ecoutes == 300000000
                  and len(_cb.oreille) == 25152 and len(_cb.formes) == 16503
                  and len(_cb.constructions) == 159251 and len(_cb.natures) == 25152
                  and (len(_cb.genres), len(_cb.nombres), len(_cb.flexions),
                       len(_cb.adjectifs), len(_cb.conjugue), len(_cb.determinants),
                       len(_cb.participes), len(_cb.auxiliaires), len(_cb.places),
                       len(_cb.personnes), len(_cb.negations))
                  == (11996, 14593, 12753, 3183, 1240, 7813, 1452, 1202, 2760, 29, 346)
                  and _r_man is not None
                  and _r_man["phrase"] == "On mange bien."
                  and _r_man["appris"] is True and _r_man["tenu"] is True
                  and _r_pc is not None and _r_pc["phrase"] == "On a bien mangé."
                  and _r_pc["appris"] is True
                  and _r_neg is not None and _r_neg["phrase"] == "On ne mange jamais bien."
                  and _r_neg["appris"] is True
                  and _r_vou is not None and _r_vou["phrase"] == "Nous voulons vraiment dire."
                  and _r_vou["appris"] is True
                  and _r_mer is not None and _r_mer["phrase"] == "L'islam est religion."
                  and _r_mer["appris"] is True and _r_mer.get("attribut") == "word_religion"
                  and _r_ami is not None
                  and _r_ami["phrase"] == "La famille aisée de Colubridae et les meilleurs amis prétendent lui."
                  and _r_ami["appris"] is True
                  and _r_ps is not None
                  and _r_ps["phrase"] == "Les employés prirent lors le vrai nom de deux autres espèces dans la famille aisée de Colubridae en le compte."
                  and _r_fut is not None
                  and _r_fut["phrase"] == "On fera egalement la première apparition pour vous dans deux dernières années du calendrier proleptique."
                  and _cb.raconter("blorpt") is None
                  and _cb.raconter("devenir") is None
                  and _cb.raconter("manger", temps="passe") is None)
    except Exception:
        _ok_ba = False
    if _ok_ba:
        print("OK : bases (raconter 8 phrases, 28 motifs, 159288 liens)")
    else:
        print("ÉCHEC : les bases sont mauvaises")
        echecs += 1
    for prog, cas in CAS.items():
        proc = subprocess.run(
            [sys.executable, "ratum.py", prog],
            capture_output=True, text=True, encoding="utf-8",
        )
        sortie = proc.stdout
        print(f"--- {prog} (code {proc.returncode}, attendu {cas['code']}) ---")
        controles += 1
        if proc.returncode != cas["code"]:
            print(f"  ÉCHEC : code {proc.returncode} au lieu de {cas['code']}\n{sortie}")
            echecs += 1
            continue
        print("  OK : code de sortie")
        for attendue in cas.get("attend", []):
            controles += 1
            if attendue in sortie:
                print(f"  OK : « {attendue} »")
            else:
                print(f"  ÉCHEC : « {attendue} » introuvable")
                echecs += 1
        for interdite in cas.get("absent", []):
            controles += 1
            if interdite not in sortie:
                print(f"  OK : « {interdite} » absent")
            else:
                print(f"  ÉCHEC : « {interdite} » présent alors qu'interdit")
                echecs += 1
    try:
        os.remove("jouets/mem.scroll")
    except OSError:
        pass
    print(f"{controles - echecs}/{controles} CONTRÔLES VERTS")
    print("TOUS LES VERDICTS CONFORMES" if echecs == 0 else f"{echecs} ÉCART(S) DÉTECTÉ(S)")
    return 0 if echecs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
