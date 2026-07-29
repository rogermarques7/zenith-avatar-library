#!/usr/bin/env python3
"""
crop.py - Recorta a folha de 3 vistas em frente / perfil / costas.

Le  00_input/sheets/{m|f}/{id}_sheet.png
Gera 00_input/references/{m|f}/{id}/{id}_ref_front.png
     (e _ref_side.png, _ref_back.png)

A folha do ChatGPT tem 3 vistas do MESMO personagem lado a lado, na ordem
FRENTE | PERFIL | COSTAS, sobre fundo cinza liso. Este script separa as tres
figuras por deteccao de fundo (mediana das bordas) - o MESMO metodo que o
process.py usa para segmentar o short -, recorta cada uma com margem uniforme
e reamostra para altura canonica. Reproduzivel nas 32 folhas: sem recorte a mao.

USO
    python scripts/crop.py zen_m_b02_d3
    python scripts/crop.py zen_m_b02_d3 --check   # so mede, nao grava

Precondicao: a folha tem EXATAMENTE 3 figuras bem separadas. Se detectar outro
numero, aborta - folha com espacamento irregular deve ser regerada, nao
compensada no recorte (ver runbook, Fase 4).
"""

import os
import sys
import argparse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zenith_paths as zp                                          # noqa: E402

# --- parametros de recorte (ajustar aqui) ---------------------------------
TARGET_H     = 1200     # altura final de cada vista, em pixels (casa com a mae)
PAD_X_FRAC   = 0.08     # margem lateral = 8% da largura da figura
PAD_Y_FRAC   = 0.05     # margem vertical = 5% da altura da figura
FG_THRESHOLD = 18.0     # distancia ao fundo (soma dos canais) para ser figura
COL_GAP_FRAC = 0.02     # gap minimo entre vistas = 2% da largura do canvas
MIN_SEG_FRAC = 0.03     # segmento de coluna valido = > 3% da largura do canvas
# Uma linha/coluna so conta como figura se tiver ESTE tanto de pixels de frente.
# Sem isso, um punhado de pixels de ruido no fundo (folhas do Gemini tem o fundo
# mais granulado que as do ChatGPT) estica a bbox ate a borda do canvas: a figura
# sai reamostrada menor e, pior, a "variacao de altura entre as vistas" passa a
# medir o canvas em vez do corpo -- justo a validacao que o pipeline nao consegue
# refazer depois (CHARACTER_BIBLE §5b item 6). Achado na folha zen_m_b06i_d3.
MIN_LINE_FRAC = 0.005   # 0,5% da dimensao perpendicular
MIN_LINE_PX   = 3       # piso absoluto, para folhas pequenas

VIEW_NAMES = ["front", "side", "back"]   # ordem da folha: FRENTE | PERFIL | COSTAS


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def die(msg, code=1):
    sys.stderr.write("\n[ERRO] " + msg + "\n")
    sys.exit(code)


def min_px(n):
    """Quantos pixels de frente uma linha/coluna precisa ter para contar."""
    return max(MIN_LINE_PX, int(n * MIN_LINE_FRAC))


def detect_segments(figure, W):
    """Blocos contiguos de colunas que contem figura (uma por vista)."""
    col_has = figure.sum(axis=0) >= min_px(figure.shape[0])
    cols = np.where(col_has)[0]
    if cols.size == 0:
        die("nenhuma figura detectada na folha (imagem vazia ou fundo nao uniforme).")
    gap = int(W * COL_GAP_FRAC)
    segs = []
    start = prev = cols[0]
    for c in cols[1:]:
        if c - prev > gap:
            segs.append((start, prev)); start = c
        prev = c
    segs.append((start, prev))
    return [(s, e) for (s, e) in segs if (e - s) > W * MIN_SEG_FRAC]


def figure_bbox(figure, x0, x1):
    """bbox da figura dentro da faixa de colunas [x0, x1]."""
    sub = figure[:, x0:x1 + 1]
    rows = np.where(sub.sum(axis=1) >= min_px(sub.shape[1]))[0]
    if rows.size == 0:
        die("vista em x=[{}..{}] ficou vazia apos o filtro de ruido.".format(x0, x1))
    return x0, int(rows.min()), x1, int(rows.max())


def crop_one(img_rgb, bg, box, W, H):
    """Recorta com margem uniforme; onde a margem ultrapassa o canvas, preenche
    com a cor de fundo, para que TODAS as vistas tenham a mesma margem exata
    independente de encostarem na borda da folha."""
    fx0, fy0, fx1, fy1 = box
    fw, fh = fx1 - fx0, fy1 - fy0
    px = int(round(fw * PAD_X_FRAC))
    py = int(round(fh * PAD_Y_FRAC))
    ox0, oy0, ox1, oy1 = fx0 - px, fy0 - py, fx1 + px, fy1 + py
    out_w, out_h = ox1 - ox0, oy1 - oy0
    canvas = np.empty((out_h, out_w, 3), dtype=np.uint8)
    canvas[:, :] = bg.astype(np.uint8)
    # regiao de intersecao com a folha real
    sx0, sy0 = max(ox0, 0), max(oy0, 0)
    sx1, sy1 = min(ox1, W), min(oy1, H)
    canvas[sy0 - oy0:sy1 - oy0, sx0 - ox0:sx1 - ox0] = img_rgb[sy0:sy1, sx0:sx1]
    im = Image.fromarray(canvas)
    scale = TARGET_H / out_h
    im = im.resize((max(1, int(round(out_w * scale))), TARGET_H), Image.LANCZOS)
    return im


def main():
    ap = argparse.ArgumentParser(description="Recorta a folha de 3 vistas.")
    ap.add_argument("id", help="ID do arquetipo, ex.: zen_m_b02_d3")
    ap.add_argument("--check", action="store_true", help="so mede, nao grava")
    a = ap.parse_args()

    root = repo_root()
    sheet = zp.sheet_path(root, a.id)
    if not os.path.isfile(sheet):
        die("folha nao encontrada: {}".format(os.path.relpath(sheet, root)))

    img = Image.open(sheet).convert("RGB")
    W, H = img.size
    arr = np.asarray(img).astype(np.float32)
    border = np.concatenate([arr[0, :, :], arr[-1, :, :], arr[:, 0, :], arr[:, -1, :]], axis=0)
    bg = np.median(border, axis=0)
    dist = np.abs(arr - bg).sum(axis=2)
    # Limiar ADAPTATIVO. O FG_THRESHOLD fixo foi calibrado nas folhas do ChatGPT;
    # as do Gemini tem o fundo mais granulado e o ruido sozinho o ultrapassa,
    # esticando a bbox ate a borda do canvas. Mede-se o piso de ruido numa faixa
    # de borda (sempre fundo) e exige-se folga sobre ele.
    edge = np.concatenate([dist[:8, :].ravel(), dist[-8:, :].ravel(),
                           dist[:, :8].ravel(), dist[:, -8:].ravel()])
    noise = float(np.percentile(edge, 99.5))
    thr = max(FG_THRESHOLD, noise * 2.0)
    figure = dist > thr

    segs = detect_segments(figure, W)
    print("folha : {}  ({}x{})".format(os.path.relpath(sheet, root), W, H))
    print("fundo : RGB {}  (ruido {:.1f} -> limiar {:.1f})".format(
        bg.round(1).tolist(), noise, thr))
    print("vistas: {} detectadas".format(len(segs)))
    if len(segs) != 3:
        die("esperava 3 vistas, achei {}. Folha com espacamento irregular -> "
            "regerar no ChatGPT, nao compensar no recorte.".format(len(segs)))

    boxes = [figure_bbox(figure, x0, x1) for (x0, x1) in segs]
    heights = [b[3] - b[1] for b in boxes]
    hmean = float(np.mean(heights))
    spread = (max(heights) - min(heights)) / hmean * 100.0
    for name, (x0, x1), b in zip(VIEW_NAMES, segs, boxes):
        print("  {:<5} x=[{:4d}..{:4d}] topo={:4d} base={:4d} altura={:4d}px".format(
            name, b[0], b[2], b[1], b[3], b[3] - b[1]))
    print("altura: variacao {:.2f}% entre as vistas (media {:.0f}px)".format(spread, hmean))
    if spread > 2.0:
        print("  AVISO: variacao de altura > 2% - conferir alinhamento da folha.")

    if a.check:
        print("\n--check: nada gravado.")
        return

    outdir = zp.refs_dir(root, a.id)
    os.makedirs(outdir, exist_ok=True)
    img_u8 = np.asarray(img)
    for name, box in zip(VIEW_NAMES, boxes):
        im = crop_one(img_u8, bg, box, W, H)
        out = os.path.join(outdir, "{}_ref_{}.png".format(a.id, name))
        im.save(out)
        print("  -> {}  ({}x{})".format(os.path.relpath(out, root), im.size[0], im.size[1]))
    print("\nOK: 3 vistas gravadas em {}".format(os.path.relpath(outdir, root)))


if __name__ == "__main__":
    main()
