# -*- coding: utf-8 -*-
"""SUBIDA E DESCIDA do pescoco por TIPO de corpo, no GLB entregue.

    blender -b -P qa/probe/sondas/pescoco_tipos.py -- --ids a,b,c --out DIR [--glb-dir DIR]
    python qa/probe/sondas/pescoco_tipos.py --folha DIR "titulo"      (fora do Blender)

Para cada avatar: base, morph_neck no MAXIMO e no MINIMO publicados no mapa
(o que o slider do app alcanca), em frente / 3-4 / lado / costas. Clay com
cavidade, lente longa, camera por matriz (mesma para os tres estados).
Pedido de 01/10: "ao finalizar um tipo de corpo suba o slider do pescoco ao
maximo e compare ... pra ver se nao cai no vale da estranheza".
"""
import json
import math
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VISTAS_TODAS = [("frente", 0), ("tresq", 35), ("lado", 90), ("costas", 180)]


def arg(n, p=None):
    return argv[argv.index(n) + 1] if n in argv else p


VISTAS = [v for v in VISTAS_TODAS if v[0] in arg("--vistas", "frente,tresq,lado,costas").split(",")]
ESTADOS = arg("--estados", "base,max,min").split(",")


def folha(d, tit):
    from PIL import Image, ImageDraw
    meta = json.load(open(os.path.join(d, "_meta.json"), encoding="utf8"))
    esc = 0.36
    im0 = Image.open(os.path.join(d, meta[0]["id"] + "_base_frente.png"))
    w, h = int(im0.width * esc), int(im0.height * esc)
    fx = 16
    W = 3 * len(VISTAS) * w + 2 * 10
    o = Image.new("RGB", (W, fx + len(meta) * (h + fx)), (20, 20, 22))
    dr = ImageDraw.Draw(o)
    dr.text((6, 2), tit, fill=(230, 230, 230))
    for li, m in enumerate(meta):
        y = fx + li * (h + fx)
        for bi, (est, rot) in enumerate((("base", "base {:.1f} cm".format(m["base_cm"])),
                                         ("max", "MAX {:+.2f} = {:+.1f} cm".format(m["inf_max"], m["cm_max"])),
                                         ("min", "MIN {:+.2f} = {:+.1f} cm".format(m["inf_min"], m["cm_min"])))):
            x0 = bi * (len(VISTAS) * w + 10)
            dr.text((x0 + 6, y + 2), "{}  {}  [{}]".format(m["id"], rot, m["tipo"]), fill=(230, 230, 120))
            for ci, (v, _) in enumerate(VISTAS):
                p = os.path.join(d, "{}_{}_{}.png".format(m["id"], est, v))
                if os.path.exists(p):
                    o.paste(Image.open(p).convert("RGB").resize((w, h)), (x0 + ci * w, y + fx))
    o.save(os.path.join(d, "_folha.png"))
    print(os.path.join(d, "_folha.png"), o.size)


def render():
    import bpy
    import mathutils
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import zenith_paths as _zp
    ids = arg("--ids").split(",")
    out = os.path.abspath(arg("--out"))
    os.makedirs(out, exist_ok=True)
    gdir = arg("--glb-dir")
    mapa = json.load(open(os.path.join(ROOT, "config", "morph_map.json"), encoding="utf8"))
    lib = {a["id"]: a for a in json.load(open(os.path.join(ROOT, "library.json"),
                                              encoding="utf8"))["avatars"]}
    meta = []
    for aid in ids:
        glb = os.path.join(gdir, aid + ".glb") if gdir else _zp.dist_glb_current(ROOT, aid)[1]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=glb)
        obs = [o for o in bpy.data.objects if o.type == "MESH"]
        sc = bpy.context.scene
        sc.render.engine = "BLENDER_WORKBENCH"
        sh = sc.display.shading
        sh.light, sh.color_type = "STUDIO", "SINGLE"
        sh.single_color = (0.62, 0.63, 0.66)
        sh.show_cavity, sh.cavity_type = True, "BOTH"
        sh.cavity_ridge_factor = sh.cavity_valley_factor = 1.6
        sc.display.render_aa = "8"
        sc.render.resolution_x, sc.render.resolution_y = int(arg("--res", "520")), int(int(arg("--res", "520")) * 560 / 520)
        sc.view_settings.view_transform = "Standard"
        sc.world = bpy.data.worlds.new("W")
        cd = bpy.data.cameras.new("c")
        cd.lens = 200
        cam = bpy.data.objects.new("c", cd)
        sc.collection.objects.link(cam)
        sc.camera = cam
        H = max((o.matrix_world @ v.co).z for o in obs for v in o.data.vertices)
        alvo = mathutils.Vector((0.0, 0.0, 0.84 * H))
        mk = [m for m in mapa[aid]["morphs"] if m["key"] == "morph_neck"]
        mk = mk[0] if mk else {"influence_max": 0, "influence_min": 0, "cm_max": 0,
                               "cm_min": 0, "base_cm": lib[aid]["circumferences_cm"]["neck"]}
        a = lib[aid]
        meta.append({"id": aid, "base_cm": mk["base_cm"], "inf_max": mk["influence_max"],
                     "inf_min": mk["influence_min"], "cm_max": mk["cm_max"], "cm_min": mk["cm_min"],
                     "tipo": "{} IMC {:.0f} {}".format(a["sex"], a["measured_bmi"], a["definition"])})
        for est, inf in [e for e in (("base", 0.0), ("max", mk["influence_max"]),
                                     ("min", mk["influence_min"])) if e[0] in ESTADOS]:
            for o in obs:
                if o.data.shape_keys:
                    for k in o.data.shape_keys.key_blocks:
                        k.slider_min, k.slider_max = -3.0, 3.0
                        k.value = inf if k.name == "morph_neck" else 0.0
            for vn, ang in VISTAS:
                t = math.radians(ang)
                dist = 2.53
                cam.location = alvo + mathutils.Vector((dist * math.sin(t), -dist * math.cos(t), 0.0))
                cam.rotation_euler = (alvo - cam.location).to_track_quat("-Z", "Y").to_euler()
                sc.render.filepath = os.path.join(out, "{}_{}_{}.png".format(aid, est, vn))
                bpy.ops.render.render(write_still=True)
    json.dump(meta, open(os.path.join(out, "_meta.json"), "w", encoding="utf8"), indent=1)
    print("TIPOS feito", out)


if __name__ == "__main__":
    if "--folha" in argv:
        folha(arg("--folha"), argv[argv.index("--folha") + 2] if len(argv) > argv.index("--folha") + 2 else "")
    else:
        render()
