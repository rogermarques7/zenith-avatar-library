#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shorts_ref.py - mede onde o short esta na FOLHA DE REFERENCIA e compara com o
que o shorts.py pintou no 3D.

    python scripts/shorts_ref.py            # tabela dos 39
    python scripts/shorts_ref.py {id}

--------------------------------------------------------------------------
PORQUE ISTO EXISTE
--------------------------------------------------------------------------
O shorts.py acha o short lendo a MALHA (vincos de tecido). Isso resolve o
problema que a projecao de imagem nao resolvia - a barriga que cobre o cos -
mas cria um ponto cego: nada estava conferindo o resultado contra a intencao.
O `--report` do shorts.py compara cada avatar com a SERIE, e a serie pode
estar consistentemente errada; foi assim que o zen_m_b12_d1 passou como
"dentro da faixa" com o short na altura errada.

A referencia e a unica fonte externa: e a imagem que gerou a malha, e nela o
short e literalmente preto sobre um corpo cinza claro. Medir ali e barato e
independente do detector 3D.

--------------------------------------------------------------------------
O QUE ESTA MEDIDA VALE, E O QUE NAO VALE
--------------------------------------------------------------------------
NAO e uma regua exata. A Meshy reinterpreta as proporcoes, entao a altura do
cos na folha e no master nao batem no centesimo - a mesma ressalva que o
CLAUDE.md ja registra sobre o measure.py (regra 5c). Serve para achar erro
GROSSO: um cos 15% da altura fora de lugar aparece aqui e nao aparece na
comparacao com a serie.

Usa a vista de COSTAS. Na frente, num corpo obeso, a barriga cobre o short na
propria imagem, entao o topo medido seria a prega e nao o cos.
"""

import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def medir(path):
    """Devolve (topo_zh, base_zh, area_frac) do short na imagem, em fracao da
    altura da FIGURA (nao do canvas)."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)

    # fundo = mediana da borda; figura = tudo que se afasta dele
    borda = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]], axis=0)
    bg = np.median(borda, axis=0)
    dist = np.abs(a - bg).sum(axis=2)
    fig = dist > 30
    ys, xs = np.where(fig)
    if ys.size == 0:
        return None
    y0, y1 = ys.min(), ys.max()
    Hpx = max(1, y1 - y0)

    # short = escuro de verdade. O corpo e cinza claro; o short e quase preto.
    lum = a.mean(axis=2)
    escuro = fig & (lum < 90)

    # ---- FRACAO DA LARGURA DO CORPO, e nao contagem de pixel escuro --------
    # A versao ingenua ("linha tem N pixels escuros") acusou short ate os pes em
    # TODOS os avatares d3: num corpo definido a sombra entre as coxas e escura
    # e vai ate o chao, e a sombra sob o braco idem. Nenhuma das duas cobre a
    # LARGURA do corpo - o short cobre. Entao a pergunta certa e "que fracao da
    # largura desta linha e escura?", nao "quantos pixels escuros ha nela".
    largura = fig.sum(axis=1).astype(np.float64)
    escuros = escuro.sum(axis=1).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(largura > 0, escuros / np.maximum(largura, 1), 0.0)
    linha_short = frac > 0.55

    # ---- maior faixa CONTIGUA ---------------------------------------------
    # O short e uma peca so. Sombra sob o braco vira uma faixa curta e separada;
    # pegar a maior corrida contigua descarta essas sem precisar de limiar novo.
    melhor, atual_ini = None, None
    for y in range(len(linha_short) + 1):
        dentro = y < len(linha_short) and linha_short[y]
        if dentro and atual_ini is None:
            atual_ini = y
        elif not dentro and atual_ini is not None:
            if melhor is None or (y - atual_ini) > (melhor[1] - melhor[0]):
                melhor = (atual_ini, y)
            atual_ini = None
    if melhor is None:
        return None

    topo = (y1 - melhor[0]) / Hpx
    base = (y1 - (melhor[1] - 1)) / Hpx
    return topo, base, escuro.sum() / float(fig.sum())


def main():
    alvo = sys.argv[1] if len(sys.argv) > 1 else None

    smap = {}
    p = os.path.join(ROOT, "config", "shorts_map.json")
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            smap = json.load(f)

    bmi = {}
    lib = os.path.join(ROOT, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            bmi = {x["id"]: x.get("measured_bmi", 0) for x in json.load(f)["avatars"]}

    def _one(v):
        return v[0] if isinstance(v, (list, tuple)) else v

    ids = [alvo] if alvo else sorted(smap, key=lambda k: bmi.get(k, 0))
    print("{:<15} {:>6}  {:>16}  {:>16}  {}".format(
        "id", "imc", "COS  ref / 3d", "BAINHA ref / 3d", "erro"))
    print("-" * 82)
    fora = []
    for aid in ids:
        ref = os.path.join(ROOT, "00_input", "references", aid, aid + "_ref_back.png")
        if not os.path.isfile(ref):
            print("{:<15} sem folha de costas".format(aid))
            continue
        m = medir(ref)
        if m is None:
            print("{:<15} short nao detectado na folha".format(aid))
            continue
        topo_ref, base_ref, _ = m

        e = smap.get(aid)
        if not e:
            continue
        w = e["waist_zh"]
        topo_3d = max(w) if isinstance(w, (list, tuple)) else w
        base_3d = _one(e["hem_l_zh"])

        d_topo = topo_3d - topo_ref
        d_base = base_3d - base_ref
        ruim = abs(d_topo) > 0.06 or abs(d_base) > 0.06
        if ruim:
            fora.append(aid)
        print("{:<15} {:>6.1f}  {:>7.3f} /{:>7.3f}  {:>7.3f} /{:>7.3f}  {:>+6.3f} {:>+6.3f} {}".format(
            aid, bmi.get(aid, 0), topo_ref, topo_3d, base_ref, base_3d,
            d_topo, d_base, "<<" if ruim else ""))
    print("-" * 82)
    print("tolerancia +-0.06 da altura (a Meshy reinterpreta proporcao; isto pega erro grosso)")
    if fora:
        print("FORA ({}): {}".format(len(fora), ", ".join(fora)))
    else:
        print("todos dentro da tolerancia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
