"""
morph_lab2.py — TESTE 2: peitoral e cintura.

POR QUE ESTE E MAIS ARRISCADO QUE O DO OMBRO
    O peitoral deste avatar e medido em at_frac 0,72, que e EXATAMENTE onde o
    braco funde com o tronco (arm_split_frac 0,72). Aumentar o peito empurra a
    parede do tronco NA DIRECAO DO BRACO — a mesma direcao em que a gordura do
    `morph_bmi` empurrava no zenith_avatar_engine quando nasceu a membrana.
    O morph de ombro escapava porque empurra para FORA, afastando do vao.

    Se a hipotese "sem morph de gordura nao ha colisao" for verdadeira mesmo,
    ela tem que sobreviver AQUI.

CINTURA — o teste que decide a contagem de avatares
    Os ~10 avatares que faltam existem para fechar vaos de CINTURA maiores que
    3 cm. Se a cintura morfar +-3 cm sem defeito, aqueles 10 deixam de ser
    necessarios. Por isso a cintura e testada NOS DOIS SENTIDOS: o reduce e o
    que o emagrecimento precisa.

USO
    blender -b -P morph_lab2.py -- --glb <master.glb> --out <dir>
"""
import bpy, sys, os, math
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
GLB = argv[argv.index("--glb") + 1]
OUT = os.path.abspath(argv[argv.index("--out") + 1])
os.makedirs(OUT, exist_ok=True)

CHEST_FRAC = 0.720
WAIST_FRAC = 0.650
ALVO_PEITO_CM = float(os.environ.get("ALVO_PEITO", "6.0"))
ALVO_CINTURA_CM = float(os.environ.get("ALVO_CINTURA", "3.0"))


def sstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def hull_perim(pts):
    if len(pts) < 3:
        return None
    p = pts[np.lexsort((pts[:, 1], pts[:, 0]))]
    def half(P):
        h = []
        for q in P:
            while len(h) >= 2 and (h[-1][0]-h[-2][0])*(q[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(q[0]-h[-2][0]) <= 0:
                h.pop()
            h.append(q)
        return h[:-1]
    h = np.array(half(p) + half(p[::-1]))
    return float(np.sum(np.linalg.norm(np.roll(h, -1, axis=0) - h, axis=1)))


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ob = [o for o in bpy.data.objects if o.type == "MESH"][0]
me = ob.data
n = len(me.vertices)
co = np.empty(n * 3); me.vertices.foreach_get("co", co); co = co.reshape(n, 3)
zmin, zmax = co[:, 2].min(), co[:, 2].max(); H = zmax - zmin


def gap_at(P, z, half=0.006):
    band = P[np.abs(P[:, 2] - z) < half]
    xs = np.sort(band[band[:, 0] > 0.02][:, 0])
    if len(xs) < 4:
        return None
    d = np.diff(xs); i = int(np.argmax(d))
    return (xs[i], xs[i + 1]) if d[i] > 0.015 else None


fusao = next(f for f in np.arange(0.60, 0.80, 0.005) if gap_at(co, zmin + f * H) is None)

# Eixo de cada braco (para PROTEGER a axila, nao para morfar).
pontos = []
for f in np.arange(0.42, fusao - 0.01, 0.01):
    g = gap_at(co, zmin + f * H)
    if not g:
        continue
    band = co[np.abs(co[:, 2] - (zmin + f * H)) < 0.008]
    arm = band[band[:, 0] > g[1] - 0.005]
    if len(arm) >= 6:
        pontos.append(arm.mean(axis=0))
pontos = np.array(pontos); centro = pontos.mean(axis=0)
eixo = np.linalg.svd(pontos - centro)[2][0]
if eixo[2] < 0:
    eixo = -eixo


def dist_eixo(P, espelhar=False):
    Q = P * np.array([-1, 1, 1]) if espelhar else P
    d = Q - centro
    return np.linalg.norm(d - np.outer(d @ eixo, eixo), axis=1)


d_braco = np.minimum(dist_eixo(co), dist_eixo(co, True))
E_BRACO = d_braco < 0.085          # identidade fixa, decidida na BASE

# Centro do tronco por altura (o push radial sai DAQUI, nao do eixo global:
# o tronco nao e um cilindro centrado).
zs = np.arange(zmin + 0.45 * H, zmin + 0.85 * H, 0.01)
cent = []
for z in zs:
    sel = (np.abs(co[:, 2] - z) < 0.008) & (~E_BRACO)
    cent.append(co[sel, :2].mean(axis=0) if sel.sum() > 6 else [0.0, 0.0])
cent = np.array(cent)
cx = np.interp(co[:, 2], zs, cent[:, 0])
cy = np.interp(co[:, 2], zs, cent[:, 1])
rad = np.stack([co[:, 0] - cx, co[:, 1] - cy], axis=1)
rnorm = np.maximum(np.linalg.norm(rad, axis=1), 1e-6)
dir_radial = np.zeros((n, 3))
dir_radial[:, 0] = rad[:, 0] / rnorm
dir_radial[:, 1] = rad[:, 1] / rnorm

# PEITORAL — banda em torno de 0,72H, radial, e FUGINDO DO BRACO.
# O gate por distancia ao braco e a licao v23/v26 do engine ("peito/flanco em
# A-pose colam no braco se o gate for por |x|").
m_peito = (sstep(co[:, 2], 0.630 * H + zmin, 0.685 * H + zmin)
           * (1 - sstep(co[:, 2], 0.760 * H + zmin, 0.815 * H + zmin))
           * sstep(d_braco, 0.075, 0.140))

# CINTURA — banda em torno de 0,65H, radial UNIFORME (convexo).
# "Pinca lateral nao-uniforme cava sulcos/valas" (licao do engine).
m_cintura = (sstep(co[:, 2], 0.560 * H + zmin, 0.615 * H + zmin)
             * (1 - sstep(co[:, 2], 0.685 * H + zmin, 0.740 * H + zmin))
             * sstep(d_braco, 0.075, 0.140))

print("mascaras: peito %d verts | cintura %d verts | sobrepoem %d"
      % ((m_peito > 0.01).sum(), (m_cintura > 0.01).sum(),
         ((m_peito > 0.01) & (m_cintura > 0.01)).sum()))


def medir(P):
    """Peitoral e cintura: fecho convexo do TRONCO (braco removido por identidade)."""
    out = []
    for frac in (CHEST_FRAC, WAIST_FRAC):
        z = zmin + frac * H
        sel = (np.abs(P[:, 2] - z) < 0.005) & (~E_BRACO)
        out.append(hull_perim(P[sel][:, :2]))
    return [(v * 100 if v else None) for v in out]


base_p, base_c = medir(co)
print("BASE: peitoral %.1f cm | cintura %.1f cm   (regua oficial: 101,9 e 90,2)"
      % (base_p, base_c))


def amplitude(mask, alvo_cm, idx, base, sinal=1.0):
    lo, hi = 0.0, 0.06
    for _ in range(24):
        mid = (lo + hi) / 2
        v = medir(co + dir_radial * (mask * mid * sinal)[:, None])[idx]
        if v is None:
            return lo
        if (v - base) * sinal < alvo_cm:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


amp_p = amplitude(m_peito, ALVO_PEITO_CM, 0, base_p)
amp_c = amplitude(m_cintura, ALVO_CINTURA_CM, 1, base_c)
amp_cr = amplitude(m_cintura, ALVO_CINTURA_CM, 1, base_c, -1.0)
print("amplitudes: peito +%.4f m | cintura +%.4f m | cintura reduce -%.4f m"
      % (amp_p, amp_c, amp_cr))

d_peito = dir_radial * (m_peito * amp_p)[:, None]
d_cint_mais = dir_radial * (m_cintura * amp_c)[:, None]
d_cint_menos = -dir_radial * (m_cintura * amp_cr)[:, None]


def vao(P):
    pior = None
    for f in np.arange(fusao - 0.10, fusao, 0.005):
        g = gap_at(P, zmin + f * H, 0.006)
        if g:
            w = (g[1] - g[0]) * 100
            if pior is None or w < pior[0]:
                pior = (w, f)
    return pior


ESTADOS = [("base            ", np.zeros((n, 3))),
           ("peito +%.0fcm     " % ALVO_PEITO_CM, d_peito),
           ("cintura +%.0fcm   " % ALVO_CINTURA_CM, d_cint_mais),
           ("cintura -%.0fcm   " % ALVO_CINTURA_CM, d_cint_menos),
           ("peito+cintura+  ", d_peito + d_cint_mais)]
for nome, delta in ESTADOS:
    P = co + delta
    p, c = medir(P)
    v = vao(P)
    print("%s peito %6.1f | cintura %6.1f | vao da axila %s"
          % (nome, p or -1, c or -1, ("%.2f cm" % v[0]) if v else "FECHOU"))

ob.shape_key_add(name="Basis", from_mix=False)
for nome, delta in (("morph_chest", d_peito),
                    ("morph_waist", d_cint_mais),
                    ("morph_waist_reduce", d_cint_menos)):
    sk = ob.shape_key_add(name=nome, from_mix=False)
    sk.data.foreach_set("co", (co + delta).astype(np.float32).ravel())
    sk.value = 0.0

glb = os.path.join(OUT, "morph_test2_zen_m_b05h_d1.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_morph=True,
                          export_morph_normal=False,
                          export_draco_mesh_compression_enable=False)
print("GLB -> %s (%.0f KB)" % (glb, os.path.getsize(glb) / 1024))
