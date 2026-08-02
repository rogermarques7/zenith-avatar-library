#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
probe_topologia.py - os masters compartilham topologia?

Roda em Blender headless:
  blender -b -P qa/probe/sondas/probe_topologia.py -- id1 id2 [id3 ...]

POR QUE ISTO EXISTE (31/07/2026, sessao 18)
-------------------------------------------
O plano de produto discutido e "aplicar shape keys em todos os avatares".
Shape key (morph target) NAO e um efeito visual: e uma segunda posicao para
CADA VERTICE da MESMA malha. Interpolar de um corpo para outro exige que o
vertice de indice i seja o MESMO PONTO ANATOMICO nos dois - mesma contagem,
mesma ordem, mesma conectividade.

Cada avatar aqui vem de uma geracao independente da Meshy e depois passa por
uma decimacao guiada pela geometria daquele corpo. Nada nesse caminho garante
correspondencia. Este script mede, em vez de supor.

O QUE ELE CHECA, do mais barato ao mais decisivo:
  1. contagem de vertices/arestas/faces - se diferir, ja acabou;
  2. valencia (grau de cada vertice) ordenada - assinatura topologica grosseira;
  3. distancia entre vertices de MESMO INDICE - se as malhas correspondessem,
     seria pequena e coerente; se for da ordem do tamanho do corpo, os indices
     nao tem relacao nenhuma;
  4. teste de vizinhanca: os vizinhos do vertice i em A sao os mesmos indices
     que os vizinhos do vertice i em B?

Contagem igual NAO prova correspondencia - todos os masters tem ~29992
vertices porque o alvo de decimacao e 60000 triangulos, o que e coincidencia
de ALVO, nao de topologia. Por isso os itens 3 e 4 existem.
"""
import sys, os

import bpy
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))


def argv_ids():
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def carregar(avatar_id):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    caminho = os.path.join(ROOT, "02_master", avatar_id + "_master.glb")
    if not os.path.exists(caminho):
        raise SystemExit("nao achei " + caminho)
    bpy.ops.import_scene.gltf(filepath=caminho)
    ob = next(o for o in bpy.data.objects if o.type == "MESH")
    me = ob.data
    verts = [ob.matrix_world @ v.co for v in me.vertices]
    # vizinhanca por indice, a partir das arestas
    viz = [set() for _ in verts]
    for e in me.edges:
        a, b = e.vertices
        viz[a].add(b); viz[b].add(a)
    return {
        "id": avatar_id,
        "nv": len(me.vertices), "ne": len(me.edges), "nf": len(me.polygons),
        "verts": verts,
        "valencia": sorted(len(v) for v in viz),
        "viz": viz,
    }


def comparar(A, B):
    print("\n" + "=" * 66)
    print("{}  x  {}".format(A["id"], B["id"]))
    print("=" * 66)

    print("  vertices : {:>6} x {:>6}   {}".format(
        A["nv"], B["nv"], "IGUAL" if A["nv"] == B["nv"] else "DIFERENTE"))
    print("  arestas  : {:>6} x {:>6}   {}".format(
        A["ne"], B["ne"], "IGUAL" if A["ne"] == B["ne"] else "DIFERENTE"))
    print("  faces    : {:>6} x {:>6}   {}".format(
        A["nf"], B["nf"], "IGUAL" if A["nf"] == B["nf"] else "DIFERENTE"))

    if A["nv"] != B["nv"]:
        print("\n  -> contagem diferente: shape key entre estes dois e IMPOSSIVEL.")
        return

    igual_val = A["valencia"] == B["valencia"]
    print("  valencia ordenada: {}".format("identica" if igual_val else "DIFERENTE"))

    # 3. distancia entre vertices de mesmo indice
    n = A["nv"]
    passo = max(1, n // 4000)
    amostra = range(0, n, passo)
    ds = [(A["verts"][i] - B["verts"][i]).length for i in amostra]
    ds.sort()
    media = sum(ds) / len(ds)
    p50 = ds[len(ds) // 2]
    p95 = ds[int(len(ds) * 0.95)]
    alturaA = max(v.z for v in A["verts"]) - min(v.z for v in A["verts"])
    print("\n  distancia entre vertices de MESMO INDICE (n={}):".format(len(ds)))
    print("    media {:.3f} m | mediana {:.3f} m | p95 {:.3f} m".format(media, p50, p95))
    print("    (altura do corpo = {:.3f} m -> mediana e {:.1f}% da altura)".format(
        alturaA, 100 * p50 / alturaA))

    # 4. vizinhanca por indice
    iguais = sum(1 for i in amostra if A["viz"][i] == B["viz"][i])
    print("\n  vizinhos identicos por indice: {}/{} ({:.1f}%)".format(
        iguais, len(list(amostra)), 100 * iguais / len(list(amostra))))

    corresponde = igual_val and iguais / len(list(amostra)) > 0.99
    print("\n  VEREDITO: topologia {}".format(
        "CORRESPONDENTE - shape key viavel" if corresponde
        else "NAO CORRESPONDENTE - shape key entre eles e impossivel"))


def main():
    ids = argv_ids()
    if len(ids) < 2:
        raise SystemExit("uso: ... -- id1 id2 [id3 ...]")
    base = carregar(ids[0])
    for outro in ids[1:]:
        comparar(base, carregar(outro))


main()
