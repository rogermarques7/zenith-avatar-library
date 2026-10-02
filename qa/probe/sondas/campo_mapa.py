# -*- coding: utf-8 -*-
"""A MASCARA de um morph pintada no corpo, calculada pelo campo - sem precisar
do shape key no GLB (morph morto nao e gravado).

    blender -b -P qa/probe/sondas/campo_mapa.py -- --id ID [--key morph_shoulder] [--mod scripts/morph.py]

Grava qa/ombro/_campo/{id}_{key}.png: frente | costas | lado | cima, com a
cabeca do umero (C_ombro) marcada em azul quando a Base a tiver.
"""
import importlib.util
import os
import sys

import bpy
import mathutils
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]


def arg(n, p=None):
    return argv[argv.index(n) + 1] if n in argv else p


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MOD = os.path.join(ROOT, arg("--mod", "scripts/morph.py"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
spec = importlib.util.spec_from_file_location("mlab", MOD)
ml = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(ml)
import zenith_paths as _zp  # noqa: E402

AID, KEY = arg("--id"), arg("--key", "morph_shoulder")
OUT = os.path.join(ROOT, "qa", "ombro", "_campo")
os.makedirs(OUT, exist_ok=True)
_, src = _zp.dist_glb_current(ROOT, AID)
ob, co_real, co, mesh, sk = ml.carregar(src)
b = ml.Base(co, mesh, AID)
m, _ = b.campo(co_real)[KEY]

me = ob.data
n = len(me.vertices)
t = np.clip(m, 0, 1)
cor = np.zeros((n, 4))
cor[:, 0] = np.clip(t * 2, 0, 1) * 0.95 + 0.05
cor[:, 1] = np.clip(t * 2 - 1, 0, 1) * 0.9 + 0.05 * (1 - t)
cor[:, 2] = 0.08 * (1 - t) + 0.05
cor[:, 3] = 1
cor[t < 0.02, :3] = 0.55
if hasattr(b, "C_ombro"):
    for sg in (1, -1):
        C = b.C_ombro * np.array([sg, 1, 1])
        perto = np.linalg.norm(co_real - C, axis=1) < 0.012
        cor[perto, :3] = (0.1, 0.3, 1.0)
if ob.data.shape_keys:
    ob.shape_key_clear()
attr = me.color_attributes.new("campo", "FLOAT_COLOR", "POINT")
attr.data.foreach_set("color", cor.ravel())
me.color_attributes.active_color = attr

sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = "VERTEX"
sh.show_xray = False
sc.render.resolution_x = sc.render.resolution_y = 500
sc.view_settings.view_transform = "Standard"
sc.world = bpy.data.worlds.new("W")
cd = bpy.data.cameras.new("c")
cd.type = "ORTHO"
cam = bpy.data.objects.new("c", cd)
sc.collection.objects.link(cam)
sc.camera = cam
zmin = float(co[:, 2].min())
H = float(co[:, 2].max()) - zmin
zc = zmin + 0.76 * H
cd.ortho_scale = 0.62 * H
arqs = []
for nome, loc, rot in (("frente", (0, -4, zc), (1.5708, 0, 0)),
                       ("costas", (0, 4, zc), (1.5708, 0, 3.1416)),
                       ("lado", (4, 0, zc), (1.5708, 0, 1.5708)),
                       ("cima", (0, 0, zmin + H + 3), (0, 0, 0))):
    cam.location = loc
    cam.rotation_euler = mathutils.Euler(rot)
    f = os.path.join(OUT, "_{}_{}_{}.png".format(AID, KEY, nome))
    sc.render.filepath = f
    bpy.ops.render.render(write_still=True)
    arqs.append(f)
img = [bpy.data.images.load(f) for f in arqs]
W = 500
px = np.zeros((500, W * 4, 4), dtype=np.float32)
for i, im in enumerate(img):
    a = np.array(im.pixels[:], dtype=np.float32).reshape(500, 500, 4)
    px[:, i * W:(i + 1) * W] = a
out = bpy.data.images.new("mos", W * 4, 500, alpha=True)
out.pixels = px.ravel()
out.filepath_raw = os.path.join(OUT, "{}_{}.png".format(AID, KEY))
out.file_format = "PNG"
out.save()
print("CAMPO", out.filepath_raw)
