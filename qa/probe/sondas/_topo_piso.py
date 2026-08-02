"""Raio de alcance do PISO na borda de cima da faixa, nos 37.

A medida do _topo_cru.py mostrou o defeito do b08_d3 com separacao total: nos
setores que sobem (3,4,7,8 - os dois peitorais) a concavidade NA ANCORA e
0.0000, e nos que ficam parados ela vale 0.18 a 0.39. O volume do peitoral apaga
o aro, e o w_faixa_curve nao tem piso nenhum sobre a forca do pico: o argmax
pousa num ruido de 0.02 la em cima.

A regra candidata: a borda so pode subir num setor onde ela EXISTE. Sem
concavidade na ancora nao ha aro para seguir, e o setor herda a ancora - que e o
que o codigo ja faz quando a coluna esta vazia.

Nao existe regua externa para o TRACADO (a folha da a altura media da peca, nao
a curva por setor). Entao o criterio e diferencial, como foi no braco: mede-se
QUEM MUDA. Regra que mexe em corpo que ja esta certo esta errada, por melhor que
pareca no papel.

    blender -b -P qa/probe/sondas/_topo_piso.py -- --root . [--piso 0.02]
"""
import argparse
import glob
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--piso", type=float, nargs="+", default=[0.005, 0.02, 0.05])
ap.add_argument("--id", nargs="*")
a = ap.parse_args(argv)

ROOT = os.path.abspath(a.root)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import bpy  # noqa: E402
import shorts as S  # noqa: E402

AZ = S.WAIST_AZ_BINS


def mediana_circ(out):
    k = S.WAIST_MEDIAN // 2
    return [int(sorted([out[(j + d) % AZ] for d in range(-k, k + 1)])[k])
            for j in range(AZ)]


def um(aid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master",
                                                    aid + "_master.glb"))
    me = [o for o in bpy.context.scene.objects if o.type == "MESH"][0].data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    H = float(co[:, 2].max() - co[:, 2].min())
    crotch, _leg, is_arm = S.w_limbs(me, np, co, H)
    kraw, _c = S.w_curvature(me, np)
    kn = np.clip(kraw / max(float(np.percentile(kraw, 99.0)), 1e-9), 0.0, 1.0)

    tronco = np.where((~is_arm) & (co[:, 2] >= crotch))[0]
    back = S.w_back_side_mask(np, AZ)
    A, ring, occ = S.w_ring_map(np, co, kn, tronco, H, "axis", AZ)
    _A2, ring_bs, _o = S.w_ring_map(np, co, kn, tronco, H, "axis", AZ,
                                    az_mask=back)
    base_b, _s, _p = S.w_pico_prior(np, ring, S.FAIXA_BASE_RANGE[0],
                                    S.FAIXA_BASE_RANGE[1], S.FAIXA_BASE_MEDIANA,
                                    S.FAIXA_BASE_SIGMA, S.FAIXA_PICO_MIN)
    if base_b is None:
        base_b = int(S.FAIXA_BASE_MEDIANA * S.Z_BINS)
    alvo = (base_b + 0.5) / S.Z_BINS + S.FAIXA_ALTURA_ZH
    topo_b, _s2, _p2 = S.w_pico_prior(np, ring_bs, alvo - S.FAIXA_ALTURA_TOL,
                                      alvo + S.FAIXA_ALTURA_TOL, alvo,
                                      S.FAIXA_ALTURA_TOL, S.FAIXA_PICO_MIN)
    if topo_b is None:
        topo_b = int(round(alvo * S.Z_BINS - 0.5))
    A_f = S.w_fill_holes(np, A, occ)

    cur, ancora, forca = [], [], []
    for j in range(AZ):
        if not back[j]:
            lo_f, hi_f = topo_b, topo_b + S.FAIXA_TOPO_UP_FRONT * S.Z_BINS
        else:
            lo_f = topo_b - S.FAIXA_TOPO_BACK_ZH * S.Z_BINS
            hi_f = topo_b + S.FAIXA_TOPO_BACK_ZH * S.Z_BINS
        lo = int(max(0, base_b + 1, round(lo_f)))
        hi = int(min(S.Z_BINS - 1, round(hi_f)))
        if hi < lo:
            cur.append(topo_b), ancora.append(0.0), forca.append(0.0)
            continue
        col = A_f[j, lo:hi + 1]
        zz = np.arange(lo, hi + 1, dtype=np.float64)
        sig = max((hi - topo_b) * S.WAIST_PRIOR_SIGMA, 1.0)
        w = col * np.exp(-0.5 * ((zz - topo_b) / sig) ** 2)
        cur.append(lo + int(w.argmax()) if w.size and w.max() > 0 else topo_b)
        ancora.append(float(A_f[j, min(max(topo_b, 0), S.Z_BINS - 1)]))
        forca.append(float(col.max()) if col.size else 0.0)

    base = mediana_circ(cur)
    linha = ["%-16s" % aid.replace("zen_f_", "")]
    for p in a.piso:
        novo = mediana_circ([topo_b if ancora[j] < p else cur[j]
                             for j in range(AZ)])
        d = max(abs(novo[j] - base[j]) for j in range(AZ)) / float(S.Z_BINS)
        nset = sum(1 for j in range(AZ) if novo[j] != base[j])
        salto = max(abs(novo[j] - novo[(j + 1) % AZ])
                    for j in range(AZ)) / float(S.Z_BINS)
        linha.append("  %2d set %.4f d  %.4f salto" % (nset, d, salto))
    s0 = max(abs(base[j] - base[(j + 1) % AZ]) for j in range(AZ)) / float(S.Z_BINS)
    zeros = sum(1 for j in range(AZ) if not back[j] and ancora[j] < 0.005)
    print("%s   | hoje %.4f salto, %d/9 setores da frente sem aro"
          % ("".join(linha), s0, zeros))
    sys.stdout.flush()


ids = a.id or sorted(os.path.basename(p).replace("_master.glb", "") for p in
                     glob.glob(os.path.join(ROOT, "02_master", "zen_f_*_master.glb")))
print("piso testado: " + "  ".join("%.3f" % p for p in a.piso))
for aid in ids:
    um(aid)
