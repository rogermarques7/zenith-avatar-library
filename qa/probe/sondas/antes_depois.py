#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""antes_depois.py - folhas de contato ANTES x DEPOIS de um lote de peca.

    python qa/probe/sondas/antes_depois.py [--depois qa/revisao/_s38]

ANTES  = qa/revisao/{id}/folha.png   (o entregue que ele julgou)
DEPOIS = {depois}/{id}/folha.png     (o entregue novo, mesmo enquadramento)

Uma linha por avatar, as duas folhas lado a lado (quadril em cima, faixa
embaixo no feminino). Tres avatares por imagem: defeito de borda e uma
DIFERENCA, e diferenca se ve lado a lado (LICOES 4.5m).
Saida: {depois}/_ab_{n}.png
"""
import argparse
import os

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--depois", default=os.path.join(ROOT, "qa", "revisao", "_s38"))
ap.add_argument("--por", type=int, default=3)
a = ap.parse_args()

ids = sorted(x for x in os.listdir(a.depois)
             if os.path.isfile(os.path.join(a.depois, x, "folha.png")))
W = 900
linhas = []
for aid in ids:
    ant = os.path.join(ROOT, "qa", "revisao", aid, "folha.png")
    if not os.path.isfile(ant):
        continue
    pa, pd = Image.open(ant).convert("RGB"), Image.open(os.path.join(a.depois, aid, "folha.png")).convert("RGB")
    s = W / pa.width
    pa = pa.resize((W, int(pa.height * s)))
    pd = pd.resize((W, int(pd.height * s)))
    r = Image.new("RGB", (2 * W + 10, max(pa.height, pd.height) + 26), (12, 12, 16))
    r.paste(pa, (0, 26))
    r.paste(pd, (W + 10, 26))
    d = ImageDraw.Draw(r)
    d.text((6, 6), aid + "   ANTES (entregue de 22-23/09)", fill=(255, 120, 120))
    d.text((W + 16, 6), aid + "   DEPOIS (borda viva, sessao 38)", fill=(120, 255, 140))
    linhas.append(r)
for k in range(0, len(linhas), a.por):
    g = linhas[k:k + a.por]
    o = Image.new("RGB", (g[0].width, sum(x.height for x in g)), (0, 0, 0))
    y = 0
    for x in g:
        o.paste(x, (0, y))
        y += x.height
    o.save(os.path.join(a.depois, "_ab_{:02d}.png".format(k // a.por + 1)))
print(len(linhas), "avatares ->", a.depois)
