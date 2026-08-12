# -*- coding: utf-8 -*-
"""cos_avental_mapa.py - desce o cos da FRENTE ate o fundo da dobra do avental,
na curva que JA ESTA no shorts_map.json, e renderiza o antes/depois.

    blender -b -P qa/probe/sondas/cos_crista_mapa.py -- --id ID [--escrever]

    --escrever  grava o waist_zh novo no mapa e marca "cos_crista": true

POR QUE NAO E UM `--fit --refit`
--------------------------------
A regra mora no `shorts.py` (`w_cos_crista`, ligada por `"cos_crista": true`) e
um `--fit` a reproduz. Mas 6 dos 7 avatares desta fila estao marcados
`"source": "manual"`, e o que ha de manual neles nao e o cos - e a BAINHA
(`hem_fonte: anel-xsign`, `malha ...`), corrigida a mao em sessoes anteriores.
Um `--refit` recalcularia tudo e jogaria essas correcoes fora. Entao aqui a
curva do mapa e a ENTRADA, e a crista e aplicada em cima dela.

O render e o banco de ensaio: pinta a regiao por VERTEX COLOR no master e
fotografa em 40 e 90 graus, sem exportar GLB nenhum. Iterar assim custa ~40 s
por avatar; iterar com `--apply` custa uma versao de dist e um `morph --apply`.
"""
import argparse
import json
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
ap.add_argument("--escrever", action="store_true")
ap.add_argument("--out", default=None)
a = ap.parse_args(argv)
OUT = os.path.abspath(a.out or os.path.join(root, "qa", "peca", a.id, "ensaio"))
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master",
                                                a.id + "_master.glb"))
ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = ob.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
smap = S.load_map(root)
entry = smap[a.id]
nor = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("normal", nor)
nor = nor.reshape(n, 3)
hem = float(np.atleast_1d(entry["hem_l_zh"]).max())
base = list(entry["waist_zh"])
crotch_zh = entry.get("crotch_override_zh") or crotch / H
novo = S.w_cos_avental(np, co, nor, is_arm, H, crotch_zh, hem, base, len(base))

print("setor   atual    novo    dz")
for j in range(len(base)):
    print("%3d   %6.3f  %6.3f  %+6.3f" % (j, base[j], novo[j], novo[j] - base[j]))
print("descida maxima = %+.4f   setores movidos = %d de %d" % (
    min(b - a_ for a_, b in zip(base, novo)),
    sum(1 for a_, b in zip(base, novo) if a_ - b > 0.0005), len(base)))

# ---- banco de ensaio: pintura por vertex color, sem exportar ---------------
col = me.color_attributes.new(name="ensaio", type="FLOAT_COLOR", domain="POINT")
mat = bpy.data.materials.new("ensaio")
me.materials.clear()
me.materials.append(mat)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "VERTEX"
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.show_object_outline = False
sc.display.render_aa = "8"
sc.render.resolution_x, sc.render.resolution_y = 800, 800
sc.render.film_transparent = False
cam_d = bpy.data.cameras.new("C")
cam_d.lens = 85
cam = bpy.data.objects.new("C", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam

def _m(v):
    """zh -> metros, aceitando escalar ou lista (o mapa usa os dois)."""
    return [x * H for x in v] if isinstance(v, (list, tuple)) else v * H


for nome, curva in (("0_atual", base), ("1_avental", novo)):
    cfg = {"hem_l": _m(entry["hem_l_zh"]),
           "hem_r": _m(entry["hem_r_zh"]),
           "hem_center_l": entry.get("hem_center_l", [0.0, 0.0]),
           "hem_center_r": entry.get("hem_center_r", [0.0, 0.0]),
           "waist": [v * H for v in curva]}
    dentro = S.w_field(np, co, cfg) > 0
    cores = np.tile(np.array([0.72, 0.73, 0.76, 1.0]), (n, 1))
    cores[dentro & (~is_arm)] = [0.02, 0.02, 0.025, 1.0]
    col.data.foreach_set("color", cores.ravel())
    me.update()
    for ang in (40, 90):
        z0 = co[:, 2].min() + H * 0.45
        r = math.radians(ang)
        cam.location = (2.4 * math.sin(r), -2.4 * math.cos(r), z0)
        cam.rotation_euler = (math.radians(90), 0.0, r)
        sc.render.filepath = os.path.join(OUT, "%s_%d.png" % (nome, ang))
        bpy.ops.render.render(write_still=True)

if a.escrever:
    entry["waist_zh"] = [round(v, 5) for v in novo]
    entry["cos_avental"] = True
    entry["source"] = entry.get("source", "auto")
    S.save_map(root, smap)
    print("mapa gravado")
print("RESULT ok")
