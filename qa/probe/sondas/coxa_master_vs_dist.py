# -*- coding: utf-8 -*-
"""Por que a COXA le diferente no master e no dist entregue.

    blender -b -P qa/probe/sondas/coxa_master_vs_dist.py -- zen_f_b08h_d3 zen_m_b02_d1

Imprime, para os dois arquivos do mesmo avatar, cada engrenagem da regua da
coxa: a virilha detectada, o topo da banda, o z escolhido pelo maximo e os dois
lacos medidos ali. A diferenca entre as duas colunas e a explicacao.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import numpy as np                      # noqa: E402
import metrics as mt                    # noqa: E402
import zenith_paths as zp               # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
root = mt.repo_root()

for aid in argv:
    print("\n" + "=" * 74)
    print(aid)
    for rotulo, path in (("master", os.path.join(root, "02_master", aid + "_master.glb")),
                         ("dist  ", zp.dist_glb_current(root, aid)[1])):
        if not path or not os.path.isfile(path):
            print("  {}: nao existe".format(rotulo))
            continue
        mesh = mt.load_mesh(path)
        base = float(mesh.verts[:, 2].min())
        H = float(mesh.verts[:, 2].max() - base)
        crotch = base + mt.CROTCH_FRAC * H
        leg_split = mt.find_crotch(mesh, base, H)
        top = crotch if leg_split is None else min(crotch, leg_split)
        banda = (top - mt.THIGH_BAND_M, top - mt.SCAN_STEP_M)
        got = mt.pair_extreme(mesh, banda[0], banda[1], False, "max")
        z = got[3]
        r = mt.relevant(mesh, z, axis_correct=False)
        print("  {} | virilha anatomica {:.3f} | leg_split {} | topo {:.3f}"
              .format(rotulo, crotch,
                      "{:.3f}".format(leg_split) if leg_split else "None", top))
        print("           banda {:.3f}..{:.3f} | z escolhido {:.3f} ({:.3f} H)"
              " | coxa {:.1f} cm  (esq {:.1f} / dir {:.1f})"
              .format(banda[0], banda[1], z, (z - base) / H,
                      got[0] * 100, got[1] * 100, got[2] * 100))
        print("           lacos em z: {}".format(
            ["{:.1f} cm".format(x[0] * 100) for x in r[:4]]))
