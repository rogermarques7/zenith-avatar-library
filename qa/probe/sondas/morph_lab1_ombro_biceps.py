"""
morph_lab.py — TESTE de viabilidade: morph de ombro + biceps num avatar da
zenith-avatar-library, SEM o morph de gordura global (morph_bmi).

POR QUE ESTE TESTE EXISTE
    O zenith_avatar_engine tentou cobrir IMC 18-40 deformando UMA malha e
    quebrou 5 vezes na axila (v23 braco colado, v77 facetamento na juncao,
    v83 membrana, v84 bolha, v91 reprovado no device). A leitura do Rogerio:
    as falhas apareciam no estado COMBINADO com o slider de IMC — o morph de
    aumento isolado se comportava melhor. Como aqui a biblioteca ja tem 76
    corpos reais, a gordura NAO precisa ser morfada: quando a distancia cresce,
    a selecao troca de avatar. Entao o morph fica pequeno e sem `morph_bmi`.

    Este script testa exatamente essa hipotese, na regiao que matou o outro
    projeto.

O QUE ELE NAO FAZ
    Nao escreve em 02_master/ nem em 03_dist/. Tudo sai na pasta de saida.

USO
    blender -b -P morph_lab.py -- --glb <master.glb> --out <dir>
"""
import bpy, sys, os, math
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
GLB = argv[argv.index("--glb") + 1]
OUT = argv[argv.index("--out") + 1]
os.makedirs(OUT, exist_ok=True)

SHOULDER_FRAC = 0.795          # a mesma altura que o metrics.py mede
ALVO_OMBRO_CM = float(os.environ.get("ALVO_OMBRO", "6.0"))
ALVO_BICEPS_CM = float(os.environ.get("ALVO_BICEPS", "4.0"))
BANDA_LO = float(os.environ.get("BANDA_LO", "0.745"))   # onde a mascara do ombro comeca


def sstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def hull_perim(pts):
    """Perimetro do fecho convexo 2D — a mesma definicao do metrics.py: fita
    metrica nao entra em concavidade."""
    if len(pts) < 3:
        return None
    p = pts[np.lexsort((pts[:, 1], pts[:, 0]))]
    def half(P):
        h = []
        for q in P:
            while len(h) >= 2 and np.cross(h[-1] - h[-2], q - h[-2]) <= 0:
                h.pop()
            h.append(q)
        return h[:-1]
    h = np.array(half(p) + half(p[::-1]))
    return float(np.sum(np.linalg.norm(np.roll(h, -1, axis=0) - h, axis=1)))


# ---------------------------------------------------------------- carregar
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ob = [o for o in bpy.data.objects if o.type == "MESH"][0]
me = ob.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)

zmin, zmax = co[:, 2].min(), co[:, 2].max()
H = zmax - zmin
print("malha: %d verts | altura %.4f m" % (n, H))


# ------------------------------------------------- achar a fusao braco/tronco
def gap_at(z, half=0.006):
    """(borda do tronco, inicio do braco) no lado direito, ou None se fundido."""
    band = co[np.abs(co[:, 2] - z) < half]
    xs = np.sort(band[band[:, 0] > 0.02][:, 0])
    if len(xs) < 4:
        return None
    d = np.diff(xs)
    i = int(np.argmax(d))
    return (xs[i], xs[i + 1]) if d[i] > 0.015 else None


fusao = None
for f in np.arange(0.60, 0.80, 0.005):
    if gap_at(zmin + f * H) is None:
        fusao = f
        break
print("bracos fundem ao tronco em z/H = %.3f" % fusao)

# Eixo do braco direito: regressao pelos centroides das fatias onde ele ainda
# e separado. O push do biceps tem que ser PERPENDICULAR a este eixo — em
# A-pose um empurrao horizontal engorda na diagonal e sobe a medida errada.
pontos = []
for f in np.arange(0.42, fusao - 0.01, 0.01):
    z = zmin + f * H
    g = gap_at(z)
    if not g:
        continue
    band = co[np.abs(co[:, 2] - z) < 0.008]
    arm = band[band[:, 0] > g[1] - 0.005]
    if len(arm) >= 6:
        pontos.append(arm.mean(axis=0))
pontos = np.array(pontos)
centro = pontos.mean(axis=0)
u, s, vt = np.linalg.svd(pontos - centro)
eixo = vt[0] / np.linalg.norm(vt[0])
if eixo[2] < 0:
    eixo = -eixo
print("eixo do braco: (%.3f, %.3f, %.3f)  inclinacao %.1f graus do vertical"
      % (*eixo, math.degrees(math.acos(abs(eixo[2])))))


def dist_ao_eixo(P, c, e):
    """Distancia perpendicular ao eixo + parametro ao longo dele."""
    d = P - c
    t = d @ e
    perp = d - np.outer(t, e)
    return np.linalg.norm(perp, axis=1), t, perp


# ---------------------------------------------------------------- as mascaras
lado = np.sign(co[:, 0])
absx = np.abs(co[:, 0])

# OMBRO — banda em torno da altura da medida, empurrando para FORA em X.
# Exclui o pescoco (|x| pequeno) e desce suave para nao criar degrau no peito.
m_ombro = (sstep(co[:, 2], (BANDA_LO) * H + zmin, (BANDA_LO + 0.045) * H + zmin)
           * (1 - sstep(co[:, 2], (0.845) * H + zmin, (0.885) * H + zmin))
           * sstep(absx, 0.055 * H, 0.105 * H))

# BICEPS — so no braco, perpendicular ao eixo, fade nas duas pontas.
d_dir, t_dir, perp_dir = dist_ao_eixo(co, centro, eixo)
d_esq, t_esq, perp_esq = dist_ao_eixo(co * np.array([-1, 1, 1]), centro, eixo)
t_lo, t_hi = np.percentile(pontos @ eixo - centro @ eixo, [10, 90])
braco_dir = (co[:, 0] > 0) & (d_dir < 0.075)
braco_esq = (co[:, 0] < 0) & (d_esq < 0.075)
m_biceps = np.zeros(n)
for mask, t in ((braco_dir, t_dir), (braco_esq, t_esq)):
    janela = sstep(t, t_lo - 0.02, t_lo + 0.06) * (1 - sstep(t, t_hi - 0.06, t_hi + 0.02))
    m_biceps = np.maximum(m_biceps, np.where(mask, janela, 0.0))

# ⚠️ GATE DE PROPRIEDADE (licao v84 do engine): onde o biceps manda, o ombro
# nao mexe. Sem isso os dois campos se somam no vale da axila — que e
# exatamente onde a membrana nasceu la.
m_ombro = m_ombro * (1 - 0.85 * m_biceps)

print("mascaras: ombro toca %d verts | biceps toca %d verts | sobrepoem %d"
      % ((m_ombro > 0.01).sum(), (m_biceps > 0.01).sum(),
         ((m_ombro > 0.01) & (m_biceps > 0.01)).sum()))


# ------------------------------------------------------ direcoes de deslocamento
dir_ombro = np.zeros((n, 3))
dir_ombro[:, 0] = lado                      # empurra lateral, para fora
dir_biceps = np.zeros((n, 3))
for mask, perp, d in ((braco_dir, perp_dir, d_dir), (braco_esq, perp_esq, d_esq)):
    seguro = np.maximum(d, 1e-6)[:, None]
    v = perp / seguro
    if mask is braco_esq:
        v = v * np.array([-1, 1, 1])        # espelha de volta
    dir_biceps[mask] = v[mask]


# ⚠️ QUEM E BRACO SE DECIDE UMA VEZ, NA MALHA BASE — nunca na deformada.
# Primeira versao selecionava por `d < 0.075` sobre as posicoes JA morfadas:
# ao empurrar para fora, o vertice saia do proprio filtro e a medida sumia
# (a busca de amplitude divergiu para 10 cm de empurrao). E a mesma familia do
# "gate de propriedade" do engine: identidade e do vertice, nao da posicao.
E2 = np.array([eixo[1], -eixo[0], 0.0]); E2 /= np.linalg.norm(E2)
E3 = np.cross(eixo, E2)
_d0, _t0, _ = dist_ao_eixo(co, centro, eixo)
ARM_DIR = (co[:, 0] > 0) & (_d0 < 0.075) & (_t0 > t_lo + 0.02) & (_t0 < t_hi - 0.02)
T_BASE = _t0


def medir(P):
    """Ombro (fecho convexo na altura da medida) e biceps (perpendicular ao eixo)."""
    z = zmin + SHOULDER_FRAC * H
    fatia = P[np.abs(P[:, 2] - z) < 0.005][:, :2]
    omb = hull_perim(fatia)
    best = None
    for tc in np.arange(t_lo + 0.03, t_hi - 0.03, 0.01):
        sel = ARM_DIR & (np.abs(T_BASE - tc) < 0.006)   # fatia definida na BASE
        if sel.sum() < 8:
            continue
        d = P[sel] - centro
        pr = d - np.outer(d @ eixo, eixo)               # posicao MORFADA, projetada
        p = hull_perim(np.c_[pr @ E2, pr @ E3])
        if p and (best is None or p > best):
            best = p
    return (omb * 100 if omb else None), (best * 100 if best else None)


base_omb, base_bic = medir(co)
print("BASE: ombro %.1f cm | biceps %.1f cm" % (base_omb, base_bic))

# ------------------------------------------------------------ calibrar em cm
def amplitude(mask, direc, alvo_cm, qual):
    """Busca binaria na amplitude ate a medida subir o alvo em cm.

    Teto de 5 cm de deslocamento: acima disso nao e mais 'aproximar o avatar
    da medida do usuario', e sim esculpir outro corpo — e o teste perde o
    sentido. Se nao alcancar, denuncia em vez de devolver um numero.
    """
    lo, hi = 0.0, 0.05
    base = base_omb if qual == "ombro" else base_bic
    for _ in range(24):
        mid = (lo + hi) / 2
        o, b = medir(co + direc * (mask * mid)[:, None])
        v = (o if qual == "ombro" else b)
        if v is None:
            print("  AVISO: medida de %s sumiu na amplitude %.4f" % (qual, mid))
            return lo
        if v - base < alvo_cm:
            lo = mid
        else:
            hi = mid
    if hi >= 0.0499:
        print("  AVISO: %s nao alcancou +%.1f cm dentro do teto de 5 cm" % (qual, alvo_cm))
    return (lo + hi) / 2


amp_o = amplitude(m_ombro, dir_ombro, ALVO_OMBRO_CM, "ombro")
amp_b = amplitude(m_biceps, dir_biceps, ALVO_BICEPS_CM, "biceps")
print("amplitude calibrada: ombro %.4f m | biceps %.4f m" % (amp_o, amp_b))

d_ombro = dir_ombro * (m_ombro * amp_o)[:, None]
d_biceps = dir_biceps * (m_biceps * amp_b)[:, None]

# ------------------------------------------- a regua da membrana: vao da axila
def vao_axila(P):
    """Menor folga entre braco e tronco nas fatias onde eles ainda sao
    separados. Se isso for a zero, a membrana nasceu."""
    pior = None
    for f in np.arange(fusao - 0.10, fusao, 0.005):
        z = zmin + f * H
        band = P[np.abs(P[:, 2] - z) < 0.006]
        xs = np.sort(band[band[:, 0] > 0.02][:, 0])
        if len(xs) < 4:
            continue
        d = np.diff(xs)
        i = int(np.argmax(d))
        if d[i] > 0.004:
            g = d[i] * 100
            if pior is None or g < pior[0]:
                pior = (g, f)
    return pior


for nome, P in (("base          ", co),
                ("so ombro      ", co + d_ombro),
                ("so biceps     ", co + d_biceps),
                ("AMBOS no max  ", co + d_ombro + d_biceps)):
    o, b = medir(P)
    v = vao_axila(P)
    print("%s ombro %6.1f cm | biceps %5.1f cm | vao minimo da axila %s"
          % (nome, o or -1, b or -1,
             ("%.2f cm em z/H %.3f" % v) if v else "FECHOU (fundiu)"))

# ------------------------------------------------------------ shape keys reais
ob.shape_key_add(name="Basis", from_mix=False)
for nome, delta in (("morph_shoulders", d_ombro), ("morph_biceps", d_biceps)):
    sk = ob.shape_key_add(name=nome, from_mix=False)
    novo = (co + delta).astype(np.float32).ravel()
    sk.data.foreach_set("co", novo)
    sk.value = 0.0

glb_out = os.path.join(OUT, "morph_test_zen_m_b05h_d1.glb")
bpy.ops.export_scene.gltf(filepath=glb_out, export_format="GLB",
                          export_morph=True, export_morph_normal=False,
                          export_draco_mesh_compression_enable=False)
print("GLB com shape keys -> %s (%.0f KB)" % (glb_out, os.path.getsize(glb_out) / 1024))
