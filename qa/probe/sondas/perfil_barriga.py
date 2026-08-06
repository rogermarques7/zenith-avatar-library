#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""perfil_barriga.py - a UNICA razao de silhueta que atravessa foto, folha e
render sem calibracao: profundidade da BARRIGA sobre a do PEITO, na vista de
perfil, e ONDE o maximo da barriga cai.

POR QUE SO ISTO
    Foto nao da centimetro (LICOES.md 2.6). E as razoes que dependem de
    ESTATURA nao atravessam foto de pessoa cabeluda contra render careca, nem
    sobrevivem a segmentacao do chao - o ladrilho tem a mesma saturacao da pele
    da perna (S 24 contra 19, medido). Entao aqui nada depende do chao nem do
    topo real: as duas medidas saem da MESMA imagem, na mesma banda, e a
    posicao e dada entre dois landmarks de alto contraste que existem nas tres
    fontes - o topo da cabeca e o CÓS DO SHORT (preto na foto e na folha,
    material proprio no render).

O QUE ELE RESPONDE
    barriga/peito   -> quanto de volume central, independente de escala
    barriga em      -> ONDE ele esta. Barril alto e avental pendente tem a mesma
                       largura maxima e caem em posicoes diferentes. Foi essa a
                       diferenca que o olho do Rogerio pegou em 05/08.
"""
import argparse, os, sys
import numpy as np
from PIL import Image


def mascara(path):
    im = Image.open(path).convert("HSV")
    a = np.asarray(im).astype(float)
    S, V = a[:, :, 1], a[:, :, 2]
    fundo_claro = (np.median(V[:40, :40]) > 120)
    if fundo_claro:                      # foto de parede clara / folha
        corpo = (S > 14) | (V < 120)
    else:                                # render de fundo escuro
        corpo = V > 45
    return corpo, S, V


def corridas(l):
    c = np.flatnonzero(l)
    if not len(c):
        return []
    q = np.flatnonzero(np.diff(c) > 1)
    ini = np.concatenate([[0], q + 1]); fim = np.concatenate([q, [len(c) - 1]])
    return [(int(c[a]), int(c[b])) for a, b in zip(ini, fim)]


def medir(path):
    corpo, S, V = mascara(path)
    h, w = corpo.shape
    linhas = np.flatnonzero(corpo.any(axis=1))
    y_topo = int(linhas[0])

    # CÓS: a faixa escura mais alta que atravessa boa parte do tronco. O short
    # e preto na foto e na folha; no render ele e um material proprio, mais
    # escuro que o corpo sob a mesma luz.
    escuro = corpo & (V < np.percentile(V[corpo], 22))
    larg_escuro = escuro.sum(axis=1)
    larg_corpo = np.maximum(corpo.sum(axis=1), 1)
    cand = np.flatnonzero((larg_escuro / larg_corpo > 0.55)
                          & (np.arange(h) > y_topo + 0.30 * (h - y_topo)))
    if not len(cand):
        return None
    y_cos = int(cand[0])
    vao = y_cos - y_topo
    if vao < 50:
        return None

    # profundidade = extensao da linha (no perfil o braco esta no plano do
    # tronco, entao a silhueta E a profundidade)
    prof = np.zeros(h)
    for y in range(y_topo, y_cos):
        r = corridas(corpo[y])
        if r:
            prof[y] = r[-1][1] - r[0][0] + 1

    def maxbanda(f0, f1):
        i0, i1 = y_topo + int(f0 * vao), y_topo + int(f1 * vao)
        b = prof[i0:i1]
        j = int(np.argmax(b))
        return float(b[j]), (i0 + j - y_topo) / vao

    peito, _ = maxbanda(0.34, 0.60)
    barriga, onde = maxbanda(0.60, 1.00)
    return {"arq": os.path.basename(path), "vao_px": vao,
            "peito": peito, "barriga": barriga,
            "razao": barriga / peito, "barriga_em": onde}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("imgs", nargs="+")
    args = ap.parse_args()
    print("%-34s %8s %9s %9s %9s %11s" % ("arquivo", "vao_px", "peito", "barriga",
                                          "barr/peito", "barriga em"))
    for p in args.imgs:
        d = medir(p)
        if not d:
            print("%-34s  (nao achei o cos)" % os.path.basename(p)); continue
        print("%-34s %8d %9.0f %9.0f %9.3f %11.3f"
              % (d["arq"][:34], d["vao_px"], d["peito"], d["barriga"],
                 d["razao"], d["barriga_em"]))
