"""
morph_neck.py — refaz a mascara do PESCOCO com o rosto congelado.

POR QUE
    A mascara do teste 3 era so por ALTURA, e nessa altura o rosto tambem mora:
    reduzir o pescoco levava o queixo e a boca junto. A sonda numerica aprovou
    (2 normais invertidas em 60 mil), a FOTO reprovou. Receita do
    zenith_avatar_engine para o mesmo defeito:

      "Protuberancia da nuca no minimo = problema de FORMA, nao de raio.
       Fix = freeze ASSIMETRICO (rosto so na frente, nuca reduz ate o
       occipital) + suavizar superficie."

    Ou seja: o teto da mascara nao pode ser uma altura unica. Na FRENTE ele tem
    que fechar antes (abaixo do queixo); ATRAS pode subir ate o occipital.

USO
    blender -b -P morph_neck.py -- --glb <master.glb> --out <dir>
"""
import bpy, sys, os
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
GLB = argv[argv.index("--glb") + 1]
OUT = os.path.abspath(argv[argv.index("--out") + 1])
os.makedirs(OUT, exist_ok=True)
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
zmin, zmax = co[:, 2].min(), co[:, 2].max(); H = zmax - zmin

# ONDE E A FRENTE. O nariz e o ponto que mais avanca na altura do rosto; o sinal
# dele em Y define o resto. Nao chutar: o process.py normaliza a orientacao, mas
# quem le tem que confirmar.
face = co[(co[:, 2] > zmin + 0.90 * H) & (co[:, 2] < zmin + 0.95 * H)]
frente = 1.0 if abs(face[:, 1].max()) > abs(face[:, 1].min()) else -1.0
print("frente = %+.0f em Y (nariz em y=%.3f)" % (frente, face[:, 1].max() if frente > 0 else face[:, 1].min()))

# Eixo do pescoco: centroide das fatias na regiao estreita.
zs = np.arange(zmin + 0.80 * H, zmin + 0.92 * H, 0.005)
cen = np.array([co[np.abs(co[:, 2] - z) < 0.006][:, :2].mean(axis=0) for z in zs])
nx, ny = cen[:, 0].mean(), cen[:, 1].mean()

print("\nraio por altura, separando FRENTE e ATRAS (cm) — onde o rosto comeca:")
for z in zs:
    band = co[np.abs(co[:, 2] - z) < 0.005]
    if len(band) < 8:
        continue
    d = np.sqrt((band[:, 0] - nx) ** 2 + (band[:, 1] - ny) ** 2) * 100
    f = band[:, 1] * frente > ny * frente
    print("   z/H %.3f  frente %5.1f  atras %5.1f" % ((z - zmin) / H,
          d[f].max() if f.any() else -1, d[~f].max() if (~f).any() else -1))

# O queixo: a menor altura em que a frente ja e ROSTO, nao pescoco. Detecto pelo
# salto do raio frontal (o queixo avanca bruscamente sobre o pescoco).
raios_f = []
for z in zs:
    band = co[np.abs(co[:, 2] - z) < 0.005]
    f = band[:, 1] * frente > ny * frente
    raios_f.append(np.sqrt((band[f, 0] - nx) ** 2 + (band[f, 1] - ny) ** 2).max() if f.any() else 0)
raios_f = np.array(raios_f)
i = int(np.argmin(raios_f))                       # pescoco mais estreito
salto = np.where(raios_f[i:] > raios_f[i] * 1.25)[0]
z_queixo = zs[i + salto[0]] if len(salto) else zs[-1]
print("\npescoco mais estreito em z/H %.3f | queixo comeca em z/H %.3f"
      % ((zs[i] - zmin) / H, (z_queixo - zmin) / H))

# ---------------------------------------------------------------- a mascara
# TETO QUE DEPENDE DE Y: na frente fecha abaixo do queixo; atras sobe.
# `t` = 0 na frente, 1 nas costas.
t = np.clip((co[:, 1] * frente - ny * frente) / -0.06, 0.0, 1.0)
teto_frente = z_queixo - 0.012                      # 1,2 cm de folga do queixo
teto_costas = zmin + 0.905 * H                      # sobe ate o occipital
teto = teto_frente + (teto_costas - teto_frente) * t

m = (sstep(co[:, 2], zmin + 0.790 * H, zmin + 0.830 * H)
     * (1 - sstep(co[:, 2], teto - 0.035, teto)))

# Direcao: radial em torno do eixo do pescoco.
r = np.stack([co[:, 0] - nx, co[:, 1] - ny], axis=1)
rn = np.maximum(np.linalg.norm(r, axis=1), 1e-6)
d = np.zeros((n, 3)); d[:, 0] = r[:, 0] / rn; d[:, 1] = r[:, 1] / rn

print("mascara toca %d verts (antes, so por altura, tocava a boca)" % (m > 0.01).sum())
# Quanto o ROSTO ainda se move — a trava que faltava no teste 3.
# ROSTO = acima do queixo E NA FRENTE. A primeira versao desta trava chamava
# de rosto tudo que estava acima do queixo, incluindo a NUCA — que deve reduzir
# mesmo (e a metade "assimetrica" da receita). Trava mal definida acusa defeito
# onde nao ha e esconde onde ha.
rosto = (co[:, 2] > z_queixo + 0.01) & (co[:, 1] * frente < ny * frente)
print("vertices de ROSTO (frente, acima do queixo) com mascara > 0,01: %d"
      % ((m > 0.01) & rosto).sum())


def circ(P):
    z = zmin + NECK_FRAC * H
    return hull_perim(P[np.abs(P[:, 2] - z) < 0.005][:, :2]) * 100


base = circ(co)
print("\npescoco base %.1f cm" % base)
print("varredura (reduce):")
alvos = {}
for amp in np.arange(-0.030, 0.001, 0.0025):
    P = co + d * (m * amp)[:, None]
    delta = circ(P) - base
    mov_rosto = np.linalg.norm((d * (m * amp)[:, None])[rosto], axis=1).max() * 100
    print("   amp %+.4f -> %+5.1f cm | maior movimento no ROSTO %.2f cm" % (amp, delta, mov_rosto))
    alvos[round(delta, 1)] = amp

ob.shape_key_add(name="Basis", from_mix=False)
sk = ob.shape_key_add(name="morph_neck_reduce", from_mix=False)
sk.data.foreach_set("co", (co + d * (m * -0.030)[:, None]).astype(np.float32).ravel())
sk.value = 0.0
glb = os.path.join(OUT, "morph_neck.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_morph=True,
                          export_morph_normal=False,
                          export_draco_mesh_compression_enable=False)
print("GLB ->", glb)
