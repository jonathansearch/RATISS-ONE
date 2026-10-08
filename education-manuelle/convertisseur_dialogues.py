#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L'ÉCOLE MANUELLE — convertisseur dialogues -> CISE sur mesure (leçon 38).
RATISS Labs · MIT.

Prend des dialogues BRUTS (tours de parole, zéro annotation : pas de lemmes,
ni natures, ni traits) et les convertit en fragment CISE : paires de mots
qui SE SUIVENT (MSUITE, dans un tour) ou SE RÉPONDENT (MREPONSE, d'un tour
à l'autre quand le locuteur change). Même moteur que convertisseur_ud
(injecter, Cerveau, figer) : seul l'extracteur change.

Format lu : auto-détecté par fichier. (v1, style Accueil_UBS) : lignes
"X: texte" (X = une lettre, le locuteur), le reste ignoré. (v2, style
Ding) : tours "NNNN L texte" (numéro, locuteur, texte sur la même ligne),
suivis de lignes sans lettres (horaires, pauses) ignorées ; une ligne
avec des lettres sous un tour = suite du tour. (v3, phrases CEFR) : CSV
sentence,difficulty : chaque phrase = 1 dialogue à 1 tour (pas de paire
entre phrases, ce ne sont pas des dialogues) ; difficulty A1..C2 = motif
de niveau MA1..MC2 (les mots du fragment vus à ce niveau) ; on boit
train+val+test (pas d'évaluation externe, le tissu boit tout).
(v4, Q&R frenchQA, leçon 41) : parquet CATIE-AQ/frenchQA (question/answers)
: chaque exemple = 1 dialogue (tour Q puis tour R, locuteurs q/r, pas
de paire ENTRE exemples) ; on boit question + 1re réponse (les réponses
d'annotation [1:] ne sont pas des suites : comptées, ignorées) ; les
CONTEXTES (paragraphes encyclopédiques) et titres ne sont pas de la
conversation : comptés, ignorés ; test sans réponses = dialogues à Q
seule (comme CEFR : le tissu boit tout ce qui est buvable). Apostrophe
typographique ’ ramenée à ' (même coupure, pas de faux collé).
Limite connue (v3, assumée) : le t euphonique (a-t-il) donne (te,il)
par la règle des élisions — systématique, pas un bruit.
Fichiers *.txt, triés (+ *.parquet : lus en l'état, non triés).
Encodage : utf-8 essayé, repli latin-1 (les vieux corpus scolaires).

Règles du tokeniseur (simples, documentées, pinnées par la batterie) :
- groupes de lettres uniquement (chiffres et ponctuation tombent, les
  apostrophes et traits d'union COUPENT : "aujourd'hui" -> aujourd + hui).
- forme accentuée d'abord (tables de la leçon 34 : c.formes), sinon
  normalisation simple (minuscules, accents retirés).
- 1-lettre : seuls "a" (à/a) et "y" passent (comme la leçon 37).
- les ÉLISIONS se résolvent (qu→que, c→ce, d→de, j→je, m→me, n→ne,
  s→se, t→te : "qu'on" donne la paire (que,on), "c'est" donne (ce,est)) ;
  "l'" reste coupé (le ou la ? ambigu, on ne devine pas).
- les HÉSITATIONS ("e") et les BRUITS (liste ci-dessous, repérés à la
  main : morceaux de mots coupés, coquilles du transcripteur, bruits
  de bouche, intrusions anglaises, inaudibles "xxx") ne sont pas appris
  ET coupent le tour : pas de paire à travers (pas de faux voisins).
- les [crochets] décrivent des bruits ([rire], [micro], [pron ...]) :
  on jette le contenu, ce n'est pas de la parole.
- dans les (parenthèses), les morceaux coupés (tiret au bord : interrup-,
  -oilà) tombent, mais les chevauchements (vraie parole à deux voix :
  (c'est moi), (bien joué)) se gardent.
- "xxx" est décollé avant tout (toux(xxx) -> toux : le mot se garde).

Lois (mêmes que l'école UD) :
- force = min(100, 10 x rencontres) — la répétition prouve.
- le marbre ne se réécrit pas : lien existant = on ne touche pas.
- R5 : l'injection manuelle n'est pas une écoute (compteur inchangé).
- la bouche dialogue ne REMPLACE pas la bouche UD (setdefault : la
  grammaire garde la priorité, le dialogue n'apprend que le neuf).
- PAS d'école de grammaire ici : sans traits annotés, ni genres ni
  tables (l'école UD les porte déjà) — assumé, pas oublié.

Usage :
  python3 education-manuelle/convertisseur_dialogues.py --dialogues DIR
  python3 education-manuelle/convertisseur_dialogues.py --dialogues DIR --injecter cerveau/fige-300M-bases.json.gz --sortie cerveau/fige-300M-accueil.json.gz
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cerveau.cerveau import Cerveau, noeud_pour  # noqa: E402
from convertisseur_ud import injecter, normaliser_structure  # noqa: E402

LETTRES = re.compile(r"[a-zàâäéèêëîïôöùûüç]+")
TOUR = re.compile(r"^([a-zA-Z])\s*:\s*(.*)$")
DING = re.compile(r"^(\d+)\s+([a-zA-Z])\s+(.*)$")
CROCHETS = re.compile(r"\[[^\]]*\]")
PARENS = re.compile(r"\(([^)]*)\)")
HESITATIONS = {"e"}
MORCEAUX = {"qu"}
ELISIONS = {"qu": "que", "c": "ce", "d": "de", "j": "je", "m": "me",
            "n": "ne", "s": "se", "t": "te"}
BRUITS = {
    # morceaux de mots coupés (transcription orale, repérés à la main)
    "aujourd", "hui", "jusqu", "teleph", "automati", "entrepri", "remerc",
    "rmations", "scolar", "scora", "reun", "repro", "ouvir", "pelez", "rap",
    "rep", "pers", "ie", "int", "ite", "lle", "men", "mie", "iger", "idation",
    "oir", "oit", "utes", "pi", "pmo", "onne", "madam", "ernet", "quelqu",
    "voye",
    # coquilles du transcripteur
    "boujour", "rapeler",
    # bruits de bouche / marques
    "bb", "pf", "mps", "xx",
    # intrusions anglaises (corpus FR : on ne garde que le français)
    "beans", "cheese", "pronounce",
    # inclassables
    "ohannic", "tohannic",
    # inaudible (convention Ding)
    "xxx",
    # --- repérés à la main dans Ding (leçon 39) ---
    # morceaux de mots coupés
    "acc", "arg", "beso", "blede", "bles", "co", "deche", "defau", "dem",
    "echan", "inte", "pa", "pla", "poins", "poss", "pou", "rou", "secon",
    "squand", "tou", "tr", "troisi",
    # coquilles du transcripteur
    "construre", "developemments", "jai", "pinurie",
    # notations du transcripteur (pas de la parole)
    "pron", "inaudible",
    # anglais clair (le franglais d'usage — deal, timing, lol — reste)
    "damned", "done", "fair", "indeed", "loose", "next", "nope", "play",
    "safe", "unlock",
    # chant (pas de la parole) et variantes de claquements (on garde "tch")
    "tatalatata", "tchk", "tchoc", "tchu",
    # inclassables
    "disaenit", "mseugeu", "zouig",
    # --- repérés dans CEFR (leçon 40 : chasse systématique) ---
    # morceaux de mots coupés / fragments
    "ax", "bap", "cre", "ent", "fe", "fen", "fre", "fub", "fur", "ges",
    "her", "ide", "ja", "kyi", "ler", "lls", "lon", "lr", "moe", "mus",
    "ner", "omb", "ome", "ore", "ota", "piu", "puf", "rey", "ri", "ros",
    "suu", "tat", "tre", "tun", "upa", "ves", "vge", "vog", "yom", "zaw",
    "tions", "iredu", "insouci", "ducation", "barbo", "npi",
    # suffixes ordinaux sans leur nombre (1er, 2ème : chiffres tombés)
    "er", "eme",
    # mots collés (espace manquante dans le jeu)
    "aimerla", "appellecahier", "assurela", "vanitecomme",
    "impertinentepropose", "dansces", "dansles", "quelquechose",
    "roledans", "sonlangage", "trouverune", "amourpropre", "compterdu",
    "lepeu", "parla", "actionet",
    # coquilles du jeu (fautes de frappe)
    "beacoup", "bbonne", "acccepte", "attteint", "chaufffeur",
    "communce", "conta", "motle", "oublique", "perde", "reporterre",
    "sinema", "suporte", "viter",
    # anglais clair ("tm" : marque déposée, notation pas parole)
    "it", "may", "nil", "put", "sit", "tm", "morning", "uploading",
    # onomatopée improvisée + URL
    "cracracracracraaa", "wwwmonprospectuscom",
    # --- repérés dans frenchQA (leçon 41 : courts + longs + triples +
    # collés rares + échantillon 200 ; règle : sigles/noms propres gardés,
    # intrusions étrangères et corruptions MT jetées) ---
    # anglais clair (courts + verbes + noms communs)
    "buy", "cry", "dry", "egg", "eat", "eye", "fly", "fog", "foo", "law",
    "low", "odd", "own", "saw", "she", "ten", "two", "way", "why",
    "writing", "written", "without", "yourself", "against", "another",
    "airport", "airborne", "airbourne", "airtrain", "backwoods",
    "warehouse", "welfare", "wildlife", "yardage", "fellowship", "flight",
    "governor", "lifesize", "month", "settle", "sheer", "straits",
    "wilderness", "faithful", "neuropsychopharmacology",
    "polytetrafluoroethylene",
    # notations techniques (extensions, fichiers)
    "mov", "txt", "zip",
    # intrusions étrangères (DE/NL/ES : même logique que l'anglais)
    "bundesverfassungsgericht", "polizeigeschichtliche",
    "reichssicherheitshauptamt", "verfassungsgerichtshof", "frankreich",
    "madchenschule", "stube", "skiinternat", "boomhuis", "rotterdamse",
    # collés avérés (jamais écrits soudés en français)
    "intercontinentalexchange", "secretprojectrevolution", "emmanuelmacron",
    "famillecharles", "italieamanda", "meninblack", "avantagent",
    "provenancede",
    # coquilles et corruptions MT
    "alfredssson", "barrret", "commment", "deviennnent", "oppposant",
    "personnnes", "recommmande", "tttites", "villle", "gossameres",
    "resonnable", "characteristiques", "differenciables", "momotremes",
    "northuumbria", "orothdoxes", "sumitoma", "witesnake", "frocat",
    "noninitarien", "somalias", "tadjikiste",
    # ordinaux romains collés (suffixe sans nombre : précédent er/eme)
    "iiieme", "viiieme", "xviiieme", "xviiiieme",
    # romans XXX : contournent la règle xxx (majuscules) + nombres
    "xxxiv", "xxxviii",
    # notations (codepoint, transcripteur)
    "fffd", "www",
    # --- repérés dans PIAF (leçon 42 : 53 neufs relus UN PAR UN) ---
    # coquille humaine (question PIAF : "système giuvermental")
    "giuvermental",
    # span tronqué ("[V]ince, Lucifer..." : réponse coupée)
    "ince",
    # intrusions (NL : réponse de traduction ; DE : nom d'organisme)
    "neushoorn", "werbestelle",
    # fragment technique (Riccò : le ò italien est hors-classe LETTRES)
    "ricc",
}
UNE_LETTRE = {"a", "y"}
MOTIF_SUITE = "MSUITE"
MOTIF_REPONSE = "MREPONSE"


def lire_fichier(chemin):
    """Un fichier -> ([(locuteur, texte, niveau)], relie) (utf-8, latin-1).

    Format auto-détecté : CSV sentence,difficulty = phrases (relie=False,
    niveau A1..C2 ou None) ; une ligne "NNNN L ..." = Ding ; sinon "X: ..."
    = Accueil (relie=True, niveau None). En Ding, les lignes sans lettres
    (horaires, pauses) ne sont pas de la parole ; une ligne à lettres
    sous un tour = suite du tour.
    """
    import csv as _csv
    import io as _io
    brut = open(chemin, "rb").read()
    try:
        texte = brut.decode("utf-8")
    except UnicodeDecodeError:
        texte = brut.decode("latin-1")
    lignes = [l.strip().strip("\ufeff") for l in texte.splitlines()]
    if chemin.endswith(".parquet"):
        import pyarrow.parquet as _pq
        t = _pq.read_table(chemin)
        qs = t.column("question").to_pylist()
        rs = t.column("answers").to_pylist()
        blocs, multi, vides = [], 0, 0
        for q, r in zip(qs, rs):
            txts = [x for x in (r.get("text") or []) if x and x.strip()]
            if len(txts) > 1:
                multi += len(txts) - 1
            if not txts:
                vides += 1
            qtxt = (q or "").replace("’", "'")
            bloc = [("q", qtxt, None)]
            if txts:
                bloc.append(("r", txts[0].replace("’", "'"), None))
            blocs.append(bloc)
        lire_fichier.qa_stats = {"multiples_ignorees": multi, "sans_reponse": vides,
                                 "contextes_ignores": len(blocs)}
        return blocs, "qa"
    if lignes and "sentence" in lignes[0] and "difficulty" in lignes[0]:
        tours = []
        for r in _csv.DictReader(_io.StringIO(texte)):
            niv = (r.get("difficulty") or "").strip() or None
            if niv is not None and not re.fullmatch(r"[A-C][12]", niv):
                niv = None
            tours.append(("p", r.get("sentence") or "", niv))
        return tours, False
    if any(DING.match(l) for l in lignes):
        tours, courant = [], None
        for l in lignes:
            m = DING.match(l)
            if m:
                courant = [m.group(2).lower(), m.group(3)]
                tours.append(courant)
            elif courant is not None and l and LETTRES.search(l):
                courant[1] += " " + l
        return [(loc, txt, None) for loc, txt in tours], True
    tours = []
    for l in lignes:
        m = TOUR.match(l)
        if m:
            tours.append((m.group(1).lower(), m.group(2), None))
    return tours, True


def _nettoyer_parens(contenu):
    """Dans les parenthèses : les morceaux coupés (tiret au bord) tombent,
    les chevauchements (vraie parole) se gardent."""
    gardes = []
    for t in contenu.split():
        t2 = t.strip(".,!?;:")
        if t2.startswith("-") or t2.endswith("-"):
            continue
        gardes.append(t)
    return " ".join(gardes)


def tokeniser(texte, formes):
    """Un tour -> [segments] (un segment = [lemmes], coupé aux bruits)."""
    texte = texte.replace("xxx", " xxx ")  # xxx décollé MAIS reste une
    # coupure (toux(xxx) -> toux + coupure : pas de paire à travers)
    texte = CROCHETS.sub(" ", texte)
    texte = PARENS.sub(lambda m: _nettoyer_parens(m.group(1)), texte)
    segments, courant = [], []
    for morceau in LETTRES.findall(texte.lower()):
        if morceau in HESITATIONS or morceau in BRUITS:
            if courant:
                segments.append(courant)
                courant = []
            continue
        if morceau in ELISIONS:
            morceau = ELISIONS[morceau]
        if len(morceau) < 2 and morceau not in UNE_LETTRE:
            continue
        lemme = formes.get(morceau) or normaliser_structure(morceau)
        if not lemme:
            continue
        if lemme in BRUITS or lemme in HESITATIONS:
            # chassé aussi sous forme accentuée (blède -> blede) : coupure.
            if courant:
                segments.append(courant)
                courant = []
            continue
        courant.append(lemme)
    if courant:
        segments.append(courant)
    return segments


def extraire(chemin, formes=None):
    """Un dossier (ou fichier) de dialogues -> (arcs, stats).

    arcs : Counter (mot1, mot2, relation) ; relations = "suite" (mots
    voisins dans un segment) ou "reponse" (fin d'un tour -> début du
    suivant, locuteur changé) ; même locuteur de suite = "suite".
    Phrases (CSV) : 1 dialogue par phrase, pas de paire entre phrases.
    formes : dict forme -> lemme (celui du cerveau, ou {} = normalisé).
    stats["mots_niveau"] : niveau -> mots (pour les motifs MA1..MC2)."""
    from collections import Counter
    formes = formes or {}
    if os.path.isdir(chemin):
        fichiers = sorted(f for f in os.listdir(chemin) if f.endswith(".txt"))
        fichiers = [os.path.join(chemin, f) for f in fichiers]
        fichiers += sorted(os.path.join(dp, f) for dp, _, fs in os.walk(chemin)
                           for f in fs if f.endswith(".parquet"))
    else:
        fichiers = [chemin]
    arcs = Counter()
    mots_niveau = {}
    qa_multi = qa_vides = qa_ctx = 0
    dialogues, tours, mots = 0, 0, 0
    for f in fichiers:
        tours_f, relie = lire_fichier(f)
        if relie == "qa":
            st = lire_fichier.qa_stats
            qa_multi += st["multiples_ignorees"]
            qa_vides += st["sans_reponse"]
            qa_ctx += st["contextes_ignores"]
            blocs = tours_f
        else:
            blocs = [tours_f] if relie else [[t] for t in tours_f]
        for bloc in blocs:
            precedent = None  # (locuteur, dernier lemme)
            bu = False
            for loc, texte, niveau in bloc:
                segments = tokeniser(texte, formes)
                if not segments:
                    continue
                bu = True
                tours += 1
                plats = [w for s in segments for w in s]
                mots += len(plats)
                for seg in segments:
                    for x, y in zip(seg, seg[1:]):
                        arcs[(x, y, "suite")] += 1
                if precedent is not None and plats:
                    rel = "reponse" if loc != precedent[0] else "suite"
                    arcs[(precedent[1], plats[0], rel)] += 1
                if plats:
                    precedent = (loc, plats[-1])
                    if niveau:
                        mots_niveau.setdefault(niveau, set()).update(plats)
            if bu:
                dialogues += 1
    stats = {"dialogues": dialogues, "tours": tours, "mots": mots,
             "paires_uniques": len(arcs), "rencontres": sum(arcs.values()),
             "mots_niveau": {k: sorted(v)
                             for k, v in sorted(mots_niveau.items())}}
    if qa_ctx:
        stats["qa"] = {"multiples_ignorees": qa_multi, "sans_reponse": qa_vides,
                       "contextes_ignores": qa_ctx}
    return arcs, stats


def convertir(arcs, source, topk=0, niveaux=None):
    """Arcs -> fragment CISE (déterministe : trié partout).

    topk = 0 : TOUT (petits corpus) ; topk > 0 : topk paires par mot
    (gros corpus : le tissu reste petit, comme la leçon 30).
    niveaux : {niveau: [mots]} -> motifs MA1..MC2 (mots du fragment)."""
    if topk and topk > 0:
        par_mot = {}
        for (a, b, r), n in arcs.items():
            par_mot.setdefault(a, []).append((a, b, r, n))
            par_mot.setdefault(b, []).append((a, b, r, n))
        gardes = {}
        for m, lst in par_mot.items():
            lst.sort(key=lambda t: (-t[3], t[0], t[1], t[2]))
            for (a, b, r, n) in lst[:topk]:
                if (a, b) not in gardes or gardes[(a, b)][1] < n:
                    gardes[(a, b)] = (r, n)
    else:
        gardes = {}
        for (a, b, r), n in arcs.items():
            if (a, b) not in gardes or gardes[(a, b)][1] < n:
                gardes[(a, b)] = (r, n)
    liens, motifs = [], {MOTIF_SUITE: set(), MOTIF_REPONSE: set()}
    for (a, b) in sorted(gardes):
        r, n = gardes[(a, b)]
        liens.append({"a": a, "b": b, "force": min(100, 10 * n),
                      "n": n, "rel": r})
        motifs[MOTIF_REPONSE if r == "reponse" else MOTIF_SUITE].update((a, b))
    mots = sorted({w for l in liens for w in (l["a"], l["b"])})
    if niveaux:
        en_mots = set(mots)
        for niv in sorted(niveaux):
            gardes_niv = sorted(set(niveaux[niv]) & en_mots)
            if gardes_niv:
                motifs["M" + niv] = set(gardes_niv)
    return {
        "format": "fragment-cise-dialogues-v1",
        "source": source,
        "loi": "force = min(100, 10 x rencontres)",
        "mots_touches": mots,
        "neurones": mots,
        "liens": liens,
        "motifs": {k: sorted(v) for k, v in sorted(motifs.items()) if v},
        "stats": {"rencontres": sum(arcs.values()),
                  "paires_uniques": len(arcs),
                  "paires_gardees": len(liens),
                  "mots_touches": len(mots)},
    }


def ecole_oreille_dial(c, lemmes):
    """L'oreille apprend les mots du dialogue déjà en nerfs (idempotent)."""
    mots, sourds = 0, 0
    for lemme in sorted(lemmes):
        noeud = noeud_pour(c.graph["neurones"], lemme)
        if noeud is None:
            sourds += 1
            continue
        c.oreille[lemme] = [noeud]
        mots += 1
    return {"mots": mots, "sourds": sourds}


def ecole_bouche_dial(c, arcs):
    """La bouche apprend comment chaque lien tenu se parle : paire ->
    (relation la plus prouvée, second mot). setdefault : l'UD garde
    la priorité, le dialogue n'apprend que le neuf. Idempotent."""
    reserve = {}
    for (a, b, r), n in arcs.items():
        clef = tuple(sorted((a, b)))
        if clef not in reserve or reserve[clef][2] < n:
            reserve[clef] = (r, b, n)
    paires, sans_lien = 0, 0
    for (a, b), (r, dep, n) in sorted(reserve.items()):
        na = noeud_pour(c.graph["neurones"], a)
        nb = noeud_pour(c.graph["neurones"], b)
        paire = tuple(sorted((na, nb))) if na is not None and nb is not None else None
        if paire is None or paire not in c.graph["liens"]:
            sans_lien += 1
            continue
        c.constructions.setdefault(paire, (r, noeud_pour(c.graph["neurones"], dep)))
        paires += 1
    return {"paires": paires, "sans_lien": sans_lien}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dialogues", required=True)
    ap.add_argument("--fragment", default=None)
    ap.add_argument("--topk", type=int, default=0)
    ap.add_argument("--injecter", default=None, help="cerveau gravé à pousser")
    ap.add_argument("--sortie", default=None, help="cerveau poussé + figé, gravé ici")
    args = ap.parse_args(argv)
    c = Cerveau.relire(args.injecter) if args.injecter else None
    formes = c.formes if c is not None else {}
    arcs, stats = extraire(args.dialogues, formes)
    print(f"DIALOGUES — {stats['dialogues']} dialogues, {stats['tours']} tours, "
          f"{stats['mots']} mots, {stats['paires_uniques']} paires uniques, "
          f"{stats['rencontres']} rencontres")
    fragment = convertir(arcs, args.dialogues, args.topk, stats["mots_niveau"])
    print(f"FRAGMENT — {len(fragment['neurones'])} mots, {len(fragment['liens'])} liens, "
          f"{len(fragment['motifs'])} motifs")
    if args.fragment:
        with open(args.fragment, "w", encoding="utf-8") as fh:
            json.dump(fragment, fh, ensure_ascii=False, indent=1)
        print(f"FRAGMENT GRAVÉ — {args.fragment}")
    if args.injecter:
        assert args.sortie, "--sortie exigé avec --injecter"
        avant = (len(c.graph["neurones"]), len(c.graph["liens"]))
        stats_i = injecter(c, fragment)
        res = c.figer()
        st_bou = ecole_bouche_dial(c, arcs)
        st_or = ecole_oreille_dial(c, fragment["neurones"])
        c.graver(args.sortie)
        print(f"POUSSÉ — +{stats_i['neurones']} neurones, +{stats_i['liens']} liens, "
              f"+{stats_i['motifs']} motifs ({stats_i['marbre_epargne']} marbre épargné)")
        print(f"BOUCHE — {st_bou['paires']} paires parlables, {st_bou['sans_lien']} sans lien")
        print(f"OREILLE — {st_or['mots']} mots appris, {st_or['sourds']} sourds")
        print(f"CERVEAU — {avant[0]}->{len(c.graph['neurones'])} neurones, "
              f"{avant[1]}->{len(c.graph['liens'])} liens, {len(res['figes'])} figés, "
              f"écoutes {c.ecoutes} (R5 : intactes)")
        print(f"GRAVÉ — {args.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
