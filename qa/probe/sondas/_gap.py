"""Ha buraco de tecido na FRENTE da faixa, ou e brilho especular no render?
Conta faces pintadas por altura, so nos setores da frente."""
import os, sys
import bpy, bmesh, numpy as np
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
pint = (campos[1] > 0) & ~arm
az = np.arctan2(cent[:, 1], cent[:, 0])
frente = (az > -np.pi * 0.75) & (az < -np.pi * 0.25)
zh = cent[:, 2] / H
print("%s  faixa %.3f .. %.3f" % (aid, e["faixa_lo_zh"], max(np.atleast_1d(e["faixa_hi_zh"]))))
for b in range(int(0.65 * 200), int(0.79 * 200)):
    lo, hi = b / 200.0, (b + 1) / 200.0
    m = frente & (zh >= lo) & (zh < hi)
    tot = int(m.sum()); pin = int((m & pint).sum()); br = int((m & arm).sum())
    print("  %.3f  faces %4d  pintadas %4d  braco %4d  %s" % (
        lo, tot, pin, br, "#" * int(40.0 * pin / max(tot, 1))))
