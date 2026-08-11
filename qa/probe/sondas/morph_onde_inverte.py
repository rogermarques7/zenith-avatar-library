# -*- coding: utf-8 -*-
"""ONDE fica o triangulo que a sonda conta como invertido.

    blender -b -P qa/probe/sondas/morph_onde_inverte.py -- --glb <dist.glb> \
        --key morph_waist --inf 0.5

A contagem de normais invertidas decide a faixa de cada morph, e ela ja matou
lado inteiro por UM triangulo (`zen_m_b03_d3`, cintura positiva). Antes de
aceitar isso em 74 avatares: um triangulo invertido no CANTO DA VIRILHA, que
ninguem ve, nao e a mesma coisa que um no cos do short.

Imprime, por triangulo invertido: material, altura em fracao do corpo, e o
angulo de azimute (0 = frente, 180 = costas).
"""
import math
import os
import sys

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
GLB = argv[argv.index("--glb") + 1]
# --key aceita "morph_waist:1.0,morph_hip:-0.5" para o estado COMBINADO
KEY = argv[argv.index("--key") + 1]
INF = float(argv[argv.index("--inf") + 1]) if "--inf" in argv else None

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ob = [o for o in bpy.data.objects if o.type == "MESH"][0]
me = ob.data
kb = me.shape_keys.key_blocks

n = len(me.vertices)
co0 = np.empty(n * 3); me.vertices.foreach_get("co", co0); co0 = co0.reshape(-1, 3)
estado = [(KEY, INF)] if INF is not None else \
    [(p.split(":")[0], float(p.split(":")[1])) for p in KEY.split(",")]
co1 = co0.copy()
for k, f in estado:
    alvo = np.empty(n * 3); kb[k].data.foreach_get("co", alvo)
    co1 = co1 + (alvo.reshape(-1, 3) - co0) * f

tris = np.array([p.vertices[:] for p in me.polygons if len(p.vertices) == 3])
idx = [i for i, p in enumerate(me.polygons) if len(p.vertices) == 3]
mat = np.array([me.polygons[i].material_index for i in idx])
nomes = [s.material.name if s.material else "?" for s in ob.material_slots]


def normais(P):
    a, b, c = P[tris[:, 0]], P[tris[:, 1]], P[tris[:, 2]]
    x = np.cross(b - a, c - a)
    return x, np.linalg.norm(x, axis=1)


x0, a0 = normais(co0)
x1, a1 = normais(co1)
area_min = float(np.median(a0)) * 0.02
ok = (a0 > area_min) & (a1 > area_min)
flip = ((x1 * x0).sum(axis=1) < 0) & ok

zmin, zmax = co0[:, 2].min(), co0[:, 2].max()
H = zmax - zmin
print("\n{}: {} triangulos invertidos de {}"
      .format(estado, int(flip.sum()), int(ok.sum())))

# AGRUPAR por vizinhanca: um vinco e um GRUPO de triangulos colados; uma
# mancha de sombreamento dentro do umbigo e um triangulo SOZINHO. A contagem
# nao separa os dois, o agrupamento separa.
viz = {}
for i in np.where(flip)[0]:
    for a, b in ((0, 1), (1, 2), (2, 0)):
        viz.setdefault(tuple(sorted((tris[i][a], tris[i][b]))), []).append(i)
pai = {i: i for i in np.where(flip)[0]}


def achar(i):
    while pai[i] != i:
        pai[i] = pai[pai[i]]
        i = pai[i]
    return i


for ligados in viz.values():
    for j in ligados[1:]:
        pai[achar(j)] = achar(ligados[0])
grupos = {}
for i in np.where(flip)[0]:
    grupos.setdefault(achar(i), []).append(i)

for g in sorted(grupos.values(), key=len, reverse=True):
    c = co0[tris[g].reshape(-1)].mean(axis=0)
    az = math.degrees(math.atan2(c[0], -c[1])) % 360
    print("  grupo de {:>3} tri | {:<14} altura {:.3f} H | azimute {:5.1f} | z {:.3f}"
          .format(len(g), nomes[mat[g[0]]], (c[2] - zmin) / H, az, c[2]))
print("  maior grupo: {}".format(max(len(g) for g in grupos.values()) if grupos else 0))
