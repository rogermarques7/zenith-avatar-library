"""Tira de contato SO da regiao da faixa, os 37 lado a lado.

A folha de contato inteira nao serve para julgar a faixa: no corpo inteiro a
banda tem 40 px de altura e o defeito que se procura - a peca atravessando o
braco - mede 2 ou 3 faces. Ja passou despercebido assim uma vez.

Aqui cada avatar entra so com a faixa de altura da banda, ampliado, com o nome
gravado. Um passe do olho responde "atravessa braco em algum?" nos 37.

    python qa/probe/sondas/_tira_faixa.py [--vista 0_frente] [--lo 0.13] [--hi 0.34]
"""
import argparse
import glob
import os

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
ap = argparse.ArgumentParser()
ap.add_argument("--vista", default="0_frente")
ap.add_argument("--lo", type=float, default=0.13)
ap.add_argument("--hi", type=float, default=0.34)
ap.add_argument("--cols", type=int, default=5)
ap.add_argument("--larg", type=int, default=380)
ap.add_argument("--pad", default="zen_f_*")
ap.add_argument("--out", default="_tira_faixa.png")
a = ap.parse_args()

ids = sorted(os.path.basename(d) for d in
             glob.glob(os.path.join(ROOT, "qa", "shorts", a.pad))
             if os.path.isfile(os.path.join(d, a.vista + ".png")))

tiles = []
for aid in ids:
    im = Image.open(os.path.join(ROOT, "qa", "shorts", aid,
                                 a.vista + ".png")).convert("RGB")
    im = im.crop((0, int(a.lo * im.height), im.width, int(a.hi * im.height)))
    h = max(1, int(im.height * a.larg / im.width))
    im = im.resize((a.larg, h), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.text((6, 4), aid.replace("zen_f_", ""), fill=(255, 240, 120))
    tiles.append(im)

if not tiles:
    raise SystemExit("nenhum render em qa/shorts/%s/%s.png" % (a.pad, a.vista))
tw, th = tiles[0].size
rows = (len(tiles) + a.cols - 1) // a.cols
folha = Image.new("RGB", (a.cols * tw, rows * th), (14, 14, 18))
for k, t in enumerate(tiles):
    folha.paste(t, ((k % a.cols) * tw, (k // a.cols) * th))
out = os.path.join(ROOT, "qa", "shorts", a.out)
folha.save(out)
print("%s  %d avatares  %dx%d" % (out, len(tiles), folha.width, folha.height))
