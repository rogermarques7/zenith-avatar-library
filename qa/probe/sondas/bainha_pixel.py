#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bainha_pixel.py - acha o vinco da bainha NO PIXEL do clay rasante.

    python qa/probe/sondas/bainha_pixel.py            # os 103
    python qa/probe/sondas/bainha_pixel.py zen_f_b06i_d3

Le `qa/revisao/_hem/{id}/rasante_frente.png` (o clay da `bainha_rasante.py`) e
grava `qa/revisao/_hem/{id}/pixel_frente.json` com a altura do vinco COLUNA A
COLUNA. O `bainha_mosaico.py` desenha isso em AZUL por cima, e e olhando o azul
que se decide se a medida vale.

--------------------------------------------------------------------------
POR QUE NO PIXEL, DEPOIS DE CINCO TENTATIVAS NA MALHA
--------------------------------------------------------------------------
Ja morreram cinco perguntas feitas a malha por numero (LICOES.md 1.10 e 4.5j):
lasca de costura, prateleira de `nz`, vinco diagonal, vinco setor a setor e
degrau de raio. Todas tentavam achar o vinco em 60k vertices, onde ele mede
menos que o ruido de decimacao.

O que mudou nao foi o sinal - foi a AMOSTRAGEM. Uma fatia de azimute de 15 graus
tem ~20 vertices; a mesma regiao no render ortografico tem ~45 COLUNAS DE PIXEL,
e cada coluna e uma media de muitos vertices feita pelo rasterizador com a luz
rasante realcando exatamente o relevo procurado. O render nao inventa geometria:
ele reamostra a mesma malha numa grade mais fina e com contraste dirigido.

⚠️ E o ganho tem preco: no pixel nao ha azimute, ha COLUNA. A conversao
coluna -> azimute depende do raio da perna, e por isso esta sonda devolve
`y_por_coluna` e `zh_por_coluna`, e NAO uma curva de 24 setores. Quem for
gravar no mapa tem de fazer essa conversao com o centro e o raio da perna, e
declarar o que fez.

--------------------------------------------------------------------------
O QUE ESTA SONDA NAO MEDE
--------------------------------------------------------------------------
- So a metade do corpo virada para a camera. A vista frontal ve o vinco da
  frente da coxa; as costas precisam da vista propria.
- Nao distingue vinco de TECIDO de vinco de PELE (prega inguinal, sulco de
  quadriceps). A continuidade entre colunas ajuda, a janela ajuda, e o resto e
  o olho na folha de contato - que e o ponto: esta sonda existe para ser
  CONFERIDA, nao para ser obedecida.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
BASE = os.path.join(ROOT, "qa", "revisao", "_hem")

# janela em fracao da altura do corpo, em volta da bainha do mapa (que e o
# centro da imagem por construcao da bainha_rasante). Para CIMA tem de caber os
# ~6 cm do zen_f_b06i_d3; para baixo basta um pouco, porque a tinta ja esta no
# ponto baixo.
SOBE_ZH = 0.045
DESCE_ZH = 0.010
# penalidade de degrau entre colunas vizinhas, em unidades de resposta por pixel
LAM = 0.06


def ridge(a):
    """Resposta de LINHA ESCURA horizontal: claro acima, escuro no centro,
    claro abaixo. E a assinatura do vinco sob luz rasante vinda de baixo - o
    ressalto do tecido tapa a luz e deixa uma sombra fina logo abaixo dele."""
    s = np.apply_along_axis(lambda c: np.convolve(c, np.ones(5) / 5, mode="same"),
                            0, a)
    k = np.zeros(21)
    k[:7] = 1.0 / 14
    k[14:] = 1.0 / 14
    k[7:14] = -1.0 / 7
    return np.apply_along_axis(lambda c: np.convolve(c, k, mode="same"), 0, s)


def traca(R, y0, y1, lam=LAM):
    """Caminho de resposta maxima ao longo das COLUNAS, com custo de degrau.

    Aqui a continuidade nao e enfeite: o vinco de tecido atravessa a coxa
    inteira, enquanto sulco de musculo e sombra de dobra sao manchas curtas. E
    o mesmo criterio que separou short de sombra no `shorts_ref.medir` (corrida
    longa contra mancha curta), agora em duas dimensoes."""
    W = y1 - y0
    nx = R.shape[1]
    custo = R[y0:y1, :]
    sc = np.full((nx, W), -1e18)
    bk = np.zeros((nx, W), dtype=np.int32)
    sc[0] = custo[:, 0]
    passo = np.abs(np.subtract.outer(np.arange(W), np.arange(W)))
    pen = lam * passo
    for x in range(1, nx):
        d = sc[x - 1][None, :] - pen
        k = d.argmax(axis=1)
        sc[x] = d[np.arange(W), k] + custo[:, x]
        bk[x] = k
    cam = [int(sc[nx - 1].argmax())]
    for x in range(nx - 1, 0, -1):
        cam.append(int(bk[x, cam[-1]]))
    return [y0 + z for z in reversed(cam)]


def uma(aid, pref="rasante", vista="frente"):
    d = os.path.join(BASE, aid)
    src = os.path.join(d, pref + "_" + vista + ".png")
    mp = os.path.join(d, pref + "_marcas.json")
    if not (os.path.isfile(src) and os.path.isfile(mp)):
        return None
    with open(mp, encoding="utf-8") as f:
        mk = json.load(f)
    a = np.asarray(Image.open(src).convert("L")).astype(np.float64)
    h, w = a.shape
    R = ridge(a)

    # a bainha do mapa esta no CENTRO da imagem por construcao (zc = hem).
    # 900 px cobrem ortho = alt*0.22*900/1100 da altura do corpo.
    px_por_zh = 900.0 / (0.22 * 900.0 / 1100.0)
    y0 = max(10, int(h / 2 - SOBE_ZH * px_por_zh))
    y1 = min(h - 10, int(h / 2 + DESCE_ZH * px_por_zh))
    cam = traca(R, y0, y1)

    # ---- COLUNA QUE NAO TEM CORPO NAO TEM MEDIDA --------------------------
    # O fundo e liso, entao a resposta de vinco nele e exatamente zero e o DP
    # atravessa o vao entre as pernas desenhando uma linha que nao mede nada.
    # Sem isto, a folha de contato mostra azul no ar e eu leria como acerto.
    # Nao ha limiar a escolher: liso e zero, superficie nao e.
    pico = R[y0:y1, :].max(axis=0)
    vale = (pico > 0.20).tolist()

    zh = [round(mk["hem_mapa_zh"] + (h / 2.0 - y) / px_por_zh, 5) for y in cam]
    res = {
        "id": aid, "hem_mapa_zh": mk["hem_mapa_zh"],
        "hem_folha_zh": mk["hem_folha_zh"],
        "janela_y": [y0, y1], "px_por_zh": round(px_por_zh, 2),
        "y_por_coluna": cam, "zh_por_coluna": zh, "vale": vale,
        "cols_validas": int(sum(vale)),
        "zh_min": min(zh), "zh_max": max(zh),
        "zh_mediana": float(np.median([z for z, v in zip(zh, vale) if v] or zh)),
        # forca media do vinco no caminho: e o numero que diz se ha vinco ou se
        # o tracado esta passeando em ruido
        "forca": round(float(np.mean([R[cam[x], x] for x in range(w) if vale[x]]
                                     or [0.0])), 3),
        "no_teto": int(sum(1 for y, v in zip(cam, vale) if v and y <= y0 + 2)),
        "no_piso": int(sum(1 for y, v in zip(cam, vale) if v and y >= y1 - 2)),
    }
    res["vista"] = vista
    res["alvo"] = pref
    nome = "pixel_{}_{}.json".format(pref.replace("rasante_", "").replace("rasante", "hem"), vista)
    with open(os.path.join(d, nome), "w", encoding="utf-8") as f:
        json.dump(res, f)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--alvo", default="hem", choices=["hem", "cos"])
    ap.add_argument("--vista", default="frente")
    a = ap.parse_args()
    pref = "rasante" if a.alvo == "hem" else "rasante_cos"
    ids = a.ids or sorted(
        x for x in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, x)) and x.startswith("zen_"))
    print("{:<18} {:>8} {:>8} {:>8} {:>8} {:>7} {:>5} {:>5}".format(
        "id", "mapa", "folha", "px_med", "px_max", "forca", "teto", "piso"))
    for aid in ids:
        r = uma(aid, pref, a.vista)
        if r is None:
            continue
        print("{:<18} {:>8.4f} {:>8} {:>8.4f} {:>8.4f} {:>7.3f} {:>5} {:>5}".format(
            aid, r["hem_mapa_zh"],
            "-" if r["hem_folha_zh"] is None else "%.4f" % r["hem_folha_zh"],
            r["zh_mediana"], r["zh_max"], r["forca"], r["no_teto"], r["no_piso"]))


main()
