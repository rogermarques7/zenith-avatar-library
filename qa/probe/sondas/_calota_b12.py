# -*- coding: utf-8 -*-
"""_calota_b12.py - eixo do braco pela CALOTA lateral, fatia a fatia."""
import os, sys
import bpy
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S
aid = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = ob.data; n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
cx = np.median(co[:, 0]); zh = co[:, 2] / H
for s in (-1, 1):
    for k in np.arange(0.58, 0.80, 0.02):
        f = (zh >= k) & (zh < k + 0.01) & (np.sign(co[:, 0] - cx) == s)
        x = (co[f, 0] - cx) * s; y = co[f, 1]
        xm = x.max()
        for d in (0.03, 0.05):
            cap = x > xm - d
            hc = (y[cap].max() - y[cap].min()) / 2
            R = (hc * hc + d * d) / (2 * d)
            yc = (y[cap].max() + y[cap].min()) / 2
            print("lado %+d zh %.2f d %.2f xmax %.3f  hc %.3f  R %.3f  centro x %.3f y %+.3f" % (s, k, d, xm, hc, R, xm - R, yc))
