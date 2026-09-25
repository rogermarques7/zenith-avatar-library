# -*- coding: utf-8 -*-
"""top_vistas.py - a FAIXA com LENTE LONGA, no GLB entregue ou na previa.

    python qa/probe/sondas/top_vistas.py zen_f_b09i_d3 [outro ...]
    python qa/probe/sondas/top_vistas.py --previa zen_f_b09i_d3 ...
    python qa/probe/sondas/top_vistas.py --ab zen_f_b09i_d3 ...   # entregue x previa
    python qa/probe/sondas/top_vistas.py --cos --ab zen_f_b09_d2  # o quadril

Saida: `qa/revisao/_top/{id}/folha.png` (ou `_previa`, ou `_ab`).

POR QUE LENTE LONGA (sessao 39, 25/09)
-------------------------------------
Perto da silhueta lateral, 85 mm inventa defeito: o braco, mais perto da
camera, projeta o mesmo corte horizontal mais baixo e mais grosso que no tronco
(LICOES.md 4.5h). A faixa mora exatamente ali. Com 250 mm a 7 m a perspectiva
quase some e o que sobra e a tinta de verdade.

Cinco azimutes porque a quina da faixa (a borda que sobe para a axila) so
aparece de 3/4 e de lado, e o triceps so de costas e de 3/4 de costas.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import metrics as mt          # noqa: E402
import zenith_paths as _zp    # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

# [nome, alvo_zh, distancia, azimute, lente]
VISTAS_TOP = [
    ["t0_frente", 0.71, 7.0, 0, 250],
    ["t1_tresq", 0.71, 7.0, 45, 250],
    ["t2_lado", 0.71, 7.0, 90, 250],
    ["t3_tresq_costas", 0.71, 7.0, 135, 250],
    ["t4_costas", 0.71, 7.0, 180, 250],
]
# --cos: o QUADRIL, com o mesmo cuidado de lente. Nasceu na sessao 39 para os
# dois shorts que ele reprovou no testador (zen_f_b09_d2, zen_f_b11_d1).
VISTAS_COS = [
    ["c0_frente", 0.50, 7.0, 0, 250],
    ["c1_tresq", 0.50, 7.0, 45, 250],
    ["c2_lado", 0.50, 7.0, 90, 250],
    ["c3_tresq_costas", 0.50, 7.0, 135, 250],
    ["c4_costas", 0.50, 7.0, 180, 250],
]
# --baixo: o quadril visto de BAIXO (-20 graus), como o testador quando gira
VISTAS_BAIXO = [
    ["b0_frente", 0.50, 7.0, 0, 250, -20],
    ["b1_tresq", 0.50, 7.0, 45, 250, -20],
    ["b2_lado", 0.50, 7.0, 90, 250, -20],
    ["b3_tresq_costas", 0.50, 7.0, 135, 250, -20],
    ["b4_costas", 0.50, 7.0, 180, 250, -20],
]
VISTAS = VISTAS_TOP


def render(aid, blender, glb, out):
    os.makedirs(out, exist_ok=True)
    hdr = os.path.join(ROOT, "03_dist", "env", "zenith_env.hdr")
    env = dict(os.environ)
    env["VISTAS"] = json.dumps(VISTAS)
    cmd = [blender, "-b", "-P", os.path.join(HERE, "render_dist.py"), "--",
           glb, out, hdr]
    r = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL)
    return r.returncode == 0


def linha(out, tw, th):
    ims = []
    for v in VISTAS:
        p = os.path.join(out, v[0] + ".png")
        im = Image.open(p).convert("RGB") if os.path.isfile(p) else \
            Image.new("RGB", (900, 1200))
        # recorte do meio: a faixa e o braco, sem o resto do corpo
        w, h = im.size
        im = im.crop((int(w * 0.05), int(h * 0.12), int(w * 0.95), int(h * 0.70)))
        ims.append(im.resize((tw, th), Image.LANCZOS))
    return ims


def folha(aid, blender, modo):
    base = os.path.join(ROOT, "qa", "revisao", "_top", aid)
    fontes = []
    if modo in ("dist", "ab"):
        ver, glb = _zp.dist_glb_current(ROOT, aid)
        fontes.append(("entregue " + os.path.basename(glb), glb,
                       os.path.join(base, "dist")))
    if modo in ("previa", "ab"):
        glb = os.path.join(ROOT, "qa", "preview", aid + "_preview.glb")
        fontes.append(("previa", glb, os.path.join(base, "previa")))
    tw, th = 330, 290
    rot = 20
    sheet = Image.new("RGB", (tw * len(VISTAS), (rot + th) * len(fontes)),
                      (16, 16, 18))
    d = ImageDraw.Draw(sheet)
    for i, (nome, glb, out) in enumerate(fontes):
        if not os.path.isfile(glb) or not render(aid, blender, glb, out):
            print("  falhou", aid, nome)
            continue
        y = i * (rot + th)
        d.text((6, y + 4), "{}   {}".format(aid, nome), fill=(215, 215, 220))
        for j, im in enumerate(linha(out, tw, th)):
            sheet.paste(im, (j * tw, y + rot))
    dest = os.path.join(base, "folha_{}{}.png".format(
        modo, {id(VISTAS_COS): "_cos", id(VISTAS_BAIXO): "_baixo"}.get(
            id(VISTAS), "")))
    sheet.save(dest)
    return dest


def main():
    args = sys.argv[1:]
    global VISTAS
    if "--cos" in args:
        args.remove("--cos")
        VISTAS = VISTAS_COS
    if "--baixo" in args:
        args.remove("--baixo")
        VISTAS = VISTAS_BAIXO
    modo = "dist"
    if args and args[0] in ("--previa", "--ab"):
        modo = args.pop(0)[2:]
    if not args:
        sys.exit(__doc__)
    blender = mt.find_blender()
    for aid in args:
        p = folha(aid, blender, modo)
        print("  ->", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
