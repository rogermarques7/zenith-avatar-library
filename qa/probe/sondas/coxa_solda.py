# -*- coding: utf-8 -*-
"""Onde exatamente a costura soldada desloca a deteccao da virilha/coxa.

    blender -b -P qa/probe/sondas/coxa_solda.py -- zen_f_b03_d1

Roda find_crotch nas DUAS versoes do mesmo dist: crua (mt.load_mesh, como o
metrics.py usa) e soldada (morph.carregar, como o morph.py usa). A diferenca
entre as duas isola se o problema e a solda em si.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import metrics as mt                    # noqa: E402
import zenith_paths as zp               # noqa: E402
import morph as mp                      # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
root = mt.repo_root()

for aid in argv:
    print("\n" + "=" * 74)
    print(aid)
    path = zp.dist_glb_current(root, aid)[1]

    # crua (metrics.py)
    mesh_crua = mt.load_mesh(path)
    base_c = float(mesh_crua.verts[:, 2].min())
    H_c = float(mesh_crua.verts[:, 2].max() - base_c)
    crotch_c = base_c + mt.CROTCH_FRAC * H_c
    split_c = mt.find_crotch(mesh_crua, base_c, H_c)
    print("  crua    | verts {} | virilha anat {:.4f} | leg_split {}"
          .format(mesh_crua.verts.shape[0], crotch_c,
                  "{:.4f}".format(split_c) if split_c else "None"))

    # soldada (morph.py)
    import bpy
    ob, co_real, co_sold, mesh_sold, sk = mp.carregar(path)
    base_s = float(co_sold[:, 2].min())
    H_s = float(co_sold[:, 2].max() - base_s)
    crotch_s = base_s + mt.CROTCH_FRAC * H_s
    split_s = mt.find_crotch(mesh_sold, base_s, H_s)
    print("  soldada | verts {} | virilha anat {:.4f} | leg_split {}"
          .format(co_sold.shape[0], crotch_s,
                  "{:.4f}".format(split_s) if split_s else "None"))
    print("  delta verts (crua-soldada): {}".format(mesh_crua.verts.shape[0] - co_sold.shape[0]))

    # o que o find_crotch ve exatamente na faixa onde as duas leituras divergem,
    # se divergirem
    if split_c and split_s and abs(split_c - split_s) > 1e-4:
        import numpy as np
        print("  divergencia! varrendo 0.780..0.860 nas duas:")
        for z in np.arange(0.780, 0.860, 0.005):
            zc = base_c + z * H_c
            zs = base_s + z * H_s
            rc = mt.relevant(mesh_crua, zc)
            rs = mt.relevant(mesh_sold, zs)
            print("    frac {:.3f} | crua: {} lacos {} | soldada: {} lacos {}"
                  .format(z, len(rc), ["{:.1f}cm".format(x[0]*100) for x in rc[:3]],
                          len(rs), ["{:.1f}cm".format(x[0]*100) for x in rs[:3]]))
