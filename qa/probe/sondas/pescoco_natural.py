# -*- coding: utf-8 -*-
"""REGUA DO VALE DA ESTRANHEZA do pescoco: o estado morfado cabe na nuvem natural?

    python qa/probe/sondas/pescoco_natural.py --estados ARQ.json [--rotulo novo]
           [--base qa/pescoco/perfis_base.json] [--ids a,b,c]

`ARQ.json` sai do `pescoco_perfil.py` (com `--infs` ou com os estados Rp/Rm).
Para cada avatar e cada estado: a circunferencia nova (anel dos raios, minimo
da banda do pescoco, somado a do library.json) e CINCO descritores de forma, e
cada descritor e comparado com o que os corpos REAIS da colecao do mesmo tipo
(mesmo sexo, IMC vizinho, mesma definicao - os mesmos pesos do campo) tem
naquela circunferencia. Sai o desvio em sigmas dos vizinhos.

Existe pelo pedido de 01/10: "suba o slider do pescoco ao maximo e compare com
pessoas reais pra ver se nao cai no vale da estranheza". A colecao sao 103
corpos humanos plausiveis, de 29 a 74 cm de pescoco; um pescoco morfado que
fica fora da nuvem deles no MESMO tamanho e uma forma que nenhum corpo tem.
|z| > 2 e alarme; o render decide (LICOES 7.5).

Descritores (raio normalizado a 1,75 m, altura a partir do queixo):
  mandibula  lado acima do queixo / lado abaixo  - o degrau que some no "cano"
  queixo     frente acima / frente abaixo         - o angulo cervicomental
  nuca       nuca no pescoco / nuca no occipital
  trapezio   lado-tras na base / no pescoco       - a abertura da base
  secao      frente / lado no pescoco             - a forma do corte
"""
import argparse
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import pescoco_campo as pc  # noqa: E402

DESC = ["mandibula", "queixo", "nuca", "trapezio", "secao"]


def grade(hs, ths, e, chave, zq):
    R = np.array(e[chave], float) * 1000 * 1.75 / e["H"]
    def r(hq, angs):
        v = []
        for a in angs:
            j = int(np.argmin(np.abs(np.array(ths) - a)))
            col = R[:, j]
            ok = ~np.isnan(col)
            v.append(np.interp(hq, hs[ok] - zq, col[ok]))
        return float(np.mean(v))
    return r


def descritores(hs, ths, e, chave, zq):
    r = grade(hs, ths, e, chave, zq)
    lat = [60, 75, 90, 105, 120]
    return np.array([
        r(+0.015, lat) / r(-0.010, lat),
        r(+0.010, [0, 15]) / r(-0.010, [0, 15]),
        r(-0.010, [165, 180]) / r(+0.020, [165, 180]),
        r(-0.035, [135, 150, 165, 180]) / r(-0.010, [135, 150, 165, 180]),
        r(-0.010, [0, 15]) / r(-0.010, [75, 90, 105]),
    ])


def perimetro_min(hs, ths, e, chave):
    """Anel dos raios (poligono simetrico), minimo na banda 0,83-0,90."""
    R = np.array(e[chave], float)
    t = np.radians(ths)
    best = 1e9
    for i, h in enumerate(hs):
        if not (0.830 <= h <= 0.900) or np.isnan(R[i]).any():
            continue
        x, y = R[i] * np.sin(t), R[i] * np.cos(t)
        best = min(best, 2 * float(np.hypot(np.diff(x), np.diff(y)).sum()))
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--estados", required=True)
    ap.add_argument("--base", default="qa/pescoco/perfis_base.json")
    ap.add_argument("--rotulo", default="")
    ap.add_argument("--ids")
    ap.add_argument("--json", help="grava os z em arquivo")
    args = ap.parse_args()
    lib = {a["id"]: a for a in json.load(open(os.path.join(ROOT, "library.json"),
                                              encoding="utf8"))["avatars"]}
    B = json.load(open(os.path.join(ROOT, args.base), encoding="utf8"))
    S = json.load(open(os.path.join(ROOT, args.estados), encoding="utf8"))
    hs, ths = np.array(B["hs"]), B["ths"]

    nuvem = {}
    for aid, e in B["avatars"].items():
        zq = pc.queixo(hs, np.array(e["R0"], float))
        nuvem[aid] = (lib[aid]["circumferences_cm"]["neck"], descritores(hs, ths, e, "R0", zq))

    ids = args.ids.split(",") if args.ids else list(S["avatars"])
    saida = {}
    print("{:<15} {:>7} {:>6}  ".format("avatar", "estado", "cm")
          + " ".join("{:>9}".format(d) for d in DESC) + "   pior")
    for aid in ids:
        e = S["avatars"][aid]
        a = lib[aid]
        zq = pc.queixo(hs, np.array(e["R0"], float))
        grp = [x for x in nuvem if lib[x]["sex"] == a["sex"]]
        lb = np.log([lib[x]["measured_bmi"] for x in grp])
        d3 = np.array([lib[x]["definition"] == "d3" for x in grp])
        w = (np.exp(-0.5 * ((lb - math.log(a["measured_bmi"])) / pc.SIGMA_IMC) ** 2)
             * np.where(d3 == (a["definition"] == "d3"), 1.0, pc.PESO_OUTRA_DEF))
        X = np.array([nuvem[x][0] for x in grp])
        D = np.array([nuvem[x][1] for x in grp])
        xm = (w * X).sum() / w.sum()
        coef, sig = [], []
        for k in range(len(DESC)):
            ym = (w * D[:, k]).sum() / w.sum()
            b = (w * (X - xm) * (D[:, k] - ym)).sum() / (w * (X - xm) ** 2).sum()
            res = D[:, k] - (ym + b * (X - xm))
            coef.append((ym, b))
            sig.append(math.sqrt((w * res ** 2).sum() / w.sum()))
        p0 = perimetro_min(hs, ths, e, "R0")
        estados = ["R0"] + sorted([k for k in e if k.startswith("R@") or k in ("Rp", "Rm", "Rp1", "Rm1")])
        saida[aid] = {}
        for ch in estados:
            c = a["circumferences_cm"]["neck"] + (perimetro_min(hs, ths, e, ch) - p0) * 100
            dd = descritores(hs, ths, e, ch, zq)
            z = [(dd[k] - (coef[k][0] + coef[k][1] * (c - xm))) / sig[k] for k in range(len(DESC))]
            pior = DESC[int(np.argmax(np.abs(z)))]
            saida[aid][ch] = {"cm": round(c, 1), "z": [round(v, 2) for v in z]}
            print("{:<15} {:>7} {:>6.1f}  ".format(aid, ch.replace("R@", ""), c)
                  + " ".join("{:>+9.1f}".format(v) for v in z)
                  + "   {}{}".format(pior, "  <-- FORA" if max(abs(v) for v in z) > 2 else ""))
    if args.json:
        json.dump(saida, open(args.json, "w", encoding="utf8"), indent=1)


if __name__ == "__main__":
    main()
