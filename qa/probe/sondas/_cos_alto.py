# -*- coding: utf-8 -*-
"""_cos_alto.py - arestas vivas DEITADAS acima do cos atual, por setor.

    blender -b -P qa/probe/sondas/_cos_alto.py -- ID [zlo zhi]

Existe porque o corredor da borda viva (+-4 cm em volta do cos atual) nao
alcanca um cos modelado muito mais alto - o zen_f_b11_d1 tinha a borda do
tecido nas costas bem acima das duas linhas (sessao 39).
"""
import math, os, sys
import bpy
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts")); sys.path.insert(0, HERE)
sys.argv_saved = list(sys.argv)
argv = sys.argv[sys.argv.index("--") + 1:]
aid = argv[0]
zlo, zhi = (float(argv[1]), float(argv[2])) if len(argv) > 2 else (0.50, 0.70)
sys.argv = [sys.argv[0], "--", "--ids", aid, "--sem-render"]
import borda_viva as BV   # noqa (so as funcoes)
import shorts as S
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = ob.data; me.update()
n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
eid, ev, mid, ang = BV.arestas_vivas(me, co)
vet = co[ev[:, 1]] - co[ev[:, 0]]
deitada = np.abs(vet[:, 2]) < 0.7071 * np.linalg.norm(vet, axis=1)
braco = is_arm[ev[:, 0]] | is_arm[ev[:, 1]]
zh = mid[:, 2] / H
e = S.load_map(ROOT)[aid]
cos = BV.curva_mapa(e["waist_zh"])
sel = deitada & ~braco & (ang >= 22) & (zh > zlo) & (zh < zhi)
th = np.arctan2(mid[sel, 1], mid[sel, 0])
b = ((th + math.pi) / (2 * math.pi) * 24).astype(int) % 24
for j in range(24):
    zz = np.sort(zh[sel][b == j])
    az = -180 + (j + .5) * 15
    # agrupa em alturas (gap > 0.006)
    grupos = []
    for z in zz:
        if grupos and z - grupos[-1][-1] < 0.006:
            grupos[-1].append(z)
        else:
            grupos.append([z])
    txt = "  ".join("%.3f(%d)" % (np.median(g), len(g)) for g in grupos if len(g) >= 3)
    print("setor %2d az %+6.1f  cos %.3f | %s" % (j, az, cos[j], txt))
