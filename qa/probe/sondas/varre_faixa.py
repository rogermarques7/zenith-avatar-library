#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""varre_faixa.py - procura as duas bordas da FAIXA no cache, em Python puro.

    python qa/probe/sondas/varre_faixa.py perfil {id}   # o perfil de anel, cru
    python qa/probe/sondas/varre_faixa.py tabela        # picos x folha, nas 37
    python qa/probe/sondas/varre_faixa.py varre         # varredura de janela

Le qa/probe/faixa/*.npz (cache_faixa.py) e qa/probe/faixa/_folha.json
(faixa_ref.py, a regua externa). Nada aqui abre o Blender: uma hipotese custa
segundos, que foi a licao da sessao 21.
"""
import glob
import math
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
CACHE = os.path.join(ROOT, "qa", "probe", "faixa")
ZB = 240


def carrega():
    folha = {}
    p = os.path.join(CACHE, "_folha.json")
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            folha = json.load(f)
    bmi = {}
    lib = os.path.join(ROOT, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            bmi = {x["id"]: x.get("measured_bmi", 0) for x in json.load(f)["avatars"]}
    dados = {}
    for p in sorted(glob.glob(os.path.join(CACHE, "*.npz"))):
        aid = os.path.basename(p)[:-4]
        d = dict(np.load(p))
        d["folha"] = folha.get(aid)
        d["imc"] = bmi.get(aid, 0.0)
        dados[aid] = d
    return dados


def picos(ring, lo_zh, hi_zh, n=6):
    """Maximos locais no intervalo, do mais forte para o mais fraco."""
    lo = max(1, int(lo_zh * ZB))
    hi = min(ZB - 1, int(hi_zh * ZB))
    out = []
    for b in range(lo, hi + 1):
        if ring[b] >= ring[b - 1] and ring[b] >= ring[b + 1]:
            out.append((float(ring[b]), (b + 0.5) / ZB))
    out.sort(reverse=True)
    return out[:n]


def ring_costas(A):
    """O perfil de anel medido SO nas costas e nos lados.

    E o sinal que decide a borda de CIMA, e nao esta no cache porque o cache
    guarda o mapa (A) e o perfil cheio. Na frente, na altura do topo, o tecido
    CONTINUA - nao ha vinco nenhum ali -, entao o quantil baixo sobre os 24
    setores nao ve anel. Mascarar a frente e o que fez o pico aparecer."""
    az = A.shape[0]
    front = az // 4
    half = max(1, az // 6)
    m = np.ones(az, dtype=bool)
    for d in range(-half, half + 1):
        m[(front + d) % az] = False
    r = np.quantile(A[m], 0.35, axis=0)
    for _ in range(2):
        r = np.convolve(r, np.array([0.25, 0.5, 0.25]), mode="same")
    return r


def cmd_chute(lo_b=(0.635, 0.700), lo_t=(0.695, 0.750)):
    """Onde o anel some, e o que a folha dizia naquele avatar.

    O --report acusa FAIXA-CHUTE mas nao diz se a janela e que estava apertada
    ou se o vinco nao existe naquele corpo. Aqui da para ver os dois de uma vez,
    em segundos, sem abrir o Blender."""
    dados = carrega()
    print("{:<16} {:>5}  {:>13}  {:>26}  {:>26}".format(
        "id", "imc", "folha t/b", "picos BASE (anel cheio)", "picos TOPO (so costas)"))
    print("-" * 96)
    for aid, d in sorted(dados.items(), key=lambda kv: kv[1]["imc"]):
        f = d["folha"] or {}
        fx = f.get("faixa")
        rb = d["ring"]
        rt = ring_costas(d["A"])
        pb = picos(rb, lo_b[0], lo_b[1], 2)
        pt = picos(rt, lo_t[0], lo_t[1], 2)

        def _p(pk):
            return "{:>26}".format("  ".join(
                "{:.3f}({:.3f})".format(z, s) for s, z in pk) or "-- SEM ANEL --")
        print("{:<16} {:>5.1f}  {:.3f}/{:.3f}  {}  {}".format(
            aid, d["imc"], fx[0] if fx else 0, fx[1] if fx else 0, _p(pb), _p(pt)))


def escolhe(ring, lo, hi, centro, sigma, smin=0.012):
    """Pico do anel pesado por um PRIOR, e nunca um pico de forca zero.

    Sem o prior o argmax pega o vinco mais fundo da janela, que nem sempre e a
    borda da peca (nos IMC 30-54 ele pegava um sulco 0.03 acima do sulco
    inframamario). Sem o corte de forca ele devolve a BORDA da janela com
    score 0.000 e isso vira um numero que ninguem consegue distinguir de uma
    medida - foi assim que o b04_d2 ganhou base 0.702 contra 0.667 da folha.
    Devolve (zh, score) ou (None, 0.0)."""
    pk = [(s, z) for s, z in picos(ring, lo, hi, 12) if s >= smin]
    if not pk:
        return None, 0.0
    z, s = max((s * math.exp(-0.5 * ((z - centro) / sigma) ** 2), z, s)
               for s, z in pk)[1:]
    return z, s


def cmd_novo(base_c=0.672, base_sig=0.030, altura=0.050, tol=0.012):
    """O modelo novo, conferido contra a folha SEM abrir o Blender.

    A mudanca de fundo: o topo deixa de ser uma medida independente e passa a
    ser BASE + ALTURA DA PECA. A folha diz que a altura da faixa nas costas e
    0.0504 com desvio de 0.0037 nas 37 - a peca e a mesma em todo mundo -,
    enquanto a base varia 0.654..0.685 com o corpo. Procurar as duas bordas
    como se fossem independentes dava ao topo um erro de ate 0.034; ancorar
    reduz o problema a UMA deteccao, a que tem o sinal forte (o sulco
    inframamario)."""
    dados = carrega()
    eb, et = [], []
    print("{:<16} {:>5}  {:>13}  {:>15}  {:>15}".format(
        "id", "imc", "folha t/b", "base 3D (erro)", "topo 3D (erro)"))
    print("-" * 74)
    for aid, d in sorted(dados.items(), key=lambda kv: kv[1]["imc"]):
        f = (d["folha"] or {}).get("faixa")
        if not f:
            continue
        b, sb = escolhe(d["ring"], 0.635, 0.700, base_c, base_sig)
        chute_b = b is None
        if b is None:
            b = base_c
        alvo = b + altura
        t, stt = escolhe(ring_costas(d["A"]), alvo - tol, alvo + tol, alvo, tol)
        chute_t = t is None
        if t is None:
            t = alvo
        db, dt = b - f[1], t - f[0]
        eb.append(abs(db))
        et.append(abs(dt))
        print("{:<16} {:>5.1f}  {:.3f}/{:.3f}  {:.3f} ({:+.3f}){}  {:.3f} ({:+.3f}){}".format(
            aid, d["imc"], f[0], f[1], b, db, "*" if chute_b else " ",
            t, dt, "*" if chute_t else " "))
    print("-" * 74)
    print("erro |base| media {:.4f} max {:.4f}   |topo| media {:.4f} max {:.4f}"
          .format(sum(eb) / len(eb), max(eb), sum(et) / len(et), max(et)))


def cmd_perfil(aid):
    d = carrega()[aid]
    f = d["folha"]
    print("{}  imc {:.1f}  folha faixa {:.3f}/{:.3f}".format(
        aid, d["imc"], f["faixa"][0], f["faixa"][1]))
    ring = d["ring"]
    for b in range(int(0.58 * ZB), int(0.84 * ZB)):
        zh = (b + 0.5) / ZB
        marca = ""
        if abs(zh - f["faixa"][0]) < 0.004:
            marca = " <== topo folha"
        elif abs(zh - f["faixa"][1]) < 0.004:
            marca = " <== base folha"
        print("  {:.3f}  {:.4f}  {}{}".format(
            zh, ring[b], "#" * int(ring[b] * 120), marca))


def cmd_tabela(lo=0.60, hi=0.80):
    dados = carrega()
    print("{:<16} {:>5}  {:>13}  {}".format("id", "imc", "folha t/b", "picos do anel"))
    print("-" * 96)
    for aid, d in sorted(dados.items(), key=lambda kv: kv[1]["imc"]):
        f = d["folha"]
        pk = picos(d["ring"], lo, hi)
        print("{:<16} {:>5.1f}  {:.3f}/{:.3f}  {}".format(
            aid, d["imc"], f["faixa"][0], f["faixa"][1],
            "  ".join("{:.3f}({:.2f})".format(z, s) for s, z in pk)))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tabela"
    if cmd == "perfil":
        cmd_perfil(sys.argv[2])
    elif cmd == "novo":
        cmd_novo()
    elif cmd == "chute":
        cmd_chute()
    else:
        cmd_tabela()
