# -*- coding: utf-8 -*-
"""_conta_mat.py - faces e area por material em GLBs (compara previa x entregue).

    blender -b -P qa/probe/sondas/_conta_mat.py -- a.glb b.glb ...
"""
import sys
import bpy
for g in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=g)
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data
    cont = {}
    for p in me.polygons:
        k = me.materials[p.material_index].name
        c = cont.setdefault(k, [0, 0.0])
        c[0] += 1
        c[1] += p.area
    print("CONTA", g.split("\\")[-1].split("/")[-1], {k: (v[0], round(v[1], 4)) for k, v in cont.items()})
