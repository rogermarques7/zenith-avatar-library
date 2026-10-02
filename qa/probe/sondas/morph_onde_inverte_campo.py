# -*- coding: utf-8 -*-
"""ONDE inverte um morph que MORREU - sem precisar do shape key no GLB.

    blender -b -P qa/probe/sondas/morph_onde_inverte_campo.py -- --id ID --key morph_chest [--inf 0.5] [--mod scripts/morph.py]

O `morph_onde_inverte.py` le o shape key do GLB, e morph com faixa zero nao
vai para o GLB (so os `usaveis` sao gravados). Aqui o campo e recalculado pela
mesma `Base` do `morph.py` (ou do modulo passado em --mod), a amplitude sai da
mesma busca de `cm_at_full`, e cada triangulo que a sonda conta como invertido
e listado com altura (z/H), azimute (0 = frente) e distancia ao eixo do braco.
"""
import importlib.util
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

AID, KEY = arg("--id"), arg("--key")
INF = float(arg("--inf", "0.5"))
_, src = _zp.dist_glb_current(ROOT, AID)
ob, co_real, co, mesh, sk = ml.carregar(src)
b = ml.Base(co, mesh, AID)
b.thigh_offset = ml.calibrar_offset_coxa(ROOT, AID, b, co)[0]
masks = b.campo(co)
m, d = masks[KEY]
spec_m = next(s for s in ml.MORPHS if s["key"] == KEY)
col = spec_m.get("cal_column", spec_m["column"])
sg = spec_m.get("cal_sign", 1)
b0 = ml.medir(b, co, col) * 100
a = 0.010
for _ in range(5):
    v = ml.medir(b, co + d * (m * a * sg)[:, None], col)
    if v is None:
        a *= 0.5
        continue
    delta = (v * 100 - b0) * sg
    if delta <= 0.05:
        a *= 2.0
        continue
    a = float(np.clip(a * (spec_m["cm_at_full"] / delta), 0.0005, 0.060))
P = co + d * (m * a * INF)[:, None]
nr, area = b.normais(P)
toca = (m[b.tris].max(axis=1) > 0.05) & (area > b.area_min) & (b.area0 > b.area_min)
inv = ((nr * b.nrm0).sum(axis=1) < 0) & toca
print("ONDE {} {} inf {:+.1f} amplitude {:.4f} -> {} invertidos".format(AID, KEY, INF, a, int(inv.sum())))
dd, _, _ = b._dist_eixo(co)
for i in np.where(inv)[0]:
    c = co[b.tris[i]].mean(axis=0)
    az = np.degrees(np.arctan2(c[0], -c[1] * b.frente)) % 360
    di = min(b._dist_eixo(c[None])[0][0], b._dist_eixo((c * np.array([-1, 1, 1]))[None])[0][0])
    print("  tri {:6d} z/H {:.3f} x {:+.3f} y {:+.3f} az {:5.0f} | area {:.2e} (mediana {:.2e}) | "
          "mascara {:.2f} | dist eixo braco {:.3f} m".format(
              i, (c[2] - b.zmin) / b.H, c[0], c[1], az, b.area0[i], np.median(b.area0),
              float(m[b.tris[i]].max()), di))
