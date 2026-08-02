#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_pannus.py - mede a geometria do avental abdominal e da bainha real.

    blender --background --python qa/probe/sondas/probe_pannus.py -- --id zen_m_b12_d1

Duas perguntas:
  1) a barriga PENDENTE cobre o cos ate que altura, e o que ha embaixo dela?
     Para cada fatia de altura no setor FRONTAL, imprime quantas travessias de
     superficie um raio horizontal encontra. Duas travessias = ha superficie
     escondida atras do avental.
  2) onde esta a bainha REAL na malha da perna? Imprime o perfil de anel
     (quantil da concavidade) por altura, para achar o vinco no olho.
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
a = ap.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master", a.id + "_master.glb"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
zs = co[:, 2]
H = zs.max() - zs.min()

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
entry = S.load_map(root).get(a.id, {})
ov = entry.get("crotch_override_zh")
if ov:
    crotch = ov * H
print("H = {:.4f}   crotch_zh = {:.4f}".format(H, crotch / H))
print("hem no mapa   = {}".format(entry.get("hem_l_zh")))
w = entry.get("waist_zh")
print("waist frente  = {:.4f}   waist costas = {:.4f}".format(min(w), max(w)))

# --- 1) o avental: quantas superficies um raio horizontal frontal atravessa --
# Setor frontal: a frente aponta para -Y.
front = (np.abs(np.arctan2(co[:, 1], co[:, 0]) + math.pi / 2) < math.radians(25)) & (~is_arm)
print("\nfatia frontal (+-25 graus)   |y| = distancia para a frente")
print("{:>7} {:>7} {:>8} {:>8} {:>8}  {}".format(
    "zh", "verts", "y_min", "y_max", "espalh", "histograma de y"))
for b in range(int(0.24 * 60), int(0.62 * 60)):
    lo, hi = b / 60.0 * H + zs.min(), (b + 1) / 60.0 * H + zs.min()
    g = np.where(front & (co[:, 2] >= lo) & (co[:, 2] < hi))[0]
    if g.size < 5:
        continue
    y = co[g, 1]
    h, _ = np.histogram(y, bins=12, range=(y.min(), y.max()))
    bar = "".join("#" if c > g.size * 0.04 else ("." if c else " ") for c in h)
    print("{:>7.3f} {:>7d} {:>8.3f} {:>8.3f} {:>8.3f}  |{}|".format(
        b / 60.0, g.size, y.min(), y.max(), y.max() - y.min(), bar))

# --- 2) a bainha real: perfil de anel na perna ------------------------------
k, _ = S.w_curvature(me, np)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
for lid in (0, 1):
    sel = np.where(leg_id == lid)[0]
    if sel.size < 50:
        continue
    A, ring, _occ = S.w_ring_map(np, co, kn, sel, H, "slice")
    print("\nperna {}  ({} verts)   perfil de anel por altura".format(lid, sel.size))
    cb = int(crotch / H * S.Z_BINS)
    for b in range(cb - int(0.10 * S.Z_BINS), cb + 2):
        zh = (b + 0.5) / S.Z_BINS
        bar = "#" * int(ring[b] * 120)
        print("  {:.4f}  {:.4f} {}".format(zh, ring[b], bar))
print("RESULT ok")
