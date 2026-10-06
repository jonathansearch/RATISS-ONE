"""Outillage COUCHES : découpage macro/micro/info + dimension + synchronisation."""
import numpy as np
from ripser import ripser


def decouper(pts, n_tore=160, n_sphere=90):
    return {"macro": pts[:n_tore], "micro": pts[n_tore:n_tore + n_sphere],
            "info": pts[n_tore + n_sphere:]}


def p_couche(pts, seuil=0.05):
    if len(pts) < 4:
        return 0.0
    dgms = ripser(pts, maxdim=2)["dgms"]
    tot = 0.0
    for d in (1, 2):
        if d < len(dgms):
            for n, m in dgms[d]:
                if np.isfinite(m) and (m - n) > seuil:
                    tot += m - n
    return float(tot)


def dim_boites(pts, echelles=(0.1, 0.2, 0.4, 0.8)):
    mins = pts.min(0)
    ns = []
    for e in echelles:
        cols = ((pts - mins) / e).astype(int).T
        ns.append(len(set(zip(*[c.tolist() for c in cols]))))
    x = np.log([1.0 / e for e in echelles])
    return float(np.polyfit(x, np.log(ns), 1)[0])


def _hilbert(x):
    n = len(x)
    X = np.fft.fft(x)
    h = np.zeros(n)
    if n % 2 == 0:
        h[0] = h[n // 2] = 1
        h[1:n // 2] = 2
    else:
        h[0] = 1
        h[1:(n + 1) // 2] = 2
    return np.fft.ifft(X * h)


def plv(a, b):
    a = np.array(a, float) + np.random.default_rng(0).normal(0, 1e-9, len(a))
    b = np.array(b, float) + np.random.default_rng(1).normal(0, 1e-9, len(b))
    pa, pb = np.angle(_hilbert(a - a.mean())), np.angle(_hilbert(b - b.mean()))
    return float(np.abs(np.exp(1j * (pa - pb)).mean()))


def corr(a, b):
    c = np.corrcoef(a, b)[0, 1]
    return float(0.0 if np.isnan(c) else c)  # série constante = zéro corrélation
