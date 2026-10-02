# -*- coding: utf-8 -*-
"""DE QUEM e o triangulo que inverte no morph do braco - braco ou tronco?

    blender -b -P qa/probe/sondas/morph_junta_braco.py -- --id ID [--key morph_biceps] [--inf 1.0,-1.0] [--mod scripts/morph.py]

Complemento do `morph_onde_inverte_campo.py` (sessao 41). Para cada triangulo
invertido, por vertice: distancia ao eixo do braco, mascara, e o "dono" pela
NORMAL - s_braco = n . radial do braco, s_tronco = n . radial do tronco (a
mesma pergunta do `shorts.w_arm_dono_field`, LICOES 4.5q). Se o triangulo e
pele do tronco (s_tronco > s_braco) recebendo empurrao do braco, o conserto e
separar pela normal; se e pele do braco, e outra coisa (prega, direcao).
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

AID, KEY = arg("--id"), arg("--key", "morph_biceps")
INFS = [float(x) for x in arg("--inf", "1.0,-1.0").split(",")]
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

# normal de vertice da base (media das faces, ponderada por area)
nrm_f, area_f = b.normais(co)
vn = np.zeros_like(co)
for k in range(3):
    np.add.at(vn, b.tris[:, k], nrm_f * area_f[:, None])
vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)

# radial do tronco (mesmo centro que o campo usa) e do braco
Z = co[:, 2]
rt = b._radial(co, np.interp(Z, b.tz, b.tc[:, 0]), np.interp(Z, b.tz, b.tc[:, 1]))
d_dir, _, perp_dir = b._dist_eixo(co)
d_esq, _, perp_esq = b._dist_eixo(co * np.array([-1.0, 1.0, 1.0]))
ra = np.where((co[:, 0] > 0)[:, None], perp_dir / np.maximum(d_dir, 1e-6)[:, None],
              perp_esq * np.array([-1.0, 1.0, 1.0]) / np.maximum(d_esq, 1e-6)[:, None])
dist = np.where(co[:, 0] > 0, d_dir, d_esq)
s_b = (vn * ra).sum(axis=1)
s_t = (vn * rt).sum(axis=1)

vao = b.t_top - b.t_pulso
tl0 = b.t_pulso + 0.78 * vao
tl1 = b.t_top - 0.10 * vao
th0 = b.t_top + 0.10 * vao
th1 = b.t_fusao + 0.05 * vao
t_arm = np.where(co[:, 0] > 0, (co - b.arm_c) @ b.arm_e,
                 (co * np.array([-1.0, 1.0, 1.0]) - b.arm_c) @ b.arm_e)
print("EIXO t: pulso {:+.3f} top {:+.3f} fusao {:+.3f} | banda biceps {:+.3f} {:+.3f} | "
      "{:+.3f} {:+.3f}  (rampa de cima {:.1f} cm)".format(
          b.t_pulso, b.t_top, b.t_fusao, tl0, tl1, th0, th1, 100 * (th1 - th0)))
print("JUNTA {} {} amplitude {:.4f} | corte {}".format(
    AID, KEY, a, "{:.1f}-{:.1f} cm".format(b.corte_lo * 100, b.corte_hi * 100)
    if getattr(b, "corte_adapt", False) else "fixo 8,0"))
for inf in INFS:
    P = co + d * (m * a * inf)[:, None]
    nr, area = b.normais(P)
    toca = (m[b.tris].max(axis=1) > 0.05) & (area > b.area_min) & (b.area0 > b.area_min)
    inv = ((nr * b.nrm0).sum(axis=1) < 0) & toca
    print("\ninf {:+.1f}: {} invertidos".format(inf, int(inv.sum())))
    for i in np.where(inv)[0]:
        c = co[b.tris[i]].mean(axis=0)
        print("  tri {:6d} z/H {:.3f} x {:+.3f} y {:+.3f} | area {:.1e} ({:.2f}x mediana) | "
              "desloc max {:.1f} mm".format(
                  i, (c[2] - b.zmin) / b.H, c[0], c[1], b.area0[i],
                  b.area0[i] / np.median(b.area0),
                  1000 * float(np.linalg.norm(P[b.tris[i]] - co[b.tris[i]], axis=1).max())))
        for vtx in b.tris[i]:
            dv = d[vtx] * m[vtx] * a * inf
            print("     v{:6d} t {:+.3f} dist {:.3f} m {:.2f} | s_braco {:+.2f} s_tronco {:+.2f} -> {} | "
                  "dir ({:+.2f},{:+.2f},{:+.2f}) | desloc {:.1f} mm".format(
                      vtx, t_arm[vtx], dist[vtx], m[vtx], s_b[vtx], s_t[vtx],
                      "TRONCO" if s_t[vtx] > s_b[vtx] else "braco ",
                      *d[vtx], 1000 * float(np.linalg.norm(dv))))
