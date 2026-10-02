# -*- coding: utf-8 -*-
"""RAIO DO BRACO por fatia, do pulso a fusao (sessao 41).

    blender -b -P qa/probe/sondas/braco_raio_fatias.py -- --ids a,b [--mod scripts/morph.py]

O corte braco/tronco do morph e fixo em 8 cm do eixo, e num braco grosso a
superficie passa disso. Medir o raio "do braco livre" por percentil global deu
20-28 cm nos obesos: alguma fatia pega outra coisa. Aqui, por fatia: o vao
braco/tronco, quantos vertices, mediana e p98 da distancia ao eixo, e a
circunferencia publicada do biceps (library_metrics.json) como regua externa.
"""
import importlib.util
import json
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]


def arg(n, p=None):
    return argv[argv.index(n) + 1] if n in argv else p


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
MOD = os.path.join(ROOT, arg("--mod", "scripts/morph.py"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
spec = importlib.util.spec_from_file_location("mlab", MOD)
ml = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(ml)
import zenith_paths as _zp  # noqa: E402

lm = json.load(open(os.path.join(ROOT, "metrics", "library_metrics.json"), encoding="utf-8"))
lm = lm.get("avatars", lm)


def publicado(aid, col):
    x = lm.get(aid) if isinstance(lm, dict) else next((a for a in lm if a.get("id") == aid), None)
    if not x:
        return None
    x = x.get("circumferences_cm", x)
    v = x.get(col)
    return v.get("cm") if isinstance(v, dict) else v


for aid in arg("--ids").split(","):
    _, src = _zp.dist_glb_current(ROOT, aid)
    ob, co_real, co, mesh, sk = ml.carregar(src)
    b = ml.Base(co, mesh, aid)
    z, H = b.zmin, b.H
    bic = publicado(aid, "biceps")
    print("RAIO {} | biceps publicado {} cm -> r circ {:.1f} cm | pulso z/H {:.3f} fusao z/H {:.3f}".format(
        aid, bic, (bic or 0) / (2 * np.pi), (b.z_pulso - z) / H, b.fusao_f))
    for zz in np.arange(b.z_pulso, z + b.fusao_f * H - 0.004, 0.012):
        g = b._gap_braco(co, zz)
        if not g:
            print("  z/H {:.3f}  sem vao".format((zz - z) / H))
            continue
        s = co[np.abs(co[:, 2] - zz) < 0.003]
        a = s[s[:, 0] > g[1] - 0.003]
        if len(a) < 6:
            continue
        dd = b._dist_eixo(a)[0]
        print("  z/H {:.3f}  vao x {:+.3f}..{:+.3f} | n {:4d} | x {:+.3f}..{:+.3f} | "
              "dist med {:.1f} p98 {:.1f} max {:.1f} cm".format(
                  (zz - z) / H, g[0], g[1], len(a), a[:, 0].min(), a[:, 0].max(),
                  100 * np.median(dd), 100 * np.percentile(dd, 98), 100 * dd.max()))
