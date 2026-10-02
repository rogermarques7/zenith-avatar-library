# -*- coding: utf-8 -*-
"""O CAMPO DO PESCOCO POR TIPO DE CORPO: onde o volume mora quando o pescoco cresce.

    blender -b -P qa/probe/sondas/pescoco_perfil.py -- --ids IDS --out qa/pescoco/perfis_base.json --so-base
    python scripts/pescoco_campo.py [--perfis qa/pescoco/perfis_base.json] [--ver zen_m_b01_d1]

Grava `config/pescoco_campo.json`, que o `morph.py` le para montar o
`morph_neck`. O mapa e o produto, como no short e no morph.

POR QUE EXISTE (sessao 42, 01/10). Ate aqui o pescoco era o MESMO cilindro em
todos os 103 - so a amplitude mudava. Medido com o perfil radial (raio que um
raio horizontal saindo do eixo do pescoco encontra na pele, independente de
topologia), a colecao mostra que cada tipo engrossa num lugar diferente, em mm
de raio por cm de pescoco (uniforme = 1,59):
  - magro, medio e musculosa: lado-tras (trapezio/esternocleidomastoideo) 3-4,8,
    garganta ~1, e ACIMA DO QUEIXO quase nada (0,3-1) - a mandibula fica nitida;
  - pesado: frente baixa (papada) e nuca 2-4, e o crescimento CONTINUA acima do
    queixo na nuca e nas bochechas.
O cilindro uniforme fazia o oposto do magro: 2,3 cm de raio por igual no
`zen_m_b01_d1` (~+14 cm na circunferencia visivel) para a regua ler +3,4 - a
"cabeca sobre um cano" do veredito dele.

COMO. Para cada avatar, regressao PONDERADA de R(h, theta) contra a
circunferencia do pescoco (library.json) entre os corpos do MESMO SEXO, com peso
pelo IMC (gaussiana em log, sigma 0,30) e pela definicao (d3 contra d1/d2 pesa
0,35). A inclinacao e puxada para a do sexo inteiro por um ridge (`RIDGE`), para
grupo pequeno nao virar ruido; depois e alisada e normalizada pelo maximo na
zona do pescoco. A altura e medida a partir do QUEIXO de cada corpo, nao em
fracao fixa - o queixo vai de 0,85 a 0,89 da altura na colecao.

⚠️ FRENTE PELOS PES E QUEIXO PELA INCLINACAO. O `morph.py` achava a frente pelo
lado do rosto mais longe de y=0 e ERRAVA EM 30 DE 103 (corpo pesado empurra o
centro da caixa para a frente e a nuca fica mais longe que o nariz): nesses o
morph empurrava o queixo e poupava a nuca, e a trava de rosto olhava a nuca. E o
queixo por "salto de 25%" nao existe no obeso - o pescoco vira cone ate o rosto e
o detector caia no fim da varredura (0,917). Aqui o queixo e onde o perfil
FRONTAL sobe mais rapido (a face de baixo do queixo e quase horizontal). Os dois
vao gravados no campo e o `morph.py` usa ESTES, nao os dele.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HQ = np.round(np.arange(-0.080, 0.0401, 0.005), 4)   # altura - queixo, fracao de H
TH = np.arange(0, 181, 15)                             # 0 frente, 180 nuca
UNIFORME = 10.0 / (2 * math.pi)                        # 1,59 mm de raio por cm
SIGMA_IMC = 0.30          # largura do vizinho em log(IMC)
PESO_OUTRA_DEF = 0.35     # d3 contra d1/d2
RIDGE = 40.0              # cm^2 x peso: puxa a inclinacao local para a do sexo
S_MIN, S_MAX = 0.3, 5.0   # mm/cm - nunca para dentro quando cresce
R_MAX = 0.150             # m: raio maior que isto e ombro/braco, nao pescoco
ALISA = 3                 # passadas do nucleo 1-2-1: com 1, o salto lado/frente na
                          # encosta do trapezio virou 1 triangulo no zen_m_b06_d3
ZONA = (-0.035, 0.000)    # onde o pescoco e pescoco, para normalizar
RASANTE = 2.0             # |dR/dz| acima disto a pele e quase horizontal: o raio
                          # horizontal RASPA a superficie e o R vira ruido (encosta
                          # do trapezio, face de baixo do queixo). Fica de fora.


def queixo(hs, R):
    f = np.nanmean(R[:, 0:2], axis=1)
    sel = (hs >= 0.845) & (hs <= 0.900)
    dR = np.gradient(f, hs)
    return float(hs[int(np.argmax(np.where(sel, dR, -1e9)))])


def reamostrar(hs, ths, e):
    R = np.array(e["R0"], float)
    zq = queixo(hs, R)
    out = np.full((len(HQ), len(TH)), np.nan)
    for j, t in enumerate(TH):
        jj = int(np.argmin(np.abs(np.array(ths) - t)))
        col = R[:, jj] * 1.75 / e["H"]
        incl = np.abs(np.gradient(col, hs * 1.75))
        ok = ~np.isnan(col) & (col < R_MAX) & (incl < RASANTE)
        if ok.sum() > 3:
            out[:, j] = np.interp(HQ, hs[ok] - zq, col[ok], left=np.nan, right=np.nan)
    return zq, out * 1000.0   # mm


def preencher(S):
    S = S.copy()
    for _ in range(40):
        nan = np.isnan(S)
        if not nan.any():
            break
        P = np.pad(S, 1, mode="edge")
        viz = np.stack([P[:-2, 1:-1], P[2:, 1:-1], P[1:-1, :-2], P[1:-1, 2:]])
        cnt = (~np.isnan(viz)).sum(axis=0)
        m = np.where(cnt > 0, np.nansum(viz, axis=0) / np.maximum(cnt, 1), np.nan)
        S[nan] = m[nan]
    return np.nan_to_num(S, nan=UNIFORME)


def alisar(S):
    k = np.array([0.25, 0.5, 0.25])
    A = np.pad(S, ((1, 1), (0, 0)), mode="edge")
    S = k[0] * A[:-2] + k[1] * A[1:-1] + k[2] * A[2:]
    A = np.pad(S, ((0, 0), (1, 1)), mode="reflect")   # theta reflete em 0 e 180
    return k[0] * A[:, :-2] + k[1] * A[:, 1:-1] + k[2] * A[:, 2:]


def inclinacao(X, Y, w):
    """Inclinacao ponderada por celula, com ridge para a do sexo (S_g)."""
    nc = Y.shape[1:]
    S = np.full(nc, np.nan)
    for i in range(nc[0]):
        for j in range(nc[1]):
            y = Y[:, i, j]
            ok = ~np.isnan(y) & (w > 1e-3)
            if ok.sum() < 4:
                continue
            ww, xx, yy = w[ok], X[ok], y[ok]
            xm, ym = (ww * xx).sum() / ww.sum(), (ww * yy).sum() / ww.sum()
            S[i, j] = (ww * (xx - xm) * (yy - ym)).sum() / (ww * (xx - xm) ** 2).sum()
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perfis", default="qa/pescoco/perfis_base.json")
    ap.add_argument("--ver", help="imprime a tabela de um avatar")
    args = ap.parse_args()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    d = json.load(open(os.path.join(root, args.perfis), encoding="utf8"))
    lib = {a["id"]: a for a in json.load(open(os.path.join(root, "library.json"),
                                              encoding="utf8"))["avatars"]}
    hs, ths = np.array(d["hs"]), d["ths"]
    ids = [a for a in d["avatars"] if a in lib]
    faltam = sorted(set(lib) - set(ids))
    if faltam:
        sys.exit("perfis sem {} avatar(es): {} ...".format(len(faltam), faltam[:3]))

    Rq = {a: reamostrar(hs, ths, d["avatars"][a]) for a in ids}
    saida = {"_sobre": ("Campo do morph_neck por avatar (scripts/pescoco_campo.py). "
                        "W[hq][theta] em [0,1]: peso do deslocamento radial; hq = "
                        "altura/H - queixo_h; theta 0 frente, 180 nuca. s_ref_mm_cm: "
                        "mm de raio por cm de pescoco onde W=1 - a amplitude NATURAL "
                        "de cm_at_full e cm_at_full x s_ref."),
             "hq": HQ.tolist(), "theta": TH.tolist(), "avatars": {}}

    for sexo in ("m", "f"):
        grp = [a for a in ids if lib[a]["sex"] == sexo]
        X = np.array([lib[a]["circumferences_cm"]["neck"] for a in grp])
        Y = np.array([Rq[a][1] for a in grp])
        lb = np.log([lib[a]["measured_bmi"] for a in grp])
        d3 = np.array([lib[a]["definition"] == "d3" for a in grp])
        S_g = preencher(inclinacao(X, Y, np.ones(len(grp))))
        for k, aid in enumerate(grp):
            w = np.exp(-0.5 * ((lb - lb[k]) / SIGMA_IMC) ** 2) \
                * np.where(d3 == d3[k], 1.0, PESO_OUTRA_DEF)
            S_l = inclinacao(X, Y, w)
            # ridge: com o Sxx ponderado da celula, puxa para S_g
            xm = (w * X).sum() / w.sum()
            sxx = (w * (X - xm) ** 2).sum()
            S = np.where(np.isnan(S_l), S_g, (S_l * sxx + S_g * RIDGE) / (sxx + RIDGE))
            S = preencher(S)
            for _ in range(ALISA):
                S = alisar(S)
            S = np.clip(S, S_MIN, S_MAX)
            zona = (HQ >= ZONA[0]) & (HQ <= ZONA[1])
            s_ref = float(np.percentile(S[zona], 90))
            W = np.clip(S / s_ref, 0.0, 1.0)
            ordem = np.argsort(-w)
            saida["avatars"][aid] = {
                "queixo_h": round(Rq[aid][0], 4), "frente": -1.0,
                "s_ref_mm_cm": round(s_ref, 3),
                "s_medio_mm_cm": round(float(S[zona].mean()), 3),
                "vizinhos_efetivos": round(float(w.sum() ** 2 / (w ** 2).sum()), 1),
                "vizinhos": [grp[i] for i in ordem[1:6]],
                "W": np.round(W, 3).tolist(),
            }

    out = os.path.join(root, "config", "pescoco_campo.json")
    json.dump(saida, open(out, "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
    print("gravado {} ({} avatares)".format(out, len(saida["avatars"])))
    if args.ver:
        e = saida["avatars"][args.ver]
        print("\n{}  queixo {:.4f}  s_ref {:.2f} mm/cm  vizinhos efetivos {}  {}".format(
            args.ver, e["queixo_h"], e["s_ref_mm_cm"], e["vizinhos_efetivos"], e["vizinhos"]))
        print("  hq     " + " ".join("{:>4d}".format(int(t)) for t in TH))
        for i, h in enumerate(HQ):
            print("{:+.3f}  ".format(h) + " ".join("{:4.2f}".format(v) for v in e["W"][i]))


if __name__ == "__main__":
    main()
