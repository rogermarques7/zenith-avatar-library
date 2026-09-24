# -*- coding: utf-8 -*-
"""faixa_tres_cores.py - onde a mascara do braco CAI, em tres cores.

    blender -b -P qa/probe/sondas/faixa_tres_cores.py -- --id ID [--id ID2 ...]

    preto     roupa pintada  (campo da peca E fora da mascara)
    vermelho  mascara do braco DENTRO da banda da faixa
    cinza     corpo

Existe porque o banco de duas cores (faixa_braco_mapa, faixa_normal_mapa)
mostra o RESULTADO e esconde a CAUSA: preto sobrando pode ser mascara que nao
alcancou o braco ou mascara que nem existe naquela fatia, e as duas pedem
consertos opostos. Com o vermelho a pergunta vira visual - a mascara chegou ate
o braco, ou ela esta pendurada no ar longe dele?

E imprime, por fatia da banda, a maior |x| da propria fatia ao lado do corte: se
o corte for MAIOR que o raio da fatia, aquela fatia nao mascara nada e a faixa
sai pintada de ponta a ponta, braco incluso. Foi esse o caso que a sonda achou.
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
ap.add_argument("--angulos", default="140,180")
a = ap.parse_args(argv)
angs = [float(x) for x in a.angulos.split(",")]

smap = S.load_map(root)

for aid in a.id:
    OUT = os.path.join(root, "qa", "peca", aid, "cores")
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
    nor = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("normal", nor)
    nor = nor.reshape(n, 3)
    H = co[:, 2].max() - co[:, 2].min()
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)

    e = smap[aid]

    def _m(v):
        return [x * H for x in v] if isinstance(v, (list, tuple)) else v * H

    cfg = {"hem_l": _m(e["hem_l_zh"]), "hem_r": _m(e["hem_r_zh"]),
           "hem_center_l": e.get("hem_center_l", [0.0, 0.0]),
           "hem_center_r": e.get("hem_center_r", [0.0, 0.0]),
           "waist": _m(e["waist_zh"])}
    if "faixa_lo_zh" not in e:
        print("%s nao tem faixa" % aid)
        continue
    cfg["faixa_lo"] = _m(e["faixa_lo_zh"])
    cfg["faixa_hi"] = _m(e["faixa_hi_zh"])
    campo = S.w_field(np, co, cfg) > 0

    lo = float(np.min(np.atleast_1d(cfg["faixa_lo"]))) / H
    hi = float(np.max(np.atleast_1d(cfg["faixa_hi"]))) / H
    z0h = float(co[:, 2].min()) / H

    diag = {}
    w = S.w_arm_wide(np, co, H, is_arm, lo - z0h, hi - z0h, diag=diag, nor=nor)
    paint = is_arm | w

    zh = (co[:, 2] - co[:, 2].min()) / H
    cx = float(np.median(co[:, 0]))
    passo = diag["passo"]
    print("== %s   faixa %.3f..%.3f   mascara %d" % (aid, lo, hi, int(w.sum())))
    print("      zh    raioE    corteE    raioD    corteD   cobre?")
    for i, z in enumerate(diag["zh"]):
        fatia = np.where((zh >= z) & (zh < z + passo))[0]
        if not len(fatia):
            continue
        x = co[fatia, 0] - cx
        linha = ["  %.3f" % z]
        cobre = []
        for sinal in (-1.0, 1.0):
            lado = x[np.sign(x) == sinal] * sinal
            raio = float(lado.max()) if len(lado) else 0.0
            c = diag["suave"][sinal][i] if sinal in diag["suave"] \
                else diag["suave"][str(sinal)][i]
            linha.append("  %7.4f  %8s" % (raio, "-" if c is None
                                           else "%.4f" % c))
            cobre.append("nao" if (c is None or c >= raio) else "sim")
        print("".join(linha) + "   " + "/".join(cobre))

    col = me.color_attributes.new(name="tres", type="FLOAT_COLOR",
                                  domain="POINT")
    me.materials.clear()
    me.materials.append(bpy.data.materials.new("tres"))
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "VERTEX"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = False
    sc.display.render_aa = "8"
    sc.render.resolution_x, sc.render.resolution_y = 800, 800
    sc.render.film_transparent = False
    cam_d = bpy.data.cameras.new("C")
    cam_d.lens = 70
    cam = bpy.data.objects.new("C", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam

    na_banda = (zh >= lo - z0h - 0.01) & (zh <= hi - z0h + 0.01)
    cores = np.tile(np.array([0.72, 0.73, 0.76, 1.0]), (n, 1))
    cores[campo & (~paint)] = [0.02, 0.02, 0.025, 1.0]
    cores[w & na_banda] = [0.85, 0.10, 0.10, 1.0]
    col.data.foreach_set("color", cores.ravel())
    me.update()
    for ang in angs:
        z0 = co[:, 2].min() + H * 0.72
        r = math.radians(ang)
        cam.location = (2.0 * math.sin(r), -2.0 * math.cos(r), z0)
        cam.rotation_euler = (math.radians(90), 0.0, r)
        sc.render.filepath = os.path.join(OUT, "tres_%03d.png" % int(ang))
        bpy.ops.render.render(write_still=True)

print("RESULT ok")
