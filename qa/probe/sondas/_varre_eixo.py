# -*- coding: utf-8 -*-
"""_varre_eixo.py - fusao do braco x base da faixa x eixo, nas femininas.

    blender -b -P qa/probe/sondas/_varre_eixo.py
"""
import json, os, sys
import bpy
import numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S
smap = S.load_map(ROOT)
ids = sorted(k for k, e in smap.items() if "faixa_lo_zh" in e)
out = {}
for aid in ids:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data; n = len(me.vertices)
    co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
    H = co[:, 2].max() - co[:, 2].min()
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
    ms = S.w_arm_tube(np, co, H, is_arm)
    lo = float(np.min(np.atleast_1d(smap[aid]["faixa_lo_zh"])))
    hi = float(np.max(np.atleast_1d(smap[aid]["faixa_hi_zh"])))
    out[aid] = {"lo": lo, "hi": hi, "arm_ext": [], "m": [
        {"sinal": m["sinal"], "fusao": m["fusao_zh"], "ax": [float(x) for x in m["ax"]],
         "Rm": float(np.mean(m["R"]))} for m in ms]}
    for s in (-1, 1):
        mm = is_arm & (np.sign(co[:, 0] - np.median(co[:, 0])) == s)
        if mm.any():
            zh = co[mm, 2] / H
            out[aid]["arm_ext"].append([float(zh.min()), float(zh.max())])
    print("%-15s lo %.3f hi %.3f  %s" % (aid, lo, hi, "  ".join(
        "%+d fus %.3f ax(%.2f,%.2f,%.2f) R %.3f" % (m["sinal"], m["fusao_zh"], *m["ax"], np.mean(m["R"])) for m in ms)), flush=True)
json.dump(out, open(os.path.join(ROOT, "qa", "probe", "_varre_eixo.json"), "w"), indent=1)
print("RESULT ok")
