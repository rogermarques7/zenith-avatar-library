#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_anel_bainha.py - o vinco de zh 0.348 DA A VOLTA na perna, ou so existe
na frente?

    blender --background --python qa/probe/sondas/probe_anel_bainha.py -- --id zen_m_b12_d1

A pergunta importa porque as duas leituras dao numeros parecidos e conclusoes
opostas:
  - se da a volta, e a BAINHA do short e a pintura tem que parar nela;
  - se so existe na frente, e o vinco onde o avental abdominal encosta na coxa,
    e usa-lo como bainha subiria o short inteiro por um motivo errado.

Imprime a concavidade por setor de azimute em cada altura, com a OCUPACAO ao
lado - celula vazia vale zero e mente calada (ver w_fill_holes).
"""
import argparse
import math
import os
import sys

import bpy
import numpy as np

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--z0", type=float, default=0.320)
ap.add_argument("--z1", type=float, default=0.372)
a = ap.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master", a.id + "_master.glb"))
me = [o for o in bpy.context.scene.objects if o.type == "MESH"][0].data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
zh = co[:, 2] / H

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
entry = S.load_map(root)[a.id]
teto = entry.get("crotch_override_zh") or crotch / H

k, _ = S.w_curvature(me, np)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)

NB = 16
for nome, lado in (("esquerda", co[:, 0] < 0), ("direita", co[:, 0] >= 0)):
    sel = np.where(lado & (~is_arm) & (zh < teto) & (zh > teto - 0.16))[0]
    print("\nperna {}   setor 0 = costas, 4 = lado, 8 = frente (aprox)".format(nome))
    print("  {:>7} {:>5}  {}".format("zh", "occ", "concavidade por setor de azimute"))
    b0 = int(a.z0 * S.Z_BINS)
    b1 = int(a.z1 * S.Z_BINS)
    for b in range(b0, b1):
        g = sel[(co[sel, 2] >= b / S.Z_BINS * H) & (co[sel, 2] < (b + 1) / S.Z_BINS * H)]
        if g.size == 0:
            continue
        cx, cy = co[g, 0].mean(), co[g, 1].mean()
        az = np.arctan2(co[g, 1] - cy, co[g, 0] - cx)
        ab = np.clip(((az + math.pi) / (2 * math.pi) * NB).astype(np.int64), 0, NB - 1)
        val = np.zeros(NB)
        occ = np.zeros(NB, dtype=bool)
        np.maximum.at(val, ab, kn[g])
        occ[ab] = True
        cells = "".join("." if not o else " 123456789#"[min(10, int(v * 10) + 1)]
                        for v, o in zip(val, occ))
        print("  {:>7.4f} {:>4.0f}%  |{}|  n={}".format(
            (b + 0.5) / S.Z_BINS, 100.0 * occ.mean(), cells, g.size))
print("\n'.' = celula VAZIA (zero por ausencia, nao por superficie lisa)")
print("RESULT ok")
