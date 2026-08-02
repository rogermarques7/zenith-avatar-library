"""Sonda 5: valida o sinal de BALANCO (normal virada para baixo) na serie toda.

Hipotese a testar, achada no b12_d1: subindo a partir da virilha, a superficie
da frente comeca virada para BAIXO e em algum ponto passa a virada para FORA.
Esse ponto de transicao seria a borda visivel do tecido - o lugar onde a barriga
pendente para de cobrir o short.

Isso importa porque a concavidade NAO serve nos corpos pesados: no centro da
frente do b12_d1 ela e 0.000 em toda a faixa, porque o pannus e um dome liso e
convexo. Vinco nao existe ali para ser achado; balanco existe.

Uma amostra nao vale nada, entao esta sonda roda em todos e imprime o erro
contra a folha, para separar "sinal" de "coincidencia num avatar".

    blender --background --python scripts/probe_nz.py -- --ids a,b,c --refs {json}
"""
import os
import sys
import json
import math
import argparse

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", required=True)
ap.add_argument("--ref", default="")
ap.add_argument("--nzlim", type=float, default=-0.35)
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
nrm = np.empty(n * 3)
me.vertices.foreach_get("normal", nrm)
nrm = nrm.reshape(n, 3)

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
ov = S.load_map(ROOT).get(a.id, {}).get("crotch_override_zh")
if ov:
    crotch = ov * H
crotch_b = int(crotch / H * S.Z_BINS)

k, _ = S.w_curvature(me, np)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
z = co[:, 2]
torso = np.where((~is_arm) & (z >= crotch))[0]
bs = S.w_back_side_mask(np, S.WAIST_AZ_BINS)
_A, ring, _o = S.w_ring_map(np, co, kn, torso, H, "axis", S.WAIST_AZ_BINS, az_mask=bs)
pk = S.w_peaks(np, ring,
               crotch_b + S.WAIST_ABOVE_CROTCH[0] * S.Z_BINS,
               crotch_b + S.WAIST_ABOVE_CROTCH[1] * S.Z_BINS)
wb = pk[0][1] if pk else int(crotch_b + 0.12 * S.Z_BINS)

azv = np.arctan2(co[:, 1], co[:, 0])
zbv = np.clip((co[:, 2] / H * S.Z_BINS).astype(np.int64), 0, S.Z_BINS - 1)
abv = np.clip(((azv + math.pi) / (2 * math.pi) * S.WAIST_AZ_BINS).astype(np.int64),
              0, S.WAIST_AZ_BINS - 1)
sel = ~is_arm
NZ = np.zeros((S.WAIST_AZ_BINS, S.Z_BINS))
CT = np.zeros((S.WAIST_AZ_BINS, S.Z_BINS))
np.add.at(NZ, (abv[sel], zbv[sel]), nrm[sel, 2])
np.add.at(CT, (abv[sel], zbv[sel]), 1.0)

# celula vazia herda a vizinha de baixo: a faixa tem de ser CONTIGUA e um buraco
# de amostragem nao pode corta-la em duas (a ocupacao chega a 32%)
NZs = np.where(CT > 0, NZ / np.maximum(CT, 1), np.nan)
for b in range(1, S.Z_BINS):
    falta = np.isnan(NZs[:, b])
    NZs[falta, b] = NZs[falta, b - 1]

ref = json.loads(a.ref) if a.ref else None
front = S.WAIST_AZ_BINS // 4
half = max(1, S.WAIST_AZ_BINS // 6)
fronts = [(front + d) % S.WAIST_AZ_BINS for d in range(-half, half + 1)]

out = {"id": a.id, "anel": round((wb + 0.5) / S.Z_BINS, 4),
       "virilha": round(crotch / H, 4), "setores": {}}
for j in fronts:
    b = crotch_b
    while b < wb and (np.isnan(NZs[j, b]) or NZs[j, b] < a.nzlim):
        b += 1
    est = (b + 0.5) / S.Z_BINS
    alvo = ref[j] if ref and j < len(ref) and ref[j] is not None else None
    out["setores"][j] = [round(est, 4), alvo]
print("NZRESULT " + json.dumps(out))
