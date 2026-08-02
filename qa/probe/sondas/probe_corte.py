#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_corte.py - corte SAGITAL do master, com a regiao pintada marcada.

    blender --background --python qa/probe/sondas/probe_corte.py -- --id zen_m_b12_d1

Desenha os vertices proximos de um plano (default x ~ 0, o plano medio) no
espaco (y, z). Vermelho = o campo do short diz "pintar"; cinza = corpo.

E a unica vista que mostra o AVENTAL DE PERFIL: onde a barriga desce, onde ela
volta e encosta no corpo, e por onde a linha do cos passa no meio disso. Numa
vista renderizada a barriga esconde exatamente o que se quer ver.
"""
import argparse
import os
import sys

import json

import bpy
import numpy as np

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--x", type=float, default=0.0, help="plano do corte, em metros")
ap.add_argument("--esp", type=float, default=0.02, help="espessura do corte")
a = ap.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master", a.id + "_master.glb"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
entry = S.load_map(root)[a.id]


def _scale(v, f):
    return [x * f for x in v] if isinstance(v, (list, tuple)) else v * f


cfg = {"hem_l": _scale(entry["hem_l_zh"], H),
       "hem_r": _scale(entry["hem_r_zh"], H),
       "hem_center_l": entry.get("hem_center_l", [0.0, 0.0]),
       "hem_center_r": entry.get("hem_center_r", [0.0, 0.0]),
       "waist": _scale(entry["waist_zh"], H)}
field = S.w_field(np, co, cfg)
pintado = (field > 0) & (~is_arm)

sel = np.where(np.abs(co[:, 0] - a.x) < a.esp)[0]
out = os.path.join(root, "qa", "probe", "vista",
                   "{}_corte_x{:+.2f}.json".format(a.id, a.x))
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    json.dump({"id": a.id, "x": a.x, "H": H,
               "y": [round(float(v), 5) for v in co[sel, 1]],
               "zh": [round(float(v) / H, 5) for v in co[sel, 2]],
               "pintado": [bool(v) for v in pintado[sel]]}, f)
print("frente = y negativo")
print("RESULT " + out)
