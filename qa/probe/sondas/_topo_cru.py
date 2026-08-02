"""A coluna de concavidade que o w_faixa_curve le, setor a setor, ANTES da mediana.

Existe porque a correcao da cunha do esterno depende de UM fato que eu nao posso
deduzir do mapa: onde esta a energia na coluna dos setores do meio da frente. Se
a coluna do esterno for uniformemente alta, o prior ja resolveria e o argmax
pousaria na ancora; se ela tiver maximo PROPRIO la em cima, nenhum prior resolve
e o conserto tem que excluir o setor. Deduzir isso do resultado pos-mediana e
palpite - dois palpites concordando nao valem uma medida.

Imprime, por setor: o argmax cru (o que o w_faixa_curve escolheria sem mediana),
o valor no argmax, o valor na ancora, e a coluna inteira em barras.

    blender -b -P qa/probe/sondas/_topo_cru.py -- --root . --id ID [ID...]
"""
import argparse
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--id", nargs="+", required=True)
a = ap.parse_args(argv)

ROOT = os.path.abspath(a.root)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import bpy  # noqa: E402
import shorts as S  # noqa: E402


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
    # MESMA normalizacao do w_fit. A crua serve para comparar setor com setor do
    # mesmo avatar, mas nao para comparar com constante nenhuma do arquivo.
    kraw, _co2 = S.w_curvature(me, np)
    kn = np.clip(kraw / max(float(np.percentile(kraw, 99.0)), 1e-9), 0.0, 1.0)

    z = co[:, 2]
    tronco = np.where((~is_arm) & (z >= crotch))[0]
    back = S.w_back_side_mask(np, S.WAIST_AZ_BINS)
    A, ring, occ = S.w_ring_map(np, co, kn, tronco, H, "axis", S.WAIST_AZ_BINS)
    _A2, ring_bs, _o = S.w_ring_map(np, co, kn, tronco, H, "axis",
                                    S.WAIST_AZ_BINS, az_mask=back)
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

    frente = S.WAIST_AZ_BINS // 4
    print("\n=== %s  base %.4f  ancora_topo %.4f  frente=setor %d"
          % (aid, (base_b + 0.5) / S.Z_BINS, (topo_b + 0.5) / S.Z_BINS, frente))
    print("  %-4s %-6s %8s %8s %8s   %s"
          % ("set", "lado", "cru_zh", "A_cru", "A_ancora", "coluna (baixo->alto)"))
    for j in range(S.WAIST_AZ_BINS):
        dianteiro = not back[j]
        if dianteiro:
            lo_f, hi_f = topo_b, topo_b + S.FAIXA_TOPO_UP_FRONT * S.Z_BINS
        else:
            lo_f = topo_b - S.FAIXA_TOPO_BACK_ZH * S.Z_BINS
            hi_f = topo_b + S.FAIXA_TOPO_BACK_ZH * S.Z_BINS
        lo = int(max(0, base_b + 1, round(lo_f)))
        hi = int(min(S.Z_BINS - 1, round(hi_f)))
        if hi < lo:
            continue
        col = A_f[j, lo:hi + 1]
        zz = np.arange(lo, hi + 1, dtype=np.float64)
        sig = max((hi - topo_b) * S.WAIST_PRIOR_SIGMA, 1.0)
        w = col * np.exp(-0.5 * ((zz - topo_b) / sig) ** 2)
        k = int(w.argmax()) if w.size and w.max() > 0 else 0
        mx = col.max() if col.size else 1.0
        barras = "".join(" .:-=+*#@"[min(8, int(9 * v / mx))] if mx > 0 else " "
                         for v in col)
        print("  %-4d %-6s %8.4f %8.4f %8.4f   |%s|"
              % (j, "FRENTE" if dianteiro else "costas",
                 (lo + k + 0.5) / S.Z_BINS, col[k], col[0], barras))


for aid in a.id:
    um(aid)
