#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""borda_viva_grava.py - passa a proposta do borda_viva.py para o shorts_map.

    python qa/probe/sondas/borda_viva_grava.py --simula          # so a tabela
    python qa/probe/sondas/borda_viva_grava.py --grava [ids...]  # escreve o mapa

Le `qa/revisao/_viva/{id}/proposta.json` e decide, BORDA POR BORDA, se a curva
lida nas arestas vivas substitui a do mapa. Nao toca GLB nenhum: depois disto
vem `shorts.py --preview` (olhar) e so entao `--apply` + `morph.py --apply`.

--------------------------------------------------------------------------
A POLITICA - cada regra tem o caso que a motivou
--------------------------------------------------------------------------
1. COBERTURA >= 0.75 da volta, ou a borda fica como esta. Borda que nao da a
   volta e arco, e arco e o que a virilha e o avental sao (LICOES 4.5n).
   Foi o que segurou o cos do zen_m_b12_d1 (0.58).
2. |delta| <= 8 cm contra o mapa em todo setor. Nenhum defeito que ele
   apontou passa de ~7 cm; mais que isso e o ajuste achando outra coisa.
3. COS_AVENTAL: os setores da frente (+-105 graus, os mesmos do
   w_cos_avental) ficam com o mapa. Debaixo do avental o tecido nao aparece
   na malha e quem decide ali e a normal da barriga (4.5e). A proposta so
   vale nos lados e nas costas, com emenda de 2 setores.
4. Depois de gravar, o cos passa pelo MESMO w_waist_liso do --fit (a folha
   entrega o caminho, nao o acabamento - 4.5k), e a trava CANTO tem de ficar
   limpa. As outras bordas ja saem alisadas do envelope.
5. `source: "manual"` + `borda_viva` com o que foi aceito e recusado, para o
   --fit nao apagar e para qualquer um auditar sem reabrir o Blender.
"""
import argparse
import json
import math
import os
import shutil
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

BASE = os.path.join(ROOT, "qa", "revisao", "_viva")
MAPA = os.path.join(ROOT, "config", "shorts_map.json")
BACKUP = os.path.join(ROOT, "qa", "probe", "_mapa_antes_s38.json")
NB = 24
COB_MIN = 0.75
DELTA_MAX = 0.046            # 8 cm em 1,75 m
CHAVE = {"hem_l": "hem_l_zh", "hem_r": "hem_r_zh", "cos": "waist_zh",
         "faixa_lo": "faixa_lo_zh", "faixa_hi": "faixa_hi_zh"}
# FOLGA para fora da peca, em fracao da altura (0.002 = 3,5 mm). A borda que a
# Meshy modela e SERRILHADA - dentes de alguns milimetros - e o envelope passa
# no meio dos dentes: na previa do zen_f_b07j_d1 as pontas de baixo da barra
# sairam como lascas claras sem tinta. Perto do erro que isto conserta (1 a 7
# cm), 3,5 mm e desprezivel, e cobre a lasca.
FOLGA = {"hem_l": -0.002, "hem_r": -0.002, "faixa_lo": -0.002,
         "cos": +0.002, "faixa_hi": +0.002}
SETOR_AZ = -math.pi + (np.arange(NB) + 0.5) * 2 * math.pi / NB


def lista(v):
    v = np.atleast_1d(np.asarray(v, dtype=float))
    return np.full(NB, v[0]) if v.size == 1 else v


def frente_avental():
    """Peso 1 nos setores do avental (+-105 graus da frente), 0 fora, com
    rampa de 2 setores - sem emenda seca entre as duas fontes."""
    d = np.degrees(np.abs(np.angle(np.exp(1j * (SETOR_AZ + math.pi / 2)))))
    # rampa de 60 graus centrada em 105: com 30 graus a emenda fazia QUINA, a
    # trava CANTO pedia alisamento e a gaussiana derrubava as costas junto
    return np.clip((135.0 - d) / 60.0, 0.0, 1.0)


# espelho esquerda/direita: o setor de azimute `az` troca com `pi - az`
ESPELHO = [int(np.argmin(np.abs(np.angle(np.exp(1j * (SETOR_AZ - (math.pi - a)))))))
           for a in SETOR_AZ]
# setores LATERAIS: ate 40 graus do eixo x, dos dois lados
LATERAL = np.abs(np.cos(SETOR_AZ)) > math.cos(math.radians(40))


def simetriza(v):
    """O corpo sai do process.py simetrico (trava de 20 mm), entao borda de
    tronco assimetrica e ruido da leitura, nao anatomia. No zen_f_b08_d2 o topo
    da faixa saiu inclinado nas costas, um lado ~2 cm acima do outro."""
    v = np.asarray(v, dtype=float)
    return (v + v[ESPELHO]) / 2.0


def corta_axila(v, antigo):
    """Topo da faixa nos setores LATERAIS: pode DESCER, mas nao sobe mais que
    0.004 (0,7 cm) acima do mapa antigo. A dobra da axila e aresta viva que
    sobrevive ao raio de 3 cm do braco, e o envelope 'de cima' subia por ela -
    na previa isso virou abinha preta no braco em b03h_d1, b05_d1, b06_d1,
    b07j_d1, b10_d2, b11_d1, b11h_d1.

    ❌ A primeira versao desta trava interpolava entre o plato da frente e as
    costas. Nao serviu: o modelo antigo desce DENTRO da frente, e a
    interpolacao punha a descida nas costas - o topo ficava 2 a 3,5 cm acima
    do antigo exatamente nas quinas de tras, onde nasciam as abinhas."""
    v = np.asarray(v, dtype=float).copy()
    teto = np.asarray(antigo, dtype=float) + 0.004
    v[LATERAL] = np.minimum(v[LATERAL], teto[LATERAL])
    return v


def canto(w):
    return max(abs(w[(i - 1) % NB] - 2 * w[i] + w[(i + 1) % NB]) for i in range(NB))


def decide(aid, e, P):
    out, notas = {}, {}
    for nome, b in P["bordas"].items():
        if b.get("falhou"):
            notas[nome] = "falhou"
            continue
        atual = lista(e[CHAVE[nome]])
        nova = np.array(b["curva"], dtype=float) + FOLGA[nome]
        if b["cobertura"] < COB_MIN:
            notas[nome] = "cobertura {:.2f}".format(b["cobertura"])
            continue
        # a BARRA tem licenca maior com cobertura alta: nos d3 de coxa cheia a
        # tinta de hoje desce 9 a 11 cm abaixo da barra modelada (zen_f_b10_d3,
        # zen_f_b04_d3 - visivel na previa), e 8 cm recusava justamente os piores
        teto = 0.069 if (nome.startswith("hem") and b["cobertura"] >= 0.85) else DELTA_MAX
        if np.abs(nova - atual).max() > teto:
            notas[nome] = "delta {:.1f} cm".format(np.abs(nova - atual).max() * 175)
            continue
        if nome in ("cos", "faixa_lo", "faixa_hi"):
            nova = simetriza(nova)
        if nome == "faixa_hi":
            nova = corta_axila(nova, atual)
        if nome == "faixa_lo":
            # a BASE tambem: nos setores laterais ela nao desce mais que 0,7 cm
            # abaixo do mapa antigo. No zen_f_b12_d1 a base lida desceu nos lados
            # e a previa saiu com ABAS pretas grandes nas quinas de baixo - o
            # entregue de hoje tinha a faixa limpa ali. Regressao, recusada.
            piso = atual - 0.004
            nova = np.where(LATERAL, np.maximum(nova, piso), nova)
        if nome == "cos":
            if e.get("cos_avental"):
                wf = frente_avental()
                nova = wf * atual + (1 - wf) * nova
            # ALISAR SO SE A QUINA PEDIR. O w_waist_liso tem teto para SUBIR e
            # nao para DESCER: com a frente do avental bem mais baixa, a
            # gaussiana arrastava as costas ~1 cm para baixo e o topo do elastico
            # voltava a ficar sem tinta (zen_m_b10_d2: lido 0.571, gravado
            # 0.563 - o mesmo defeito do entregue). A curva do envelope ja sai
            # lisa; o alisamento so entra se a trava CANTO reprovar.
            if canto(nova) > S.WAIST_CANTO_MAX_ZH:
                hem = min(lista(e["hem_l_zh"]).min(), lista(e["hem_r_zh"]).min())
                crua = nova.copy()
                liso = np.array(S.w_waist_liso(np, list(nova), hem + 1.0 / S.Z_BINS))
                # ...e fora do avental o alisamento NAO desce a curva lida: a
                # quina costuma estar na emenda do avental, e e la que ele age
                livre = frente_avental() < 0.01 if e.get("cos_avental") else                     np.ones(NB, dtype=bool)
                tent = np.where(livre, np.maximum(liso, crua), liso)
                nova = tent if canto(tent) <= S.WAIST_CANTO_MAX_ZH else liso
            if canto(nova) > S.WAIST_CANTO_MAX_ZH:
                notas[nome] = "CANTO {:.3f}".format(canto(nova))
                continue
        out[nome] = [round(float(v), 5) for v in nova]
        notas[nome] = "ok {:+.1f}..{:+.1f} cm".format(
            (nova - atual).min() * 175, (nova - atual).max() * 175)
    return out, notas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--grava", action="store_true")
    a = ap.parse_args()
    with open(MAPA, encoding="utf-8") as f:
        smap = json.load(f)
    ids = a.ids or sorted(x for x in os.listdir(BASE)
                          if os.path.isfile(os.path.join(BASE, x, "proposta.json")))
    if a.grava and not os.path.isfile(BACKUP):
        shutil.copyfile(MAPA, BACKUP)
        print("backup:", os.path.relpath(BACKUP, ROOT))
    mudou = 0
    for aid in ids:
        with open(os.path.join(BASE, aid, "proposta.json"), encoding="utf-8") as f:
            P = json.load(f)
        e = smap[aid]
        novas, notas = decide(aid, e, P)
        print("{:<15} {}".format(aid, " | ".join(
            "{} {}".format(k, v) for k, v in notas.items())))
        if a.grava and novas:
            for nome, v in novas.items():
                e[CHAVE[nome]] = v
            e["source"] = "manual"
            if "hem_l" in novas or "hem_r" in novas:
                # a bainha deixou de ser o pico do anel: as travas de CHUTE do
                # _hem_flags nao se aplicam, so a faixa v-b (mesma regra do
                # resgate por anel)
                e["hem_fonte"] = "borda_viva"
            e["borda_viva"] = {"sessao": 38, "aceitas": sorted(novas),
                               "notas": notas}
            mudou += 1
    if a.grava:
        S.save_map(ROOT, smap)      # mesmo formato do --fit (sort_keys)
        print("{} entradas alteradas".format(mudou))


if __name__ == "__main__":
    main()
