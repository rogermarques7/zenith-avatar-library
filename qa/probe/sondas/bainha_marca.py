#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bainha_marca.py - desenha as marcas de 1 px nos renders do bainha_rasante.

    python qa/probe/sondas/bainha_marca.py zen_m_b09h_d1 [...]

Roda no Python do SISTEMA (o do Blender nao tem PIL). Le o marcas.json que a
sonda gravou e risca cada altura candidata com uma linha de 1 px, deixando
metade da largura LIMPA - a marca aponta sem tapar, que era o defeito da
primeira versao (toro em 3D comendo o relevo que a sonda existe para mostrar).
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
BASE = os.path.join(ROOT, "qa", "revisao", "_hem")


def uma(aid):
    d = os.path.join(BASE, aid)
    with open(os.path.join(d, "marcas.json"), encoding="utf-8") as f:
        mk = json.load(f)
    for nome in ("frente", "obliqua", "lado", "costas"):
        p = os.path.join(d, "rasante_" + nome + ".png")
        if not os.path.isfile(p):
            continue
        im = np.asarray(Image.open(p).convert("RGB")).copy()
        h, w = im.shape[:2]
        for i, (rot, (y, cor)) in enumerate(sorted(mk["marcas"].items())):
            if not (0 <= y < h):
                continue
            # so o terco esquerdo e o terco direito: o meio fica limpo
            im[y, :w // 5] = cor
            im[y, -w // 5:] = cor
            # um tracinho vertical de 9 px na ponta, para achar a linha
            x = w // 5 + 4 + i * 10
            im[max(0, y - 4):min(h, y + 5), x:x + 2] = cor
        Image.fromarray(im).save(os.path.join(d, "marcado_" + nome + ".png"))
    print("{}: mapa={:.4f} folha={} -> {}".format(
        aid, mk["hem_mapa_zh"],
        "-" if mk["hem_folha_zh"] is None else "%.4f" % mk["hem_folha_zh"], d))


for _a in sys.argv[1:]:
    uma(_a)
