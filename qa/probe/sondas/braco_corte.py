# -*- coding: utf-8 -*-
"""braco_corte.py - o corte braco/tronco do w_arm_wide, fatia a fatia.

    blender -b -P qa/probe/sondas/braco_corte.py -- --id ID [--id ID2 ...]

Imprime, por fatia de 0.005 da altura dentro da banda da faixa:

    zh        altura da fatia
    meia      meia-largura da fatia (do eixo ate o ponto mais lateral)
    cru E/D   o corte que a passada 1 achou em cada lado, em metros
    suave     depois da mediana movel de 5
    %         quanto da meia-largura fica marcada como braco

Existe porque o recorte na quina de baixo da faixa (FILA_PECAS, fila viva desde
11/08) e uma ESCADA no render, e escada tem duas causas possiveis que a foto nao
distingue: o corte pular de fatia para fatia, ou o corte estar certo e a
quantizacao da malha ser o degrau. Este print separa as duas.
"""
import argparse
import os
import sys

import bpy
import numpy as np

root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(root, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
ap = argparse.ArgumentParser()
ap.add_argument("--id", action="append", required=True)
a = ap.parse_args(argv)

smap = S.load_map(root)
for aid in a.id:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master",
                                                    aid + "_master.glb"))
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    H = co[:, 2].max() - co[:, 2].min()
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)

    e = smap[aid]
    lo = float(np.atleast_1d(e["faixa_lo_zh"]).min())
    hi = float(np.atleast_1d(e["faixa_hi_zh"]).max())
    d = {}
    m = S.w_arm_wide(np, co, H, is_arm, lo, hi, diag=d)

    print("== %s   faixa %.3f..%.3f   fusao do braco %.4f   marcados %d" % (
        aid, lo, hi,
        float(((co[:, 2] - co[:, 2].min()) / H)[is_arm].max()) if is_arm.any()
        else -1.0, int(m.sum())))
    print("  %6s %7s | %8s %8s | %8s %8s | %5s %5s | %s" % (
        "zh", "meia", "cruE", "cruD", "suaveE", "suaveD", "%E", "%D", "fonte"))

    def _f(v):
        return "  -     " if v is None else "%8.4f" % v

    def _p(v, mw):
        return "  -  " if v is None or mw <= 0 else "%4.0f%%" % (100.0 * v / mw)

    for i, zh in enumerate(d["zh"]):
        mw = d["meia_largura"][i]
        print("  %6.3f %7.4f | %s %s | %s %s | %s %s | %s/%s" % (
            zh, mw, _f(d["cru"][-1.0][i]), _f(d["cru"][1.0][i]),
            _f(d["suave"][-1.0][i]), _f(d["suave"][1.0][i]),
            _p(d["suave"][-1.0][i], mw), _p(d["suave"][1.0][i], mw),
            d["fonte"][-1.0][i], d["fonte"][1.0][i]))

    # ---- o PERFIL DE PROFUNDIDADE cru, que e o sinal de onde tudo sai -------
    # De fora para dentro, coluna a coluna: o braco e um tubo raso e o tronco e
    # fundo. E aqui que se ve se o degrau existe e onde ele esta - o criterio
    # atual (60% da profundidade MAXIMA da fatia) nao olha para o degrau, olha
    # para o valor absoluto, e por isso o busto o empurra para dentro.
    z = co[:, 2]
    zh_v = (z - z.min()) / H
    cx = np.median(co[:, 0])
    for zsel in (d["zh"][1], d["zh"][len(d["zh"]) // 2], d["zh"][-2]):
        f = np.where((zh_v >= zsel) & (zh_v < zsel + d["passo"]))[0]
        y, x = co[f, 1], co[f, 0] - cx
        fundo = y.max() - y.min()
        for sinal in (-1.0, 1.0):
            lado = np.where(np.sign(x) == sinal)[0]
            if len(lado) < 20:
                continue
            xl = x[lado] * sinal
            perfil = []
            for b in np.arange(xl.max(), 0.0, -S.COL_W * H):
                col = (xl <= b) & (xl > b - S.COL_W * H)
                if col.sum() < 3:
                    perfil.append((b, None))
                    continue
                yc = y[lado][col]
                perfil.append((b, yc.max() - yc.min()))
            print("  perfil zh %.3f lado %+d  fundo %.4f  (60%%=%.4f)" % (
                zsel, sinal, fundo, 0.60 * fundo))
            print("    " + "  ".join(
                "%.3f:%s" % (b, "----" if p is None else "%.3f" % p)
                for b, p in perfil[:14]))
print("RESULT ok")
