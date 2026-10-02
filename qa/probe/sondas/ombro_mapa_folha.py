# -*- coding: utf-8 -*-
"""Folha de LOCALIZACAO do morph_shoulder: antes x depois, varios corpos.

    python qa/probe/sondas/ombro_mapa_folha.py DIR_ANTES OUT.png ID [ID ...]

Para cada id roda o `ombro_mapa.py` num GLB de DIR_ANTES ({id}.glb ou
{id}_v*.glb - serve o backup de 03_dist) e no entregue CORRENTE (03_dist), e
poe os dois lado a lado: frente | costas | lado | cima. A pergunta desta
folha e so ONDE o campo mora - o resultado visual e o `ombro_ab2.py`.
"""
import glob
import os
import subprocess
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "scripts"))
import metrics as mt  # noqa: E402
import zenith_paths as _zp  # noqa: E402

antes, out, ids = sys.argv[1], sys.argv[2], sys.argv[3:]


def de_antes(aid):
    f = os.path.join(antes, aid + ".glb")
    return f if os.path.exists(f) else sorted(glob.glob(os.path.join(antes, aid + "_v*.glb")))[-1]


root = mt.repo_root()
sonda = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ombro_mapa.py")
V = ["frente", "costas", "lado", "cima"]
t = 190
linhas = []
for aid in ids:
    par = []
    for tag, glb in (("antes", de_antes(aid)),
                     ("depois", _zp.dist_glb_current(root, aid)[1])):
        d = os.path.join(root, "qa", "ombro", "_mapas", tag, aid)
        subprocess.run([mt.find_blender(), "-b", "-P", sonda, "--", "--id", aid, "--glb", glb,
                        "--out", d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ims = []
        for v in V:
            f = os.path.join(d, "morph_shoulder_{}.png".format(v))
            if os.path.exists(f):
                ims.append(Image.open(f).convert("RGB").resize((t, t)))
            else:                             # o GLB nao tem o shape key
                im = Image.new("RGB", (t, t), (60, 40, 40))
                ImageDraw.Draw(im).text((8, t // 2), "sem morph_shoulder", fill=(255, 200, 200))
                ims.append(im)
        par.append(ims)
    linhas.append((aid, par))
o = Image.new("RGB", (t * 8 + 10, (t + 16) * len(linhas) + 18), (30, 30, 32))
dr = ImageDraw.Draw(o)
dr.text((6, 3), "ANTES - dragona (frente costas lado cima)", fill=(240, 240, 240))
dr.text((t * 4 + 16, 3), "DEPOIS - deltoide (frente costas lado cima)", fill=(240, 240, 120))
for i, (aid, par) in enumerate(linhas):
    y = 18 + i * (t + 16)
    dr.text((6, y + 2), aid, fill=(200, 200, 200))
    for b, ims in enumerate(par):
        for j, im in enumerate(ims):
            o.paste(im, (b * (t * 4 + 10) + j * t, y + 14))
o.save(out)
print(out, o.size)
