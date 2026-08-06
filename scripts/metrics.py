#!/usr/bin/env python3
"""
metrics.py - Antropometria dos masters da Zenith Avatar Library.

Le  02_master/{id}_master.glb
Gera metrics/library_metrics.json  (acumulativo: mescla a cada rodada)

POR QUE ESTE SCRIPT EXISTE
    O 'measure.py' mede a FOLHA DE REFERENCIA 2D em % da altura da figura.
    Serve para ordenar a grade e pegar inversao, mas mede o DESENHO, nao o
    produto - e a Meshy infere geometria, entao os dois divergem. Alem disso
    "% de pixel" nao se compara com uma fita metrica.

    Este script mede o MASTER 3D em circunferencias, que e o que permite:
      1. calibrar a grade contra pessoas reais (teste final);
      2. dar alvo numerico para as shape keys do sistema hibrido
         ("biceps +2 cm" so existe se o biceps de base for conhecido).

TRES DECISOES QUE MUDAM OS NUMEROS
    1. Circunferencia = perimetro do FECHO CONVEXO da secao, nao o perimetro
       real. Fita metrica nao entra em concavidade; medir o perimetro
       verdadeiro daria numeros sistematicamente maiores que a fita.

    2. As partes do corpo sao separadas por TOPOLOGIA, nao por distancia.
       Cortar uma malha fechada num plano produz LACOS fechados independentes
       (tronco, braco esq, braco dir). Agrupar por proximidade nao funciona: a
       folga da axila e menor que a aresta media do master 18k, entao o tronco
       e os bracos virariam um cluster so e o peito mediria ~137 cm.

    3. Todo master tem a MESMA altura canonica (1,75 m) e o app escala por
       altura do usuario. Entao o numero comparavel com uma pessoa real nao e
       o centimetro, e a RAZAO circunferencia/altura - invariante a escala.
       O JSON guarda os dois; para calibrar, usar a razao.

MEMBRO EM A-POSE
    Os bracos ficam a ~40 graus do eixo vertical. Uma fatia horizontal corta o
    biceps em diagonal e superestima a circunferencia em ~1/cos(40) = 1,31 -
    erro grande demais para calibrar. Por isso cada medida de membro estima o
    eixo local (deriva do centroide do laco entre z-d e z+d) e projeta os
    pontos no plano PERPENDICULAR a esse eixo antes de fechar o casco. No
    tronco o eixo ja e ~vertical e a correcao vira identidade.

RESSALVA
    O master inclui a geometria do short. Quadril e coxa saem com a espessura
    do tecido junto. Sao shorts de compressao colados, entao o erro e < 1 cm,
    mas ao calibrar contra pessoa real vale medir por cima de roupa justa.

USO
    python scripts/metrics.py zen_m_b05_d2
    python scripts/metrics.py --all
    python scripts/metrics.py --all --csv        # tabela em metrics/library_metrics.csv

O Blender roda headless via subprocess (mesmo padrao do process.py: este
arquivo se auto-reinvoca em modo WORKER). Se o executavel nao estiver no PATH,
aponte-o pela variavel de ambiente BLENDER.
"""

import os
import sys
import glob
import json
import argparse
import subprocess
from datetime import datetime, timezone

# ==========================================================================
# CONSTANTES  (ajustar aqui, nunca no meio do codigo)
# ==========================================================================

CANONICAL_HEIGHT_M = 1.75      # igual ao process.py; todos os masters tem esta altura

# ANCORAS ESQUELETICAS (fracao da estatura)
#
# O Character Bible obriga a MESMA altura e as MESMAS proporcoes em toda a
# grade - "a diferenca entre tipos de corpo aparece em largura e volume, nunca
# em altura". Logo virilha e axila caem sempre na mesma fracao da estatura:
# e um INVARIANTE do projeto, nao um chute. Confirmado na medicao: a virilha
# detectada deu 0,466 IDENTICA nos tres avatares magros/atleticos.
#
# Nao usar a deteccao como ancora foi uma correcao necessaria. O que a
# topologia detecta e "onde os membros deixam de se tocar", que so coincide
# com virilha/axila em corpo magro. No b11_d1 (obesidade II) as coxas se tocam
# e a "virilha" detectada caiu em 0,334 - todos os landmarks ancorados nela
# desabaram para a barriga e a cintura mediu 222 cm.
#
# A deteccao continua rodando, mas agora so como DIAGNOSTICO: ela diz ate que
# altura os membros estao separados, e portanto quais medidas sao confiaveis.
CROTCH_FRAC  = 0.466
ARMPIT_FRAC  = 0.710
#
# Posicoes abaixo sao FRACOES DO VAO virilha->axila (0 = virilha, 1 = axila),
# ou fracoes da estatura quando fora desse vao.
# Alturas de fita, em fracao da estatura. Fixas de proposito: e assim que uma
# fita metrica mede uma pessoa (peito na linha do mamilo, cintura no umbigo), e
# so numero medido no MESMO lugar em todos os avatares e comparavel entre si.
# Procurar "o maximo da faixa" parecia mais esperto e estava errado: num obeso
# o maximo da faixa do peito e a BARRIGA, e o b11_d1 mediu 246 cm de peito.
#
# ONDE AS BANDAS FORAM CALIBRADAS (01/08, sessao 20)
#     O app Zenith desenha, em cada tela do guia de medidas, o anel roxo na
#     altura exata onde manda passar a fita. Isolando esse anel por pixel e
#     dividindo pela estatura da figura, sai um at_frac COMPARAVEL com o daqui
#     - e ele e regua EXTERNA, porque nasceu no outro repositorio, sem
#     combinacao. Ele bate em 0,001 no quadril (0,507 x 0,507) e na cintura
#     minima (0,645 x 0,644), o que calibra a leitura; e por isso as
#     divergencias dele valem alguma coisa. Ver docs/INTEGRACAO_ZENITH.md.
NAVEL_FRAC   = 0.600       # cintura de fita
NECK_BAND    = (0.830, 0.900)   # pescoco: o ponto mais ESTREITO (definicao correta)
WAIST_BAND   = (0.550, 0.680)   # cintura natural: o ponto mais estreito do tronco
HIP_BAND     = (0.470, 0.550)   # quadril: o ponto mais LARGO (e o que a fita busca)
CHEST_PAD_M  = 0.010       # recuo quando o peito precisa descer ate os bracos

# PEITO: continua FIXO, e agora isso esta MEDIDO, nao herdado.
#     O INTEGRACAO_ZENITH.md secao 6.2 mandava trocar por "maximo numa banda".
#     Testado em 01/08 com CHEST_BAND = (0,715, 0,775): no b01_d1 o maximo subiu
#     para 0,764 e o peito foi de 78,2 para 86,2 cm. Os +8 cm nao sao peito - o
#     maximo FOGE PARA A AXILA, onde dorsal e deltoide entram no casco convexo.
#     O comentario de cima avisava do risco pela barriga; o risco real e o
#     oposto, e so aparece em corpo magro (no obeso o arm_split ja corta antes).
#     Peito de fita e LANDMARK (linha do mamilo), nao extremo. Banda descartada.
CHEST_FRAC   = 0.720       # linha do mamilo

# OMBRO: coluna NOVA (01/08). O app coleta shoulder_cm e ate agora a biblioteca
#     nao tinha o que responder. E CIRCUNFERENCIA, nao largura - decisao tomada
#     no INTEGRACAO_ZENITH.md secao 8c (largura de deltoide a deltoide e
#     inviavel de auto-medir: fita reta, horizontal, com as duas pontas fora do
#     campo de visao). O render do app ja e um anel, e a altura dele e a fonte
#     deste numero: 0,795 da estatura.
#     Tambem foi tentado como maximo de banda (0,760-0,825) e tambem foi
#     descartado pelo mesmo motivo do peito: em 2 dos 3 avatares de teste o
#     maximo desceu ate o piso da banda, ou seja, fugiu para o TORAX. Ombro de
#     fita tambem e landmark.
#     A fatia fica ACIMA da axila DE PROPOSITO: os deltoides estao fundidos ao
#     tronco, a secao e um laco fechado unico e o casco convexo dele e
#     exatamente o que a fita mede. Por isso a coluna passa check_arms=False -
#     "bracos fundidos" e a definicao da medida, nao um defeito dela.
SHOULDER_FRAC = 0.795

ARM_PAD_M    = 0.020       # afasta a medida de biceps da zona de fusao do deltoide
THIGH_BAND_M = 0.060       # coxa: maximo nos 6 cm abaixo da virilha

# PANTURRILHA: o teto era 0,320 e ESTAVA MEDINDO O JOELHO.
#     Medido em 01/08: 50 dos 76 avatares (35 dos 51 na faixa de usuario)
#     travavam o maximo em 0,320 exato - a borda da propria banda. Maximo que
#     pousa na borda em 2/3 dos casos nao e maximo, e corte: a 0,320 da estatura
#     (56 cm do chao) a fatia pega a base da coxa, porque a linha do joelho fica
#     em ~0,285. Os 16 que escapavam achavam o pico em 0,206-0,223, que e onde o
#     app desenha o anel (0,214) e onde o ventre da panturrilha realmente esta.
#     A coluna media DUAS PARTES DO CORPO sob o mesmo nome.
#     O teto novo fica abaixo da linha do joelho, entao o joelho sai do alcance.
CALF_BAND    = (0.170, 0.265)   # fracao da estatura

# Quanto o pico pode encostar na borda da banda antes de ser DENUNCIADO.
# Existe por causa do defeito da panturrilha acima: ele sobreviveu a producao
# inteira porque nada olhava ONDE o maximo tinha caido, so QUANTO ele valia.
# Uma banda cujo extremo vive na borda esta cortando a medida, nao achando-a.
BAND_EDGE_TOL_FRAC = 0.004

COLUMNS = ["neck", "shoulder", "chest", "waist_navel", "waist_min", "hip",
           "biceps", "forearm", "wrist", "thigh", "calf"]

# Densidade corporal media. Varia ~1,07 (muito magro) a ~1,00 (obeso); usar um
# valor unico introduz erro de ~3% na massa, irrelevante perto do que se quer
# medir aqui (se o avatar cai ou nao na faixa de IMC que promete).
BODY_DENSITY = 1010.0      # kg/m3

SCAN_STEP_M     = 0.005    # passo das varreduras
SLICE_DELTA_M   = 0.010    # +/-1 cm para estimar o eixo local do membro
MAX_AXIS_TILT   = 0.50     # cos minimo com a vertical; abaixo disso o eixo e suspeito
MIN_LOOP_PTS    = 6        # laco com menos pontos que isso e ruido de malha
REL_AREA_MIN    = 0.05     # laco com area < 5% da maior da fatia e dedo/ruido
CROTCH_RATIO    = 1.5      # acima da virilha o laco da pelve domina o 2o colocado

# ==========================================================================
# Deteccao de contexto: estamos rodando DENTRO do Blender?
# ==========================================================================
try:
    import bpy  # noqa: F401
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


# ==========================================================================
#  DRIVER  (Python normal, sem bpy)
# ==========================================================================

def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def find_blender():
    """Localiza o executavel do Blender. Ordem: env BLENDER -> PATH -> instalacoes comuns."""
    import shutil

    env = os.environ.get("BLENDER")
    if env:
        if os.path.isfile(env):
            return env
        sys.exit("A variavel de ambiente BLENDER aponta para um arquivo inexistente:\n  {}".format(env))

    onpath = shutil.which("blender")
    if onpath:
        return onpath

    candidates = []
    for base in (r"C:\Program Files\Blender Foundation",
                 r"C:\Program Files (x86)\Blender Foundation"):
        candidates += glob.glob(os.path.join(base, "Blender *", "blender.exe"))
    candidates += glob.glob("/Applications/Blender*.app/Contents/MacOS/Blender")
    candidates += ["/usr/bin/blender", "/usr/local/bin/blender", "/snap/bin/blender"]

    existing = sorted(c for c in candidates if os.path.isfile(c))
    if existing:
        return existing[-1]

    sys.exit(
        "Blender nao encontrado. Aponte o executavel:\n"
        '  Windows:  set BLENDER="C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe"\n'
        "  macOS:    export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender\n"
        "  Linux:    export BLENDER=/usr/bin/blender"
    )


def driver_main():
    ap = argparse.ArgumentParser(description="Antropometria dos masters (circunferencias em cm).")
    ap.add_argument("ids", nargs="*", help="ids dos avatares (ex.: zen_m_b05_d2)")
    ap.add_argument("--all", action="store_true", help="mede todos os masters existentes")
    ap.add_argument("--csv", action="store_true", help="grava tambem metrics/library_metrics.csv")
    args = ap.parse_args()

    root = repo_root()
    master_dir = os.path.join(root, "02_master")

    if args.all:
        ids = sorted(os.path.basename(p)[:-len("_master.glb")]
                     for p in glob.glob(os.path.join(master_dir, "*_master.glb")))
    else:
        ids = args.ids
    if not ids:
        ap.error("informe ao menos um id ou use --all")

    missing = [i for i in ids
               if not os.path.isfile(os.path.join(master_dir, i + "_master.glb"))]
    if missing:
        sys.exit("master inexistente para: {}".format(", ".join(missing)))

    blender = find_blender()
    print("Blender: {}".format(blender))
    print("Medindo {} master(es)...".format(len(ids)))
    print("-" * 70)

    # Uma unica invocacao do Blender para todos os ids: o startup custa ~10 s e
    # pagar isso 30 vezes seria o grosso do tempo total.
    cmd = [blender, "--background", "--python", os.path.abspath(__file__), "--",
           "--worker", "--root", root, "--ids"] + ids
    if args.csv:
        cmd.append("--csv")
    sys.exit(subprocess.run(cmd).returncode)


# ==========================================================================
#  GEOMETRIA  (puro numpy; roda dentro do Blender)
# ==========================================================================

def convex_hull_2d(pts):
    """Casco convexo por monotone chain. pts: array (n,2). Retorna (m,2) ordenado."""
    import numpy as np
    if len(pts) < 3:
        return pts
    p = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for q in p:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], q) <= 0:
            lower.pop()
        lower.append(q)
    upper = []
    for q in p[::-1]:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], q) <= 0:
            upper.pop()
        upper.append(q)
    h = lower[:-1] + upper[:-1]
    return np.array(h) if len(h) >= 3 else pts


def hull_perimeter_area(pts):
    """(perimetro, area) do fecho convexo 2D. O perimetro e o que a fita le."""
    import numpy as np
    h = convex_hull_2d(pts)
    if len(h) < 3:
        return 0.0, 0.0
    nxt = np.roll(h, -1, axis=0)
    per = float(np.linalg.norm(h - nxt, axis=1).sum())
    area = float(abs((h[:, 0] * nxt[:, 1] - nxt[:, 0] * h[:, 1]).sum()) / 2.0)
    return per, area


def mesh_volume(verts, tris):
    """Volume da malha fechada (teorema da divergencia sobre os triangulos).

    So faz sentido porque o process.py ja validou watertight + 1 ilha em todo
    master. Volume x densidade corporal da a MASSA - e massa/altura^2 da o IMC
    REAL do avatar, que e o teste direto de calibracao da grade.
    """
    import numpy as np
    a, b, c = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    return abs(float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum()) / 6.0)


class Mesh:
    """Malha achatada em arrays, com o mapa face->arestas pre-computado.

    O mapa existe para separar os lacos por topologia: duas arestas cortadas
    pertencem ao mesmo laco se compartilham uma face.
    """

    def __init__(self, verts, edges, face_edges, tris):
        import numpy as np
        self.verts = verts
        self.edges = edges
        self.face_edges = face_edges
        self.tris = tris
        fz = verts[:, 2][edges[face_edges, 0]]     # (F,3) z de um extremo de cada aresta
        gz = verts[:, 2][edges[face_edges, 1]]
        both = np.concatenate([fz, gz], axis=1)
        self.face_zmin = both.min(axis=1)
        self.face_zmax = both.max(axis=1)
        self._cache = {}   # as varreduras se sobrepoem; fatiar de novo e puro custo

    def loops(self, z):
        key = round(z, 5)
        if key not in self._cache:
            self._cache[key] = self._loops(z)
        return self._cache[key]

    def _loops(self, z):
        """Lacos fechados da interseccao com o plano Z=z. Lista de arrays (n,3)."""
        import numpy as np
        e = self.edges
        za, zb = self.verts[e[:, 0], 2], self.verts[e[:, 1], 2]
        cross = ((za - z) * (zb - z)) < 0
        if not cross.any():
            return []

        idx = np.flatnonzero(cross)
        slot = np.full(len(e), -1, dtype=int)
        slot[idx] = np.arange(len(idx))

        a, b = self.verts[e[idx, 0]], self.verts[e[idx, 1]]
        t = ((z - a[:, 2]) / (b[:, 2] - a[:, 2]))[:, None]
        pts = a + t * (b - a)

        parent = np.arange(len(idx))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        # so as faces que o plano atravessa
        cand = np.flatnonzero((self.face_zmin < z) & (self.face_zmax > z))
        for f in cand:
            ce = [s for s in slot[self.face_edges[f]] if s >= 0]
            for k in range(1, len(ce)):
                ri, rj = find(ce[0]), find(ce[k])
                if ri != rj:
                    parent[ri] = rj

        groups = {}
        for i in range(len(idx)):
            groups.setdefault(find(i), []).append(i)
        return [pts[g] for g in groups.values() if len(g) >= MIN_LOOP_PTS]


def measure_loop(loop, axis):
    """Perimetro do laco projetado no plano perpendicular a 'axis'."""
    import numpy as np
    centroid = loop.mean(axis=0)
    helper = np.array([1.0, 0.0, 0.0])
    if abs(float(axis @ helper)) > 0.9:
        helper = np.array([0.0, 1.0, 0.0])
    u = np.cross(axis, helper)
    u /= np.linalg.norm(u)
    w = np.cross(axis, u)
    local = loop - centroid
    return hull_perimeter_area(np.stack([local @ u, local @ w], axis=1))


def ranked_loops(mesh, z, axis_correct):
    """
    Lacos da fatia z, do maior para o menor POR AREA.

    Area e nao perimetro: o tronco tem area muito maior que um braco, enquanto
    os perimetros podem se aproximar num arquetipo musculoso.
    Retorna lista de (perimetro_m, area_m2, centroide).
    """
    import numpy as np

    loops = mesh.loops(z)
    if not loops:
        return []

    below = mesh.loops(z - SLICE_DELTA_M) if axis_correct else []
    above = mesh.loops(z + SLICE_DELTA_M) if axis_correct else []

    def nearest(groups, ref):
        best, bd = None, 1e9
        for g in groups:
            c = g.mean(axis=0)
            d = float(np.linalg.norm(c[:2] - ref[:2]))
            if d < bd:
                best, bd = c, d
        return best if bd < 0.12 else None

    out = []
    for lp in loops:
        centroid = lp.mean(axis=0)
        axis = np.array([0.0, 0.0, 1.0])
        if axis_correct:
            lo, hi = nearest(below, centroid), nearest(above, centroid)
            if lo is not None and hi is not None:
                v = hi - lo
                n = float(np.linalg.norm(v))
                # eixo quase horizontal = pareamento errado entre fatias; a
                # projecao colapsaria a secao. Melhor cair na vertical.
                if n > 1e-6 and abs(v[2] / n) >= MAX_AXIS_TILT:
                    axis = v / n
        per, area = measure_loop(lp, axis)
        out.append((per, area, centroid))

    out.sort(key=lambda t: -t[1])
    return out


def relevant(mesh, z, axis_correct=False):
    """Lacos da fatia sem dedos e ruido de malha, do maior para o menor por area."""
    r = ranked_loops(mesh, z, axis_correct)
    if not r:
        return []
    amax = r[0][1]
    return [t for t in r if t[1] >= REL_AREA_MIN * amax]


def find_armpit(mesh, base, height):
    """Maior z em que bracos e tronco ainda sao lacos separados.

    Acima disso o plano corta uma peca so e qualquer medida de tronco passa a
    incluir os bracos no casco convexo.
    """
    import numpy as np
    found = None
    for z in np.arange(base + 0.40 * height, base + 0.85 * height, SCAN_STEP_M):
        if len(relevant(mesh, float(z))) >= 3:
            found = float(z)
    return found


def find_crotch(mesh, base, height):
    """Menor z em que as duas pernas ja viraram um laco so (a pelve)."""
    import numpy as np
    for z in np.arange(base + 0.30 * height, base + 0.62 * height, SCAN_STEP_M):
        r = relevant(mesh, float(z))
        two_legs = len(r) >= 2 and r[0][1] < CROTCH_RATIO * r[1][1]
        if not two_legs:
            return float(z)
    return None


def torso_at(mesh, z):
    """Perimetro do laco do tronco (maior area) na altura z."""
    r = relevant(mesh, z)
    return r[0][0] if r else None


def torso_extreme(mesh, z0, z1, mode):
    """(perimetro, z) do tronco no ponto mais largo/estreito do intervalo."""
    import numpy as np
    best, best_z = None, None
    for z in np.arange(z0, z1, SCAN_STEP_M):
        p = torso_at(mesh, float(z))
        if p is None:
            continue
        if best is None or (p > best if mode == "max" else p < best):
            best, best_z = p, float(z)
    return best, best_z


def pair_at(mesh, z, skip_torso, axis_correct=True):
    """Media dos dois membros pareados na altura z. Retorna (media, esq, dir)."""
    r = relevant(mesh, z, axis_correct=axis_correct)
    if skip_torso:
        r = r[1:]
    if len(r) < 2:
        return None
    pair = sorted(r[:2], key=lambda t: t[2][0])    # por X: esquerda, direita
    a, b = pair[0][0], pair[1][0]
    return (a + b) / 2.0, a, b


def pair_extreme(mesh, z0, z1, skip_torso, mode):
    """(media, esq, dir, z) no ponto mais grosso/fino do intervalo."""
    import numpy as np
    best, best_z = None, None
    for z in np.arange(z0, z1, SCAN_STEP_M):
        got = pair_at(mesh, float(z), skip_torso, axis_correct=False)
        if got is None:
            continue
        if best is None or (got[0] > best[0] if mode == "max" else got[0] < best[0]):
            best, best_z = got, float(z)
    if best_z is None:
        return None
    # remede no z escolhido, agora corrigindo a inclinacao do membro
    final = pair_at(mesh, best_z, skip_torso, axis_correct=True) or best
    return final[0], final[1], final[2], best_z


# ==========================================================================
#  WORKER  (dentro do Blender)
# ==========================================================================

def load_mesh(path):
    import numpy as np

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(meshes) != 1:
        raise RuntimeError("esperado 1 malha, achou {}".format(len(meshes)))
    obj = meshes[0]
    me = obj.data

    mw = obj.matrix_world
    verts = np.array([(mw @ v.co)[:] for v in me.vertices], dtype=float)
    edges = np.array([e.vertices[:] for e in me.edges], dtype=int)

    lookup = {}
    for e in me.edges:
        lookup[tuple(sorted(e.vertices[:]))] = e.index
    face_edges, tris = [], []
    for p in me.polygons:
        if len(p.vertices) != 3:
            raise RuntimeError("malha nao triangulada (face com {} lados)".format(len(p.vertices)))
        face_edges.append([lookup[tuple(sorted(k))] for k in p.edge_keys])
        tris.append(p.vertices[:])
    return Mesh(verts, edges, np.array(face_edges, dtype=int), np.array(tris, dtype=int))


def worker_main():
    import numpy as np

    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--root", required=True)
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--csv", action="store_true")
    args = ap.parse_args(argv)

    out_dir = os.path.join(args.root, "metrics")
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "library_metrics.json")

    store = {"schema_version": 1, "canonical_height_m": CANONICAL_HEIGHT_M, "avatars": {}}
    if os.path.isfile(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                store = json.load(f)
            store.setdefault("avatars", {})
        except (ValueError, OSError):
            pass  # arquivo corrompido: recomeca em vez de travar a producao

    rows = []
    for aid in args.ids:
        try:
            mesh = load_mesh(os.path.join(args.root, "02_master", aid + "_master.glb"))
        except RuntimeError as exc:
            print("[SKIP] {}: {}".format(aid, exc))
            continue

        base = float(mesh.verts[:, 2].min())
        height = float(mesh.verts[:, 2].max() - base)
        volume = mesh_volume(mesh.verts, mesh.tris)
        mass = volume * BODY_DENSITY

        # ancoras esqueleticas (invariante do projeto)
        crotch = base + CROTCH_FRAC * height
        armpit = base + ARMPIT_FRAC * height
        span = armpit - crotch

        # deteccao = diagnostico: ate onde os membros estao de fato separados
        arm_split = find_armpit(mesh, base, height)
        leg_split = find_crotch(mesh, base, height)

        m = {}

        def band_edge(z, band):
            """'hi'/'lo' se o extremo escolhido encostou na borda da banda.

            Banda cujo maximo cai na borda nao achou o maximo: ela foi CORTADA
            antes dele. Foi assim que a panturrilha passou a producao inteira
            medindo o joelho - 50 dos 76 travados em 0,320 exato, e nenhuma
            trava olhava para isso porque todas olhavam so o centimetro.
            """
            if z is None or band is None:
                return None
            f = (z - base) / height
            if f <= (band[0] - base) / height + BAND_EDGE_TOL_FRAC:
                return "lo"
            if f >= (band[1] - base) / height - BAND_EDGE_TOL_FRAC:
                return "hi"
            return None

        def put(name, per, z, check_arms=True, band=None):
            """Registra a medida, marcando se os bracos estavam fundidos ao tronco.

            Acima de arm_split o casco convexo do tronco engloba os bracos e o
            numero fica inflado. Melhor entregar marcado do que limpo e errado.
            O pescoco e o ombro passam check_arms=False: no pescoco os bracos
            nem aparecem na fatia, e no ombro a fusao E a medida.
            """
            entry = {"cm": round(per * 100, 1) if per else None,
                     "at_frac": round((z - base) / height, 3) if z is not None else None}
            if per and z is not None and check_arms and arm_split is not None and z > arm_split:
                entry["arms_merged"] = True
            edge = band_edge(z, band) if per else None
            if edge:
                entry["at_band_edge"] = edge
            m[name] = entry

        # --- tronco -------------------------------------------------------
        neck_band = (base + NECK_BAND[0] * height, base + NECK_BAND[1] * height)
        put("neck", *torso_extreme(mesh, neck_band[0], neck_band[1], "min"),
            check_arms=False, band=neck_band)

        # Ombro: circunferencia na linha dos deltoides, ACIMA da axila de
        # proposito (ver SHOULDER_FRAC). Nao ha o que cortar pela fusao dos
        # bracos - a fusao e o que se quer medir.
        shoulder_z = base + SHOULDER_FRAC * height
        put("shoulder", torso_at(mesh, shoulder_z), shoulder_z, check_arms=False)

        # Peito na linha do mamilo. Se os bracos fundem abaixo disso, desce ate
        # logo abaixo da fusao - poucos cm de diferenca e um numero utilizavel,
        # em vez de um valor inflado pelos bracos.
        chest_z = base + CHEST_FRAC * height
        if arm_split is not None and arm_split < chest_z:
            # Aqui o numero deixa de ser peito e tende a barriga. Antes isso
            # saia limpo: o b12_d1 publicava 202,7 cm em 'chest' e em
            # 'waist_navel' - o MESMO z, sem nada avisando. Agora vai marcado.
            chest_z = arm_split - CHEST_PAD_M
            put("chest", torso_at(mesh, chest_z), chest_z)
            m["chest"]["below_band"] = True
        else:
            put("chest", torso_at(mesh, chest_z), chest_z)

        navel_z = base + NAVEL_FRAC * height
        put("waist_navel", torso_at(mesh, navel_z), navel_z)

        waist_band = (base + WAIST_BAND[0] * height, base + WAIST_BAND[1] * height)
        put("waist_min", *torso_extreme(mesh, waist_band[0], waist_band[1], "min"),
            band=waist_band)
        hip_band = (base + HIP_BAND[0] * height, base + HIP_BAND[1] * height)
        put("hip", *torso_extreme(mesh, hip_band[0], hip_band[1], "max"), band=hip_band)

        # --- membros ------------------------------------------------------
        def put_pair(name, got, band=None):
            if got is None:
                m[name] = {"cm": None, "at_frac": None}
                return
            avg, left, right, z = got
            m[name] = {"cm": round(avg * 100, 1), "left_cm": round(left * 100, 1),
                       "right_cm": round(right * 100, 1),
                       "at_frac": round((z - base) / height, 3)}
            edge = band_edge(z, band)
            if edge:
                m[name]["at_band_edge"] = edge

        # O braco so e mensuravel onde ainda e um laco proprio. Em corpo magro
        # isso vai ate a axila; em obeso o braco encosta antes e o teto cai.
        arm_top = (armpit if arm_split is None else min(armpit, arm_split)) - ARM_PAD_M
        wrist = pair_extreme(mesh, crotch, arm_top, True, "min")
        if wrist is None:
            put_pair("biceps", None)
            put_pair("forearm", None)
            put("wrist", None, None, check_arms=False)
        else:
            wrist_z = wrist[3]
            mid = (wrist_z + arm_top) / 2.0
            put_pair("forearm", pair_extreme(mesh, wrist_z, mid, True, "max"))
            put_pair("biceps", pair_extreme(mesh, mid, arm_top, True, "max"))
            put("wrist", wrist[0], wrist_z)

        # Coxa: so mensuravel abaixo de onde as coxas se tocam. Num obeso esse
        # teto fica bem abaixo da virilha e a medida deixa de ser "coxa".
        thigh_top = crotch if leg_split is None else min(crotch, leg_split)
        thigh_band = (thigh_top - THIGH_BAND_M, thigh_top - SCAN_STEP_M)
        # 'at_band_edge: hi' na coxa e ESPERADO e nao e defeito: a coxa e mais
        # larga colada na virilha, entao o maximo cai no teto por anatomia, nao
        # por corte. Na panturrilha o mesmo sinal significava o oposto.
        put_pair("thigh", pair_extreme(mesh, thigh_band[0], thigh_band[1], False, "max"),
                 band=thigh_band)
        calf_band = (base + CALF_BAND[0] * height, base + CALF_BAND[1] * height)
        put_pair("calf", pair_extreme(mesh, calf_band[0], calf_band[1], False, "max"),
                 band=calf_band)

        # A razao e o invariante: os masters tem altura fixa e o app escala por
        # altura do usuario. E a razao que se compara com uma pessoa real.
        ratios = {k: (round(v["cm"] / (height * 100), 4) if v.get("cm") else None)
                  for k, v in m.items()}

        store["avatars"][aid] = {
            "measured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "height_m": round(height, 5),
            # Ate onde os membros estao separados do corpo. Quanto MAIS BAIXO
            # que a ancora esqueletica (0,710 / 0,466), mais o arquetipo tem
            # contato de membro - e menos confiavel fica a medida de tronco.
            "arm_split_frac": round((arm_split - base) / height, 3) if arm_split else None,
            "leg_split_frac": round((leg_split - base) / height, 3) if leg_split else None,
            "volume_l": round(volume * 1000, 1),
            "est_mass_kg": round(mass, 1),
            "est_bmi": round(mass / (height ** 2), 1),
            "circumferences_cm": m,
            "ratios_to_height": ratios,
        }
        rows.append((aid, m))
        print("[OK] {}".format(aid))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)

    cols = COLUMNS
    print("\n{:<16}".format("avatar") + "".join("{:>11}".format(c) for c in cols))
    for aid, m in rows:
        line = "{:<16}".format(aid)
        for c in cols:
            v = m[c]["cm"]
            mark = "*" if m[c].get("arms_merged") else ""
            # '^'/'v': o extremo encostou na borda da banda. Na coxa e normal;
            # em qualquer outra coluna quer dizer que a banda cortou a medida.
            edge = m[c].get("at_band_edge")
            if edge and c != "thigh":
                mark += "^" if edge == "hi" else "v"
            if m[c].get("below_band"):
                mark += "!"
            line += "{:>11}".format("--" if v is None else "{:.1f}{}".format(v, mark))
        print(line)
    if any(e.get("arms_merged") for _, m in rows for e in m.values()):
        print("\n* medido acima da altura em que os bracos encostam no tronco:"
              "\n  o casco convexo engloba os bracos e o valor esta INFLADO.")
    edged = [(aid, c) for aid, m in rows for c in cols
             if c != "thigh" and m[c].get("at_band_edge")]
    if edged:
        print("\n^/v o extremo caiu na BORDA da banda em {} medida(s): a banda"
              "\n  cortou antes do pico, entao o numero nao e o que a coluna promete."
              .format(len(edged)))
        for aid, c in edged[:10]:
            print("    {} {}".format(aid, c))
    below = [(aid, c) for aid, m in rows for c in cols if m[c].get("below_band")]
    if below:
        print("\n! medido ABAIXO da banda (bracos fundem cedo demais): {} caso(s)."
              "\n  Nesses o 'peito' tende ao valor da barriga - nao comparar com os outros."
              .format(len(below)))
    print("\nJSON: {}".format(json_path))

    if args.csv:
        csv_path = os.path.join(out_dir, "library_metrics.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("avatar," + ",".join(cols) + "," +
                    ",".join(c + "_ratio" for c in cols) + "\n")
            for aid in sorted(store["avatars"]):
                a = store["avatars"][aid]
                cm = [a["circumferences_cm"].get(c, {}).get("cm") for c in cols]
                rt = [a["ratios_to_height"].get(c) for c in cols]
                f.write(aid + "," + ",".join("" if v is None else str(v) for v in cm + rt) + "\n")
        print("CSV : {}".format(csv_path))


# O guarda de __main__ existe para o metrics.py poder ser IMPORTADO como
# modulo (o morph.py calibra os shape keys contra a regua daqui, e regua
# reimplementada e regua que diverge). Sem ele, `import metrics` ja rodava o
# driver e saia com erro de argumento. Nada muda para quem executa o arquivo:
# tanto `python scripts/metrics.py` quanto `blender -b -P scripts/metrics.py`
# entram com __name__ == "__main__" (conferido nos dois).
if __name__ == "__main__":
    if IN_BLENDER and "--worker" in sys.argv:
        worker_main()
    elif not IN_BLENDER:
        driver_main()
