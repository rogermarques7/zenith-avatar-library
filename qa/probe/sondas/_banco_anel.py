"""BANCO DE ENSAIO: o perfil de anel cru de cada avatar, gravado uma vez.

Escolher janela do cos e ancora de virilha exige comparar varias hipoteses
contra as 37 folhas. Cada hipotese testada pelo --fit custa um Blender por
avatar; testadas aqui custam um laco de numpy. Entao o Blender roda UMA vez por
avatar e grava o sinal cru - o perfil de ring_score do tronco e de cada perna,
mais a virilha detectada e a altura -, e toda a varredura de janela acontece
depois, em _varre_janela.py, sem Blender nenhum.

O que se grava e o SINAL, nao a conclusao: nenhuma janela e aplicada aqui. Se
uma hipotese futura precisar de outro limiar ou de outra faixa, ela se responde
sobre este mesmo arquivo.

RESSALVA que ja custou caro nesta sessao: cache de sonda ENVELHECE. O npz de
qa/probe/faixa/ foi gerado antes das correcoes de mascara de braco e passou a
prever base errada por avatar. Este arquivo grava o hash do master junto, e o
_varre_janela.py recusa rodar se o master mudou depois.

    blender -b -P qa/probe/sondas/_banco_anel.py -- --root . --sexo f
"""
import argparse
import hashlib
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--id", default=None)
ap.add_argument("--sexo", default="f")
a = ap.parse_args(argv)

ROOT = os.path.abspath(a.root)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import bpy  # noqa: E402
import shorts as S  # noqa: E402

OUT = os.path.join(ROOT, "qa", "probe", "anel")
if not os.path.isdir(OUT):
    os.makedirs(OUT)

if a.id:
    ids = [a.id]
else:
    pref = "zen_%s_" % a.sexo
    ids = sorted(n[:-len("_master.glb")]
                 for n in os.listdir(os.path.join(ROOT, "02_master"))
                 if n.startswith(pref) and n.endswith("_master.glb"))

for aid in ids:
    master = os.path.join(ROOT, "02_master", aid + "_master.glb")
    with open(master, "rb") as f:
        h = hashlib.sha1(f.read()).hexdigest()[:16]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=master)
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = obj.data

    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    z = co[:, 2]
    H = float(z.max() - z.min())

    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
    k, _ = S.w_curvature(me, np)
    kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)

    pernas = []
    for lid in (0, 1):
        sel = np.where(leg_id == lid)[0]
        if sel.size == 0:
            pernas.append(np.zeros(S.Z_BINS))
            continue
        _A, ring, _o = S.w_ring_map(np, co, kn, sel, H, "slice")
        pernas.append(np.asarray(ring, dtype=np.float64))

    torso = np.where((~is_arm) & (z >= crotch))[0]
    back = S.w_back_side_mask(np, S.WAIST_AZ_BINS)
    _At, ring_t, _ot = S.w_ring_map(np, co, kn, torso, H, "axis", S.WAIST_AZ_BINS,
                                    az_mask=back)

    # O tronco acima RECORTA em z>=crotch, entao com a virilha baixa demais ele
    # ainda cobre tudo que interessa; mas com uma virilha ALTA (hipotese que a
    # varredura vai testar) o recorte mudaria o sinal. Por isso vai tambem um
    # tronco sem recorte de virilha, e a varredura usa este quando desloca a
    # ancora - do contrario ela estaria varrendo um sinal que so existe porque a
    # ancora velha estava errada.
    torso_livre = np.where(~is_arm)[0]
    _A2, ring_tl, _o2 = S.w_ring_map(np, co, kn, torso_livre, H, "axis",
                                     S.WAIST_AZ_BINS, az_mask=back)

    np.savez(os.path.join(OUT, aid + ".npz"), sha=h, H=H, crotch_zh=crotch / H,
             perna0=pernas[0], perna1=pernas[1],
             tronco=np.asarray(ring_t, dtype=np.float64),
             tronco_livre=np.asarray(ring_tl, dtype=np.float64))
    print("gravado %s  virilha %.4f" % (aid, crotch / H))
