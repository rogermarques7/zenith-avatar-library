# -*- coding: utf-8 -*-
"""_dono_glb.py - faces PRETAS da previa em cima de vertice que o campo diz BRACO.

    blender -b -P qa/probe/sondas/_dono_glb.py -- ID
"""
import os
import sys

import bpy
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

aid = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = ob.data
n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
nor = np.empty(n * 3); me.vertices.foreach_get("normal", nor); nor = nor.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
ms = S.w_arm_tube(np, co, H, is_arm)
f = S.w_arm_dono_field(np, me, co, nor, H, ms)
kd = KDTree(n)
for i in range(n):
    kd.insert(Vector(co[i]), i)
kd.balance()

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "qa", "preview", aid + "_preview.glb"))
ob2 = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
m2 = ob2.data
mats = [m.name if m else "" for m in m2.materials]
print("materiais", mats)
ruim = []
for p in m2.polygons:
    if "Short" not in mats[p.material_index]:
        continue
    c = ob2.matrix_world @ p.center
    zh = c.z / H
    if zh < 0.60:
        continue
    _co, idx, d = kd.find(c)
    if f[idx] < -0.05:
        ruim.append((c.x, c.y, zh, f[idx], is_arm[idx]))
print("faces pretas em cima de braco (dono<-0.05):", len(ruim))
ruim = np.array(ruim) if ruim else np.zeros((0, 5))
for s in (-1, 1):
    r = ruim[np.sign(ruim[:, 0]) == s] if len(ruim) else ruim
    if len(r):
        print(" lado %+d: %d faces  x %.3f..%.3f  y %+.3f..%+.3f  zh %.3f..%.3f  dono min %.2f  is_arm %d" % (
            s, len(r), r[:, 0].min(), r[:, 0].max(), r[:, 1].min(), r[:, 1].max(),
            r[:, 2].min(), r[:, 2].max(), r[:, 3].min(), int(r[:, 4].sum())))
# e o ponto: o master e o GLB estao no MESMO referencial?
z2 = np.array([v.co.z for v in m2.vertices])
print("master z %.3f..%.3f  glb z %.3f..%.3f" % (co[:, 2].min(), co[:, 2].max(), z2.min(), z2.max()))

# as faces pretas mais LATERAIS, por lado, e o dono do vertice mais proximo
pts = []
for p in m2.polygons:
    if "Short" not in mats[p.material_index]:
        continue
    c = ob2.matrix_world @ p.center
    if c.z / H < 0.62:
        continue
    _co, idx, d = kd.find(c)
    pts.append((c.x, c.y, c.z / H, f[idx], d, idx))
pts = np.array(pts)
for s in (-1, 1):
    r = pts[np.sign(pts[:, 0]) == s]
    o = np.argsort(-np.abs(r[:, 0]))[:12]
    print("lado %+d, as 12 mais laterais:" % s)
    for q in r[o]:
        print("   x %+.3f y %+.3f zh %.3f  dono %+.2f  dist %.4f  arm %d" % (
            q[0], q[1], q[2], q[3], q[4], is_arm[int(q[5])]))
