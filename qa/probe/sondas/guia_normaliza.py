#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""guia_normaliza.py - poe um guia novo no enquadramento do conjunto e instala.

    python qa/probe/sondas/guia_normaliza.py <origem.png> <destino.png> [referencia.png]

POR QUE
    O app desenha o PNG inteiro num espaco fixo. Figura que ocupa 83% do quadro
    aparece muito maior que uma que ocupa 61%, e a ilustracao "pula" de tamanho
    ao passar de um passo do guia para o outro. O `anel_guia.py` NAO pega isso:
    ele mede o anel em fracao da FIGURA, entao passa com a figura de qualquer
    tamanho. Foi assim que a primeira feminina chegou com o anel certo (0,603) e
    o enquadramento errado.

    A referencia de enquadramento e o `abdomen.png`, que e o guia masculino ja
    ajustado. Semelhanca pura (escala uniforme + translacao) sobre fundo preto:
    nao distorce nada e o `at_frac` sobrevive por construcao.
"""
import os
import sys

import numpy as np
from PIL import Image

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "..", "..", "zenith", "assets", "medidas")
REFERENCIA = os.path.join(APP, "abdomen.png")


def caixa(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32) / 255.0
    fig = a.max(axis=2) > 0.10
    ys = np.flatnonzero(fig.sum(axis=1) >= 8)
    t, b = int(ys[0]), int(ys[-1])
    xs = np.flatnonzero(fig[t:b + 1].sum(axis=0) >= 3)
    return t, b, int(xs[0]), int(xs[-1]), a.shape[1], a.shape[0]


def main():
    if len(sys.argv) not in (3, 4):
        raise SystemExit("uso: guia_normaliza.py <origem.png> <destino.png> [referencia.png]")
    src, out = sys.argv[1], sys.argv[2]
    # ⚠️ A REFERENCIA PADRAO NAO SERVE PARA O GUIA DE ALTURA. A `caixa()` mede a
    # envoltoria de TUDO que esta aceso, e no guia de altura isso inclui a SETA
    # de cota ao lado do corpo - centralizar essa envoltoria empurraria a figura
    # para o meio, desfazendo o deslocamento a esquerda que o guia masculino usa
    # de proposito para abrir espaco para a seta. Para aquele, a referencia e o
    # proprio `altura.png`.
    ref = sys.argv[3] if len(sys.argv) == 4 else REFERENCIA
    mt, mb, mx0, mx1, mW, mH = caixa(ref)
    ft, fb, fx0, fx1, fW, fH = caixa(src)

    k = (mb - mt) / (fb - ft)
    im = Image.open(src).convert("RGB").resize(
        (max(int(round(fW * k)), 1), max(int(round(fH * k)), 1)), Image.LANCZOS)
    dy = int(round(mt - ft * k))
    dx = int(round((mx0 + mx1) / 2.0 - (fx0 * k + fx1 * k) / 2.0))

    folha = Image.new("RGB", (mW, mH), (0, 0, 0))
    folha.paste(im, (dx, dy))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    folha.save(out)

    t2, b2, _, _, _, H2 = caixa(out)
    print("origem  figura {} px ({:.0f}% do quadro)".format(
        fb - ft, 100.0 * (fb - ft) / fH))
    print("escala  {:.4f}   dx {}  dy {}".format(k, dx, dy))
    print("saida   figura y {}..{} = {} px ({:.0f}% do quadro)   "
          "referencia: {} px ({:.0f}%)".format(
              t2, b2, b2 - t2, 100.0 * (b2 - t2) / H2,
              mb - mt, 100.0 * (mb - mt) / mH))
    print("->", out)


if __name__ == "__main__":
    main()
