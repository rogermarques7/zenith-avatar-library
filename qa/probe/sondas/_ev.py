import os, sys
import bpy, numpy as np
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S
aid = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
me = [o for o in bpy.context.scene.objects if o.type == "MESH"][0].data
n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
z = co[:, 2]
start, dst = S.w_adjacency(me, np)
order = np.argsort(z, kind="stable")
rank = np.empty(n, dtype=np.int64); rank[order] = np.arange(n)
parent = list(range(n))
def find(x):
    r = x
    while parent[r] != r: r = parent[r]
    while parent[x] != r: parent[x], x = r, parent[x]
    return r
members = {}
events = []
sig = max(200, int(0.015 * n))
print("n=%d sig=%d" % (n, sig))
for v in order:
    v = int(v); parent[v] = v; members[v] = [v]
    for j in range(start[v], start[v + 1]):
        u = int(dst[j])
        if rank[u] >= rank[v]: continue
        ra, rb = find(u), find(v)
        if ra == rb: continue
        ma, mb = members[ra], members[rb]
        if len(ma) < len(mb): ra, rb, ma, mb = rb, ra, mb, ma
        if len(mb) >= 50 and len(ma) >= 50:
            events.append((float(z[v]), len(mb), len(ma), float(z[np.array(mb)].min())))
        parent[rb] = ra; ma.extend(mb); del members[rb]
for ez, nb, nA, zmin in events[:14]:
    print("  z=%.3f (zh %.3f)  menor=%6d  maior=%7d  zmin_menor=%.3f (zh %.3f) %s" % (
        ez, ez / H, nb, nA, zmin, zmin / H,
        "SIG" if nb >= sig else ""))
