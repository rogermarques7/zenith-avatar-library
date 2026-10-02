# -*- coding: utf-8 -*-
"""As PESSOAS REAIS (test/pessoas_reais.json) contra avatar escolhido + morph.

    python qa/probe/sondas/pessoas_reais.py [--mapa config/morph_map.json]

Mesma regra do app: select.py escolhe o corpo, morph_cases.solve() decide as
influences, e o centimetro alcancado sai da CURVA publicada no mapa. Imprime o
resto por coluna e o RMS antes/depois. Era rodado a mao ate a sessao 41.
"""
import argparse
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import morph_cases as mc  # noqa: E402
import importlib  # noqa: E402
sel = importlib.import_module("select")  # scripts/select.py, nao o modulo da stdlib
if not hasattr(sel, "select") or not hasattr(sel, "load_index"):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import importlib.util as _u
    spec = _u.spec_from_file_location("zselect", os.path.join(ROOT, "scripts", "select.py"))
    sel = _u.module_from_spec(spec)
    spec.loader.exec_module(sel)


def cm_da_curva(curve, inf):
    pts = sorted(curve)
    if inf <= pts[0][0]:
        return pts[0][1]
    if inf >= pts[-1][0]:
        return pts[-1][1]
    for (a, ca), (b, cb) in zip(pts, pts[1:]):
        if a <= inf <= b:
            return ca + (inf - a) / (b - a) * (cb - ca) if b > a else ca
    return pts[-1][1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapa", default="config/morph_map.json")
    args = ap.parse_args()
    idx = sel.load_index(os.path.join(ROOT, "library.json"))
    mapa = json.load(open(os.path.join(ROOT, args.mapa), encoding="utf8"))
    pessoas = json.load(open(os.path.join(ROOT, "test", "pessoas_reais.json"),
                             encoding="utf8"))["pessoas"]
    fmap = idx["selection"]["app_field_map"]
    av = {a["id"]: a for a in idx["avatars"]}
    for p in pessoas:
        h = p["height_cm"] / 100.0
        r = sel.select(idx, p["sex"], h, p["weight_kg"], p["measures"])
        a = av[r["id"]]
        k = mc.REF_HEIGHT_M / h
        medidas = {}
        for app_key, v in p["measures"].items():
            col = fmap.get(app_key)
            if col:
                medidas[col] = v
        infl = mc.solve(mapa[a["id"]], h, medidas, r["columns_used"])
        antes, depois, linha = [], [], []
        for m in mapa[a["id"]]["morphs"]:
            col = m.get("column")
            if not col or col not in medidas:
                continue
            alvo = medidas[col] * k
            d0 = alvo - m["base_cm"]
            ganho = cm_da_curva(m["curve"], infl.get(m["key"], 0.0))
            antes.append(d0)
            depois.append(d0 - ganho)
            linha.append("{} {:+.1f} (inf {:+.2f})".format(col, d0 - ganho, infl.get(m["key"], 0.0)))
        rms = lambda xs: math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else 0.0
        print("{} -> {} [{}, IMC {}]".format(p["nome"], a["id"], a["definition"], a["measured_bmi"]))
        print("  resto depois do morph: " + " | ".join(linha))
        print("  erro RMS: antes {:.1f} cm -> depois {:.1f} cm\n".format(rms(antes), rms(depois)))


if __name__ == "__main__":
    main()
