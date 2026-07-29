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
  - o quadril e mais largo que os ombros? (exigencia do descritor feminino)
  - onde a roupa preta comeca e termina? (cos e sutia - insumo futuro do
    equivalente feminino do shorts_ref.py)

Uso: python scripts/sheet_qa.py "<caminho da folha>"
"""

import sys
import numpy as np
from PIL import Image

BG_TOL = 28          # mesma tolerancia do measure.py
DARK_MAX = 90        # tecido preto sobre corpo cinza claro (shorts_ref.py usa ideia igual)


def main(path):
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    h, w, _ = img.shape
    print("imagem: {} x {} px".format(w, h))

    corners = np.concatenate([img[:8, :8].reshape(-1, 3), img[:8, -8:].reshape(-1, 3),
                              img[-8:, :8].reshape(-1, 3), img[-8:, -8:].reshape(-1, 3)])
    bg = np.median(corners, axis=0)
    print("fundo: RGB {}".format(tuple(int(c) for c in bg)))
    mask = np.abs(img - bg).max(axis=2) > BG_TOL

    # --- separar as 3 figuras por colunas vazias -------------------------
    col_has = mask.any(axis=0)
    runs, start = [], None
    for x in range(w):
        if col_has[x] and start is None:
            start = x
        elif not col_has[x] and start is not None:
            if x - start > w * 0.02:          # ignora respingo
                runs.append((start, x - 1))
            start = None
    if start is not None:
        runs.append((start, w - 1))

    print("\nfiguras detectadas: {}".format(len(runs)))
    if len(runs) != 3:
        print("  !! o crop.py espera exatamente 3 colunas de figura")

    nomes = ["frente", "perfil", "costas"]
    figs = []
    for i, (x0, x1) in enumerate(runs):
        sub = mask[:, x0:x1 + 1]
        rows = np.flatnonzero(sub.any(axis=1))
        y0, y1 = int(rows[0]), int(rows[-1])
        figs.append(dict(nome=nomes[i] if i < 3 else str(i),
                         x0=x0, x1=x1, y0=y0, y1=y1, alt=y1 - y0 + 1, sub=sub))
        print("  {:7s} x {:4d}-{:4d}  y {:4d}-{:4d}  altura {:4d} px".format(
            figs[-1]["nome"], x0, x1, y0, y1, figs[-1]["alt"]))

    # --- alinhamento e escala -------------------------------------------
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

    # --- larguras da vista FRONTAL, em fracao da altura da figura --------
    f = figs[0]
    alt = f["alt"]

    def largura_em(frac):
        y = f["y0"] + int(frac * alt)
        cols = np.flatnonzero(f["sub"][y])
        return (cols[-1] - cols[0] + 1) if cols.size else 0

    def largura_max(a, b):
        return max(largura_em(t) for t in np.arange(a, b, 0.004))

    def largura_min(a, b):
        vals = [largura_em(t) for t in np.arange(a, b, 0.004)]
        return min(v for v in vals if v)

    print("\nVISTA FRONTAL - larguras (% da altura da figura)")
    # Faixas em fracao da altura total, com a cabeca em 0. Os bracos em A-pose
    # entram na silhueta (limitacao herdada do measure.py), entao ombro e
    # quadril sao medidos onde o braco AINDA nao chegou / JA passou.
    for rot, (a, b) in [("ombros   0,18-0,24", (0.18, 0.24)),
                        ("cintura  0,40-0,48", (0.40, 0.48)),
                        ("quadril  0,50-0,56", (0.50, 0.56))]:
        val = largura_min(a, b) if "cintura" in rot else largura_max(a, b)
        print("  {}: {:4d} px = {:.1f}% da altura".format(rot, val, 100.0 * val / alt))

    # --- tecido preto ----------------------------------------------------
    print("\nROUPA PRETA na vista frontal (fracao da altura, 0 = topo da cabeca)")
    sub_img = img[:, f["x0"]:f["x1"] + 1]
    dark = (sub_img.max(axis=2) < DARK_MAX) & f["sub"]
    for y in range(f["y0"], f["y1"] + 1):
        pass
    linhas = []
    for y in range(f["y0"], f["y1"] + 1):
        n = int(dark[y].sum())
        larg = int(f["sub"][y].sum())
        linhas.append(n / larg if larg else 0.0)
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


if __name__ == "__main__":
    main(sys.argv[1])
