#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASSE BINAIRE — le même flot que generer_masse.iterer, en 3 octets/séquence.
RATISS Labs · MIT.

50 mots vrais -> index 0..49 (même ordre trié que le générateur : le flux
aléatoire est IDENTIQUE au JSONL, seed 7 = seed 7). Sans JSON : 3 octets
par séquence, chargeable en RAM d'un coup (100M = 300 Mo).

Usage : python3 education-massive/binaire_masse.py --n 30000000 --seed 7 --sortie masse.bin
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generer_masse import charger, iterer  # noqa: E402


def table():
    _, mots = charger()
    return mots, {m: i for i, m in enumerate(mots)}


def ecrire(n, seed, sortie):
    mots, idx = table()
    assert len(mots) <= 256, "trop de mots pour 1 octet"
    buf = bytearray()
    with open(sortie, "wb") as fh:
        for s in iterer(n, seed):
            buf += bytes([idx[m] for m in s["mots"]])
            if len(buf) >= 1 << 20:
                fh.write(buf)
                buf = bytearray()
        if buf:
            fh.write(buf)
    print(f"BINAIRE ÉCRIT — {n} séquences -> {sortie} (seed {seed}, {3 * n} octets)")


def lire_iter(entree, mots):
    with open(entree, "rb") as fh:
        while True:
            rec = fh.read(3)
            if len(rec) < 3:
                return
            yield [mots[rec[0]], mots[rec[1]], mots[rec[2]]]


def lire_ram(entree, mots):
    data = open(entree, "rb").read()
    n = len(data) // 3
    for i in range(n):
        o = 3 * i
        yield [mots[data[o]], mots[data[o + 1]], mots[data[o + 2]]]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30000000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--sortie", default="masse.bin")
    args = ap.parse_args(argv)
    ecrire(args.n, args.seed, args.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
