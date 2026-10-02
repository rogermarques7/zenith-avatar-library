# -*- coding: utf-8 -*-
"""A/B do PESCOCO entre DOIS GLBs (copia do ombro_ab2.py com estados fracionarios).

    blender -b -P qa/probe/sondas/pescoco_ab.py -- --a A.glb --b B.glb --out DIR
            [--inf 1,-0.5,-1] [--infa ...] [--infb ...]

Rotulo do estado = a influence com 2 casas (o ombro_ab2 arredonda -0,5 para "-0").
--infa/--infb deixam comparar no MESMO CENTIMETRO quando as curvas diferem.

Original:

    blender -b -P qa/probe/sondas/ombro_ab2.py -- --a A.glb --b B.glb --out DIR
            [--key morph_shoulder] [--inf 1,-1] [--lente 150]

Existe porque o `morph_render_ab.py` (camera por restricao TRACK_TO) deu
enquadramento diferente para dois GLBs com a base identica (25/09) - A/B com
camera que anda nao compara nada. Aqui a camera e posta por matriz, uma vez, e
os dois arquivos passam por ela. Clay com cavidade (Workbench), lente longa.
Grava {tag}_{estado}_{vista}.png; a costura e o ombro_ab2_folha.py.
"""
import bpy
import sys
import os
import math
import mathutils

argv = sys.argv[sys.argv.index("--") + 1:]


def arg(n, p=None):
    return argv[argv.index(n) + 1] if n in argv else p


A, B, OUT = arg("--a"), arg("--b"), os.path.abspath(arg("--out"))
KEY = arg("--key", "morph_neck")
INFS = [float(x) for x in arg("--inf", "1,-0.5,-1").split(",")]
INFA = [float(x) for x in arg("--infa", arg("--inf", "1,-0.5,-1")).split(",")]
INFB = [float(x) for x in arg("--infb", arg("--inf", "1,-0.5,-1")).split(",")]
LENTE = float(arg("--lente", "200"))
os.makedirs(OUT, exist_ok=True)

# alvo = ombro direito do avatar (x>0), dist grande + lente longa
VISTAS = [("frente", 0), ("tresq", 35), ("lado", 90), ("costas", 180)]


def cena(glb):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    ob = [o for o in bpy.data.objects if o.type == "MESH"][0]
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "SINGLE"
    sh.single_color = (0.62, 0.63, 0.66)
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.cavity_ridge_factor = 1.6
    sh.cavity_valley_factor = 1.6
    sc.display.render_aa = "8"
    sc.render.resolution_x = 520
    sc.render.resolution_y = 560
    sc.view_settings.view_transform = "Standard"
    sc.world = bpy.data.worlds.new("W")
    cd = bpy.data.cameras.new("c")
    cd.lens = LENTE
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    for k in ob.data.shape_keys.key_blocks:
        k.slider_min, k.slider_max = -3.0, 3.0
    return ob, cam, sc


def mirar(cam, alvo, dist, ang):
    a = math.radians(ang)
    pos = mathutils.Vector((alvo[0] + dist * math.sin(a), alvo[1] - dist * math.cos(a), alvo[2]))
    cam.location = pos
    d = mathutils.Vector(alvo) - pos
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


for tag, glb in (("A", A), ("B", B)):
    ob, cam, sc = cena(glb)
    kb = ob.data.shape_keys.key_blocks
    H = max((ob.matrix_world @ v.co).z for v in ob.data.vertices)
    alvo = (float(arg("--ax", "0.0")) * H / 1.75, 0.0, float(arg("--az", "0.855")) * H)
    lista = INFA if tag == "A" else INFB
    estados = [("base", 0.0)] + [("e{}".format(n), i) for n, i in enumerate(lista)]
    for nome, inf in estados:
        for k in kb:
            if k.name != "Basis":
                k.value = 0.0
        if KEY in kb:
            kb[KEY].value = inf
        for vn, ang in VISTAS:
            mirar(cam, alvo, float(arg("--dist", str(1.9 * LENTE / 150.0))), ang)
            sc.render.filepath = os.path.join(OUT, "{}_{}_{}.png".format(tag, nome, vn))
            bpy.ops.render.render(write_still=True)
print("AB2 feito", OUT)
