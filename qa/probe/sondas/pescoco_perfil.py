# -*- coding: utf-8 -*-
"""PERFIL RADIAL do pescoco: R(altura, angulo) na base e nos extremos do morph.

    blender -b -P qa/probe/sondas/pescoco_perfil.py -- --ids LISTA.txt --out SAIDA.json
            [--glb-dir DIR]   (le {DIR}/{id}.glb em vez do dist corrente)
            [--so-base]       (so a base: entrada do scripts/pescoco_campo.py)
            [--infs 1,-0.5]   (estados R@+1.00 ... com o morph_neck do proprio GLB)

Existe para a pauta de 01/10 ("cada tipo de corpo engrossa o pescoco de um
jeito"). A malha de cada avatar tem topologia propria, entao nao da para
comparar vertice com vertice entre corpos - mas da para comparar o RAIO que um
raio horizontal, saindo do eixo do pescoco, encontra na superficie. Isso e
independente de topologia: R(h, theta) do magro, do pesado e do musculoso vivem
na mesma grade, e a diferenca entre eles diz ONDE o volume extra mora.

Mede tres estados por avatar: base, morph_neck no teto positivo do mapa e no
teto negativo. Primeiro acerto do raio (BVH), media dos dois lados.
theta = 0 frente, 90 lado, 180 nuca. h em fracao da altura.
"""
import bpy
import sys
import os
import json
import math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:]


def arg(nome, padrao=None):
    return argv[argv.index(nome) + 1] if nome in argv else padrao


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import zenith_paths as _zp  # noqa: E402

IDS = [l.strip() for l in open(arg("--ids"), encoding="utf8") if l.strip()]
OUT = arg("--out")
GLB_DIR = arg("--glb-dir")
INFS = [float(x) for x in arg("--infs", "").split(",") if x]  # estados extras R@inf
SO_BASE = "--so-base" in argv   # so R0 - e o que o scripts/pescoco_campo.py le
MAPA = json.load(open(os.path.join(ROOT, "config", "morph_map.json"), encoding="utf8"))

HS = np.round(np.arange(0.760, 0.9301, 0.0025), 4)
THS = np.arange(0, 181, 15)


def carregar(glb):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    ob = [o for o in bpy.data.objects if o.type == "MESH"][0]
    me = ob.data
    n = len(me.vertices)
    mw = np.array(ob.matrix_world)

    def co(block):
        a = np.zeros(n * 3)
        block.data.foreach_get("co", a)
        a = a.reshape(-1, 3)
        return (np.c_[a, np.ones(n)] @ mw.T)[:, :3]
    kb = me.shape_keys.key_blocks if me.shape_keys else None
    base = co(kb[0]) if kb else co(me)
    neck = (co(kb["morph_neck"]) - base) if kb and "morph_neck" in kb else None
    polys = [tuple(p.vertices) for p in me.polygons]
    return base, neck, polys


def eixo(co, z, H):
    # frente pelos PES (o dedo vai mais longe do tornozelo que o calcanhar).
    # O criterio antigo - lado do rosto mais longe de y=0 - erra em 30 de 103:
    # num corpo pesado o centro da caixa vai para a frente e a nuca fica mais
    # longe que o nariz (sessao 42, 01/10).
    pe = co[co[:, 2] < z + 0.02 * H]
    cy = co[(co[:, 2] > z + 0.04 * H) & (co[:, 2] < z + 0.06 * H)][:, 1].mean()
    frente = 1.0 if (pe[:, 1].max() - cy) > (cy - pe[:, 1].min()) else -1.0
    zs = np.arange(z + 0.80 * H, z + 0.92 * H, 0.005)
    cen = np.array([co[np.abs(co[:, 2] - t) < 0.006][:, :2].mean(axis=0) for t in zs])
    nx, ny = float(cen[:, 0].mean()), float(cen[:, 1].mean())
    raios = []
    for t in zs:
        b = co[np.abs(co[:, 2] - t) < 0.005]
        fr = b[:, 1] * frente > ny * frente
        raios.append(float(np.sqrt((b[fr, 0] - nx) ** 2 + (b[fr, 1] - ny) ** 2).max())
                     if fr.any() else 0.0)
    raios = np.array(raios)
    i = int(np.argmin(raios))
    salto = np.where(raios[i:] > raios[i] * 1.25)[0]
    zq = float(zs[i + salto[0]]) if len(salto) else float(zs[-1])
    return frente, nx, ny, zq


def perfil(co, polys, nx, ny, frente, z, H):
    bvh = BVHTree.FromPolygons([Vector(v) for v in co], polys)
    R = np.full((len(HS), len(THS)), np.nan)
    for i, h in enumerate(HS):
        zz = z + h * H
        for j, th in enumerate(THS):
            t = math.radians(th)
            vals = []
            for sx in (+1.0, -1.0):
                d = Vector((sx * math.sin(t), frente * math.cos(t), 0.0))
                hit = bvh.ray_cast(Vector((nx, ny, zz)), d, 0.30)
                if hit[0] is not None:
                    vals.append(hit[3])
            if vals:
                R[i, j] = float(np.mean(vals))
    return R


saida = {"hs": HS.tolist(), "ths": THS.tolist(), "avatars": {}}
if OUT and os.path.exists(OUT):
    saida = json.load(open(OUT, encoding="utf8"))
for aid in IDS:
    if aid in saida["avatars"]:
        continue
    glb = os.path.join(GLB_DIR, aid + ".glb") if GLB_DIR else _zp.dist_glb_current(ROOT, aid)[1]
    base, neck, polys = carregar(glb)
    z, H = float(base[:, 2].min()), float(base[:, 2].max() - base[:, 2].min())
    frente, nx, ny, zq = eixo(base, z, H)
    e = {"H": H, "z_queixo_h": (zq - z) / H, "nx": nx, "ny": ny}
    e["R0"] = perfil(base, polys, nx, ny, frente, z, H).tolist()
    mk = [m for m in MAPA.get(aid, {}).get("morphs", []) if m["key"] == "morph_neck"]
    if neck is not None and mk and not SO_BASE:
        mk = mk[0]
        e["inf"] = [mk["influence_min"], mk["influence_max"]]
        e["cm"] = [mk["cm_min"], mk["cm_max"]]
        e["base_cm"] = mk["base_cm"]
        for nome, inf in (("Rp", mk["influence_max"]), ("Rm", mk["influence_min"]),
                          ("Rp1", 1.0), ("Rm1", -1.0)):
            e[nome] = perfil(base + neck * inf, polys, nx, ny, frente, z, H).tolist()
    if neck is not None and INFS:
        for inf in INFS:
            e["R@{:+.2f}".format(inf)] = perfil(base + neck * inf, polys, nx, ny, frente, z, H).tolist()
    saida["avatars"][aid] = e
    print("ok", aid, "queixo", round(e["z_queixo_h"], 4))
    json.dump(saida, open(OUT, "w", encoding="utf8"))
