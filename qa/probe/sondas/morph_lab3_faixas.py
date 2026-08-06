"""
morph_lab3.py — TESTE 3: ATE ONDE cada morph aguenta.

Os testes 1 e 2 perguntaram "funciona?". Este pergunta "ate quanto?", porque a
faixa vira a regra do salto: fora dela a selecao troca de avatar em vez de
esticar a malha. O caso real do Rogerio estourou duas faixas que eu tinha
PROPOSTO sem medir — cintura +5,0 (propus +-3) e pescoco -9,7 (propus +-7).
Numero proposto vira numero medido, como foi com o z_cap.

DEFEITO, COMO SE MEDE SEM O OLHO
    Renderizar cada passo e caro; por isso o sweep usa duas sondas numericas que
    pegam as duas falhas classicas, e SO os pontos suspeitos vao para a foto:
      normais invertidas -> dobra/inversao da superficie (o morph passou do
                            ponto e a malha virou do avesso);
      raio minimo        -> colapso (a reducao levou a secao a fechar em si).
    A foto continua sendo o veredito (licao v84 do engine); as sondas so dizem
    ONDE olhar.
"""
import bpy, sys, os, math
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
GLB = argv[argv.index("--glb") + 1]
OUT = os.path.abspath(argv[argv.index("--out") + 1])
os.makedirs(OUT, exist_ok=True)

WAIST_FRAC = 0.650
NECK_FRAC = 0.860


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
tris = np.array([list(p.vertices) for p in me.polygons if len(p.vertices) == 3])
zmin, zmax = co[:, 2].min(), co[:, 2].max(); H = zmax - zmin

# ⚠️ O BRACO SAI DA CONTA. Sem isto o fecho convexo da fatia engole os bracos e
# a "cintura" mede 162 cm em vez de 101 — o mesmo erro que o metrics.py evita
# separando por TOPOLOGIA. Identidade decidida na base, uma vez.
def _gap(z, half=0.006):
    band = co[np.abs(co[:, 2] - z) < half]
    xs = np.sort(band[band[:, 0] > 0.02][:, 0])
    if len(xs) < 4:
        return None
    d = np.diff(xs); i = int(np.argmax(d))
    return (xs[i], xs[i + 1]) if d[i] > 0.015 else None


_fusao = next((f for f in np.arange(0.60, 0.80, 0.005) if _gap(zmin + f * H) is None), 0.72)
_pts = []
for f in np.arange(0.42, _fusao - 0.01, 0.01):
    g = _gap(zmin + f * H)
    if g:
        b = co[np.abs(co[:, 2] - (zmin + f * H)) < 0.008]
        a = b[b[:, 0] > g[1] - 0.005]
        if len(a) >= 6:
            _pts.append(a.mean(axis=0))
_pts = np.array(_pts); _c = _pts.mean(axis=0)
_e = np.linalg.svd(_pts - _c)[2][0]
if _e[2] < 0:
    _e = -_e


def _dist_eixo(P, esp=False):
    Q = P * np.array([-1, 1, 1]) if esp else P
    d = Q - _c
    return np.linalg.norm(d - np.outer(d @ _e, _e), axis=1)


E_BRACO = np.minimum(_dist_eixo(co), _dist_eixo(co, True)) < 0.085

# Centro do tronco por altura (o push radial sai daqui).
zs = np.arange(zmin + 0.45 * H, zmin + 0.95 * H, 0.01)
cent = []
for z in zs:
    sel = (np.abs(co[:, 2] - z) < 0.008) & (~E_BRACO)
    cent.append(co[sel, :2].mean(axis=0) if sel.sum() > 6 else [0.0, 0.0])
cent = np.array(cent)
cx = np.interp(co[:, 2], zs, cent[:, 0]); cy = np.interp(co[:, 2], zs, cent[:, 1])
rad = np.stack([co[:, 0] - cx, co[:, 1] - cy], axis=1)
rnorm = np.maximum(np.linalg.norm(rad, axis=1), 1e-6)
dir_rad = np.zeros((n, 3)); dir_rad[:, 0] = rad[:, 0] / rnorm; dir_rad[:, 1] = rad[:, 1] / rnorm

# Mascara so por ALTURA: cintura e pescoco sao anéis fechados do tronco, sem
# braco por perto. Reducao radial UNIFORME (licao do engine: pinca lateral
# nao-uniforme cava sulcos).
m_cint = (sstep(co[:, 2], 0.560 * H + zmin, 0.615 * H + zmin)
          * (1 - sstep(co[:, 2], 0.685 * H + zmin, 0.740 * H + zmin)))
m_pesc = (sstep(co[:, 2], 0.800 * H + zmin, 0.838 * H + zmin)
          * (1 - sstep(co[:, 2], 0.885 * H + zmin, 0.925 * H + zmin)))

normal0 = None


def sondas(P, mask):
    """(circunferencia, normais invertidas, raio minimo na banda)."""
    global normal0
    v0, v1, v2 = P[tris[:, 0]], P[tris[:, 1]], P[tris[:, 2]]
    nrm = np.cross(v1 - v0, v2 - v0)
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = nrm / np.maximum(ln, 1e-12)
    if normal0 is None:
        normal0 = nrm.copy()
        invert = 0
    else:
        toca = mask[tris].max(axis=1) > 0.05
        invert = int(((nrm * normal0).sum(axis=1) < 0)[toca].sum())
    r = np.linalg.norm(np.stack([P[:, 0] - cx, P[:, 1] - cy], axis=1), axis=1)
    return invert, float(r[mask > 0.5].min()) * 100


def circ(P, frac):
    z = zmin + frac * H
    sel = (np.abs(P[:, 2] - z) < 0.005) & (~E_BRACO)
    return hull_perim(P[sel][:, :2]) * 100


sondas(co, m_cint)   # calibra a referencia de normais
base_c, base_p = circ(co, WAIST_FRAC), circ(co, NECK_FRAC)
print("BASE: cintura %.1f cm | pescoco %.1f cm" % (base_c, base_p))
print()

for nome, mask, frac, base, passos in (
        ("CINTURA", m_cint, WAIST_FRAC, base_c, np.arange(-0.035, 0.036, 0.005)),
        ("PESCOCO", m_pesc, NECK_FRAC, base_p, np.arange(-0.030, 0.031, 0.005))):
    print("%s — varredura de amplitude:" % nome)
    print("   %9s %10s %12s %12s" % ("amplitude", "delta cm", "normais inv.", "raio min cm"))
    for amp in passos:
        P = co + dir_rad * (mask * amp)[:, None]
        inv, rmin = sondas(P, mask)
        d = circ(P, frac) - base
        alerta = "  <-- DEFEITO" if inv > 0 or rmin < 1.0 else ""
        print("   %+9.3f %+10.1f %12d %12.1f%s" % (amp, d, inv, rmin, alerta))
    print()

# Exporta as pontas para a foto decidir.
ob.shape_key_add(name="Basis", from_mix=False)
for nome, delta in (("morph_waist_max", dir_rad * (m_cint * 0.035)[:, None]),
                    ("morph_waist_min", dir_rad * (m_cint * -0.035)[:, None]),
                    ("morph_neck_min", dir_rad * (m_pesc * -0.030)[:, None])):
    sk = ob.shape_key_add(name=nome, from_mix=False)
    sk.data.foreach_set("co", (co + delta).astype(np.float32).ravel())
    sk.value = 0.0
glb = os.path.join(OUT, "morph_test3.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_morph=True,
                          export_morph_normal=False,
                          export_draco_mesh_compression_enable=False)
print("GLB ->", glb)
