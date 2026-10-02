# -*- coding: utf-8 -*-
"""Landmarks do braco AO LONGO DO EIXO, em cm a partir do cotovelo (sessao 41).

    blender -b -P qa/probe/sondas/biceps_eixo.py -- --ids a,b

Imprime cotovelo, leitura da regua (t_top), fusao, cabeca do umero e o raio do
braco - para escolher o topo da faixa do biceps em fracao do UMERO, nao em
raios de braco (3 R num braco de 7,5 cm sao 22 cm: caia no meio do braco).
"""
import importlib.util
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
spec = importlib.util.spec_from_file_location("mlab", os.path.join(ROOT, "scripts", "morph.py"))
ml = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(ml)
import zenith_paths as _zp  # noqa: E402

ids = argv[argv.index("--ids") + 1].split(",")
for aid in ids:
    _, src = _zp.dist_glb_current(ROOT, aid)
    ob, co_real, co, mesh, sk = ml.carregar(src)
    b = ml.Base(co, mesh, aid)
    vao = b.t_top - b.t_pulso
    t_cot = b.t_pulso + 0.72 * vao
    t_cab = float((b.C_ombro - b.arm_c) @ b.arm_e)
    L = t_cab - t_cot
    f = lambda t: (t - t_cot) / L  # noqa: E731
    print("EIXO {:16s} umero {:.1f} cm | R {:.1f} | top {:.2f} L | fusao {:.2f} L | "
          "faixa antiga {:.2f}..{:.2f} L".format(
              aid, 100 * L, 100 * b.r_braco, f(b.t_top), f(b.t_fusao),
              f(t_cot + 0.06 * vao), f(b.t_fusao + 0.05 * vao)))
