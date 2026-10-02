# -*- coding: utf-8 -*-
"""O triangulo que a sonda chama de INVERTIDO ja estava torto na malha BASE?

    blender -b -P qa/probe/sondas/morph_tri_base.py -- --id ID --key morph_waist --inf -0.5

A sonda de normais invertidas compara a normal de cada triangulo deformado com
a normal DELE MESMO na base (`nrm0`). Se o triangulo ja nasce dobrado - normal
contra a dos vizinhos, lasca numa prega da Meshy -, qualquer empurrao pequeno o
vira, e a contagem acusa o morph por um defeito da malha. Sinal disso: a
contagem fica CONSTANTE com a amplitude (1 em -0,5, 1 em -1,0, 1 em -1,5).

Para cada invertido imprime, NA BASE: o angulo da normal dele contra a media
das normais dos triangulos vizinhos (por vertice), a razao de aspecto e a area
relativa a mediana. E o mesmo no estado deformado.
"""
import importlib.util
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]


def arg(n, p=None):
    return argv[argv.index(n) + 1] if n in argv else p


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
spec = importlib.util.spec_from_file_location("mlab", os.path.join(ROOT, "scripts", "morph.py"))
ml = importlib.util.module_from_spec(spec)
sys.argv = ["x"]
spec.loader.exec_module(ml)
import zenith_paths as _zp  # noqa: E402

AID, KEY, INF = arg("--id"), arg("--key", "morph_waist"), float(arg("--inf", "-0.5"))
_, src = _zp.dist_glb_current(ROOT, AID)
ob, co_real, co, mesh, sk = ml.carregar(src)
b = ml.Base(co, mesh, AID)
b.thigh_offset = ml.calibrar_offset_coxa(ROOT, AID, b, co)[0]
m, d = b.campo(co)[KEY]
spec_m = next(s for s in ml.MORPHS if s["key"] == KEY)
cal = spec_m.get("cal_column", spec_m["column"])
sg = spec_m.get("cal_sign", 1)
b0 = ml.medir(b, co, cal) * 100
a = 0.010
for _ in range(5):
    v = ml.medir(b, co + d * (m * a * sg)[:, None], cal)
    if v is None:
        a *= 0.5
        continue
    dl = (v * 100 - b0) * sg
    if dl <= 0.05:
        a *= 2.0
        continue
    a = float(np.clip(a * (spec_m["cm_at_full"] / dl), 0.0005, 0.060))
T = b.tris
por_v = [[] for _ in range(len(co))]
for t, (i, j, k) in enumerate(T):
    por_v[i].append(t); por_v[j].append(t); por_v[k].append(t)


def contra_vizinhos(nr, t):
    viz = {u for v in T[t] for u in por_v[v]} - {t}
    mv = nr[list(viz)].mean(axis=0)
    mv /= max(np.linalg.norm(mv), 1e-12)
    return float(np.degrees(np.arccos(np.clip(nr[t] @ mv, -1, 1))))


def aspecto(P, t):
    p = P[T[t]]
    l = sorted(np.linalg.norm(p[[1, 2, 0]] - p, axis=1))
    return l[2] / max(l[0], 1e-9)


P = co + d * (m * a * INF)[:, None]
nr, area = b.normais(P)
toca = (m[T].max(axis=1) > 0.05) & (area > b.area_min) & (b.area0 > b.area_min)
inv = np.where(((nr * b.nrm0).sum(axis=1) < 0) & toca)[0]
med = float(np.median(b.area0))
print("TRI {} {} inf {:+.1f}: {} invertidos".format(AID, KEY, INF, len(inv)))
for t in inv:
    c = co[T[t]].mean(axis=0)
    print("   tri {:6d} z/H {:.3f} | BASE: {:5.0f} graus contra vizinhos, aspecto {:5.1f}, area {:.2f}x mediana"
          " | DEFORMADO: {:5.0f} graus".format(
              t, (c[2] - b.zmin) / b.H, contra_vizinhos(b.nrm0, t), aspecto(co, t),
              b.area0[t] / med, contra_vizinhos(nr, t)))
