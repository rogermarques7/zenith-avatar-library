# -*- coding: utf-8 -*-
"""Costura do pescoco_ab.py: linhas = estados, colunas = vistas; A a esquerda, B a direita.
    python qa/probe/sondas/pescoco_ab_folha.py DIR "titulo" "rotA1,rotA2,.." "rotB1,.." """
import os
import sys
from PIL import Image, ImageDraw

d, tit = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else ""
ra = ["base"] + (sys.argv[3].split(";") if len(sys.argv) > 3 else [])
rb = ["base"] + (sys.argv[4].split(";") if len(sys.argv) > 4 else [])
V = ["frente", "tresq", "lado", "costas"]
E = ["base"] + ["e{}".format(i) for i in range(len(ra) - 1)]
esc = 0.40
im0 = Image.open(os.path.join(d, "A_base_frente.png"))
w, h = int(im0.width * esc), int(im0.height * esc)
fx, gap = 16, 14
W = 2 * len(V) * w + gap
o = Image.new("RGB", (W, fx + len(E) * (h + fx)), (20, 20, 22))
dr = ImageDraw.Draw(o)
dr.text((6, 2), "A = entregue (cilindro)   |   B = proposta (campo por tipo)   " + tit, fill=(230, 230, 230))
for li, e in enumerate(E):
    y = fx + li * (h + fx)
    for bi, (tag, rot) in enumerate((("A", ra), ("B", rb))):
        x0 = bi * (len(V) * w + gap)
        dr.text((x0 + 6, y + 2), "{} {}".format(tag, rot[li] if li < len(rot) else e), fill=(230, 230, 120))
        for ci, v in enumerate(V):
            p = os.path.join(d, "{}_{}_{}.png".format(tag, e, v))
            if os.path.exists(p):
                o.paste(Image.open(p).convert("RGB").resize((w, h)), (x0 + ci * w, y + fx))
o.save(os.path.join(d, "_folha.png"))
print(os.path.join(d, "_folha.png"), o.size)
