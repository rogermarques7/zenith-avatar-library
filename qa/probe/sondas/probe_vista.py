#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_vista.py - renderiza um GLB de 03_dist/ de QUALQUER angulo, com e sem luz.

    blender --background --python qa/probe/sondas/probe_vista.py -- \
        --id zen_m_b12_d1 --az 0,180 --el -50,0

Dois modos por vista:
  <nome>.png       ambiente Zenith normal (e o que o Rogerio ve no tester)
  <nome>_flat.png  EMISSAO PURA: corpo cinza, short VERMELHO, sem luz nenhuma.

O segundo existe porque com luz nao da para distinguir SOMBRA de DIVISA DE COR -
e a malha da Meshy tem o degrau de tecido do short modelado, que projeta uma
linha escura por conta propria. Ja gerou hipotese errada uma vez (sessao 4).
"""
import argparse
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--az", default="0,90,180,270")
ap.add_argument("--el", default="0")
ap.add_argument("--out", default=None)
ap.add_argument("--zoom", type=float, default=1.0, help="aproxima a camera")
ap.add_argument("--alvo", type=float, default=None,
                help="altura do alvo em fracao da altura (default: meio do corpo)")
ap.add_argument("--sem", action="store_true",
                help="com --master: nao pinta short nenhum. Serve para separar SOMBRA de PINTURA: a cavidade debaixo da barriga renderiza escura por conta propria, e ja confundiu diagnostico antes.")
ap.add_argument("--externa", type=float, default=None,
                help="com --master: nao pintar face mais de X metros para dentro do raio maximo da sua celula (azimute x altura)")
ap.add_argument("--nz", type=float, default=None,
                help="com --master: nao pintar face com normal.z abaixo disto")
ap.add_argument("--nz-acima", dest="nz_acima", type=float, default=0.0,
                help="o teste da normal so vale acima desta altura")
ap.add_argument("--master", action="store_true",
                help="le 02_master/ e pinta pelo mapa, em vez de ler 03_dist/. "
                     "E o que permite conferir um ajuste ANTES de gravar o "
                     "asset que o app consome.")
a = ap.parse_args(argv)

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
glb = (os.path.join(root, "02_master", a.id + "_master.glb") if a.master else
       os.path.join(root, "03_dist", "glb", a.id + "_v1.glb"))
out_dir = a.out or os.path.join(root, "qa", "probe", "vista", a.id)
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]

if a.master:
    # Pinta aqui pelo mapa, sem cortar a malha: a divisa fica quantizada por
    # triangulo (~6 mm), o que basta para julgar ONDE ela esta. Quem entrega a
    # borda exata e o shorts.py --apply.
    import numpy as np
    sys.path.insert(0, os.path.join(root, "scripts"))
    import shorts as S
    import zenith_material as zm

    me = obj.data
    nv = len(me.vertices)
    co = np.empty(nv * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(nv, 3)
    H0 = co[:, 2].max() - co[:, 2].min()
    _c, _leg, is_arm = S.w_limbs(me, np, co, H0)
    e = S.load_map(root)[a.id]

    def _sc(v):
        return [x * H0 for x in v] if isinstance(v, (list, tuple)) else v * H0

    cfg = {"hem_l": _sc(e["hem_l_zh"]), "hem_r": _sc(e["hem_r_zh"]),
           "hem_center_l": e.get("hem_center_l", [0.0, 0.0]),
           "hem_center_r": e.get("hem_center_r", [0.0, 0.0]),
           "waist": _sc(e["waist_zh"])}
    me.materials.clear()
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    me.materials.append(zm.make_body_material(bpy))
    me.materials.append(zm.make_shorts_material(bpy))
    cent = np.array([tuple(p.center) for p in me.polygons])
    fld = S.w_field(np, cent, cfg)
    braco = np.array([any(is_arm[i] for i in p.vertices) for p in me.polygons])
    ok = (fld > 0) & (~braco)
    if a.sem:
        ok = ok & False
    if a.externa is not None:
        # FOLHA EXTERNA: numa celula (azimute x altura), so e short o que esta a
        # menos de X metros do raio MAXIMO daquela celula. O que fica mais para
        # dentro esta atras da barriga - invisivel de fora, e so vaza por baixo.
        # Local e adaptativo: nao precisa de limiar de raio global, que nao
        # existe num corpo cuja cintura vai de 0.19 a 0.39 de raio.
        import math as _m
        NB = 24
        rr = np.hypot(cent[:, 0], cent[:, 1])
        aa = np.clip(((np.arctan2(cent[:, 1], cent[:, 0]) + _m.pi)
                      / (2 * _m.pi) * NB).astype(np.int64), 0, NB - 1)
        zb = np.clip((cent[:, 2] / H0 * 240).astype(np.int64), 0, 239)
        chave = aa * 240 + zb
        rmax = np.zeros(NB * 240)
        np.maximum.at(rmax, chave, rr)
        corta = ok & (rr < rmax[chave] - a.externa)
        print("faces atras da folha externa: {} de {} pintadas".format(
            int(corta.sum()), int(ok.sum())))
        ok = ok & (~corta)
    if a.nz is not None:
        # A prateleira que e a face de baixo do avental e HORIZONTAL e virada
        # para BAIXO; o resto do short naquela faixa de altura e vertical e
        # virado para FORA. Teste do discriminador.
        nz = np.array([p.normal.z for p in me.polygons])
        corta = ok & (nz < a.nz) & (cent[:, 2] > a.nz_acima * H0)
        print("faces cortadas pelo teste da normal: {} de {} pintadas".format(
            int(corta.sum()), int(ok.sum())))
        ok = ok & (~corta)
    for i, p in enumerate(me.polygons):
        p.material_index = 1 if ok[i] else 0
    print("pintado do mapa: hem {} / cos {:.3f}..{:.3f}".format(
        e["hem_l_zh"], min(e["waist_zh"]), max(e["waist_zh"])))

mats = [m.name for m in obj.data.materials]
print("materiais:", mats)

scene = bpy.context.scene
engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                       else "BLENDER_EEVEE")
scene.render.resolution_x, scene.render.resolution_y = 700, 900
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
try:
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
except TypeError:
    pass

bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
zz = [v.z for v in bb]
height = max(zz) - min(zz)
cz = (min(zz) + max(zz)) / 2.0 if a.alvo is None else min(zz) + a.alvo * height
center = Vector((0.0, 0.0, cz))

target = bpy.data.objects.new("target", None)
bpy.context.collection.objects.link(target)
target.location = center
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 70.0
cam = bpy.data.objects.new("cam", cam_d)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.constraints.new("TRACK_TO").target = target

# --- mundo com o ambiente Zenith -------------------------------------------
env = os.path.join(root, "03_dist", "env", "zenith_env.hdr")
world = bpy.data.worlds.new("Zenith")
scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()
tex = nt.nodes.new("ShaderNodeTexEnvironment")
tex.image = bpy.data.images.load(env)
bgn = nt.nodes.new("ShaderNodeBackground")
outw = nt.nodes.new("ShaderNodeOutputWorld")
nt.links.new(tex.outputs["Color"], bgn.inputs["Color"])
nt.links.new(bgn.outputs["Background"], outw.inputs["Surface"])

pbr_mats = list(obj.data.materials)


def make_flat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    e = m.node_tree.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = rgba
    o = m.node_tree.nodes.new("ShaderNodeOutputMaterial")
    m.node_tree.links.new(e.outputs["Emission"], o.inputs["Surface"])
    return m


flat_mats = [make_flat("flat_body", (0.45, 0.45, 0.50, 1.0)),
             make_flat("flat_short", (1.0, 0.05, 0.05, 1.0))]

azs = [float(x) for x in a.az.split(",")]
els = [float(x) for x in a.el.split(",")]
dist_cam = height * 2.2 / max(a.zoom, 0.05)

for az in azs:
    for el in els:
        ra, re = math.radians(az), math.radians(el)
        cam.location = center + Vector((
            math.sin(ra) * dist_cam * math.cos(re),
            -math.cos(ra) * dist_cam * math.cos(re),
            dist_cam * math.sin(re)))
        bpy.context.view_layer.update()
        tag = "az{:03.0f}_el{:+03.0f}".format(az, el)

        for i, m in enumerate(pbr_mats):
            obj.data.materials[i] = m
        scene.render.filepath = os.path.join(out_dir, tag + ".png")
        bpy.ops.render.render(write_still=True)

        for i, m in enumerate(flat_mats):
            obj.data.materials[i] = m
        scene.render.filepath = os.path.join(out_dir, tag + "_flat.png")
        bpy.ops.render.render(write_still=True)

print("RESULT ok -> " + out_dir)
