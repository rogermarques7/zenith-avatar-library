# -*- coding: utf-8 -*-
"""Costura do ombro_ab2.py: linhas = estado (base, +1, -1), colunas = vistas;
bloco A (entregue) a esquerda, bloco B (proposta) a direita.
    python qa/probe/sondas/ombro_ab2_folha.py DIR [titulo]"""
import os
import sys
from PIL import Image, ImageDraw

d = sys.argv[1]
tit = sys.argv[2] if len(sys.argv) > 2 else ""
V = ["frente", "tresq", "lado", "costas"]
E = ["base", "+1", "-1"]
esc = 0.42
im0 = Image.open(os.path.join(d, "A_base_frente.png"))
w, h = int(im0.width * esc), int(im0.height * esc)
fx, gap = 18, 12
W = 2 * len(V) * w + gap
o = Image.new("RGB", (W, fx + len(E) * (h + fx)), (20, 20, 22))
dr = ImageDraw.Draw(o)
dr.text((6, 3), "A = entregue   |   B = proposta   " + tit, fill=(230, 230, 230))
for li, e in enumerate(E):
    y = fx + li * (h + fx)
    for bi, tag in enumerate(("A", "B")):
        x0 = bi * (len(V) * w + gap)
        dr.text((x0 + 6, y + 3), "{} influence {}".format(tag, e), fill=(230, 230, 120))
        for ci, v in enumerate(V):
            p = os.path.join(d, "{}_{}_{}.png".format(tag, e, v))
            if os.path.exists(p):
                o.paste(Image.open(p).convert("RGB").resize((w, h)), (x0 + ci * w, y + fx))
o.save(os.path.join(d, "_folha.png"))
print(os.path.join(d, "_folha.png"), o.size)
