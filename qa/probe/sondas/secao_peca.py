#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""secao_peca.py - centro e raio da secao, por perna e no tronco.

    blender -b -P qa/probe/sondas/secao_peca.py

Grava `qa/probe/secao_peca.json` com, para cada avatar:

    hem: {l: [cx, cy, R], r: [...]}   na altura da bainha do mapa
    cos: {t: [cx, cy, R]}             na altura do topo do cos

E o que o `bainha_anel.py` precisa para converter COLUNA DE PIXEL em AZIMUTE.

--------------------------------------------------------------------------
POR QUE NAO SAI DA SILHUETA DA IMAGEM (23/09, sessao 37)
--------------------------------------------------------------------------
Numa projecao ortografica as bordas da perna sao exatamente `cx +- R`, entao a
silhueta daria os dois numeros de graca - e era assim na primeira versao. Nao
funciona: no enquadramento de 0.22 da altura a coxa de um corpo largo SAI DO
QUADRO. Medido no `zen_m_b09h_d1`, a corrida da perna esquerda comeca na coluna
0, ou seja a borda externa nao esta na imagem, e `cx`/`R` saem errados sem
avisar.

Alargar o quadro resolveria e custaria ~4 h de render nas quatro passadas. A
malha custa 10 min e e mais exata. E a independencia que importa continua de
pe: a ALTURA do vinco - que e a medida que vai corrigir o detector - continua
saindo da imagem. Da malha vem so a geometria da secao, que nao e o que esta
sendo corrigido.
"""
import json
import math
import os
import sys

import bpy
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

FATIA_ZH = 0.006      # +-1 cm em volta da altura pedida


def secao(co, sel, z_alvo, H, z0):
    """(cx, cy, a, b) da secao horizontal: centro e SEMI-EIXOS em x e y.

    ⚠️ Nao basta um raio. O `w_field` mede o azimute do COS em volta da ORIGEM
    (`arctan2(y, x)`), e a secao do tronco nao esta centrada na origem nem e
    circular - e uma elipse achatada, com `a/b` indo de 1,0 a 1,45 no acervo
    (a §7.19 ja media isso para a cintura). Com um raio so, a coluna de pixel
    vira um azimute errado justamente nos setores de lado, que sao os que
    separam frente de costas.

    Com os dois semi-eixos a conta fecha: dado X, a profundidade da superficie
    frontal e `cy - b*sqrt(1 - ((X-cx)/a)^2)`, e dai sai o azimute de verdade."""
    zc = z0 + z_alvo * H
    m = sel[np.abs(co[sel, 2] - zc) < FATIA_ZH * H]
    if m.size < 40:
        return None
    cx, cy = float(co[m, 0].mean()), float(co[m, 1].mean())
    a = float(np.percentile(np.abs(co[m, 0] - cx), 98))
    b = float(np.percentile(np.abs(co[m, 1] - cy), 98))
    return [round(cx, 5), round(cy, 5), round(a, 5), round(b, 5)]


def main():
    with open(os.path.join(ROOT, "config", "shorts_map.json"), encoding="utf-8") as f:
        smap = json.load(f)
    out = {}
    for i, aid in enumerate(sorted(smap), 1):
        master = os.path.join(ROOT, "02_master", aid + "_master.glb")
        if not os.path.isfile(master):
            continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=master)
        ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
        me = ob.data
        n = len(me.vertices)
        co = np.empty(n * 3, dtype=np.float64)
        me.vertices.foreach_get("co", co)
        co = co.reshape(n, 3)
        z0 = float(co[:, 2].min())
        H = float(co[:, 2].max() - z0)
        crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)

        lids = [0, 1]
        mx = [float(co[leg_id == l, 0].mean()) if (leg_id == l).any() else 0.0
              for l in lids]
        if mx[0] > mx[1]:
            lids.reverse()

        e = smap[aid]
        hm = e["hem_l_zh"]
        hm = hm[0] if isinstance(hm, list) else float(hm)
        w = e["waist_zh"]
        cz = max(w) if isinstance(w, list) else float(w)

        d = {"H": round(H, 5), "z0": round(z0, 5), "hem": {}, "cos": {}}
        for lado, lid in zip("lr", lids):
            s = secao(co, np.where(leg_id == lid)[0], hm, H, z0)
            if s:
                d["hem"][lado] = s
        # o cos e um anel em volta do TRONCO, nao da perna
        tronco = np.where(~is_arm)[0]
        s = secao(co, tronco, cz, H, z0)
        if s:
            d["cos"]["t"] = s
        out[aid] = d
        print("[{}/{}] {}  hem {} cos {}".format(i, len(smap), aid,
                                                 list(d["hem"]), list(d["cos"])))
    p = os.path.join(ROOT, "qa", "probe", "secao_peca.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("->", p)


main()
