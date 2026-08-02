#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_folha_f.py - silhueta do TRONCO de uma folha, com o braco FORA da conta.

Existe porque as bandas do sheet_qa medem a largura do bounding box da linha,
e em A-pose o braco e a mao entram nela: mae e filha dao ~52% de "quadril"
porque o que esta sendo medido na altura do quadril e mao-a-mao, nao osso a
osso. Aqui cada linha e quebrada em CORRIDAS contiguas e so a corrida CENTRAL
(a que contem o eixo do corpo) e medida.

Uso: python qa/probe/sondas/probe_folha_f.py "<folha A>" ["<folha B>"]
"""

import sys
import numpy as np
from PIL import Image

# NAO da para achar o corpo por diferenca de fundo nestas folhas. O sheet_qa
# herdou BG_TOL=28 do measure.py, calibrado nas MASCULINAS; baixar para 8 nao
# resolve porque o problema nao e o limiar: no ombro da mae a pele iluminada
# mede diferenca ZERO do fundo por dezenas de pixels seguidos. O corpo vira
# renda e a "cintura" sai com 5 px.
#
# O que sobrevive e o CONTORNO (o lado sombreado da silhueta, 50+ de diferenca).
# Entao a silhueta e obtida por PREENCHIMENTO: o fundo e a regiao plana ligada
# a borda da imagem; tudo que o contorno fecha por dentro e corpo, mesmo que
# tenha a cor exata do fundo.
BG_TOL = 6           # so precisa separar fundo plano (ruido medido <= 4) do contorno
GAP_MAX = 4          # fecha buraco de anti-aliasing dentro do corpo
RUN_MIN = 4          # descarta respingo


def _preenche_fundo(livre):
    """Flood fill em varredura de linha a partir das bordas. True = fundo."""
    h, w = livre.shape
    fora = np.zeros((h, w), bool)
    pilha = []
    for x in range(w):
        for y in (0, h - 1):
            if livre[y, x]:
                pilha.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if livre[y, x]:
                pilha.append((x, y))
    while pilha:
        x, y = pilha.pop()
        if fora[y, x] or not livre[y, x]:
            continue
        x0 = x
        while x0 > 0 and livre[y, x0 - 1] and not fora[y, x0 - 1]:
            x0 -= 1
        x1 = x
        while x1 < w - 1 and livre[y, x1 + 1] and not fora[y, x1 + 1]:
            x1 += 1
        fora[y, x0:x1 + 1] = True
        for vy in (y - 1, y + 1):
            if 0 <= vy < h:
                faixa = livre[vy, x0:x1 + 1] & ~fora[vy, x0:x1 + 1]
                for dx in np.flatnonzero(faixa):
                    pilha.append((x0 + int(dx), vy))
    return fora


def _limpa(cs):
    """Funde corridas separadas por gap <= GAP_MAX e joga fora as curtas."""
    if not cs:
        return []
    out = [list(cs[0])]
    for x0, x1 in cs[1:]:
        if x0 - out[-1][1] - 1 <= GAP_MAX:
            out[-1][1] = x1
        else:
            out.append([x0, x1])
    return [(a, b) for a, b in out if b - a + 1 >= RUN_MIN]


def figuras(path):
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    h, w, _ = img.shape
    corners = np.concatenate([img[:8, :8].reshape(-1, 3), img[:8, -8:].reshape(-1, 3),
                              img[-8:, :8].reshape(-1, 3), img[-8:, -8:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    mask = ~_preenche_fundo(np.abs(img - bg).max(axis=2) <= BG_TOL)

    col_has = mask.any(axis=0)
    runs, start = [], None
    for x in range(w):
        if col_has[x] and start is None:
            start = x
        elif not col_has[x] and start is not None:
            if x - start > w * 0.02:
                runs.append((start, x - 1))
            start = None
    if start is not None:
        runs.append((start, w - 1))

    out = []
    for x0, x1 in runs:
        sub = mask[:, x0:x1 + 1]
        rows = np.flatnonzero(sub.any(axis=1))
        out.append(dict(sub=sub, x0=x0, x1=x1, y0=int(rows[0]), y1=int(rows[-1]),
                        alt=int(rows[-1] - rows[0] + 1)))
    return out


def corridas(linha):
    """[(x0, x1), ...] das corridas contiguas de True."""
    idx = np.flatnonzero(linha)
    if idx.size == 0:
        return []
    quebras = np.flatnonzero(np.diff(idx) > 1)
    ini = np.concatenate([[0], quebras + 1])
    fim = np.concatenate([quebras, [idx.size - 1]])
    return _limpa([(int(idx[a]), int(idx[b])) for a, b in zip(ini, fim)])


def tronco_em(f, frac, eixo):
    """Largura da corrida que contem o eixo do corpo. (-1, n_corridas) se sumir."""
    y = f["y0"] + int(frac * f["alt"])
    cs = corridas(f["sub"][y])
    for x0, x1 in cs:
        if x0 <= eixo <= x1:
            return x1 - x0 + 1, len(cs)
    return -1, len(cs)


def medir(path):
    f = figuras(path)[0]          # vista FRONTAL
    alt = f["alt"]
    # eixo do corpo: mediana das colunas ocupadas na altura do peito
    y = f["y0"] + int(0.28 * alt)
    cols = np.flatnonzero(f["sub"][y])
    eixo = int(np.median(cols))

    print("\n== {}".format(path.split("\\")[-1]))
    print("   figura {} px de altura, eixo em x={}".format(alt, eixo))

    def varre(a, b, modo, alvo):
        """alvo='tronco' usa a corrida do eixo e SO aceita linha com os dois
        bracos destacados (3 corridas) - senao a largura vira ombro+braco.
        alvo='membro' pega a corrida mais larga fora do eixo (coxa, que na
        altura medida ja se separou em duas)."""
        melhor, onde, descartadas = None, None, 0
        for t in np.arange(a, b, 0.004):
            y = f["y0"] + int(t * alt)
            cs = corridas(f["sub"][y])
            if alvo in ("tronco", "ombro"):
                larg = next((x1 - x0 + 1 for x0, x1 in cs if x0 <= eixo <= x1), -1)
                # 3 corridas = tronco + 2 bracos destacados. Sem isso a largura
                # do "tronco" inclui o braco colado e nao mede nada.
                if larg < 0 or (alvo == "tronco" and len(cs) < 3):
                    descartadas += 1
                    continue
            else:
                fora = [x1 - x0 + 1 for x0, x1 in cs if not (x0 <= eixo <= x1)]
                if not fora:
                    descartadas += 1
                    continue
                larg = max(fora)
            if melhor is None or (modo == "max" and larg > melhor) or (modo == "min" and larg < melhor):
                melhor, onde = larg, t
        return melhor, onde, descartadas

    # No ombro o braco esta ANATOMICAMENTE colado ao tronco - nao ha 3 corridas
    # e nao adianta exigir. Por isso a linha e FIXA em 0,19 (a mesma da medicao
    # que aprovou a mae): varrer uma faixa aqui so acharia o ponto em que o
    # braco ja abriu, que e largura de envergadura, nao de ombro.
    linhas = [("ombro   ", 0.190, 0.194, "max", "ombro"),
              ("cintura ", 0.330, 0.400, "min", "tronco"),
              ("quadril ", 0.470, 0.560, "max", "tronco"),
              ("coxa    ", 0.560, 0.640, "max", "membro")]
    r = {}
    for nome, a, b, modo, alvo in linhas:
        larg, onde, desc = varre(a, b, modo, alvo)
        if larg is None:
            print("   {}: SEM LINHA UTIL na faixa {:.3f}-{:.3f}".format(nome, a, b))
            continue
        r[nome.strip()] = larg
        aviso = "  ({} linhas descartadas)".format(desc) if desc else ""
        print("   {}: {:4d} px = {:5.2f}% da altura  @ {:.3f}{}".format(
            nome, larg, 100.0 * larg / alt, onde, aviso))
    print("   cintura/quadril: {:.3f}".format(r["cintura"] / r["quadril"]))
    print("   cintura/ombro  : {:.3f}".format(r["cintura"] / r["ombro"]))
    return {k: 100.0 * v / alt for k, v in r.items()}


if __name__ == "__main__":
    res = [medir(p) for p in sys.argv[1:]]
    if len(res) == 2:
        print("\n== DELTA (B - A), em pontos percentuais da altura")
        for k in res[0]:
            print("   {:8s}: {:+.2f} pp   ({:.2f} -> {:.2f})".format(
                k, res[1][k] - res[0][k], res[0][k], res[1][k]))
