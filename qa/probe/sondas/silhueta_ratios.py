#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""silhueta_ratios.py - mede RAZOES de silhueta numa imagem de corpo inteiro.

    python qa/probe/sondas/silhueta_ratios.py <img> [<img> ...] --vista frente|perfil

PARA QUE SERVE, E O QUE ELE NAO FAZ
    Foto nao da centimetro: sem escala e camera calibrada ela da PROPORCAO.
    E prever cm de corpo a partir de imagem 2D tem placar 0 de 5 neste projeto
    (LICOES.md 2.6). Entao aqui so saem numeros invariantes de escala - razoes
    entre larguras, e a ALTURA RELATIVA em que cada extremo acontece.

    A altura relativa e o numero que interessa para a pergunta "o avatar parece
    comigo?": barriga alta e arredondada e barriga baixa e pendente tem a mesma
    largura maxima e caem em fracoes de estatura diferentes.

COMO ELE ACHA O CORPO
    Por diferenca contra o fundo, estimado nos CANTOS da imagem. Serve para
    fundo claro liso (parede, folha de referencia) e para fundo escuro liso
    (render). O maior componente conexo vira a silhueta; sombra encostada na
    parede e o inimigo, e por isso o limiar e por canal e nao por luminancia.

⚠️ ESTATURA INCLUI CABELO. Comparar uma foto de pessoa com cabelo contra um
   render careca desloca TODAS as fracoes para baixo. Por isso o script imprime
   tambem as razoes ancoradas no ENTREPERNAS, que nao dependem do topo.
"""

import argparse
import os
import sys

import numpy as np

try:
    from PIL import Image
except ImportError:
    sys.exit("precisa do Pillow:  python -m pip install pillow")


def silhueta(path, tol=28):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    k = max(4, min(h, w) // 40)
    cantos = np.concatenate([a[:k, :k].reshape(-1, 3), a[:k, -k:].reshape(-1, 3),
                             a[-k:, :k].reshape(-1, 3), a[-k:, -k:].reshape(-1, 3)])
    fundo = np.median(cantos, axis=0)
    corpo = (np.abs(a - fundo).max(axis=2) > tol)

    return maior_componente(corpo), os.path.basename(path)


# ⚠️ ESTA SONDA AINDA NAO SERVE PARA A VISTA FRONTAL DE FOLHA DE REFERENCIA.
#     Em folha, a pele iluminada mede diferenca ~ZERO do fundo claro por
#     dezenas de pixels e a mascara sai OCA: o tronco vira um anel, e a
#     "corrida central" do ombro leu 19 px contra 410 de extensao da linha -
#     tinha pegado um brilho dentro do peito. E o mesmo defeito que obrigou a
#     reescrita do sheet_qa.py na sessao 8 (LICOES.md 1.1).
#
#     Preencher buraco (fundo que nao alcanca a borda) foi TESTADO e nao
#     bastou: melhorou a frente da folha de 0,360 para 0,475 em
#     quadril/cintura, ainda longe do 1,01 do render, e QUEBROU o perfil - o
#     entrepernas foi de 0,451 para 0,990, porque no perfil o vao entre as
#     pernas nao toca a borda e virou corpo. Ficou fora de proposito.
#
#     O que JA VALE hoje: a vista de PERFIL, nas tres imagens (o entrepernas
#     bateu 0,451 nas tres, que e a calibracao), e a vista frontal entre
#     RENDERS, que tem fundo escuro. Numero de frente vindo de folha nao deve
#     ser publicado ate isto fechar - o caminho e o do crop.py/sheet_qa.py,
#     que ja resolveram este fundo.


def maior_componente(mask):
    """Maior regiao conexa, por union-find sobre CORRIDAS de cada linha.

    Sem scipy de proposito: o projeto roda com numpy e Blender, e uma
    dependencia nova so para rotular pixel nao se paga. Corridas em vez de
    pixels porque sao ~100x menos elementos.
    """
    h, w = mask.shape
    runs, por_linha = [], []
    for y in range(h):
        c = np.flatnonzero(mask[y])
        atual = []
        if len(c):
            quebras = np.flatnonzero(np.diff(c) > 1)
            ini = np.concatenate([[0], quebras + 1])
            fim = np.concatenate([quebras, [len(c) - 1]])
            for a, b in zip(ini, fim):
                atual.append(len(runs))
                runs.append((y, int(c[a]), int(c[b])))
        por_linha.append(atual)

    pai = list(range(len(runs)))

    def acha(i):
        while pai[i] != i:
            pai[i] = pai[pai[i]]
            i = pai[i]
        return i

    for y in range(1, h):
        for i in por_linha[y]:
            _, a0, a1 = runs[i]
            for j in por_linha[y - 1]:
                _, b0, b1 = runs[j]
                if a0 <= b1 and b0 <= a1:          # sobrepoem em X
                    ri, rj = acha(i), acha(j)
                    if ri != rj:
                        pai[ri] = rj

    tam = {}
    for i, (_, a0, a1) in enumerate(runs):
        r = acha(i)
        tam[r] = tam.get(r, 0) + (a1 - a0 + 1)
    if not tam:
        return None
    melhor = max(tam, key=tam.get)

    out = np.zeros_like(mask)
    for i, (y, a0, a1) in enumerate(runs):
        if acha(i) == melhor:
            out[y, a0:a1 + 1] = True
    return out


def corridas(linha):
    """[(x0, x1)] dos blocos de corpo daquela linha."""
    c = np.flatnonzero(linha)
    if not len(c):
        return []
    q = np.flatnonzero(np.diff(c) > 1)
    ini = np.concatenate([[0], q + 1])
    fim = np.concatenate([q, [len(c) - 1]])
    return [(int(c[a]), int(c[b])) for a, b in zip(ini, fim)]


def perfil(corpo, central):
    """(y0, y1, largura por linha).

    ⚠️ `central=True` mede a CORRIDA DO EIXO, nao a extensao da linha. Em
    A-pose - e tambem com o braco pendurado - `ultimo - primeiro` e MAO A MAO,
    nao osso a osso: medindo assim, o avatar base e o avatar morfado deram
    numeros IDENTICOS, porque quem definia a largura eram as maos, que morph
    nenhum toca. E o mesmo defeito que o sheet_qa.py ja tinha corrigido na
    sessao 8, e eu o reintroduzi aqui.
    """
    linhas = np.flatnonzero(corpo.any(axis=1))
    y0, y1 = int(linhas[0]), int(linhas[-1])
    eixo = float(np.median(np.flatnonzero(corpo.any(axis=0))))
    larg = np.zeros(y1 - y0 + 1, dtype=float)
    for i, y in enumerate(range(y0, y1 + 1)):
        r = corridas(corpo[y])
        if not r:
            continue
        if central:
            dentro = [t for t in r if t[0] <= eixo <= t[1]]
            t = dentro[0] if dentro else max(r, key=lambda t: t[1] - t[0])
        else:
            t = (r[0][0], r[-1][1])
        larg[i] = t[1] - t[0] + 1
    return y0, y1, larg


def entrepernas(corpo, y0, y1):
    """Fracao da estatura em que as pernas se juntam - o landmark que NAO
    depende do cabelo, e por isso o unico que atravessa foto de pessoa
    cabeluda contra render careca."""
    H = y1 - y0
    topo = None
    for y in range(y1, y0 + int(0.45 * H), -1):
        r = [t for t in corridas(corpo[y]) if (t[1] - t[0]) > 0.02 * H]
        if len(r) >= 2:
            topo = y
    return (topo - y0) / H if topo else None


def medir(path, vista):
    corpo, nome = silhueta(path)
    if corpo is None or not corpo.any():
        return None
    # na FRENTE o braco e ruido e sai pela corrida central; no PERFIL ele esta
    # no mesmo plano do tronco e a extensao da linha E a profundidade.
    y0, y1, larg = perfil(corpo, central=(vista == "frente"))
    H = y1 - y0

    def f(y_idx):
        return y_idx / H

    def banda(a, b):
        i0, i1 = int(a * H), int(b * H)
        return larg[i0:i1], i0

    out = {"arquivo": nome, "altura_px": H}
    ep = entrepernas(corpo, y0, y1)
    out["entrepernas_frac"] = ep

    if vista == "frente":
        # Ombro: maximo do tronco alto. Braco pendurado colado nao permite
        # separar ombro de braco, entao isto e LARGURA TOTAL - comparavel entre
        # imagens da mesma pose, e so isso.
        omb, i = banda(0.16, 0.26)
        out["ombro_larg"] = float(omb.max())
        out["ombro_em"] = f(i + int(np.argmax(omb)))
        cin, i = banda(0.34, 0.50)
        out["cintura_larg"] = float(cin.max())
        out["cintura_em"] = f(i + int(np.argmax(cin)))
        qua, i = banda(0.46, 0.56)
        out["quadril_larg"] = float(qua.max())
        out["quadril_em"] = f(i + int(np.argmax(qua)))
        cox, i = banda(0.56, 0.66)
        out["coxa_larg"] = float(cox.max())
        pan, i = banda(0.76, 0.88)
        out["panturrilha_larg"] = float(pan.max())
    else:
        # PERFIL: a profundidade e a largura da silhueta. O maximo do tronco e
        # a barriga; ONDE ele cai separa barriga alta de barriga pendente.
        pei, i = banda(0.22, 0.34)
        out["peito_prof"] = float(pei.max())
        bar, i = banda(0.34, 0.55)
        j = int(np.argmax(bar))
        out["barriga_prof"] = float(bar.max())
        out["barriga_em"] = f(i + j)
        # centro de massa VERTICAL do excesso: onde a profundidade passa da do
        # peito. E o que distingue barril de avental.
        acima = bar - out["peito_prof"]
        acima[acima < 0] = 0
        if acima.sum() > 0:
            idx = np.arange(len(bar))
            out["excesso_centroide"] = f(i + float((acima * idx).sum() / acima.sum()))
            out["excesso_area"] = float(acima.sum() / (H * out["peito_prof"]))
        cox, i = banda(0.56, 0.66)
        out["coxa_prof"] = float(cox.max())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("imgs", nargs="+")
    ap.add_argument("--vista", choices=["frente", "perfil"], required=True)
    args = ap.parse_args()

    linhas = [medir(p, args.vista) for p in args.imgs]
    linhas = [x for x in linhas if x]
    if not linhas:
        sys.exit("nenhuma silhueta encontrada")

    if args.vista == "frente":
        cols = [("ombro/cintura", lambda d: d["ombro_larg"]/d["cintura_larg"]),
                ("quadril/cintura", lambda d: d["quadril_larg"]/d["cintura_larg"]),
                ("coxa/cintura", lambda d: d["coxa_larg"]/d["cintura_larg"]),
                ("pantu/coxa", lambda d: d["panturrilha_larg"]/d["coxa_larg"]),
                ("cintura em", lambda d: d["cintura_em"]),
                ("entrepernas", lambda d: d["entrepernas_frac"] or float("nan"))]
    else:
        cols = [("barriga/peito", lambda d: d["barriga_prof"]/d["peito_prof"]),
                ("coxa/peito", lambda d: d["coxa_prof"]/d["peito_prof"]),
                ("barriga em", lambda d: d["barriga_em"]),
                ("excesso em", lambda d: d.get("excesso_centroide", float("nan"))),
                ("excesso area", lambda d: d.get("excesso_area", 0.0)),
                ("entrepernas", lambda d: d["entrepernas_frac"] or float("nan"))]

    print("%-38s %8s" % ("arquivo", "alt_px") + "".join("%15s" % c for c, _ in cols))
    for d in linhas:
        print("%-38s %8d" % (d["arquivo"][:38], d["altura_px"])
              + "".join("%15.3f" % fn(d) for _, fn in cols))


if __name__ == "__main__":
    main()
