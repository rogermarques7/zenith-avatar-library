#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_bainha_vinco.py - a BAINHA na malha, sem luz, com as candidatas por cima.

    blender --background --python qa/probe/sondas/probe_bainha_vinco.py -- \
        --id zen_m_b12_d1 --aneis 0.33125,0.3479 --az 20 --foco 0.35

Mesmo metodo da sonda do cos (probe_vinco.py): concavidade como emissao pura,
sem iluminacao nenhuma, porque com luz a SOMBRA do degrau de tecido se confunde
com a divisa de cor - confusao que ja custou uma implementacao inteira na
sessao 4.

Desenha um anel horizontal por altura pedida:
  VERDE     a primeira (a bainha que esta no mapa hoje)
  VERMELHO  a segunda (a candidata)
Onde o vinco branco encosta no anel, aquele anel esta na bainha.
"""
import argparse
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--aneis", default="")
ap.add_argument("--az", type=float, default=0.0)
ap.add_argument("--el", type=float, default=0.0)
ap.add_argument("--foco", type=float, default=0.35)
ap.add_argument("--lente", type=float, default=110.0)
a = ap.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", a.id + "_master.glb"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
n = len(me.vertices)
co = np.empty(n * 3)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
zmin = co[:, 2].min()
H = co[:, 2].max() - zmin

# concavidade CRUA (sem suavizar): o vinco da bainha e fraco e a suavizacao o
# apaga - foi o que a sessao 4 descobriu ao procura-lo com luz.
k, _ = S.w_curvature(me, np, passes=0)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)

ca = me.color_attributes.new(name="conc", type="FLOAT_COLOR", domain="POINT")
for i in range(n):
    v = float(kn[i])
    ca.data[i].color = (v, v, v, 1.0)


def emissivo(nome, cor):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    e = nt.nodes.new("ShaderNodeEmission")
    if cor is None:
        at = nt.nodes.new("ShaderNodeAttribute")
        at.attribute_name = "conc"
        nt.links.new(at.outputs["Color"], e.inputs["Color"])
    else:
        e.inputs["Color"].default_value = cor
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
    return m


me.materials.clear()
me.materials.append(emissivo("conc_m", None))

rad = float(np.hypot(co[:, 0], co[:, 1]).max()) * 1.04
cores = [(0.0, 1.0, 0.15, 1.0), (1.0, 0.1, 0.0, 1.0), (0.2, 0.5, 1.0, 1.0)]
for i, s in enumerate([x for x in a.aneis.split(",") if x]):
    zh = float(s)
    cur = bpy.data.curves.new("anel%d" % i, "CURVE")
    cur.dimensions = "3D"
    cur.bevel_depth = H * 0.0025
    sp = cur.splines.new("POLY")
    N = 96
    sp.points.add(N - 1)
    sp.use_cyclic_u = True
    for t in range(N):
        ang = t / float(N) * 2 * math.pi
        sp.points[t].co = (math.cos(ang) * rad, math.sin(ang) * rad, zmin + zh * H, 1.0)
    ob = bpy.data.objects.new("anel%d" % i, cur)
    bpy.context.collection.objects.link(ob)
    cur.materials.append(emissivo("anel%d_m" % i, cores[i % len(cores)]))
    print("anel {} zh={:.4f} cor={}".format(i, zh, ["verde", "vermelho", "azul"][i % 3]))

scene = bpy.context.scene
engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                       else "BLENDER_EEVEE")
scene.render.resolution_x, scene.render.resolution_y = 760, 900
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("w")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
try:
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
except TypeError:
    pass

foco = Vector((0.0, 0.0, zmin + a.foco * H))
tg = bpy.data.objects.new("t", None)
bpy.context.collection.objects.link(tg)
tg.location = foco
cd = bpy.data.cameras.new("c")
cd.lens = a.lente
cam = bpy.data.objects.new("c", cd)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.constraints.new("TRACK_TO").target = tg
ra, re = math.radians(a.az), math.radians(a.el)
d = H * 1.2
cam.location = foco + Vector((math.sin(ra) * d * math.cos(re),
                              -math.cos(ra) * d * math.cos(re),
                              d * math.sin(re)))

out = os.path.join(ROOT, "qa", "probe", "vista",
                   "{}_bainha_az{:03.0f}_el{:+03.0f}.png".format(a.id, a.az, a.el))
os.makedirs(os.path.dirname(out), exist_ok=True)
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("RESULT " + out)
