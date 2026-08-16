# -*- coding: utf-8 -*-
"""faixa_braco_mapa.py - banco de ensaio da MASCARA DE BRACO na faixa.

    blender -b -P qa/probe/sondas/faixa_braco_mapa.py -- --id ID [--id ID2 ...]

Pinta a peca no master por vertex color, em dois estados, e fotografa:

    0_antes   criterio so de PROFUNDIDADE + mediana de 5 (o de 11/08)
    1_agora   criterio do VAO com plano B de profundidade + ajuste de grau 2

Sem exportar GLB e sem gastar versao de dist - ~40 s por avatar, contra um
`shorts --apply` mais um `morph --apply` por tentativa (regra 9).

⚠️ Julga TRACADO e COBERTURA, nao pintura fina: a divisa aqui e inequivoca por
construcao. Veredito final e no GLB entregue com HDR (render_dist.py, LICOES
4.5c).

O "antes" e reproduzido desligando as duas mudancas pelas chaves do modulo
(`_arm_cut_vao` devolvendo None e `ARM_AJUSTE_GRAU = 0`), e nao por copia do
codigo velho: copia diverge, chave nao.
"""
import argparse
import math
import os
import sys

import bpy
import numpy as np

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", action="append", required=True)
ap.add_argument("--angulos", default="0,40,70,90")
a = ap.parse_args(argv)
angs = [float(x) for x in a.angulos.split(",")]

smap = S.load_map(root)
_vao = S._arm_cut_vao

for aid in a.id:
    OUT = os.path.join(root, "qa", "peca", aid, "braco")
    os.makedirs(OUT, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master",
                                                    aid + "_master.glb"))
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    H = co[:, 2].max() - co[:, 2].min()
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)

    e = smap[aid]

    def _m(v):
        return [x * H for x in v] if isinstance(v, (list, tuple)) else v * H

    cfg = {"hem_l": _m(e["hem_l_zh"]), "hem_r": _m(e["hem_r_zh"]),
           "hem_center_l": e.get("hem_center_l", [0.0, 0.0]),
           "hem_center_r": e.get("hem_center_r", [0.0, 0.0]),
           "waist": _m(e["waist_zh"])}
    if "faixa_lo_zh" in e:
        cfg["faixa_lo"] = _m(e["faixa_lo_zh"])
        cfg["faixa_hi"] = _m(e["faixa_hi_zh"])
    campo = S.w_field(np, co, cfg) > 0

    lo = float(np.min(np.atleast_1d(cfg["faixa_lo"]))) / H
    hi = float(np.max(np.atleast_1d(cfg["faixa_hi"]))) / H
    z0h = float(co[:, 2].min()) / H

    estados = []
    for nome, usa_vao, grau in (("0_antes", False, 0), ("1_agora", True, 2)):
        S._arm_cut_vao = _vao if usa_vao else (lambda *_a, **_k: None)
        S.ARM_AJUSTE_GRAU = grau
        w = S.w_arm_wide(np, co, H, is_arm, lo - z0h, hi - z0h)
        estados.append((nome, is_arm | w, int(w.sum())))
    S._arm_cut_vao, S.ARM_AJUSTE_GRAU = _vao, 2

    print("== %s   marcados alem do w_limbs: antes %d  agora %d" % (
        aid, estados[0][2], estados[1][2]))

    col = me.color_attributes.new(name="ensaio", type="FLOAT_COLOR",
                                  domain="POINT")
    me.materials.clear()
    me.materials.append(bpy.data.materials.new("ensaio"))
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "VERTEX"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = False
    sc.display.render_aa = "8"
    sc.render.resolution_x, sc.render.resolution_y = 700, 700
    sc.render.film_transparent = False
    cam_d = bpy.data.cameras.new("C")
    cam_d.lens = 70
    cam = bpy.data.objects.new("C", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam

    for nome, paint, _ in estados:
        cores = np.tile(np.array([0.72, 0.73, 0.76, 1.0]), (n, 1))
        cores[campo & (~paint)] = [0.02, 0.02, 0.025, 1.0]
        col.data.foreach_set("color", cores.ravel())
        me.update()
        for ang in angs:
            z0 = co[:, 2].min() + H * 0.72
            r = math.radians(ang)
            cam.location = (2.0 * math.sin(r), -2.0 * math.cos(r), z0)
            cam.rotation_euler = (math.radians(90), 0.0, r)
            sc.render.filepath = os.path.join(OUT, "%s_%03d.png"
                                              % (nome, int(ang)))
            bpy.ops.render.render(write_still=True)

print("RESULT ok")
