# -*- coding: utf-8 -*-
"""cos_etapas.py - imprime o cos em CADA etapa do w_fit, setor a setor.

    blender -b -P qa/probe/sondas/cos_etapas.py -- --id ID

    bruto     saida do w_waist_curve (argmax + prior + mediana de 7)
    avental   depois do w_cos_avental (dobra + mediana de 3 + trava de degrau)
    liso      depois do w_waist_liso (alisamento com teto)

Existe porque um vinco que sobra na curva final pode ter nascido em qualquer uma
das tres, e a resposta muda o conserto: quina no `bruto` e argmax; quina que
APARECE no `avental` e trava de degrau; quina que sobrevive ao `liso` e o teto
segurando uma medida de verdade. Sem separar as etapas, o palpite e cego.

Nao grava nada e nao renderiza - so instrumenta o w_fit por monkeypatch.
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
ap.add_argument("--id", required=True)
a = ap.parse_args(argv)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(root, "02_master",
                                                a.id + "_master.glb"))
ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
me = ob.data
n = len(me.vertices)
co = np.empty(n * 3, dtype=np.float64)
me.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
H = co[:, 2].max() - co[:, 2].min()
crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
e = S.load_map(root).get(a.id, {})

etapas = []
_av, _li = S.w_cos_avental, S.w_waist_liso


def av(np_, co_, nor_, arm_, H_, cz, hz, waist, ab):
    etapas.append(("bruto", list(waist)))
    out = _av(np_, co_, nor_, arm_, H_, cz, hz, waist, ab)
    etapas.append(("avental", list(out)))
    return out


def li(np_, waist, piso):
    if not etapas or etapas[-1][0] != "avental":
        etapas.append(("bruto", list(waist)))
    out = _li(np_, waist, piso)
    etapas.append(("liso", list(out)))
    return out


S.w_cos_avental, S.w_waist_liso = av, li
cfg, diag = S.w_fit(me, np, co, H, crotch, leg_id, is_arm,
                    crotch_override=e.get("crotch_override_zh"),
                    waist_override=e.get("waist_ring_override_zh"),
                    faixa=S.tem_faixa(a.id),
                    faixa_base_override=e.get("faixa_base_override_zh"),
                    faixa_topo_reto=bool(e.get("faixa_topo_reto")),
                    faixa_topo_frente=e.get("faixa_topo_frente_zh"),
                    cos_avental=bool(e.get("cos_avental")))
S.w_cos_avental, S.w_waist_liso = _av, _li

print("anel = %.4f   virilha = %.4f" % (diag["waist_ring_zh"], diag["crotch_zh"]))
print("%-8s %s" % ("setor", " ".join("%6d" % j for j in range(S.WAIST_AZ_BINS))))
for nome, w in etapas:
    print("%-8s %s" % (nome, " ".join("%6.3f" % v for v in w)))
for nome, w in etapas:
    m = len(w)
    print("%-8s passo %.3f  canto %.3f" % (
        nome,
        max(abs(w[i] - w[(i + 1) % m]) for i in range(m)),
        max(abs(w[(i - 1) % m] - 2 * w[i] + w[(i + 1) % m]) for i in range(m))))
print("RESULT ok")
