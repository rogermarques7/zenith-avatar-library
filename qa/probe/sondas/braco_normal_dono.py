# -*- coding: utf-8 -*-
"""braco_normal_dono.py - de QUEM e esta superficie: do braco ou do tronco?

    blender -b -P qa/probe/sondas/braco_normal_dono.py -- --id ID [--id ...]

Prototipo do criterio da sessao 39. Para cada vertice na altura da faixa:

    s_braco  = normal . (direcao radial a partir do EIXO DO BRACO)
    s_tronco = normal . (direcao radial horizontal a partir do eixo do TRONCO)
    campo    = s_tronco - s_braco        (> 0 tronco, < 0 braco)

A face do braco olha para longe do eixo do braco; o flanco do tronco, para longe
do eixo do tronco. E local e nao tem limiar de TAMANHO - o que matou o tubo de
raio fixo (acima da fusao a secao do braco cresce 30%). Depois o campo e ALISADO
pela malha, porque a normal de musculo e cheia de calombo.

Cores: preto = faixa (campo da peca > 0 e tronco), vermelho = braco pelo
criterio na banda, azul = braco topologico (w_limbs), cinza = corpo.
Saida: qa/peca/{id}/dono/*.png
"""
import argparse
import math
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
ap.add_argument("--alisa", type=int, default=10)
a = ap.parse_args(argv)

VISTAS = [(0, 0.0), (35, -0.2), (90, 0.0), (145, -0.2), (180, 0.0), (-35, 0.2)]

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
    nor = np.empty(n * 3)
    me.vertices.foreach_get("normal", nor)
    nor = nor.reshape(n, 3)
    H = co[:, 2].max() - co[:, 2].min()
    z0 = co[:, 2].min()
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
    ms = S.w_arm_tube(np, co, H, is_arm)
    f = S.w_arm_dono_field(np, me, co, nor, H, ms, alisa=a.alisa)

    e = S.load_map(ROOT)[aid]
    cfg = {"hem_l": np.atleast_1d(e["hem_l_zh"]) * H,
           "hem_r": np.atleast_1d(e["hem_r_zh"]) * H,
           "hem_center_l": e.get("hem_center_l", [0, 0]),
           "hem_center_r": e.get("hem_center_r", [0, 0]),
           "waist": np.atleast_1d(e["waist_zh"]) * H,
           "faixa_lo": np.atleast_1d(e["faixa_lo_zh"]) * H,
           "faixa_hi": np.atleast_1d(e["faixa_hi_zh"]) * H}
    campo = S.w_field(np, co, cfg) > 0
    zh = (co[:, 2] - z0) / H
    lo = float(np.min(cfg["faixa_lo"])) / H
    hi = float(np.max(cfg["faixa_hi"])) / H
    banda = (zh >= lo - 0.01) & (zh <= hi + 0.01)
    cores = np.tile(np.array([0.72, 0.73, 0.76, 1.0]), (n, 1))
    cores[campo & ~is_arm & (f > 0)] = [0.02, 0.02, 0.025, 1.0]
    cores[(f < 0) & banda] = [0.85, 0.10, 0.10, 1.0]
    cores[is_arm & banda] = [0.1, 0.2, 0.9, 1.0]
    col = me.color_attributes.new(name="c", type="FLOAT_COLOR", domain="POINT")
    col.data.foreach_set("color", cores.ravel())
    me.update()
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "VERTEX"
    sc.render.resolution_x, sc.render.resolution_y = 600, 600
    cam_d = bpy.data.cameras.new("C")
    cam_d.lens = 200
    cam = bpy.data.objects.new("C", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    OUT = os.path.join(ROOT, "qa", "peca", aid, "dono")
    os.makedirs(OUT, exist_ok=True)
    for i, (ang, xo) in enumerate(VISTAS):
        r = math.radians(ang)
        zc = z0 + H * 0.71
        cam.location = (xo + 5.0 * math.sin(r), -5.0 * math.cos(r), zc)
        cam.rotation_euler = (math.radians(90), 0.0, r)
        sc.render.filepath = os.path.join(OUT, "d%d.png" % i)
        bpy.ops.render.render(write_still=True)
print("RESULT ok")
