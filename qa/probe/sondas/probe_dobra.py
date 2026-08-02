#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_dobra.py - onde o AVENTAL dobra, e onde esta a BAINHA de verdade.

    blender --background --python qa/probe/sondas/probe_dobra.py -- --id zen_m_b12_d1

(a) Por setor de azimute, mapa de ocupacao (raio x altura). A barriga pendente
    aparece como duas folhas de superficie no mesmo raio: a face da frente
    descendo e a face de BAIXO voltando. A dobra e o ponto mais baixo da folha
    externa - e o unico lugar onde a divisa de cor pode ficar sem subir na pele.

(b) Perfil de anel da perna com a selecao ESTENDIDA ate a virilha corrigida.
    w_limbs so marca perna abaixo da altura em que as duas se separam (0.297
    aqui); com crotch_override_zh = 0.37 a janela da bainha cai inteira num
    trecho SEM VERTICE DE PERNA, w_peaks volta vazio e a bainha vira chute.
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
me = [o for o in bpy.context.scene.objects if o.type == "MESH"][0].data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
zh = co[:, 2] / H
r = np.hypot(co[:, 0], co[:, 1])
az = np.arctan2(co[:, 1], co[:, 0])

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
entry = S.load_map(root)[a.id]
cov = entry.get("crotch_override_zh")
print("virilha detectada = {:.4f}   override = {}".format(crotch / H, cov))
print("waist_zh atual    = {}".format([round(v, 4) for v in entry["waist_zh"]]))

NB = S.WAIST_AZ_BINS
ab = np.clip(((az + math.pi) / (2 * math.pi) * NB).astype(np.int64), 0, NB - 1)
front = NB // 4
back_side = S.w_back_side_mask(np, NB)

def _dobra(sel, rmax, minimo=3):
    """Menor altura em que a FOLHA EXTERNA ainda existe, exigindo continuidade.

    Sem o minimo de vertices e sem parar na primeira lacuna, meia duzia de
    vertices soltos la embaixo (ruido de decimacao entre as coxas) puxam a dobra
    0.03 para baixo - foi o que fez o setor 9 medir 0.305 em vez de 0.330."""
    ext = sel[r[sel] > 0.70 * rmax]
    if ext.size < minimo:
        return float("nan")
    zz = 0.44
    ultimo = float("nan")
    while zz > 0.24:
        g = ext[(zh[ext] >= zz) & (zh[ext] < zz + 0.005)]
        if g.size >= minimo:
            ultimo = zz
        elif not math.isnan(ultimo):
            break
        zz -= 0.005
    return ultimo


print("\n(a) OCUPACAO (raio x altura) por setor.  '#' = ha superficie")
print("    linhas = altura de 0.44 ate 0.28 (de cima para baixo)")
zlist = [0.44 - i * 0.005 for i in range(33)]
for j in list(range(NB)):
    if back_side[j]:
        continue
    sel = np.where((ab == j) & (~is_arm) & (zh > 0.24) & (zh < 0.60))[0]
    if sel.size < 20:
        continue
    rmax = float(np.percentile(r[sel], 99))
    rb = np.linspace(0.04, rmax * 1.02, 26)
    print("  --- setor {} ({} da frente)   r_max = {:.3f}   waist = {:.4f}".format(
        j, j - front, rmax, entry["waist_zh"][j]))
    dobra = None
    for zz in zlist:
        g = sel[(zh[sel] >= zz) & (zh[sel] < zz + 0.005)]
        if g.size == 0:
            print("    {:.3f} |{}|".format(zz, " " * 25))
            continue
        h, _ = np.histogram(r[g], bins=rb)
        line = "".join("#" if c else " " for c in h)
        # folha externa = raio acima de 70% do maximo do setor
        if dobra is None and (r[g] > 0.70 * rmax).any():
            pass
        print("    {:.3f} |{}|  n={}".format(zz, line, g.size))
    print("    dobra = {:.4f}".format(_dobra(sel, rmax)))

print("\n(b) BAINHA: perfil de anel com a perna estendida ate a virilha corrigida")
k, _ = S.w_curvature(me, np)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
teto = (cov or crotch / H)
for nome, lado in (("esquerda", co[:, 0] < 0), ("direita", co[:, 0] >= 0)):
    sel = np.where(lado & (~is_arm) & (zh < teto) & (zh > teto - 0.16))[0]
    A, ring, occ = S.w_ring_map(np, co, kn, sel, H, "slice")
    print("  perna {}  ({} verts)   ocupacao media = {:.0%}".format(
        nome, sel.size, occ.mean()))
    cb = int(teto * S.Z_BINS)
    for b in range(cb - int(0.11 * S.Z_BINS), cb):
        print("    {:.4f}  {:.4f} {}".format(
            (b + 0.5) / S.Z_BINS, ring[b], "#" * int(ring[b] * 150)))
print("RESULT ok")
