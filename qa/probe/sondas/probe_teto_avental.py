#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_teto_avental.py - ate que altura a barriga pendente ESCONDE o short.

    blender --background --python qa/probe/sondas/probe_teto_avental.py -- --id zen_m_b12_d1

Num corpo com avental abdominal a superficie deixa de ser estrelada em volta do
eixo: no mesmo azimute e na mesma altura existem DUAS folhas, a face da frente
da barriga (raio grande) e a face de BAIXO dela voltando para o corpo (raio
pequeno). Tudo que esta na folha interna fica atras da barriga - invisivel de
fora, e visivel so por baixo, que foi de onde o Rogerio pegou o defeito.

Pintar a folha interna de preto nao aparece de frente nem de lado, so vaza por
baixo. Entao o teto do avental - a maior altura em que ainda ha duas folhas - e
o piso do que vale a pena pintar naquele azimute.

Imprime o teto por setor, no formato de lista pronta para o shorts_map.json.
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
ap.add_argument("--vao", type=float, default=0.055,
                help="vao radial minimo, em metros, para valer como duas folhas")
ap.add_argument("--z0", type=float, default=0.28)
ap.add_argument("--z1", type=float, default=0.46)
a = ap.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master", a.id + "_master.glb"))
me = [o for o in bpy.context.scene.objects if o.type == "MESH"][0].data
n = len(me.vertices)
co = np.empty(n * 3)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
zh = co[:, 2] / H
r = np.hypot(co[:, 0], co[:, 1])
az = np.arctan2(co[:, 1], co[:, 0])
_c, _leg, is_arm = S.w_limbs(me, np, co, H)

NB = S.WAIST_AZ_BINS
ab = np.clip(((az + math.pi) / (2 * math.pi) * NB).astype(np.int64), 0, NB - 1)
PASSO = 0.004
teto = [0.0] * NB
print("{:>6} {:>8} {:>8}  {}".format("setor", "teto", "faixa", "duas folhas por altura"))
for j in range(NB):
    sel = np.where((ab == j) & (~is_arm) & (zh > a.z0) & (zh < a.z1))[0]
    dupla = []
    zz = a.z1
    while zz > a.z0:
        g = sel[(zh[sel] >= zz) & (zh[sel] < zz + PASSO)]
        if g.size >= 6:
            rr = np.sort(r[g])
            if (np.diff(rr).max() if rr.size > 1 else 0.0) >= a.vao:
                dupla.append(zz)
        zz -= PASSO
    # o teto e o topo da corrida CONTIGUA mais alta: folhas duplas soltas mais
    # acima sao braco encostando no tronco ou ruido, nao avental
    corrida = []
    for z in dupla:
        if corrida and abs(corrida[-1] - z) > PASSO * 2.5:
            break
        corrida.append(z)
    teto[j] = round(corrida[0] + PASSO, 4) if corrida else 0.0
    print("{:>6} {:>8.4f} {:>13}  corrida={:<3} soltas={}".format(
        j, teto[j],
        "{:.3f}-{:.3f}".format(min(corrida), max(corrida)) if corrida else "-",
        len(corrida), len(dupla) - len(corrida)))

print("\navental_zh = " + repr(teto))
print("RESULT ok")
