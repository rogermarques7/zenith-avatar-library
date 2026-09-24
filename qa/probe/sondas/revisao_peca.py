# -*- coding: utf-8 -*-
"""revisao_peca.py - folha de contato da ROUPA INTEIRA no GLB entregue.

    python qa/probe/sondas/revisao_peca.py zen_f_b08_d2 [outro ...]
    python qa/probe/sondas/revisao_peca.py --todos      # o acervo do shorts_map
    python qa/probe/sondas/revisao_peca.py --mosaico    # grade de frentes, 6 por imagem

Saida: `qa/revisao/{id}/folha.png` e `qa/revisao/_mosaico_{n}.png`.

POR QUE NAO BASTA O `peca_folha.py`
-----------------------------------
Ele enquadra o QUADRIL, que e onde mora o short. A faixa feminina mora em 0.72
da altura e simplesmente nao aparece naquele corte - e a listra branca do topo
da faixa foi o defeito que passou por 37 avatares na sessao 26. Uma revisao que
so olha o quadril repete o mesmo erro de "julgar numa imagem que nao mostra o
defeito procurado" (LICOES.md 1.1), so que do outro lado do corpo.

Aqui a folha tem DUAS linhas: quadril (4 azimutes) e, no feminino, faixa (3).
Quem renderiza continua sendo o `render_dist.py` - aluminio + `zenith_env.hdr`,
no arquivo que o usuario baixa -, porque veredito de PINTURA nao se da no clay
do `--fit` (LICOES.md 4.5c).

O MOSAICO E PARA VARRER, NAO PARA APROVAR
-----------------------------------------
Com 103 corpos, abrir 103 folhas para achar os poucos tortos e caro. O mosaico
poe seis frentes lado a lado so para dizer ONDE olhar de perto; o veredito sai
sempre da folha do avatar, que tem resolucao para uma tira de 1 cm.
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
VISTAS_COS = [
    ["c0_frente", 0.42, 2.9, 0, 85],
    ["c1_tresquartos", 0.42, 2.9, 40, 85],
    ["c2_lado", 0.42, 2.9, 90, 85],
    ["c3_costas", 0.42, 2.9, 180, 85],
]
VISTAS_FAIXA = [
    ["f0_frente", 0.70, 2.6, 0, 85],
    ["f1_tresquartos", 0.70, 2.6, 40, 85],
    ["f2_costas", 0.70, 2.6, 180, 85],
]


def _render(root, aid, blender, vistas, out, glb=None):
    """`glb` explicito serve a PREVIA (qa/preview/), que nao esta em 03_dist.
    O enquadramento tem de ser o mesmo dos dois lados, senao a previa nao
    antecipa o veredito - por isso ela reusa esta funcao em vez de copiar."""
    if glb is None:
        ver, glb = _zp.dist_glb_current(root, aid)
    else:
        ver = "previa"
    if glb is None:
        return None, None
    hdr = os.path.join(root, "03_dist", "env", "zenith_env.hdr")
    sonda = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "render_dist.py")
    env = dict(os.environ)
    env["VISTAS"] = json.dumps(vistas)
    cmd = [blender, "-b", "-P", sonda, "--", glb, out, hdr]
    r = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL)
    if r.returncode != 0:
        return None, None
    return ver, glb


def folha(root, aid, blender, esc=0.42, glb=None, out=None):
    out = out or os.path.join(root, "qa", "revisao", aid)
    os.makedirs(out, exist_ok=True)
    vistas = list(VISTAS_COS)
    if aid.startswith("zen_f_"):
        vistas += VISTAS_FAIXA
    ver, glb = _render(root, aid, blender, vistas, out, glb=glb)
    if glb is None:
        print("  SEM GLB  " + aid)
        return None

    tw, th = int(900 * esc), int(1200 * esc)
    linhas = [VISTAS_COS] + ([VISTAS_FAIXA] if aid.startswith("zen_f_") else [])
    cols = max(len(l) for l in linhas)
    faixa = 22
    sheet = Image.new("RGB", (tw * cols, faixa + th * len(linhas)), (16, 16, 18))
    d = ImageDraw.Draw(sheet)
    d.text((6, 6), "{}   {}".format(aid, os.path.basename(glb)),
           fill=(215, 215, 220))
    for li, linha in enumerate(linhas):
        for ci, v in enumerate(linha):
            p = os.path.join(out, v[0] + ".png")
            if not os.path.isfile(p):
                continue
            im = Image.open(p).convert("RGB")
            sheet.paste(im.resize((tw, th), Image.LANCZOS),
                        (ci * tw, faixa + li * th))
    dest = os.path.join(out, "folha.png")
    sheet.save(dest)
    return dest


def mosaico(root, ids, por_imagem=6, esc=0.40):
    """Grade das frentes ja renderizadas. Nao chama o Blender."""
    tw, th = int(900 * esc), int(1200 * esc)
    faixa = 20
    feitos = []
    for k in range(0, len(ids), por_imagem):
        lote = ids[k:k + por_imagem]
        # Lote so de masculinos nao tem a linha da faixa, e linha vazia num
        # mosaico e metade da imagem gasta sem informacao nenhuma.
        linhas = ["c0_frente"]
        if any(a.startswith("zen_f_") for a in lote):
            linhas.append("f0_frente")
        sheet = Image.new("RGB", (tw * len(lote), faixa + th * len(linhas)),
                          (16, 16, 18))
        d = ImageDraw.Draw(sheet)
        for ci, aid in enumerate(lote):
            base = os.path.join(root, "qa", "revisao", aid)
            d.text((ci * tw + 6, 6), aid, fill=(215, 215, 220))
            for li, nome in enumerate(linhas):
                p = os.path.join(base, nome + ".png")
                if not os.path.isfile(p):
                    continue
                im = Image.open(p).convert("RGB")
                sheet.paste(im.resize((tw, th), Image.LANCZOS),
                            (ci * tw, faixa + li * th))
        dest = os.path.join(root, "qa", "revisao",
                            "_mosaico_{:02d}.png".format(k // por_imagem + 1))
        sheet.save(dest)
        feitos.append(dest)
    return feitos


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    root = mt.repo_root()
    with open(os.path.join(root, "config", "shorts_map.json"),
              encoding="utf-8") as f:
        acervo = sorted(json.load(f).keys())

    if args[0] == "--mosaico":
        ids = args[1:] or acervo
        for p in mosaico(root, ids):
            print(p)
        return

    ids = acervo if args[0] == "--todos" else args
    blender = mt.find_blender()
    for aid in ids:
        p = folha(root, aid, blender)
        if p:
            print(p)


if __name__ == "__main__":
    main()
