#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""borda_viva_folha.py - risca as curvas do borda_viva.py sobre o clay e monta
UMA folha por avatar para o veredito dele.

    python qa/probe/sondas/borda_viva_folha.py            # tudo em qa/revisao/_viva
    python qa/probe/sondas/borda_viva_folha.py zen_f_b06i_d3 ...

Roda no Python do SISTEMA (o do Blender nao tem PIL).

    AZUL       a proposta: a borda do tecido lida nas arestas vivas
    VERMELHO   a tinta de hoje (o mapa)

Linha PONTILHADA de 1 px: a marca aponta sem tapar o relevo, que e o unico
dado da imagem (a primeira versao do bainha_rasante punha toro em 3D e comia
exatamente o degrau de 1 mm que queria mostrar). Cada vista sai tambem LIMPA
em `{regiao}_{ang}.png`, para abrir e conferir sem marca nenhuma.

Uma folha: linhas = regioes (barra, cos, faixa), colunas = 6 azimutes de
camera (0 = frente, 180 = costas). Cabecalho com o que o ajuste mediu por
borda - cobertura baixa e avatar para o olho, nao numero para gravar.
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
BASE = os.path.join(ROOT, "qa", "revisao", "_viva")
AZUL = (20, 110, 255)
VERM = (230, 30, 30)
TILE_W = 700


def risca(im, pts, cor, fase):
    """Pontilhado 2 px ligado / 2 px desligado ao longo da curva visivel.
    Salto grande entre pontos seguidos = pedaco escondido: nao liga por cima."""
    a = np.array(im)
    h, w = a.shape[:2]
    segs, seg = [], []
    for p in pts:
        if p is None or (seg and abs(p[0] - seg[-1][0]) + abs(p[1] - seg[-1][1]) > 40):
            segs.append(seg)
            seg = []
        if p is not None:
            seg.append(p)
    segs.append(seg)
    for seg in segs:
        if len(seg) < 2:
            continue
        s = np.array(seg)
        L = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(s, axis=0).T))])
        for t in np.arange(fase, L[-1], 1.0):
            if int(t) % 4 >= 2:
                continue
            xi = int(round(np.interp(t, L, s[:, 0])))
            yi = int(round(np.interp(t, L, s[:, 1])))
            if 0 <= xi < w and 0 <= yi < h:
                a[yi, xi] = cor
    return Image.fromarray(a)


def uma(aid):
    d = os.path.join(BASE, aid)
    with open(os.path.join(d, "proposta.json"), encoding="utf-8") as f:
        P = json.load(f)
    if "vistas" not in P:
        print(aid, "sem render")
        return None
    linhas = []
    for reg, vistas in P["vistas"].items():
        tiles = []
        for png, px in vistas.items():
            im = Image.open(os.path.join(d, png)).convert("RGB")
            for borda, cc in px.items():
                if "proposta" in cc:
                    im = risca(im, cc["proposta"], AZUL, 0)
                im = risca(im, cc["atual"], VERM, 0)
            im.save(os.path.join(d, "marcado_" + png))
            s = TILE_W / im.width
            t = im.resize((TILE_W, int(im.height * s)), Image.LANCZOS)
            dr = ImageDraw.Draw(t)
            dr.text((8, 6), "{} {}".format(reg, png.split("_")[1][:3]), fill=(255, 255, 0))
            tiles.append(t)
        row = Image.new("RGB", (TILE_W * len(tiles), tiles[0].height), (20, 20, 20))
        for i, t in enumerate(tiles):
            row.paste(t, (i * TILE_W, 0))
        linhas.append(row)
    cab = 64
    W = max(r.width for r in linhas)
    Ht = cab + sum(r.height for r in linhas)
    out = Image.new("RGB", (W, Ht), (12, 12, 16))
    dr = ImageDraw.Draw(out)
    txt = ["{}   AZUL = borda do tecido (arestas vivas)   VERMELHO = tinta de hoje".format(aid)]
    partes = []
    for nome, b in P["bordas"].items():
        if b.get("falhou"):
            partes.append("{}: FALHOU".format(nome))
        else:
            partes.append("{}: {:+.1f}..{:+.1f} cm  cob {:.0%}  {:.0f}graus".format(
                nome, b["delta_cm"][0], b["delta_cm"][1], b["cobertura"], b["limiar"]))
    txt.append("   ".join(partes))
    for i, t in enumerate(txt):
        dr.text((10, 8 + 24 * i), t, fill=(235, 235, 235))
    y = cab
    for r in linhas:
        out.paste(r, (0, y))
        y += r.height
    dst = os.path.join(BASE, "_folha_{}.png".format(aid))
    out.save(dst)
    print(dst)
    return dst


ids = sys.argv[1:] or sorted(x for x in os.listdir(BASE)
                             if os.path.isdir(os.path.join(BASE, x)))
for _a in ids:
    uma(_a)
