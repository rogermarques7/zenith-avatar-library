"""Visibilidade de CADA ilha de CADA peca, para escolher o limiar com medida.

O VISIVEL_MIN saiu de duas observacoes: ilha interna de verdade mede 0-1% de
livre e a faixa do b05_d3 mede 42%. Entre uma coisa e outra havia um vazio, e o
limiar foi para o meio dele. Quem cai NO vazio precisa aparecer aqui antes de
virar veredito - senao o limiar passa a ser calibrado pelo que ele mesmo
filtrou, que e o defeito que a doutrina da regua externa proibe."""
import os, sys
import bpy, bmesh, numpy as np
from mathutils.bvhtree import BVHTree

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S

aid = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
me = [o for o in bpy.context.scene.objects if o.type == "MESH"][0].data
n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
e = S.load_map(ROOT)[aid]
cfg = {"hem_l": np.atleast_1d(e["hem_l_zh"]) * H, "hem_r": np.atleast_1d(e["hem_r_zh"]) * H,
       "hem_center_l": e["hem_center_l"], "hem_center_r": e["hem_center_r"],
       "waist": [v * H for v in np.atleast_1d(e["waist_zh"])],
       "faixa_lo": e["faixa_lo_zh"] * H,
       "faixa_hi": [v * H for v in np.atleast_1d(e["faixa_hi_zh"])]}
bm = bmesh.new(); bm.from_mesh(me)
bm.faces.ensure_lookup_table(); bm.verts.index_update()
cent = np.array([tuple(f.calc_center_median()) for f in bm.faces])
campos = S.w_field(np, cent, cfg, partes=True)
z0h = co[:, 2].min() / H
is_paint = is_arm | S.w_arm_wide(np, co, H, is_arm,
                                 float(np.min(np.atleast_1d(cfg["faixa_lo"]))) / H - z0h,
                                 float(np.max(np.atleast_1d(cfg["faixa_hi"]))) / H - z0h)
arm = np.array([any(is_paint[v.index] for v in f.verts) for f in bm.faces])
bvh = BVHTree.FromBMesh(bm)


def livre(g):
    am = g[::max(1, len(g) // 200)]
    k = 0
    for f in am:
        p = f.calc_center_median(); d = f.normal.copy()
        if d.length < 1e-9:
            continue
        if bvh.ray_cast(p + d * 0.002, d, 1.0)[0] is None:
            k += 1
    return k / float(len(am))


print("%s  faixa %.3f .. %.3f" % (aid, e["faixa_lo_zh"],
                                  max(np.atleast_1d(e["faixa_hi_zh"]))))
for ip, campo in enumerate(campos):
    sel = set(np.where((campo > 0) & ~arm)[0].tolist())
    visto, ilhas = set(), []
    for i in sel:
        if i in visto:
            continue
        pil, fila = [], [i]; visto.add(i)
        while fila:
            j = fila.pop(); f = bm.faces[j]; pil.append(f)
            for ed in f.edges:
                for o in ed.link_faces:
                    if o.index in sel and o.index not in visto:
                        visto.add(o.index); fila.append(o.index)
        ilhas.append(pil)
    ilhas.sort(key=len, reverse=True)
    print("  peca %d: %d ilhas" % (ip, len(ilhas)))
    for g in ilhas[:6]:
        z = np.array([f.calc_center_median().z for f in g]) / H
        x = np.array([f.calc_center_median().x for f in g]) / H
        y = np.array([f.calc_center_median().y for f in g]) / H
        print("    %6d faces  livre %5.1f%%  zh %.3f..%.3f  x %+.3f..%+.3f"
              "  y %+.3f..%+.3f  %s" % (
                  len(g), 100.0 * livre(g), z.min(), z.max(), x.min(), x.max(),
                  y.min(), y.max(),
                  "cruza o meio" if x.min() < 0 < x.max() else "so de um lado"))
