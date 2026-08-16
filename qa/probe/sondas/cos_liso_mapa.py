# -*- coding: utf-8 -*-
"""cos_liso_mapa.py - banco de ensaio do ALISAMENTO do cos.

    blender -b -P qa/probe/sondas/cos_liso_mapa.py -- --id ID [--sigmas 0.7,1.0,1.6]

Le a curva que JA ESTA no shorts_map.json, aplica o w_waist_liso do shorts.py em
varios sigmas e fotografa cada estado em quatro azimutes, por vertex color no
master - sem exportar GLB, sem gastar versao de dist. ~40 s por avatar.

POR QUE UM BANCO, E NAO UM --apply POR TENTATIVA
------------------------------------------------
O sigma e um valor decidido por RENDER, e a LICOES 7.12 cobra o render nos dois
EXTREMOS para um valor desses - senao e chute com cara de calibracao. Fazer isso
com --apply custaria, por tentativa, uma versao de GLB entregue mais um
`morph --apply` por cima (regra 9). Aqui custa 40 s.

⚠️ Este render julga TRACADO, nao PINTURA. Ele pinta preto exatamente onde o
campo do w_field e positivo, entao a divisa e inequivoca e a forma dela se le -
que e a pergunta desta sonda. Se o que estiver em jogo for tinta faltando, a
regua e o qa/probe/sondas/render_dist.py, no GLB entregue com o HDR (LICOES
4.5c).

A saida e um PNG por (estado, angulo) em qa/peca/{id}/liso/. Monte a folha com
qa/probe/sondas/_zoom.py ou com o stitcher do chamador.
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
ap.add_argument("--id", required=True)
ap.add_argument("--sigmas", default="0.7,1.0,1.6")
ap.add_argument("--tetos", default="2")
ap.add_argument("--angulos", default="0,45,90,135")
ap.add_argument("--out", default=None)
ap.add_argument("--escrever", action="store_true",
                help="grava no mapa a curva alisada com o WAIST_LISO_SIGMA "
                     "do shorts.py, sem tocar em mais nada da entrada")
a = ap.parse_args(argv)
OUT = os.path.abspath(a.out or os.path.join(root, "qa", "peca", a.id, "liso"))
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master",
                                                a.id + "_master.glb"))
ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = ob.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
entry = S.load_map(root)[a.id]
base = list(entry["waist_zh"])
piso = float(np.atleast_1d(entry["hem_l_zh"]).max()) + 1.0 / S.Z_BINS


def _canto(w):
    m = len(w)
    return max(abs(w[(i - 1) % m] - 2 * w[i] + w[(i + 1) % m]) for i in range(m))


def _passo(w):
    m = len(w)
    return max(abs(w[i] - w[(i + 1) % m]) for i in range(m))


estados = [("0_atual", base)]
sig0, tet0 = S.WAIST_LISO_SIGMA, S.WAIST_LISO_TETO_BINS
for t in [float(x) for x in a.tetos.split(",")]:
    for s in [float(x) for x in a.sigmas.split(",")]:
        S.WAIST_LISO_SIGMA, S.WAIST_LISO_TETO_BINS = s, t
        estados.append(("s%st%d" % (("%.1f" % s).replace(".", ""), t),
                        S.w_waist_liso(np, base, piso)))
S.WAIST_LISO_SIGMA, S.WAIST_LISO_TETO_BINS = sig0, tet0

print("estado      passo   canto   sobe   desce")
for nome, w in estados:
    print("%-10s %6.3f  %6.3f  %+.3f  %+.3f" % (
        nome, _passo(w), _canto(w),
        max([b - c for c, b in zip(base, w)] + [0.0]),
        max([c - b for c, b in zip(base, w)] + [0.0])))

# ---- pintura por vertex color, sem exportar --------------------------------
col = me.color_attributes.new(name="ensaio", type="FLOAT_COLOR", domain="POINT")
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
cam_d.lens = 55
cam = bpy.data.objects.new("C", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam

angs = [float(x) for x in a.angulos.split(",")]
def _m(v):
    """zh -> metros, aceitando escalar ou lista (o mapa usa os dois)."""
    return [x * H for x in v] if isinstance(v, (list, tuple)) else v * H


for nome, curva in estados:
    cfg = {"hem_l": _m(entry["hem_l_zh"]),
           "hem_r": _m(entry["hem_r_zh"]),
           "hem_center_l": entry.get("hem_center_l", [0.0, 0.0]),
           "hem_center_r": entry.get("hem_center_r", [0.0, 0.0]),
           "waist": [v * H for v in curva]}
    dentro = S.w_field(np, co, cfg) > 0
    cores = np.tile(np.array([0.72, 0.73, 0.76, 1.0]), (n, 1))
    cores[dentro & (~is_arm)] = [0.02, 0.02, 0.025, 1.0]
    col.data.foreach_set("color", cores.ravel())
    me.update()
    for ang in angs:
        z0 = co[:, 2].min() + H * 0.50
        r = math.radians(ang)
        cam.location = (2.2 * math.sin(r), -2.2 * math.cos(r), z0)
        cam.rotation_euler = (math.radians(90), 0.0, r)
        sc.render.filepath = os.path.join(OUT, "%s_%03d.png" % (nome, int(ang)))
        bpy.ops.render.render(write_still=True)

if a.escrever:
    # ⚠️ POR QUE ISTO EXISTE, e por que nao e um `--fit --refit`.
    # Seis masculinos estao marcados `"source": "manual"` no mapa, e o que ha de
    # manual neles NAO e o cos - e a BAINHA (`hem_fonte: anel-xsign`), corrigida
    # a mao em sessoes anteriores. Um `--refit` recalcularia tudo e jogaria essas
    # correcoes fora. Aqui a curva do mapa e a ENTRADA e o alisamento e aplicado
    # em cima dela; nenhum outro campo da entrada e tocado.
    smap = S.load_map(root)
    smap[a.id]["waist_zh"] = [round(v, 5)
                              for v in S.w_waist_liso(np, base, piso)]
    S.save_map(root, smap)
    print("mapa gravado (so waist_zh)")
print("RESULT ok")
