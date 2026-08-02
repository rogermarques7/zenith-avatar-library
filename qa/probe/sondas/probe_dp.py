"""Sonda 4: a DP prefere o caminho RETO ou o caminho da FOLHA, e por quanto?

Se o detector nao desce, so ha duas causas possiveis: ou o ganho no fundo nao
existe (problema de sinal), ou existe e nao paga o custo do degrau (problema de
LAMBDA). Esta sonda separa as duas imprimindo o ganho celula a celula nos dois
caminhos, em vez de deixar a escolha implicita dentro da DP.

    blender --background --python scripts/probe_dp.py -- --id X --ref "[...]"
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
ap.add_argument("--ref", default="")
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
torso = np.where((~is_arm) & (z >= crotch))[0]
bs = S.w_back_side_mask(np, S.WAIST_AZ_BINS)
A, ring, occ = S.w_ring_map(np, co, kn, torso, H, "axis", S.WAIST_AZ_BINS, az_mask=bs)
pk = S.w_peaks(np, ring,
               crotch_b + S.WAIST_ABOVE_CROTCH[0] * S.Z_BINS,
               crotch_b + S.WAIST_ABOVE_CROTCH[1] * S.Z_BINS)
wb = pk[0][1] if pk else int(crotch_b + 0.12 * S.Z_BINS)
Af = S.w_fill_holes(np, A, occ)

ref = json.loads(a.ref) if a.ref else None
front = S.WAIST_AZ_BINS // 4
half = max(1, S.WAIST_AZ_BINS // 6)
fronts = [(front + d) % S.WAIST_AZ_BINS for d in range(-half, half + 1)]

print("PROBE_DP {}  anel bin {} (zh {:.4f})  LAMBDA {}  passo {}".format(
    a.id, wb, (wb + 0.5) / S.Z_BINS, S.WAIST_LAMBDA, S.WAIST_STEP_MAX_B))
print("  ocupacao na frente: {:.0f}%".format(
    100 * np.mean(occ[np.ix_(fronts, range(crotch_b, wb + 1))])))
print("\n  {:>4} {:>8} {:>8} {:>8} {:>8}".format(
    "setor", "alvo_zh", "ganho_alvo", "ganho_anel", "vantagem"))
tot = 0.0
for j in fronts:
    if not ref or ref[j] is None:
        continue
    b = int(ref[j] * S.Z_BINS)
    b = max(0, min(S.Z_BINS - 1, b))
    ga, gr = Af[j, b], Af[j, wb]
    tot += ga - gr
    print("  {:>4} {:>8.4f} {:>10.3f} {:>10.3f} {:>+9.3f}".format(
        j, ref[j], ga, gr, ga - gr))
print("\n  ganho total do caminho da folha sobre o reto: {:+.3f}".format(tot))
prof = max(abs(int(ref[j] * S.Z_BINS) - wb) for j in fronts
           if ref and ref[j] is not None)
print("  custo do degrau para descer {} bins e voltar: {:.3f}".format(
    prof, 2 * prof * S.WAIST_LAMBDA))
print("  => a DP {} descer".format("DEVE" if tot > 2 * prof * S.WAIST_LAMBDA
                                   else "NAO vai"))
print("\n  perfil de ganho no setor central (s{}):".format(front))
for b in range(crotch_b, wb + 2, 2):
    v = Af[front, b]
    print("   zh {:.4f}  {:6.3f}  {}{}".format(
        (b + 0.5) / S.Z_BINS, v, "#" * int(v * 40),
        "   <- ALVO" if ref and ref[front] and abs(b - int(ref[front] * S.Z_BINS)) < 2
        else ("   <- anel" if b == wb else "")))

# --- NORMAL PARA BAIXO: a assinatura do BALANCO ------------------------------
# O pannus nao faz vinco, faz sombra de si mesmo. Mas a face de baixo dele
# aponta para BAIXO (nz << 0), e a barriga da frente e o short apontam para
# FORA (nz ~ 0). O fim da faixa que aponta para baixo e a borda visivel do
# tecido. Isso e geometria pura e nao depende de haver vinco nenhum.
nrm = np.empty(n * 3)
me.vertices.foreach_get("normal", nrm)
nrm = nrm.reshape(n, 3)
import math as _m
azv = np.arctan2(co[:, 1], co[:, 0])
zbv = np.clip((co[:, 2] / H * S.Z_BINS).astype(np.int64), 0, S.Z_BINS - 1)
abv = np.clip(((azv + _m.pi) / (2 * _m.pi) * S.WAIST_AZ_BINS).astype(np.int64),
              0, S.WAIST_AZ_BINS - 1)
sel = ~is_arm
NZ = np.zeros((S.WAIST_AZ_BINS, S.Z_BINS))
CT = np.zeros((S.WAIST_AZ_BINS, S.Z_BINS))
np.add.at(NZ, (abv[sel], zbv[sel]), nrm[sel, 2])
np.add.at(CT, (abv[sel], zbv[sel]), 1.0)
NZ = np.where(CT > 0, NZ / np.maximum(CT, 1), np.nan)

print("\n  nz MEDIO por celula (negativo = superficie virada para baixo):")
print("      zh " + " ".join("{:6.3f}".format((b + .5) / S.Z_BINS)
                             for b in range(crotch_b, wb + 2, 3)))
for j in fronts:
    print("  s{:>2}    ".format(j) + " ".join(
        ("{:6.2f}".format(NZ[j, b]) if not np.isnan(NZ[j, b]) else "     .")
        for b in range(crotch_b, wb + 2, 3)))
print("\n  fim da faixa virada para baixo (nz < -0.35), por setor:")
for j in fronts:
    col = NZ[j, crotch_b:wb + 2]
    baixo = np.where(col < -0.35)[0]
    if baixo.size:
        print("  s{:>2}  faixa zh {:.4f} .. {:.4f}   alvo da folha {}".format(
            j, (crotch_b + baixo.min() + .5) / S.Z_BINS,
            (crotch_b + baixo.max() + .5) / S.Z_BINS,
            "{:.4f}".format(ref[j]) if ref and ref[j] else "-"))
    else:
        print("  s{:>2}  nenhuma".format(j))
