"""Sonda 3: render de EMISSAO PURA da concavidade, com as curvas por cima.

Metodo herdado da sessao 4, que ja tinha resolvido uma pergunta parecida sobre a
bainha: com luz, a sombra do degrau de tecido se confunde com a divisa de cor, e
foi essa confusao que gerou uma hipotese errada e uma implementacao inteira que
piorou o resultado. Sem luz nao ha o que confundir.

Aqui a pergunta e: nos corpos pesados, a divisa entre a barriga pendente e o
short EXISTE como vinco na malha? E, se existe, ela e mais forte ou mais fraca
que as dobras da propria barriga?

Pinta a concavidade em escala de cinza por vertice e desenha:
  VERDE     a curva do cos que esta no mapa hoje
  VERMELHO  a curva medida na FOLHA de referencia (o alvo)

    blender --background --python scripts/probe_vinco.py -- --id zen_m_b12_d1
"""
import os
import sys
import math
import argparse

import bpy
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--ref", default="")  # perfil da folha em JSON (o Blender nao tem PIL)
a = ap.parse_args(argv)

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import json                  # noqa: E402
import shorts as S           # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(
    filepath=os.path.join(ROOT, "02_master", a.id + "_master.glb"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
zs = [v.co.z for v in me.vertices]
H = max(zs) - min(zs)
n = len(me.vertices)
co = np.empty(n * 3)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)

k, _ = S.w_curvature(me, np)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)

# concavidade como COR DE VERTICE, e material de emissao pura lendo essa cor
ca = me.color_attributes.new(name="conc", type="FLOAT_COLOR", domain="POINT")
for i in range(n):
    v = float(kn[i])
    ca.data[i].color = (v, v * 0.25, v * 0.25, 1.0)

mat = bpy.data.materials.new("emis")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
attr = nt.nodes.new("ShaderNodeAttribute")
attr.attribute_name = "conc"
emi = nt.nodes.new("ShaderNodeEmission")
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(attr.outputs["Color"], emi.inputs["Color"])
nt.links.new(emi.outputs["Emission"], out.inputs["Surface"])
me.materials.clear()
me.materials.append(mat)

# ---- curvas: a do mapa (verde) e a da folha (vermelha) ---------------------
smap = S.load_map(ROOT)
entry = smap.get(a.id, {})
waist = entry.get("waist_zh")
ref = json.loads(a.ref) if a.ref else None

zmin = min(zs)
rad = max(math.hypot(v.co.x, v.co.y) for v in me.vertices) * 1.06


def anel(vals, cor, nome):
    if not vals:
        return
    pts, nb = [], len(vals)
    for j in range(nb):
        if vals[j] is None:
            continue
        az = (j + 0.5) / nb * 2 * math.pi - math.pi
        if math.sin(az) > -0.15:          # so a frente, que e o que a camera ve
            continue
        pts.append((az, vals[j]))
    if len(pts) < 2:
        return
    cur = bpy.data.curves.new(nome, "CURVE")
    cur.dimensions = "3D"
    cur.bevel_depth = H * 0.004
    sp = cur.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for i, (az, zh) in enumerate(pts):
        sp.points[i].co = (math.cos(az) * rad, math.sin(az) * rad,
                           zmin + zh * H, 1.0)
    ob = bpy.data.objects.new(nome, cur)
    bpy.context.collection.objects.link(ob)
    m = bpy.data.materials.new(nome + "_m")
    m.use_nodes = True
    nt2 = m.node_tree
    nt2.nodes.clear()
    e = nt2.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = cor
    o2 = nt2.nodes.new("ShaderNodeOutputMaterial")
    nt2.links.new(e.outputs["Emission"], o2.inputs["Surface"])
    cur.materials.append(m)


anel(waist, (0.0, 1.0, 0.2, 1.0), "cos_mapa")
anel(ref, (1.0, 0.15, 0.0, 1.0), "cos_folha")

scene = bpy.context.scene
engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                       else "BLENDER_EEVEE")
scene.render.resolution_x, scene.render.resolution_y = 700, 900
scene.render.film_transparent = False
scene.world = bpy.data.worlds.new("w")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
try:
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
except TypeError:
    pass

bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
zz = [v.z for v in bb]
# enquadra so o trecho do short, senao nao da para ver vinco nenhum
foco = Vector((0.0, 0.0, zmin + 0.46 * H))
tg = bpy.data.objects.new("t", None)
bpy.context.collection.objects.link(tg)
tg.location = foco
cd = bpy.data.cameras.new("c")
cd.lens = 120.0
cam = bpy.data.objects.new("c", cd)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.constraints.new("TRACK_TO").target = tg
cam.location = foco + Vector((0.0, -H * 1.15, 0.0))

os.makedirs(os.path.join(ROOT, "qa", "probe"), exist_ok=True)
scene.render.filepath = os.path.join(ROOT, "qa", "probe", a.id + "_vinco.png")
bpy.ops.render.render(write_still=True)
print("RESULT " + scene.render.filepath)
