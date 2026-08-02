"""TODOS os picos de anel da perna e do tronco, SEM janela nenhuma.

Mesma doutrina do _corridas.py: despejar o sinal cru e escolher depois. Aqui
importa mais que o normal, porque a suspeita e justamente contra a JANELA - em
5 femininas o waist_peaks e o hem_peaks voltaram VAZIOS, e lista vazia tem duas
leituras opostas:

  (a) a malha nao tem vinco nenhum ali  -> nao adianta mexer na ancora;
  (b) o vinco existe e a janela nao o cobre -> a ancora e o conserto.

As duas produzem exatamente o mesmo diag, entao o mapa nao sabe distinguir. So
o perfil inteiro sabe. Se aparecer um pico forte logo ACIMA do teto da janela
(crotch + WAIST_ABOVE_CROTCH[1]) e ele bater com a corrida escura da folha, e o
caso (b) e a virilha esta baixa demais - o modo de falha ja documentado do
zen_m_b12_d1.

Imprime tambem a janela vigente e a que existiria com a virilha corrigida, para
nao ter de refazer a conta a mao.

    blender -b -P qa/probe/sondas/_anel_cru.py -- --root . --id zen_f_b10_d1
"""
import argparse
import json
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

master = os.path.join(ROOT, "02_master", a.id + "_master.glb")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=master)
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data

n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
zs = co[:, 2]
H = float(zs.max() - zs.min())

crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
k, _ = S.w_curvature(me, np)
kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
cz = crotch / H

folha = {}
p = os.path.join(ROOT, "qa", "probe", "faixa", "_folha.json")
if os.path.isfile(p):
    with open(p, "r", encoding="utf-8") as f:
        folha = (json.load(f).get(a.id) or {}).get("short") or {}

print("== %s   virilha %.4f   folha cos/bainha %s" % (
    a.id, cz, ("%.3f / %.3f" % tuple(folha)) if folha else "-"))


def linha(rot, tag):
    pk = S.w_peaks(np, rot, 1, S.Z_BINS - 1, floor=0.0)
    pk = [(s, b) for s, b in pk if s > 0.004][:8]
    print("  %-8s %s" % (tag, "  ".join(
        "%.3f@%.3f" % (s, (b + 0.5) / S.Z_BINS) for s, b in pk) or "(nenhum)"))


lids = [0, 1]
for lid in lids:
    sel = np.where(leg_id == lid)[0]
    if sel.size == 0:
        continue
    _A, ring, _o = S.w_ring_map(np, co, kn, sel, H, "slice")
    linha(ring, "perna%d" % lid)

torso = np.where((~is_arm) & (zs >= crotch))[0]
back = S.w_back_side_mask(np, S.WAIST_AZ_BINS)
_At, ring_t, _ot = S.w_ring_map(np, co, kn, torso, H, "axis", S.WAIST_AZ_BINS,
                                az_mask=back)
linha(ring_t, "tronco")

lo = max(cz + S.WAIST_ABOVE_CROTCH[0], S.WAIST_ABS_RANGE[0])
hi = min(cz + S.WAIST_ABOVE_CROTCH[1], S.WAIST_ABS_RANGE[1])
print("  janela cos    hoje %.3f-%.3f   bainha hoje %.3f-%.3f" % (
    lo, hi, cz - S.HEM_BELOW_CROTCH[1], cz - S.HEM_BELOW_CROTCH[0]))
if folha:
    # que virilha poria a corrida da folha DENTRO das duas janelas
    a_lo = folha[0] - S.WAIST_ABOVE_CROTCH[1]
    a_hi = folha[0] - S.WAIST_ABOVE_CROTCH[0]
    b_lo = folha[1] + S.HEM_BELOW_CROTCH[0]
    b_hi = folha[1] + S.HEM_BELOW_CROTCH[1]
    print("  virilha que cobriria a folha: cos %.3f-%.3f   bainha %.3f-%.3f"
          % (a_lo, a_hi, b_lo, b_hi))
