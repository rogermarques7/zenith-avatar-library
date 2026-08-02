#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cache_bainha.py - grava o PERFIL DE ANEL DA PERNA dos 39, para iterar a
janela da bainha sem reabrir o Blender.

    blender --background --python qa/probe/sondas/cache_bainha.py

Mesmo motivo do scripts/cache_maps.py, so que para a BAINHA: o cache de la
guarda o mapa do TRONCO (cos) e nao serve aqui. Uma passada de --fit --all custa
~25 min; o mapa de concavidade e sempre o mesmo para um master que nao mudou.

DUAS selecoes de perna por avatar, e a diferenca entre elas e o defeito:

  producao : leg_id do w_limbs, que so rotula perna ABAIXO da altura em que as
             duas se separam. Num corpo pesado as coxas se tocam bem abaixo da
             virilha anatomica, entao a janela HEM_BELOW_CROTCH cai num trecho
             SEM VERTICE DE PERNA, w_peaks volta vazio e a bainha vira chute
             (LICOES.md 4.3 - o chute nao se anuncia).
  x-sign   : perna = sinal de x, ate um teto generoso acima da virilha
             detectada. E a selecao que resolveu o zen_m_b12_d1 na sessao 6.

Grava qa/probe/hem/{id}.npz com os dois perfis, em Z_BINS bins de altura.
"""
import glob
import json
import os
import sys

import bpy
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

OUT = os.path.join(ROOT, "qa", "probe", "hem")
os.makedirs(OUT, exist_ok=True)

smap = S.load_map(ROOT)
ids = sorted(smap)

for aid in ids:
    master = os.path.join(ROOT, "02_master", aid + "_master.glb")
    if not os.path.isfile(master):
        print("SKIP {} sem master".format(aid))
        continue

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=master)
    me = [o for o in bpy.context.scene.objects if o.type == "MESH"][0].data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    H = co[:, 2].max() - co[:, 2].min()
    zh = co[:, 2] / H

    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
    ov = smap[aid].get("crotch_override_zh")
    crotch_zh = float(ov) if ov else crotch / H

    k, _ = S.w_curvature(me, np)
    kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)

    # --- selecao de producao (leg_id), na ordem esquerda/direita do w_fit -----
    lids = [0, 1]
    mx = [float(co[leg_id == l, 0].mean()) if (leg_id == l).any() else 0.0
          for l in lids]
    if mx[0] > mx[1]:
        lids.reverse()
    prod = []
    for lid in lids:
        sel = np.where(leg_id == lid)[0]
        _A, ring, _o = S.w_ring_map(np, co, kn, sel, H, "slice")
        prod.append(ring)

    # --- selecao por sinal de x, ate 0.10 da altura ACIMA da virilha ---------
    # O teto precisa passar da virilha porque nos IMC 100+ a bainha real fica
    # ACIMA da altura em que o w_limbs separa as pernas (b11_d1: separa em
    # 0.332, folha poe a bainha em 0.342).
    teto = crotch_zh + 0.10
    xs = []
    for lado in (co[:, 0] < 0, co[:, 0] >= 0):
        sel = np.where(lado & (~is_arm) & (zh < teto) & (zh > teto - 0.30))[0]
        _A, ring, _o = S.w_ring_map(np, co, kn, sel, H, "slice")
        xs.append(ring)

    np.savez_compressed(
        os.path.join(OUT, aid + ".npz"),
        prod_l=prod[0].astype(np.float32), prod_r=prod[1].astype(np.float32),
        xs_l=xs[0].astype(np.float32), xs_r=xs[1].astype(np.float32),
        meta=np.array([crotch_zh, crotch / H, teto, H], dtype=np.float64))
    print("HEM " + json.dumps({"id": aid, "crotch_zh": round(crotch_zh, 4),
                               "detectada": round(crotch / H, 4)}))

print("FIM {} arquivos em qa/probe/hem/".format(
    len(glob.glob(os.path.join(OUT, "*.npz")))))
