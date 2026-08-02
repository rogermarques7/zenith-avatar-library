"""Sonda: onde esta a PREGA DA BARRIGA, e ela tem sinal?

Existe por causa da doutrina do state.md - "antes de fazer a borda perseguir um
vinco, medir se o vinco tem sinal". Na sessao 4 uma hipotese sobre a bainha
serpenteando custou uma implementacao inteira que PIOROU o resultado, porque
ninguem tinha medido o vinco antes de sair atras dele.

Aqui a pergunta e outra: nos corpos pesados a barriga cai POR CIMA do cos, e a
pintura estava atravessando a barriga numa reta horizontal. O cos da frente
deveria descer ate a prega. Antes de mexer no detector, esta sonda imprime,
para cada setor de azimute da FRENTE, o perfil de concavidade em z - para ver
se a prega existe, onde ela esta em relacao ao anel, e quao forte ela e
comparada ao que hoje ganha.

Nao escreve nada. So mede.

    blender --background --python scripts/probe_belly.py -- --id zen_m_b12_d1
"""
import os
import sys
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

master = os.path.join(ROOT, "02_master", a.id + "_master.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=master)
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data

zs = [v.co.z for v in me.vertices]
H = max(zs) - min(zs)
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
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
back_side = S.w_back_side_mask(np, S.WAIST_AZ_BINS)
A, ring = S.w_ring_map(np, co, kn, torso, H, "axis", S.WAIST_AZ_BINS,
                       az_mask=back_side)
pk = S.w_peaks(np, ring,
               crotch_b + S.WAIST_ABOVE_CROTCH[0] * S.Z_BINS,
               crotch_b + S.WAIST_ABOVE_CROTCH[1] * S.Z_BINS)
waist_b = pk[0][1] if pk else int(crotch_b + 0.12 * S.Z_BINS)

print("PROBE {}".format(a.id))
print("  virilha zh {:.4f}{}   anel zh {:.4f} {}".format(
    crotch / H, " (override)" if ov else "", (waist_b + 0.5) / S.Z_BINS,
    "" if pk else "[SEM PICO - chute]"))

front = S.WAIST_AZ_BINS // 4
half = max(1, S.WAIST_AZ_BINS // 6)
fronts = [(front + d) % S.WAIST_AZ_BINS for d in range(-half, half + 1)]

# Perfil de concavidade MEDIO sobre os setores da frente, de crotch ate o anel
# + um pouco. E aqui que a prega tem de aparecer, se aparecer.
lo = crotch_b
hi = min(S.Z_BINS - 1, waist_b + 20)
prof = A[fronts, lo:hi + 1].mean(axis=0)
mx = float(prof.max()) or 1.0

print("  perfil de concavidade da FRENTE (media dos setores {}):".format(fronts))
print("  {:>7} {:>8} {:>7}  {}".format("zh", "d_anel", "sinal", "barra"))
for i, b in enumerate(range(lo, hi + 1)):
    zh = (b + 0.5) / S.Z_BINS
    d = zh - (waist_b + 0.5) / S.Z_BINS
    v = prof[i] / mx
    mark = ""
    if b == waist_b:
        mark = "  <- ANEL"
    elif i > 0 and i < len(prof) - 1 and prof[i] >= prof[i - 1] and prof[i] >= prof[i + 1] and v > 0.5:
        mark = "  <- pico"
    print("  {:7.4f} {:+8.4f} {:7.3f}  {}{}".format(
        zh, d, v, "#" * int(v * 50), mark))

# --- por SETOR, nao a media: e assim que a DP enxerga -----------------------
print("\n  concavidade POR SETOR da frente (linha = setor, coluna = zh):")
zs_show = list(range(crotch_b, min(S.Z_BINS - 1, waist_b + 4), 4))
print("      zh " + " ".join("{:5.3f}".format((b + 0.5) / S.Z_BINS) for b in zs_show))
for j in fronts:
    print("  s{:>2}  ".format(j) + " ".join("{:5.2f}".format(A[j, b]) for b in zs_show))
print("\n  melhor celula de cada setor da frente:")
for j in fronts:
    seg = A[j, crotch_b:waist_b + 1]
    if seg.size:
        b = crotch_b + int(seg.argmax())
        print("  s{:>2}  argmax zh {:.4f}  valor {:.3f}   (no anel: {:.3f})".format(
            j, (b + 0.5) / S.Z_BINS, A[j, b], A[j, waist_b]))

# --- DEGRAU DE RAIO: o pannus e um BALANCO, nao um vinco --------------------
# Fatia horizontal abaixo da barriga pendente corta so coxa/short (raio pequeno);
# logo acima corta o pannus (raio grande). O salto de raio marca a borda visivel
# do tecido, e nao depende de haver vinco nenhum na superficie.
print("\n  RAIO por setor da frente (r em fracao da altura):")
import math as _m
az_all = np.arctan2(co[:, 1], co[:, 0])
r_all = np.hypot(co[:, 0], co[:, 1])
zb_all = np.clip((co[:, 2] / H * S.Z_BINS).astype(np.int64), 0, S.Z_BINS - 1)
ab_all = np.clip(((az_all + _m.pi) / (2 * _m.pi) * S.WAIST_AZ_BINS).astype(np.int64),
                 0, S.WAIST_AZ_BINS - 1)
R = np.zeros((S.WAIST_AZ_BINS, S.Z_BINS))
np.maximum.at(R, (ab_all[~is_arm], zb_all[~is_arm]), r_all[~is_arm] / H)
print("      zh " + " ".join("{:5.3f}".format((b + 0.5) / S.Z_BINS) for b in zs_show))
for j in fronts:
    print("  s{:>2}  ".format(j) + " ".join("{:5.3f}".format(R[j, b]) for b in zs_show))
print("\n  maior salto de raio subindo, por setor (janela virilha..anel):")
for j in fronts:
    seg = R[j, crotch_b:waist_b + 2]
    d = np.diff(seg)
    if d.size:
        k = int(d.argmax())
        print("  s{:>2}  salto em zh {:.4f}   dr {:+.4f}   r {:.3f} -> {:.3f}".format(
            j, (crotch_b + k + 1 + 0.5) / S.Z_BINS, d[k], seg[k], seg[k + 1]))
