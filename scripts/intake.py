#!/usr/bin/env python3
"""
intake.py - Traz a folha de 3 vistas do Downloads para 00_input/sheets/, apagando
o selo do Gemini no caminho.

Le   a imagem mais recente de Downloads (ou --from CAMINHO)
Gera 00_input/sheets/{id}_sheet.png

POR QUE ESTE SCRIPT EXISTE
    O humano gera a folha no ChatGPT/Gemini e ela cai em Downloads. Renomear,
    mover e apagar o selo a mao e trabalho manual que o pipeline pode fazer -
    e o selo, se passar, chega na Meshy como mancha sobre o fundo liso. O
    crop.py NAO acusa: o selo cai dentro da coluna de uma das vistas em vez de
    virar uma 4a figura (CHARACTER_BIBLE §5c item 8).

O SELO
    O Gemini carimba uma estrela de 4 pontas (SynthID visivel) no canto
    inferior direito. O script acha qualquer blob compacto e ISOLADO do corpo
    naquele quadrante e cobre com um retalho de fundo limpo copiado da
    vizinhanca - preserva o grao do fundo, que uma cor chapada nao preserva.
    Folha do ChatGPT nao tem selo: o script simplesmente nao acha nada e segue.

USO
    python scripts/intake.py zen_m_b06j_d3
    python scripts/intake.py zen_m_b06j_d3 --check          # so relata, nao grava
    python scripts/intake.py zen_m_b06j_d3 --from C:\\...\\x.png
    python scripts/intake.py zen_m_b06j_d3 --force          # sobrescreve folha existente

Depois: python scripts/crop.py {id}
"""

import os
import sys
import glob
import shutil
import argparse
import numpy as np
from PIL import Image

# --- parametros -----------------------------------------------------------
FG_THRESHOLD  = 18.0    # mesmo piso do crop.py (soma dos canais)
SEAL_MIN_PX   = 15      # menor lado plausivel do selo
SEAL_MAX_PX   = 300     # maior lado plausivel
SEAL_MIN_FILL = 0.20    # blob compacto: area/bbox. Estrela cheia da ~0,45
SEAL_QUADRANT = (0.55, 0.55)   # procura em x> e y> desta fracao do canvas
SEAL_LIGHTER  = 6       # o selo e MAIS CLARO que o fundo, em TODOS os canais
SEAL_ISOLATION = 20     # px de fundo limpo exigidos ao redor do selo
PATCH_PAD     = 5       # folga ao redor do selo, em px
RESIDUE_MAX   = 6       # pixels acima do limiar aceitos apos apagar
SHEET_EXTS    = (".png", ".jpg", ".jpeg", ".webp")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def die(msg, code=1):
    sys.stderr.write("\n[ERRO] " + msg + "\n")
    sys.exit(code)


def newest_download():
    """Imagem mais recente na pasta Downloads do usuario."""
    dl = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.isdir(dl):
        die("pasta Downloads nao encontrada: {}".format(dl))
    cands = [p for p in glob.glob(os.path.join(dl, "*"))
             if p.lower().endswith(SHEET_EXTS)]
    if not cands:
        die("nenhuma imagem em {}".format(dl))
    return max(cands, key=os.path.getmtime)


def foreground_mask(arr):
    """Mascara de 'nao e fundo', com o limiar adaptativo do crop.py."""
    border = np.concatenate([arr[0, :, :], arr[-1, :, :], arr[:, 0, :], arr[:, -1, :]], axis=0)
    bg = np.median(border, axis=0)
    dist = np.abs(arr - bg).sum(axis=2)
    edge = np.concatenate([dist[:8, :].ravel(), dist[-8:, :].ravel(),
                           dist[:, :8].ravel(), dist[:, -8:].ravel()])
    noise = float(np.percentile(edge, 99.5))
    thr = max(FG_THRESHOLD, noise * 2.0)
    return dist, bg, thr, noise


def components(mask):
    """Rotula componentes conexos (8-conex) por runs + union-find.

    Sem scipy nesta maquina, e um label por pixel em Python seria lento demais
    numa folha de 2752x1536. Por runs sao ~milhares de iteracoes, nao milhoes.
    """
    H, W = mask.shape
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    next_label = 1
    prev_runs = []
    all_runs = []
    for y in range(H):
        row = mask[y].astype(np.int8)
        edges = np.flatnonzero(np.diff(np.concatenate(([0], row, [0]))))
        starts, ends = edges[0::2], edges[1::2] - 1
        runs = []
        for s, e in zip(starts, ends):
            lab = None
            for (ps, pe, pl) in prev_runs:
                if ps <= e + 1 and s <= pe + 1:      # 8-conex
                    if lab is None:
                        lab = find(pl)
                    else:
                        union(lab, pl)
            if lab is None:
                lab = next_label
                parent[lab] = lab
                next_label += 1
            runs.append((int(s), int(e), lab))
            all_runs.append((y, int(s), int(e), lab))
        prev_runs = runs

    boxes = {}
    for (y, s, e, lab) in all_runs:
        r = find(lab)
        b = boxes.get(r)
        n = e - s + 1
        if b is None:
            boxes[r] = [s, y, e, y, n]
        else:
            b[0] = min(b[0], s); b[1] = min(b[1], y)
            b[2] = max(b[2], e); b[3] = max(b[3], y)
            b[4] += n
    return list(boxes.values())


def find_seal(arr, bg, body, W, H):
    """Blob compacto, MAIS CLARO que o fundo e ISOLADO do corpo, no quadrante
    inferior direito.

    Nao se procura o selo na mascara de figura do crop.py: numa folha de fundo
    granulado o limiar adaptativo sobe (ruido 27 -> limiar 54) e o selo, que tem
    contraste baixo (~25), fica ABAIXO dele - enquanto pedacos do corpo se
    destacam como blobs soltos. Numa folha assim a versao anterior deste script
    ia apagar uma MAO (blob 21x59 na coluna do perfil). Dois criterios matam
    esse falso positivo de vez:

      claro   - o selo e branco sobre cinza; sombra e vinco de corpo sao mais
                escuros que o fundo, nunca mais claros em todos os canais.
      isolado - o selo pousa em fundo limpo. Pedaco de corpo tem corpo do lado.
                Isso tambem garante que o retalho de cobertura e seguro.
    """
    qx, qy = W * SEAL_QUADRANT[0], H * SEAL_QUADRANT[1]
    lighter = (arr - bg).min(axis=2) > SEAL_LIGHTER
    lighter[:int(qy), :] = False
    lighter[:, :int(qx)] = False
    cands = []
    for (x0, y0, x1, y1, area) in components(lighter):
        w, h = x1 - x0 + 1, y1 - y0 + 1
        if not (SEAL_MIN_PX <= w <= SEAL_MAX_PX and SEAL_MIN_PX <= h <= SEAL_MAX_PX):
            continue
        fill = area / float(w * h)
        if fill < SEAL_MIN_FILL:
            continue
        # Anel de fundo ao redor do blob. So o ANEL: o proprio selo costuma
        # entrar na mascara de figura (numa folha pouco ruidosa o limiar cai
        # abaixo do contraste dele), entao incluir o interior daria sempre
        # "tem corpo do lado" e nenhum selo seria achado.
        p = SEAL_ISOLATION
        ry0, rx0 = max(0, y0 - p), max(0, x0 - p)
        ring = body[ry0:y1 + 1 + p, rx0:x1 + 1 + p].copy()
        ring[y0 - ry0:y1 - ry0 + 1, x0 - rx0:x1 - rx0 + 1] = False
        if ring.any():
            continue        # tem corpo encostado: nao e selo
        cands.append((area, x0, y0, x1, y1, fill))
    if not cands:
        return None
    cands.sort(reverse=True)
    return cands[0]


def clean_patch(dist, thr, box, W):
    """Acha um retalho de fundo LIMPO do mesmo tamanho, deslocado em x."""
    x0, y0, x1, y1 = box
    w = x1 - x0 + 1
    for step in range(w + 8, W, 12):
        for dx in (step, -step):
            sx0, sx1 = x0 + dx, x1 + dx
            if sx0 < 0 or sx1 >= W:
                continue
            if dist[y0:y1 + 1, sx0:sx1 + 1].max() <= thr:
                return dx
    return None


def main():
    ap = argparse.ArgumentParser(description="Traz a folha do Downloads e apaga o selo.")
    ap.add_argument("id", help="ID do arquetipo, ex.: zen_m_b06j_d3")
    ap.add_argument("--from", dest="src", default=None, help="caminho da folha (default: mais recente em Downloads)")
    ap.add_argument("--check", action="store_true", help="so relata, nao grava")
    ap.add_argument("--force", action="store_true", help="sobrescreve folha ja existente")
    ap.add_argument("--keep-seal", action="store_true", help="nao apaga o selo (folha sem selo)")
    a = ap.parse_args()

    root = repo_root()
    src = a.src or newest_download()
    if not os.path.isfile(src):
        die("arquivo nao encontrado: {}".format(src))
    dst = os.path.join(root, "00_input", "sheets", a.id + "_sheet.png")
    if os.path.exists(dst) and not a.force and not a.check:
        die("ja existe {} - use --force para sobrescrever.\n"
            "       (folha aprovada nao se substitui: gere um ID novo)".format(
                os.path.relpath(dst, root)))

    img = Image.open(src).convert("RGB")
    W, H = img.size
    arr = np.asarray(img).astype(np.float32)
    dist, bg, thr, noise = foreground_mask(arr)
    mask = dist > thr

    print("origem: {}".format(src))
    print("        {}x{}  fundo RGB {}  (ruido {:.1f} -> limiar {:.1f})".format(
        W, H, bg.round(1).tolist(), noise, thr))

    out = np.asarray(img).copy()
    if a.keep_seal:
        print("selo  : --keep-seal, nada apagado")
    else:
        seal = find_seal(arr, bg, mask, W, H)
        if seal is None:
            print("selo  : nenhum encontrado (folha do ChatGPT, ou selo ausente)")
        else:
            area, x0, y0, x1, y1, fill = seal
            print("selo  : x=[{}..{}] y=[{}..{}]  {}x{}px  area={}  preench.={:.2f}".format(
                x0, x1, y0, y1, x1 - x0 + 1, y1 - y0 + 1, area, fill))
            bx0, by0 = max(0, x0 - PATCH_PAD), max(0, y0 - PATCH_PAD)
            bx1, by1 = min(W - 1, x1 + PATCH_PAD), min(H - 1, y1 + PATCH_PAD)
            dx = clean_patch(dist, thr, (bx0, by0, bx1, by1), W)
            if dx is None:
                die("nao achei fundo limpo para cobrir o selo - apagar a mao.")
            out[by0:by1 + 1, bx0:bx1 + 1] = out[by0:by1 + 1, bx0 + dx:bx1 + dx + 1]
            print("        coberto com retalho de fundo dx={:+d}px".format(dx))
            # Confere o residuo pelo MESMO criterio que achou o selo (mais claro
            # que o fundo). Usar o limiar do crop.py aqui daria zero de graca
            # justamente nas folhas em que o selo passa por baixo dele.
            reg = out[by0:by1 + 1, bx0:bx1 + 1].astype(np.float32)
            res = int(((reg - bg).min(axis=2) > SEAL_LIGHTER).sum())
            print("        residuo: {} px mais claros que o fundo (aceito <= {})".format(
                res, RESIDUE_MAX))
            if res > RESIDUE_MAX:
                die("residuo alto - o retalho pegou corpo. Conferir a mao.")

    if a.check:
        print("\n--check: nada gravado.")
        return

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    Image.fromarray(out).save(dst)
    print("\n-> {}".format(os.path.relpath(dst, root)))
    print("Proximo: python scripts/crop.py {}".format(a.id))


if __name__ == "__main__":
    main()
