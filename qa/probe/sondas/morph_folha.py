# -*- coding: utf-8 -*-
"""Folha de contato do morph: BASE x TODOS NO MAXIMO x TODOS NO MINIMO.

    python qa/probe/sondas/morph_folha.py zen_m_b02_d1

Le o `config/morph_map.json` (que ja descreve o GLB corrente), renderiza os
tres estados em quatro vistas com o `morph_render_ab.py` e costura tudo numa
imagem so - `qa/morph/{id}/folha.png`.

POR QUE UMA FOLHA E NAO 12 ARQUIVOS
-----------------------------------
O veredito e comparativo: defeito de morph aparece como DIFERENCA contra a
base (membrana na axila, vinco na virilha, degrau no deltoide, barriga funda
demais de perfil). Olhar 12 PNGs em sequencia perde a comparacao; a folha
poe base/max/min na mesma linha, na mesma vista.

O estado combinado e o que importa: cada morph passou sozinho na varredura do
`--fit`, e a colisao que derrubou o projeto anterior so aparecia com todos
ligados juntos.
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

VISTAS = [
    ["corpo",       [0, 0, 0.95], 3.2,  0],
    ["perfil",      [0, 0, 0.95], 3.2, 90],   # a profundidade da barriga mora aqui
    ["tresquartos", [0, 0, 1.15], 2.2, 35],
    ["axila",       [0.19, 0, 1.24], 0.55, 30],
]


def main():
    aid = sys.argv[1]
    root = mt.repo_root()
    ver, glb = _zp.dist_glb_current(root, aid)
    if glb is None:
        sys.exit("sem GLB em 03_dist/glb para " + aid)

    mapa = json.load(open(os.path.join(root, "config", "morph_map.json"),
                          encoding="utf-8"))
    if aid not in mapa:
        sys.exit("{} nao esta no morph_map.json - rode morph.py --apply antes".format(aid))
    morphs = mapa[aid]["morphs"]
    keys = [m["key"] for m in morphs]
    mx = [m.get("influence_max", 0.0) for m in morphs]
    mn = [m.get("influence_min", 0.0) for m in morphs]
    # O achatamento e acoplado: acompanha o `morph_waist` e so no lado positivo.
    for i, m in enumerate(morphs):
        if m.get("couple"):
            j = keys.index(m["couple"])
            mx[i] = mx[j]
            mn[i] = 0.0

    out = os.path.join(root, "qa", "morph", aid)
    estados = [["0_base"] + [0.0] * len(keys),
               ["1_max"] + mx,
               ["2_min"] + mn]

    env = dict(os.environ)
    env["KEYS"] = json.dumps(keys)
    env["ESTADOS"] = json.dumps(estados)
    env["VISTAS"] = json.dumps(VISTAS)
    sonda = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "morph_render_ab.py")
    hdr = os.path.join(root, "03_dist", "env", "zenith_env.hdr")
    cmd = [mt.find_blender(), "--background", "--python", sonda, "--",
           "--glb", glb, "--out", out, "--hdr", hdr]
    r = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL)
    if r.returncode != 0:
        sys.exit("blender falhou")

    # --- costura ---------------------------------------------------------
    esc = 0.42
    tw, th = int(720 * esc), int(900 * esc)
    faixa = 22
    folha = Image.new("RGB", (tw * len(VISTAS), (th + faixa) * len(estados)),
                      (16, 16, 18))
    d = ImageDraw.Draw(folha)
    for li, est in enumerate(estados):
        y = li * (th + faixa)
        d.text((6, y + 6), "{}  {}".format(est[0], os.path.basename(glb)),
               fill=(210, 210, 215))
        for ci, v in enumerate(VISTAS):
            p = os.path.join(out, "%s_%s.png" % (v[0], est[0]))
            im = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
            folha.paste(im, (ci * tw, y + faixa))
    dest = os.path.join(out, "folha.png")
    folha.save(dest)
    print(dest)


if __name__ == "__main__":
    main()
