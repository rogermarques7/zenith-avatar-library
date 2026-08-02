#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""plot_corte.py - desenha o JSON do probe_corte.py (roda no Python do sistema,
porque o Python do Blender nao tem PIL)."""
import json
import sys

from PIL import Image, ImageDraw

for path in sys.argv[1:]:
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    W, Hp = 620, 820
    y0, y1 = -0.62, 0.38
    z0, z1 = 0.18, 0.72
    img = Image.new("RGB", (W, Hp), (18, 18, 24))
    dr = ImageDraw.Draw(img)

    def px(y, zh):
        return ((y - y0) / (y1 - y0) * W, Hp - (zh - z0) / (z1 - z0) * Hp)

    for zh in [z0 + i * 0.02 for i in range(int((z1 - z0) / 0.02) + 1)]:
        _, yy = px(0, zh)
        forte = abs(zh * 100 - round(zh * 100 / 10) * 10) < 0.5
        dr.line([(0, yy), (W, yy)], fill=(60, 60, 78) if forte else (34, 34, 44))
        if forte:
            dr.text((4, yy - 11), "{:.2f}".format(zh), fill=(130, 130, 155))

    for y, zh, p in zip(d["y"], d["zh"], d["pintado"]):
        x, yy = px(y, zh)
        c = (240, 60, 55) if p else (170, 170, 186)
        dr.ellipse([x - 1.7, yy - 1.7, x + 1.7, yy + 1.7], fill=c)

    dr.text((8, 8), "{}  corte x={:+.2f}   frente = esquerda".format(d["id"], d["x"]),
            fill=(220, 220, 235))
    out = path[:-5] + ".png"
    img.save(out)
    print(out)
