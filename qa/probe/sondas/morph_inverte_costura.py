# -*- coding: utf-8 -*-
"""O triangulo que inverte num morph esta na COSTURA corpo/peca? (sessao 41)

    blender -b -P qa/probe/sondas/morph_inverte_costura.py -- --id ID [--key morph_waist] [--inf -0.5]

Mesmo calculo do `morph_onde_inverte_campo.py` (campo + amplitude da busca do
morph.py), e para cada triangulo invertido: a distancia do centroide ate a
costura (vertices da malha REAL que existem nas duas primitivas, corpo e peca)
e o maior diedro entre ele e os vizinhos na base - a borda viva da roupa tem
diedro > 30 graus (LICOES 4.5p), prega de pele e vale liso.
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
import bpy  # noqa: E402
import zenith_paths as _zp  # noqa: E402

AID, KEY, INF = arg("--id"), arg("--key", "morph_waist"), float(arg("--inf", "-0.5"))
_, src = _zp.dist_glb_current(ROOT, AID)
ob, co_real, co, mesh, sk = ml.carregar(src)

# Vertices da malha REAL por material (0 = corpo, 1 = peca). A costura nao se
# acha por posicao identica (a duplicata do glTF nao bate no arredondamento);
# basta a distancia ate o vertice mais proximo de CADA material.
me = ob.data
nmat = max((p.material_index for p in me.polygons), default=0) + 1
por_mat = [set() for _ in range(nmat)]
for p in me.polygons:
    por_mat[p.material_index].update(p.vertices)
pts_mat = [co_real[sorted(v)] if v else np.zeros((0, 3)) for v in por_mat]
b = ml.Base(co, mesh, AID)
b.thigh_offset = ml.calibrar_offset_coxa(ROOT, AID, b, co)[0]
m, d = b.campo(co)[KEY]
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
inv = np.where(((nr * b.nrm0).sum(axis=1) < 0) & toca)[0]

# vizinhanca por aresta, para o diedro na base
from collections import defaultdict  # noqa: E402
viz = defaultdict(list)
for ti, t in enumerate(b.tris):
    for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
        viz[tuple(sorted(e))].append(ti)
print("COSTURA {} {} inf {:+.1f}: {} invertidos | materiais {}".format(
    AID, KEY, INF, len(inv), [len(x) for x in pts_mat]))
for i in inv:
    c = co[b.tris[i]].mean(axis=0)
    dm = [float(np.linalg.norm(x - c, axis=1).min()) if len(x) else float("nan") for x in pts_mat]
    t = b.tris[i]
    die = 0.0
    for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
        for tj in viz[tuple(sorted(e))]:
            if tj != i:
                cosv = float(np.clip((b.nrm0[i] * b.nrm0[tj]).sum(), -1, 1))
                die = max(die, float(np.degrees(np.arccos(cosv))))
    print("  tri {:6d} z/H {:.3f} | dist ao corpo {:.1f} cm, a peca {:.1f} cm | maior diedro com vizinho {:.0f} graus".format(
        i, (c[2] - b.zmin) / b.H, 100 * dm[0], 100 * dm[1] if len(dm) > 1 else float("nan"), die))
