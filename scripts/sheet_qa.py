#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sheet_qa.py - QA de uma folha de 3 vistas AINDA EM DOWNLOADS, antes de decidir se ela entra no repositorio pelo intake.py.

Nasceu como sonda descartavel em 29/07 e foi PROMOVIDA a script: virou passo
padrao antes de aprovar folha, e qa/ esta no .gitignore (ficaria fora do repo).

Existe porque o measure.py so roda sobre os recortes de 00_input/references/,
ou seja depois do intake+crop - e nao faz sentido gravar no repositorio uma
folha que pode reprovar. Aqui a folha e medida onde ela esta.

Responde as perguntas do checklist do CHARACTER_BIBLE secao 6 que sao
MENSURAVEIS (as outras - rosto neutro, careca, perfil puro - sao do olho):

  - as 3 vistas estao ALINHADAS e na MESMA ESCALA? (topo da cabeca e sola dos
    pes na mesma linha, mesma altura de figura)
  - o espacamento entre elas e uniforme? (o crop.py depende disso)
  - a resolucao serve para a Meshy Multi-View?
  - a silhueta do TRONCO: ombro, cintura, quadril, coxa (vista frontal) e a
    PROFUNDIDADE de barriga, gluteo e coxa (vista de perfil)
  - onde a roupa preta comeca e termina? (cos e faixa - insumo futuro do
    equivalente feminino do shorts_ref.py)

Uso: python scripts/sheet_qa.py "<caminho da folha>" ["<folha de referencia>"]

Com dois caminhos, imprime o DELTA entre as duas. Vale a restricao da regra 5c
do CLAUDE.md: so compara folhas do MESMO gerador com a MESMA pose.

## Reescrito em 29/07/2026 (sessao 8) - a versao anterior media outra coisa

Tres defeitos, todos encontrados de uma vez ao rodar a mesma regua na folha-mae
ja aprovada (doutrina da regua externa: [[regua-externa-antes-de-dizer-pronto]]).
NAO desfazer nenhum dos tres achando que e complicacao:

1. **A largura saia MAO A MAO, nao osso a osso.** As faixas mediam
   `cols[-1] - cols[0]` da linha inteira, e em A-pose o braco e a mao entram
   nisso: mae e filha davam ~52% de "quadril", numero que nao existe em corpo
   nenhum. Agora cada linha e quebrada em CORRIDAS contiguas e so a do eixo do
   corpo conta - com a exigencia de haver 3 corridas (tronco + 2 bracos
   destacados), senao a linha e descartada.
2. **BG_TOL=28, herdado do measure.py, nao acha o corpo nas folhas FEMININAS.**
   E o limiar nao e o problema: no ombro da mae a pele iluminada mede diferenca
   ZERO do fundo por dezenas de pixels seguidos. Com mascara por diferenca o
   corpo vira renda e a "cintura" sai com 5 px. O que sobrevive e o CONTORNO,
   entao a silhueta agora vem por PREENCHIMENTO (o fundo e a regiao plana ligada
   a borda da imagem; o que o contorno fecha e corpo, mesmo tendo a cor exata
   do fundo). O measure.py nao sofre disso porque usa os EXTREMOS da linha, e
   buraco no meio nao move extremo - nao "consertar" o measure.py por analogia.
3. **So a vista frontal era medida, e largura nao e volume.** No `f_b04_d2` a
   largura frontal ficou parada (ombro +0,17 pp) enquanto a profundidade de
   barriga, gluteo e coxa caiu 4-5% - a folha tinha dado o passo, e a regua
   frontal sozinha teria reprovado uma folha boa. Perfil entrou por isso.

O que esta regua continua NAO medindo: TONUS. Ela ve largura e profundidade,
nao relevo de superficie - foi assim que na sessao 7 duas folhas com abdomens
diferentes (uma com gomos que o descritor proibia) sairam como "o mesmo corpo".
Para isso existe `qa/probe/sondas/probe_tonus_f.py`. Ver [[regua-de-altura-nao-ve-tracado]].
"""

import sys
import numpy as np
from PIL import Image

# So precisa separar o fundo PLANO do contorno: o ruido medido do fundo nestas
# folhas e no maximo 4. Nao confundir com o BG_TOLERANCE=28 do measure.py, que
# resolve outro problema (ver defeito 2 no cabecalho).
BG_TOL = 6
GAP_MAX = 4          # fecha buraco de anti-aliasing dentro do corpo
RUN_MIN = 4          # descarta respingo
DARK_MAX = 90        # tecido preto sobre corpo cinza claro (shorts_ref.py usa ideia igual)

# Faixas em fracao da altura da figura, 0 = topo da cabeca.
#   modo  : max / min dentro da faixa
#   alvo  : 'ombro'  corrida do eixo, SEM exigir braco destacado (no ombro ele
#                    esta anatomicamente colado - por isso a faixa e fixa em
#                    0,19: varrer aqui so acharia onde o braco ja abriu, que e
#                    envergadura, nao ombro)
#           'tronco' corrida do eixo, exigindo 3 corridas
#           'membro' corrida mais larga FORA do eixo (coxa, ja separada em duas)
FRONTAL = [("ombro   ", 0.190, 0.194, "max", "ombro"),
           ("cintura ", 0.330, 0.400, "min", "tronco"),
           ("quadril ", 0.470, 0.560, "max", "tronco"),
           ("coxa    ", 0.560, 0.640, "max", "membro")]

# No perfil nao ha braco aberto para atrapalhar: a largura da linha E a
# profundidade do corpo.
PERFIL = [("torso   ", 0.245, 0.300),
          ("barriga ", 0.360, 0.430),
          ("gluteo  ", 0.470, 0.545),
          ("coxa    ", 0.575, 0.640)]


def _preenche_fundo(livre):
    """Flood fill em varredura de linha a partir das bordas. True = fundo."""
    h, w = livre.shape
    fora = np.zeros((h, w), bool)
    pilha = [(x, y) for x in range(w) for y in (0, h - 1) if livre[y, x]]
    pilha += [(x, y) for y in range(h) for x in (0, w - 1) if livre[y, x]]
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


def corridas(linha):
    """[(x0, x1), ...] das corridas contiguas de True, ja limpas."""
    idx = np.flatnonzero(linha)
    if idx.size == 0:
        return []
    quebras = np.flatnonzero(np.diff(idx) > 1)
    ini = np.concatenate([[0], quebras + 1])
    fim = np.concatenate([quebras, [idx.size - 1]])
    return _limpa([(int(idx[a]), int(idx[b])) for a, b in zip(ini, fim)])


def carrega(path):
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    corners = np.concatenate([img[:8, :8].reshape(-1, 3), img[:8, -8:].reshape(-1, 3),
                              img[-8:, :8].reshape(-1, 3), img[-8:, -8:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    mask = ~_preenche_fundo(np.abs(img - bg).max(axis=2) <= BG_TOL)
    return img, bg, mask


def separa(mask):
    """As 3 figuras, por colunas vazias - o mesmo criterio do crop.py."""
    h, w = mask.shape
    col_has = mask.any(axis=0)
    runs, start = [], None
    for x in range(w):
        if col_has[x] and start is None:
            start = x
        elif not col_has[x] and start is not None:
            runs.append((start, x - 1))
            start = None
    if start is not None:
        runs.append((start, w - 1))

    out = []
    for x0, x1 in runs:
        # Respingo fora, por LARGURA e por ALTURA. A versao anterior filtrava so
        # a largura e so nas corridas FECHADAS - a corrida que ia ate a ultima
        # coluna escapava do filtro. Um unico pixel fora de cor no canto
        # inferior direito virava "4a figura" e derrubava o bloco de
        # alinhamento inteiro, que so imprime com exatamente 3.
        if x1 - x0 + 1 <= w * 0.02:
            continue
        sub = mask[:, x0:x1 + 1]
        rows = np.flatnonzero(sub.any(axis=1))
        if rows[-1] - rows[0] + 1 <= h * 0.20:
            continue
        out.append(dict(sub=sub, x0=x0, x1=x1, y0=int(rows[0]), y1=int(rows[-1]),
                        alt=int(rows[-1] - rows[0] + 1)))
    return out


def _varre(f, a, b, modo, alvo, eixo):
    melhor, onde, descartadas = None, None, 0
    for t in np.arange(a, b, 0.004):
        y = f["y0"] + int(t * f["alt"])
        cs = corridas(f["sub"][y])
        if alvo == "membro":
            fora = [x1 - x0 + 1 for x0, x1 in cs if not (x0 <= eixo <= x1)]
            if not fora:
                descartadas += 1
                continue
            larg = max(fora)
        else:
            larg = next((x1 - x0 + 1 for x0, x1 in cs if x0 <= eixo <= x1), -1)
            if larg < 0 or (alvo == "tronco" and len(cs) < 3):
                descartadas += 1
                continue
        if melhor is None or (modo == "max" and larg > melhor) or (modo == "min" and larg < melhor):
            melhor, onde = larg, t
    return melhor, onde, descartadas


def main(path, ref=None):
    img, bg, mask = carrega(path)
    h, w, _ = img.shape
    print("imagem: {} x {} px".format(w, h))
    print("fundo: RGB {}".format(tuple(int(c) for c in bg)))

    figs = separa(mask)
    print("\nfiguras detectadas: {}".format(len(figs)))
    if len(figs) != 3:
        print("  !! o crop.py espera exatamente 3 colunas de figura")

    nomes = ["frente", "perfil", "costas"]
    for i, f in enumerate(figs):
        f["nome"] = nomes[i] if i < 3 else str(i)
        print("  {:7s} x {:4d}-{:4d}  y {:4d}-{:4d}  altura {:4d} px".format(
            f["nome"], f["x0"], f["x1"], f["y0"], f["y1"], f["alt"]))

    if len(figs) == 3:
        tops = [f["y0"] for f in figs]
        bots = [f["y1"] for f in figs]
        alts = [f["alt"] for f in figs]
        print("\nALINHAMENTO (regra critica - o pipeline nao corrige altura)")
        print("  topo da cabeca : {}  -> espalhamento {} px".format(tops, max(tops) - min(tops)))
        print("  sola dos pes   : {}  -> espalhamento {} px".format(bots, max(bots) - min(bots)))
        print("  altura         : {}  -> variacao {:.2f}% da altura".format(
            alts, 100.0 * (max(alts) - min(alts)) / max(alts)))
        centros = [(f["x0"] + f["x1"]) / 2 for f in figs]
        gaps = [centros[1] - centros[0], centros[2] - centros[1]]
        print("  espacamento entre centros: {:.0f} e {:.0f} px  (dif {:.1f}%)".format(
            gaps[0], gaps[1], 100.0 * abs(gaps[0] - gaps[1]) / max(gaps)))

    med = {}

    # --- vista FRONTAL: largura do TRONCO, com o braco fora ---------------
    f = figs[0]
    alt = f["alt"]
    cols = np.flatnonzero(f["sub"][f["y0"] + int(0.28 * alt)])
    eixo = int(np.median(cols))
    print("\nVISTA FRONTAL - largura do tronco (% da altura da figura)")
    for nome, a, b, modo, alvo in FRONTAL:
        larg, onde, desc = _varre(f, a, b, modo, alvo, eixo)
        if larg is None:
            print("  {}: SEM LINHA UTIL entre {:.3f} e {:.3f}".format(nome, a, b))
            continue
        med[nome.strip()] = 100.0 * larg / alt
        aviso = "  ({} linhas descartadas)".format(desc) if desc else ""
        print("  {}: {:4d} px = {:5.2f}%  @ {:.3f}{}".format(
            nome, larg, med[nome.strip()], onde, aviso))
    if "cintura" in med and "quadril" in med:
        print("  cintura/quadril: {:.3f}   cintura/ombro: {:.3f}".format(
            med["cintura"] / med["quadril"], med["cintura"] / med["ombro"]))

    # --- vista de PERFIL: profundidade -----------------------------------
    if len(figs) > 1:
        g = figs[1]
        print("\nVISTA DE PERFIL - profundidade (% da altura da figura)")
        for nome, a, b in PERFIL:
            vals = [max((x1 - x0 + 1) for x0, x1 in corridas(g["sub"][g["y0"] + int(t * g["alt"])]) or [(0, -1)])
                    for t in np.arange(a, b, 0.003)]
            v = max(vals)
            med["p_" + nome.strip()] = 100.0 * v / g["alt"]
            print("  {}: {:4d} px = {:5.2f}%".format(nome, v, med["p_" + nome.strip()]))

    # --- tecido preto ----------------------------------------------------
    print("\nROUPA PRETA na vista frontal (fracao da altura, 0 = topo da cabeca)")
    sub_img = img[:, f["x0"]:f["x1"] + 1]
    dark = (sub_img.max(axis=2) < DARK_MAX) & f["sub"]
    linhas = []
    for y in range(f["y0"], f["y1"] + 1):
        larg = int(f["sub"][y].sum())
        linhas.append(int(dark[y].sum()) / larg if larg else 0.0)
    linhas = np.array(linhas)
    # corridas contiguas com >25% da largura do corpo em preto = peca de roupa
    peca, ini = [], None
    for i, v in enumerate(linhas):
        if v > 0.25 and ini is None:
            ini = i
        elif v <= 0.25 and ini is not None:
            if i - ini > alt * 0.02:
                peca.append((ini, i - 1))
            ini = None
    if ini is not None:
        peca.append((ini, len(linhas) - 1))
    for a, b in peca:
        print("  peca de {:.3f} a {:.3f}  (altura {:.3f})".format(a / alt, b / alt, (b - a) / alt))

    return med


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__.strip().splitlines()[-1])
    print("=" * 62)
    atual = main(sys.argv[1])
    if len(sys.argv) > 2:
        print("\n" + "=" * 62 + "\nREFERENCIA: {}".format(sys.argv[2]))
        base = main(sys.argv[2])
        print("\n" + "=" * 62)
        print("DELTA (folha - referencia), em pontos percentuais da altura")
        for k in atual:
            if k in base:
                rot = k if not k.startswith("p_") else "perfil " + k[2:]
                print("  {:14s}: {:+6.2f} pp   ({:.2f} -> {:.2f})".format(
                    rot, atual[k] - base[k], base[k], atual[k]))
