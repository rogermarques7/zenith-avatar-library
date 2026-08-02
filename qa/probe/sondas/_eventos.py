"""TODOS os eventos grandes de fusao do union-find, sem filtro de braco.

O w_limbs so aceita como braco o evento que passa em tres testes ao mesmo
tempo (comeca acima de 0.20 H, funde abaixo de 0.85 H, e se estende por pelo
menos 0.15 H). No zen_f_b12_d1 nenhum evento passa - arm_verts sai 0 e os dois
bracos vao pintados de preto, com a faixa atravessando os dois. Antes de mexer
no filtro e preciso ver o que a malha oferece: se ha um evento de braco que
reprova por pouco em UM dos testes, o conserto e outro do que se nao ha evento
de braco nenhum.

    blender -b -P qa/probe/sondas/_eventos.py -- --root . --id zen_f_b12_d1
"""
import argparse
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--id", required=True)
a = ap.parse_args(argv)

ROOT = os.path.abspath(a.root)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import bpy  # noqa: E402
import shorts as S  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master",
                                                a.id + "_master.glb"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
z = co[:, 2]
H = float(z.max() - z.min())

start, dst = S.w_adjacency(me, np)
order = np.argsort(z, kind="stable")
rank = np.empty(n, dtype=np.int64)
rank[order] = np.arange(n)
parent = list(range(n))


def find(x):
    r = x
    while parent[r] != r:
        r = parent[r]
    while parent[x] != r:
        parent[x], x = r, parent[x]
    return r


members, events = {}, []
sig = max(200, int(0.015 * n))
for v in order:
    v = int(v)
    parent[v] = v
    members[v] = [v]
    for j in range(start[v], start[v + 1]):
        u = int(dst[j])
        if rank[u] >= rank[v]:
            continue
        ra, rb = find(u), find(v)
        if ra == rb:
            continue
        ma, mb = members[ra], members[rb]
        if len(ma) < len(mb):
            ra, rb, ma, mb = rb, ra, mb, ma
        if len(mb) >= sig and len(ma) >= sig:
            events.append((float(z[v]), list(mb), list(ma)))
        parent[rb] = ra
        ma.extend(mb)
        del members[rb]

print("%s   H=%.4f   limiar de evento grande = %d vertices" % (a.id, H, sig))
print("%-6s %8s %8s %8s %8s   %s" % ("i", "funde_zh", "n", "base_zh", "ext_zh",
                                     "testes de braco"))
for i, (ez, sm, _bg) in enumerate(events):
    sm = np.array(sm, dtype=np.int64)
    base, ext = z[sm].min(), ez - z[sm].min()
    t = []
    t.append("base>0.20 %s" % ("ok" if base > 0.20 * H else "NAO"))
    t.append("funde<0.85 %s" % ("ok" if ez < 0.85 * H else "NAO"))
    t.append("ext>=0.15 %s" % ("ok" if ext >= 0.15 * H else "NAO"))
    print("%-6d %8.4f %8d %8.4f %8.4f   %s" % (
        i, ez / H, len(sm), base / H, ext / H, "  ".join(t)))
    if i >= 14:
        print("   (... %d eventos no total)" % len(events))
        break
