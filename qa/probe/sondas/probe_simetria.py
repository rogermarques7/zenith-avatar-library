#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_simetria.py - mede assimetria esquerda/direita nos masters, SEM gravar.

POR QUE EXISTE
    O Rogerio subiu a vista de perfil no slot ESQUERDO do Multi-View da Meshy
    nos 39 masculinos e no zen_f_b08_d3, e no slot DIREITO nos outros femininos.
    A pergunta e se o slot muda a malha. O logs/process.log so guarda
    PASS/FAIL da trava de simetria, nao o numero - entao o numero se remede
    aqui, sobre os masters que ja existem.

METODO
    Identico ao symmetry_dev do process.py: espelha cada vertice no plano
    X=centro e mede a distancia PONTO-A-SUPERFICIE por BVH. Vertice-a-vertice
    nao serve porque a decimacao Collapse embaralha o pareamento entre os lados.

NAO GRAVA NADA. So le 02_master/ e imprime.

USO
    blender --background --python qa/probe/sondas/probe_simetria.py
"""

import os
import sys
import glob

import bpy
from mathutils.bvhtree import BVHTree


def limpa_cena():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def desvio(obj):
    verts = [v.co.copy() for v in obj.data.vertices]
    xs = [v.x for v in verts]
    centro = 0.5 * (min(xs) + max(xs))
    polys = [tuple(p.vertices) for p in obj.data.polygons]
    bvh = BVHTree.FromPolygons([tuple(v) for v in verts], polys)
    step = max(1, len(verts) // 60000)
    devs = []
    for i in range(0, len(verts), step):
        p = verts[i].copy()
        p.x = 2.0 * centro - p.x
        loc, nrm, idx, d = bvh.find_nearest(p)
        if d is not None:
            devs.append(d)
    return sum(devs) / len(devs), max(devs), len(devs)


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", ".."))
    alvos = sorted(glob.glob(os.path.join(root, "02_master", "zen_*_master.glb")))
    print("\nMASTERS: {}\n".format(len(alvos)))
    print("{:18s} {:>10s} {:>10s} {:>8s}".format("id", "media_mm", "max_mm", "n"))
    for p in alvos:
        aid = os.path.basename(p).replace("_master.glb", "")
        limpa_cena()
        bpy.ops.import_scene.gltf(filepath=p)
        objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        if not objs:
            print("{:18s} {:>10s}".format(aid, "SEM MALHA"))
            continue
        m, mx, n = desvio(objs[0])
        print("{:18s} {:10.4f} {:10.4f} {:8d}".format(aid, m * 1000.0, mx * 1000.0, n))
        sys.stdout.flush()


if __name__ == "__main__":
    main()
