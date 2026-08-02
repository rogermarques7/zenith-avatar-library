"""Quantas faces caem em CADA peca do campo, antes de qualquer filtro?

O b05_d3 saiu com por_peca [1, 0] e 7152 escondidas, e da para ler isso de duas
maneiras opostas: ou a faixa foi pintada e o teste de visibilidade a jogou fora,
ou o campo da faixa nao pegou face nenhuma. As duas dao a mesma linha no log.
Aqui elas se separam."""
import os, sys
import bpy, bmesh, numpy as np

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
bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.index_update()
cent = np.array([tuple(f.calc_center_median()) for f in bm.faces])
campos = S.w_field(np, cent, cfg, partes=True)
arm = np.array([any(is_arm[v.index] for v in f.verts) for f in bm.faces])

print("%s  faces %d  faixa %.3f .. %.3f" % (
    aid, len(bm.faces), e["faixa_lo_zh"], max(np.atleast_1d(e["faixa_hi_zh"]))))
for ip, campo in enumerate(campos):
    dentro = campo > 0
    print("  peca %d: campo>0 %6d   sem braco %6d" % (
        ip, int(dentro.sum()), int((dentro & ~arm).sum())))

from mathutils.bvhtree import BVHTree
bvh = BVHTree.FromBMesh(bm)
print("  altura do corpo em unidades: %.3f" % H)
for ip, campo in enumerate(campos):
    idx = np.where((campo > 0) & ~arm)[0]
    if idx.size == 0:
        continue
    am = idx[::max(1, idx.size // 300)]
    fora_n = fora_i = 0
    dist = []
    for i in am:
        f = bm.faces[int(i)]
        p = f.calc_center_median(); d = f.normal.copy()
        h1 = bvh.ray_cast(p + d * 0.002, d, 1.0)
        h2 = bvh.ray_cast(p - d * 0.002, -d, 1.0)
        if h1[0] is None:
            fora_n += 1
        elif h1[3] is not None:
            dist.append(h1[3])
        if h2[0] is None:
            fora_i += 1
    print("  peca %d: livre pela normal %.0f%%, livre pelo avesso %.0f%%, "
          "distancia mediana do que bate %.4f" % (
              ip, 100.0 * fora_n / len(am), 100.0 * fora_i / len(am),
              float(np.median(dist)) if dist else -1))

# a faixa mora acima da virilha; quanto do tronco o is_arm come naquela altura?
zh = cent[:, 2] / H
lo, hi = e["faixa_lo_zh"], max(np.atleast_1d(e["faixa_hi_zh"]))
band = (zh >= lo) & (zh <= hi)
print("  na altura da faixa: faces %d, braco %d (%.0f%%)" % (
    int(band.sum()), int((band & arm).sum()),
    100.0 * (band & arm).sum() / max(1, band.sum())))
