#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""faixa_ref.py - REGUA EXTERNA da roupa feminina, lida na folha de referencia.

    python qa/probe/sondas/faixa_ref.py           # tabela das 37
    python qa/probe/sondas/faixa_ref.py {id}

O shorts_ref.py devolve UMA corrida escura, porque no masculino so ha uma peca.
A roupa feminina tem duas (faixa + short), entao aqui se devolvem TODAS as
corridas e elas se identificam pela ordem: a de cima e a faixa, a de baixo e o
short. O criterio de "escuro" e o mesmo - fracao da LARGURA DO CORPO naquela
linha, nao contagem de pixel - porque foi ele que resolveu a sombra entre as
coxas dos d3 (ver shorts_ref.py).

Vale a mesma ressalva do shorts_ref.py: a Meshy reinterpreta proporcao, entao
isto acha erro GROSSO, nao centesimo. E e exatamente para isso que serve - a
janela do detector 3D tem que ser calibrada por algo que nao seja o proprio
detector 3D (LICOES.md 1.3).
"""
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import zenith_paths as zp  # noqa: E402

FRAC_MIN = 0.55    # fracao da largura do TRONCO para a linha valer como tecido
LUM_MAX = 90       # o corpo e cinza claro; a peca e quase preta
CORRIDA_MIN = 0.01  # em fracao da altura da figura: abaixo disso e ruido


# ---------------------------------------------------------------------------
# A FRACAO E MEDIDA NA MAIOR CORRIDA DA LINHA, NAO NA FIGURA INTEIRA
# ---------------------------------------------------------------------------
# A primeira versao herdou do shorts_ref.py a conta "pixels escuros / pixels de
# figura na linha". No short isso funciona porque na altura do short o braco ja
# e so pulso e mao. Na FAIXA nao: na altura do peito os dois bracos estao ali, em
# A-pose, e entram no denominador. O resultado foi um vies SO NO TOPO - a base
# da faixa bateu com a malha no milesimo (0.668 contra 0.669) e o topo saiu
# 0.04 da altura baixo demais (0.719 contra 0.760), porque perto do topo o
# deltoide engrossa, o denominador cresce e a fracao cai abaixo do limiar antes
# de a peca acabar.
#
# O erro foi pego pintando: com o topo da folha, o render deixou o terco de cima
# da faixa MODELADA sem pintar - da para ver o degrau de tecido aparecendo acima
# do preto. Regua externa tambem erra; o que nao pode e errar CALADA.
#
# Aqui a fracao passa a ser medida dentro da maior corrida contigua de figura da
# propria linha, que e o tronco na altura do peito e uma coxa na altura da
# bainha. Braco separado do corpo simplesmente sai da conta.
def corridas(path):
    """Todas as corridas de tecido na vista, de cima para baixo.

    Devolve [(topo_zh, base_zh)] em fracao da altura da FIGURA, com zh=0 nos
    pes - mesma convencao do 3D."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)

    borda = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]], axis=0)
    bg = np.median(borda, axis=0)
    fig = np.abs(a - bg).sum(axis=2) > 30
    ys, _xs = np.where(fig)
    if ys.size == 0:
        return []
    y0, y1 = ys.min(), ys.max()
    Hpx = max(1, y1 - y0)

    escuro = fig & (a.mean(axis=2) < LUM_MAX)
    frac = np.zeros(fig.shape[0])
    for y in range(y0, y1 + 1):
        xs = np.where(fig[y])[0]
        if xs.size == 0:
            continue
        cortes = np.where(np.diff(xs) > 1)[0]
        ini = np.concatenate([[0], cortes + 1])
        fim = np.concatenate([cortes, [xs.size - 1]])
        i = int(np.argmax(fim - ini))
        a0, a1 = xs[ini[i]], xs[fim[i]] + 1
        frac[y] = escuro[y, a0:a1].sum() / float(a1 - a0)
    linha = frac > FRAC_MIN

    out, ini = [], None
    for y in range(len(linha) + 1):
        dentro = y < len(linha) and linha[y]
        if dentro and ini is None:
            ini = y
        elif not dentro and ini is not None:
            topo = (y1 - ini) / Hpx
            base = (y1 - (y - 1)) / Hpx
            if topo - base >= CORRIDA_MIN:
                out.append((topo, base))
            ini = None
    return out


# ---------------------------------------------------------------------------
# A COMPARACAO E POR SETOR, PORQUE A BORDA DE CIMA NAO E UMA ALTURA SO
# ---------------------------------------------------------------------------
# No short bastava confrontar UM numero (o topo do cos) com a folha. Na faixa
# nao: o busto empurra a borda de cima e a frente sobe 0.03-0.06 da altura em
# relacao as costas. Confrontar a media contra a folha das costas reprovaria o
# resultado certo, e confrontar contra a folha da frente aprovaria uma faixa
# reta. Entao sao TRES confrontos - base, topo de costas, topo de frente - e
# cada um contra a vista que o mede.
#
# Convencao do pipeline: a frente aponta para -Y, que cai no setor n//4.
def do_3d(hi, quarto):
    """Mediana de faixa_hi_zh no quarto de azimute pedido ('frente'|'costas')."""
    n = len(hi)
    c = n // 4 if quarto == "frente" else (n // 4 + n // 2) % n
    half = max(1, n // 8)
    vs = [hi[(c + d) % n] for d in range(-half, half + 1)]
    return float(np.median(vs))


# ---------------------------------------------------------------------------
# QUAL DAS CORRIDAS DA FRENTE E A FAIXA - pela BASE, nao pela ordem (11/08)
# ---------------------------------------------------------------------------
# A versao anterior pegava a corrida de CIMA da vista frontal. Em 35 das 37 isso
# acerta, e em duas nao: o b08_d1 e o b11_d1 tem uma terceira corrida escura la
# em cima (0.869..0.856 e 0.861..0.848, treze milesimos de altura, na sombra do
# queixo), e a regua devolvia ELA como topo da faixa. O efeito nao era silencioso
# - dava -0.113 e -0.101 contra o 3D, absurdo obvio -, mas tirava os dois avatares
# do alcance de qualquer conserto guiado por folha.
#
# O criterio novo nao e altura minima de corrida (isso seria mais um limiar
# escolhido para caber nesses dois): e o FATO MEDIDO de que a borda de BAIXO da
# faixa esta na mesma altura na frente e nas costas - delta +0.015 medio, contra
# +0.031 a +0.060 da borda de cima. Entao a corrida frontal certa e a que casa a
# base com a das costas, e as costas leem bem nos 37.
#
# A trava continua: se a melhor candidata errar a base por mais que isto, nao ha
# faixa legivel na frente e a funcao devolve None em vez de um numero plausivel.
# Regua externa tambem erra; o que nao pode e errar CALADA.
BASE_TOL = 0.05


def casa_frente(cf, faixa_costas):
    """A corrida frontal da FAIXA, escolhida pela base contra a vista de costas."""
    if len(cf) < 2 or not faixa_costas:
        return None
    alvo = faixa_costas[1]
    melhor = min(cf, key=lambda c: abs(c[1] - alvo))
    return melhor if abs(melhor[1] - alvo) <= BASE_TOL else None


def main():
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    smap = {}
    p = os.path.join(ROOT, "config", "shorts_map.json")
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            smap = json.load(f)
    bmi = {}
    lib = os.path.join(ROOT, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            bmi = {x["id"]: x.get("measured_bmi", 0) for x in json.load(f)["avatars"]}

    ids = [alvo] if alvo else sorted(
        (i for i, _d in zp.all_ref_dirs(ROOT) if i.startswith("zen_f_")),
        key=lambda k: bmi.get(k, 0))

    print("{:<16} {:>5}  {:>15}  {:>15}  {:>15}  {:>21}  {:>14}".format(
        "id", "imc", "FAIXA costas t/b", "FAIXA frente t/b", "SHORT cos/bainha",
        "3D-folha base/cos/fre", "SHORT c/b"))
    print("-" * 116)
    saida = {}
    for aid in ids:
        ref = zp.ref_path(ROOT, aid, "back")
        if not os.path.isfile(ref):
            print("{:<16} sem folha de costas".format(aid))
            continue
        cs = corridas(ref)
        faixa = cs[0] if len(cs) >= 2 else None
        short = cs[1] if len(cs) >= 2 else (cs[0] if cs else None)

        # A FRENTE e uma medida diferente, nao uma confirmacao da mesma: o busto
        # empurra a borda de cima da faixa para CIMA, entao topo de frente e topo
        # de costas nao sao o mesmo numero. Foi essa diferenca que apareceu no 3D
        # antes de aparecer aqui - o render da frente mostrava tecido modelado
        # acima da pintura, e o das costas nao.
        fr = zp.ref_path(ROOT, aid, "front")
        cf = corridas(fr) if os.path.isfile(fr) else []
        frente = casa_frente(cf, faixa)
        saida[aid] = {"faixa": faixa, "faixa_frente": frente, "short": short,
                      "n": len(cs)}

        def _f(v):
            return "{:>6.3f}/{:.3f}".format(*v) if v else "{:>14}".format("-")

        e = smap.get(aid, {})
        hi = e.get("faixa_hi_zh")
        d = "{:>21}".format("-")
        if hi is not None and faixa:
            hi = list(np.atleast_1d(hi))
            db = e["faixa_lo_zh"] - faixa[1]
            dc = do_3d(hi, "costas") - faixa[0]
            df = (do_3d(hi, "frente") - frente[0]) if frente else float("nan")
            d = "{:+7.3f}{:+7.3f}{:+7.3f}".format(db, dc, df)

        # O SHORT tambem precisa de regua externa, e nao tinha. Metade das
        # femininas sai com BAINHA-CHUTE (nenhum pico de anel nas duas pernas),
        # ou seja a altura veio de um recuo e nao de uma medida - exatamente o
        # caso em que consistencia interna nao prova nada. Aqui o cos e a bainha
        # do 3D vao contra a corrida escura de BAIXO da folha de costas.
        ds = "{:>14}".format("-")
        if short and e.get("waist_zh") is not None:
            w = list(np.atleast_1d(e["waist_zh"]))
            cos3d = do_3d(w, "costas") if len(w) > 1 else w[0]
            hem3d = float(np.min(np.atleast_1d(e["hem_l_zh"])))
            ds = "{:+7.3f}{:+7.3f}".format(cos3d - short[0], hem3d - short[1])
        print("{:<16} {:>5.1f}  {}  {}  {}  {}  {}".format(
            aid, bmi.get(aid, 0), _f(faixa), _f(frente), _f(short), d, ds))

    out = os.path.join(ROOT, "qa", "probe", "faixa", "_folha.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(saida, f, indent=1)
    print("\ngravado: {}".format(os.path.relpath(out, ROOT)))


main()
