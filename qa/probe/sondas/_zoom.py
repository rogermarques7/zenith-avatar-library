"""Recorte ampliado de um render de QA. Existe porque olhar a folha de contato
nao resolve borda: serrilhado de duas ou tres faces some na miniatura e e
justamente ele que denuncia mascara mal cortada.

    python qa/probe/sondas/_zoom.py qa/shorts/ID/0_frente.png x0 y0 x1 y1 [k]
"""
import sys

from PIL import Image

p = sys.argv[1]
x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
k = int(sys.argv[6]) if len(sys.argv) > 6 else 4
im = Image.open(p).convert("RGB").crop((x0, y0, x1, y1))
im = im.resize((im.width * k, im.height * k), Image.NEAREST)
out = p.replace(".png", "_zoom.png")
im.save(out)
print(out, im.size)
