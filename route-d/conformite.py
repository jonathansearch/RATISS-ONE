#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROUTE D — conformité : le C sort EXACTEMENT comme le Python, au caractère près.
RATISS Labs · MIT.

Compile route-d/ratum.c (zéro warning toléré : -Wall -Wextra), rejoue les 24
programmes du corpus avec les deux berceaux, compare sorties + codes octet par
octet — plus le scroll mem.scroll (j04) : le JSON doit être identique lui aussi.

Usage : python3 route-d/conformite.py
Sortie : CONFORMITE OK — 24/24 sorties identiques (+ scroll identique).
"""
import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
from tests_verdicts import CAS, reconstruire_ecoute, regenerer_vocabulaire  # noqa: E402

C_SRC = os.path.join(RACINE, "route-d", "ratum.c")
C_BIN = os.path.join(RACINE, "route-d", "ratum-c")
SCROLL = os.path.join(RACINE, "jouets", "mem.scroll")


def compiler():
    proc = subprocess.run(
        ["gcc", "-O2", "-Wall", "-Wextra", "-o", C_BIN, C_SRC],
        capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode != 0:
        print(f"ÉCHEC compilation :\n{proc.stderr}")
        return False
    if "warning" in proc.stderr.lower():
        print(f"WARNINGS REFUSÉS :\n{proc.stderr}")
        return False
    print("OK : ratum.c compilé (-O2 -Wall -Wextra, zéro warning)")
    return True


def jouer(cmd, prog):
    try:
        os.remove(SCROLL)
    except OSError:
        pass
    proc = subprocess.run(cmd + [prog], capture_output=True, cwd=RACINE)
    scroll = None
    if os.path.exists(SCROLL):
        with open(SCROLL, "rb") as fh:
            scroll = fh.read()
        os.remove(SCROLL)
    return proc.returncode, proc.stdout, scroll


def main():
    if not compiler():
        return 1
    if not reconstruire_ecoute() or not regenerer_vocabulaire():
        print("ÉCHEC : régénération du corpus")
        return 1
    print(f"OK : corpus régénéré ({len(CAS)} programmes)")
    ecarts, scrolls = 0, 0
    for prog in CAS:
        code_py, out_py, scroll_py = jouer([sys.executable, "ratum.py"], prog)
        code_c, out_c, scroll_c = jouer([C_BIN], prog)
        if code_py == code_c and out_py == out_c:
            extra = ""
            if scroll_py is not None or scroll_c is not None:
                if scroll_py == scroll_c and scroll_py is not None:
                    scrolls += 1
                    extra = " + scroll identique"
                else:
                    extra = " mais SCROLL DIFFÉRENT"
                    ecarts += 1
            print(f"OK : {prog} ({len(out_py)} octets identiques{extra})")
        else:
            ecarts += 1
            print(f"ÉCART : {prog} (codes {code_py}/{code_c}, "
                  f"{len(out_py)}/{len(out_c)} octets)")
            for i, (a, b) in enumerate(zip(out_py.split(b"\n"), out_c.split(b"\n"))):
                if a != b:
                    print(f"  ligne {i + 1} :\n    py : {a[:120]!r}\n    c  : {b[:120]!r}")
                    break
    print(f"CONFORMITE {'OK' if ecarts == 0 else 'KO'} — "
          f"{len(CAS) - ecarts}/{len(CAS)} sorties identiques"
          + (f" (+ {scrolls} scroll identique)" if scrolls else ""))
    return 0 if ecarts == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
