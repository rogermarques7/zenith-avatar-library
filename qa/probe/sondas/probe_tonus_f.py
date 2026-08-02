#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_tonus_f.py - mede RELEVO (tonus) na folha, nao largura.

Na sessao 7 a regua de silhueta disse "o mesmo corpo" entre duas folhas que
diferiam em gomos abdominais: ela mede LARGURA e o que mudou era TONUS. Esta
sonda faz a pergunta que faltava - o quanto a superficie ondula.

Metodo: segunda derivada da luminancia ao longo de cada linha, na faixa
central do corpo. Superficie lisa -> perto de zero. Gomo abdominal, linha alba
e separacao muscular -> picos. So compara folhas do MESMO gerador com a MESMA
luz (mesma restricao da regra 5c).

Uso: python qa/probe/sondas/probe_tonus_f.py "<folha A>" "<folha B>" ...
"""

import sys
import numpy as np
from PIL import Image

import probe_folha_f as pf

REGIOES = [("abdomen ", 0.335, 0.410, 0.22),
           ("peitoral", 0.245, 0.300, 0.26),
           ("coxas   ", 0.575, 0.660, 0.42)]


def medir(path):
    img = np.asarray(Image.open(path).convert("L")).astype(float)
    f = pf.figuras(path)[0]
    alt, y0, xoff = f["alt"], f["y0"], f["x0"]
    cols = np.flatnonzero(f["sub"][y0 + int(0.28 * alt)])
    eixo = int(np.median(cols))

    print("\n== {}".format(path.replace("/", "\\").split("\\")[-1]))
    out = {}
    for nome, a, b, meia_frac in REGIOES:
        vals = []
        for t in np.arange(a, b, 0.002):
            y = y0 + int(t * alt)
            cs = pf.corridas(f["sub"][y])
            alvo = next(((x0, x1) for x0, x1 in cs if x0 <= eixo <= x1), None)
            if alvo is None:
                continue
            x0, x1 = alvo
            larg = x1 - x0 + 1
            if larg < 40:
                continue
            c = (x0 + x1) // 2
            meia = max(8, int(larg * meia_frac))
            faixa = img[y, xoff + c - meia: xoff + c + meia]
            if faixa.size < 16:
                continue
            vals.append(float(np.abs(np.diff(faixa, 2)).mean()))
        if not vals:
            print("   {}: sem linha util".format(nome))
            continue
        out[nome.strip()] = float(np.mean(vals))
        print("   {}: relevo {:.3f}   (p90 {:.3f}, {} linhas)".format(
            nome, out[nome.strip()], float(np.percentile(vals, 90)), len(vals)))
    return out


if __name__ == "__main__":
    res = [(p, medir(p)) for p in sys.argv[1:]]
    if len(res) == 2:
        print("\n== DELTA de relevo (B - A), em % do valor de A")
        for k in res[0][1]:
            a, b = res[0][1][k], res[1][1].get(k)
            if b is not None:
                print("   {:8s}: {:+6.1f}%   ({:.3f} -> {:.3f})".format(k, 100.0 * (b - a) / a, a, b))
