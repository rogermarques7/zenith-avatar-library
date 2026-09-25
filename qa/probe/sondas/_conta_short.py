# -*- coding: utf-8 -*-
"""_conta_short.py - area pintada ABAIXO de zh 0.62 (so o short) em GLBs.

    blender -b -P qa/probe/sondas/_conta_short.py -- a.glb b.glb ...
"""
import sys
import bpy
for g in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=g)
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data
    H = max(v.co.z for v in me.vertices)
    a = n = 0
    for p in me.polygons:
        if "Short" in me.materials[p.material_index].name and p.center.z / H < 0.62:
            a += p.area
            n += 1
    print("SHORT", g.replace("\\", "/").split("/")[-1], n, round(a, 5))
