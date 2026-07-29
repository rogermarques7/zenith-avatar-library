"""Grava em disco o que o detector do cos le da malha, para poder iterar o
ALGORITMO sem reabrir o Blender.

Motivo: cada rodada de `--fit --all` custa ~25 min, e a escolha da curva do cos
ja consumiu tres rodadas inteiras (prior gaussiano, DP, e a comparacao entre as
duas). Nada do que se ajusta nessa escolha depende do Blender - depende do mapa
de concavidade, que e sempre o mesmo para um master que nao mudou. Cacheado, a
iteracao cai para segundos e da para varrer parametro contra as tres reguas.

    blender --background --python scripts/cache_maps.py -- --id X
    (um por avatar; grava qa/probe/maps/{id}.npz)
"""
import os
import sys
import json
import argparse

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
a = ap.parse_args(argv)

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(
    filepath=os.path.join(ROOT, "02_master", a.id + "_master.glb"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
zs = [v.co.z for v in me.vertices]
H = max(zs) - min(zs)
n = len(me.vertices)
co = np.empty(n * 3)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
ov = S.load_map(ROOT).get(a.id, {}).get("crotch_override_zh")
if ov:
    crotch = ov * H
crotch_b = int(crotch / H * S.Z_BINS)

k, _ = S.w_curvature(me, np)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
z = co[:, 2]

# bainha: identica ao w_fit, para o piso do cos bater com o de producao
lids = [0, 1]
mx = [float(co[leg_id == l, 0].mean()) if (leg_id == l).any() else 0.0 for l in lids]
if mx[0] > mx[1]:
    lids.reverse()
hems = []
for lid in lids:
    sel = np.where(leg_id == lid)[0]
    _A, ring, _o = S.w_ring_map(np, co, kn, sel, H, "slice")
    pk = S.w_peaks(np, ring,
                   crotch_b - S.HEM_BELOW_CROTCH[1] * S.Z_BINS,
                   crotch_b - S.HEM_BELOW_CROTCH[0] * S.Z_BINS)
    hems.append(pk[0][1] if pk else int(crotch_b - 0.035 * S.Z_BINS))

torso = np.where((~is_arm) & (z >= crotch))[0]
bs = S.w_back_side_mask(np, S.WAIST_AZ_BINS)
A, ring_t, occ = S.w_ring_map(np, co, kn, torso, H, "axis", S.WAIST_AZ_BINS,
                              az_mask=bs)
pk = S.w_peaks(np, ring_t,
               crotch_b + S.WAIST_ABOVE_CROTCH[0] * S.Z_BINS,
               crotch_b + S.WAIST_ABOVE_CROTCH[1] * S.Z_BINS)
wb = pk[0][1] if pk else int(crotch_b + 0.12 * S.Z_BINS)

out = os.path.join(ROOT, "qa", "probe", "maps")
os.makedirs(out, exist_ok=True)
np.savez_compressed(os.path.join(out, a.id + ".npz"),
                    A=A.astype(np.float32), occ=occ,
                    ring=ring_t.astype(np.float32),
                    meta=np.array([crotch_b, wb, max(hems), min(hems),
                                   1 if pk else 0], dtype=np.int32))
print("CACHE " + json.dumps({"id": a.id, "crotch_b": crotch_b, "waist_b": wb,
                             "hem_b": int(max(hems)), "anel": bool(pk)}))
