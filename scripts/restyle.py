#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
restyle.py - troca o MATERIAL dos avatares ja produzidos, sem re-processar.

    python scripts/restyle.py --all              # regrava os 39 dist
    python scripts/restyle.py zen_m_b05_d2       # um so
    python scripts/restyle.py --preview zen_m_b05_d2   # render de conferencia

--------------------------------------------------------------------------
PORQUE ESTE SCRIPT EXISTE, EM VEZ DE RODAR process.py DE NOVO
--------------------------------------------------------------------------
Material e assunto de DISTRIBUICAO, nao de normalizacao. Rodar process.py
para trocar uma cor significaria:

  - re-decimar 39 malhas (a decimacao Collapse nao e deterministica entre
    execucoes: a topologia sairia diferente da que passou no QA), e
  - sobrescrever 02_master/, que a regra 7 do CLAUDE.md proibe sem
    confirmacao, justamente porque exigiria refazer o QA humano.

Este script LE os masters e reescreve apenas 03_dist/glb/. A geometria
aprovada nao e tocada - o unico dado que muda no arquivo e o material. Por
isso uma rodada de ajuste de cor custa minutos e e reversivel.

E so METADE do visual. A outra metade e a iluminacao, que nao cabe no GLB:
ver scripts/make_env.py.

Validacao: a contagem de triangulos do dist tem que bater com a do master.
Se divergir, o export mexeu na malha e o dist nao serve.
"""

import argparse
import glob
import json
import os
import sys

# ============================================================================
# DRIVER (Python do sistema) - descobre o Blender e o chama por avatar.
# ============================================================================

BG_HEX = "#0D0D12"      # fundo do app, usado so na composicao do preview


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _die(msg, code=2):
    sys.stderr.write("\n[ERRO] " + msg + "\n")
    sys.exit(code)


def find_blender():
    """Mesma ordem de busca do process.py: env BLENDER -> PATH -> instalacoes."""
    import shutil

    env = os.environ.get("BLENDER")
    if env:
        if os.path.isfile(env):
            return env
        _die("A variavel BLENDER aponta para arquivo inexistente:\n  {}".format(env))

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

    _die("Blender nao encontrado. Defina a variavel BLENDER apontando para o executavel.")


def discover_ids(root):
    out = []
    for p in sorted(glob.glob(os.path.join(root, "02_master", "*_master.glb"))):
        name = os.path.basename(p)
        out.append(name[: -len("_master.glb")])
    return out


def composite_previews(paths, bg_hex):
    """Renders saem com fundo transparente; compoe sobre o fundo do app para
    a conferencia ser feita na condicao real de exibicao."""
    from PIL import Image

    bg = tuple(int(bg_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    for p in paths:
        im = Image.open(p).convert("RGBA")
        flat = Image.new("RGBA", im.size, bg)
        flat.alpha_composite(im)
        flat.convert("RGB").save(p)


def _ids_com_short(root):
    """Ids que tem peca pintada no config/shorts_map.json.

    Fonte unica de quem 'esta vestido' - o dist nao serve para responder isso,
    porque um dist sem short pode ser justamente o que este script apagou."""
    p = os.path.join(root, "config", "shorts_map.json")
    if not os.path.isfile(p):
        return set()
    with open(p, "r", encoding="utf-8") as f:
        return set(json.load(f).keys())


def driver_main():
    ap = argparse.ArgumentParser(
        description="Aplica o material Zenith atual sobre os masters, regravando 03_dist/glb/.")
    ap.add_argument("id", nargs="?", help="ID do avatar, ex.: zen_m_b05_d2")
    ap.add_argument("--all", action="store_true", help="todos os masters de 02_master/")
    ap.add_argument("--preview", metavar="ID",
                    help="renderiza o avatar com o ambiente Zenith em qa/look/{id}/ "
                         "(nao regrava o dist)")
    args = ap.parse_args()

    root = repo_root()
    blender = find_blender()

    if args.preview:
        ids, mode = [args.preview], "preview"
    elif args.all and not args.id:
        ids, mode = discover_ids(root), "restyle"
        if not ids:
            _die("Nenhum *_master.glb em 02_master/.")
    elif args.id and not args.all:
        ids, mode = [args.id], "restyle"
    else:
        _die("Informe UM id, OU --all, OU --preview ID.")

    sys.path.insert(0, os.path.join(root, "scripts"))
    import zenith_material as zm
    import zenith_paths as zp

    print("Blender : {}".format(blender))
    print("Modo    : {}".format(mode))
    print("Material: base {} | metallic {} | roughness {}".format(
        zm.ZENITH_BASE_HEX, zm.ZENITH_METALLIC, zm.ZENITH_ROUGHNESS))
    print("IDs     : {}".format(", ".join(ids)))
    print("-" * 70)

    dressed = _ids_com_short(root)

    failures = []
    skipped_dressed = []
    for aid in ids:
        master = os.path.join(root, "02_master", aid + "_master.glb")
        if not os.path.isfile(master):
            print("[SKIP] {}: nao existe {}".format(aid, os.path.relpath(master, root)))
            failures.append(aid)
            continue

        # 🔴 O RESTYLE APAGAVA O SHORT, e em silencio. Ele le o MASTER, que nao
        # tem peca pintada, e regrava o dist; o shorts.py le o master MAIS o
        # mapa e regrava o MESMO arquivo. Quem roda por ultimo vence - e em
        # 31/07 o `--all` venceu e zerou os 39 shorts masculinos de uma vez,
        # sem um aviso sequer (medido: os 76 dist estavam com 1 material).
        #
        # Recusar, e nao reaplicar sozinho: reaplicar em lote poria o DETECTOR
        # no caminho do material, e o mapa existe justamente porque o detector
        # erra (CLAUDE.md regra 3b - o mapa e o produto). O shorts.py --apply
        # ja aplica o material corrente junto do short, entao ele nao e um
        # remendo: e o comando completo para quem tem peca.
        if mode == "restyle" and aid in dressed:
            skipped_dressed.append(aid)
            continue

        cmd = [blender, "--background", "--python", os.path.abspath(__file__), "--",
               "--worker", "--mode", mode, "--id", aid, "--root", root]
        import subprocess
        proc = None
        if mode == "restyle":
            proc = subprocess.run(cmd, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True)
            rc = proc.returncode
        else:
            rc = subprocess.call(cmd)
        if rc != 0:
            print("[FAIL] {} (codigo {})".format(aid, rc))
            # LICOES 4.2d: a mensagem do worker JA EXISTIA e era descartada
            # aqui - 76 falhas apareceram como "codigo 1" e custaram uma sessao
            # de diagnostico. Trava que detecta e nao conta o porque nao serve.
            for line in ((proc.stdout or "").strip().splitlines()[-6:] if proc else []):
                print("       | " + line)
            failures.append(aid)
        else:
            # a versao vem do DISCO, nao do que o worker disse ter feito
            v, _ = zp.dist_glb_current(root, aid)
            print("[ok]   {}  -> v{}".format(aid, v))

    if mode == "preview":
        look = os.path.join(root, "qa", "look", ids[0])
        pngs = sorted(glob.glob(os.path.join(look, "*.png")))
        if pngs:
            composite_previews(pngs, BG_HEX)
            print("\npreview: {} ({} imagens, compostas sobre {})".format(
                os.path.relpath(look, root), len(pngs), BG_HEX))

    print("-" * 70)
    feitos = len(ids) - len(failures) - len(skipped_dressed)
    print("{}/{} ok".format(feitos, len(ids) - len(skipped_dressed)))
    if skipped_dressed:
        print("\n[NAO TOCADOS] {} avatar(es) tem peca pintada, e o restyle apagaria "
              "o short.\nO shorts.py aplica o material corrente JUNTO do short - "
              "rode nestes:".format(len(skipped_dressed)))
        for aid in skipped_dressed:
            print("  python scripts/shorts.py --apply {}".format(aid))
    if failures:
        print("falharam: {}".format(", ".join(failures)))
        return 1
    return 0


# ============================================================================
# WORKER (Python do Blender)
# ============================================================================

def worker_main():
    import bpy
    from mathutils import Vector

    argv = sys.argv[sys.argv.index("--") + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--mode", required=True, choices=["restyle", "preview"])
    ap.add_argument("--id", required=True)
    ap.add_argument("--root", required=True)
    a = ap.parse_args(argv)

    sys.path.insert(0, os.path.join(a.root, "scripts"))
    import zenith_material as zm
    import zenith_paths as zp

    master = os.path.join(a.root, "02_master", a.id + "_master.glb")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=master)

    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(meshes) != 1:
        sys.stderr.write("esperava 1 malha no master, achei {}\n".format(len(meshes)))
        sys.exit(1)
    obj = meshes[0]

    obj.data.materials.clear()
    # clear() esvazia o SLOT do objeto, mas NAO apaga o datablock que veio do
    # master - ele fica em bpy.data.materials com 0 usuarios, ainda ocupando o
    # nome "Zenith_Body". O material novo entao nasce como "Zenith_Body.001" e a
    # trava de nome la embaixo derruba o avatar inteiro.
    #
    # Nao aparecia antes porque na fase roxa o master trazia "Zenith_Purple":
    # nome diferente, sem colisao. Quando os masters passaram a ter
    # "Zenith_Body", o restyle passou a colidir COM ELE MESMO - e o efeito so
    # apareceu em 31/07, ao mudar a cor, com 0/76 avatares processados.
    for m in list(bpy.data.materials):
        if m.users == 0:
            bpy.data.materials.remove(m)
    obj.data.materials.append(zm.make_body_material(bpy))
    for p in obj.data.polygons:
        p.material_index = 0

    if a.mode == "restyle":
        tris_before = sum(len(p.vertices) - 2 for p in obj.data.polygons)

        # Versao NOVA, nunca por cima: o dist e URL de CDN (zenith_paths.py).
        version, dist = zp.dist_glb_next(a.root, a.id)

        def reject(msg):
            """Desfaz o arquivo novo e deixa a versao anterior servindo."""
            if os.path.isfile(dist):
                os.remove(dist)
            sys.stderr.write(msg)
            sys.exit(1)

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        # Mesmos parametros de Draco do process.py. Quantizacao de normal em 14
        # bits: o default de 10 arredonda as normais e devolve o facetamento.
        bpy.ops.export_scene.gltf(
            filepath=dist, export_format="GLB", use_selection=True,
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14,
            export_draco_normal_quantization=14,
        )

        # Confere que so o material mudou: a malha exportada tem que ter a
        # mesma contagem de triangulos do master.
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=dist)
        back = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        tris_after = sum(len(p.vertices) - 2 for o in back for p in o.data.polygons)
        if tris_after != tris_before:
            reject("geometria mudou no export: {} -> {} triangulos\n".format(
                tris_before, tris_after))
        names = [m.name for m in back[0].data.materials]
        if names != [zm.MATERIAL_NAME]:
            reject("materiais inesperados no dist: {}\n".format(names))

        gone = zp.dist_glb_retire(a.root, a.id, keep=version)
        print("{}: {} tri, material {}, v{}{}".format(
            a.id, tris_after, zm.MATERIAL_NAME, version,
            " (aposentou {})".format(", ".join(gone)) if gone else ""))
        sys.exit(0)

    # ---------------------------------------------------------------- preview
    env = os.path.join(a.root, "03_dist", "env", "zenith_env.hdr")
    if not os.path.isfile(env):
        sys.stderr.write("ambiente nao encontrado: {}\nRode scripts/make_env.py.\n".format(env))
        sys.exit(1)

    scene = bpy.context.scene
    world = bpy.data.worlds.new("Zenith")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(env)
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(tex.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    zs = [v.z for v in bb]
    center = Vector((0.0, 0.0, (min(zs) + max(zs)) / 2.0))
    height = max(zs) - min(zs)

    target = bpy.data.objects.new("target", None)
    bpy.context.collection.objects.link(target)
    target.location = center

    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 85.0
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    con = cam.constraints.new("TRACK_TO")
    con.target = target

    engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines else "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 700, 1000
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True     # composto sobre o fundo do app no driver

    # ⚠️ ESTE PREVIEW NAO E O RUNTIME. O EEVEE e o model-viewer nao resolvem
    # IBL do mesmo jeito: na pratica o navegador entrega rim roxo mais forte e
    # mais contraste que o render abaixo. Serve para conferencia rapida e para
    # comparar avatares ENTRE SI; decisao de aparencia se toma no navegador,
    # com .claude/launch.json + preview, que e onde o app vai rodar.
    #
    # View transform: o padrao do Blender 4/5 e AgX, que comprime e DESSATURA
    # muito. O model-viewer usa um tonemap neutro. Com AgX o preview mentiria
    # ainda mais para o lado escuro, e a calibracao sairia estourada.
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
    except TypeError:
        pass

    out_dir = os.path.join(a.root, "qa", "look", a.id)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    import math
    dist_cam = height * 2.3
    for name, ang in (("00_frente", 0), ("01_tresquartos", 40), ("02_lado", 90), ("03_costas", 180)):
        r = math.radians(ang)
        cam.location = center + Vector((math.sin(r) * dist_cam, -math.cos(r) * dist_cam, height * 0.10))
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(out_dir, name + ".png")
        bpy.ops.render.render(write_still=True)

    print("preview de {} em {}".format(a.id, out_dir))
    sys.exit(0)


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker_main()
    else:
        sys.exit(driver_main())
