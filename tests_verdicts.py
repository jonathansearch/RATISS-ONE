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
