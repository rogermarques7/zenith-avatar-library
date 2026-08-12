# -*- coding: utf-8 -*-
"""mascara_peca.py - MASCARA da peca no GLB entregue: cor chapada, camera
ortografica, fundo transparente.

    blender -b -P qa/probe/sondas/mascara_peca.py -- <glb> <pasta> [azimutes]

    azimutes: lista separada por virgula, em graus (default "0,90,180")
    -> grava <pasta>/mascara_{ang}.png em RGBA

POR QUE UMA MASCARA E NAO O RENDER BONITO
-----------------------------------------
O `render_dist.py` existe para VER (LICOES.md 4.5c): ele tem o HDR, o metal e a
sombra, e e nele que se julga se a peca esta feia. Mas justamente por isso ele
nao serve de REGUA: sombra no vinco e escura como tecido preto, e o fundo do HDR
tem gradiente. Medir "onde comeca o preto" ali confunde sombra com pintura.

Aqui a camera e ORTOGRAFICA (a folha de referencia tambem e praticamente ortho,
entao as duas sao comparaveis coluna a coluna), a luz e chapada (`FLAT`), a cor
e a do MATERIAL e o fundo e alpha=0. O resultado tem tres classes exatas:
alpha=0 (fundo), claro (corpo `#B9BCC2`) e escuro (peca). Nao ha meio-termo.

E o instrumento que faltava para a §4.5b: para a FAIXA nao havia regua do
tracado por setor, so da altura do pico. Para o COS ha - o short e preto na
folha de referencia frontal, e o topo dele e visivel em toda a largura.
"""
import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
if len(argv) < 2:
    raise SystemExit("uso: ... -- <glb> <pasta> [azimutes]")
glb, out = argv[0], os.path.abspath(argv[1])
angs = [float(x) for x in (argv[2] if len(argv) > 2 else "0,90,180").split(",")]
os.makedirs(out, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "FLAT"
sh.color_type = "MATERIAL"
sh.show_cavity = False
sh.show_object_outline = False
sc.display.render_aa = "OFF"          # borda dura: cada pixel e corpo OU peca
sc.render.resolution_x, sc.render.resolution_y = 900, 1500
sc.render.film_transparent = True
sc.view_settings.view_transform = "Standard"

zs = [(ob.matrix_world @ v.co).z for v in ob.data.vertices]
alt = max(zs) - min(zs)
centro = min(zs) + alt / 2.0

cam_d = bpy.data.cameras.new("C")
cam_d.type = "ORTHO"
cam_d.ortho_scale = alt * 1.04
cam = bpy.data.objects.new("C", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam

for ang in angs:
    a = math.radians(ang)
    cam.location = (4.0 * math.sin(a), -4.0 * math.cos(a), centro)
    cam.rotation_euler = (math.radians(90), 0.0, a)
    sc.render.filepath = os.path.join(out, "mascara_%d.png" % int(round(ang)))
    bpy.ops.render.render(write_still=True)
    print("OK", sc.render.filepath)
