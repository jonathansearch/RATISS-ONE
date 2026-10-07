#define _POSIX_C_SOURCE 200809L
/*
 * RATUM v2 — second berceau (C).
 * RATISS Labs · MIT.
 *
 * Portage fidèle de ratum.py (l'interprète de référence) : mêmes sorties
 * au caractère près sur les 24 programmes du corpus (voir conformite.py).
 * Périmètre et divergences documentées : route-d/LISEZ-MOI.md.
 *
 * Compilation : gcc -O2 -Wall -Wextra -o route-d/ratum-c route-d/ratum.c
 * Usage : ./route-d/ratum-c programme.ratum
 */
#include <ctype.h>
#include <errno.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Loi universelle (ratum.py) */
#define PAS_RENFORCER 10
#define PAS_DELIE 3
#define PAS_OUBLIER 3
#define SEUIL_DEFAUT 50
#define FORCE_NAISSANCE 10
#define VITESSE_CISE 10

static jmp_buf echec;
static char message_erreur[1024];

#define LEVER(noligne, ...) do { \
    snprintf(message_erreur, sizeof message_erreur, "ligne %d : ", noligne); \
    snprintf(message_erreur + strlen(message_erreur), \
             sizeof message_erreur - strlen(message_erreur), __VA_ARGS__); \
    longjmp(echec, 1); \
  } while (0)

static int borne(int n) {
  return n < 0 ? 0 : (n > 100 ? 100 : n);
}

/* ---------- structures ---------- */

typedef struct {
  char *nom;
  int seuil, charge, coups, cise;
} Neurone;

typedef struct {
  char *a, *b;   /* a <= b (strcmp), comme sorted((a, b)) */
  int force, gele;
  int ia, ib;    /* index neurones (re-résolus après nettoyer/relire) */
} Lien;

typedef struct {
  char *nom;
  char **membres;
  int *imembres;
  int nmb;
} Motif;

typedef struct {
  char *motif;
  char **figes;
  int nfig;
} Etincelle;

typedef struct {
  char *nom;
  Neurone *neurones;
  int nneur, capneur;
  Lien *liens;
  int nlien, caplien;
  Motif *motifs;
  int nmotif, capmotif;
  Etincelle *journal;
  int njourn, capjourn;
} Tissu;

static Tissu *T = NULL;  /* l'unique tissu du programme */

/* ---------- petits tableaux ---------- */

static void *grandir(void *p, int *cap, int n, int taille) {
  if (n >= *cap) {
    *cap = *cap ? *cap * 2 : 16;
    p = realloc(p, (size_t)*cap * (size_t)taille);
    if (!p) {
      fprintf(stderr, "mémoire épuisée\n");
      exit(2);
    }
  }
  return p;
}

static char *dupstr(const char *s) {
  char *d = malloc(strlen(s) + 1);
  if (!d) {
    fprintf(stderr, "mémoire épuisée\n");
    exit(2);
  }
  strcpy(d, s);
  return d;
}

/* ---------- norme des mots-clés ---------- */

static void normer(const char *src, char *dst) {
  /* = norm() : minuscules ASCII + é/è/ê/É/È/Ê -> e. */
  while (*src) {
    unsigned char c = (unsigned char)*src;
    if (c >= 'A' && c <= 'Z') {
      *dst++ = (char)(c + 32);
      src++;
    } else if (c == 0xC3 && (src[1] == '\xA9' || src[1] == '\xA8' ||
                             src[1] == '\xAA' || src[1] == '\x89' ||
                             src[1] == '\x88' || src[1] == '\x8A')) {
      *dst++ = 'e';
      src += 2;
    } else {
      *dst++ = *src++;
    }
  }
  *dst = '\0';
}

/* ---------- recherche ---------- */

static int idx_neurone(const char *nom) {
  for (int i = 0; i < T->nneur; i++)
    if (strcmp(T->neurones[i].nom, nom) == 0)
      return i;
  return -1;
}

static int idx_motif(const char *nom) {
  for (int i = 0; i < T->nmotif; i++)
    if (strcmp(T->motifs[i].nom, nom) == 0)
      return i;
  return -1;
}

/* cle_lien : (min, max) au sens strcmp — comme sorted() sur de l'UTF-8. */
static void ordonner(const char **a, const char **b) {
  if (strcmp(*a, *b) > 0) {
    const char *t = *a;
    *a = *b;
    *b = t;
  }
}

static int idx_lien(const char *a, const char *b) {
  ordonner(&a, &b);
  for (int i = 0; i < T->nlien; i++)
    if (strcmp(T->liens[i].a, a) == 0 && strcmp(T->liens[i].b, b) == 0)
      return i;
  return -1;
}

static void reindexer(void) {
  for (int i = 0; i < T->nlien; i++) {
    T->liens[i].ia = idx_neurone(T->liens[i].a);
    T->liens[i].ib = idx_neurone(T->liens[i].b);
  }
  for (int i = 0; i < T->nmotif; i++)
    for (int j = 0; j < T->motifs[i].nmb; j++)
      T->motifs[i].imembres[j] = idx_neurone(T->motifs[i].membres[j]);
}

static int actif(int i) {
  return T->neurones[i].charge >= T->neurones[i].seuil;
}

/* ---------- découpage ---------- */

typedef struct {
  int noligne;
  char **mots;
  int nmots;
} Instr;

static Instr *instr = NULL;
static int ninstr = 0, capinstr = 0;

static void decoupage(FILE *fh) {
  char *ligne = NULL;
  size_t cap = 0;
  ssize_t n;
  int noligne = 0;
  while ((n = getline(&ligne, &cap, fh)) >= 0) {
    noligne++;
    char *diese = strchr(ligne, '#');
    if (diese)
      *diese = '\0';
    /* découpe aux blancs (comme str.split()) */
    int nmots = 0, capmots = 0;
    char **mots = NULL;
    for (char *p = ligne; *p;) {
      while (*p && isspace((unsigned char)*p))
        p++;
      if (!*p)
        break;
      char *deb = p;
      while (*p && !isspace((unsigned char)*p))
        p++;
      char sauve = *p;
      *p = '\0';
      mots = grandir(mots, &capmots, nmots, sizeof *mots);
      mots[nmots++] = dupstr(deb);
      if (!sauve)
        break;
      p++;
    }
    if (nmots == 0) {
      free(mots);
      continue;
    }
    instr = grandir(instr, &capinstr, ninstr, sizeof *instr);
    instr[ninstr].noligne = noligne;
    instr[ninstr].mots = mots;
    instr[ninstr].nmots = nmots;
    ninstr++;
  }
  free(ligne);
}

/* ---------- blocs ---------- */

static int est_ouvreur(const char *w) {
  char n[64];
  /* les mots-clés tiennent en 63 octets (corpus) */
  if (strlen(w) >= sizeof n)
    return 0;
  normer(w, n);
  return strcmp(n, "tissu") == 0 || strcmp(n, "repeter") == 0 || strcmp(n, "si") == 0;
}

static int est_fin(const char *w) {
  char n[64];
  if (strlen(w) >= sizeof n)
    return 0;
  normer(w, n);
  return strcmp(n, "fin") == 0;
}

static int bloc_fin(int debut) {
  int prof = 0;
  for (int k = debut; k < ninstr; k++) {
    if (est_ouvreur(instr[k].mots[0]))
      prof++;
    else if (est_fin(instr[k].mots[0])) {
      prof--;
      if (prof == 0)
        return k;
    }
  }
  LEVER(instr[debut].noligne, "bloc ouvert mais jamais fermé par 'fin'");
  return -1;
}

static int bloc_sinon(int debut, int fin) {
  int prof = 0;
  for (int k = debut; k < fin; k++) {
    char n[64];
    if (strlen(instr[k].mots[0]) < sizeof n)
      normer(instr[k].mots[0], n);
    else
      n[0] = '\0';
    if (est_ouvreur(instr[k].mots[0]))
      prof++;
    else if (strcmp(n, "fin") == 0)
      prof--;
    else if (strcmp(n, "sinon") == 0 && prof == 1)
      return k;
  }
  return -1;
}

/* ---------- résonance ---------- */

static int cmp_str(const void *pa, const void *pb) {
  return strcmp(*(char *const *)pa, *(char *const *)pb);
}

static int resonance(const char *motif) {
  int im = idx_motif(motif);
  if (im < 0) {
    snprintf(message_erreur, sizeof message_erreur, "motif inconnu '%s'", motif);
    longjmp(echec, 1);
  }
  /* sorted(set(membres)) */
  int n = T->motifs[im].nmb;
  char **mb = malloc((size_t)(n > 0 ? n : 1) * sizeof *mb);
  for (int i = 0; i < n; i++)
    mb[i] = T->motifs[im].membres[i];
  qsort(mb, (size_t)n, sizeof *mb, cmp_str);
  int u = 0;
  for (int i = 0; i < n; i++)
    if (i == 0 || strcmp(mb[i], mb[i - 1]) != 0)
      mb[u++] = mb[i];
  long somme = 0;
  int npaires = 0;
  for (int i = 0; i < u; i++)
    for (int j = i + 1; j < u; j++) {
      int il = idx_lien(mb[i], mb[j]);
      somme += il >= 0 ? T->liens[il].force : 0;
      npaires++;
    }
  free(mb);
  if (!npaires)
    return 0;
  return (int)(somme / npaires);
}

/* ---------- commandes ---------- */

static int entier(int noligne, char **mots, int nmots, int pos, const char *usage) {
  if (nmots <= pos)
    LEVER(noligne, "il manque un nombre — usage : %s", usage);
  char *fin;
  errno = 0;
  long v = strtol(mots[pos], &fin, 10);
  if (fin == mots[pos] || *fin != '\0')
    LEVER(noligne, "'%s' n'est pas un nombre — usage : %s", mots[pos], usage);
  (void)errno;
  return (int)v;
}

static void exige_tissu(int noligne) {
  if (!T)
    LEVER(noligne, "aucun tissu ouvert — commence par 'tissu <nom>'");
}

static void exige_neurone(int noligne, const char *nom) {
  if (idx_neurone(nom) < 0)
    LEVER(noligne, "neurone inconnu '%s' — déclare-le d'abord", nom);
}

static void cmd_tissu(int noligne, char **mots, int nmots) {
  if (nmots != 2)
    LEVER(noligne, "usage : tissu <nom>");
  if (T)
    LEVER(noligne, "v0 : un seul tissu par programme");
  T = calloc(1, sizeof *T);
  T->nom = dupstr(mots[1]);
  printf("=== tissu %s ===\n", mots[1]);
}

static void cmd_neurone(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots < 2 || nmots > 5)
    LEVER(noligne, "usage : neurone <nom> [seuil <n>] [cise]");
  int seuil = SEUIL_DEFAUT, type_cise = 0;
  /* reste = mots[2:] normés, moins la paire seuil <n> */
  char reste[3][64];
  int nreste = 0;
  for (int i = 2; i < nmots && nreste < 3; i++) {
    if (strlen(mots[i]) < sizeof reste[0])
      normer(mots[i], reste[nreste++]);
    else
      LEVER(noligne, "usage : neurone <nom> [seuil <n>] [cise]");
  }
  int is = -1;
  for (int i = 0; i < nreste; i++)
    if (strcmp(reste[i], "seuil") == 0) {
      is = i;
      break;
    }
  if (is >= 0) {
    if (is + 1 >= nreste)
      LEVER(noligne, "usage : neurone <nom> [seuil <n>] [cise]");
    seuil = borne(entier(noligne, mots, nmots, 2 + is + 1, "neurone <nom> seuil <n>"));
    for (int i = is; i + 2 < nreste; i++)
      strcpy(reste[i], reste[i + 2]);
    nreste -= 2;
  }
  if (nreste == 1 && strcmp(reste[0], "cise") == 0)
    type_cise = 1;
  else if (!(nreste == 0 || (nreste == 1 && strcmp(reste[0], "transporteur") == 0)))
    LEVER(noligne, "usage : neurone <nom> [seuil <n>] [cise]");
  int ix = idx_neurone(mots[1]);
  if (ix < 0) {
    T->neurones = grandir(T->neurones, &T->capneur, T->nneur, sizeof *T->neurones);
    ix = T->nneur++;
    T->neurones[ix].nom = dupstr(mots[1]);
  }
  T->neurones[ix].seuil = seuil;
  T->neurones[ix].charge = 0;
  T->neurones[ix].coups = 0;
  T->neurones[ix].cise = type_cise;
}

static void cmd_lien(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  char dernier[64] = "";
  if (strlen(mots[nmots - 1]) < sizeof dernier)
    normer(mots[nmots - 1], dernier);
  int gele = nmots > 3 && strcmp(dernier, "gele") == 0;
  int ncorps = gele ? nmots - 1 : nmots;
  char force_kw[64] = "";
  if (ncorps == 5 && strlen(mots[3]) < sizeof force_kw)
    normer(mots[3], force_kw);
  if (!((ncorps == 3) || (ncorps == 5 && strcmp(force_kw, "force") == 0)))
    LEVER(noligne, "usage : lien <a> <b> [force <n>] [gelé]");
  exige_neurone(noligne, mots[1]);
  exige_neurone(noligne, mots[2]);
  int force = ncorps == 5
      ? borne(entier(noligne, mots, nmots, 4, "lien <a> <b> force <n>"))
      : FORCE_NAISSANCE;
  const char *a = mots[1], *b = mots[2];
  ordonner(&a, &b);
  int ix = idx_lien(a, b);
  if (ix < 0) {
    T->liens = grandir(T->liens, &T->caplien, T->nlien, sizeof *T->liens);
    ix = T->nlien++;
    T->liens[ix].a = dupstr(a);
    T->liens[ix].b = dupstr(b);
    T->liens[ix].gele = 0;
  }
  T->liens[ix].force = force;
  if (gele)
    T->liens[ix].gele = 1;
  T->liens[ix].ia = idx_neurone(T->liens[ix].a);
  T->liens[ix].ib = idx_neurone(T->liens[ix].b);
}

static void cmd_motif(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  int nreste = 0;
  for (int i = 2; i < nmots; i++)
    if (strcmp(mots[i], ":") != 0)
      nreste++;
  if (nmots < 3 || !nreste)
    LEVER(noligne, "usage : motif <NOM> : <neurone> <neurone> ...");
  for (int i = 2; i < nmots; i++)
    if (strcmp(mots[i], ":") != 0)
      exige_neurone(noligne, mots[i]);
  int ix = idx_motif(mots[1]);
  if (ix < 0) {
    T->motifs = grandir(T->motifs, &T->capmotif, T->nmotif, sizeof *T->motifs);
    ix = T->nmotif++;
    T->motifs[ix].nom = dupstr(mots[1]);
    T->motifs[ix].membres = NULL;
    T->motifs[ix].imembres = NULL;
    T->motifs[ix].nmb = 0;
  } else {
    for (int i = 0; i < T->motifs[ix].nmb; i++)
      free(T->motifs[ix].membres[i]);
    free(T->motifs[ix].membres);
    free(T->motifs[ix].imembres);
    T->motifs[ix].nmb = 0;
  }
  T->motifs[ix].membres = malloc((size_t)nreste * sizeof(char *));
  T->motifs[ix].imembres = malloc((size_t)nreste * sizeof(int));
  for (int i = 2; i < nmots; i++)
    if (strcmp(mots[i], ":") != 0) {
      T->motifs[ix].membres[T->motifs[ix].nmb] = dupstr(mots[i]);
      T->motifs[ix].imembres[T->motifs[ix].nmb] = idx_neurone(mots[i]);
      T->motifs[ix].nmb++;
    }
}

static void cmd_rencontre(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 2 || idx_motif(mots[1]) < 0)
    LEVER(noligne, "usage : rencontre <motif> (motif déclaré)");
  Motif *m = &T->motifs[idx_motif(mots[1])];
  for (int i = 0; i < m->nmb; i++) {
    T->neurones[m->imembres[i]].charge = 100;
    T->neurones[m->imembres[i]].coups++;
  }
}

static void cmd_propager(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 1)
    LEVER(noligne, "usage : propager");
  (void)mots;
  int *vieux = malloc((size_t)(T->nneur > 0 ? T->nneur : 1) * sizeof *vieux);
  int *nouv = malloc((size_t)(T->nneur > 0 ? T->nneur : 1) * sizeof *nouv);
  for (int i = 0; i < T->nneur; i++)
    vieux[i] = nouv[i] = T->neurones[i].charge;
  for (int i = 0; i < T->nlien; i++) {
    int f = T->liens[i].force, ia = T->liens[i].ia, ib = T->liens[i].ib;
    nouv[ib] = borne(nouv[ib] + f * vieux[ia] / 200);
    nouv[ia] = borne(nouv[ia] + f * vieux[ib] / 200);
  }
  for (int i = 0; i < T->nneur; i++)
    T->neurones[i].charge = nouv[i];
  free(vieux);
  free(nouv);
}

static void cmd_renforcer(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  char w1[64] = "", w3[64] = "";
  if (nmots > 1 && strlen(mots[1]) < sizeof w1)
    normer(mots[1], w1);
  if (nmots > 3 && strlen(mots[3]) < sizeof w3)
    normer(mots[3], w3);
  int haut, bas;
  if (nmots == 1) {
    haut = PAS_RENFORCER;
    bas = PAS_DELIE;
  } else if (nmots == 3 && strcmp(w1, "pas") == 0) {
    haut = bas = entier(noligne, mots, nmots, 2, "renforcer [pas <n>]");
  } else if (nmots == 5 && strcmp(w1, "lie") == 0 && strcmp(w3, "delie") == 0) {
    haut = entier(noligne, mots, nmots, 2, "renforcer lie <X> delie <Y>");
    bas = entier(noligne, mots, nmots, 4, "renforcer lie <X> delie <Y>");
  } else {
    LEVER(noligne, "usage : renforcer [pas <n>] ou renforcer lie <X> delie <Y>");
    return;
  }
  for (int i = 0; i < T->nlien; i++) {
    if (T->liens[i].gele)
      continue;
    if (actif(T->liens[i].ia) && actif(T->liens[i].ib)) {
      int f = T->liens[i].force;
      int gain = haut * (100 - f) / 100;
      if (gain < 1)
        gain = 1;
      T->liens[i].force = borne(f + gain);
    } else {
      T->liens[i].force = borne(T->liens[i].force - bas);
    }
  }
}

static void cmd_oublier(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  char w1[64] = "";
  if (nmots > 1 && strlen(mots[1]) < sizeof w1)
    normer(mots[1], w1);
  int pas = PAS_OUBLIER;
  if (nmots == 3 && strcmp(w1, "pas") == 0)
    pas = entier(noligne, mots, nmots, 2, "oublier [pas <n>]");
  else if (nmots != 1)
    LEVER(noligne, "usage : oublier [pas <n>]");
  for (int i = 0; i < T->nlien; i++)
    if (!T->liens[i].gele)
      T->liens[i].force = borne(T->liens[i].force - pas);
  for (int i = 0; i < T->nneur; i++)
    T->neurones[i].coups = 0;
}

static void cmd_repos(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 1)
    LEVER(noligne, "usage : repos");
  (void)mots;
  for (int i = 0; i < T->nneur; i++)
    T->neurones[i].charge = 0;
}

static void cmd_adapter(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 1)
    LEVER(noligne, "usage : adapter");
  (void)mots;
  for (int i = 0; i < T->nneur; i++)
    if (!T->neurones[i].cise)
      T->neurones[i].seuil = (T->neurones[i].seuil + T->neurones[i].charge) / 2;
}

static void cmd_nettoyer(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 1)
    LEVER(noligne, "usage : nettoyer");
  (void)mots;
  /* liens à 0 arrachés (ordre conservé : décalage, pas d'échange) */
  int morts_l = 0;
  for (int i = 0; i < T->nlien;) {
    if (T->liens[i].force <= 0 && !T->liens[i].gele) {
      free(T->liens[i].a);
      free(T->liens[i].b);
      memmove(&T->liens[i], &T->liens[i + 1],
              (size_t)(T->nlien - i - 1) * sizeof *T->liens);
      T->nlien--;
      morts_l++;
    } else {
      i++;
    }
  }
  /* neurones isolés morts, SAUF nommés (motifs) et CISE */
  int morts_n = 0;
  for (int i = 0; i < T->nneur;) {
    int relie = 0, nomme = 0;
    for (int j = 0; j < T->nlien; j++)
      if (T->liens[j].ia == i || T->liens[j].ib == i) {
        relie = 1;
        break;
      }
    for (int j = 0; j < T->nmotif && !nomme; j++)
      for (int k = 0; k < T->motifs[j].nmb; k++)
        if (T->motifs[j].imembres[k] == i) {
          nomme = 1;
          break;
        }
    if (!relie && !nomme && !T->neurones[i].cise) {
      free(T->neurones[i].nom);
      memmove(&T->neurones[i], &T->neurones[i + 1],
              (size_t)(T->nneur - i - 1) * sizeof *T->neurones);
      T->nneur--;
      morts_n++;
    } else {
      i++;
    }
  }
  reindexer();
  printf("nettoyage : %d liens morts, %d neurones morts\n", morts_l, morts_n);
}

static void cmd_cise(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 2 || idx_motif(mots[1]) < 0)
    LEVER(noligne, "usage : cise <motif> (motif déclaré)");
  Motif *m = &T->motifs[idx_motif(mots[1])];
  /* dict.fromkeys : dédup dans l'ordre */
  int *vus = malloc((size_t)(m->nmb > 0 ? m->nmb : 1) * sizeof *vus);
  int nvus = 0;
  char **figes = malloc((size_t)(m->nmb > 0 ? m->nmb : 1) * sizeof *figes);
  int nfig = 0;
  for (int i = 0; i < m->nmb; i++) {
    int ix = m->imembres[i];
    int deja = 0;
    for (int j = 0; j < nvus; j++)
      if (vus[j] == ix)
        deja = 1;
    if (deja)
      continue;
    vus[nvus++] = ix;
    Neurone *v = &T->neurones[ix];
    if (v->cise)
      continue;
    int vitesse = v->coups + v->charge / 20;
    if (vitesse >= VITESSE_CISE && v->charge >= v->seuil) {
      v->cise = 1;
      figes[nfig++] = v->nom;
    }
  }
  free(vus);
  int fils = 0;
  for (int i = 0; i < T->nlien; i++)
    if (!T->liens[i].gele && T->neurones[T->liens[i].ia].cise &&
        T->neurones[T->liens[i].ib].cise) {
      T->liens[i].gele = 1;
      fils++;
    }
  if (nfig) {
    T->journal = grandir(T->journal, &T->capjourn, T->njourn, sizeof *T->journal);
    Etincelle *e = &T->journal[T->njourn++];
    e->motif = dupstr(mots[1]);
    e->figes = malloc((size_t)nfig * sizeof *e->figes);
    for (int i = 0; i < nfig; i++)
      e->figes[i] = dupstr(figes[i]);
    e->nfig = nfig;
    printf("étincelle : ");
    for (int i = 0; i < nfig; i++)
      printf("%s%s", i ? " " : "", figes[i]);
    printf(" figé%s, %d filament%s\n", nfig > 1 ? "s" : "", fils, fils > 1 ? "s" : "");
  } else {
    printf("étincelle : rien d'assez rapide\n");
  }
  free(figes);
}

static void cmd_resonance(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 2)
    LEVER(noligne, "usage : résonance <motif>");
  printf("résonance %s = %d/100\n", mots[1], resonance(mots[1]));
}

static void cmd_mesurer(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 1)
    LEVER(noligne, "usage : mesurer");
  (void)mots;
  long somme = 0;
  int forts = 0;
  for (int i = 0; i < T->nlien; i++) {
    somme += T->liens[i].force;
    if (T->liens[i].force >= 70)
      forts++;
  }
  printf("liens : %d\n", T->nlien);
  printf("force moyenne : %d/100\n", T->nlien ? (int)(somme / T->nlien) : 0);
  printf("liens forts : %d\n", forts);
  int ncise = 0, nfil = 0;
  for (int i = 0; i < T->nneur; i++)
    if (T->neurones[i].cise)
      ncise++;
  for (int i = 0; i < T->nlien; i++)
    if (T->liens[i].gele)
      nfil++;
  printf("cise : %d neurone%s, %d filament%s\n", ncise, ncise > 1 ? "s" : "",
         nfil, nfil > 1 ? "s" : "");
}

static void cmd_juger(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 3)
    LEVER(noligne, "usage : juger <motif> <seuil>");
  int r = resonance(mots[1]);
  int seuil = entier(noligne, mots, nmots, 2, "juger <motif> <seuil>");
  printf("JUGEMENT %s : %s (%d/100, seuil %d)\n", mots[1],
         r >= seuil ? "TIENT" : "ROMPT", r, seuil);
}

static int cmp_lien_tri(const void *pa, const void *pb) {
  const Lien *la = &T->liens[*(const int *)pa];
  const Lien *lb = &T->liens[*(const int *)pb];
  int c = strcmp(la->a, lb->a);
  return c ? c : strcmp(la->b, lb->b);
}

static int cmp_neur_tri(const void *pa, const void *pb) {
  return strcmp(T->neurones[*(const int *)pa].nom, T->neurones[*(const int *)pb].nom);
}

static void cmd_dire(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots < 2)
    LEVER(noligne, "usage : dire <mots...> (avec résonance <motif>, forces ou seuils)");
  int premier = 1;
  for (int i = 1; i < nmots;) {
    char n[64] = "";
    if (strlen(mots[i]) < sizeof n)
      normer(mots[i], n);
    if (!premier)
      putchar(' ');
    premier = 0;
    if (strcmp(n, "resonance") == 0 && i + 1 < nmots) {
      printf("%d", resonance(mots[i + 1]));
      i += 2;
    } else if (strcmp(n, "forces") == 0) {
      if (!T->nlien) {
        printf("(aucun lien)");
      } else {
        int *tri = malloc((size_t)T->nlien * sizeof *tri);
        for (int j = 0; j < T->nlien; j++)
          tri[j] = j;
        qsort(tri, (size_t)T->nlien, sizeof *tri, cmp_lien_tri);
        for (int j = 0; j < T->nlien; j++) {
          Lien *l = &T->liens[tri[j]];
          printf("%s%s-%s=%d%s", j ? " " : "", l->a, l->b, l->force,
                 l->gele ? "!" : "");
        }
        free(tri);
      }
      i++;
    } else if (strcmp(n, "seuils") == 0) {
      if (T->nneur) {
        int *tri = malloc((size_t)T->nneur * sizeof *tri);
        for (int j = 0; j < T->nneur; j++)
          tri[j] = j;
        qsort(tri, (size_t)T->nneur, sizeof *tri, cmp_neur_tri);
        for (int j = 0; j < T->nneur; j++)
          printf("%s%s=%d", j ? " " : "", T->neurones[tri[j]].nom,
                 T->neurones[tri[j]].seuil);
        free(tri);
      }
      i++;
    } else {
      fputs(mots[i], stdout);
      i++;
    }
  }
  putchar('\n');
}

/* ---------- graver : JSON identique à json.dump(indent=1) ---------- */

static void json_chaine(FILE *fh, const char *s) {
  fputc('"', fh);
  for (; *s; s++) {
    unsigned char c = (unsigned char)*s;
    if (c == '"')
      fputs("\\\"", fh);
    else if (c == '\\')
      fputs("\\\\", fh);
    else if (c == '\n')
      fputs("\\n", fh);
    else if (c == '\t')
      fputs("\\t", fh);
    else if (c == '\r')
      fputs("\\r", fh);
    else if (c == '\b')
      fputs("\\b", fh);
    else if (c == '\f')
      fputs("\\f", fh);
    else if (c < 0x20)
      fprintf(fh, "\\u%04x", c);
    else
      fputc(c, fh);
  }
  fputc('"', fh);
}

static void indenter(FILE *fh, int n) {
  for (int i = 0; i < n; i++)
    fputc(' ', fh);
}

static void cmd_graver(int noligne, char **mots, int nmots) {
  exige_tissu(noligne);
  if (nmots != 2)
    LEVER(noligne, "usage : graver <fichier>");
  FILE *fh = fopen(mots[1], "w");
  if (!fh)
    LEVER(noligne, "impossible de graver '%s'", mots[1]);
  fputs("{\n", fh);
  indenter(fh, 1);
  fputs("\"tissu\": ", fh);
  json_chaine(fh, T->nom);
  fputs(",\n", fh);
  /* neurones */
  indenter(fh, 1);
  fputs("\"neurones\": ", fh);
  if (!T->nneur) {
    fputs("{}", fh);
  } else {
    fputs("{\n", fh);
    for (int i = 0; i < T->nneur; i++) {
      Neurone *v = &T->neurones[i];
      indenter(fh, 2);
      json_chaine(fh, v->nom);
      fputs(": {\n", fh);
      indenter(fh, 3);
      fprintf(fh, "\"seuil\": %d,\n", v->seuil);
      indenter(fh, 3);
      fprintf(fh, "\"charge\": %d,\n", v->charge);
      indenter(fh, 3);
      fprintf(fh, "\"coups\": %d,\n", v->coups);
      indenter(fh, 3);
      fprintf(fh, "\"type\": \"%s\"\n", v->cise ? "cise" : "transporteur");
      indenter(fh, 2);
      fputs(i + 1 < T->nneur ? "},\n" : "}\n", fh);
    }
    indenter(fh, 1);
    fputc('}', fh);
  }
  fputs(",\n", fh);
  /* liens */
  indenter(fh, 1);
  fputs("\"liens\": ", fh);
  if (!T->nlien) {
    fputs("[]", fh);
  } else {
    fputs("[\n", fh);
    for (int i = 0; i < T->nlien; i++) {
      Lien *l = &T->liens[i];
      indenter(fh, 2);
      fputs("{\n", fh);
      indenter(fh, 3);
      fputs("\"a\": ", fh);
      json_chaine(fh, l->a);
      fputs(",\n", fh);
      indenter(fh, 3);
      fputs("\"b\": ", fh);
      json_chaine(fh, l->b);
      fputs(",\n", fh);
      indenter(fh, 3);
      fprintf(fh, "\"force\": %d\n", l->force);
      indenter(fh, 2);
      fputs(i + 1 < T->nlien ? "},\n" : "}\n", fh);
    }
    indenter(fh, 1);
    fputc(']', fh);
  }
  fputs(",\n", fh);
  /* gelés (ordre d'insertion — voir LISEZ-MOI.md) */
  indenter(fh, 1);
  fputs("\"geles\": ", fh);
  int ngel = 0;
  for (int i = 0; i < T->nlien; i++)
    if (T->liens[i].gele)
      ngel++;
  if (!ngel) {
    fputs("[]", fh);
  } else {
    fputs("[\n", fh);
    int k = 0;
    for (int i = 0; i < T->nlien; i++) {
      if (!T->liens[i].gele)
        continue;
      indenter(fh, 2);
      fputs("[\n", fh);
      indenter(fh, 3);
      json_chaine(fh, T->liens[i].a);
      fputs(",\n", fh);
      indenter(fh, 3);
      json_chaine(fh, T->liens[i].b);
      fputc('\n', fh);
      indenter(fh, 2);
      fputs(++k < ngel ? "],\n" : "]\n", fh);
    }
    indenter(fh, 1);
    fputc(']', fh);
  }
  fputs(",\n", fh);
  /* journal */
  indenter(fh, 1);
  fputs("\"journal_cise\": ", fh);
  if (!T->njourn) {
    fputs("[]", fh);
  } else {
    fputs("[\n", fh);
    for (int i = 0; i < T->njourn; i++) {
      Etincelle *e = &T->journal[i];
      indenter(fh, 2);
      fputs("{\n", fh);
      indenter(fh, 3);
      fputs("\"motif\": ", fh);
      json_chaine(fh, e->motif);
      fputs(",\n", fh);
      indenter(fh, 3);
      fputs("\"figes\": ", fh);
      if (!e->nfig) {
        fputs("[]\n", fh);
      } else {
        fputs("[\n", fh);
        for (int j = 0; j < e->nfig; j++) {
          indenter(fh, 4);
          json_chaine(fh, e->figes[j]);
          fputs(j + 1 < e->nfig ? ",\n" : "\n", fh);
        }
        indenter(fh, 3);
        fputs("]\n", fh);
      }
      indenter(fh, 2);
      fputs(i + 1 < T->njourn ? "},\n" : "}\n", fh);
    }
    indenter(fh, 1);
    fputc(']', fh);
  }
  fputs(",\n", fh);
  /* motifs */
  indenter(fh, 1);
  fputs("\"motifs\": ", fh);
  if (!T->nmotif) {
    fputs("{}", fh);
  } else {
    fputs("{\n", fh);
    for (int i = 0; i < T->nmotif; i++) {
      Motif *m = &T->motifs[i];
      indenter(fh, 2);
      json_chaine(fh, m->nom);
      fputs(": ", fh);
      if (!m->nmb) {
        fputs("[]", fh);
      } else {
        fputs("[\n", fh);
        for (int j = 0; j < m->nmb; j++) {
          indenter(fh, 3);
          json_chaine(fh, m->membres[j]);
          fputs(j + 1 < m->nmb ? ",\n" : "\n", fh);
        }
        indenter(fh, 2);
        fputc(']', fh);
      }
      fputs(i + 1 < T->nmotif ? ",\n" : "\n", fh);
    }
    indenter(fh, 1);
    fputc('}', fh);
  }
  fputs("\n}", fh);
  fclose(fh);
  printf("tissu gravé dans %s\n", mots[1]);
}

/* ---------- relire : mini-lecteur JSON (sous-ensemble scroll) ---------- */

typedef struct {
  const char *p;
  int noligne;
} Lecteur;

static void json_erreur(Lecteur *l, const char *quoi) {
  LEVER(l->noligne, "scroll illisible (%s)", quoi);
}

static void json_blancs(Lecteur *l) {
  while (*l->p == ' ' || *l->p == '\t' || *l->p == '\n' || *l->p == '\r')
    l->p++;
}

static void json_attend(Lecteur *l, char c) {
  json_blancs(l);
  if (*l->p != c)
    json_erreur(l, "ponctuation attendue");
  l->p++;
}

static int json_hex(char c) {
  if (c >= '0' && c <= '9')
    return c - '0';
  if (c >= 'a' && c <= 'f')
    return c - 'a' + 10;
  if (c >= 'A' && c <= 'F')
    return c - 'A' + 10;
  return -1;
}

static char *json_texte(Lecteur *l) {
  json_attend(l, '"');
  size_t cap = 32, n = 0;
  char *s = malloc(cap);
  for (;;) {
    char c = *l->p++;
    if (c == '"')
      break;
    if (c == '\0')
      json_erreur(l, "chaîne non fermée");
    char out[4];
    int nout = 1;
    out[0] = c;
    if (c == '\\') {
      char e = *l->p++;
      if (e == 'n')
        out[0] = '\n';
      else if (e == 't')
        out[0] = '\t';
      else if (e == 'r')
        out[0] = '\r';
      else if (e == 'b')
        out[0] = '\b';
      else if (e == 'f')
        out[0] = '\f';
      else if (e == '"' || e == '\\' || e == '/')
        out[0] = e;
      else if (e == 'u') {
        int v = 0;
        for (int i = 0; i < 4; i++) {
          int h = json_hex(*l->p++);
          if (h < 0)
            json_erreur(l, "échappement unicode");
          v = v * 16 + h;
        }
        if (v < 0x80) {
          out[0] = (char)v;
        } else if (v < 0x800) {
          out[0] = (char)(0xC0 | (v >> 6));
          out[1] = (char)(0x80 | (v & 0x3F));
          nout = 2;
        } else {
          out[0] = (char)(0xE0 | (v >> 12));
          out[1] = (char)(0x80 | ((v >> 6) & 0x3F));
          out[2] = (char)(0x80 | (v & 0x3F));
          nout = 3;
        }
      } else {
        json_erreur(l, "échappement inconnu");
      }
    }
    while (n + (size_t)nout + 1 > cap) {
      cap *= 2;
      s = realloc(s, cap);
    }
    for (int i = 0; i < nout; i++)
      s[n++] = out[i];
  }
  s[n] = '\0';
  return s;
}

static long json_nombre(Lecteur *l) {
  json_blancs(l);
  char *fin;
  long v = strtol(l->p, &fin, 10);
  if (fin == l->p)
    json_erreur(l, "nombre attendu");
  l->p = fin;
  return v;
}

static void json_sauter(Lecteur *l) {
  /* saute une valeur quelconque (clés inconnues ignorées, comme Python) */
  json_blancs(l);
  if (*l->p == '"') {
    char *s = json_texte(l);
    free(s);
  } else if (*l->p == '{') {
    l->p++;
    json_blancs(l);
    if (*l->p == '}') {
      l->p++;
      return;
    }
    for (;;) {
      char *k = json_texte(l);
      free(k);
      json_attend(l, ':');
      json_sauter(l);
      json_blancs(l);
      if (*l->p == ',') {
        l->p++;
        continue;
      }
      json_attend(l, '}');
      return;
    }
  } else if (*l->p == '[') {
    l->p++;
    json_blancs(l);
    if (*l->p == ']') {
      l->p++;
      return;
    }
    for (;;) {
      json_sauter(l);
      json_blancs(l);
      if (*l->p == ',') {
        l->p++;
        continue;
      }
      json_attend(l, ']');
      return;
    }
  } else {
    (void)json_nombre(l);
  }
}

static void cmd_relire(int noligne, char **mots, int nmots) {
  if (nmots != 2)
    LEVER(noligne, "usage : relire <fichier>");
  FILE *fh = fopen(mots[1], "r");
  if (!fh)
    LEVER(noligne, "impossible de relire '%s'", mots[1]);
  size_t cap = 4096, n = 0;
  char *buf = malloc(cap);
  size_t r;
  while ((r = fread(buf + n, 1, cap - n, fh)) > 0)
    n += r;
  if (!feof(fh)) {
    fclose(fh);
    free(buf);
    LEVER(noligne, "impossible de relire '%s'", mots[1]);
  }
  fclose(fh);
  buf = realloc(buf, n + 1);
  buf[n] = '\0';
  Lecteur l = {buf, noligne};
  Tissu *t = calloc(1, sizeof *t);
  Tissu *sauve = T;
  T = t; /* les ajouts ci-dessous écrivent dans le neuf */
  json_attend(&l, '{');
  json_blancs(&l);
  if (*l.p != '}') {
    for (;;) {
      char *cle = json_texte(&l);
      json_attend(&l, ':');
      if (strcmp(cle, "tissu") == 0) {
        t->nom = json_texte(&l);
      } else if (strcmp(cle, "neurones") == 0) {
        json_attend(&l, '{');
        json_blancs(&l);
        if (*l.p != '}') {
          for (;;) {
            char *nom = json_texte(&l);
            json_attend(&l, ':');
            json_attend(&l, '{');
            int seuil = 0, charge = 0, coups = 0, cise = 0;
            json_blancs(&l);
            if (*l.p != '}') {
              for (;;) {
                char *k = json_texte(&l);
                json_attend(&l, ':');
                if (strcmp(k, "seuil") == 0)
                  seuil = (int)json_nombre(&l);
                else if (strcmp(k, "charge") == 0)
                  charge = (int)json_nombre(&l);
                else if (strcmp(k, "coups") == 0)
                  coups = (int)json_nombre(&l);
                else if (strcmp(k, "type") == 0) {
                  char *tv = json_texte(&l);
                  cise = strcmp(tv, "cise") == 0;
                  free(tv);
                } else {
                  json_sauter(&l);
                }
                free(k);
                json_blancs(&l);
                if (*l.p == ',') {
                  l.p++;
                  continue;
                }
                json_attend(&l, '}');
                break;
              }
            } else {
              l.p++;
            }
            t->neurones = grandir(t->neurones, &t->capneur, t->nneur, sizeof *t->neurones);
            Neurone *v = &t->neurones[t->nneur++];
            v->nom = nom;
            v->seuil = seuil;
            v->charge = charge;
            v->coups = coups;
            v->cise = cise;
            json_blancs(&l);
            if (*l.p == ',') {
              l.p++;
              continue;
            }
            json_attend(&l, '}');
            break;
          }
        } else {
          l.p++;
        }
      } else if (strcmp(cle, "liens") == 0) {
        json_attend(&l, '[');
        json_blancs(&l);
        if (*l.p != ']') {
          for (;;) {
            json_attend(&l, '{');
            char *a = NULL, *b = NULL;
            int force = 0;
            json_blancs(&l);
            if (*l.p != '}') {
              for (;;) {
                char *k = json_texte(&l);
                json_attend(&l, ':');
                if (strcmp(k, "a") == 0)
                  a = json_texte(&l);
                else if (strcmp(k, "b") == 0)
                  b = json_texte(&l);
                else if (strcmp(k, "force") == 0)
                  force = (int)json_nombre(&l);
                else
                  json_sauter(&l);
                free(k);
                json_blancs(&l);
                if (*l.p == ',') {
                  l.p++;
                  continue;
                }
                json_attend(&l, '}');
                break;
              }
            } else {
              l.p++;
            }
            const char *pa = a, *pb = b;
            ordonner(&pa, &pb);
            t->liens = grandir(t->liens, &t->caplien, t->nlien, sizeof *t->liens);
            Lien *li = &t->liens[t->nlien++];
            li->a = dupstr(pa);
            li->b = dupstr(pb);
            li->force = force;
            li->gele = 0;
            free(a);
            free(b);
            json_blancs(&l);
            if (*l.p == ',') {
              l.p++;
              continue;
            }
            json_attend(&l, ']');
            break;
          }
        } else {
          l.p++;
        }
      } else if (strcmp(cle, "geles") == 0) {
        json_attend(&l, '[');
        json_blancs(&l);
        if (*l.p != ']') {
          for (;;) {
            json_attend(&l, '[');
            char *a = json_texte(&l);
            json_attend(&l, ',');
            char *b = json_texte(&l);
            json_blancs(&l);
            json_attend(&l, ']');
            const char *pa = a, *pb = b;
            ordonner(&pa, &pb);
            for (int i = 0; i < t->nlien; i++)
              if (strcmp(t->liens[i].a, pa) == 0 && strcmp(t->liens[i].b, pb) == 0)
                t->liens[i].gele = 1;
            free(a);
            free(b);
            json_blancs(&l);
            if (*l.p == ',') {
              l.p++;
              continue;
            }
            json_attend(&l, ']');
            break;
          }
        } else {
          l.p++;
        }
      } else if (strcmp(cle, "journal_cise") == 0) {
        json_attend(&l, '[');
        json_blancs(&l);
        if (*l.p != ']') {
          for (;;) {
            json_attend(&l, '{');
            char *motif = NULL;
            char **figes = NULL;
            int nfig = 0, capfig = 0;
            json_blancs(&l);
            if (*l.p != '}') {
              for (;;) {
                char *k = json_texte(&l);
                json_attend(&l, ':');
                if (strcmp(k, "motif") == 0) {
                  free(motif);
                  motif = json_texte(&l);
                } else if (strcmp(k, "figes") == 0) {
                  json_attend(&l, '[');
                  json_blancs(&l);
                  if (*l.p != ']') {
                    for (;;) {
                      char *f = json_texte(&l);
                      if (nfig >= capfig) {
                        capfig = capfig ? capfig * 2 : 4;
                        figes = realloc(figes, (size_t)capfig * sizeof *figes);
                      }
                      figes[nfig++] = f;
                      json_blancs(&l);
                      if (*l.p == ',') {
                        l.p++;
                        continue;
                      }
                      json_attend(&l, ']');
                      break;
                    }
                  } else {
                    l.p++;
                  }
                } else {
                  json_sauter(&l);
                }
                free(k);
                json_blancs(&l);
                if (*l.p == ',') {
                  l.p++;
                  continue;
                }
                json_attend(&l, '}');
                break;
              }
            } else {
              l.p++;
            }
            t->journal = grandir(t->journal, &t->capjourn, t->njourn, sizeof *t->journal);
            Etincelle *e = &t->journal[t->njourn++];
            e->motif = motif ? motif : dupstr("");
            e->figes = figes;
            e->nfig = nfig;
            json_blancs(&l);
            if (*l.p == ',') {
              l.p++;
              continue;
            }
            json_attend(&l, ']');
            break;
          }
        } else {
          l.p++;
        }
      } else if (strcmp(cle, "motifs") == 0) {
        json_attend(&l, '{');
        json_blancs(&l);
        if (*l.p != '}') {
          for (;;) {
            char *nom = json_texte(&l);
            json_attend(&l, ':');
            json_attend(&l, '[');
            char **mb = NULL;
            int nmb = 0, capmb = 0;
            json_blancs(&l);
            if (*l.p != ']') {
              for (;;) {
                char *w = json_texte(&l);
                if (nmb >= capmb) {
                  capmb = capmb ? capmb * 2 : 4;
                  mb = realloc(mb, (size_t)capmb * sizeof *mb);
                }
                mb[nmb++] = w;
                json_blancs(&l);
                if (*l.p == ',') {
                  l.p++;
                  continue;
                }
                json_attend(&l, ']');
                break;
              }
            } else {
              l.p++;
            }
            t->motifs = grandir(t->motifs, &t->capmotif, t->nmotif, sizeof *t->motifs);
            Motif *m = &t->motifs[t->nmotif++];
            m->nom = nom;
            m->membres = mb;
            m->imembres = malloc((size_t)(nmb > 0 ? nmb : 1) * sizeof *m->imembres);
            m->nmb = nmb;
            json_blancs(&l);
            if (*l.p == ',') {
              l.p++;
              continue;
            }
            json_attend(&l, '}');
            break;
          }
        } else {
          l.p++;
        }
      } else {
        json_sauter(&l);
      }
      free(cle);
      json_blancs(&l);
      if (*l.p == ',') {
        l.p++;
        continue;
      }
      json_attend(&l, '}');
      break;
    }
  } else {
    l.p++;
  }
  /* l'ancien tissu est remplacé (relire ne vérifie pas, comme Python) */
  (void)sauve;
  reindexer();
  free(buf);
  printf("tissu relu depuis %s\n", mots[1]);
}

/* ---------- exécution ---------- */

static void commande(int noligne, char **mots, int nmots) {
  char n[64] = "";
  if (strlen(mots[0]) < sizeof n)
    normer(mots[0], n);
  if (strcmp(n, "neurone") == 0)
    cmd_neurone(noligne, mots, nmots);
  else if (strcmp(n, "lien") == 0)
    cmd_lien(noligne, mots, nmots);
  else if (strcmp(n, "motif") == 0)
    cmd_motif(noligne, mots, nmots);
  else if (strcmp(n, "rencontre") == 0)
    cmd_rencontre(noligne, mots, nmots);
  else if (strcmp(n, "propager") == 0)
    cmd_propager(noligne, mots, nmots);
  else if (strcmp(n, "renforcer") == 0)
    cmd_renforcer(noligne, mots, nmots);
  else if (strcmp(n, "oublier") == 0)
    cmd_oublier(noligne, mots, nmots);
  else if (strcmp(n, "repos") == 0)
    cmd_repos(noligne, mots, nmots);
  else if (strcmp(n, "adapter") == 0)
    cmd_adapter(noligne, mots, nmots);
  else if (strcmp(n, "nettoyer") == 0)
    cmd_nettoyer(noligne, mots, nmots);
  else if (strcmp(n, "cise") == 0)
    cmd_cise(noligne, mots, nmots);
  else if (strcmp(n, "resonance") == 0)
    cmd_resonance(noligne, mots, nmots);
  else if (strcmp(n, "mesurer") == 0)
    cmd_mesurer(noligne, mots, nmots);
  else if (strcmp(n, "juger") == 0)
    cmd_juger(noligne, mots, nmots);
  else if (strcmp(n, "dire") == 0)
    cmd_dire(noligne, mots, nmots);
  else if (strcmp(n, "graver") == 0)
    cmd_graver(noligne, mots, nmots);
  else if (strcmp(n, "relire") == 0)
    cmd_relire(noligne, mots, nmots);
  else
    LEVER(noligne, "mot inconnu '%s' — voir LANGAGE-RATUM.md", mots[0]);
}

static int condition_si(int noligne, char **mots, int nmots) {
  char w2[64] = "", w4[64] = "";
  if (strlen(mots[2 < nmots ? 2 : 0]) < sizeof w2 && nmots > 2)
    normer(mots[2], w2);
  if (nmots > 4 && strlen(mots[4]) < sizeof w4)
    normer(mots[4], w4);
  if (nmots != 5 || strcmp(w2, "tient") != 0 || strcmp(w4, "alors") != 0)
    LEVER(noligne, "usage : si <motif> tient <seuil> alors");
  return resonance(mots[1]) >=
         entier(noligne, mots, nmots, 3, "si <motif> tient <seuil> alors");
}

static void executer(int debut, int fin) {
  int k = debut;
  while (k < fin) {
    int noligne = instr[k].noligne;
    char **mots = instr[k].mots;
    int nmots = instr[k].nmots;
    char n[64] = "";
    if (strlen(mots[0]) < sizeof n)
      normer(mots[0], n);
    if (strcmp(n, "tissu") == 0) {
      int finb = bloc_fin(k);
      cmd_tissu(noligne, mots, nmots);
      executer(k + 1, finb);
      k = finb + 1;
    } else if (strcmp(n, "repeter") == 0) {
      int finb = bloc_fin(k);
      int r = entier(noligne, mots, nmots, 1, "répéter <nombre>");
      for (int i = 0; i < r; i++)
        executer(k + 1, finb);
      k = finb + 1;
    } else if (strcmp(n, "si") == 0) {
      int finb = bloc_fin(k);
      int cond = condition_si(noligne, mots, nmots);
      int sin = bloc_sinon(k, finb);
      if (cond)
        executer(k + 1, sin >= 0 ? sin : finb);
      else if (sin >= 0)
        executer(sin + 1, finb);
      k = finb + 1;
    } else if (strcmp(n, "fin") == 0 || strcmp(n, "sinon") == 0) {
      LEVER(noligne, "'%s' sans bloc ouvert", mots[0]);
    } else {
      commande(noligne, mots, nmots);
      k++;
    }
  }
}

/* ---------- programme principal ---------- */

int main(int argc, char **argv) {
  if (argc != 2) {
    printf("usage : ratum-c programme.ratum\n");
    return 2;
  }
  FILE *fh = fopen(argv[1], "r");
  if (!fh) {
    printf("impossible de lire %s : %s\n", argv[1], strerror(errno));
    return 2;
  }
  decoupage(fh);
  fclose(fh);
  if (setjmp(echec)) {
    printf("ERREUR RATUM — %s\n", message_erreur);
    return 1;
  }
  executer(0, ninstr);
  printf("=== fin du programme ===\n");
  return 0;
}
