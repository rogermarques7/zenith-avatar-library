#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cache_faixa.py - grava o PERFIL DE ANEL DO TRONCO das femininas, para achar
as duas bordas da FAIXA sem reabrir o Blender a cada hipotese.

    blender --background --python qa/probe/sondas/cache_faixa.py

Mesmo motivo do cache_bainha.py (sessao 21): uma passada de --fit --all custa
~25 min e o mapa de concavidade de um master que nao mudou e sempre o mesmo.
A licao daquela sessao foi que hipotese cara nao se testa - se chuta. Aqui a
pergunta e nova em folha ("onde estao as duas bordas da faixa?"), entao o cache
vem ANTES de qualquer codigo de deteccao.

O QUE ENTRA NO CACHE, E POR QUE MAIS DE UM SINAL
------------------------------------------------
A bainha e o cos foram achados so por CONCAVIDADE (ring_score). Na faixa isso
pode nao bastar: a borda de baixo do short cai sobre a coxa lisa, mas a borda de
baixo da faixa cai no SULCO INFRAMAMARIO, que ja e um vinco anatomico - e a de
cima cai no peitoral, que tem relevo proprio. Entao o cache guarda tambem o
RAIO por (azimute, altura): o tecido e uma casca por cima da pele, e a borda
dele e um DEGRAU DE RAIO. Se a concavidade nao separar, o degrau separa.

Guarda o mapa inteiro, nao so o perfil: a faixa pode ter borda inclinada
(mais baixa na frente, por causa do busto) e isso so aparece por azimute.

Grava qa/probe/faixa/{id}.npz.
"""
import glob
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

OUT = os.path.join(ROOT, "qa", "probe", "faixa")
os.makedirs(OUT, exist_ok=True)

AZ = S.WAIST_AZ_BINS
ZB = S.Z_BINS

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
alvo = set(args)

ids = sorted(os.path.basename(p)[: -len("_master.glb")]
             for p in glob.glob(os.path.join(ROOT, "02_master", "zen_f_*_master.glb")))
if alvo:
    ids = [i for i in ids if i in alvo]

for aid in ids:
    master = os.path.join(ROOT, "02_master", aid + "_master.glb")
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
    k, _ = S.w_curvature(me, np)
    kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)

    tronco = np.where((~is_arm) & (co[:, 2] >= crotch))[0]
    A, ring, occ = S.w_ring_map(np, co, kn, tronco, H, "axis", AZ)

    # --- raio por (azimute, altura), medido no EIXO -------------------------
    # A faixa e uma casca sobre a pele: a borda dela e um degrau de raio. Media
    # e nao maximo porque o maximo pega o vertice mais externo da celula, que num
    # tronco decimado pula.
    rad = np.full((AZ, ZB), np.nan)
    r = np.hypot(co[tronco, 0], co[tronco, 1])
    az = np.arctan2(co[tronco, 1], co[tronco, 0])
    ab = np.clip(((az + math.pi) / (2 * math.pi) * AZ).astype(np.int64), 0, AZ - 1)
    zb = np.clip((zh[tronco] * ZB).astype(np.int64), 0, ZB - 1)
    soma = np.zeros((AZ, ZB))
    cont = np.zeros((AZ, ZB))
    np.add.at(soma, (ab, zb), r)
    np.add.at(cont, (ab, zb), 1.0)
    viz = cont > 0
    rad[viz] = soma[viz] / cont[viz]

    # altura da axila: a faixa mora abaixo dela, e e o teto natural da busca
    axila = float(zh[is_arm].min()) if is_arm.any() else 0.75

    np.savez_compressed(
        os.path.join(OUT, aid + ".npz"),
        A=A.astype(np.float32), ring=ring.astype(np.float32),
        occ=occ, rad=rad.astype(np.float32),
        meta=np.array([crotch / H, axila, H, float(is_arm.sum())],
                      dtype=np.float64))
    print("FAIXA " + json.dumps({"id": aid, "crotch_zh": round(crotch / H, 4),
                                 "axila_zh": round(axila, 4)}))

print("FIM {} arquivos em qa/probe/faixa/".format(
    len(glob.glob(os.path.join(OUT, "*.npz")))))
