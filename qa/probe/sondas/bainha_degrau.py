#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bainha_degrau.py - ❌ HIPOTESE MORTA: a bainha pelo DEGRAU DE RAIO.

    blender -b -P qa/probe/sondas/bainha_degrau.py -- --ids zen_m_b09h_d1,...
    blender -b -P qa/probe/sondas/bainha_degrau.py -- --todos

Grava qa/probe/hem_degrau/{id}.json e imprime uma linha por avatar.

--------------------------------------------------------------------------
🔴 LEIA ISTO ANTES DE RODAR: ELA NAO FUNCIONA, E O MOTIVO E MEDIDO (23/09)
--------------------------------------------------------------------------
Fica no repositorio como a QUINTA hipotese morta da bainha, ao lado das quatro
do LICOES.md 1.10 - nao como ferramenta. Rodada nos primeiros seis avatares ela
devolve degraus de 24 a 39 mm, que nao sao tecido: sao a coxa AFINANDO.

O sinal nao existe a 60k. Medido no `zen_m_b09h_d1`, o raio mediano do quadrante
externo, em fatias de 2,6 mm, salta assim descendo a perna:

    11.097 -> 10.424 -> 10.332 -> 11.070 cm

ou seja **+-0,7 cm de ruido entre fatias vizinhas** - e a espessura do tecido
que se procurava mede 4 mm. Nao e limiar mal escolhido nem alisamento de menos:
o degrau esta uma ordem de grandeza abaixo do ruido da propria medida. Some-se
que o raio cai monotonicamente pela conicidade da coxa, entao o "maior degrau"
foge para a borda da janela (LICOES.md 1.11) em quase todo avatar.

✅ **O que FUNCIONOU no lugar dela: uma IMAGEM** - `bainha_rasante.py`, clay sem
pintura, luz rasante, camera ortografica nivelada. Ver LICOES.md 4.5j. A licao
e a da 4.5j inteira: a quinta pergunta feita a malha por numero morreu como as
quatro anteriores, e quem respondeu foi um render de 40 s.

--------------------------------------------------------------------------
POR QUE UM SINAL NOVO, E POR QUE ESTE
--------------------------------------------------------------------------
A frente da bainha foi aberta em 13/08 e revertida inteira. O LICOES.md 1.10
lista o que ja morreu ali - lasca de costura, prateleira de `nz`, vinco
diagonal, vinco setor a setor - e fecha com a condicao de reabertura:

    "Quem reabrir precisa de um SINAL NOVO - nao de um offset maior, nao de
     mais uma passada de curvatura."

As quatro mortas perguntam a mesma coisa de quatro jeitos: ONDE A SUPERFICIE
DOBRA (curvatura, normal). Esta pergunta e outra: ONDE A SUPERFICIE AFASTA DO
OSSO. O tecido e uma CASCA SOBRE A PELE - o state.md ja registra isso para a
faixa do zen_f_b05_d3, medido em 4 mm - entao descendo a perna o raio cai de
degrau quando a casca acaba. Raio e uma medida de POSICAO, nao de derivada:
sobrevive a decimacao, que e exatamente o que matou o vinco setor a setor.

--------------------------------------------------------------------------
O QUE ESTA SONDA NAO MEDE
--------------------------------------------------------------------------
- Nao serve onde a Meshy modelou o short RENTE, sem espessura: ali nao ha
  degrau e a sonda devolve `deg_zh: null`. Isso e resposta, nao falha - e o
  caso em que so a folha tem o sinal.
- Nao mede a bainha da perna INTERNA perto da virilha, onde as duas coxas se
  tocam: a secao deixa de ser um disco e o raio mediano passa a medir a fusao.
  Por isso o azimute externo (|nx| alto) tem peso e o interno e descartado.
- O degrau da PERNA tambem existe no joelho e na virilha. A janela e ancorada
  na bainha do mapa (+-JANELA_ZH), entao esta sonda responde "o degrau perto
  da linha pintada esta ACIMA ou ABAIXO dela?" e nunca "onde esta a bainha no
  vazio".
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
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--ids", default="")
ap.add_argument("--todos", action="store_true")
a = ap.parse_args(argv)

OUT = os.path.join(ROOT, "qa", "probe", "hem_degrau")
os.makedirs(OUT, exist_ok=True)

# Janela em volta da bainha do mapa. 0.030 da altura = 5,2 cm, larga o
# bastante para o degrau real caber dos dois lados e estreita o bastante para
# nao alcancar joelho (>=0.09 abaixo) nem virilha (>=0.015 acima).
JANELA_ZH = 0.030
# Resolucao vertical: 0.0015 da altura = 2,6 mm. Z_BINS do shorts.py e 240
# (7,3 mm), e o defeito que se procura mede 6 a 9 mm - medir o defeito com a
# regua que o produziu nao responde nada.
PASSO_ZH = 0.0015
# So o quadrante EXTERNO da coxa. O interno mede a fusao com a outra perna.
NX_MIN = 0.45


def carrega(aid):
    master = os.path.join(ROOT, "02_master", aid + "_master.glb")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=master)
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = obj.data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    return me, co.reshape(n, 3)


def perfil(co, sel, cx, cy, z0, z1, passo):
    """Raio mediano do quadrante externo, por fatia fina de altura.

    `z0`, `z1` e `passo` vem em METROS - PASSO_ZH e fracao da altura e tem de
    ser multiplicado por H antes de chegar aqui."""
    zs = np.arange(z0, z1 + passo / 2, passo)
    dx = co[sel, 0] - cx
    dy = co[sel, 1] - cy
    r = np.hypot(dx, dy)
    nx = np.abs(dx) / np.maximum(r, 1e-9)
    ok = nx >= NX_MIN
    zv = co[sel, 2]
    out = []
    for zc in zs:
        m = ok & (np.abs(zv - zc) < passo)
        out.append(float(np.median(r[m])) if m.sum() >= 12 else np.nan)
    return zs, np.array(out)


def degrau(zs, rr):
    """Maior QUEDA de raio descendo, em curva alisada. Devolve (zh, cm)."""
    bons = ~np.isnan(rr)
    if bons.sum() < len(rr) * 0.6:
        return None, 0.0
    rr = np.interp(np.arange(len(rr)), np.where(bons)[0], rr[bons])
    # media movel de 3 amostras (7,9 mm): tira ruido de decimacao e nao
    # apaga um degrau de 4 mm, que e a espessura medida do tecido
    k = np.ones(3) / 3.0
    rs = np.convolve(rr, k, mode="same")
    d = rs[:-1] - rs[1:]          # positivo = raio caiu descendo
    if d.size == 0:
        return None, 0.0
    i = int(np.argmax(d))
    if i == 0 or i == d.size - 1:
        return None, float(d[i])  # encostou na borda da janela: nao vale
    return float((zs[i] + zs[i + 1]) / 2), float(d[i])


def uma(aid, smap):
    e = smap.get(aid)
    if not e:
        return None
    me, co = carrega(aid)
    zs_all = co[:, 2]
    H = float(zs_all.max() - zs_all.min())
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)

    lids = [0, 1]
    mx = [float(co[leg_id == l, 0].mean()) if (leg_id == l).any() else 0.0
          for l in lids]
    if mx[0] > mx[1]:
        lids.reverse()

    res = {"id": aid, "H": round(H, 4), "pernas": []}
    for lado, lid in zip(("l", "r"), lids):
        hem = e["hem_" + lado + "_zh"]
        hem = hem[0] if isinstance(hem, list) else float(hem)
        c = e.get("hem_center_" + lado, [0.0, 0.0])
        sel = np.where(leg_id == lid)[0]
        z0 = (hem - JANELA_ZH) * H + zs_all.min()
        z1 = (hem + JANELA_ZH) * H + zs_all.min()
        zs, rr = perfil(co, sel, c[0], c[1], z0, z1, PASSO_ZH * H)
        zd, dcm = degrau(zs, rr)
        res["pernas"].append({
            "lado": lado,
            "hem_mapa_zh": round(hem, 4),
            "degrau_zh": None if zd is None else round((zd - zs_all.min()) / H, 4),
            "degrau_mm": round(dcm * 1000, 2),
            "delta_zh": None if zd is None else
                        round((zd - zs_all.min()) / H - hem, 4),
            "n": int(sel.size),
        })
    return res


def main():
    with open(os.path.join(ROOT, "config", "shorts_map.json"), encoding="utf-8") as f:
        smap = json.load(f)
    ids = ([k for k in sorted(smap)] if a.todos
           else [x for x in a.ids.split(",") if x])
    print("{:<18} {:>9} {:>9} {:>8} {:>7}   {:>9} {:>8} {:>7}".format(
        "id", "hem_map", "deg_l", "d_l", "mm_l", "deg_r", "d_r", "mm_r"))
    for aid in ids:
        r = uma(aid, smap)
        if r is None:
            continue
        with open(os.path.join(OUT, aid + ".json"), "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1)
        p = r["pernas"]
        print("{:<18} {:>9.4f} {:>9} {:>8} {:>7.2f}   {:>9} {:>8} {:>7.2f}".format(
            aid, p[0]["hem_mapa_zh"],
            "-" if p[0]["degrau_zh"] is None else "%.4f" % p[0]["degrau_zh"],
            "-" if p[0]["delta_zh"] is None else "%+.4f" % p[0]["delta_zh"],
            p[0]["degrau_mm"],
            "-" if p[1]["degrau_zh"] is None else "%.4f" % p[1]["degrau_zh"],
            "-" if p[1]["delta_zh"] is None else "%+.4f" % p[1]["delta_zh"],
            p[1]["degrau_mm"]))


main()
