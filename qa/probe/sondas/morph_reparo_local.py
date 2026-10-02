# -*- coding: utf-8 -*-
"""BANCO DE ENSAIO: reparo LOCAL do deslocamento onde o morph inverte triangulo.

    blender -b -P qa/probe/sondas/morph_reparo_local.py -- --id ID --key morph_waist [--aneis 2] [--iter 3]

Hoje 1 a 3 triangulos em influence -0,5 derrubam o lado negativo INTEIRO de um
morph (8 cinturas, 11 quadris, 8 peitos). Tolerar contagem foi refutado
(LICOES 7.23 - o mesmo numero e invisivel num corpo e visivel no outro). A
pergunta aqui e outra: da para TIRAR a dobra, e nao esconde-la?

Triangulo inverte quando dois vizinhos recebem deslocamentos muito diferentes
em relacao ao tamanho do triangulo. O reparo mede, no pior estado varrido, quais
triangulos invertem; pega os vertices deles + N aneis de vizinhanca; e troca o
deslocamento desses vertices pela media dos vizinhos, algumas iteracoes (o
resto da malha nao muda um bit). Depois re-varre a faixa inteira e mede quanto
a coluna andou - o reparo nao pode custar o centimetro.

Nada e gravado. Imprime, por influence: invertidos antes/depois e cm antes/depois.
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

AID, KEY = arg("--id"), arg("--key", "morph_waist")
ANEIS, ITER = int(arg("--aneis", "2")), int(arg("--iter", "3"))
_, src = _zp.dist_glb_current(ROOT, AID)
ob, co_real, co, mesh, sk = ml.carregar(src)
b = ml.Base(co, mesh, AID)
b.thigh_offset = ml.calibrar_offset_coxa(ROOT, AID, b, co)[0]
m, d = b.campo(co)[KEY]
spec_m = next(s for s in ml.MORPHS if s["key"] == KEY)
col = spec_m["column"]
cal = spec_m.get("cal_column", col)
b0c = ml.medir(b, co, cal) * 100
a = 0.010
for _ in range(5):
    v = ml.medir(b, co + d * (m * a)[:, None], cal)
    if v is None:
        a *= 0.5
        continue
    dl = v * 100 - b0c
    if dl <= 0.05:
        a *= 2.0
        continue
    a = float(np.clip(a * (spec_m["cm_at_full"] / dl), 0.0005, 0.060))
delta = d * (m * a)[:, None]            # deslocamento em influence 1,0
b0 = ml.medir(b, co, col) * 100

# vizinhanca por aresta
T = b.tris
viz = [set() for _ in range(len(co))]
for i, j, k in T:
    viz[i].update((j, k)); viz[j].update((i, k)); viz[k].update((i, j))


def invertidos(P, mask):
    nr, area = b.normais(P)
    toca = (mask[T].max(axis=1) > 0.05) & (area > b.area_min) & (b.area0 > b.area_min)
    return np.where(((nr * b.nrm0).sum(axis=1) < 0) & toca)[0]


infs = [-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0]
ruins = set()
for inf in infs:
    if abs(inf) <= 1.0:                  # repara ate o teto publicado (+-1,0)
        for t in invertidos(co + delta * inf, m):
            ruins.update(T[t])
alvo = set(ruins)
for _ in range(ANEIS):
    alvo |= {n for v in list(alvo) for n in viz[v]}
alvo = np.array(sorted(alvo))
novo = delta.copy()
for _ in range(ITER):
    med = np.array([novo[list(viz[v])].mean(axis=0) for v in alvo])
    novo[alvo] = 0.5 * novo[alvo] + 0.5 * med
print("REPARO {} {} | amplitude {:.4f} | vertices ruins {} -> regiao alisada {} ({} aneis, {} iter)".format(
    AID, KEY, a, len(ruins), len(alvo), ANEIS, ITER))
print("   influence | inv antes -> depois | cm antes -> depois")
for inf in infs:
    ia, ib = len(invertidos(co + delta * inf, m)), len(invertidos(co + novo * inf, m))
    va, vb = ml.medir(b, co + delta * inf, col), ml.medir(b, co + novo * inf, col)
    print("   {:+5.1f}     | {:4d} -> {:4d}          | {:+6.2f} -> {:+6.2f}".format(
        inf, ia, ib, va * 100 - b0 if va else float("nan"), vb * 100 - b0 if vb else float("nan")))
mx = float(np.abs(novo - delta).max() * 1000)
print("   maior mudanca de deslocamento: {:.2f} mm (em {} vertices)".format(mx, len(alvo)))
