#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bainha_rasante.py - a bainha MODELADA, com luz rasante, e as duas linhas
candidatas desenhadas por cima.

    blender -b -P qa/probe/sondas/bainha_rasante.py -- --ids zen_m_b09h_d1,...

Renderiza o MASTER (sem pintura nenhuma: um material so) com luz rasante, que
e o unico angulo em que relevo de milimetros aparece - a mesma doutrina do
probe_superficie.py (LICOES.md 1.12). Por cima desenha:

    VERMELHO  a bainha do mapa   (onde a tinta acaba hoje)
    VERDE     a bainha da folha  (shorts_ref.medir, a regua externa)

A pergunta que esta imagem responde, e que nenhuma medida do projeto respondeu
ate agora: EXISTE degrau de tecido na malha, e ele esta ACIMA da linha
vermelha? Se existe e esta acima, a tinta desce alem do tecido e a queixa do
Rogerio e de pintura. Se nao existe degrau nenhum, o short da perna e pintura
pura e a folha e a unica fonte que sobra.

⚠️ Sem pintura DE PROPOSITO. Com o preto contra o claro o olho ve a divisa de
cor e para ali; foi essa confusao que produziu a hipotese errada do "vinco
diagonal" na sessao 4 (ver o docstring de w_fit). Um material so, luz rasante,
e o relevo fica sozinho na imagem.
"""
import argparse
import json
import math
import os
import sys

import bpy
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
# ⚠️ O Python do Blender nao tem PIL, entao a folha NAO se le aqui dentro. O
# numero externo vem do cache qa/probe/folha_peca/hem.json, gravado pelo Python
# do sistema com shorts_ref.medir(). Importar shorts_ref aqui mata a sonda.
FOLHA = {}
_fp = os.path.join(ROOT, "qa", "probe", "folha_peca", "hem.json")
if os.path.isfile(_fp):
    with open(_fp, encoding="utf-8") as _f:
        FOLHA = json.load(_f)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--ids", default="")
ap.add_argument("--todos", action="store_true")
ap.add_argument("--vistas", default="frente,obliqua",
                help="quais das 4 renderizar; menos vistas = varredura mais rapida")
ap.add_argument("--span", type=float, default=0.13)
# a mesma sonda serve para a FAIXA: o que muda e so a altura do alvo.
# O defeito de borda de peca e o mesmo problema nos dois lugares -
# tecido modelado de um lado da linha, tinta do outro.
ap.add_argument("--zh", type=float, default=None,
                help="altura do alvo; padrao = a bainha do mapa")
ap.add_argument("--alvo", default="hem", choices=["hem", "cos"],
                help="que BORDA enquadrar; 'cos' usa o topo do cos do mapa, por "
                     "avatar - as duas bordas da mesma peca tem o mesmo defeito")
ap.add_argument("--out", default=os.path.join(ROOT, "qa", "revisao", "_hem"))
a = ap.parse_args(argv)

# ⚠️ `RenderEngine.__subclasses__()` so enxerga engine de ADDON - as embutidas
# nao aparecem ali. O probe_superficie.py usa esse teste e por isso cai sempre
# no except. O jeito honesto de perguntar e TENTAR ATRIBUIR: o RNA recusa
# identificador que nao existe, com TypeError.
def _engine():
    sc = bpy.context.scene
    for nome in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = nome
            return nome
        except TypeError:
            continue
    raise SystemExit("ABORTADO: sem EEVEE. Workbench apaga relevo (LICOES 1.12).")


ENGINE = _engine()


# ⚠️ As linhas NAO sao desenhadas em 3D. A primeira versao punha um toro por
# altura e ele tapava exatamente o relevo de 1 mm que a sonda existe para
# mostrar - a marca comia o objeto medido. Aqui a camera e ORTOGRAFICA, entao a
# altura vira linha de pixel por uma conta fechada, e a marca e 1 px, desenhada
# depois no PNG pelo `bainha_marca.py`.
def linha_px(zh, z0, alt, zc, ortho, res_y):
    """Linha de pixel de uma altura zh, na camera ortografica desta sonda."""
    dz = (z0 + zh * alt) - zc
    return int(round(res_y / 2 - dz / ortho * res_y))


def _posiciona_luz(lamp, ang, zc, alt):
    """⚠️ A LUZ GIRA COM A CAMERA. A primeira versao deixava a lampada fixa em
    (-3,-3), entao na vista de COSTAS ela iluminava a FRENTE do corpo e as
    costas saiam em sombra chapada - e o relevo e o unico dado desta sonda.
    Medido: forca do vinco 3,5 na frente contra 1,2 nas costas no
    zen_m_b09h_d1. Luz rasante que nao acompanha o ponto de vista nao e luz
    rasante, e contraluz."""
    r = math.radians(ang)
    lamp.location = (-3 * math.cos(r) - 3 * math.sin(r),
                     -3 * math.cos(r) + 3 * math.sin(r), zc - alt * 0.02)
    lamp.rotation_euler = (math.radians(100), 0, r + math.radians(-40))


def uma(aid, smap):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(
        filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    zs = [v.co.z for v in ob.data.vertices]
    xs = [v.co.x for v in ob.data.vertices]
    z0, alt = min(zs), max(zs) - min(zs)

    # UM material so, claro e fosco: o relevo tem de ser a unica informacao
    ob.data.materials.clear()
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    mat = bpy.data.materials.new("clay")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.72, 0.73, 0.75, 1)
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Metallic"].default_value = 0.0
    ob.data.materials.append(mat)

    e = smap[aid]
    if a.zh is not None:
        hm, hf = float(a.zh), None
    elif a.alvo == "cos":
        w = e["waist_zh"]
        hm = max(w) if isinstance(w, list) else float(w)
        hf = FOLHA.get(aid, {}).get("back", {}).get("topo")
    else:
        hm = e["hem_l_zh"]
        hm = hm[0] if isinstance(hm, list) else float(hm)
        hf = FOLHA.get(aid, {}).get("back", {}).get("base")

    sc = bpy.context.scene
    sc.render.engine = ENGINE
    RES_X, RES_Y = 1100, 900
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.35, 0.38, 1)

    ld = bpy.data.lights.new("k", type="AREA")
    ld.energy = 900
    ld.size = 2
    lamp = bpy.data.objects.new("k", ld)
    sc.collection.objects.link(lamp)
    zc = z0 + hm * alt
    # rasante: quase no plano do corte, vindo de baixo-lado. Luz de cima
    # esconde exatamente o degrau que se procura, porque ele e um ressalto
    # virado para baixo.


    cd = bpy.data.cameras.new("c")
    cd.type = "ORTHO"
    cd.ortho_scale = alt * a.span
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam

    outdir = os.path.join(a.out, aid)
    os.makedirs(outdir, exist_ok=True)
    PREFIXO = "rasante_" if a.alvo == "hem" else "rasante_cos_"
    if a.zh is not None:
        PREFIXO = "rasante_faixa_"
    quero = [x for x in a.vistas.split(",") if x]
    for nome, ang in [v for v in (("frente", 0), ("obliqua", 40), ("lado", 90),
                                  ("costas", 180)) if v[0] in quero]:
        r = math.radians(ang)
        cam.location = (5 * math.sin(r), -5 * math.cos(r), zc)
        cam.rotation_euler = (math.radians(90), 0, r)
        _posiciona_luz(lamp, ang, zc, alt)
        sc.render.filepath = os.path.join(outdir, PREFIXO + nome + ".png")
        bpy.ops.render.render(write_still=True)
    ortho = cd.ortho_scale * RES_Y / RES_X
    marcas = {"mapa": [linha_px(hm, z0, alt, zc, ortho, RES_Y), [235, 40, 40]]}
    if hf is not None:
        marcas["folha"] = [linha_px(hf, z0, alt, zc, ortho, RES_Y), [30, 210, 60]]
    with open(os.path.join(outdir, PREFIXO.rstrip("_") + "_marcas.json"), "w",
              encoding="utf-8") as f:
        json.dump({"id": aid, "hem_mapa_zh": hm, "hem_folha_zh": hf,
                   "res": [RES_X, RES_Y], "marcas": marcas}, f, indent=1)
    print("OK {}  mapa={:.4f}  folha={}".format(
        aid, hm, "-" if hf is None else "%.4f" % hf))


with open(os.path.join(ROOT, "config", "shorts_map.json"), encoding="utf-8") as f:
    SMAP = json.load(f)
_IDS = sorted(SMAP) if a.todos else [x for x in a.ids.split(",") if x]
for _i, _aid in enumerate(_IDS, 1):
    print("[{}/{}]".format(_i, len(_IDS)), end=" ")
    uma(_aid, SMAP)
