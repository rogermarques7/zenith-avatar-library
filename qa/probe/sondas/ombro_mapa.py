# -*- coding: utf-8 -*-
"""ONDE o shape key age: mapa de calor do deslocamento, em ortografica.

    blender -b -P qa/probe/sondas/ombro_mapa.py -- --id zen_m_b05h_d2 [--key morph_shoulder|all] [--glb F] [--out DIR]

Le o GLB ENTREGUE (o que o app baixa), pega o shape key pedido em influence
1,0 e pinta cada vertice pela magnitude do deslocamento (cinza = parado,
vermelho -> amarelo = ate o maximo). Vistas ortograficas niveladas - frente,
costas, lado, cima.

Existe porque a queixa (25/09) e de LOCALIZACAO ("a localizacao deles estava
um pouco errada, principalmente nos ombros"), e o `morph_folha.py` mostra o
RESULTADO do morph, nao ONDE ele mora. Localizacao se ve no mapa do campo.
Com `--key all` percorre todos os shape keys e grava `_todos.png`.
"""
import bpy
import sys
import os
import json
import mathutils
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]


def arg(nome, padrao=None):
    return argv[argv.index(nome) + 1] if nome in argv else padrao


AID = arg("--id")
KEY = arg("--key", "morph_shoulder")
GLB = arg("--glb")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.abspath(arg("--out", os.path.join(ROOT, "qa", "ombro", AID)))
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import zenith_paths as _zp  # noqa: E402

if GLB is None:
    _, GLB = _zp.dist_glb_current(ROOT, AID)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
obs = [o for o in bpy.data.objects if o.type == "MESH"]
ob = obs[0]
me = ob.data
mw = np.array(ob.matrix_world)
kb = me.shape_keys.key_blocks
n = len(me.vertices)


def co_de(block):
    a = np.zeros(n * 3)
    block.data.foreach_get("co", a)
    a = a.reshape(-1, 3)
    return (np.c_[a, np.ones(n)] @ mw.T)[:, :3]


base = co_de(kb[0])
zmin, H = base[:, 2].min(), base[:, 2].max() - base[:, 2].min()
zf = (base[:, 2] - zmin) / H
KEYS = [k.name for k in kb][1:] if KEY == "all" else [KEY]
TUDO = KEY == "all"

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "VERTEX"
sh.show_cavity = True
sh.cavity_type = "BOTH"
sc.display.render_aa = "8"
sc.render.resolution_x = 500 if TUDO else 700
sc.render.resolution_y = 700
sc.view_settings.view_transform = "Standard"
sc.world = bpy.data.worlds.new("W")
for o in obs:
    if o is not ob:
        o.hide_render = True
cd = bpy.data.cameras.new("c")
cd.type = "ORTHO"
cam = bpy.data.objects.new("c", cd)
sc.collection.objects.link(cam)
sc.camera = cam
if TUDO:                                  # corpo inteiro
    zc, cd.ortho_scale = zmin + 0.52 * H, 1.08 * H
    VISTAS = ["frente", "costas", "lado"]
else:                                     # so o tronco de cima
    zc, cd.ortho_scale = zmin + 0.78 * H, 0.57 * H
    VISTAS = ["frente", "costas", "lado", "cima"]
POSE = {
    "frente": ((0, -4, zc), (1.5708, 0, 0)),
    "costas": ((0, 4, zc), (1.5708, 0, 3.1416)),
    "lado":   ((4, 0, zc), (1.5708, 0, 1.5708)),
    "cima":   ((0, 0, zmin + H + 3), (0, 0, 0)),
}
attr = me.color_attributes.new("calor", "FLOAT_COLOR", "POINT")
me.color_attributes.active_color = attr


def um(key):
    d = co_de(kb[key]) - base
    mag = np.linalg.norm(d, axis=1)
    w = mag / max(mag.max(), 1e-9)
    sel = w > 0.5
    res = {
        "id": AID, "key": key, "max_mm": float(mag.max() * 1000),
        "z_frac_plato": [float(zf[sel].min()), float(zf[sel].max())] if sel.any() else None,
        "z_frac_centro": float((zf * w).sum() / w.sum()),
        "absx_plato_cm": [float(np.abs(base[sel, 0]).min() * 100),
                          float(np.abs(base[sel, 0]).max() * 100)] if sel.any() else None,
        "comp_xyz": [float(np.abs(d[:, i]).sum() / max(np.abs(d).sum(), 1e-9)) for i in range(3)],
    }
    print("OMBRO_MAPA", json.dumps(res))
    t = np.clip(w, 0, 1)
    cor = np.zeros((n, 4))
    cor[:, 0] = np.clip(t * 2, 0, 1) * 0.95 + 0.05
    cor[:, 1] = np.clip(t * 2 - 1, 0, 1) * 0.9 + 0.05 * (1 - t)
    cor[:, 2] = 0.08 * (1 - t) + 0.05
    cor[:, 3] = 1
    cor[t < 0.02, :3] = 0.55
    attr.data.foreach_set("color", cor.ravel())
    me.update()
    arqs = []
    for nome in VISTAS:
        loc, rot = POSE[nome]
        cam.location = loc
        cam.rotation_euler = mathutils.Euler(rot)
        f = os.path.join(OUT, "{}_{}.png".format(key, nome))
        sc.render.filepath = f
        bpy.ops.render.render(write_still=True)
        arqs.append(f)
    return res, arqs


todos = []
for k in KEYS:
    todos.append(um(k))
json.dump([r for r, _ in todos], open(os.path.join(OUT, "resumo_{}.json".format(KEY)), "w"), indent=1)

try:
    from PIL import Image, ImageDraw
    fs = [a for _, arqs in todos for a in arqs]
    ims = [Image.open(f).convert("RGB") for f in fs]
    cols = len(VISTAS) * (2 if TUDO else 1)
    lin = (len(ims) + cols - 1) // cols
    w0, h0 = ims[0].size
    o = Image.new("RGB", (w0 * cols, h0 * lin), (40, 40, 40))
    dr = ImageDraw.Draw(o)
    for i, im in enumerate(ims):
        x, y = (i % cols) * w0, (i // cols) * h0
        o.paste(im, (x, y))
        if i % len(VISTAS) == 0:
            dr.text((x + 8, y + 8), todos[i // len(VISTAS)][0]["key"], fill=(255, 255, 255))
    o.save(os.path.join(OUT, "_todos.png" if TUDO else "_mosaico_{}.png".format(KEY)))
except ImportError:
    pass
