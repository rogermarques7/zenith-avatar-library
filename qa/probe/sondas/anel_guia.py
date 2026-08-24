#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""anel_guia.py - ONDE o anel de um guia de medidas do app cai, em fracao da
estatura da figura, para comparar direto com o `at_frac` do metrics.py.

POR QUE ELA EXISTE
    O guia e um DESENHO, e o desenho e o que o usuario obedece - nao o rotulo do
    campo nem o texto da ajuda. Em 21/08 os dois primeiros corpos reais medidos
    no projeto puseram a fita no umbigo com o rotulo ja corrigido para "Cintura":
    o rotulo nao venceu o habito. Quem manda e o anel.

    E o §8 antigo do INTEGRACAO_ZENITH ja tinha produzido tres afirmacoes falsas
    sobre esses arquivos porque foram lidas no CABECALHO DE COMENTARIO do .dart
    em vez dos pixels (LICOES 1.7b). Esta sonda le os pixels.

⚠️ O CRITERIO E LARGURA DA LINHA, NAO BRILHO.
    A figura e contorno luminoso sobre preto, e o contorno SATURA igual ao anel -
    limiar de brilho sozinho devolve a figura inteira (mediu o anel do
    abdomen.png com 925 px de altura). O que separa os dois e quantos pixels
    acesos ha NA LINHA: o anel atravessa o tronco inteiro, o contorno sao duas
    bordas finas. Com o criterio frouxo o abdomen.png lia 0,657; com este, 0,637.

USO
    python qa/probe/sondas/anel_guia.py <arquivo.png> [<arquivo.png> ...]
    python qa/probe/sondas/anel_guia.py            # todos os guias do app
"""
import os
import sys

import numpy as np
from PIL import Image

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "..", "..", "zenith", "assets", "medidas")

# As alturas do metrics.py, para o numero encostar sem conversao.
REF = {
    "waist_navel": 0.600,   # <- o que o `waist_cm` do app significa desde 21/08
    "waist_min": 0.645,
    "hip": 0.507,
    "chest": 0.720,
    "shoulder": 0.795,
    "thigh": 0.460,
    "calf": 0.207,
    "neck": 0.876,
}

# ⚠️ O QUE ELA NAO MEDE. O anel e uma ELIPSE em perspectiva, e esta sonda devolve
# o centro do NUCLEO ACESO - que nao e exatamente a altura anatomica que o
# desenho marca quando a elipse esta muito inclinada. Serve para dizer "este anel
# esta na cintura minima e nao no umbigo" (8 pontos de diferenca em at_frac);
# NAO serve para brigar por 0,01. Divergencia pequena contra o REF nao e defeito
# do asset sem alguem olhar o desenho.

MIN_NA_LINHA = 100      # o anel atravessa o tronco; contorno nao chega perto
BRILHO = 0.80
SATURACAO = 0.20


def medir(caminho):
    a = np.asarray(Image.open(caminho).convert("RGB")).astype(np.float32) / 255.0
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)

    figura = mx > 0.10
    linhas = np.flatnonzero(figura.sum(axis=1) >= 8)
    if len(linhas) < 2:
        return None
    topo, base = int(linhas[0]), int(linhas[-1])
    alt = base - topo

    anel = (mx > BRILHO) & (sat > SATURACAO)
    ys = np.flatnonzero(anel.sum(axis=1) >= MIN_NA_LINHA)
    if len(ys) == 0:
        return {"erro": "anel nao encontrado (nenhuma linha com {} px acesos)"
                        .format(MIN_NA_LINHA)}
    blocos = np.split(ys, np.flatnonzero(np.diff(ys) > 4) + 1)
    b = max(blocos, key=len)
    y0, y1 = int(b[0]), int(b[-1])
    frac = (base - (y0 + y1) / 2.0) / alt
    perto = min(REF.items(), key=lambda kv: abs(kv[1] - frac))
    return {"topo": topo, "base": base, "alt": alt, "y0": y0, "y1": y1,
            "frac": frac, "perto": perto[0], "delta": frac - perto[1]}


def main():
    alvos = sys.argv[1:]
    if not alvos:
        alvos = sorted(os.path.join(APP, f) for f in os.listdir(APP)
                       if f.endswith(".png"))
    for p in alvos:
        nome = os.path.basename(p)
        r = medir(p)
        if r is None or "erro" in r:
            print("{:20s} {}".format(nome, (r or {}).get("erro", "nao li")))
            continue
        print("{:20s} figura {:4d}..{:4d} ({:4d} px)  anel {:4d}..{:4d}  "
              "at_frac {:.3f}   mais perto: {} ({:+.3f})".format(
                  nome, r["topo"], r["base"], r["alt"], r["y0"], r["y1"],
                  r["frac"], r["perto"], r["delta"]))


if __name__ == "__main__":
    main()
