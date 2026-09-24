#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bainha_anel.py - a borda da peca como ANEL FECHADO, rastreada no pixel.

    python qa/probe/sondas/bainha_anel.py --alvo hem
    python qa/probe/sondas/bainha_anel.py --alvo cos --ids zen_f_b01_d1 --marcar

Junta o clay de FRENTE e o de COSTAS (`bainha_rasante.py`), converte coluna em
azimute e rastreia o vinco dando A VOLTA na perna. Grava
`qa/probe/anel_{alvo}.json` com uma curva de 24 setores por perna, no formato
que o `w_field` do shorts.py ja le (lista + `hem_center`) e que nunca tinha
sido usado.

--------------------------------------------------------------------------
1. POR QUE PRECISA DAS DUAS VISTAS (23/09, sessao 37)
--------------------------------------------------------------------------
A versao anterior mediu so a vista FRONTAL e gravou a mediana como um numero
por perna. O Rogerio reprovou 3 das 4 previas e disse por que:

> *"vc ta tentando seguir uma linha reta sem levar em consideracao que na parte
>  de tras, por conta do volume do gluteo, tem uma curvatura - na frente a barra
>  da perna fica numa altura e nas costas em outra."*

Um ESCALAR e um plano horizontal: por construcao ele nao consegue ser uma
altura na frente e outra atras. E a estatistica com que eu justifiquei o
escalar ("espalhamento de 1,0 cm dentro da perna") tinha sido calculada **so
com a frente** - cega no eixo exato do defeito.

⚠️ Dos 4, aprovou 1: o de MENOR correcao (0,5 cm). Guardar isso: quando a
correcao e pequena a forma do anel nao importa; quando e grande, ela e tudo.
Nao existe "aplicar primeiro os faceis" - os faceis sao os que nao precisam.

--------------------------------------------------------------------------
2. O ANEL FECHADO E O QUE SEPARA TECIDO DE PELE
--------------------------------------------------------------------------
Rastrear cada vista sozinha nao funciona, e o motivo e anatomico: ha SEMPRE um
vinco de pele mais forte que a barra por perto.

    na frente : a prega INGUINAL, que so existe na frente
    nas costas: o sulco GLUTEO, que so existe atras

Medido no `zen_m_b09h_d1`: nas costas o tracado seguia o sulco gluteo no meio
da coxa e so caia na barra nas pontas - 3,5 cm de erro, com sinal mais forte
que o do alvo. Nenhum limiar separa os dois, porque o falso e mais nitido.

✅ O que separa e a TOPOLOGIA: a barra DA A VOLTA na perna; a prega inguinal e
o sulco gluteo, nao. Rastreando no anel inteiro, o vinco falso paga um salto
enorme na emenda de +-90 graus e perde para a barra, que fecha. E a mesma
doutrina do `w_ring_map` ("anel fechado e o que o detector sabe achar"), agora
no pixel em vez de na malha.

--------------------------------------------------------------------------
3. COMO A COLUNA VIRA AZIMUTE - conta fechada, nada da malha
--------------------------------------------------------------------------
    X_mundo = +(coluna - RX/2) * ortho / RX     (frente, ve sin(az) < 0)
    X_mundo = -(coluna - RX/2) * ortho / RX     (costas, ve sin(az) > 0)
    cos(az) = (X - cx) / R

`cx` e `R` saem da propria SILHUETA: numa projecao ortografica as bordas da
perna sao exatamente `cx +- R`. Nao entra nada do detector que esta medida vai
corrigir, e e isso que a torna uma regua externa de verdade.

--------------------------------------------------------------------------
4. O QUE ESTA SONDA NAO MEDE
--------------------------------------------------------------------------
- Perna colada na outra: sem borda interna nao ha `R`, logo nao ha azimute. O
  avatar sai com `ok: false`. E resposta, nao falha.
- A MAO entra no quadro em A-pose e vira uma terceira corrida escura; por isso
  a silhueta pega as duas MAIORES corridas, uma de cada lado do centro.
- Perto de +-90 graus a projecao e rasante: a ALTURA continua certa, o AZIMUTE
  atribuido nao. Por isso os setores rasantes entram com peso menor.
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
BASE = os.path.join(ROOT, "qa", "revisao", "_hem")
AZ = 24
RX, RY = 1100, 900
SPAN = 0.22
PX_POR_ZH = RY / (SPAN * RY / RX)      # px por fracao da altura do corpo
SOBE_ZH, DESCE_ZH = 0.045, 0.012
LAM = 0.05                              # penalidade de degrau entre setores
MIN_COLS = 12                           # colunas minimas para um setor valer


def ridge(a):
    """Linha ESCURA horizontal: claro acima, escuro no centro, claro abaixo."""
    s = np.apply_along_axis(lambda c: np.convolve(c, np.ones(5) / 5, mode="same"), 0, a)
    k = np.zeros(21)
    k[:7] = 1.0 / 14
    k[14:] = 1.0 / 14
    k[7:14] = -1.0 / 7
    return np.apply_along_axis(lambda c: np.convolve(c, k, mode="same"), 0, s)


SECAO = {}
_sp = os.path.join(ROOT, "qa", "probe", "secao_peca.json")
if os.path.isfile(_sp):
    with open(_sp, encoding="utf-8") as _f:
        SECAO = json.load(_f)


def azimute(x_px, sec, vista, origem):
    """Coluna de pixel -> azimute, pela elipse da secao.

    A camera e ORTOGRAFICA e nivelada, entao a coluna da o X do mundo por conta
    fechada. O que falta e o Y, e ele vem da elipse: na vista de frente a
    superficie visivel e a de menor Y, na de costas a de maior.

    `origem` diz em volta de QUE ponto o azimute e medido, e isso nao e
    detalhe: o `w_field` mede a BAINHA em volta de `hem_center` e o COS em
    volta de (0, 0). Usar o centro errado gira a curva inteira.

    Devolve (az, peso). O peso cai perto de +-90 graus, onde a projecao e
    rasante: la a ALTURA lida continua certa e o AZIMUTE nao."""
    cx, cy, ea, eb = sec
    sinal = 1.0 if vista == "frente" else -1.0
    X = sinal * (x_px - RX / 2.0) * (SPAN * 1.75) / RX
    t = (X - cx) / max(ea, 1e-9)
    if abs(t) > 0.995:
        return None
    Y = cy - sinal * eb * math.sqrt(1.0 - t * t)
    az = math.atan2(Y - origem[1], X - origem[0])
    return az, math.sqrt(1.0 - t * t)


def silhueta(a):
    """Mascara de corpo. O fundo do render e EXATAMENTE plano, entao ele e o
    valor mais frequente ENTRE OS PIXELS SEM GRADIENTE.

    ⚠️ Nao basta o valor mais frequente da imagem: neste enquadramento a coxa
    ocupa mais area que o fundo e o histograma cru devolve a PELE, invertendo a
    mascara inteira. Nao e limiar - e perguntar a coisa certa: fundo e a regiao
    lisa, nao a regiao grande."""
    g = np.abs(np.gradient(a.astype(np.float64))[0]) + \
        np.abs(np.gradient(a.astype(np.float64))[1])
    liso = a[g < 0.5]
    bg = int(np.bincount(liso.astype(np.int64).ravel()).argmax()) if liso.size else 0
    return bg, np.abs(a.astype(np.int16) - bg) > 4


def pernas(corpo, y):
    """As duas maiores corridas, uma de cada lado do centro (ver §4)."""
    idx = np.where(corpo[y])[0]
    if idx.size < 40:
        return []
    q = np.where(np.diff(idx) > 1)[0]
    ini = np.concatenate([[0], q + 1])
    fim = np.concatenate([q, [idx.size - 1]])
    runs = [(int(idx[i]), int(idx[f])) for i, f in zip(ini, fim) if idx[f] - idx[i] > 45]
    meio = corpo.shape[1] / 2.0
    e = [r for r in runs if (r[0] + r[1]) / 2.0 < meio]
    d = [r for r in runs if (r[0] + r[1]) / 2.0 >= meio]
    if not e or not d:
        return []
    a = max(e, key=lambda r: r[1] - r[0])
    b = max(d, key=lambda r: r[1] - r[0])
    if a[1] >= meio or b[0] <= meio:      # corrida unica: pernas coladas
        return []
    return [a, b]


def anel_dp(A, occ, lam=LAM):
    """DP CIRCULAR sobre o azimute. E o passo que separa tecido de pele: a
    barra fecha a volta, a prega inguinal e o sulco gluteo nao."""
    nb, W = A.shape
    passo = np.abs(np.subtract.outer(np.arange(W), np.arange(W)))
    melhor = None
    for start in range(0, W, 2):
        sc = np.full((nb, W), -1e18)
        bk = np.zeros((nb, W), dtype=np.int32)
        sc[0, start] = A[0, start]
        for j in range(1, nb):
            d = sc[j - 1][None, :] - lam * passo
            k = d.argmax(axis=1)
            sc[j] = d[np.arange(W), k] + A[j]
            bk[j] = k
        for z in range(W):
            tot = sc[nb - 1, z] - lam * abs(z - start)
            if melhor is None or tot > melhor[0]:
                cam = [z]
                for j in range(nb - 1, 0, -1):
                    cam.append(int(bk[j, cam[-1]]))
                melhor = (tot, list(reversed(cam)))
    return melhor[1]


def uma(aid, alvo, marcar=False):
    d = os.path.join(BASE, aid)
    pref = "rasante" if alvo == "hem" else "rasante_cos"
    out = {"id": aid, "alvo": alvo, "ok": False}
    mp = os.path.join(d, pref + "_marcas.json")
    if not os.path.isfile(mp):
        out["motivo"] = "sem marcas"
        return out
    with open(mp, encoding="utf-8") as f:
        mk = json.load(f)
    zc = mk["hem_mapa_zh"]

    y0 = max(10, int(RY / 2 - SOBE_ZH * PX_POR_ZH))
    y1 = min(RY - 10, int(RY / 2 + DESCE_ZH * PX_POR_ZH))
    W = y1 - y0

    sp = SECAO.get(aid, {})
    secs = sp.get("hem" if alvo == "hem" else "cos", {})
    if (alvo == "hem" and len(secs) < 2) or (alvo == "cos" and not secs):
        out["motivo"] = "sem secao de malha (w_limbs nao alcanca a altura)"
        return out
    A = {k: np.zeros((AZ, W)) for k in secs}
    N = {k: np.zeros(AZ) for k in secs}
    imgs = {}
    for vista in ("frente", "costas"):
        png = os.path.join(d, "{}_{}.png".format(pref, vista))
        if not os.path.isfile(png):
            out["motivo"] = "falta " + os.path.basename(png)
            return out
        a = np.asarray(Image.open(png).convert("L"))
        imgs[vista] = a
        R = ridge(a)
        for lado, sec in secs.items():
            origem = (sec[0], sec[1]) if alvo == "hem" else (0.0, 0.0)
            for x in range(RX):
                r = azimute(x, sec, vista, origem)
                if r is None:
                    continue
                az, peso = r
                j = int((az + math.pi) / (2 * math.pi) * AZ) % AZ
                A[lado][j] += R[y0:y1, x] * peso
                N[lado][j] += peso

    curva, diag = {}, {}
    for lado in secs:
        n = N[lado]
        if (n > 0).sum() < AZ * 0.7:
            out["motivo"] = "setores vazios na perna " + lado
            return out
        M = A[lado] / np.maximum(n[:, None], 1e-9)
        # setor sem amostra herda do vizinho, para o DP nao ver buraco
        for j in range(AZ):
            if n[j] <= MIN_COLS:
                k = min([b for b in range(AZ) if n[b] > MIN_COLS],
                        key=lambda b: min(abs(b - j), AZ - abs(b - j)))
                M[j] = M[k]
        cam = anel_dp(M, n)
        zs = [round(zc + (RY / 2.0 - (y0 + z)) / PX_POR_ZH, 5) for z in cam]
        curva[lado] = zs
        diag[lado] = {
            "forca": round(float(np.mean([M[j, cam[j]] for j in range(AZ)])), 2),
            "no_teto": int(sum(1 for z in cam if z <= 1)),
            "no_piso": int(sum(1 for z in cam if z >= W - 2)),
            "setores_vazios": int((n <= MIN_COLS).sum()),
        }
    out.update(ok=True, curva=curva, diag=diag, hem_mapa_zh=zc, secao=secs,
               amplitude_cm={k: round((max(v) - min(v)) * 175, 1)
                             for k, v in curva.items()},
               frente_vs_costas_cm={
                   k: round((float(np.median(v[:AZ // 4] + v[3 * AZ // 4:]))
                             - float(np.median(v[AZ // 4:3 * AZ // 4]))) * 175, 1)
                   for k, v in curva.items()},
               sobe_cm={k: round((float(np.median(v)) - zc) * 175, 1)
                        for k, v in curva.items()})
    if marcar:
        _marca(d, pref, imgs, out, y0, y1, alvo)
    return out


def _marca(d, pref, imgs, out, y0, y1, alvo):
    """Desenha o anel de volta nas DUAS vistas - e a conferencia no olho.

    Usa a MESMA funcao `azimute()` do tracado: se a conversao coluna->azimute
    estiver errada, o azul sai fora do vinco e isso aparece na imagem. Uma
    marcacao que usasse outra conta nao conferiria nada."""
    for vista, a in imgs.items():
        im = np.dstack([a, a, a]).copy()
        for lado, sec in out["secao"].items():
            origem = (sec[0], sec[1]) if alvo == "hem" else (0.0, 0.0)
            for x in range(RX):
                r = azimute(x, sec, vista, origem)
                if r is None:
                    continue
                j = int((r[0] + math.pi) / (2 * math.pi) * AZ) % AZ
                y = int(round(RY / 2.0
                              - (out["curva"][lado][j] - out["hem_mapa_zh"]) * PX_POR_ZH))
                if 0 <= y < RY - 1:
                    im[y:y + 2, x] = [40, 120, 255]
        y = int(RY / 2)
        im[y:y + 2, :RX // 5] = [235, 40, 40]
        im[y:y + 2, -RX // 5:] = [235, 40, 40]
        Image.fromarray(im).save(os.path.join(d, "anel_" + pref + "_" + vista + ".png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--alvo", default="hem", choices=["hem", "cos"])
    ap.add_argument("--ids", default="")
    ap.add_argument("--marcar", action="store_true")
    a = ap.parse_args()
    ids = [x for x in a.ids.split(",") if x] or sorted(
        x for x in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, x)) and x.startswith("zen_"))
    res, maus = {}, []
    for aid in ids:
        r = uma(aid, a.alvo, a.marcar)
        if r["ok"]:
            res[aid] = r
            print("{:<18} sobe {:>5} cm  amplitude {:>5} cm  frente-costas {:>5} cm"
                  .format(aid, r["sobe_cm"]["l"], r["amplitude_cm"]["l"],
                          r["frente_vs_costas_cm"]["l"]))
        else:
            maus.append((aid, r.get("motivo", "?")))
    p = os.path.join(ROOT, "qa", "probe", "anel_{}.json".format(a.alvo))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("\nanel montado em {} de {}".format(len(res), len(ids)))
    for aid, m in maus[:10]:
        print("  FORA {:<18} {}".format(aid, m))
    if len(maus) > 10:
        print("  ... e mais {}".format(len(maus) - 10))
    print("->", os.path.relpath(p, ROOT))


main()
