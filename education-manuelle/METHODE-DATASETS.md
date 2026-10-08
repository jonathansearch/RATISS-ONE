# MÉTHODE — boire un dataset (passerelle pour GLM)

Tu prends la suite. Tout est ici : les liens, l'état, la procédure exacte,
les lois, le reste à boire. Lis tout avant de toucher quoi que ce soit.

## 1. Les 2 dépôts

- LABO (système, cerveau, convertisseur, batterie, preuves) :
  https://github.com/jonathansearch/RATISS-ONE
- DONNÉES (catalogue, fiches, listes, échantillons) :
  https://github.com/jonathansearch/bases-donnees
- Catalogue détaillé (sources + commandes de clone) :
  `LISTE-RESTE.md` dans le dépôt données (+ `INDICE.md` = l'état).

## 2. L'état actuel (8 oct. 2026)

- Cerveau courant : `cerveau/fige-300M-narrativeqa.json.gz`
  (95660 neurones, 428471 liens, 36 motifs, écoutes 300000000).
  Toujours injecter dans le DERNIER cerveau, jamais un vieux.
- Batterie : 134/134 verts (`python3 -u tests_verdicts.py`, ~1 min).
- Convertisseur : `education-manuelle/convertisseur_dialogues.py`
  (formats : Accueil `X:`, Ding `NNNN L`, phrases CSV, parquets
  wildchat/frenchQA/piaf/fquad2, CSV narrativeqa `;` ; voir §4).
- Bus (8) : accueil-ubs (38), ding-01 (39), french_CEFR (40),
  frenchQA (41), piaf (42), fquad2 (43), wildchat-1m-fr (44),
  narrativeqa-fr (45). Prochaine leçon = 46, puis 47...
  (un dataset = une leçon).
- Espace : pas de plafond de ton côté (le 128 Mo, c'est seulement
  chez Ratiss, pas chez toi).

## 3. La procédure exacte (13 pas, dans l'ordre)

1. CHOISIR 1 dataset non bu (§6). UN SEUL complet à la fois, jamais 2.
2. CLONER dans `bases-donnees/francais/<nom>/brut/` (ou
   `conversations/<nom>/brut/`). Léger d'abord si possible.
3. INSPECTER le format : encodage (utf-8 ? latin-1 ?), tours,
   locuteurs, marqueurs (`[...]`, `(...)`, horodatages...). Regarder
   de vrais extraits, compter (fichiers/tours/mots).
4. ADAPTER le convertisseur si format nouveau (`lire_fichier` :
   auto-détection par fichier). Règles à documenter dans le docstring :
   ce qui se garde, ce qui se jette, pourquoi. Ne JAMAIS deviner.
5. DRY RUN (fragment seul, sans injecter) : chiffres cohérents ?
6. INJECTER : `--injecter cerveau/fige-300M-cefr.json.gz
   --sortie cerveau/fige-300M-<nom>.json.gz`
   (remplace `cefr` par le dernier cerveau du moment).
7. CHASSE AUX BRUITS (à la main, obligatoire) : lister les neurones
   neufs (script §5.3), juger UN PAR UN. On JETTE : morceaux coupés,
   coquilles, notations du transcripteur, mots collés, URLs, anglais
   clair, chant. On GARDE : tout ce qui est vraiment dit (oral,
   franglais d'usage, vulgarités attestées, noms propres, sigles).
   Ajouter à `BRUITS`, REJOUER jusqu'à AUCUN. Les bruits COUPENT
   (pas de paire à travers), les formes accentuées aussi.
8. BATTERIE : ajouter fixture (`education-manuelle/echantillon-<nom>.*`,
   ~5 tours, committée) + 1 contrôle (template §5.1 : pins fixture +
   pins artefact + rejoué +0 + R5 + `del` cerveaux contre les pics
   mémoire). Lancer : `python3 -u tests_verdicts.py` → TOUT VERT.
9. REJEU ×3 (script §5.2) : passages 2,3,4 → +0, 100 %, signature
   identique → réservoir vide PROUVÉ.
10. PREUVE : `preuves/dialogues-<nom>.txt` (sorties exactes, pas
    d'invention).
11. DOCS : `FICHE.json` (chiffres exacts + statut BU + licence) et
    ligne `INDICE.md` (dépôt données).
12. JETER le brut (`rm -rf brut/`) : on garde la TRACE (cerveau +
    fiche), jamais la donnée brute. Et ne JAMAIS commiter de brut
    (GitHub : 100 Mo/fichier max).
13. COMMIT + PUSH les 2 dépôts (message : `leçon 41 : <nom> bu ...`),
    puis RAPPORT au chef (français direct, emojis 🎉🔥💪, chiffres,
    honnêteté ; JAMAIS de proposition de suite : attendre son ordre).

## 4. Le convertisseur (ce qu'il fait)

- Lit des tours de parole (ou phrases) → paires de mots qui SE SUIVENT
  (MSUITE) ou SE RÉPONDENT (MREPONSE, locuteur changé) → fragment CISE
  → `injecter` (soudure, marbre respecté) → `figer` → bouche
  (setdefault : l'UD garde la priorité) + oreille (0 sourd attendu).
- force = min(100, 10 x rencontres). R5 : écoutes inchangées.
- Phrases isolées (CSV) : 1 dialogue par phrase, pas de paire entre
  phrases. Niveaux CEFR → motifs MA1..MC2.
- Élisions résolues : qu→que, c→ce, d→de, j→je, m→me, n→ne, s→se,
  t→te. "l'" coupé (ambigu). Chiffres tombés. JAMAIS commiter un
  fragment complet (éphémère) ; committer fixtures + cerveaux.

## 5. Code prêt à copier

### 5.1 Template contrôle batterie (à la suite des autres)

```python
    _ok_NOM = False
    try:
        try:
            del _cdc, _cef  # libère le contrôle précédent (pics mémoire)
        except NameError:
            pass
        _arcsn, _stn = _dx("education-manuelle/echantillon-NOM.EXT")
        _fn1 = _dc(_arcsn, "test", 0, _stn["mots_niveau"])
        _fn2 = _dc(_arcsc, "test", 0, _stc["mots_niveau"])
        _loin = all(l["force"] == min(100, 10 * l["n"]) for l in _fn1["liens"])
        with _ctx.redirect_stdout(_io.StringIO()):
            _cdn = _Cerveau("FR")
            _sin = _injecter(_cdn, _fn1)
            _si2n = _injecter(_cdn, _fn1)
            _rfn = _cdn.figer()
            _bon = _dbo(_cdn, _arcsn)
            _odn = _dor(_cdn, _fn1["neurones"])
            _nef = _Cerveau.relire("cerveau/fige-300M-NOM.json.gz")
        _ok_NOM = (_fn1 == _fn2 and _loin
                  and (_stn["dialogues"], _stn["tours"], _stn["mots"],
                       _stn["paires_uniques"]) == (D, T, M, P)
                  and (len(_fn1["neurones"]), len(_fn1["liens"]),
                       len(_fn1["motifs"])) == (N, L, MO)
                  and _fn1.get("format") == "fragment-cise-dialogues-v1"
                  and _cdn.ecoutes == 0 and _odn["sourds"] == 0
                  and _si2n["neurones"] == 0 and _si2n["liens"] == 0
                  and len(_rfn["figes"]) == len(_cdn.graph["neurones"])
                  and (len(_nef.graph["neurones"]), len(_nef.graph["liens"]),
                       len(_nef.motifs)) == (NN, LL, MM)
                  and _nef.ecoutes == 300000000
                  and (len(_nef.motifs["MSUITE"]), ...) == (...))
        try:
            del _cdn, _nef  # libère (pics mémoire)
        except NameError:
            pass
    except Exception:
        _ok_NOM = False
    if _ok_NOM:
        print("OK : NOM (...)")
    else:
        print("ÉCHEC : le convertisseur NOM est mauvais")
        echecs += 1
    controles += 1
```

(Remplace NOM, D/T/M/P, N/L/MO, NN/LL/MM par TES chiffres mesurés.)

### 5.2 Rejeu ×3 (après l'injection, brut encore présent)

```python
import sys, contextlib, io, hashlib, json
sys.path.insert(0, "education-manuelle")
from convertisseur_dialogues import extraire, convertir, ecole_oreille_dial, ecole_bouche_dial
from convertisseur_ud import injecter
from cerveau.cerveau import Cerveau

def signature(c):
    h = hashlib.sha256()
    h.update(json.dumps(sorted(c.graph["neurones"]), ensure_ascii=False).encode())
    h.update(json.dumps(sorted((list(k), v) for k, v in c.graph["liens"].items()), ensure_ascii=False).encode())
    h.update(json.dumps(sorted(c.motifs.items()), ensure_ascii=False).encode())
    return h.hexdigest()[:16]

with contextlib.redirect_stdout(io.StringIO()):
    c = Cerveau.relire("cerveau/fige-300M-NOM.json.gz")
    formes = dict(c.formes)
arcs, stats = extraire("BRUT", formes)
frag = convertir(arcs, "NOM", 0, stats["mots_niveau"])
sig0 = signature(c)
for p in (2, 3, 4):
    av_b, av_o = len(c.constructions), len(c.oreille)
    with contextlib.redirect_stdout(io.StringIO()):
        st = injecter(c, frag)
        c.figer()
        ecole_bouche_dial(c, arcs)
        ecole_oreille_dial(c, frag["neurones"])
    print("passage %d : +%d neurones +%d liens (épargné %d) | bouche +%d oreille +%d | écoutes %d" % (
        p, st["neurones"], st["liens"], st["marbre_epargne"],
        len(c.constructions) - av_b, len(c.oreille) - av_o, c.ecoutes))
print("signature avant/après : %s / %s" % (sig0, signature(c)))
```

(Attendu : +0 partout, signature identique.)

### 5.3 Lister les neurones neufs (chasse aux bruits)

```python
from cerveau.cerveau import Cerveau
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()):
    a = Cerveau.relire("cerveau/fige-300M-PRECEDENT.json.gz")
    c = Cerveau.relire("cerveau/fige-300M-NOM.json.gz")
neufs = sorted(set(c.graph["neurones"]) - set(a.graph["neurones"]))
mots = [n[5:] if n.startswith("word_") else n for n in neufs]
print(len(mots))
print(" ".join(mots))
```

### 5.4 Rituel git (chaque session : config perdue au restore)

```bash
git config user.email "ratiss-labs@example.com"
git config user.name "RATISS Labs"
git remote remove origin 2>/dev/null
git remote add origin "https://CLE@github.com/jonathansearch/NOM-DEPOT.git"
git add -A && git commit -m "message" && git push origin main
git remote set-url origin "https://github.com/jonathansearch/NOM-DEPOT.git"
```

(CLE = contenu de `~/.cles-ratiss/github`, chmod 600.
JAMAIS de clé dans un fichier, commit ou URL persistante.)

Environnement : `pip install huggingface_hub` à chaque session.

## 6. Données NON BUES (reste à entraîner)

| Donnée | Taille | Langue | Statut / format |
|---|---|---|---|
| iRead4Skills lexiques | 544 Ko | FR | listes de mots (pas de phrases !), Zenodo public ; dataset 1 🔒 restreint |
| CATIE-AQ | 100 petits | FR | prompts/QA, formats variés (1 par 1 !) |
| TCOF | ~200k mots | FR | ⚠️ page 404 : masse à retrouver |
| FLEURON | ? | FR | ⚠️ site 404 : masse à retrouver |
| CFDD / Claire | ~15 Go | FR | 🔒 401 HF : accès à débloquer |
| discord-dialogues | 331 Mo | EN | ⚠️ ANGLAIS : demander au chef d'abord |
| yield | 363 Mo | EN | ⚠️ ANGLAIS : demander au chef d'abord |
| ko-agent | 1,36 Go | EN | trajectoires + outils ; ANGLAIS |
| lmsys-chat-1m | 1,49 Go | EN | 🔒 gated + ANGLAIS |
| ultrachat-200k | 1,62 Go | EN | ANGLAIS |
| escorpius-dialog | 2,98 Go | ES | ESPAGNOL + 3 fichiers déshydratés (IDs seuls) |
| wildchat-1m | 3,36 Go | EN | ANGLAIS |
| Zagreus / Ilyana | — | — | MODÈLES : jamais (pas de LLM dans le système) |

⚠️ POINTS À TRANCHER PAR LE CHEF (pas par toi) : le cerveau est
FRANÇAIS — boire de l'ANGLAIS ou de l'ESPAGNOL ? CFDD 15 Go (accès +
poids) ? En cas de doute : rapport + attendre l'ordre.

## 7. Lois (non négociables)

- 1 dataset complet à la fois ; brut jeté après usage (la trace
  seule, jamais la donnée) ; jamais de brut commité (100 Mo/fichier).
- Marbre : lien existant = on ne touche pas. R5 : écoutes intactes.
- Batterie verte AVANT chaque push. Preuves = sorties réelles.
- Pas de LLM dans le système, jamais. Pas de maths imposées au chef.
- Secrets hors dépôt, toujours. Le chef tranche, on exécute.
- Rapports : français direct, emojis 🎉🔥💪, chiffres, honnêteté.
