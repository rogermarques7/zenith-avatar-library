# -*- coding: utf-8 -*-
"""Costura os PNGs do ombro_mapa.py (--key all) numa folha: uma linha por
shape key, frente | costas | lado.  python qa/probe/sondas/ombro_mosaico.py DIR [escala]"""
import json, os, sys
from PIL import Image, ImageDraw
d = sys.argv[1]
esc = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
res = json.load(open(os.path.join(d, "resumo_all.json")))
V = ["frente", "costas", "lado"]
ims = []
for r in res:
    ims.append([Image.open(os.path.join(d, "{}_{}.png".format(r["key"], v))).convert("RGB") for v in V])
w0, h0 = ims[0][0].size
w0, h0 = int(w0 * esc), int(h0 * esc)
cols = 2  # dois shape keys por linha
o = Image.new("RGB", (w0 * 3 * cols, h0 * ((len(ims) + cols - 1) // cols)), (40, 40, 40))
dr = ImageDraw.Draw(o)
for i, trio in enumerate(ims):
    x0, y0 = (i % cols) * 3 * w0, (i // cols) * h0
    for j, im in enumerate(trio):
        o.paste(im.resize((w0, h0)), (x0 + j * w0, y0))
    dr.text((x0 + 6, y0 + 6), res[i]["key"], fill=(255, 255, 255))
o.save(os.path.join(d, "_todos.png"))
print(os.path.join(d, "_todos.png"), o.size)
