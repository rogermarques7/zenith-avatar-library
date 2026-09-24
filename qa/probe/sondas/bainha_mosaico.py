#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bainha_mosaico.py - marca os 103 clays e monta folhas de contato.

    python qa/probe/sondas/bainha_mosaico.py            # marca + mosaico dos 103
    python qa/probe/sondas/bainha_mosaico.py --vista obliqua

Roda depois de `bainha_rasante.py --todos`. Saida em
qa/revisao/_hem/_mosaico_{vista}_NN.png, 6 avatares por imagem.

--------------------------------------------------------------------------
POR QUE ISTO EXISTE (23/09, sessao 37)
--------------------------------------------------------------------------
Na madrugada eu declarei "mecanismo da bainha provado" depois de olhar a imagem
de TRES avatares, e apresentei isso ao lado de uma medida feita nos 103. O
Rogerio leu a revisao e perguntou, com razao: *"vc realmente fez uma varredura
em todos os corpos? parece que vc nao ta enxergando os corpos, ta tentando
corrigir no escuro."*

A distincao que faltava, e que vale mais que o conserto:

> MEDIR os 103 nao e OLHAR os 103. Uma estatistica sobre a serie prova que o
> defeito EXISTE e diz o tamanho medio dele; ela nao diz em QUAIS corpos, nem
> com que cara. Enquanto o veredito for visual - e neste projeto ele sempre e -
> a varredura tem de terminar numa IMAGEM DE TODOS, nao num numero sobre todos.

E olhar 103 PNGs em sequencia tambem nao funciona: defeito de borda e uma
diferenca, e diferenca se ve lado a lado. Dai a folha de contato - a mesma
razao que fez nascer o `morph_folha.py` e o `revisao_peca.py --mosaico`.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
BASE = os.path.join(ROOT, "qa", "revisao", "_hem")

ap = argparse.ArgumentParser()
ap.add_argument("--vista", default="frente")
ap.add_argument("--por-imagem", type=int, default=6)
ap.add_argument("--larg", type=int, default=560)
a = ap.parse_args()


def marca(aid, vista, dest_wh=None):
    """Risca a linha do mapa (vermelha) e a da folha (verde).

    Deixa o MEIO limpo de proposito: a marca aponta a altura sem tapar a
    regiao medida - a primeira versao desenhava um toro em 3D e ele comia o
    relevo de 1 mm que a sonda existe para mostrar.

    ⚠️ `dest_wh` faz a marca ser desenhada DEPOIS do redimensionamento. Uma
    linha de 1 px riscada em 1100x900 e depois reduzida para 560 px vira um
    cinza de 50% e some no clay claro - na primeira folha de contato a linha do
    mapa simplesmente nao existia, e uma marca que some numa folha de varredura
    e pior que marca nenhuma, porque a folha parece completa."""
    d = os.path.join(BASE, aid)
    mp = os.path.join(d, "rasante_marcas.json")
    src = os.path.join(d, "rasante_" + vista + ".png")
    if not (os.path.isfile(mp) and os.path.isfile(src)):
        return None
    with open(mp, encoding="utf-8") as f:
        mk = json.load(f)
    im0 = Image.open(src).convert("RGB")
    esc = 1.0
    if dest_wh:
        esc = dest_wh[1] / float(im0.height)
        im0 = im0.resize(dest_wh, Image.LANCZOS)
    im = np.asarray(im0).copy()
    h, w = im.shape[:2]

    # ---- AZUL: o vinco medido no pixel (bainha_pixel.py) -------------------
    # Desenhado COLUNA A COLUNA, sem alisar, de proposito: e a medida crua que
    # tem de ser julgada. Se o azul montar no vinco nas 103, a medida vale; se
    # escorregar, aparece aqui e nao dentro de um GLB ja gravado.
    pj = os.path.join(d, "pixel_" + vista + ".json")
    if os.path.isfile(pj):
        with open(pj, encoding="utf-8") as f:
            px = json.load(f)
        ys = px["y_por_coluna"]
        vale = px.get("vale") or [True] * len(ys)
        for xi in range(w):
            j = int(round(xi / esc)) if esc != 1.0 else xi
            if not (0 <= j < len(ys)) or not vale[j]:
                continue
            y = int(round(ys[j] * esc))
            if 0 <= y < h - 1:
                im[y:y + 2, xi] = [40, 120, 255]
    for i, (_rot, (y0, cor)) in enumerate(sorted(mk["marcas"].items())):
        y = int(round(y0 * esc))
        if not (1 <= y < h - 1):
            continue
        im[y:y + 2, :w // 5] = cor
        im[y:y + 2, -w // 5:] = cor
        x = w // 5 + 3 + i * 7
        im[max(0, y - 5):min(h, y + 6), x:x + 2] = cor
    out = Image.fromarray(im)
    if not dest_wh:
        out.save(os.path.join(d, "marcado_" + vista + ".png"))
    return out, mk


def main():
    ids = sorted(d for d in os.listdir(BASE)
                 if os.path.isdir(os.path.join(BASE, d)) and d.startswith("zen_"))
    cw = a.larg
    ch = None
    feitos = []
    for aid in ids:
        if ch is None:
            r0 = marca(aid, a.vista)
            if r0 is None:
                continue
            ch = int(cw * r0[0].height / r0[0].width)
        r = marca(aid, a.vista, dest_wh=(cw, ch))
        if r is not None:
            feitos.append((aid, r[0], r[1]))
    if not feitos:
        print("nada marcado - rodou o bainha_rasante.py --todos?")
        return 1

    cols, linhas = 3, (a.por_imagem + 2) // 3
    rot = 22
    n = 0
    for k in range(0, len(feitos), a.por_imagem):
        lote = feitos[k:k + a.por_imagem]
        W, H = cols * cw, linhas * (ch + rot)
        folha = Image.new("RGB", (W, H), (16, 16, 20))
        dr = ImageDraw.Draw(folha)
        for i, (aid, im, mk) in enumerate(lote):
            x, y = (i % cols) * cw, (i // cols) * (ch + rot)
            folha.paste(im, (x, y + rot))
            hf = mk["hem_folha_zh"]
            dr.text((x + 6, y + 5), "{}   mapa {:.4f}{}".format(
                aid, mk["hem_mapa_zh"],
                "" if hf is None else "   folha {:.4f}  d{:+.4f}".format(
                    hf, mk["hem_mapa_zh"] - hf)), fill=(235, 235, 240))
        n += 1
        p = os.path.join(BASE, "_mosaico_{}_{:02d}.png".format(a.vista, n))
        folha.save(p)
        print("->", os.path.relpath(p, ROOT))
    print("{} avatares em {} folhas".format(len(feitos), n))
    return 0


sys.exit(main())
