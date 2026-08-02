#!/usr/bin/env python3
"""
process.py - Pipeline de normalizacao da Zenith Avatar Library.

Le  01_raw/{id}_raw.glb
Gera 02_master/{id}_master.glb  (fonte de verdade, sem compressao)
     03_dist/glb/{id}_v1.glb     (distribuicao, Draco)

O trabalho e transformacao, nao reparo: os GLBs crus do Meshy (plano Pro)
chegam limpos (malha unica, watertight, 1 ilha, sem material). Este script
normaliza altura, aterra os pes, centraliza, decima, aplica o material Zenith
e valida antes de exportar.

USO
    python scripts/process.py zen_m_b05_d2
    python scripts/process.py zen_m_b05_d2 --tris 30000
    python scripts/process.py zen_m_b05_d2 --force
    python scripts/process.py --all

O Blender roda headless via subprocess. Se o executavel nao estiver no PATH,
aponte-o pela variavel de ambiente BLENDER (ver mensagem de erro).

Este arquivo se auto-reinvoca: quando chamado por 'python' roda em modo DRIVER
(parse de argumentos, localiza o Blender, aplica a regra nao-destrutiva e
dispara o subprocess). Quando chamado pelo Blender via '--python' roda em modo
WORKER (o pipeline bpy propriamente dito).
"""

import os
import sys
import glob
import argparse
import subprocess
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zenith_material as _zm                                       # noqa: E402
import zenith_paths as _zp                                          # noqa: E402

# ==========================================================================
# CONSTANTES  (ajustar aqui, nunca no meio do codigo)
# ==========================================================================

CANONICAL_HEIGHT_M = 1.75          # altura final identica para TODOS os avatares
TARGET_TRIS        = 60000         # alvo de triangulos pos-decimacao
TRIS_TOLERANCE     = 0.15          # +/- 15% em torno do alvo

# ⚠️ 60k, NAO 18k. Esta constante ficou em 18000 de 27/07 a 29/07 enquanto a
# regra 3 do CLAUDE.md ja dizia 60k e os 39 masters ja estavam em 60000 - eles
# foram reprocessados com --tris explicito e ninguem voltou aqui. O primeiro
# avatar feminino saiu em 17988 por causa disso, com 9/9 validacoes: as travas
# conferem o alvo CONTRA ELE MESMO, entao um alvo errado passa limpo.
#
# Por que 60k: em 18k, com o material titanio (claro e specular), a faceta da
# decimacao aparece e o relevo muscular borra. O roxo saturado anterior
# escondia isso. Custo medido: ~183 KB por avatar com Draco contra ~64 KB em
# 18k, dentro do orcamento de 1-3 MB. Ver README secao 4.

# O MATERIAL NAO MORA MAIS AQUI. Ele vive em scripts/zenith_material.py, que
# tambem alimenta o restyle.py - se cada script tivesse sua constante, um
# avatar novo sairia com cor diferente dos que ja existem e ninguem veria ate
# o app. Ler aquele arquivo antes de mexer em cor.
#
# 27/07/2026: o corpo deixou de ser roxo (#8346C6) e passou a ser titanio
# cinza. A identidade Zenith virou LUZ (rim roxo + azul frio) e mora fora do
# GLB, em 03_dist/env/zenith_env.hdr - ver scripts/make_env.py.

# Segmentacao do short por projecao da imagem frontal de referencia.
SHORTS_LUMA_MAX    = 90            # limiar de luminancia (0-255) na imagem: < => short
SHORTS_TRIS_MIN    = 0.02          # fracao minima esperada de triangulos no short
SHORTS_TRIS_MAX    = 0.25          # fracao maxima esperada de triangulos no short
# Faixa de altura (fracao da altura canonica) em que o short pode existir. A
# projecao frontal nao tem profundidade; este filtro impede que sombras escuras
# da frente (esterno/peitoral) marquem vertices das costas na mesma coluna X/Z.
# Generosa de proposito: arquetipos obesos deslocam a cintura.
SHORTS_Z_MIN       = 0.35          # fracao da altura canonica
SHORTS_Z_MAX       = 0.65

MERGE_DISTANCE_M   = 0.0001        # merge by distance (soldar vertices coincidentes)
NONMANIFOLD_WELD_M = 0.0005        # solda residual so nos vertices non-manifold (pincas de dedos)
MATERIAL_NAME        = _zm.MATERIAL_NAME          # slot 0 - corpo
SHORTS_MATERIAL_NAME = _zm.SHORTS_MATERIAL_NAME   # slot 1 - short

# Short: TEMPORARIAMENTE DESLIGADO (23/07). A segmentacao por projecao frontal
# deixa a borda serrilhada e nao ha regra universal que sirva para todos os
# corpos (a barriga pendente dos obesos quebra qualquer heuristica). Decisao:
# o corpo sai com material unico agora; o short sera feito por avatar, a mao no
# Blender, ao final da producao. Religar = True.
SHORTS_ENABLED     = False

# Tolerancias de validacao (metros; 1 unidade Blender == 1 metro)
HEIGHT_TOL_M       = 0.0005        # altura: +/- 0,5 mm
FLOOR_TOL_M        = 0.0005        # pe no chao (Y=0 no export): +/- 0,5 mm
CENTER_TOL_M       = 0.002         # centralizacao X/Z: +/- 2 mm

# Limiares de simetria - PROVISORIOS, calibrados sobre UMA amostra.
# A metrica e distancia PONTO-A-SUPERFICIE do vertice espelhado (ver
# symmetry_dev): a decimacao Collapse embaralha o pareamento vertice-a-vertice
# entre os lados, entao medir vertice-a-vertice superestimaria a assimetria
# (chegou a 31 mm de "falso" desvio). Ponto-a-superficie mede a forma real.
# No 1o avatar (zen_m_b05_d2) o master 18k mediu media ~0,4 mm / max ~5,7 mm.
# Revisar (provavelmente apertar) apos o piloto de 4.
SYM_MEAN_TOL_M     = 0.005         # desvio medio de simetria < 5 mm
SYM_MAX_TOL_M      = 0.020         # desvio maximo de simetria < 20 mm

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
        _die_driver(
            "A variavel de ambiente BLENDER aponta para um arquivo inexistente:\n"
            "  {}\n".format(env)
        )

    onpath = shutil.which("blender")
    if onpath:
        return onpath

    candidates = []
    # Windows
    for base in (
        r"C:\Program Files\Blender Foundation",
        r"C:\Program Files (x86)\Blender Foundation",
    ):
        candidates += glob.glob(os.path.join(base, "Blender *", "blender.exe"))
    # macOS
    candidates += glob.glob("/Applications/Blender*.app/Contents/MacOS/Blender")
    # Linux
    candidates += ["/usr/bin/blender", "/usr/local/bin/blender", "/snap/bin/blender"]

    existing = [c for c in candidates if os.path.isfile(c)]
    if existing:
        # maior versao pelo nome do caminho (ordenacao textual serve para "Blender 5.1")
        existing.sort()
        return existing[-1]

    _die_driver(
        "Blender nao encontrado.\n"
        "Aponte o executavel de uma destas formas:\n"
        '  Windows:  set BLENDER=\"C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe\"\n'
        "  macOS:    export BLENDER=/Applications/Blender.app/Contents/MacOS/Blender\n"
        "  Linux:    export BLENDER=/usr/bin/blender\n"
        "...ou adicione o Blender ao PATH."
    )


def _die_driver(msg, code=2):
    sys.stderr.write("\n[ERRO] " + msg + "\n")
    sys.exit(code)


def discover_ids(root):
    """IDs a partir de 01_raw/*_raw.glb."""
    raws = sorted(glob.glob(os.path.join(root, "01_raw", "*_raw.glb")))
    ids = []
    for p in raws:
        name = os.path.basename(p)
        if name.endswith("_raw.glb"):
            ids.append(name[: -len("_raw.glb")])
    return ids


def driver_main():
    parser = argparse.ArgumentParser(
        description="Normaliza avatares crus do Meshy para a Zenith Avatar Library."
    )
    parser.add_argument("id", nargs="?", help="ID do arquetipo, ex.: zen_m_b05_d2")
    parser.add_argument("--all", action="store_true", help="processa todos os *_raw.glb em 01_raw/")
    parser.add_argument("--tris", type=int, default=TARGET_TRIS,
                        help="alvo de triangulos (padrao {})".format(TARGET_TRIS))
    parser.add_argument("--force", action="store_true",
                        help="sobrescreve um master ja existente (exige QA de novo)")
    args = parser.parse_args()

    if bool(args.id) == bool(args.all):
        _die_driver("Informe UM id OU --all (nao ambos, nao nenhum).", code=2)

    root = repo_root()
    blender = find_blender()

    if args.all:
        ids = discover_ids(root)
        if not ids:
            _die_driver("Nenhum arquivo *_raw.glb encontrado em 01_raw/.", code=2)
    else:
        ids = [args.id]

    print("Blender: {}".format(blender))
    print("Repo   : {}".format(root))
    print("Alvo   : {} triangulos (+/- {:.0f}%)".format(args.tris, TRIS_TOLERANCE * 100))
    print("IDs    : {}".format(", ".join(ids)))
    print("-" * 70)

    failures = []
    for aid in ids:
        raw = os.path.join(root, "01_raw", aid + "_raw.glb")
        master = os.path.join(root, "02_master", aid + "_master.glb")

        if not os.path.isfile(raw):
            print("[SKIP] {}: nao existe {}".format(aid, os.path.relpath(raw, root)))
            failures.append(aid)
            continue

        # Regra 7 do CLAUDE.md: nao sobrescrever um master aprovado sem confirmacao.
        if os.path.isfile(master) and not args.force:
            print("[RECUSA] {}: {} ja existe.".format(aid, os.path.relpath(master, root)))
            print("         Refazer a normalizacao exige QA de novo. Use --force para sobrescrever.")
            failures.append(aid)
            continue

        print("\n==> processando {}".format(aid))
        cmd = [
            blender, "--background", "--python", os.path.abspath(__file__), "--",
            "--worker", "--id", aid, "--root", root, "--tris", str(args.tris),
        ]
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            print("[FALHA] {}: Blender/worker retornou {} (nao exportado).".format(aid, rc))
            failures.append(aid)
        else:
            print("[OK] {}".format(aid))

    print("-" * 70)
    if failures:
        print("Concluido com falhas: {}".format(", ".join(failures)))
        sys.exit(1)
    print("Concluido: {} avatar(es) processado(s) com sucesso.".format(len(ids)))
    sys.exit(0)


# ==========================================================================
#  WORKER  (dentro do Blender, bpy disponivel)
# ==========================================================================

def worker_main():
    import bmesh
    import traceback
    from mathutils import Vector, kdtree

    # --- argumentos apos o "--" ---
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    wp = argparse.ArgumentParser()
    wp.add_argument("--worker", action="store_true")
    wp.add_argument("--id", required=True)
    wp.add_argument("--root", required=True)
    wp.add_argument("--tris", type=int, default=TARGET_TRIS)
    a = wp.parse_args(argv)

    aid = a.id
    root = a.root
    target_tris = a.tris

    raw_path = os.path.join(root, "01_raw", aid + "_raw.glb")
    master_path = os.path.join(root, "02_master", aid + "_master.glb")
    # Versao NOVA, nunca por cima: o dist e URL de CDN (zenith_paths.py). Num
    # avatar inedito isso da v1; num reprocessamento, da a seguinte - e e ai
    # que importa, porque e o unico caso em que ja existe alguem com o arquivo
    # velho em cache.
    dist_version, dist_path = _zp.dist_glb_next(root, aid)
    log_path = os.path.join(root, "logs", "process.log")

    for d in (os.path.dirname(master_path), os.path.dirname(dist_path), os.path.dirname(log_path)):
        os.makedirs(d, exist_ok=True)

    def fail(msg, code=1):
        """Aborta sem exportar, registra o motivo e sai != 0."""
        print("\n[VALIDACAO/ERRO] {}".format(msg))
        _write_log(log_path, aid, result="FAIL", note=msg)
        sys.exit(code)

    # ---------------------------------------------------------------- helpers
    def mesh_world_verts(obj):
        mw = obj.matrix_world
        return [mw @ v.co for v in obj.data.vertices]

    def bbox(verts):
        xs = [p.x for p in verts]; ys = [p.y for p in verts]; zs = [p.z for p in verts]
        mn = Vector((min(xs), min(ys), min(zs)))
        mx = Vector((max(xs), max(ys), max(zs)))
        return mn, mx, (mn + mx) * 0.5, (mx - mn)

    def tri_count(obj):
        me = obj.data
        me.calc_loop_triangles()
        return len(me.loop_triangles)

    def bmesh_stats(obj):
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        boundary = sum(1 for e in bm.edges if e.is_boundary)
        nonman = sum(1 for e in bm.edges if len(e.link_faces) > 2)
        # ilhas: flood fill por faces vizinhas
        visited = set(); islands = 0
        for f in bm.faces:
            if f.index in visited:
                continue
            islands += 1
            stack = [f]; visited.add(f.index)
            while stack:
                cf = stack.pop()
                for e in cf.edges:
                    for nf in e.link_faces:
                        if nf.index not in visited:
                            visited.add(nf.index); stack.append(nf)
        bm.free()
        return boundary, nonman, islands

    def symmetry_dev(obj, verts, x_center):
        """Simetria por distancia PONTO-A-SUPERFICIE: espelha cada vertice no
        plano X=x_center e mede a distancia ate a superficie da propria malha
        (via BVH). Isso mede a assimetria real da forma, e nao o pareamento de
        vertices, que a decimacao Collapse embaralha entre os lados."""
        from mathutils.bvhtree import BVHTree
        polys = [tuple(p.vertices) for p in obj.data.polygons]
        vlist = [tuple(v) for v in verts]
        bvh = BVHTree.FromPolygons(vlist, polys)
        step = max(1, len(verts) // 60000)   # amostragem em malhas grandes
        devs = []
        for i in range(0, len(verts), step):
            p = verts[i].copy()
            p.x = 2.0 * x_center - p.x
            loc, nrm, idx, d = bvh.find_nearest(p)
            if d is not None:
                devs.append(d)
        return (sum(devs) / len(devs)), max(devs), len(devs)

    # Material: zenith_material.py e a fonte unica (compartilhada com o
    # restyle.py). Os valores e o porque deles estao documentados la.

    def assign_materials(obj, ref_path):
        """Atribui DOIS materiais (corpo roxo + short preto) segmentando o short
        pela projecao da imagem frontal de referencia sobre a malha ja normalizada.
        O GLB do Meshy vem sem UV e sem material: a unica fonte da posicao do short
        e a imagem que gerou a malha, entao as proporcoes batem.

        Precondicao: ref_path existe (o chamador aborta se faltar). Retorna a
        fracao de triangulos atribuida ao short."""
        me = obj.data
        me.materials.clear()
        body = _zm.make_body_material(bpy)

        import numpy as np

        # --- carregar imagem e ler os pixels como estao (sem gestao de cor) ---
        img = bpy.data.images.load(ref_path, check_existing=False)
        w, h = img.size
        try:
            img.colorspace_settings.name = "Non-Color"   # valores sRGB crus 0..1
        except Exception:
            pass
        buf = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(buf)
        # Blender guarda de baixo p/ cima: inverter para linha 0 = TOPO da imagem.
        px = buf.reshape(h, w, 4)[::-1]
        rgb = px[:, :, :3] * 255.0
        luma = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
        bpy.data.images.remove(img)

        # --- fundo = mediana das bordas; figura = distancia ao fundo > 18 ---
        border = np.concatenate(
            [rgb[0, :, :], rgb[-1, :, :], rgb[:, 0, :], rgb[:, -1, :]], axis=0)
        bg = np.median(border, axis=0)
        dist = np.abs(rgb - bg).sum(axis=2)               # soma dos canais (0-765)
        figure = dist > 18.0
        ys, xs = np.where(figure)
        if xs.size == 0:
            fail("figura nao detectada em {}: a imagem de referencia parece "
                 "vazia/uniforme. Verifique o recorte.".format(os.path.basename(ref_path)))
        x0, x1 = int(xs.min()), int(xs.max())
        y0, y1 = int(ys.min()), int(ys.max())
        bw = max(1, x1 - x0)
        bh = max(1, y1 - y0)

        # --- projetar cada vertice da malha normalizada para um pixel ---
        n = len(me.vertices)
        co = np.empty(n * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        co = co.reshape(n, 3)
        vx = co[:, 0]
        vz = co[:, 2]                                     # altura (pes=0, topo=CANONICAL)
        xmin = float(vx.min())
        xmax = float(vx.max())
        u = x0 + (vx - xmin) / (xmax - xmin) * bw
        v = y0 + (1.0 - vz / CANONICAL_HEIGHT_M) * bh     # eixo Y da imagem cresce p/ baixo
        ui = np.clip(np.round(u).astype(np.int64), 0, w - 1)
        vi = np.clip(np.round(v).astype(np.int64), 0, h - 1)
        # Vertice e short se o pixel for escuro E a altura estiver na faixa
        # plausivel do short (a projecao frontal nao distingue frente/costas;
        # a faixa-Z barra sombras da frente marcando vertices das costas).
        z_lo = SHORTS_Z_MIN * CANONICAL_HEIGHT_M
        z_hi = SHORTS_Z_MAX * CANONICAL_HEIGHT_M
        vert_short = (luma[vi, ui] < SHORTS_LUMA_MAX) & (vz >= z_lo) & (vz <= z_hi)

        # --- face e short se a MAIORIA dos seus vertices for short ---
        nf = len(me.polygons)
        face_short = [False] * nf
        for poly in me.polygons:
            vs = poly.vertices
            s = sum(1 for vidx in vs if vert_short[vidx])
            face_short[poly.index] = (2 * s > len(vs))

        # --- limpeza final da fronteira: 2 passadas de maioria por vizinhanca
        #     de faces (remove faces isoladas que sobraram apos a suavizacao). ---
        bm = bmesh.new()
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        for _ in range(2):
            updated = list(face_short)
            for f in bm.faces:
                neigh = [nfc.index for e in f.edges for nfc in e.link_faces
                         if nfc.index != f.index]
                if not neigh:
                    continue
                sc = sum(1 for k in neigh if face_short[k])
                if 2 * sc > len(neigh):
                    updated[f.index] = True
                elif 2 * sc < len(neigh):
                    updated[f.index] = False
            face_short = updated
        bm.free()

        # --- criar e atribuir os dois materiais ---
        me.materials.append(body)                         # slot 0 - corpo
        me.materials.append(_zm.make_shorts_material(bpy))            # slot 1
        idx = np.where(np.array(face_short, dtype=bool), 1, 0).astype(np.int32)
        me.polygons.foreach_set("material_index", idx)
        me.update()

        return float(np.count_nonzero(idx)) / nf

    # ---------------------------------------------------------------- pipeline
    try:
        print("=" * 70)
        print("WORKER  id={}  target_tris={}".format(aid, target_tris))
        print("raw : {}".format(raw_path))

        # 1. cena vazia + import
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if not os.path.isfile(raw_path):
            fail("arquivo cru nao encontrado: {}".format(raw_path))
        bpy.ops.import_scene.gltf(filepath=raw_path)

        # 2. defensivo
        meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
        if armatures:
            fail("o GLB contem armature ({}). O pipeline nao rigga avatares; "
                 "gere sem esqueleto.".format(", ".join(o.name for o in armatures)))
        if not meshes:
            fail("nenhuma malha no GLB.")
        if len(meshes) > 1:
            print("aviso: {} malhas encontradas -> juntando em uma.".format(len(meshes)))
            bpy.ops.object.select_all(action="DESELECT")
            for m in meshes:
                m.select_set(True)
            bpy.context.view_layer.objects.active = meshes[0]
            bpy.ops.object.join()
        obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # 3. merge by distance + recalcular normais para fora
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=MERGE_DISTANCE_M)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")

        # 4. medir estado cru
        raw_tris = tri_count(obj)
        raw_verts = len(obj.data.vertices)
        _, _, _, raw_dim = bbox(mesh_world_verts(obj))
        raw_height = raw_dim.z   # apos import glTF, a altura e Z (Y-up -> Z-up)
        print("cru : tris={}  verts={}  bbox=({:.4f}, {:.4f}, {:.4f})".format(
            raw_tris, raw_verts, raw_dim.x, raw_dim.y, raw_dim.z))

        # 5. aplicar transformacoes de import
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # 6. DECIMAR primeiro (Collapse, com simetria em X) sobre a contagem REAL
        #    de faces. Ordem deliberada: a decimacao Collapse perturba a bounding
        #    box (empurra o Zmin) e quebra a simetria L/R (colapsa arestas de forma
        #    independente nos dois lados). Se normalizassemos ANTES de decimar, os
        #    pes sairiam do chao e a altura escaparia da tolerancia de 0,5 mm. Por
        #    isso a normalizacao (altura/pes/centro) e a ULTIMA etapa geometrica.
        #    use_symmetry='X' decima espelhado e preserva a simetria do avatar.
        cur_tris = tri_count(obj)
        if cur_tris > target_tris:
            ratio = target_tris / float(cur_tris)
            mod = obj.modifiers.new(name="decimate", type="DECIMATE")
            mod.decimate_type = "COLLAPSE"
            mod.ratio = ratio
            mod.use_symmetry = True
            mod.symmetry_axis = "X"
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)
        else:
            ratio = 1.0
            print("aviso: malha ja abaixo do alvo ({} <= {}); decimacao ignorada.".format(
                cur_tris, target_tris))

        # 7. cicatrizar micro-defeitos que o colapso possa ter aberto (vertices
        #    coincidentes, arestas degeneradas, micro-furos). NAO e reparo do
        #    fonte: e limpar o que a propria decimacao gerou, para devolver a
        #    malha ao estado fechado.
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=MERGE_DISTANCE_M)
        bpy.ops.mesh.dissolve_degenerate(threshold=1e-5)   # arestas/faces de area ~0
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_non_manifold()                 # so o que ficou aberto
        bpy.ops.mesh.fill_holes(sides=0)
        # cicatrizar pincas non-manifold residuais: arestas com 3+ faces nas
        # extremidades fundidas (dedos) que a decimacao simetrica belisca. Nao
        # sao furos, entao fill_holes nao resolve. Soldar SO os vertices
        # non-manifold, com folga maior, corrige localmente sem tocar a mao.
        # threshold escalonado: as 3 primeiras passadas na folga padrao (pincas
        # de dedos); se ainda sobrar non-manifold (dobras de 4 faces que a
        # decimacao funde onde duas superficies quase se tocam - ex.: mao na coxa
        # nos corpos obesos extremos), escala ate 2mm. So age em vertices
        # non-manifold selecionados -> em malha ja limpa e no-op.
        for thr in (NONMANIFOLD_WELD_M, NONMANIFOLD_WELD_M, NONMANIFOLD_WELD_M,
                    0.001, 0.002):
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.mesh.select_non_manifold()
            bpy.ops.mesh.remove_doubles(threshold=thr)
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")

        out_tris = tri_count(obj)
        decim_ratio = out_tris / float(raw_tris) if raw_tris else 0.0
        print("dec : {} -> {} tris  (razao {:.4f})".format(raw_tris, out_tris, decim_ratio))

        # 8. escala UNIFORME para altura canonica (Z). Nunca eixo isolado.
        #    A diferenca entre arquetipos e largura/volume, nunca altura.
        #    Assar a escala ANTES de medir a translacao: assim mesh_world_verts
        #    le coordenadas ja escaladas (matriz identidade) e nao depende de um
        #    matrix_world que fica obsoleto ao atribuir obj.scale em headless.
        _, _, _, dim = bbox(mesh_world_verts(obj))
        if dim.z <= 1e-9:
            fail("altura degenerada (Z ~ 0).")
        scale_factor = CANONICAL_HEIGHT_M / dim.z
        obj.scale = (scale_factor, scale_factor, scale_factor)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # 9. transladar: Z minimo = 0 (pes no chao); centralizar X e Y pela bbox
        #    ja escalada (co assado, matrix_world = identidade -> leitura confiavel).
        mn, mx, ctr, _ = bbox(mesh_world_verts(obj))
        dx, dy, dz = -ctr.x, -ctr.y, -mn.z
        obj.location = (dx, dy, dz)
        translation = (dx, dy, dz)

        # 10. aplicar a translacao: geometria final congelada aqui
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

        # 11. material Zenith. Com SHORTS_ENABLED, separa o short preto do corpo
        #     roxo por projecao da imagem frontal (referencia obrigatoria). Sem
        #     ele (padrao atual), o corpo sai TODO ROXO num unico material e o
        #     short fica para a etapa manual no Blender ao final.
        if SHORTS_ENABLED:
            ref_front = _zp.ref_path(root, aid, "front")
            if not os.path.isfile(ref_front):
                fail("referencia frontal obrigatoria ausente: {}. Ela vem do "
                     "recorte e separa o short do corpo. Coloque a imagem em "
                     "00_input/references/ e reprocess.".format(
                         os.path.relpath(ref_front, root)))
            shorts_frac = assign_materials(obj, ref_front)
            print("materiais: corpo={} + short={}  (fracao short = {:.4f})".format(
                MATERIAL_NAME, SHORTS_MATERIAL_NAME, shorts_frac))
        else:
            me = obj.data
            me.materials.clear()
            me.materials.append(_zm.make_body_material(bpy))
            for p in me.polygons:
                p.material_index = 0
            me.update()
            shorts_frac = 0.0
            # "roxo" saiu do texto em 29/07: o corpo e titanio cinza desde
            # 27/07 e o log dizia o contrario, o que atrapalha quem confere.
            print("materiais: corpo={} (titanio, peca unica; short e aplicado "
                  "depois pelo shorts.py)".format(MATERIAL_NAME))

        # 11. VALIDAR (tudo antes de exportar; export glTF e apenas rotacao de
        #     eixos Z-up->Y-up, entao estas metricas valem para o GLB exportado:
        #     Blender Z (altura) -> glTF Y ; Blender Y -> glTF Z).
        verts = mesh_world_verts(obj)
        mn, mx, ctr, dim = bbox(verts)
        boundary, nonman, islands = bmesh_stats(obj)
        sym_mean, sym_max, sym_n = symmetry_dev(obj, verts, ctr.x)

        lo = target_tris * (1 - TRIS_TOLERANCE)
        hi = target_tris * (1 + TRIS_TOLERANCE)

        checks = []  # (nome, passou, detalhe)
        checks.append(("tris", lo <= out_tris <= hi,
                       "{} (faixa {:.0f}-{:.0f})".format(out_tris, lo, hi)))
        checks.append(("height", abs(dim.z - CANONICAL_HEIGHT_M) <= HEIGHT_TOL_M,
                       "{:.5f} m (alvo {:.5f})".format(dim.z, CANONICAL_HEIGHT_M)))
        checks.append(("floor_Y0", abs(mn.z) <= FLOOR_TOL_M,
                       "Zmin={:.5f} m".format(mn.z)))
        checks.append(("center_XZ", abs(ctr.x) <= CENTER_TOL_M and abs(ctr.y) <= CENTER_TOL_M,
                       "Xc={:.5f} Zexp={:.5f} m".format(ctr.x, ctr.y)))
        checks.append(("watertight", boundary == 0 and nonman == 0,
                       "borda={} nonmanifold={}".format(boundary, nonman)))
        checks.append(("islands", islands == 1, "ilhas={}".format(islands)))
        checks.append(("symmetry", sym_mean < SYM_MEAN_TOL_M and sym_max < SYM_MAX_TOL_M,
                       "media={:.5f} max={:.5f} m (n={})".format(sym_mean, sym_max, sym_n)))
        mats = obj.data.materials
        names = [m.name for m in mats]
        if SHORTS_ENABLED:
            # exatamente 2 materiais nomeados, na ordem certa.
            checks.append(("materials",
                           len(mats) == 2 and names[0] == MATERIAL_NAME
                           and names[1] == SHORTS_MATERIAL_NAME,
                           "n={} {}".format(len(mats), names)))
            # fracao de triangulos do short dentro da faixa esperada.
            checks.append(("shorts_frac",
                           SHORTS_TRIS_MIN <= shorts_frac <= SHORTS_TRIS_MAX,
                           "{:.4f} (faixa {:.2f}-{:.2f})".format(
                               shorts_frac, SHORTS_TRIS_MIN, SHORTS_TRIS_MAX)))
        else:
            # corpo todo roxo: um unico material.
            checks.append(("materials",
                           len(mats) == 1 and names[0] == MATERIAL_NAME,
                           "n={} {}".format(len(mats), names)))

        print("\nvalidacoes:")
        for name, ok, detail in checks:
            print("  [{}] {:<12} {}".format("PASS" if ok else "FALHA", name, detail))

        val_summary = ";".join("{}={}".format(n, "PASS" if ok else "FAIL") for n, ok, _ in checks)

        if not all(ok for _, ok, _ in checks):
            failed = [n for n, ok, _ in checks if not ok]
            _write_log(log_path, aid, raw_tris=raw_tris, out_tris=out_tris,
                       decim_ratio=decim_ratio, raw_height=raw_height,
                       scale_factor=scale_factor, translation=translation,
                       shorts_frac=shorts_frac,
                       val_summary=val_summary, result="FAIL",
                       note="validacoes falharam: " + ",".join(failed))
            print("\n[FALHA] validacoes reprovadas: {}. Nada exportado.".format(", ".join(failed)))
            sys.exit(1)

        # 12. export master (sem compressao)
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Sombreamento suave: interpola as normais entre faces vizinhas. Sem
        # isso o glTF pode sair com aparencia facetada. Corpo organico -> tudo
        # suave (nao ha arestas vivas a preservar; a barra do short e limite de
        # material, nao de geometria).
        bpy.ops.object.shade_smooth()

        bpy.ops.export_scene.gltf(
            filepath=master_path, export_format="GLB", use_selection=True,
            export_draco_mesh_compression_enable=False,
        )
        # 13. export dist (Draco). Quantizacao de normal alta (14 bits) para nao
        #     reintroduzir facetamento: o default de 10 bits arredonda as normais
        #     e volta a parecer quadriculado no model-viewer.
        bpy.ops.export_scene.gltf(
            filepath=dist_path, export_format="GLB", use_selection=True,
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14,
            export_draco_normal_quantization=14,
        )

        gone = _zp.dist_glb_retire(root, aid, keep=dist_version)

        print("\nmaster: {}".format(master_path))
        print("dist  : {}{}".format(
            dist_path,
            "   (aposentou {})".format(", ".join(gone)) if gone else ""))

        # 14. log
        _write_log(log_path, aid, raw_tris=raw_tris, out_tris=out_tris,
                   decim_ratio=decim_ratio, raw_height=raw_height,
                   scale_factor=scale_factor, translation=translation,
                   shorts_frac=shorts_frac,
                   val_summary=val_summary, result="PASS",
                   master=master_path, dist=dist_path)

        print("[PASS] {}".format(aid))
        sys.exit(0)

    except SystemExit:
        raise
    except Exception as exc:  # qualquer erro inesperado: nao exporta, sai != 0
        traceback.print_exc()
        _write_log(log_path, aid, result="ERROR", note=repr(exc))
        sys.exit(1)


def _write_log(log_path, aid, raw_tris=None, out_tris=None, decim_ratio=None,
               raw_height=None, scale_factor=None, translation=None,
               val_summary=None, result="?", note=None, master=None, dist=None,
               shorts_frac=None):
    """Uma linha por execucao em logs/process.log."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tr = ("({:.5f},{:.5f},{:.5f})".format(*translation)) if translation else "-"
    fields = [
        ts,
        "id=" + aid,
        "result=" + result,
        "tris_raw={}".format(raw_tris if raw_tris is not None else "-"),
        "tris_out={}".format(out_tris if out_tris is not None else "-"),
        "decim_ratio={}".format("{:.4f}".format(decim_ratio) if decim_ratio is not None else "-"),
        "raw_height_m={}".format("{:.5f}".format(raw_height) if raw_height is not None else "-"),
        "scale={}".format("{:.5f}".format(scale_factor) if scale_factor is not None else "-"),
        "translate=" + tr,
        "shorts_frac={}".format("{:.4f}".format(shorts_frac) if shorts_frac is not None else "-"),
        "valid=[{}]".format(val_summary if val_summary else "-"),
        "master={}".format(master if master else "-"),
        "dist={}".format(dist if dist else "-"),
    ]
    if note:
        fields.append("note=" + note.replace("\n", " "))
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(" | ".join(fields) + "\n")
    except OSError:
        pass  # log nunca deve derrubar o pipeline


# ==========================================================================
#  ENTRYPOINT
# ==========================================================================
if __name__ == "__main__":
    if IN_BLENDER and "--worker" in sys.argv:
        worker_main()
    elif not IN_BLENDER:
        driver_main()
    # (Blender sem --worker: script carregado mas nao dispara nada.)
