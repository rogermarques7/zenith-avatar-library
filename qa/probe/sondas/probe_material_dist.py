#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_material_dist.py - confere o material NOS GLBs ENTREGUES.

  blender -b -P qa/probe/sondas/probe_material_dist.py [-- N]

Regua EXTERNA ao restyle.py: ele valida o proprio export reimportando o
arquivo, o que responde "gravei o que eu quis?" mas nao "o que esta em
03_dist/glb/ e o que o zenith_material.py manda hoje?". Em 31/07 o restyle
falhou em 76/76 por colisao de nome de material e a causa ficou escondida
porque o driver engolia a saida do worker - por isso existe uma segunda
leitura, que le do disco e compara com a fonte unica.

--------------------------------------------------------------------------
E ELE TAMBEM CONFERE SE O SHORT AINDA ESTA LA (01/08)
--------------------------------------------------------------------------
A primeira versao exigia UM material, e essa era a verdade quando ela foi
escrita. Depois de reaplicar os shorts, a verdade para 39 dos 76 e DOIS - e a
sonda acusaria os 39 como fora do padrao. Uma sonda que grita onde esta certo
e pior que sonda nenhuma: quem for arrumar o "defeito" roda restyle --all,
que e exatamente o que apagou os 39 shorts na sessao 18.

Entao a pergunta certa nao e "quantos materiais" e sim "os materiais deste
avatar sao os que o config/shorts_map.json manda?". Quem tem entrada no mapa
precisa de corpo + short; quem nao tem, so corpo. Assim a sonda vira a regua
que faltava em 01/08, quando os 76 estavam com 1 material e NADA avisou.
"""
import glob
import json
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import zenith_material as zm

TOL = 0.002


def com_short():
    """ids que TEM peca, segundo o mapa - o mapa e o produto (CLAUDE.md 3b)."""
    p = os.path.join(ROOT, "config", "shorts_map.json")
    if not os.path.isfile(p):
        return set()
    with open(p, "r", encoding="utf-8") as f:
        return set(json.load(f))


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    limite = int(args[0]) if args else 0

    esperado = zm.hex_to_linear_rgba(zm.ZENITH_BASE_HEX)[:3]
    arquivos = sorted(glob.glob(os.path.join(ROOT, "03_dist", "glb", "*.glb")))
    if limite:
        arquivos = arquivos[:limite]

    print("esperado: {} base={} metallic={} roughness={}".format(
        zm.ZENITH_BASE_HEX, tuple(round(v, 4) for v in esperado),
        zm.ZENITH_METALLIC, zm.ZENITH_ROUGHNESS))
    print("conferindo {} arquivos\n".format(len(arquivos)))

    mapeados = com_short()
    print("com short no mapa: {}\n".format(len(mapeados)))

    ruins = []
    sem_peca = []
    for f in arquivos:
        nome = os.path.basename(f)
        aid = nome[:-4].rsplit("_v", 1)[0]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=f)
        ob = next(o for o in bpy.context.scene.objects if o.type == "MESH")
        mats = [m.name for m in ob.data.materials]
        bsdf = next(n for n in ob.data.materials[0].node_tree.nodes
                    if n.bl_idname == "ShaderNodeBsdfPrincipled")
        cor = tuple(bsdf.inputs["Base Color"].default_value[:3])
        met = bsdf.inputs["Metallic"].default_value
        rou = bsdf.inputs["Roughness"].default_value

        esperados = ([zm.MATERIAL_NAME, zm.SHORTS_MATERIAL_NAME]
                     if aid in mapeados else [zm.MATERIAL_NAME])
        erros = []
        if mats != esperados:
            erros.append("materiais {} (esperado {})".format(mats, esperados))
            if aid in mapeados and zm.SHORTS_MATERIAL_NAME not in mats:
                sem_peca.append(aid)
        if any(abs(a - b) > TOL for a, b in zip(cor, esperado)):
            erros.append("cor {}".format(tuple(round(v, 4) for v in cor)))
        if abs(met - zm.ZENITH_METALLIC) > TOL:
            erros.append("metallic {:.3f}".format(met))
        if abs(rou - zm.ZENITH_ROUGHNESS) > TOL:
            erros.append("roughness {:.3f}".format(rou))
        if erros:
            ruins.append((nome, erros))
            print("  [RUIM] {}: {}".format(nome, " | ".join(erros)))

    print("\n" + "=" * 60)
    if sem_peca:
        print("SHORT APAGADO em {}: {}".format(len(sem_peca), ", ".join(sem_peca)))
        print("  -> python scripts/shorts.py --apply {}".format(sem_peca[0]))
    if ruins:
        print("FORA DO PADRAO: {} de {}".format(len(ruins), len(arquivos)))
    else:
        print("OK: {}/{} com {} / metallic {} / roughness {}".format(
            len(arquivos), len(arquivos), zm.ZENITH_BASE_HEX,
            zm.ZENITH_METALLIC, zm.ZENITH_ROUGHNESS))


main()
