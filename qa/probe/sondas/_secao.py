"""A secao transversal na altura da faixa, em ASCII. Sinal cru, escolha depois.

A faixa atravessa os dois bracos em corpo pesado (visto no zen_f_b10_d1 e no
zen_f_b12_d1) porque a mascara de braco e TOPOLOGICA: o componente do braco
acaba onde ele funde no tronco, e num corpo de IMC alto isso acontece bem abaixo
da faixa - em 30 dos 37 femininos. Acima da fusao o braco nao esta marcado, e o
campo da faixa so olha altura.

Antes de inventar criterio geometrico, ver o que a secao oferece: o braco e
separavel do tronco nessa altura, ou eles sao um blob so? A resposta muda o
conserto - vao dar coisas diferentes um vale entre dois picos e uma massa
continua.

    blender -b -P qa/probe/sondas/_secao.py -- --root . --id ID --zh 0.72
"""
import argparse
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--id", required=True)
ap.add_argument("--zh", type=float, nargs="+", required=True)
a = ap.parse_args(argv)

ROOT = os.path.abspath(a.root)
import bpy  # noqa: E402

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master",
                                                a.id + "_master.glb"))
obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = obj.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
z = co[:, 2]
H = float(z.max() - z.min())
z0 = float(z.min())
zh = (z - z0) / H
cx, cy = float(np.median(co[:, 0])), float(np.median(co[:, 1]))

for alvo in a.zh:
    m = np.abs(zh - alvo) < 0.004
    x, y = (co[m, 0] - cx) / H, (co[m, 1] - cy) / H
    print("\n=== %s  zh=%.3f  %d vertices  x %.3f..%.3f  y %.3f..%.3f"
          % (a.id, alvo, m.sum(), x.min(), x.max(), y.min(), y.max()))

    # raster: x na horizontal (largura do corpo), y na vertical (frente/costas)
    W, Hh = 78, 22
    g = np.zeros((Hh, W), dtype=int)
    xi = ((x - x.min()) / max(x.max() - x.min(), 1e-9) * (W - 1)).astype(int)
    yi = ((y - y.min()) / max(y.max() - y.min(), 1e-9) * (Hh - 1)).astype(int)
    for i, j in zip(yi, xi):
        g[i, j] += 1
    for r in g[::-1]:
        print("   " + "".join("#" if v > 2 else ("+" if v else ".") for v in r))

    # A PROFUNDIDADE por coluna de x. O braco e um tubo raso (frente a costas,
    # uns 0.05 H); o tronco no peito e fundo (0.20 H). Se o degrau existir, ele
    # separa os dois sem precisar achar o vinco.
    print("   x/H:  " + " ".join("%6.3f" % v for v in
                                 np.linspace(x.min(), x.max(), 12)))
    prof = []
    bx = np.linspace(x.min(), x.max(), 25)
    for i in range(24):
        s = (x >= bx[i]) & (x < bx[i + 1] + 1e-12)
        prof.append((y[s].max() - y[s].min()) if s.sum() >= 3 else 0.0)
    print("   prof: " + " ".join("%.3f" % v for v in prof))
