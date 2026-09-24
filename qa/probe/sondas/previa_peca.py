#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""previa_peca.py - a folha de contato da PREVIA, antes de gastar versao.

    python qa/probe/sondas/previa_peca.py zen_f_b03h_d1 [outro ...]

Faz duas coisas numa chamada:

  1. `shorts.py {id} --preview` - pinta a peca exatamente como o `--apply`
     pintaria e grava em `qa/preview/{id}_preview.glb`, SEM tocar
     `03_dist/glb/` e sem aposentar versao nenhuma;
  2. renderiza esse arquivo com aluminio + `zenith_env.hdr`, no MESMO
     enquadramento do `revisao_peca.py`.

Saida: `qa/preview/{id}/folha.png`.

--------------------------------------------------------------------------
POR QUE ISTO EXISTE (23/09, sessao 37)
--------------------------------------------------------------------------
O ciclo de conserto de peca era APLICA -> OLHA. Cada volta custava uma versao
de GLB (regra 8) mais um `morph --apply` por cima (regra 9) - e o custo nao e o
problema principal. O problema e que, sendo caro, o julgamento visual foi
empurrado para DEPOIS da entrega: eu decidia por medida e conferia por imagem
no fim, quando voltar atras ja tinha preco.

O Rogerio nomeou isso em 23/09, olhando um lote que eu tinha acabado de
entregar: *"parece que vc nao ta enxergando os corpos, ta tentando corrigir no
escuro"*. Estava certo, e a conta e simples: eu tinha medido 103 avatares e
olhado a imagem de 3.

⚠️ **O enquadramento e o mesmo do `revisao_peca.py` de proposito.** Uma previa
com outro corte nao antecipa o veredito - e a §1.10 outra vez: regua que nao
reproduz a queixa nao guia conserto nenhum. Por isso este arquivo REUSA a
funcao `folha()` de la em vez de copiar a lista de vistas.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as mt          # noqa: E402
import revisao_peca as rp     # noqa: E402


def uma(aid, blender):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "shorts.py"),
                        aid, "--preview"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    saida = r.stdout.decode("utf-8", "replace")
    linha = [l for l in saida.splitlines() if l.startswith("[ok]") or l.startswith("[FAIL]")]
    print(linha[0] if linha else saida.strip()[-300:])
    glb = os.path.join(ROOT, "qa", "preview", aid + "_preview.glb")
    if not os.path.isfile(glb):
        print("  sem previa para " + aid)
        return None
    out = os.path.join(ROOT, "qa", "preview", aid)
    return rp.folha(ROOT, aid, blender, glb=glb, out=out)


def main():
    ids = sys.argv[1:]
    if not ids:
        sys.exit(__doc__)
    blender = mt.find_blender()
    for aid in ids:
        p = uma(aid, blender)
        if p:
            print("  ->", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
