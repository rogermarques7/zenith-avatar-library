# -*- coding: utf-8 -*-
"""braco_tubo_mede.py - a geometria do braco TOPOLOGICO (w_limbs), fatia a fatia.

    blender -b -P qa/probe/sondas/braco_tubo_mede.py -- --id ID [--id ...]

Imprime, por lado, a altura da fusao e o centroide/raio de cada fatia do braco
abaixo dela. Serve para decidir se o braco e um TUBO de eixo reto ate a fusao -
premissa do w_arm_tube - antes de escrever o modelo.
"""
import argparse
import os
import sys

import bpy
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", action="append", required=True)
a = ap.parse_args(argv)

for aid in a.id:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master",
                                                    aid + "_master.glb"))
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data
    n = len(me.vertices)
    co = np.empty(n * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    H = co[:, 2].max() - co[:, 2].min()
    z0 = co[:, 2].min()
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
    cx = float(np.median(co[:, 0]))
    print("== %s  H=%.3f  crotch_zh=%.3f" % (aid, H, (crotch - z0) / H))
    for sinal in (-1, 1):
        m = is_arm & (np.sign(co[:, 0] - cx) == sinal)
        zh = (co[m, 2] - z0) / H
        fz = zh.max()
        print(" lado %+d  arm_verts=%d  zh %.3f..%.3f (fusao)" % (
            sinal, m.sum(), zh.min(), fz))
        idx = np.where(m)[0]
        for k in np.arange(fz - 0.20, fz + 1e-9, 0.02):
            s = idx[(zh >= k - 0.005) & (zh < k + 0.005)]
            if len(s) < 10:
                continue
            c = co[s].mean(axis=0)
            r = np.hypot(co[s, 0] - c[0], co[s, 1] - c[1])
            print("   zh %.3f  n=%4d  cx=%+.3f cy=%+.3f  r50=%.3f r90=%.3f "
                  "rmax=%.3f  xmin=%.3f xmax=%.3f" % (
                      k, len(s), c[0] - cx, c[1], np.median(r),
                      np.quantile(r, 0.9), r.max(),
                      (co[s, 0] - cx).min() * sinal * -1 if sinal < 0 else
                      (co[s, 0] - cx).min(),
                      np.abs(co[s, 0] - cx).max()))
print("RESULT ok")
