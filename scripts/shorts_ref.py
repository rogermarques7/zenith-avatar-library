#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shorts_ref.py - mede onde o short esta na FOLHA DE REFERENCIA e compara com o
que o shorts.py pintou no 3D.

    python scripts/shorts_ref.py            # tabela dos 39
    python scripts/shorts_ref.py {id}

--------------------------------------------------------------------------
PORQUE ISTO EXISTE
--------------------------------------------------------------------------
O shorts.py acha o short lendo a MALHA (vincos de tecido). Isso resolve o
problema que a projecao de imagem nao resolvia - a barriga que cobre o cos -
mas cria um ponto cego: nada estava conferindo o resultado contra a intencao.
O `--report` do shorts.py compara cada avatar com a SERIE, e a serie pode
estar consistentemente errada; foi assim que o zen_m_b12_d1 passou como
"dentro da faixa" com o short na altura errada.

A referencia e a unica fonte externa: e a imagem que gerou a malha, e nela o
short e literalmente preto sobre um corpo cinza claro. Medir ali e barato e
independente do detector 3D.

--------------------------------------------------------------------------
O QUE ESTA MEDIDA VALE, E O QUE NAO VALE
--------------------------------------------------------------------------
NAO e uma regua exata. A Meshy reinterpreta as proporcoes, entao a altura do
cos na folha e no master nao batem no centesimo - a mesma ressalva que o
CLAUDE.md ja registra sobre o measure.py (regra 5c). Serve para achar erro
GROSSO: um cos 15% da altura fora de lugar aparece aqui e nao aparece na
comparacao com a serie.

Usa a vista de COSTAS. Na frente, num corpo obeso, a barriga cobre o short na
propria imagem, entao o topo medido seria a prega e nao o cos.
"""

import json
import math
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import zenith_paths as zp                                          # noqa: E402
# ⚠️ shorts.py so importa bpy DENTRO do worker, entao ele e importavel daqui.
# E preciso: o alisamento do cos (w_waist_liso) tem de ser o MESMO codigo dos
# dois lados, senao a folha grava uma curva que o --fit nunca produziria.
import shorts as S                                                 # noqa: E402


def medir(path):
    """Devolve (topo_zh, base_zh, area_frac) do short na imagem, em fracao da
    altura da FIGURA (nao do canvas)."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)

    # fundo = mediana da borda; figura = tudo que se afasta dele
    borda = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]], axis=0)
    bg = np.median(borda, axis=0)
    dist = np.abs(a - bg).sum(axis=2)
    fig = dist > 30
    ys, xs = np.where(fig)
    if ys.size == 0:
        return None
    y0, y1 = ys.min(), ys.max()
    Hpx = max(1, y1 - y0)

    # short = escuro de verdade. O corpo e cinza claro; o short e quase preto.
    lum = a.mean(axis=2)
    escuro = fig & (lum < 90)

    # ---- FRACAO DA LARGURA DO CORPO, e nao contagem de pixel escuro --------
    # A versao ingenua ("linha tem N pixels escuros") acusou short ate os pes em
    # TODOS os avatares d3: num corpo definido a sombra entre as coxas e escura
    # e vai ate o chao, e a sombra sob o braco idem. Nenhuma das duas cobre a
    # LARGURA do corpo - o short cobre. Entao a pergunta certa e "que fracao da
    # largura desta linha e escura?", nao "quantos pixels escuros ha nela".
    largura = fig.sum(axis=1).astype(np.float64)
    escuros = escuro.sum(axis=1).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(largura > 0, escuros / np.maximum(largura, 1), 0.0)
    linha_short = frac > 0.55

    # ---- maior faixa CONTIGUA ---------------------------------------------
    # O short e uma peca so. Sombra sob o braco vira uma faixa curta e separada;
    # pegar a maior corrida contigua descarta essas sem precisar de limiar novo.
    melhor, atual_ini = None, None
    for y in range(len(linha_short) + 1):
        dentro = y < len(linha_short) and linha_short[y]
        if dentro and atual_ini is None:
            atual_ini = y
        elif not dentro and atual_ini is not None:
            if melhor is None or (y - atual_ini) > (melhor[1] - melhor[0]):
                melhor = (atual_ini, y)
            atual_ini = None
    if melhor is None:
        return None

    topo = (y1 - melhor[0]) / Hpx
    base = (y1 - (melhor[1] - 1)) / Hpx
    return topo, base, escuro.sum() / float(fig.sum())


# Setores da frente do cos, na convencao de w_back_side_mask (24 setores, o 6 e
# o centro da frente). So estes tem coluna util na vista frontal da folha.
WAIST_AZ_BINS = 24


def perfil_frontal(path, nb=WAIST_AZ_BINS, banda=None):
    """Topo do short por SETOR DE AZIMUTE na vista FRONTAL, em fracao da altura
    da figura. Devolve lista de nb posicoes, None onde nao da para medir.

    `banda=(lo, hi)` restringe a busca a uma faixa de altura da figura. SEM ELA
    ESTA FUNCAO NAO SERVE NA COLECAO FEMININA - ver o bloco A FAIXA DO PEITO.

    ---------------------------------------------------------------------
    🔴 A FAIXA DO PEITO ERA A MAIOR CORRIDA (achado de 23/09, sessao 37)
    ---------------------------------------------------------------------
    Esta funcao nasceu em 29/07, quando so existiam os 39 masculinos - e neles
    o unico preto da folha E o short. Desde 01/08 a feminina veste FAIXA + short
    e a faixa e uma barra cheia, mais alta que o short em coluna de tronco.
    "Maior corrida contigua" passou a devolver a FAIXA.

    Nao saiu calado - saiu como numero absurdo que ninguem leu: o `--tracado`
    marcava ERRO em 21 avatares, com erro medio de -0.10 a -0.23 da altura (17
    a 40 cm!) e assimetria esquerda/direita de ~0.20 nas femininas. Plausivel
    demais para alarme, absurdo demais para medida. A §1.1 de novo: a regua nao
    estava errada por pouco, estava medindo OUTRA PECA.

    ⚠️ E o custo nao foi so a regua cega. A sessao 36 consertou o "cos mergulha
    na frente" em 6 avatares ancorando no ANEL DA MALHA, porque a regua externa
    do caminho frontal nao estava disponivel. O anel ficou de 2,0 a 7,2 cm ACIMA
    do que a folha diz, e foi exatamente isso que o Rogerio reprovou em 23/09:
    "o cos ta pintando acima de onde deveria e pegando parte da barriga".

    A banda vem da vista de COSTAS (medir()), que nao tem o problema: la a
    maior corrida e o short mesmo, porque a faixa de costas e mais baixa que a
    da frente e o short cobre o gluteo inteiro. Uma peca calibra a outra.

    ---------------------------------------------------------------------
    PORQUE A VISTA FRONTAL, se o resto do arquivo usa a de costas
    ---------------------------------------------------------------------
    A medida de costas responde "a que ALTURA esta o cos". Esta responde "que
    CAMINHO ele faz", que e outra pergunta e ficou sem regua ate a sessao 5 -
    era a pendencia 3 do state.md, e custou o Rogerio ver no olho que a pintura
    tinha subido na barriga dos corpos pesados.

    Aqui a barriga cobrindo o short NAO e um problema a evitar, e exatamente o
    que se quer medir: nos corpos pesados o que o usuario ve e a prega, e e ela
    que o 3D tem de reproduzir. O cabecalho de medir() diz para nao usar a
    frente porque "o topo medido seria a prega e nao o cos" - verdade, e para
    ESTA medida a prega e o alvo.

    ---------------------------------------------------------------------
    MAIOR CORRIDA CONTIGUA, nao "pixel escuro mais alto"
    ---------------------------------------------------------------------
    Mesma armadilha que medir() ja tinha levado por linha, agora por coluna. A
    primeira versao pegava o pixel escuro mais alto da coluna e leu 0.848 no
    b12_d1 - sombra sob o peito. Sombra de dobra e mancha CURTA; o short e uma
    corrida LONGA. Exigir altura minima de corrida separa os dois sem limiar
    novo de cor."""
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)

    borda = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]], axis=0)
    bg = np.median(borda, axis=0)
    fig = np.abs(a - bg).sum(axis=2) > 30
    ys, _ = np.where(fig)
    if ys.size == 0:
        return None
    y0, y1 = ys.min(), ys.max()
    Hpx = max(1, y1 - y0)

    lum = a.mean(axis=2)
    esc = fig & (lum < 90)

    largura = fig.sum(axis=1).astype(np.float64)
    escuros = esc.sum(axis=1).astype(np.float64)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(largura > 0, escuros / np.maximum(largura, 1), 0.0)
    linhas = np.where(frac > 0.55)[0]
    if banda is not None:
        zl = (y1 - linhas) / float(Hpx)
        linhas = linhas[(zl >= banda[0]) & (zl <= banda[1])]
    if linhas.size == 0:
        return None

    # centro e raio do corpo medidos NA ALTURA DO SHORT, nao na figura inteira:
    # ombro e coxa tem larguras diferentes e o mapeamento azimute->coluna erra
    # se usar a silhueta toda.
    ymid = int(linhas.mean())
    cols = np.where(fig[ymid])[0]
    xc = (cols.min() + cols.max()) / 2.0
    R = (cols.max() - cols.min()) / 2.0

    def maior_corrida(coluna):
        idx = np.where(coluna)[0]
        if idx.size == 0:
            return None
        quebras = np.where(np.diff(idx) > 1)[0]
        ini = np.concatenate([[0], quebras + 1])
        fim = np.concatenate([quebras, [idx.size - 1]])
        k = int(np.argmax(fim - ini))
        return idx[ini[k]], fim[k] - ini[k] + 1

    out = []
    for j in range(nb):
        az = (j + 0.5) / nb * 2 * math.pi - math.pi
        # a frente aponta para -Y, ou seja sin(az) < 0. 0.30 deixa de fora os
        # setores rasantes, onde a coluna tangencia a silhueta e nao mede nada.
        if math.sin(az) > -0.30:
            out.append(None)
            continue
        # 0.88 do raio: em 1.0 a coluna cai na borda da silhueta, onde o short
        # aparece com 1 ou 2 pixels e a medida vira ruido.
        x = int(round(xc + math.cos(az) * R * 0.88))
        if not (0 <= x < esc.shape[1]):
            out.append(None)
            continue
        col = esc[:, x]
        if banda is not None:
            # a MESMA banda tem de valer por coluna, nao so na escolha do ymid:
            # a faixa do peito e uma corrida por coluna tambem, e e ela que
            # vencia o `argmax`. A folga (0.03 para baixo, 0.02 para cima) deixa
            # o arco da prega existir sem alcancar o peito.
            fora = np.ones(col.shape, dtype=bool)
            zc_col = (y1 - np.arange(col.size)) / float(Hpx)
            fora[(zc_col >= banda[0] - 0.03) & (zc_col <= banda[1] + 0.02)] = False
            col = col & ~fora
        r = maior_corrida(col)
        out.append(round(float((y1 - r[0]) / Hpx), 4)
                   if r is not None and r[1] >= 0.02 * Hpx else None)
    return out


def banda_do_short(path_costas):
    """(lo, hi) da banda do short, medida na vista de COSTAS. E o argumento
    `banda` de perfil_frontal() - ver o bloco A FAIXA DO PEITO la."""
    m = medir(path_costas)
    return None if m is None else (m[1] - 0.02, m[0] + 0.05)


def _simetriza(pr, nb=WAIST_AZ_BINS):
    """Espelha o perfil em volta do centro da frente e devolve (media, assimetria).

    O corpo e simetrico e o short tambem, entao um arco de verdade aparece IGUAL
    nos dois lados. Isto nao e refinamento cosmetico - e o que separa sinal de
    ruido nesta regua, e a primeira versao sem isto ia mandar consertar 3
    avatares magros que estavam certos:

      b01_d1  setor 5 -> 0.575   setor 7 (espelho) -> 0.536

    Num corpo magro so 4 colunas sao mensuraveis e uma delas raspa o vao entre
    as pernas; a discordancia esquerda/direita de 0.039 virava "arco" e a
    amplitude do b01_d1 saia maior que a do b08_d1, que tem barriga de verdade.
    Ja no b12_d1 os pares batem em 0.003 e a U aparece limpa. Mesma licao da
    primeira versao de medir(), que acusou 'short ate os pes' em todos os d3:
    padrao implausivel na serie e defeito da regua, nao dos avatares."""
    front = nb // 4
    med, asym = [None] * nb, 0.0
    for d in range(-(nb // 4), nb // 4 + 1):
        j, k = (front + d) % nb, (front - d) % nb
        a, b = pr[j], pr[k]
        if a is None and b is None:
            continue
        if a is not None and b is not None:
            med[j] = (a + b) / 2.0
            asym = max(asym, abs(a - b))
        else:
            med[j] = a if a is not None else b
    return med, asym


def _monotona(pr, nb=WAIST_AZ_BINS):
    """Do flanco para o centro, a borda visivel do tecido so pode DESCER.

    E anatomia, nao suavizacao: a barriga cobre o short mais no meio do que nos
    lados, entao a divisa nao tem como subir indo para o centro. Nenhum avatar
    da serie viola isso na medida limpa - o b12_d1 vai 0.468 0.436 0.386 0.353
    0.339, o b11_d1 vai 0.480 0.460 0.426 0.412, sempre descendo.

    Existe por causa de dois que violavam: b09_d2 e b10_d2 mediam um W, subindo
    nos setores vizinhos ao centro (0.494 · 0.511 · 0.499 · 0.511 · 0.494). Isso
    e a SOMBRA do vinco central da barriga lida como tecido - a mesma familia de
    engano que ja tinha feito a primeira versao de medir() acusar 'short ate os
    pes' nos d3, e a primeira versao de perfil_frontal() ler sombra do peito no
    b12_d1. Gravado no mapa, o W virava um degrau serrilhado bem no meio do
    short, visivel no render.

    A imposicao e por REGRESSAO ISOTONICA (PAVA), nao por minimo corrente. A
    primeira versao usava minimo corrente e foi pior que o problema: no b09_d2 o
    setor de flanco le baixo demais - a coluna a 0.88 do raio raspa a silhueta
    num corpo largo - e o minimo corrente adotava esse ponto ruim e ACHATAVA o
    perfil inteiro em 0.472. Minimo corrente propaga o pior ponto; a isotonica
    faz a media dos que se contradizem e fica perto dos dados."""
    front = nb // 4
    out = list(pr)
    # meio perfil, do centro para o flanco, tem de ser NAO DECRESCENTE
    lado = [(front + d) % nb for d in range(0, nb // 4 + 1)]
    idx = [j for j in lado if out[j] is not None]
    if len(idx) < 3:
        return out
    v = [out[j] for j in idx]

    # PAVA: junta blocos que violam a ordem e substitui pela media do bloco
    blocos = [[x, 1] for x in v]
    i = 0
    while i < len(blocos) - 1:
        if blocos[i][0] > blocos[i + 1][0]:
            s = blocos[i][0] * blocos[i][1] + blocos[i + 1][0] * blocos[i + 1][1]
            n = blocos[i][1] + blocos[i + 1][1]
            blocos[i:i + 2] = [[s / n, n]]
            i = max(i - 1, 0)
        else:
            i += 1
    ajust = []
    for val, cnt in blocos:
        ajust.extend([val] * cnt)

    for j, x in zip(idx, ajust):
        out[j] = round(x, 4)
    # espelha para o outro lado, que a simetrizacao ja tinha igualado
    for d in range(1, nb // 4 + 1):
        ja, jb = (front + d) % nb, (front - d) % nb
        if out[ja] is not None and out[jb] is not None:
            out[jb] = out[ja]
    return out


def tracado(smap, bmi, ids):
    """Compara o CAMINHO do cos da frente com a folha, setor a setor."""
    print("{:<15} {:>6}  {:>8} {:>8}  {:>7} {:>7} {:>6}  {}".format(
        "id", "imc", "arco_ref", "arco_3d", "erro_md", "erro_mx", "assim", "obs"))
    print("-" * 86)
    fora = []
    for aid in ids:
        ref = zp.ref_path(ROOT, aid, "front")
        e = smap.get(aid)
        if not e or not os.path.isfile(ref):
            continue
        pr = perfil_frontal(ref, banda=banda_do_short(zp.ref_path(ROOT, aid, "back")))
        w = e["waist_zh"]
        # ⚠️ Cos ESCALAR tambem se confere. A versao anterior pulava esses com
        # "nao medido", e em 23/09 isso escondeu justamente os 6 que a sessao 36
        # tinha acabado de achatar - os mesmos que o Rogerio reprovou depois.
        # Altura constante e uma curva de 24 setores iguais; nao ha caso novo.
        if isinstance(w, (int, float)):
            w = [float(w)] * WAIST_AZ_BINS
        if pr is None:
            print("{:<15} nao medido".format(aid))
            continue
        pr, asym = _simetriza(pr)
        pr = _monotona(pr)
        pares = [(w[j], pr[j]) for j in range(len(pr)) if pr[j] is not None]
        if len(pares) < 4:
            print("{:<15} poucos setores".format(aid))
            continue
        difs = [t - r for t, r in pares]
        md = sum(difs) / len(difs)
        mx = max(difs, key=abs)
        # AMPLITUDE do arco: e o que o detector estava perdendo. Um cos reto tem
        # amplitude ~0 e passa em qualquer teste de ALTURA, que era o cego das
        # duas reguas antigas.
        arco_ref = max(r for _, r in pares) - min(r for _, r in pares)
        arco_3d = max(t for t, _ in pares) - min(t for t, _ in pares)
        obs = []
        if abs(mx) > TOL_TRACADO:
            obs.append("ERRO")
        # O arco so conta como REAL se for maior que a discordancia
        # esquerda/direita da propria medida. A assimetria e o piso de ruido
        # desta regua e nao da para trata-la como defeito: a pose das folhas
        # nao e simetrica de proposito (e por isso que a bainha e gravada como
        # escalar POR PERNA, e nao uma so). Usada como veredito, ela reprovava
        # 17 dos 39 e enterrava os defeitos de verdade no meio.
        if arco_ref > max(ARCO_MIN, asym) and arco_3d < arco_ref * 0.5:
            obs.append("ARCO-RASO")
        if obs:
            fora.append(aid)
        print("{:<15} {:>6.1f}  {:>8.3f} {:>8.3f}  {:>+7.3f} {:>+7.3f} {:>6.3f}  {} {}".format(
            aid, bmi.get(aid, 0), arco_ref, arco_3d, md, mx, asym,
            " ".join(obs), "<<" if obs else ""))
    print("-" * 86)
    print("erro por setor +-{} da altura · ARCO-RASO se o 3d entrega menos da "
          "metade do arco da folha, e so quando o arco supera {} e a propria "
          "assimetria da medida".format(TOL_TRACADO, ARCO_MIN))
    if fora:
        print("FORA ({}): {}".format(len(fora), ", ".join(fora)))
    else:
        print("todos dentro da tolerancia")
    return 1 if fora else 0


TOL_TRACADO = 0.030   # erro por setor contra a folha
ARCO_MIN    = 0.030   # abaixo disto o arco e ruido de medida, nao anatomia


def escrever(smap, root, aid):
    """Grava no mapa o arco da FRENTE medido na folha, marcando a entrada como
    manual. NAO toca em bainha, costas nem em nada mais.

    ---------------------------------------------------------------------
    PORQUE ISTO EXISTE, E PORQUE NAO CONTRARIA A REGRA 3b
    ---------------------------------------------------------------------
    A regra do CLAUDE.md diz que o short e lido da MALHA e nunca da imagem. O
    motivo dela e concreto: o process.py achava o short projetando a imagem
    frontal e chamando pixel escuro de tecido, e isso nao sobrevivia a corpo
    obeso. Continua valendo, e o shorts.py segue 100% na malha.

    O que se descobriu na sessao 5 e o caso simetrico: nos corpos MUITO pesados a
    malha e que nao tem sinal. Medido no b12_d1 (IMC 148), a concavidade no
    centro da frente e 0.000 em TODA a faixa - o pannus e um dome liso e convexo,
    nao ha vinco ali para achar. Um render de emissao pura confirmou: a barriga
    sai preta do comeco ao fim. Nao e limiar mal escolhido, e ausencia de sinal.

    Foi testada uma alternativa geometrica - o balanco do pannus vira a normal
    para BAIXO - e ela bateu com a folha no b12_d1 (erro 0.004..0.05). Rodada
    nos 39, ERROU sistematicamente por -0.06 a -0.13: em corpo normal a
    transicao acontece logo acima da virilha. O acerto era coincidencia de uma
    amostra. Hipotese descartada, e barata por ter sido testada na serie antes
    de virar codigo.

    Restando: a folha TEM o sinal, e a medida foi conferida desenhando as marcas
    em cima da imagem em 3 avatares - elas seguem a divisa barriga/short. Entao
    a fonte certa para estes poucos avatares e a folha, e o lugar certo para
    esse codigo e AQUI, no medidor externo, e nao dentro do shorts.py.

    O mapa e o produto; o detector so propoe. Esta funcao e mais uma forma de
    proposta, com procedencia gravada no proprio mapa (waist_front_fonte)."""
    ref = zp.ref_path(ROOT, aid, "front")
    if not os.path.isfile(ref):
        print("{}: sem folha frontal".format(aid))
        return 1
    e = smap.get(aid)
    if not e or not isinstance(e.get("waist_zh"), list):
        print("{}: sem entrada de cos no mapa - rode --fit antes".format(aid))
        return 1

    banda = banda_do_short(zp.ref_path(ROOT, aid, "back"))
    pr, _ = _simetriza(perfil_frontal(ref, banda=banda) or [])
    pr = _monotona(pr)
    w = list(e["waist_zh"])
    nb = len(w)
    front = nb // 4
    half = max(1, nb // 6)
    medidos = [j for j in range(nb) if pr[j] is not None]
    if len(medidos) < 4:
        print("{}: folha nao mediu setores suficientes".format(aid))
        return 1

    # ---- o DESLOCAMENTO entre folha e malha vem da vista de COSTAS ----------
    # A folha da a forma E a altura do arco; falta so corrigir o vies sistematico
    # entre as duas (a Meshy reinterpreta proporcao). Esse vies se mede onde as
    # duas concordam, que e justamente onde medir() ja olha: as costas, em que o
    # elastico esta a vista e nao ha barriga cobrindo nada.
    #
    # A primeira versao ancorava pelo ponto mais alto do proprio arco, tratando a
    # folha como so uma FORMA. Errado: no b12_d1 isso subia o arco inteiro 0.074,
    # enquanto o vies real medido nas costas e 0.016. A folha nao e so forma -
    # ela tambem sabe a altura, a menos de um deslocamento pequeno e mensuravel.
    costas = zp.ref_path(ROOT, aid, "back")
    m = medir(costas) if os.path.isfile(costas) else None
    if m is None:
        print("{}: sem folha de costas - nao da para medir o deslocamento".format(aid))
        return 1
    desloc = max(w) - m[0]

    mudou = 0
    for d in range(-half, half + 1):
        j = (front + d) % nb
        if pr[j] is None:
            continue
        novo = round(pr[j] + desloc, 5)
        if abs(novo - w[j]) > 1e-6:
            mudou += 1
        w[j] = novo

    # ---- os BURACOS da folha, dentro e fora do trecho medido ----------------
    # A folha nao mede todo setor: nos rasantes a coluna nao atravessa o corpo, e
    # bem no centro ela as vezes tambem falha (a fenda entre os dois lobos do
    # pannus). Deixar esses setores com o valor da MALHA nao funciona - foi
    # exatamente isso que produziu um degrau de 0.130 no b12_d1, em que o setor
    # central sozinho ficou 0.13 acima dos dois vizinhos vindos da folha.
    #
    # Duas situacoes diferentes, e duas respostas:
    #   DENTRO do trecho medido -> interpola entre os vizinhos medidos. E o mesmo
    #     arco, so falta um ponto dele.
    #   FORA -> rampa ate o valor da malha. Ali nenhuma das duas fontes mede, e
    #     ligar as duas em linha reta e a unica coisa honesta a fazer.
    dd = sorted(d for d in range(-half, half + 1) if pr[(front + d) % nb] is not None)
    dmin, dmax = dd[0], dd[-1]

    for d in range(dmin + 1, dmax):
        j = (front + d) % nb
        if pr[j] is not None:
            continue
        ant = max(x for x in dd if x < d)
        prox = min(x for x in dd if x > d)
        a0, a1 = w[(front + ant) % nb], w[(front + prox) % nb]
        w[j] = round(a0 + (a1 - a0) * (d - ant) / float(prox - ant), 5)

    for lim, passo in ((dmin, -1), (dmax, +1)):
        vao = [front + lim + passo * t
               for t in range(1, abs(half - abs(lim)) + 1)]
        vao = [d for d in vao if abs(d - front) <= half]
        js = [d % nb for d in vao]
        a0 = w[(front + lim) % nb]
        a1 = w[((front + lim) + passo * (len(js) + 1)) % nb]
        for t, j in enumerate(js, start=1):
            w[j] = round(a0 + (a1 - a0) * t / float(len(js) + 1), 5)

    # ---- ALISAR, porque a folha entrega o CAMINHO e nao o ACABAMENTO -------
    # 🔴 Achado de 23/09 (sessao 37): esta funcao gravava o arco CRU. No
    # `w_fit` o alisamento (`w_waist_liso`) e o ULTIMO passo justamente porque o
    # que vem antes decide ONDE o cos esta e ele decide COMO chega la - e aqui a
    # folha entrava depois de tudo, pulando o alisamento inteiro.
    #
    # O preco apareceu no GLB entregue: no `zen_f_b03h_d1` o mergulho sumiu e
    # sobrou uma COROA - dente de serra de 3,9 cm entre setores vizinhos, com a
    # trava `CANTO` em 0.039 contra o corte de 0.018. A medida da folha tem
    # ruido de coluna, e 24 setores de ruido desenham uma serra.
    #
    # E a §4.5f de novo, de cabeca para baixo: la a curva da MALHA saia
    # poligonal; aqui e a da FOLHA. Mesmo conserto, mesmo teto de 2 bins.
    hem = e.get("hem_l_zh")
    hem = hem[0] if isinstance(hem, list) else float(hem)
    w = S.w_waist_liso(np, w, hem + 1.0 / S.Z_BINS)
    w = [round(v, 5) for v in w]

    # O cos tem de continuar sendo UMA curva: na divisa entre o trecho vindo da
    # folha e o trecho vindo da malha nao pode haver degrau. Se houver, e sinal
    # de que o deslocamento nao serviu para este avatar - melhor recusar do que
    # gravar um cos com degrau e deixar a trava de tracado achar depois.
    salto = max(abs(w[j] - w[(j + 1) % nb]) for j in range(nb))
    if salto > 0.045:
        print("{}: RECUSADO - a emenda com a malha daria degrau de {:.3f} "
              "(limite 0.045). Mapa nao alterado.".format(aid, salto))
        return 1

    e["waist_zh"] = w
    e["source"] = "manual"
    e["waist_front_fonte"] = "folha"
    p = os.path.join(root, "config", "shorts_map.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(smap, f, indent=2, sort_keys=True)
    print("{}: arco da frente gravado da folha ({} setores, deslocamento "
          "{:+.4f}, maior salto {:.3f}) -> source=manual".format(
              aid, mudou, desloc, salto))
    return 0
# assimetria nao tem limiar: entra na comparacao do arco, acima.


# quanto de VIES a serie pode ter antes de virar defeito, em fracao da altura.
# 0.004 = 7 mm = ~1 bin de Z_BINS, que e a resolucao do proprio detector. Abaixo
# disso nao ha o que corrigir; acima, ha - e a tira preta que o Rogerio viu em
# 23/09 media 0.0061.
VIES_MAX = 0.004


def _vies(serie):
    """Media e contagem de SINAL da serie, por coluna e por classe.

    ---------------------------------------------------------------------
    🔴 POR QUE ISTO E TAO IMPORTANTE QUANTO O VEREDITO POR AVATAR (23/09)
    ---------------------------------------------------------------------
    A tolerancia declarada aqui e +-0.06 da altura, e ela pega erro GROSSO -
    esta escrito no cabecalho e e verdade. O que nao estava escrito e que, por
    isso mesmo, ela e CEGA PARA VIES: um erro sistematico dez vezes menor que a
    tolerancia passa em 103 de 103 e mesmo assim e visivel no avatar.

    Foi o que aconteceu com a bainha. Todo mundo "dentro", e somando:

        media -0.0061 da altura (1,07 cm), 81 negativos de 103,
        pior nos d3 (-0.0076) que nos d2 (-0.0050)

    ou seja, a tinta descia cerca de um centimetro abaixo do tecido em 80
    avatares, e a correlacao com `d3` que o Rogerio tinha visto A OLHO estava
    ali, medida, desde sempre. Custou nada achar: bastou contar sinal.

    > Regua de passa/nao-passa nao ve vies. Toda regua que devolve erro por
    > avatar tem de publicar tambem media e contagem de sinal da serie.

    A quebra por classe (d1/d2/d3) esta aqui de proposito: e ela que transforma
    "ele acha que e pior nos d3" em hipotese testada. LICOES.md 4.5j."""
    if len(serie) < 10:
        return
    import statistics as _st
    print()
    print("VIES DA SERIE (n={}) - a tolerancia acima nao ve isto".format(len(serie)))
    for nome, i in (("cos   ", 1), ("bainha", 2)):
        v = [r[i] for r in serie]
        neg = sum(1 for x in v if x < 0)
        alerta = " <<< VIES" if abs(_st.mean(v)) > VIES_MAX else ""
        print("  {}  media {:+.4f}  mediana {:+.4f}  neg {}/{}{}".format(
            nome, _st.mean(v), _st.median(v), neg, len(v), alerta))
        por = {}
        for aid, _dt, _db in serie:
            por.setdefault(aid.rsplit("_", 1)[-1], []).append(_db if i == 2 else _dt)
        print("          por classe: " + "  ".join(
            "{} {:+.4f} (n={})".format(k, _st.mean(por[k]), len(por[k]))
            for k in sorted(por)))


def main():
    argv = [x for x in sys.argv[1:]]
    modo_tracado = "--tracado" in argv
    modo_escrever = "--escrever" in argv
    argv = [x for x in argv if not x.startswith("--")]
    alvo = argv[0] if argv else None

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

    def _one(v):
        return v[0] if isinstance(v, (list, tuple)) else v

    ids = [alvo] if alvo else sorted(smap, key=lambda k: bmi.get(k, 0))

    if modo_escrever:
        if not alvo:
            print("--escrever exige um id: nunca em lote, e um avatar por vez")
            return 2
        return escrever(smap, ROOT, alvo)

    if modo_tracado:
        return tracado(smap, bmi, ids)

    print("{:<15} {:>6}  {:>16}  {:>16}  {}".format(
        "id", "imc", "COS  ref / 3d", "BAINHA ref / 3d", "erro"))
    print("-" * 82)
    fora = []
    serie = []
    for aid in ids:
        ref = zp.ref_path(ROOT, aid, "back")
        if not os.path.isfile(ref):
            print("{:<15} sem folha de costas".format(aid))
            continue
        m = medir(ref)
        if m is None:
            print("{:<15} short nao detectado na folha".format(aid))
            continue
        topo_ref, base_ref, _ = m

        e = smap.get(aid)
        if not e:
            continue
        w = e["waist_zh"]
        topo_3d = max(w) if isinstance(w, (list, tuple)) else w
        base_3d = _one(e["hem_l_zh"])

        d_topo = topo_3d - topo_ref
        d_base = base_3d - base_ref
        ruim = abs(d_topo) > 0.06 or abs(d_base) > 0.06
        if ruim:
            fora.append(aid)
        serie.append((aid, d_topo, d_base))
        print("{:<15} {:>6.1f}  {:>7.3f} /{:>7.3f}  {:>7.3f} /{:>7.3f}  {:>+6.3f} {:>+6.3f} {}".format(
            aid, bmi.get(aid, 0), topo_ref, topo_3d, base_ref, base_3d,
            d_topo, d_base, "<<" if ruim else ""))
    print("-" * 82)
    print("tolerancia +-0.06 da altura (a Meshy reinterpreta proporcao; isto pega erro grosso)")
    if fora:
        print("FORA ({}): {}".format(len(fora), ", ".join(fora)))
    else:
        print("todos dentro da tolerancia")
    _vies(serie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
