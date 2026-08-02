#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""varre_bainha.py - escolhe a janela da bainha contra a serie, em segundos.

    python qa/probe/sondas/varre_bainha.py            # tabela
    python qa/probe/sondas/varre_bainha.py --varre    # varredura de janelas

Le o cache de qa/probe/hem/ (cache_bainha.py) e a folha de referencia
(shorts_ref.medir na vista de costas). Nao abre o Blender.

O TESTE que da direito de confiar no numero novo: nos avatares em que a
deteccao de PRODUCAO funciona (hem_peaks_zh nao vazio, e o Rogerio nao
reprovou), a deteccao nova tem que devolver O MESMO ANEL. Regua nova se calibra
rodando na peca ja aprovada - LICOES.md 1.6.
"""
import argparse
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S            # noqa: E402
import shorts_ref as SR       # noqa: E402
import zenith_paths as zp     # noqa: E402

HEM = os.path.join(ROOT, "qa", "probe", "hem")

# os 12 que o Rogerio reprovou no olho em 28/07 (diario, sessao 6)
REPROVADOS = {"zen_m_" + x for x in (
    "b07_d1 b07_d3 b08_d1 b08_d2 b08_d3 b09_d1 b09_d2 b10_d1 b10_d2 "
    "b11_d1 b11_d2 b12_d1").split()}


def carrega():
    smap = S.load_map(ROOT)
    bmi = {}
    lib = os.path.join(ROOT, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            bmi = {x["id"]: x.get("measured_bmi", 0) for x in json.load(f)["avatars"]}

    dados = {}
    for aid in sorted(smap):
        p = os.path.join(HEM, aid + ".npz")
        if not os.path.isfile(p):
            continue
        z = np.load(p)
        costas = zp.ref_path(ROOT, aid, "back")
        m = SR.medir(costas) if os.path.isfile(costas) else None
        e = smap[aid]
        pk = e["diag"].get("hem_peaks_zh", [[], []])
        dados[aid] = {
            "prod": (z["prod_l"], z["prod_r"]),
            "xs": (z["xs_l"], z["xs_r"]),
            "crotch": float(z["meta"][0]),
            "detectada": float(z["meta"][1]),
            "teto": float(z["meta"][2]),
            "hem_map": (e["hem_l_zh"], e["hem_r_zh"]),
            "chutada": (len(pk[0]) == 0, len(pk[1]) == 0),
            "folha": m[1] if m else None,
            "bmi": bmi.get(aid, 0.0),
        }
    return dados


def pico(ring, lo_zh, hi_zh):
    """Melhor anel da janela, em fracao da altura. None se nao houver pico."""
    pk = S.w_peaks(np, ring, lo_zh * S.Z_BINS, hi_zh * S.Z_BINS)
    if not pk:
        return None, 0.0
    score, b = pk[0]
    return (b + 0.5) / S.Z_BINS, score


def detecta(d, modo, folga_baixo=0.035, folga_cima=0.020):
    """Devolve (esq, dir) em fracao da altura, ou None por perna.

    modo 'prod'  : janela ancorada na virilha, selecao leg_id (o de hoje)
    modo 'folha' : janela ancorada na BAINHA DA FOLHA, selecao por sinal de x
    """
    out = []
    for i in range(2):
        if modo == "prod":
            ring = d["prod"][i]
            lo = d["crotch"] - S.HEM_BELOW_CROTCH[1]
            hi = d["crotch"] - S.HEM_BELOW_CROTCH[0]
        else:
            ring = d["xs"][i]
            if d["folha"] is None:
                out.append((None, 0.0))
                continue
            lo = d["folha"] - folga_baixo
            hi = min(d["folha"] + folga_cima, d["teto"] - 0.005)
        out.append(pico(ring, lo, hi))
    return out


def tabela(dados, folga_baixo, folga_cima):
    print("{:<15} {:>6} {:>7} {:>7}  {:>7} {:>7}  {:>7} {:>7}  {:>7} {}".format(
        "id", "imc", "virilha", "folha", "mapa_e", "mapa_d",
        "novo_e", "novo_d", "d_mapa", "obs"))
    print("-" * 104)
    difs_ok = []
    for aid, d in sorted(dados.items(), key=lambda kv: kv[1]["bmi"]):
        novo = detecta(d, "folha", folga_baixo, folga_cima)
        ne, nd = novo[0][0], novo[1][0]
        me, md = d["hem_map"]
        obs = []
        if any(d["chutada"]):
            obs.append("CHUTE")
        if aid in REPROVADOS:
            obs.append("reprovado")
        dif = None
        if ne is not None and nd is not None:
            dif = ((ne - me) + (nd - md)) / 2.0
            if not any(d["chutada"]):
                difs_ok.append(dif)
        print("{:<15} {:>6.1f} {:>7.3f} {:>7.3f}  {:>7.3f} {:>7.3f}  "
              "{:>7} {:>7}  {:>7} {}".format(
                  aid, d["bmi"], d["crotch"],
                  d["folha"] if d["folha"] is not None else float("nan"),
                  me, md,
                  "{:.3f}".format(ne) if ne is not None else "-",
                  "{:.3f}".format(nd) if nd is not None else "-",
                  "{:+.3f}".format(dif) if dif is not None else "-",
                  " ".join(obs)))
    print("-" * 104)
    if difs_ok:
        a = np.array(difs_ok)
        print("CALIBRACAO nos que a producao ja acertava (n={}): "
              "|novo - mapa| mediana {:.4f}  p90 {:.4f}  max {:.4f}".format(
                  a.size, float(np.median(np.abs(a))),
                  float(np.percentile(np.abs(a), 90)), float(np.abs(a).max())))


def varre_virilha(dados):
    """Janela ancorada na VIRILHA sobre o perfil x-sign - sem folha nenhuma.

    E a unica variante que serve de CONSERTO DE PRODUCAO: o w_fit nao tem a
    folha na mao, e um detector que dependesse dela violaria a regra 3b do
    CLAUDE.md (o short e lido da malha). A pergunta e se o teto pode subir
    ACIMA da virilha detectada sem que o proprio anel da virilha ganhe nos
    corpos magros."""
    print("{:>7} {:>7}  {:>5} {:>8} {:>8} {:>8}  {}".format(
        "abaixo", "acima", "n_ok", "mediana", "p90", "max", "os 5 chutados"))
    for lo in (0.065, 0.080):
        for hi in (-0.015, 0.0, 0.015, 0.025, 0.035, 0.045):
            difs, faltou, chutados = [], 0, []
            for aid, d in sorted(dados.items()):
                v = []
                for i in range(2):
                    p, _s = pico(d["xs"][i], d["crotch"] - lo, d["crotch"] + hi)
                    v.append(p)
                if any(x is None for x in v):
                    if any(d["chutada"]):
                        chutados.append(aid.replace("zen_m_", "") + ":-")
                    else:
                        faltou += 1
                    continue
                if any(d["chutada"]):
                    ok = (d["folha"] is not None
                          and abs((v[0] + v[1]) / 2 - d["folha"]) < 0.025)
                    chutados.append("{}:{:.3f}{}".format(
                        aid.replace("zen_m_", ""), (v[0] + v[1]) / 2,
                        "" if ok else "!"))
                    continue
                me, md = d["hem_map"]
                difs.append(((v[0] - me) + (v[1] - md)) / 2.0)
            a = np.abs(np.array(difs))
            print("{:>7.3f} {:>+7.3f}  {:>5} {:>8.4f} {:>8.4f} {:>8.4f}  {} {}".format(
                lo, hi, a.size, float(np.median(a)),
                float(np.percentile(a, 90)), float(a.max()),
                "sem pico:{}".format(faltou), " ".join(chutados)))


def varre(dados):
    """Qual janela reproduz melhor o mapa nos que a producao acertava."""
    print("{:>6} {:>6}  {:>5} {:>8} {:>8} {:>8}".format(
        "baixo", "cima", "n_ok", "mediana", "p90", "max"))
    for fb in (0.025, 0.030, 0.035, 0.040, 0.050):
        for fc in (0.010, 0.015, 0.020, 0.030):
            difs, faltou = [], 0
            for aid, d in dados.items():
                if any(d["chutada"]):
                    continue
                novo = detecta(d, "folha", fb, fc)
                if novo[0][0] is None or novo[1][0] is None:
                    faltou += 1
                    continue
                me, md = d["hem_map"]
                difs.append(((novo[0][0] - me) + (novo[1][0] - md)) / 2.0)
            a = np.abs(np.array(difs))
            print("{:>6.3f} {:>6.3f}  {:>5} {:>8.4f} {:>8.4f} {:>8.4f}  "
                  "sem pico: {}".format(
                      fb, fc, a.size, float(np.median(a)),
                      float(np.percentile(a, 90)), float(a.max()), faltou))


def escrever(dados, aid, folga_baixo, folga_cima):
    """Grava a bainha nova no config/shorts_map.json, UM avatar por vez.

    So aceita avatar cuja bainha era CHUTE (hem_peaks_zh vazio nas duas pernas).
    Onde o detector de producao achou anel, o numero dele fica: a janela desta
    sonda e ancorada na FOLHA e por isso nao serve de detector - serve de
    resgate para quem nao tem numero nenhum.

    A janela (-0.030, +0.020) nao foi escolhida a gosto: e o envelope medido de
    (bainha 3D - bainha da folha) nos 32 avatares que a producao acertou, que vai
    de -0.0244 a +0.0081. LICOES.md 1.8c - a tolerancia sai dos dados que o
    sistema ja tem, nao da minha cabeca."""
    d = dados.get(aid)
    if d is None:
        print("{}: sem cache - rode cache_bainha.py".format(aid))
        return 1
    if not all(d["chutada"]):
        print("{}: a producao ACHOU anel nesta bainha - nao sobrescrever "
              "(chute = {})".format(aid, d["chutada"]))
        return 1
    if d["folha"] is None:
        print("{}: sem folha de costas".format(aid))
        return 1

    novo = detecta(d, "folha", folga_baixo, folga_cima)
    if any(p is None for p, _ in novo):
        print("{}: sem anel na janela da folha - nao gravar chute novo por cima "
              "de chute velho".format(aid))
        return 1

    smap = S.load_map(ROOT)
    e = smap[aid]
    velho = (e["hem_l_zh"], e["hem_r_zh"])
    e["hem_l_zh"] = round(novo[0][0], 5)
    e["hem_r_zh"] = round(novo[1][0], 5)
    e["source"] = "manual"
    e["hem_fonte"] = "anel-xsign"
    e["diag"]["hem_anel_xsign"] = {
        "score": [round(novo[0][1], 4), round(novo[1][1], 4)],
        "folha_zh": round(d["folha"], 4),
        "janela": [-folga_baixo, folga_cima],
        "antes": [round(velho[0], 5), round(velho[1], 5)],
    }
    S.save_map(ROOT, smap)
    print("{}: bainha {:.4f}/{:.4f} -> {:.4f}/{:.4f}  (folha {:.3f}, "
          "score {:.3f}/{:.3f})  source=manual".format(
              aid, velho[0], velho[1], novo[0][0], novo[1][0], d["folha"],
              novo[0][1], novo[1][1]))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--escrever", metavar="ID")
    ap.add_argument("--varre", action="store_true")
    ap.add_argument("--virilha", action="store_true")
    ap.add_argument("--baixo", type=float, default=0.035)
    ap.add_argument("--cima", type=float, default=0.020)
    a = ap.parse_args()
    dados = carrega()
    if a.escrever:
        return escrever(dados, a.escrever, a.baixo, a.cima)
    if a.virilha:
        return varre_virilha(dados)
    if a.varre:
        return varre(dados)
    tabela(dados, a.baixo, a.cima)


if __name__ == "__main__":
    main()
