# -*- coding: utf-8 -*-
"""A RAMPA DE CIMA da faixa do biceps, no acervo inteiro (sessao 41).

    blender -b -P qa/probe/sondas/biceps_rampa.py -- [--ids a,b,c] [--mod scripts/morph.py]

A faixa do biceps no eixo do braco desce de t_top + 0,10 vao ate
t_fusao + 0,05 vao. Quando a fusao braco/tronco fica colada no arm_top, essa
rampa encolhe a menos de 1 cm e vira DEGRAU - o triangulo que o atravessa
inverte. Esta sonda imprime, por corpo: os landmarks no eixo, o comprimento da
rampa de cima e da de baixo, e se o `morph_map.json` tem biceps publicado.
"""
import importlib.util
import json
import os
import sys

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


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

mapa = json.load(open(os.path.join(ROOT, "config", "morph_map.json"), encoding="utf-8"))
ids = arg("--ids").split(",") if arg("--ids") else sorted(mapa)
print("RAMPA id               pulso    top  fusao | baixo cm  cima cm | biceps_no_mapa")
for aid in ids:
    try:
        _, src = _zp.dist_glb_current(ROOT, aid)
        ob, co_real, co, mesh, sk = ml.carregar(src)
        b = ml.Base(co, mesh, aid)
    except Exception as e:  # noqa: BLE001
        print("RAMPA {:16s} ERRO {}".format(aid, e))
        continue
    vao = b.t_top - b.t_pulso
    tl0, tl1 = b.t_pulso + 0.78 * vao, b.t_top - 0.10 * vao
    th0, th1 = b.t_top + 0.10 * vao, b.t_fusao + 0.05 * vao
    tem = any(mm["key"] == "morph_biceps" for mm in mapa.get(aid, {}).get("morphs", []))
    print("RAMPA {:16s} {:+.3f} {:+.3f} {:+.3f} | {:7.1f}  {:7.1f} | {}".format(
        aid, b.t_pulso, b.t_top, b.t_fusao, 100 * (tl1 - tl0), 100 * (th1 - th0),
        "sim" if tem else "NAO"))
