#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""foto_medidas.py - estima circunferencias em CM a partir de duas fotos
(frente e perfil) de uma pessoa, com a altura real como ancora.

    python qa/probe/sondas/foto_medidas.py --frente f.jpg --perfil p.jpg --altura 176

POR QUE ISTO PODE EXISTIR, DEPOIS DE 0 DE 5
    O `LICOES.md` 2.6 mata prever corpo em cm a partir de FOLHA 2D gerada, e
    continua valendo: la nao ha escala nenhuma, e o gerador inventa proporcao.
    Aqui e diferente em duas coisas - a foto e de uma pessoa real, e existe uma
    ANCORA de comprimento verdadeiro (a altura). Com ancora, a escala deixa de
    ser chute.

    O que continua sendo estimativa e a CIRCUNFERENCIA: a foto da largura e
    profundidade, e o perimetro sai de um modelo de elipse. Cintura humana e
    mais achatada que elipse, entao o numero tende a sair BAIXO. Por isso o
    script imprime a comparacao com a fita quando ela e informada - sem essa
    regua externa, o resultado nao deve ser usado para decidir nada.

⚠️ TRES VIESES CONHECIDOS, todos na mesma direcao (medida sai baixa):
    1. CABELO entra na estatura. A ancora fica maior que 176 e a escala
       px/cm sobe, encolhendo tudo. ~1-2%.
    2. O braco encosta no tronco no quadril e some da corrida central.
    3. Elipse subestima secao achatada.
"""

import argparse
import math
import os

import numpy as np
from PIL import Image

# As MESMAS alturas do metrics.py - medir noutro lugar nao seria comparavel.
FRACS = {
    "neck":      ("min", 0.830, 0.900),
    "shoulder":  ("fix", 0.795, None),
    "chest":     ("fix", 0.720, None),
    "waist_min": ("min", 0.550, 0.680),
    "hip":       ("max", 0.470, 0.550),
    "thigh":     ("max", 0.400, 0.462),
    "calf":      ("max", 0.170, 0.265),
}


def mascara(path):
    """Pele (saturada) + short/cabelo (escuro). Medido nestas fotos: pele S~88,
    ladrilho S=6, rejunte S=14, parede S=3 - o limiar em 40 separa com folga."""
    hsv = np.asarray(Image.open(path).convert("HSV")).astype(float)
    S, V = hsv[:, :, 1], hsv[:, :, 2]
    return (S > 40) | (V < 100)


def corridas(l):
    c = np.flatnonzero(l)
    if not len(c):
        return []
    q = np.flatnonzero(np.diff(c) > 1)
    ini = np.concatenate([[0], q + 1]); fim = np.concatenate([q, [len(c) - 1]])
    return [(int(c[a]), int(c[b])) for a, b in zip(ini, fim)]


def corpo(path, ignora_ate_x=0):
    m = mascara(path)
    m[:, :ignora_ate_x] = False          # tira a fita metrica da conta
    # maior faixa continua de linhas com corpo
    lin = m.sum(axis=1)
    ys = np.flatnonzero(lin > 25)
    gr, ini, ant = [], ys[0], ys[0]
    for y in ys[1:]:
        if y - ant > 15:
            gr.append((ini, ant)); ini = y
        ant = y
    gr.append((ini, ant))
    y0, y1 = max(gr, key=lambda g: g[1] - g[0])
    return m, y0, y1


def largura(m, y, central, eixo):
    r = corridas(m[y])
    if not r:
        return 0.0
    if central:
        dentro = [t for t in r if t[0] <= eixo <= t[1]]
        t = dentro[0] if dentro else max(r, key=lambda t: t[1] - t[0])
    else:
        t = (r[0][0], r[-1][1])
    return float(t[1] - t[0] + 1)


def perfilar(path, altura_cm, central, ignora_ate_x=0):
    m, y0, y1 = corpo(path, ignora_ate_x)
    pxcm = (y1 - y0) / altura_cm
    eixo = float(np.median(np.flatnonzero(m[y0:y1].any(axis=0))))
    larg = np.array([largura(m, y, central, eixo) for y in range(y0, y1 + 1)])
    return {"y0": y0, "y1": y1, "pxcm": pxcm, "larg": larg, "H": y1 - y0}


def em(d, frac):
    """indice do perfil na fracao da estatura (0 = pes, 1 = topo)"""
    return int(round((1.0 - frac) * d["H"]))


def extremo(d, modo, f0, f1):
    i0, i1 = em(d, f1), em(d, f0)
    b = d["larg"][i0:i1 + 1]
    b = b[b > 0]
    if not len(b):
        return None
    return float(b.min() if modo == "min" else b.max())


def elipse(a_cm, b_cm):
    """Perimetro de elipse (Ramanujan). a,b sao os SEMI-eixos."""
    if a_cm <= 0 or b_cm <= 0:
        return None
    h = ((a_cm - b_cm) / (a_cm + b_cm)) ** 2
    return math.pi * (a_cm + b_cm) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frente", required=True)
    ap.add_argument("--perfil", required=True)
    ap.add_argument("--altura", type=float, required=True, help="cm")
    ap.add_argument("--corta-x-frente", type=int, default=0)
    ap.add_argument("--corta-x-perfil", type=int, default=0)
    ap.add_argument("--fita", nargs="*", default=[],
                    help="coluna=cm para conferir, ex.: waist_min=107.5 calf=36")
    args = ap.parse_args()

    fita = {}
    for t in args.fita:
        k, v = t.split("=")
        fita[k] = float(v)

    F = perfilar(args.frente, args.altura, True, args.corta_x_frente)
    P = perfilar(args.perfil, args.altura, False, args.corta_x_perfil)
    print("frente: %d px de estatura -> %.2f px/cm" % (F["H"], F["pxcm"]))
    print("perfil: %d px de estatura -> %.2f px/cm" % (P["H"], P["pxcm"]))
    print()
    print("%-11s %9s %9s %11s %10s %9s"
          % ("coluna", "larg_cm", "prof_cm", "circ_est", "fita", "erro"))
    for col, (modo, f0, f1) in FRACS.items():
        if modo == "fix":
            lf = extremo(F, "max", f0 - 0.004, f0 + 0.004)
            lp = extremo(P, "max", f0 - 0.004, f0 + 0.004)
        else:
            lf = extremo(F, modo, f0, f1)
            lp = extremo(P, modo, f0, f1)
        if not lf or not lp:
            continue
        w, dp = lf / F["pxcm"], lp / P["pxcm"]
        c = elipse(w / 2, dp / 2)
        ref = fita.get(col)
        print("%-11s %9.1f %9.1f %11.1f %10s %9s"
              % (col, w, dp, c,
                 "%.1f" % ref if ref else "-",
                 "%+.1f" % (c - ref) if ref else "-"))


if __name__ == "__main__":
    main()
