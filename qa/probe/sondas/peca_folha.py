# -*- coding: utf-8 -*-
"""Folha de contato da PECA no GLB ENTREGUE - quatro vistas em volta do quadril.

    python qa/probe/sondas/peca_folha.py zen_m_b12_d1 [zen_m_b11_d2 ...]
    python qa/probe/sondas/peca_folha.py --fila        # os 7 do FILA_PECAS 2

Saida: `qa/peca/{id}/folha.png` (frente / tres-quartos / lado / costas).

POR QUE ESTE ENQUADRAMENTO, E POR QUE NAO O QA DO `--fit`
---------------------------------------------------------
O `qa/shorts/{id}/*.png` e clay de corpo inteiro: mostra geometria (ilha,
costura, regiao conexa) e esconde PINTURA - foi assim que uma listra branca
passou por 37 avatares na sessao 26 (LICOES.md 4.5c). Aqui quem renderiza e o
`render_dist.py`, com o aluminio e o `zenith_env.hdr`, no arquivo que o usuario
baixa.

E o short nao mora em 0.72 da altura como a faixa: o cos vai de 0.48 a 0.57 e a
bainha de 0.34 a 0.40. Enquadrar o quadril e o que faz uma tira de 1 cm ocupar
pixel suficiente para ser vista - e a fila dos 7 masculinos e justamente a dos
corpos mais pesados, onde a barriga cai por cima do cos e a linha deixa de ser
horizontal.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", "scripts"))
import metrics as mt          # noqa: E402
import zenith_paths as _zp    # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

# [nome, alvo_zh, distancia, azimute, lente]
VISTAS = [
    ["0_frente", 0.42, 2.9, 0, 85],
    ["1_tresquartos", 0.42, 2.9, 40, 85],
    ["2_lado", 0.42, 2.9, 90, 85],
    ["3_costas", 0.42, 2.9, 180, 85],
]

FILA = ["zen_m_b09_d1", "zen_m_b09_d2", "zen_m_b10_d1", "zen_m_b10_d2",
        "zen_m_b11_d1", "zen_m_b11_d2", "zen_m_b12_d1"]


def folha(root, aid, blender):
    ver, glb = _zp.dist_glb_current(root, aid)
    if glb is None:
        sys.exit("sem GLB em 03_dist/glb para " + aid)
    out = os.path.join(root, "qa", "peca", aid)
    os.makedirs(out, exist_ok=True)
    hdr = os.path.join(root, "03_dist", "env", "zenith_env.hdr")
    sonda = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "render_dist.py")
    env = dict(os.environ)
    env["VISTAS"] = json.dumps(VISTAS)
    cmd = [blender, "-b", "-P", sonda, "--", glb, out, hdr]
    r = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL)
    if r.returncode != 0:
        sys.exit("blender falhou em " + aid)

    esc = 0.5
    tw, th = int(900 * esc), int(1200 * esc)
    faixa = 20
    sheet = Image.new("RGB", (tw * len(VISTAS), th + faixa), (16, 16, 18))
    d = ImageDraw.Draw(sheet)
    d.text((6, 5), "{}  {}".format(aid, os.path.basename(glb)),
           fill=(210, 210, 215))
    for ci, v in enumerate(VISTAS):
        im = Image.open(os.path.join(out, v[0] + ".png")).convert("RGB")
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (ci * tw, faixa))
    dest = os.path.join(out, "folha.png")
    sheet.save(dest)
    return dest


def main():
    args = sys.argv[1:]
    ids = FILA if (args and args[0] == "--fila") else args
    if not ids:
        sys.exit(__doc__)
    root = mt.repo_root()
    blender = mt.find_blender()
    for aid in ids:
        print(folha(root, aid, blender))


if __name__ == "__main__":
    main()
