#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""morph.py - aplica os SHAPE KEYS de ajuste fino num avatar entregue.

    python scripts/morph.py zen_m_b05h_d2 --fit     # calibra e sonda, NAO grava
    python scripts/morph.py zen_m_b05h_d2 --apply   # grava o dist v(n+1)
    python scripts/morph.py zen_m_b05h_d2 --remap   # so o mapa, sem gastar versao
    python scripts/morph.py zen_m_b05h_d2 --preview # GLB em qa/preview/morph/, para olhar antes

--------------------------------------------------------------------------
POR QUE ELE LE O DIST E NAO O MASTER  (regra 9 do CLAUDE.md)
--------------------------------------------------------------------------
O master nao tem peca. Quem le o master e grava o dist APAGA o short - foi
exatamente isso que o `restyle.py --all` fez com os 39 masculinos em 31/07.
Este script le `03_dist/glb/{id}_v{n}.glb`, que ja tem material E peca, e so
ACRESCENTA shape keys: nenhum vertice da base se move, nenhum material muda.
A trava do fim confere as duas coisas contra o arquivo de entrada.

--------------------------------------------------------------------------
⚠️ O DIST TEM DUAS SUPERFICIES SOLTAS, E ISSO QUEBRA A REGUA
--------------------------------------------------------------------------
glTF quebra primitiva por material, entao corpo e short viajam separados e a
costura vem com os vertices DUPLICADOS (32.151 no disco contra 25.914+6.237).
Para o `metrics.py`, que separa medida por TOPOLOGIA, isso vira uma ilha a
mais: na faixa de altura do short a fatia devolve lacos extras, o `r[1:]` que
descarta o tronco descarta a peca errada e o numero sai de outro lugar do
corpo. Medido, lendo o dist cru: antebraco **48,3 cm** onde o
`library_metrics.json` diz 29,8, e cintura 86,2 onde ele diz 101,3.

Por isso a medida roda numa copia SOLDADA (`remove_doubles`), e o campo de
deformacao e uma funcao da POSICAO - avaliada na copia soldada para calibrar e
na malha real, com os vertices duplicados, para gravar o shape key. Os dois
lados da costura recebem o mesmo deslocamento e ela nao abre.

A trava disso e o §CONFERENCIA: a regua sobre a base tem que reproduzir o
`library_metrics.json`. Regua que nao reproduz a medida publicada nao calibra
morph nenhum.

--------------------------------------------------------------------------
A REGUA E A DO metrics.py, NAO UMA PARECIDA
--------------------------------------------------------------------------
As sondas `morph_lab*.py` mediam por casco convexo da fatia com o braco
removido "por identidade". Serve para pesquisa, mas o numero que o app compara
com a fita do usuario e o do `metrics.py`. Aqui a calibracao chama as funcoes
DAQUELE arquivo sobre a malha deformada - assim "o morph vale +6 cm de ombro"
quer dizer +6 cm *na mesma regua* que produziu o `library.json`.

--------------------------------------------------------------------------
IDENTIDADE E LANDMARK SE DECIDEM NA MALHA BASE  (LICOES.md 7.7)
--------------------------------------------------------------------------
Quem e braco, quem e perna, quem e rosto, onde esta a axila, a virilha e o
pulso: tudo sai da malha sem deformacao, uma vez. Vale para as MASCARAS (a
primeira versao do morph de biceps selecionava o braco sobre as posicoes ja
morfadas e a busca divergiu) e vale tambem para as ANCORAS DA REGUA: o
antebraco e medido entre o pulso e o meio do braco, e se o pulso for
reprocurado a cada amplitude a janela anda junto com o morph e o cm deixa de
ser comparavel. Foi o que produziu "-17,7 cm em toda influence negativa" na
primeira rodada desta calibracao.

--------------------------------------------------------------------------
O CONTRATO COM O APP
--------------------------------------------------------------------------
`config/morph_map.json` publica, por morph:
    key             nome do shape key no GLB (== targetNames do glTF)
    column          a coluna de medida do app que ele corrige
    cm_at_full      quantos cm a coluna anda com influence = 1.0
    influence_min   limite seguro NEGATIVO (medido, nao proposto)
    influence_max   limite seguro POSITIVO (medido)
E o app faz:
    inf = clamp((usuario_cm - avatar_cm) / cm_at_full, influence_min, influence_max)

⚠️ O GLB sai com DUAS primitivas. Cada uma vira um THREE.Mesh com o SEU
proprio `morphTargetInfluences`; quem so setar no primeiro morfa o corpo e
deixa o short parado. Percorrer a arvore inteira.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as mt          # noqa: E402  - a regua oficial
import zenith_paths as _zp    # noqa: E402

try:
    import bpy                # noqa: F401
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


# ==========================================================================
#  A TABELA DOS MORPHS
# ==========================================================================
# `cm_at_full` e a UNIDADE, nao o limite: quanto a coluna anda com o shape key
# em 1.0. O limite sai da varredura e vai medido para o mapa. Os numeros aqui
# sao redondos de proposito, para o app poder dizer "+6 cm de ombro" sem conta.
# ⚠️ `cal_sign` existe por causa do PESCOCO, e a razao e estrutural, nao um
#    ajuste: ele e um MINIMO de banda travado pelo queixo, entao CRESCER satura
#    (+2,2 cm por mais amplitude que se dê) enquanto REDUZIR responde. Calibrar
#    pelo lado que satura faz a busca de amplitude fugir para o teto - mediu
#    0,060 m, e nesse tamanho o lado negativo virou -19 cm com 206 triangulos
#    invertidos. Quem tem lado saturado calibra pelo outro.
#
# ⚠️ `cal_column` SEPARA A REGUA QUE CALIBRA DA REGUA QUE SE PUBLICA, e existe
#    por uma razao de CUSTO, medida em 21/08.
#
#    Quando o app trocou a cintura de `waist_min` para `waist_navel`, a coluna
#    publicada tinha que mudar junto - senao `morph_cases.solve()` zera o morph
#    (coluna que a selecao descartou nao morfa, LICOES 7.18), e foi exatamente o
#    que aconteceu: 357 dos 608 casos zeraram `morph_waist` de uma vez.
#
#    Mas a AMPLITUDE e outra coisa. Ela e escolhida pela busca de `cm_at_full`,
#    e o deslocamento resultante esta GRAVADO NO GLB. Recalibrar a amplitude
#    numa coluna nova muda o deslocamento, o `--remap` recusa (guarda de 0,2 mm)
#    e a saida vira `--apply` nos 76: versao nova de GLB, Storage desatualizado e
#    aprovacao visual de novo - tudo isso para mudar de que altura sai o
#    centimetro, o que nao e motivo para mexer em geometria aprovada.
#
#    Entao a amplitude continua sendo calibrada em `waist_min` e a CURVA e o
#    `base_cm` saem em `waist_navel`. O mapa publica a promessa medida na regua
#    que o app usa; o arquivo nao muda um vertice. `cm_at_full` deixa de ser
#    redondo neste morph, e nao faz mal - o cabecalho do mapa ja avisa que quem
#    multiplica `cm_at_full x influence` erra, e que a promessa e a CURVA.
MORPHS = [
    {"key": "morph_neck",     "column": "neck",      "cm_at_full": 6.0, "cal_sign": -1},
    {"key": "morph_shoulder", "column": "shoulder",  "cm_at_full": 6.0},
    {"key": "morph_chest",    "column": "chest",     "cm_at_full": 6.0},
    {"key": "morph_waist",    "column": "waist_navel",
     "cal_column": "waist_min", "cm_at_full": 10.0},
    {"key": "morph_hip",      "column": "hip",       "cm_at_full": 8.0},
    {"key": "morph_biceps",   "column": "biceps",    "cm_at_full": 4.0},
    {"key": "morph_forearm",  "column": "forearm",   "cm_at_full": 3.0},
    {"key": "morph_thigh",    "column": "thigh",     "cm_at_full": 6.0},
    {"key": "morph_calf",     "column": "calf",      "cm_at_full": 3.0},

    # ⚠️ ACHATAMENTO DA CINTURA - o unico morph que NAO tem coluna de medida.
    #     Ele muda a FORMA da secao (largura contra profundidade) a perimetro
    #     ~constante, e existe porque fechar centimetro nao e o mesmo que
    #     parecer com a pessoa. Medido no corpo do Rogerio: o `morph_waist`
    #     isotropico acertou o perimetro (+5,6 cm) e DOBROU o erro no eixo que o
    #     olho ve - a barriga foi de 1,9 para 3,6 cm mais funda que a dele.
    #     Perimetro e o que a fita mede; profundidade e o que aparece de perfil.
    #
    #     `couple` diz ao app: aplique este junto com o `morph_waist`, mas SO
    #     quando ele for positivo. Reduzir cintura tem que perder profundidade
    #     (e o que emagrecer faz), entao a reducao continua isotropica.
    #
    #     `depth_column` e o criterio de calibracao: a amplitude e a que devolve a
    #     PROFUNDIDADE da base quando o `morph_waist` esta em +1,0. E o default
    #     conservador - o morph deixa de piorar o eixo visivel, sem apostar em
    #     nenhuma forma de corpo.
    {"key": "morph_waist_flatten", "column": None, "kind": "flatten",
     "couple": "morph_waist", "couple_when": "positive",
     "depth_column": "_waist_depth"},

    # ⚠️ QUADRIL e PEITORAL ganharam o mesmo tratamento em 16/08, a pedido dele.
    #     O raciocinio e identico ao da cintura e ja estava escrito como
    #     pendencia desde 06/08: morph radial uniforme PRESERVA a forma da
    #     secao, entao fechar centimetro de perimetro custa profundidade — e
    #     profundidade e o eixo que aparece de perfil e de 3/4.
    #
    #     Cada um mede a SUA profundidade, na altura em que a SUA regua le:
    #     `_hip_depth` no maximo da banda do quadril, `_chest_depth` na fracao
    #     do peito. Reaproveitar a altura da cintura seria calibrar a forma de
    #     uma secao medindo outra.
    #
    #     Mesmo default conservador: a amplitude e a que devolve a profundidade
    #     da BASE quando o morph de tamanho esta em +1,0. Nao se mira forma de
    #     ninguem — com UM corpo real medido no projeto inteiro, mirar uma razao
    #     seria embutir aquele corpo como padrao de todo mundo.
    {"key": "morph_hip_flatten", "column": None, "kind": "flatten",
     "couple": "morph_hip", "couple_when": "positive",
     "depth_column": "_hip_depth"},
    {"key": "morph_chest_flatten", "column": None, "kind": "flatten",
     "couple": "morph_chest", "couple_when": "positive",
     "depth_column": "_chest_depth"},
]

# Quanto o morph de TAMANHO precisa afundar a secao para valer a pena publicar o
# morph de FORMA junto. Abaixo disso a busca devolveria amplitude ~0 e o que
# sairia e uma shape key que nao move nada e mesmo assim carrega um target
# esparso de milhares de vertices no GLB.
FLATTEN_MIN_GANHO_CM = 0.2

# Amplitudes varridas para achar onde cada morph quebra. Passa do util de
# proposito: faixa so vale medida ate o defeito aparecer.
SWEEP = [-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0]

# ⚠️ TETO DE INFLUENCE, E ELE VEIO DA FOTO, NAO DAS SONDAS.
# Em influence -2,0 as sondas numericas devolvem ZERO normal invertida no
# ombro, no biceps e no antebraco - e a foto mostra braco cordao, degrau no
# deltoide e vinco na juncao do trapezio. E a §7.5 do LICOES.md acontecendo de
# novo: sonda diz ONDE olhar, foto diz SE esta bom.
#
# O teto e POR MORPH desde 06/08, e nao mais um numero unico. O ±1,0 nasceu da
# foto do BRACO, e aplica-lo a panturrilha era generalizar um veredito visual
# de uma regiao para outra: a panturrilha e um cilindro isolado, varreu limpa
# ate ±2,0 (±6 cm) com ZERO normal invertida, e o teto unico estava cortando
# metade da faixa dela a toa - justo numa das duas colunas que sobram no corpo
# do Rogerio.
#
# ⚠️ TODO valor acima de 1,0 aqui precisa de RENDER OLHADO naquele extremo.
# Numero nesta tabela sem foto correspondente e exatamente o erro que a §7.5
# documenta.
# O pescoco ESTEVE aqui com 1,5 e saiu: o 1,5 foi posto esperando ganho no lado
# da REDUCAO, e la a sonda e a foto reprovaram juntas (-9,3 cm faz degrau na
# base contra o trapezio). Sobrava so o lado do crescimento, que renderia +0,2
# cm - e eu nao renderizei o pescoco em +1,5. Numero sem foto nao fica na
# tabela, e a regra acima vale tambem para mim.
#
# 🔴 O PESCOCO VOLTA COM TETO ASSIMETRICO: -0,5 / +1,0 (sessao 41, 27/09).
# Reprovado no olho dele no testador: *"o morph do pescoco entrou no vale da
# estranheza"* (zen_m_b05k_d1, pescoco 48,7 cm pedido em 42). Em -1 (-6 cm) a
# sonda contava zero invertida e a foto mostrava o pescoco virando HASTE - anel
# na nuca, vinco na furcula, perfil concavo -, porque so o anel encolhe entre
# cabeca e trapezio parados. Em -0,5 (-2,6 cm) as tres vistas ficam naturais.
# Subir o piso da mascara (0,800 e 0,815) foi testado: melhora a frente e PIORA
# o anel da nuca - refutado. O resto do pedido aparece como sobra.
# Tupla = (teto do lado negativo, teto do lado positivo).
INFLUENCE_CAP = {"morph_calf": 2.0, "morph_neck": (0.5, 1.0)}
INFLUENCE_CAP_PADRAO = 1.0

# A regua sobre a base tem que bater com o library_metrics.json. Acima disto o
# script para: a divergencia significa que ele nao esta medindo o mesmo corpo.
TOL_BASE_CM = 0.6

MAP_PATH = "config/morph_map.json"

# Corte braco/tronco em distancia ao eixo do braco (ver `Base._corte_braco`).
# Era booleano a 8 cm ate a sessao 41; braco grosso atravessava (LICOES 7.27).
BRACO_CORTE = 0.080
BRACO_CORTE_MIN = 0.070  # o corte em rampa nunca comeca antes disto do eixo
BRACO_FOLGA = 0.006     # a pele tem que ficar a 6 mm do corte, senao ele anda
BRACO_RAMPA = 0.015
BRACO_RAZAO_MAX = 2.0   # raio por fatia / raio do biceps publicado: acima disto nao e braco
BRACO_TRECHO = 0.85     # so o braco LIVRE: os ultimos 15% antes da fusao abrem para o tronco
BICEPS_TOPO_L = (0.65, 0.85)  # topo da faixa do biceps em fracao do UMERO (cotovelo=0, cabeca=1): plato ate 0,65, zero em 0,85 (sessao 41)
# 🔴 O PESCOCO E UM CILINDRO, NAO UMA FAIXA DE ALTURA (sessao 41, 30/09).
# A mascara antiga subia de 0,760 a 0,835 da altura e empurrava TUDO naquela
# faixa a partir do eixo do pescoco - trapezio, alto do ombro, alto do peito e
# das costas. A regua do ombro le a 0,795, dentro dela: com o pescoco no
# extremo o OMBRO andava ate 7,7 cm (m_b07_d3) e 6,9 (m_b05k_d1), somando por
# cima do morph do ombro no app. E na frente o teto caia 5,5 cm antes do
# queixo, entao o pescoco so ficava cheio num ANEL na base - o que ele viu:
# *"o morph pega somente numa parte, precisamos que ele pegue todo o pescoco"*.
# Agora: cheio ate PESCOCO_RAIO[0] raios do pescoco, zero em [1]; teto com
# rampa de PESCOCO_TOPO. Medido: ombro vaza 0,1-1,3 cm (era ate 7,7).
# ❌ Raio 1,25-1,75 zerou o vazamento e fez GOLA na base (degrau em +0,5 e
# colarinho em -0,5, no render). ❌ Topo de 2 cm deixou faixa sob o queixo.
# 🔴 Sessao 42 (01/10): o cilindro virou ENVELOPE. Dentro dele o peso e o campo
# natural do tipo de corpo (config/pescoco_campo.json); cheio por igual, ele
# fazia o "cano" no maximo (LICOES 7.30). Piso e teto agora contam do QUEIXO.
PESCOCO_RAIO = (1.3, 3.0)
# Sessao 42 (01/10): piso e teto passaram a ser medidos a partir do QUEIXO de
# cada corpo (fracao de H), nao em fracao fixa - o queixo vai de 0,85 a 0,89 da
# altura na colecao. Piso: cheio a partir de 5,5% abaixo do queixo (a furcula
# fica em ~4,5%). Teto: na frente zera 0,6% ACIMA do queixo (a garganta sob a
# mandibula tem que andar, e onde a regua le), na nuca 4% acima; rampa de 1%.
# ❌ Zerar a frente em 0,9% (rampa cheia na altura da regua) foi testado: a
# naturalidade do zen_f_b07i_d1 so foi de 1,55 a 1,52 e o zen_m_b01_d1 perdeu o
# +1 pela trava de rosto. Nao e a rampa que faz a regua responder menos.
PESCOCO_PISO = (-0.085, -0.055)
PESCOCO_TETO = (0.006, 0.040)
PESCOCO_TOPO = 0.010
# ⚠️ Olhado nos 103 no maximo do slider (sessao 42): com o piso de tras valendo
# tambem na FRENTE, o morph empurrava a pele inclinada do alto do esterno e
# abria um ENTALHE ali (zen_m_b07h_d1, zen_f_b05_d2). A frente para na furcula.
# ❌ Rampa curta (-0,060/-0,040) fez DEGRAU na clavicula dos obesos: 4% de H.
PESCOCO_PISO_FRENTE = (-0.080, -0.040)
# ... e nos corpos em que a regua le ACIMA do queixo (18, os obesos e alguns
# musculosos de pescoco grosso), a rampa de 1% cortava a papada no meio: quina
# ao longo da mandibula e canto da boca puxado (zen_m_b05i_d1, zen_m_b08_d1). La
# a frente esmaece por toda a papada, do queixo ate a regua. Nos lados a rampa
# cresce ate PESCOCO_TOPO_LADO: risco fino no lado do pescoco (zen_f_b09j_d1).
PESCOCO_TOPO_LADO = 0.016
PESCOCO_NATURAL_MAX = 1.3   # amplitude <= 1,3x a natural do tipo (ver worker_main); 1,6 ainda deixava o V no zen_m_b09_d2
SONDA_MOV_MIN = 0.004   # 4 mm: triangulo que vira andando menos que isto nao se ve (foto, sessao 41)
TRONCO_CENTRO_ALISA = 5   # fatias de 1 cm na media movel do centro do tronco (sessao 41)
BICEPS_RAMPA_MIN = 0.030   # rampa de cima da faixa do biceps nunca menor que isto (sessao 41)

# ⚠️ O DELTOIDE (25/09, sessao 40). Ate aqui o `morph_shoulder` era um BLOCO
# em Z (0,745-0,885 da altura) por |x| > 0,055 H, empurrado so em +X: uma
# "dragona" que escorregava o ombro inteiro de lado - trapezio, alto do peito
# e costas juntos - com um corte HORIZONTAL atravessando o braco inclinado.
# No obeso (zen_m_b12_d1) o bloco era metade do peito e das costas. Queixa
# dele (25/09): "a localizacao ... estava um pouco errada, principalmente nos
# ombros". Hoje e uma CAPSULA em volta do eixo do braco, fechada na cabeca do
# umero (ver `Base._ombro_landmarks` e `Base._deltoide`). Os numeros abaixo
# sao multiplos do RAIO DO BRACO, para a calota escalar com o corpo:
OMBRO_CABECA_R = 1.1           # raio do circulo inscrito no canto do ombro
OMBRO_R = (1.2, 2.9)           # queda radial: cheia ate 1,2 R, zero em 2,9 R
OMBRO_DESCE = (1.2, 3.6)       # desce pelo braco: cheia ate 1,2 R, zero em 3,6 R
OMBRO_LAT = (-1.0, 0.35)       # face da axila fora (cosseno com "para fora")
OMBRO_R_BRACO = (0.028, 0.075)  # trava de sanidade do raio (m)
OMBRO_R_BRACO_PISO = 0.205     # ... e piso relativo ao raio do anel do ombro
# A calota ESTREITA (1,3-2,1 R) foi testada antes e reprovada no olho: na magra
# (zen_f_b01_d1) +1 virava uma BOLA sobre o ombro e -1 deixava degrau na borda
# de baixo. A larga distribui os mesmos +6 cm e as duas coisas somem.


# ==========================================================================
#  DRIVER
# ==========================================================================

def driver_main():
    ap = argparse.ArgumentParser(description="Shape keys de ajuste fino no avatar entregue.")
    ap.add_argument("avatar_id")
    ap.add_argument("--fit", action="store_true",
                    help="calibra e sonda, sem gravar nada em 03_dist/")
    ap.add_argument("--apply", action="store_true",
                    help="grava 03_dist/glb/{id}_v(n+1).glb e o config/morph_map.json")
    ap.add_argument("--remap", action="store_true",
                    help="so reescreve o config/morph_map.json contra o dist "
                         "CORRENTE, sem exportar GLB nem gastar versao")
    ap.add_argument("--preview", action="store_true",
                    help="grava o GLB com shape keys em qa/preview/morph/{id}.glb - "
                         "sem mapa, sem versao, sem aposentar nada")
    args = ap.parse_args()
    if not (args.fit or args.apply or args.remap or args.preview):
        ap.error("escolha --fit (so mede), --apply (grava), --remap (so o mapa) "
                 "ou --preview (GLB em qa/, para olhar antes)")
    if sum([args.apply, args.remap, args.preview]) > 1:
        ap.error("--apply, --remap e --preview sao excludentes")

    root = mt.repo_root()
    _zp.sex_of(args.avatar_id)                     # estoura em id malformado
    ver, src = _zp.dist_glb_current(root, args.avatar_id)
    if src is None:
        sys.exit("nao existe 03_dist/glb/{}_v*.glb - rode process.py/shorts.py antes."
                 .format(args.avatar_id))
    print("entrada: {} (v{})".format(os.path.basename(src), ver))

    cmd = [mt.find_blender(), "--background", "--python", os.path.abspath(__file__), "--",
           "--worker", "--root", root, "--id", args.avatar_id]
    if args.apply:
        cmd.append("--apply")
    if args.remap:
        cmd.append("--remap")
    if args.preview:
        cmd.append("--preview")
    sys.exit(subprocess.run(cmd).returncode)


# ==========================================================================
#  GEOMETRIA
# ==========================================================================

def sstep(x, a, b):
    """Rampa suave de a ate b. `a`/`b` podem ser array - o teto da mascara do
    pescoco depende de Y (fecha antes na frente do que atras)."""
    import numpy as np
    larg = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    t = np.clip((x - a) / np.where(np.abs(larg) < 1e-9, 1e-9, larg), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _rampa_min(a, b, r):
    """(a, b) alargado para b - a >= r, em volta do meio."""
    if b - a >= r:
        return a, b
    c = 0.5 * (a + b)
    return c - 0.5 * r, c + 0.5 * r


def band(x, lo0, lo1, hi0, hi1):
    """Janela suave: sobe de lo0 a lo1, desce de hi0 a hi1."""
    return sstep(x, lo0, lo1) * (1.0 - sstep(x, hi0, hi1))


CAMPO_PESCOCO_PATH = "config/pescoco_campo.json"
_CAMPO_PESCOCO = {}


def _campo_pescoco(aid):
    """A entrada do avatar no config/pescoco_campo.json (frente, queixo, W).
    Sem entrada o script PARA: cair num campo generico seria voltar ao
    cilindro igual para todos, que e o defeito que este arquivo conserta."""
    if not _CAMPO_PESCOCO:
        p = os.path.join(mt.repo_root(), CAMPO_PESCOCO_PATH)
        if not os.path.exists(p):
            sys.exit("falta {} - rode scripts/pescoco_campo.py".format(CAMPO_PESCOCO_PATH))
        _CAMPO_PESCOCO.update(json.load(open(p, encoding="utf8")))
    e = _CAMPO_PESCOCO["avatars"].get(aid)
    if e is None:
        sys.exit("{} sem entrada em {} - rode scripts/pescoco_campo.py".format(
            aid, CAMPO_PESCOCO_PATH))
    return dict(e, _hq=_CAMPO_PESCOCO["hq"], _theta=_CAMPO_PESCOCO["theta"])


def _bilinear(xs, ys, T, x, y):
    """T[i][j] na grade (xs[i], ys[j]), avaliada em (x, y); fora da grade, a borda."""
    import numpy as np
    fx = np.interp(x, xs, np.arange(len(xs)))
    fy = np.interp(y, ys, np.arange(len(ys)))
    i0 = np.clip(np.floor(fx).astype(int), 0, len(xs) - 2)
    j0 = np.clip(np.floor(fy).astype(int), 0, len(ys) - 2)
    ax, ay = fx - i0, fy - j0
    return ((1 - ax) * (1 - ay) * T[i0, j0] + ax * (1 - ay) * T[i0 + 1, j0]
            + (1 - ax) * ay * T[i0, j0 + 1] + ax * ay * T[i0 + 1, j0 + 1])


class Base(object):
    """Os landmarks e os perfis, decididos UMA VEZ na malha soldada e sem
    deformacao. Nada aqui depende da lista de vertices: os perfis de centro
    sao curvas em Z, e por isso o mesmo campo pode ser avaliado na malha real
    (com a costura duplicada) sem recalcular nada."""

    def __init__(self, co, mesh, aid=None):
        self.aid = aid
        import numpy as np
        self.co, self.mesh = co, mesh
        self.n = len(co)
        self.zmin = float(co[:, 2].min())
        self.H = float(co[:, 2].max()) - self.zmin
        z, H = self.zmin, self.H

        # --- ate onde braco e perna ainda sao lacos proprios (regua oficial)
        self.arm_split = mt.find_armpit(mesh, z, H)
        self.leg_split = mt.find_crotch(mesh, z, H)
        self.crotch = z + mt.CROTCH_FRAC * H
        self.armpit = z + mt.ARMPIT_FRAC * H
        self.leg_top = self.leg_split if self.leg_split else self.crotch

        # --- EIXO DO BRACO. O empurrao do biceps/antebraco e PERPENDICULAR a
        # ele: em A-pose um empurrao horizontal engorda na diagonal e sobe a
        # medida errada.
        self.fusao_f = ((self.arm_split - z) / H) if self.arm_split else 0.72
        pts = []
        for f in np.arange(0.42, self.fusao_f - 0.01, 0.01):
            g = self._gap_braco(co, z + f * H)
            if not g:
                continue
            b = co[np.abs(co[:, 2] - (z + f * H)) < 0.008]
            a = b[b[:, 0] > g[1] - 0.005]
            if len(a) >= 6:
                pts.append(a.mean(axis=0))
        pts = np.array(pts)
        self.arm_c = pts.mean(axis=0)
        e = np.linalg.svd(pts - self.arm_c)[2][0]
        self.arm_e = e if e[2] >= 0 else -e

        # --- ANCORAS DA REGUA DO BRACO, congeladas (ver cabecalho)
        self.arm_top = (self.armpit if self.arm_split is None
                        else min(self.armpit, self.arm_split)) - mt.ARM_PAD_M
        w = mt.pair_extreme(mesh, self.crotch, self.arm_top, True, "min")
        self.z_pulso = w[3] if w else z + 0.56 * H
        self.z_meio = (self.z_pulso + self.arm_top) / 2.0

        # --- AS MESMAS ANCORAS, PROJETADAS NO EIXO DO BRACO (14/08).
        # O braco em A-pose sai a ~24 graus da vertical, entao faixa de Z
        # GLOBAL corta o braco na DIAGONAL: a mesma fatia pega biceps de um
        # lado e cotovelo do outro. Foi por isso que duas tentativas de
        # reposicionar o morph do biceps em Z falharam no testador (prints do
        # Rogerio, 14/08). `t` = projecao no eixo do proprio membro, entao a
        # faixa acompanha a inclinacao e vale igual nos dois bracos.
        d0, _, _ = self._dist_eixo(co)
        _br = (co[:, 0] > 0) & (d0 < 0.080)
        _t = (co[_br] - self.arm_c) @ self.arm_e
        _zb = co[_br][:, 2]

        def _t_em(z_alvo, meia=0.012):
            """t medio dos vertices do braco na altura z_alvo."""
            m = np.abs(_zb - z_alvo) < meia
            return float(_t[m].mean()) if m.sum() >= 4 else None

        self.t_pulso = _t_em(self.z_pulso)
        self.t_top = _t_em(self.arm_top)
        # teto: onde o braco funde no tronco. Acima daqui a mascara pegaria
        # deltoide/peito, e `no_braco` sozinho nao segura (a reta do eixo,
        # estendida, passa perto do pescoco - a sonda achou ate vertice de
        # CABECA em t alto).
        self.t_fusao = _t_em(self.arm_split if self.arm_split else self.armpit)
        if self.t_pulso is None or self.t_top is None:
            self.t_pulso, self.t_top = -0.06, 0.23      # fallback medido
        if self.t_fusao is None or self.t_fusao <= self.t_top:
            self.t_fusao = self.t_top + 0.35 * (self.t_top - self.t_pulso)

        # --- PERFIL DO CENTRO DO TRONCO, com o braco fora da conta. O push
        # radial sai daqui: o tronco nao e cilindro centrado, e usar o eixo
        # global empurraria a barriga so para a frente.
        d_dir, _, _ = self._dist_eixo(co)
        d_esq, _, _ = self._dist_eixo(co * np.array([-1.0, 1.0, 1.0]))
        E_BRACO = np.minimum(d_dir, d_esq) < 0.085
        self.tz, self.tc = self._perfil_tronco(co, ~E_BRACO, z + 0.30 * H, z + 0.98 * H)

        # --- PERFIL DE CADA PERNA, e o VAO entre elas por altura. O vao e o
        # que impede o morph de coxa/quadril de empurrar uma perna contra a
        # outra: onde elas ja se tocam, a componente para dentro morre.
        #
        # ⚠️ `~E_BRACO` NAO E DECORACAO AQUI. Em A-pose a MAO pousa em z/H 0,44
        # a 0,47, que e dentro da faixa da coxa: sem tirar o braco, ela entra
        # no centroide da perna e, pior, recebe o empurrao radial da coxa. Foi
        # o que produziu 68 a 538 triangulos invertidos em TODA amplitude, e os
        # invertidos estavam em |x| = 43 cm - o dedo, nao a perna.
        self.lz, self.lc = {}, {}
        for sg in (+1.0, -1.0):
            sel = (co[:, 0] * sg > 0) & (co[:, 2] < self.leg_top) & (~E_BRACO)
            self.lz[sg], self.lc[sg] = self._perfil(co, sel, z + 0.06 * H, self.leg_top)
        self.gz, self.gv = self._perfil_vao(co)
        self.az, self.av = self._perfil_axila(co)

        # --- PESCOCO: eixo, frente, queixo (LICOES.md 7.5 e 7.30)
        # 🔴 FRENTE e QUEIXO vem do `config/pescoco_campo.json` desde a sessao
        # 42 (01/10), nao mais daqui. A frente era "o lado do rosto mais longe
        # de y=0" e ERRAVA EM 30 DE 103 - no corpo pesado o centro da caixa vai
        # para a frente e a nuca fica mais longe que o nariz. Nesses o morph do
        # pescoco empurrava o QUEIXO e poupava a nuca, e a trava de rosto olhava
        # a nuca. E o queixo por "salto de 25%" nao existe no obeso (pescoco em
        # cone ate o rosto): caia no fim da varredura. Ver scripts/pescoco_campo.py.
        zs = np.arange(z + 0.80 * H, z + 0.92 * H, 0.005)
        cen = np.array([co[np.abs(co[:, 2] - t) < 0.006][:, :2].mean(axis=0) for t in zs])
        self.nx, self.ny = float(cen[:, 0].mean()), float(cen[:, 1].mean())
        cp = _campo_pescoco(aid)
        self.frente = float(cp["frente"])
        self.z_queixo = z + float(cp["queixo_h"]) * H
        self.pesc_W = np.array(cp["W"], float)
        self.pesc_hq = np.array(cp["_hq"], float)
        self.pesc_th = np.array(cp["_theta"], float)
        self.pesc_s_ref = float(cp["s_ref_mm_cm"])
        # ⚠️ Nos corpos de IMC > 60 a regua do pescoco (minimo da banda) le na
        # BORDA de cima, 0,900 - acima do queixo, na papada. Proteger o rosto a
        # partir do queixo deixava a regua parada (zen_m_b10_d1: amplitude no
        # teto, 0 cm, 131 triangulos invertidos). Ali o pescoco medido E a
        # papada, e no tipo pesado ela cresce junto (o campo mostra), entao o
        # rosto protegido comeca acima de onde a regua le.
        self.z_regua_pesc = float(mt.torso_extreme(
            mesh, z + mt.NECK_BAND[0] * H, z + mt.NECK_BAND[1] * H, "min")[1])
        self.z_rosto = max(self.z_queixo, self.z_regua_pesc)
        # raio do pescoco onde a regua le (minimo da banda) - escala do cilindro
        rs = []
        for zz in np.arange(z + mt.NECK_BAND[0] * H, z + mt.NECK_BAND[1] * H, 0.004):
            bb = co[np.abs(co[:, 2] - zz) < 0.003]
            rr = np.hypot(bb[:, 0] - self.nx, bb[:, 1] - self.ny)
            rr = rr[rr < 0.12]
            if len(rr) > 8:
                rs.append(float(np.median(rr)))
        self.r_pescoco = min(rs) if rs else 0.060

        self.tris = mesh.tris
        self.nrm0, self.area0 = self.normais(co)
        self._ombro_landmarks(co)
        self._corte_braco(co, aid)
        # Piso de area para a sonda de inversao: abaixo dele a normal e ruido
        # numerico, nao dobra de superficie. Sem o piso um unico triangulo
        # lasca condenava a faixa inteira de um morph.
        self.area_min = float(np.median(self.area0)) * 0.02

    # ------------------------------------------------------------- ombro
    def _ombro_landmarks(self, co):
        """A CABECA DO UMERO, decidida na malha base (LICOES 7.7).

        O deltoide e uma CALOTA em volta da cabeca do umero. Tres jeitos de
        achar o centro dela foram testados em 25/09; so o terceiro presta:
          1. estender o eixo do braco para cima: o braco em A-pose inclina
             tambem em PROFUNDIDADE (~0,22 em Y), e a reta sai pelas costas
             do ombro 3 cm abaixo do topo;
          2. estender so a vista frontal do eixo ate a silhueta de cima: o
             eixo passa por DENTRO do ombro e so sai no trapezio (x 13 cm no
             zen_m_b05h_d2, contra 20 do acromio);
          3. o CIRCULO INSCRITO no canto do ombro, na silhueta frontal -
             tangente a borda lateral (deltoide) e a de cima (acromio). O
             centro dele e a cabeca do umero; o Y e o meio do corpo ali.
        O raio da calota vem do braco livre logo abaixo da fusao, entao ela
        escala com o corpo - magro, obeso, feminino - sem numero em metro."""
        import numpy as np
        z, H = self.zmin, self.H
        secs = []
        for f in np.arange(self.fusao_f - 0.045, self.fusao_f - 0.004, 0.005):
            g = self._gap_braco(co, z + f * H)
            if not g:
                continue
            b = co[np.abs(co[:, 2] - (z + f * H)) < 0.004]
            a = b[b[:, 0] > g[1] - 0.003]
            if len(a) >= 8:
                secs.append(a)
        if secs:
            raios = [float(np.median(np.linalg.norm(a[:, :2] - a[:, :2].mean(axis=0), axis=1)))
                     for a in secs]
            # a secao horizontal de um cilindro inclinado e uma ELIPSE: o raio
            # medio dela superestima o raio do braco no eixo maior.
            self.r_braco = float(np.median(raios)) * (0.5 + 0.5 * abs(self.arm_e[2]))
        else:
            self.r_braco = 0.045
        # ⚠️ Corpo obeso funde o braco cedo e a "fatia livre" pega tronco: o
        # zen_m_b12_d1 media 19,7 cm de raio e o ombro morria. Trava + aviso.
        if not (OMBRO_R_BRACO[0] <= self.r_braco <= OMBRO_R_BRACO[1]):
            print("ombro: raio de braco {:.1f} cm fora de {:.1f}-{:.1f} - travado".format(
                self.r_braco * 100, OMBRO_R_BRACO[0] * 100, OMBRO_R_BRACO[1] * 100))
            self.r_braco = float(np.clip(self.r_braco, *OMBRO_R_BRACO))
        # ⚠️ PISO pelo tamanho do corpo. No acervo o raio do braco fica entre
        # 21% e 35% do raio do anel do ombro (mediana 26%); o zen_f_b12_d1 (IMC
        # 114, braco fundido) mediu 17,8% e a calota saiu pequena e ALTA - em
        # +1 virava um calombo no alto do ombro. O piso so alcanca quem esta
        # fora da populacao sadia.
        anel = mt.torso_at(self.mesh, z + mt.SHOULDER_FRAC * H)
        if anel:
            piso = OMBRO_R_BRACO_PISO * anel / (2 * np.pi)
            if self.r_braco < piso:
                print("ombro: raio de braco {:.1f} cm abaixo do piso {:.1f} ({:.0f}% do anel "
                      "do ombro) - erguido".format(self.r_braco * 100, piso * 100,
                                                   OMBRO_R_BRACO_PISO * 100))
                self.r_braco = float(piso)
        z_fusao = float((self.arm_c + self.t_fusao * self.arm_e)[2])
        direita = co[(co[:, 0] > 0.02) & (co[:, 2] < z + 0.90 * H)]
        Rc = OMBRO_CABECA_R * self.r_braco

        def x_fora(zz):
            b = direita[np.abs(direita[:, 2] - zz) < 0.004]
            return float(b[:, 0].max()) if len(b) else None

        def z_topo(xx):
            b = direita[np.abs(direita[:, 0] - xx) < 0.004]
            return float(b[:, 2].max()) if len(b) else None

        cx = cz = None
        for zz in np.arange(z_fusao, z + 0.88 * H, 0.002):
            xo = x_fora(zz)
            if xo is None:
                continue
            zt = z_topo(xo - Rc)
            if zt is not None and zt - zz <= Rc:
                cx, cz = xo - Rc, float(zz)
                break
        if cx is None:
            print("ombro: canto do ombro nao achado - centro no eixo, a 0,80 H")
            cx, cz = float((self.arm_c + self.t_fusao * self.arm_e)[0]), z + 0.80 * H
        # O Y e o meio da CALOTA, nao do corpo: so o que esta ALEM do centro em
        # x (deltoide puro). A coluna inteira naquele x pegava o alto do peito,
        # e num busto volumoso (zen_f_b09j_d1) o centro caiu na FRENTE do ombro
        # (y -0,8 contra +4 a +5 no acervo) - a calota escorria para o peito e
        # o morph morreu.
        fat = co[(co[:, 0] > cx) & (np.abs(co[:, 2] - cz) < 0.012)]
        cy = float((fat[:, 1].max() + fat[:, 1].min()) / 2) if len(fat) > 4 else float(self.arm_c[1])
        self.C_ombro = np.array([cx, cy, cz])
        print("ombro: r_braco {:.1f} cm | cabeca do umero z/H {:.3f} x {:.1f} y {:+.1f} cm".format(
            self.r_braco * 100, (cz - z) / H, cx * 100, cy * 100))

    def _corte_braco(self, co, aid=None):
        """ONDE ACABA O BRACO, em distancia ao eixo - e o corte tem que ficar
        FORA do membro.

        Ate a sessao 41 era fixo em 8,0 cm (`d < 0.080`, booleano). O braco
        grosso passa disso: o zen_m_b08_d3 (biceps 62 cm) tem a pele a 8,6-9,3
        cm do eixo no biceps, e o zen_f_b09i_d3 a 7,7 - 3 mm do corte. Um
        vertice anda, o vizinho fica, o triangulo entre os dois inverte e o
        morph do biceps morre justo no corpo de quem treina (LICOES 7.27).

        O raio e o p98 da distancia ao eixo POR FATIA do braco livre, e o
        corte sai do MAIOR deles. ⚠️ So ate 85% do caminho pulso->fusao: colada
        na fusao a fatia abre para o tronco (11-14 cm no b08_d3), e o p98
        global dessa regiao deu 20-28 cm nos obesos - o corte engolia o torax
        (testado e refutado na sessao 41). Braco que cabe com folga dentro dos
        8 cm fica BYTE A BYTE igual (`corte_adapt = False`)."""
        import numpy as np
        z, H = self.zmin, self.H
        z_fim = self.z_pulso + BRACO_TRECHO * (z + self.fusao_f * H - self.z_pulso)
        p98 = []
        for zz in np.arange(self.z_pulso, z_fim, 0.006):
            g = self._gap_braco(co, zz)
            if not g:
                continue
            b = co[np.abs(co[:, 2] - zz) < 0.003]
            a = b[b[:, 0] > g[1] - 0.003]
            if len(a) >= 6:
                p98.append(float(np.percentile(self._dist_eixo(a)[0], 98)))
        self.r_braco_max = max(p98) if p98 else 0.0
        # 🔴 TRAVA pela regua EXTERNA. Mesmo so no braco livre, em ~20 corpos
        # alguma fatia pega outra coisa (o vao braco/tronco achado no lugar
        # errado): 20-50 cm de "raio". Medido nos 103, a razao contra o raio da
        # circunferencia PUBLICADA do biceps separa limpo - 1,05 a 1,76 nos
        # sadios, 2,8 a 6,2 nos contaminados. Acima de BRACO_RAZAO_MAX o numero
        # nao e braco e o corte fica fixo. Sem id (sonda antiga), idem.
        r_pub = None
        if aid:
            p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "metrics", "library_metrics.json")
            with open(p, "r", encoding="utf-8") as f:
                c = json.load(f)["avatars"].get(aid, {}).get(
                    "circumferences_cm", {}).get("biceps", {}).get("cm")
            r_pub = c / 100.0 / (2 * np.pi) if c else None   # cm -> m
        if r_pub is None or self.r_braco_max > BRACO_RAZAO_MAX * r_pub:
            if self.r_braco_max + BRACO_FOLGA > BRACO_CORTE:
                print("braco: raio {:.1f} cm NAO confere com o biceps publicado ({}) - "
                      "corte fixo".format(self.r_braco_max * 100,
                                          "{:.1f} cm de raio".format(r_pub * 100)
                                          if r_pub else "sem medida"))
            self.r_braco_max = 0.0
        self.corte_adapt = self.r_braco_max + BRACO_FOLGA > BRACO_CORTE
        # ⚠️ SEMPRE rampa, nunca booleano (LICOES 7.11). Enquanto a faixa do
        # biceps parava no meio do braco, o degrau de 8 cm nunca era cruzado;
        # com o topo subindo ao umero (sessao 41) ela chega a axila, onde o
        # braco abre para o tronco, e o zen_m_b05h_d2 inverteu 31 triangulos
        # exatamente em d = 0,080 (mascara 1,00 contra 0,00 a 1 mm).
        self.corte_lo = max(BRACO_CORTE_MIN, self.r_braco_max + BRACO_FOLGA)
        self.corte_hi = self.corte_lo + BRACO_RAMPA
        print("braco: raio max {:.1f} cm ({} fatias) | corte RAMPA {:.1f}-{:.1f} cm{}".format(
            self.r_braco_max * 100, len(p98), self.corte_lo * 100, self.corte_hi * 100,
            " (alargado)" if self.corte_adapt else ""))

    def _no_braco(self, d):
        """peso (0..1) de pertencer ao braco, pela distancia ao eixo."""
        return 1.0 - sstep(d, self.corte_lo, self.corte_hi)

    def _deltoide(self, P):
        """(mascara, direcao) do deltoide: CAPSULA em volta do eixo do braco,
        fechada na cabeca do umero.

        A direcao e a radial da capsula - abaixo da cabeca, perpendicular ao
        braco (o musculo engorda para fora do osso, nao escorrega de lado);
        acima dela, esferica (a calota abre). O eixo e o `arm_e` ja ajustado
        (estavel em ~23 graus no acervo); ligar o centro ao centroide da fusao
        foi testado e deu 74 graus no obeso. A face que olha para a axila fica
        fora (`OMBRO_LAT`), senao o vao braco/tronco fecha."""
        import numpy as np
        R = self.r_braco
        m = np.zeros(len(P))
        dirv = np.zeros((len(P), 3))
        e = self.arm_e
        o = np.array([1.0, 0.0, 0.0]) - e[0] * e
        o /= np.linalg.norm(o)
        for sg in (+1.0, -1.0):
            Q = P * np.array([sg, 1.0, 1.0])
            t = (Q - self.C_ombro) @ e
            eixo = self.C_ombro + np.minimum(t, 0.0)[:, None] * e
            v = Q - eixo
            r = np.maximum(np.linalg.norm(v, axis=1), 1e-6)
            u = v / r[:, None]
            w = ((1.0 - sstep(r, OMBRO_R[0] * R, OMBRO_R[1] * R))
                 * sstep(t, -OMBRO_DESCE[1] * R, -OMBRO_DESCE[0] * R)
                 * sstep(u @ o, OMBRO_LAT[0], OMBRO_LAT[1])
                 * sstep(Q[:, 0], 0.03, 0.06))
            lado = (P[:, 0] * sg) > 0
            m = np.where(lado, w, m)
            dirv[lado] = (u * np.array([sg, 1.0, 1.0]))[lado]
        return m, dirv

    # ------------------------------------------------------------------ util
    def _gap_braco(self, co, z, half=0.006):
        import numpy as np
        b = co[np.abs(co[:, 2] - z) < half]
        xs = np.sort(b[b[:, 0] > 0.02][:, 0])
        if len(xs) < 4:
            return None
        d = np.diff(xs)
        i = int(np.argmax(d))
        return (xs[i], xs[i + 1]) if d[i] > 0.015 else None

    def _dist_eixo(self, P):
        import numpy as np
        d = P - self.arm_c
        t = d @ self.arm_e
        perp = d - np.outer(t, self.arm_e)
        return np.linalg.norm(perp, axis=1), t, perp

    def _perfil(self, co, sel, z0, z1):
        """(zs, centros XY) do que esta em `sel`, fatia a fatia."""
        import numpy as np
        zs = np.arange(z0, z1, 0.01)
        cent, ult = [], np.array([0.0, 0.0])
        for t in zs:
            s = sel & (np.abs(co[:, 2] - t) < 0.010)
            if s.sum() > 6:
                ult = co[s, :2].mean(axis=0)
            cent.append(ult)
        return zs, np.array(cent)

    def _perfil_tronco(self, co, sel, z0, z1):
        """(zs, centros XY) do TRONCO - o meio da caixa da fatia, alisado em Z.

        🔴 Ate a sessao 41 era o `_perfil` (MEDIA dos vertices da fatia), e a
        media segue a DENSIDADE da malha: no cos do short e nas bordas da faixa
        ha muito mais vertice, e o centro pulava ate 8 cm para a frente ou para
        tras entre fatias a 1 cm uma da outra. A direcao radial de cintura,
        quadril e peito sai daqui, entao dois vizinhos de 5 mm recebiam
        empurroes a 15 graus um do outro e o triangulo entre eles virava - eram
        os furos do item D (f_b07i_d1 em z/H 0,585 com o pulo em 0,586;
        m_b04_d1 em 0,563 com o pulo em 0,563), visiveis no render.
        O meio da caixa nao depende de quantos vertices ha em cada lado; e o
        alisamento (media movel de 5 fatias) tira o que sobra de degrau."""
        import numpy as np
        zs = np.arange(z0, z1, 0.01)
        cent, ult = [], np.array([0.0, 0.0])
        for t in zs:
            s = sel & (np.abs(co[:, 2] - t) < 0.010)
            if s.sum() > 6:
                xy = co[s, :2]
                ult = (xy.min(axis=0) + xy.max(axis=0)) / 2.0
            cent.append(ult)
        cent = np.array(cent)
        k = TRONCO_CENTRO_ALISA
        if len(cent) > k:
            pad = np.pad(cent, ((k // 2, k // 2), (0, 0)), mode="edge")
            cent = np.stack([np.convolve(pad[:, j], np.ones(k) / k, mode="valid")
                             for j in range(2)], axis=1)
        return zs, cent

    def _perfil_vao(self, co):
        """(zs, folga entre as duas pernas) por altura. Onde elas se tocam,
        zero."""
        import numpy as np
        zs = np.arange(self.zmin + 0.06 * self.H, self.leg_top + 0.02, 0.01)
        out = []
        for t in zs:
            b = co[np.abs(co[:, 2] - t) < 0.008]
            d, e = b[b[:, 0] > 0][:, 0], b[b[:, 0] < 0][:, 0]
            out.append(float(d.min() - e.max()) if len(d) > 3 and len(e) > 3 else 0.0)
        return zs, np.maximum(np.array(out), 0.0)

    def _perfil_axila(self, co):
        """(zs, folga braco<->tronco) por altura, do lado direito. Zero onde
        eles ja estao fundidos."""
        import numpy as np
        zs = np.arange(self.zmin + 0.35 * self.H, self.zmin + self.fusao_f * self.H, 0.01)
        out = []
        for t in zs:
            g = self._gap_braco(co, t)
            out.append(float(g[1] - g[0]) if g else 0.0)
        return zs, np.array(out)

    def normais(self, P):
        """Normal de face NORMALIZADA. Triangulo degenerado devolve zero de
        proposito - a sonda de inversao o ignora, ver `sondas`."""
        import numpy as np
        t = self.tris
        nr = np.cross(P[t[:, 1]] - P[t[:, 0]], P[t[:, 2]] - P[t[:, 0]])
        ln = np.linalg.norm(nr, axis=1, keepdims=True)
        return np.where(ln > 1e-12, nr / np.maximum(ln, 1e-12), 0.0), ln[:, 0]

    # ------------------------------------------------------ o campo, em P
    def campo(self, P):
        """{nome: (mascara (n,), direcao (n,3))} avaliado em QUALQUER array de
        posicoes - e por isso a malha soldada (para medir) e a real (para
        gravar o shape key) recebem exatamente o mesmo deslocamento."""
        import numpy as np
        z, H = self.zmin, self.H
        Z = P[:, 2]
        n = len(P)

        # -------- identidade e direcoes do braco
        d_dir, _, perp_dir = self._dist_eixo(P)
        d_esq, _, perp_esq = self._dist_eixo(P * np.array([-1.0, 1.0, 1.0]))
        d_braco = np.minimum(d_dir, d_esq)
        br_dir = (P[:, 0] > 0) & (self._no_braco(d_dir) > 0)
        br_esq = (P[:, 0] < 0) & (self._no_braco(d_esq) > 0)
        w_br = np.where(P[:, 0] > 0, self._no_braco(d_dir), self._no_braco(d_esq))
        # t = quanto o vertice andou AO LONGO do eixo do proprio braco (ver
        # t_pulso/t_top/t_fusao na Base). Um so array: cada lado projeta no seu
        # eixo, e o lado oposto fica com valor irrelevante porque as mascaras
        # do braco sao multiplicadas por br_dir/br_esq.
        t_arm = np.where(P[:, 0] > 0,
                         (P - self.arm_c) @ self.arm_e,
                         (P * np.array([-1.0, 1.0, 1.0]) - self.arm_c) @ self.arm_e)
        dir_arm = np.zeros((n, 3))
        # A componente do braco que aponta PARA O TRONCO morre onde a axila ja
        # esta fechando - o mesmo remedio das coxas. Sem ela o unico jeito de
        # proteger o vao seria manter a mascara fraca no lugar em que a regua
        # mede, e mascara fraca no ponto da medida foi o que produziu
        # "+0,1 cm com influence 0,5" nesta calibracao.
        vao = np.interp(Z, self.az, self.av)
        abre_ax = sstep(vao, 0.004, 0.025)
        for sg, mask, perp, d in ((+1.0, br_dir, perp_dir, d_dir),
                                  (-1.0, br_esq, perp_esq, d_esq)):
            v = perp / np.maximum(d, 1e-6)[:, None]
            if sg < 0:
                v = v * np.array([-1.0, 1.0, 1.0])
            para_dentro = np.maximum(0.0, -sg * v[:, 0])
            v[:, 0] = v[:, 0] + (1.0 - abre_ax) * para_dentro * sg
            dir_arm[mask] = v[mask]

        # -------- radial do tronco
        dir_trunk = self._radial(P, np.interp(Z, self.tz, self.tc[:, 0]),
                                 np.interp(Z, self.tz, self.tc[:, 1]))
        # ⚠️ NA VIRILHA O CAMPO DO TRONCO NAO TEM DIRECAO ESTAVEL. Ali a secao
        # deixa de ser um anel e vira sela: o centro do "tronco" cai ENTRE as
        # pernas, e a 5 mm de distancia de x=0 dois vizinhos recebem empurroes
        # opostos. Era isso que invertia 1 triangulo em influence -0,5 do
        # quadril - e um sliver de 9,6e-6 no perineo, com |x| de 2 mm, bloqueava
        # a reducao INTEIRA do quadril. Preco alto por um triangulo escondido:
        # com o quadril travado em 0, um usuario que pede gluteo menor recebe o
        # corpo so engordando pela cintura.
        meio = 1.0 - sstep(np.abs(P[:, 0]), 0.004, 0.030)
        virilha = 1.0 - sstep(np.abs(Z - self.leg_top), 0.010, 0.045)
        dir_trunk = dir_trunk * (1.0 - meio * virilha)[:, None]

        # -------- radial das pernas, com a componente PARA DENTRO morta onde
        # as coxas ja se tocam
        # ⚠️ AS DUAS FRONTEIRAS DA PERNA SAO RAMPA, NAO BOOLEANO. Com `Z <
        # leg_top` cru, o vertice logo abaixo da virilha andava e o logo acima
        # ficava parado: o triangulo entre os dois virava do avesso. Os 24 a
        # 177 invertidos que sobraram depois de tirar a mao estavam TODOS em
        # z/H 0,459-0,461, ou seja no proprio corte. O mesmo vale para o gate
        # do braco, que passa por essa altura em A-pose.
        fora_braco = sstep(d_braco, 0.085, 0.135)
        dentro_perna = fora_braco * (1 - sstep(Z, self.leg_top - 0.005,
                                               self.leg_top + 0.045))
        na_perna = (Z < self.leg_top + 0.050) & (d_braco > 0.080)
        folga = np.interp(Z, self.gz, self.gv)
        abre = sstep(folga, 0.010, 0.045)
        # ⚠️ ESCOLHER UMA PERNA POR SINAL DE X e um corte duro no meio: o
        # campo radial vem de DOIS centros diferentes, e no vertice de x = 0,3
        # mm contra o de x = -0,2 mm ele apontava para lados opostos - 2,3 mm
        # de deslocamento contra 0,4 mm em meio milimetro de distancia. Aqui os
        # dois campos sao MISTURADOS numa faixa de 2 cm em torno da linha do
        # meio, que e justamente onde as coxas se tocam.
        peso = np.clip(P[:, 0] / 0.020, -1.0, 1.0)
        dir_leg = np.zeros((n, 3))
        for sg in (+1.0, -1.0):
            u = self._radial(P, np.interp(Z, self.lz[sg], self.lc[sg][:, 0]),
                             np.interp(Z, self.lz[sg], self.lc[sg][:, 1]))
            para_dentro = np.maximum(0.0, -sg * u[:, 0])
            u[:, 0] = u[:, 0] + (1.0 - abre) * para_dentro * sg
            dir_leg += u * (0.5 * (1.0 + sg * peso))[:, None]
        dir_leg[~na_perna] = 0.0

        # -------- radial do pescoco
        r = np.stack([P[:, 0] - self.nx, P[:, 1] - self.ny], axis=1)
        rn = np.maximum(np.linalg.norm(r, axis=1), 1e-6)
        dir_neck = np.zeros((n, 3))
        dir_neck[:, 0] = r[:, 0] / rn
        dir_neck[:, 1] = r[:, 1] / rn

        # ================================================== as mascaras
        # OMBRO - o DELTOIDE, capsula em volta do eixo do braco (25/09; ver
        # OMBRO_* no topo). A regua le em 0,795, que passa pela calota.
        m_ombro, dir_ombro = self._deltoide(P)

        # BICEPS e ANTEBRACO - so no braco, e as janelas em Z sao as MESMAS em
        # que o metrics.py mede, para calibrar o que a regua le.
        # ⚠️ A mascara tem que estar CHEIA na altura em que a regua le, e as
        # duas leem um MAXIMO dentro de uma banda. Com o plato deslocado, o
        # maximo continua onde estava e a medida so anda quando o morph passa
        # por cima dele: media +0,1 cm em influence 0,5 e +4,3 cm em 1,0, ou
        # seja o mapa mentiria em toda a metade de baixo da faixa.
        no_braco = (br_dir | br_esq).astype(float) * w_br
        # 🔴 O BICEPS E FAIXA NO EIXO DO BRACO, NAO EM ALTURA (14/08, 3a versao;
        # as duas anteriores falharam no testador, com print do Rogerio).
        #
        # O que a sonda `perfil_braco` mediu no b04_d2, projetando no eixo:
        #     eixo a 24,3 graus da vertical
        #     cotovelo  t=+0,15   (raio para de cair e volta a subir)
        #     biceps    t=+0,20 a +0,34
        #     fusao     t=+0,31   (arm_split; acima disso e deltoide/tronco)
        #     arm_top   t=+0,23   <- o TETO da mascara antiga
        #
        # Os dois defeitos que ele viu saem dai, e sao um so erro:
        #   - faixa de Z corta um membro inclinado na DIAGONAL, entao a mesma
        #     fatia pega biceps de um lado e cotovelo do outro;
        #   - `arm_top` nao e o topo do biceps, e o MEIO dele - o plato antigo
        #     ia de t~0,18 a t~0,23 e deixava de fora 2/3 do musculo. Era a
        #     "regiao minima" da queixa.
        #
        # Agora o plato vai do cotovelo (+15% do vao pulso->arm_top, para nao
        # tocar a dobra) ate a FUSAO com o tronco, que e onde o braco acaba de
        # verdade. A regua le em arm_top, que fica dentro do plato - a exigencia
        # do §7.9 (mascara CHEIA onde a regua le) continua satisfeita.
        # O plato fica CENTRADO em t_top, que e onde a regua le o maximo - a
        # exigencia do §7.9. As rampas e que sao longas: descem ate logo acima
        # do cotovelo e sobem ate a fusao, entao o musculo inteiro se move com
        # queda suave nas pontas, sem parede no cotovelo nem empurrao dentro da
        # axila (que era de onde vinham as normais invertidas).
        vao_br = self.t_top - self.t_pulso
        t_cot = self.t_pulso + 0.72 * vao_br
        t_lo0 = t_cot + 0.06 * vao_br
        t_lo1 = self.t_top - 0.10 * vao_br
        t_hi0 = self.t_top + 0.10 * vao_br
        # ⚠️ O TETO PARA NA FUSAO, e mexer nele foi TESTADO E NAO CONVERGIU
        # (14/08). Recuar para antes da fusao devolvia faixa no zen_m_b10_d1
        # mas colapsava a mascara para 199 vertices (morph invisivel); por um
        # piso de 0.25*vao a mascara voltava a 386 vertices e a faixa caia de
        # novo. Corpo obeso funde o braco cedo demais para esta banda ter folga.
        # O valor abaixo e o que esta APLICADO nos 76 e verificado na foto.
        t_hi1 = self.t_fusao + 0.05 * vao_br
        # ⚠️ RAMPA MINIMA nas duas bordas (sessao 41, LICOES 7.27). Quando a
        # fusao cola no arm_top, t_hi1 - t_hi0 cai a ZERO (zen_m_b06h_d3,
        # m_b07_d3, m_b08_d3) e a borda de cima vira degrau no eixo: o
        # triangulo que o atravessa inverte e o biceps morre inteiro. No
        # braco curto (zen_m_b11_d1, vao pulso->top de 8 cm) e a de BAIXO que
        # encolhe. A rampa curta e alargada em volta do proprio meio - quem ja
        # tem rampa maior nao muda.
        # 🔴 O TOPO DA FAIXA VEM DO UMERO, NAO DA AXILA (sessao 41, reprovado
        # no olho dele: "ta morfando o cotovelo e nao o biceps"). O mapa de
        # localizacao mostrou a mascara numa faixa estreita logo acima do
        # cotovelo em TODOS os corpos, inclusive no b05h_d2. Medido ao longo do
        # eixo (`biceps_eixo.py`), em fracao do umero a partir do cotovelo: a
        # faixa antiga ia de 0,06 a 0,34-0,50 (a fusao, que e a axila projetada
        # num braco inclinado), e a regua le a 0,24-0,31. A metade de cima do
        # braco - o ventre do biceps - ficava parada. Agora o plato vai ate
        # BICEPS_TOPO_L[0] do umero e a rampa morre em [1], onde o deltoide ja
        # manda (a cabeca do umero e a mesma do deltoide). Nunca abaixo do antigo.
        # ❌ Em raios de braco (3,0 R / 1,8 R) nao serviu: 3 R num braco de 7,5
        # cm sao 22 cm, e a faixa continuava no meio do braco.
        t_cab = float((self.C_ombro - self.arm_c) @ self.arm_e)
        L_um = t_cab - t_cot
        t_hi0 = max(t_hi0, t_cot + BICEPS_TOPO_L[0] * L_um)
        t_hi1 = max(t_hi1, t_cot + BICEPS_TOPO_L[1] * L_um)
        t_hi0, t_hi1 = _rampa_min(t_hi0, t_hi1, BICEPS_RAMPA_MIN)
        m_biceps = no_braco * band(t_arm, t_lo0, t_lo1, t_hi0, t_hi1)
        # ⚠️ A DESCIDA DO ANTEBRACO MORRE NO COTOVELO, nao no meio do osso.
        # A versao anterior fechava de z_meio-0,010 a z_meio+0,020: 3 cm de
        # rampa no MEIO de um antebraco liso, com plato de so 5 cm. Encolher
        # um anel de 5 cm em 7 mm de raio e deixar o resto parado nao le como
        # "antebraco mais fino", le como MORDIDA - foi o defeito que o Rogerio
        # viu no testador em 05/08, e o render confirmou o degrau na silhueta.
        # Agora a descida leva 9,8 cm e so acaba colada na axila, onde a
        # geometria do braco ja muda sozinha. O plato continua cobrindo os
        # 0,626 em que a regua le (§7.9).
        # O preco e sobreposicao com o biceps no cotovelo, e ela e deliberada:
        # braco de verdade nao tem degrau na dobra.
        m_antebraco = no_braco * band(Z, self.z_pulso, self.z_pulso + 0.045,
                                      self.z_meio + 0.010, self.arm_top - 0.010)
        # ⚠️ GATE DE PROPRIEDADE (licao v84 do engine): onde o biceps manda, o
        # ombro nao mexe. Sem isso os dois campos se somam no vale da axila,
        # que e onde a membrana nasceu la. Era 0,85 com a dragona; o deltoide
        # cobre de verdade o terco de cima do braco (ele e o musculo que fica
        # POR CIMA do biceps ali), e com 0,85 a calota era apagada justo onde
        # a regua do biceps nao le.
        #
        # ⚠️ E o gate usa o braco em RAMPA, nao o `no_braco` booleano: a
        # mascara do biceps tem degrau em 8 cm do eixo, e no braco grosso esse
        # degrau passava para o ombro - o zen_m_b08_d3 (biceps 62 cm) nunca
        # teve morph de ombro por UM triangulo a 8,1 cm do eixo. Sem o degrau,
        # zero invertidos.
        braco_suave = np.where(P[:, 0] > 0,
                               1.0 - sstep(d_dir, 0.065, 0.095),
                               1.0 - sstep(d_esq, 0.065, 0.095))
        m_ombro = m_ombro * (1 - 0.5 * braco_suave * band(t_arm, t_lo0, t_lo1, t_hi0, t_hi1))

        # PEITO e CINTURA - radiais do centro do tronco, FUGINDO DO BRACO por
        # distancia (licao v23/v26: gate por |x| cola no braco em A-pose).
        # Reducao radial UNIFORME: pinca lateral cava sulco.
        fuga = sstep(d_braco, 0.075, 0.140)
        m_peito = band(Z, z + 0.630 * H, z + 0.685 * H,
                       z + 0.760 * H, z + 0.815 * H) * fuga

        # ⚠️ CINTURA e QUADRIL sao EXTREMOS de banda, e por isso a mascara tem
        # que cobrir a BANDA INTEIRA - nao so o ponto onde o extremo esta hoje.
        # Com a mascara comecando dentro da banda (0,560 contra WAIST_BAND
        # 0,550), inflar o meio empurra o MINIMO para a borda descoberta: a
        # medida travou em +2,5 cm para qualquer amplitude, inclusive a de
        # 6 cm que so deformou o corpo. E a versao de cintura da mesma
        # armadilha que fez o `metrics.py` medir joelho na banda da
        # panturrilha - extremo que pousa na borda nao e extremo, e corte.
        m_cintura = band(Z, z + (mt.WAIST_BAND[0] - 0.055) * H, z + mt.WAIST_BAND[0] * H,
                         z + mt.WAIST_BAND[1] * H, z + (mt.WAIST_BAND[1] + 0.055) * H) * fuga
        # O `fuga` tambem aqui: a banda do quadril (0,470-0,550) e a altura em
        # que o ANTEBRACO passa em A-pose, e sem o gate ele seria empurrado
        # radialmente a partir do centro do tronco junto com o gluteo.
        m_quadril = band(Z, z + (mt.HIP_BAND[0] - 0.020) * H, z + (mt.HIP_BAND[0] + 0.006) * H,
                         z + mt.HIP_BAND[1] * H, z + (mt.HIP_BAND[1] + 0.055) * H) * fuga

        # COXA e PANTURRILHA - radial por PERNA, e pelo mesmo motivo o plato
        # cobre a banda que o metrics.py varre. A da panturrilha (0,170-0,265)
        # ja foi corrigida uma vez por estar medindo o JOELHO.
        m_coxa = dentro_perna * sstep(Z, z + 0.300 * H, z + 0.355 * H)
        m_pant = dentro_perna * band(Z, z + (mt.CALF_BAND[0] - 0.035) * H,
                                     z + mt.CALF_BAND[0] * H, z + mt.CALF_BAND[1] * H,
                                     z + (mt.CALF_BAND[1] + 0.035) * H)

        # PESCOCO - teto que depende de Y: na FRENTE fecha abaixo do queixo,
        # ATRAS sobe ate o occipital (receita do engine para a nuca). O piso e
        # uma rampa LARGA de proposito: rampa curta faz degrau contra o
        # trapezio, que foi o limite medido em -5/-6 cm.
        # ⚠️ O TETO INCLINADO PRECISA DE RAMPA LARGA NOS DOIS SENTIDOS. Ele sobe
        # 7,5 cm da frente para a nuca; com a mistura frente/costas em 6 cm e a
        # descida em 3,5 cm, em z/H 0,860 a frente valia 0,04 e as costas 0,96 -
        # 0,92 de mascara em poucos centimetros de circunferencia. Em -1,5 isso
        # dobrava 22 triangulos, TODOS nas costas, exatamente na faixa da
        # transicao. Agora a mistura leva 11 cm e a descida 5,5 cm.
        t = np.clip((P[:, 1] * self.frente - self.ny * self.frente) / -0.11, 0.0, 1.0)
        # 🔴 O PESO VEM DA COLECAO, POR TIPO DE CORPO (sessao 42, 01/10). O
        # cilindro de altura cheia empurrava 2,3 cm de raio POR IGUAL no
        # zen_m_b01_d1 para a regua (minimo logo abaixo do queixo) ler +3,4 cm:
        # a circunferencia visivel andava ~+14 cm, a mandibula sumia e a cabeca
        # ficava "sobre um cano" (veredito dele). Hoje W(hq, theta) e a
        # inclinacao NATURAL do raio contra a circunferencia entre os vizinhos
        # do mesmo tipo (scripts/pescoco_campo.py): o magro engrossa no
        # lado-tras e quase nada acima do queixo; o pesado na papada e na nuca.
        # O envelope abaixo so protege: piso na base do pescoco (abaixo e peito
        # e trapezio, que tem morph proprio), teto no rosto, cilindro no ombro.
        hq = (Z - z) / H - (self.z_queixo - z) / H
        ang = np.degrees(np.arctan2(np.abs(P[:, 0] - self.nx),
                                    (P[:, 1] - self.ny) * self.frente))
        W = _bilinear(self.pesc_hq, self.pesc_th, self.pesc_W, hq, ang)
        teto_f = self.z_rosto + PESCOCO_TETO[0] * H
        teto_c = max(self.z_queixo + PESCOCO_TETO[1] * H, teto_f + 0.020 * H)
        teto = teto_f + (teto_c - teto_f) * t
        # comprimento da rampa: 1% na frente (+ a papada, quando a regua le
        # acima do queixo), crescendo para os lados e a nuca
        papada = (self.z_rosto - self.z_queixo) * (1 - t)
        rampa = (PESCOCO_TOPO + (PESCOCO_TOPO_LADO - PESCOCO_TOPO) * np.clip(2 * t, 0, 1)) * H + papada
        # o piso da frente vale SO na frente: pelo angulo, nao pelo `t` (que
        # e 0 tambem no lado - la a encosta do trapezio dobrava, zen_m_b10_d1)
        lado = sstep(ang, 35.0, 75.0)
        piso0 = PESCOCO_PISO_FRENTE[0] + (PESCOCO_PISO[0] - PESCOCO_PISO_FRENTE[0]) * lado
        piso1 = PESCOCO_PISO_FRENTE[1] + (PESCOCO_PISO[1] - PESCOCO_PISO_FRENTE[1]) * lado
        r_pesc = np.hypot(P[:, 0] - self.nx, P[:, 1] - self.ny)
        m_pescoco = (sstep(hq, piso0, piso1)
                     * (1 - sstep(Z, teto - rampa, teto))
                     * (1 - sstep(r_pesc, PESCOCO_RAIO[0] * self.r_pescoco,
                                  PESCOCO_RAIO[1] * self.r_pescoco))
                     * W)

        return {
            "morph_neck":     (m_pescoco,   dir_neck),
            "morph_shoulder": (m_ombro,     dir_ombro),
            "morph_chest":    (m_peito,     dir_trunk),
            "morph_waist":    (m_cintura,   dir_trunk),
            "morph_hip":      (m_quadril,   dir_trunk),
            "morph_biceps":   (m_biceps,    dir_arm),
            "morph_forearm":  (m_antebraco, dir_arm),
            "morph_thigh":    (m_coxa,      dir_leg),
            "morph_calf":     (m_pant,      dir_leg),
            # ACHATAR: para fora em X, para dentro em Y, na MESMA banda da
            # cintura. O perimetro quase nao muda; o que muda e a razao entre
            # largura e profundidade.
            "morph_waist_flatten": (m_cintura, self._achatar(P)),
            # ...e a MESMA operacao nas outras duas bandas do tronco (16/08).
            # A direcao e identica - `_achatar` ja e generico, ele so precisa do
            # perfil do centro do tronco -, o que muda e a mascara e, na
            # calibracao, QUAL profundidade e medida.
            "morph_hip_flatten":   (m_quadril, self._achatar(P)),
            "morph_chest_flatten": (m_peito,   self._achatar(P)),
        }

    def _achatar(self, P):
        import numpy as np
        Z = P[:, 2]
        cx = np.interp(Z, self.tz, self.tc[:, 0])
        cy = np.interp(Z, self.tz, self.tc[:, 1])
        rad = np.stack([P[:, 0] - cx, P[:, 1] - cy], axis=1)
        rn = np.maximum(np.linalg.norm(rad, axis=1), 1e-6)
        out = np.zeros((len(P), 3))
        out[:, 0] = rad[:, 0] / rn
        out[:, 1] = -rad[:, 1] / rn          # o sinal e a diferenca toda
        return out

    def _radial(self, P, cx, cy):
        import numpy as np
        rad = np.stack([P[:, 0] - cx, P[:, 1] - cy], axis=1)
        rn = np.maximum(np.linalg.norm(rad, axis=1), 1e-6)
        out = np.zeros((len(P), 3))
        out[:, 0] = rad[:, 0] / rn
        out[:, 1] = rad[:, 1] / rn
        return out

    def rosto(self, P):
        """Vertices de ROSTO: acima do queixo E NA FRENTE.

        ⚠️ O sinal aqui ja esteve invertido - no `morph_lab4` e na primeira
        versao deste arquivo - e a trava selecionava a NUCA, que deve reduzir
        mesmo. Ela entao acusava 'movimento no rosto' em toda amplitude,
        inclusive nas boas. Trava mal definida e pior que trava nenhuma:
        ensina a ignorar o alarme (LICOES.md 7.5)."""
        return ((P[:, 2] > self.z_rosto + 0.01)
                & (P[:, 1] * self.frente > self.ny * self.frente))

    # --------------------------------------------------------------- sondas
    def sondas(self, P, mask):
        """(normais invertidas na mascara, vao da axila cm, vao entre coxas cm,
        maior movimento no rosto cm)."""
        import numpy as np
        nr, area = self.normais(P)
        # ⚠️ So conta triangulo que ANDOU o bastante para a dobra ser vista
        # (sessao 41, 01/10). Na cintura do f_b08_d2, f_b09i_d1 e f_b05_d2 a
        # sonda travava o lado negativo inteiro por UM triangulo que virava com
        # 0,8-3,2 mm de movimento - e o render em -1 saiu limpo nos tres. Os
        # furos reais (f_b07i_d1, m_b04_d1) andavam 8-10 mm. Nao e a tolerancia
        # "ate 2 invertidos" refutada na §7.23: aquela contava TRIANGULOS e o
        # mesmo numero era visivel num corpo e invisivel no outro; esta mede o
        # tamanho do movimento, e o limite veio da foto. LICOES 7.29.
        anda = np.linalg.norm(P - self.co, axis=1)[self.tris].max(axis=1) >= SONDA_MOV_MIN
        toca = (mask[self.tris].max(axis=1) > 0.05) & (area > self.area_min) \
            & (self.area0 > self.area_min) & anda
        inv = int(((nr * self.nrm0).sum(axis=1) < 0)[toca].sum())
        rst = self.rosto(self.co)
        mov = float(np.linalg.norm((P - self.co)[rst], axis=1).max() * 100) if rst.any() else 0.0
        return inv, self._vao_axila(P), self._vao_coxas(P), mov

    def _vao_axila(self, P):
        """Menor folga entre braco e tronco onde eles ainda sao separados. Se
        isso for a zero, a membrana nasceu - foi la que o zenith_avatar_engine
        quebrou cinco vezes."""
        import numpy as np
        pior = None
        for f in np.arange(self.fusao_f - 0.10, self.fusao_f, 0.005):
            g = self._gap_braco(P, self.zmin + f * self.H)
            if g:
                w = (g[1] - g[0]) * 100
                pior = w if pior is None or w < pior else pior
        return pior

    def _vao_coxas(self, P):
        """O mesmo entre as duas coxas - a versao de baixo da mesma armadilha.

        ⚠️ So conta fatia onde a folga EXISTE (> 4 mm). Sem esse filtro a sonda
        devolvia 0,04 cm ate na malha base, porque perto da virilha as coxas ja
        se encostam por anatomia: qualquer limiar sobre esse numero comparava
        ruido com ruido."""
        import numpy as np
        pior = None
        for f in np.arange(0.20, (self.leg_top - self.zmin) / self.H, 0.005):
            b = P[np.abs(P[:, 2] - (self.zmin + f * self.H)) < 0.006]
            d, e = b[b[:, 0] > 0][:, 0], b[b[:, 0] < 0][:, 0]
            if len(d) < 3 or len(e) < 3:
                continue
            w = (d.min() - e.max()) * 100
            if w > 0.4:
                pior = w if pior is None or w < pior else pior
        return pior


# ==========================================================================
#  A REGUA OFICIAL, aplicada a uma malha deformada
# ==========================================================================

def _prof_em(m, zc):
    """Profundidade (extensao em Y) da secao do tronco na altura `zc`.

    O criterio de calibracao dos morphs de FORMA. Nao e medida de fita: fita da
    perimetro, e perimetro e cego para forma - duas cinturas de 101 cm podem ser
    redonda ou chata. Profundidade e o eixo que aparece de perfil e de 3/4, e foi
    nele que o morph isotropico piorava o avatar (LICOES 7.19).

    Pega o MAIOR laco da fatia porque na altura do peito o corte pode devolver
    tambem os bracos como lacos proprios."""
    if zc is None:
        return None
    lps = m.loops(float(zc))
    if not lps:
        return None
    lp = max(lps, key=len)
    return float(lp[:, 1].max() - lp[:, 1].min())


def medir(base, P, column):
    """O centimetro daquela coluna, pelas MESMAS funcoes do metrics.py, com os
    landmarks de ancoragem congelados na base (ver cabecalho)."""
    m = mt.Mesh(P, base.mesh.edges, base.mesh.face_edges, base.mesh.tris)
    z, H = base.zmin, base.H

    if column == "neck":
        return mt.torso_extreme(m, z + mt.NECK_BAND[0] * H, z + mt.NECK_BAND[1] * H, "min")[0]
    if column == "shoulder":
        return mt.torso_at(m, z + mt.SHOULDER_FRAC * H)
    if column == "chest":
        cz = z + mt.CHEST_FRAC * H
        if base.arm_split is not None and base.arm_split < cz:
            cz = base.arm_split - mt.CHEST_PAD_M
        return mt.torso_at(m, cz)
    if column == "waist_min":
        return mt.torso_extreme(m, z + mt.WAIST_BAND[0] * H, z + mt.WAIST_BAND[1] * H, "min")[0]
    if column == "waist_navel":
        # fracao FIXA, nao extremo procurado - e por isso que ela virou a coluna
        # publicada em 21/08 (o CLAUDE.md ja manda medida de fita ser landmark).
        # 0,600 cai dentro da WAIST_BAND (0,550-0,680), entao a mascara do
        # morph de cintura cobre esta altura sem mudanca nenhuma.
        return mt.torso_at(m, z + mt.NAVEL_FRAC * H)
    if column == "_waist_depth":
        # profundidade (Y) da secao na altura em que o waist_min e lido. Nao e
        # medida de fita - e o eixo que o olho ve de perfil, e o criterio de
        # calibracao do achatamento.
        per, zc = mt.torso_extreme(m, z + mt.WAIST_BAND[0] * H,
                                   z + mt.WAIST_BAND[1] * H, "min")
        return _prof_em(m, zc)
    if column == "_hip_depth":
        # a mesma coisa na altura em que o QUADRIL e lido (maximo da banda).
        per, zc = mt.torso_extreme(m, z + mt.HIP_BAND[0] * H,
                                   z + mt.HIP_BAND[1] * H, "max")
        return _prof_em(m, zc)
    if column == "_chest_depth":
        # e na altura do PEITO, que nao e extremo de banda: e fracao fixa, com
        # o mesmo recuo pela axila que a medida de peito usa (CHEST_PAD_M).
        # Repetir a conta aqui em vez de reaproveitar o `chest` e de proposito -
        # aquele ramo devolve PERIMETRO e este precisa da altura.
        cz = z + mt.CHEST_FRAC * H
        if base.arm_split is not None and base.arm_split < cz:
            cz = base.arm_split - mt.CHEST_PAD_M
        return _prof_em(m, cz)
    if column == "hip":
        return mt.torso_extreme(m, z + mt.HIP_BAND[0] * H, z + mt.HIP_BAND[1] * H, "max")[0]
    if column == "biceps":
        r = mt.pair_extreme(m, base.z_meio, base.arm_top, True, "max")
        return r[0] if r else None
    if column == "forearm":
        r = mt.pair_extreme(m, base.z_pulso, base.z_meio, True, "max")
        return r[0] if r else None
    if column == "thigh":
        topo = base.leg_top
        r = mt.pair_extreme(m, topo - mt.THIGH_BAND_M, topo - mt.SCAN_STEP_M, False, "max")
        if r is None:
            return None
        # LICOES 7.25 / PROBLEMA_COXA.md: a banda cai no aro do short e le a
        # peca, nao a perna - sempre para MAIS (nunca para menos). Duas
        # tentativas de filtrar QUAL triangulo entra no laco quebraram avatar
        # que ja lia certo (ver docstring de calibrar_offset_coxa). Este e um
        # terceiro caminho: nao mexe em qual malha e medida, corrige o NUMERO
        # por um offset constante medido uma vez contra o master.
        return r[0] + getattr(base, "thigh_offset", 0.0)
    if column == "calf":
        r = mt.pair_extreme(m, z + mt.CALF_BAND[0] * H, z + mt.CALF_BAND[1] * H, False, "max")
        return r[0] if r else None
    raise ValueError("coluna desconhecida: {}".format(column))


# ==========================================================================
#  WORKER
# ==========================================================================

def carregar(path):
    """(objeto Blender, co real, co soldada, Mesh soldada).

    A copia soldada existe pelo motivo do cabecalho: o dist chega com a
    costura corpo/short duplicada e a regua por topologia le outra coisa."""
    import bmesh
    import numpy as np

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(obs) != 1:
        raise RuntimeError("esperado 1 malha, achou {}".format(len(obs)))
    ob = obs[0]
    mw = ob.matrix_world
    if max(abs(mw[i][j] - (1.0 if i == j else 0.0))
           for i in range(4) for j in range(4)) > 1e-6:
        raise RuntimeError("matrix_world nao e identidade - o shape key seria "
                           "gravado em coordenada diferente da medida")

    # ⚠️ Se o dist ja tem shape key, ele SAI. Este script le o dist corrente, e
    # depois do primeiro --apply o corrente e o que ele mesmo gravou: sem
    # limpar, a segunda rodada empilha 9 morphs em cima dos 9 e o GLB sai com
    # 18 targets e nomes `.001`. Recalibrar tem que partir sempre da base - que
    # e exatamente o que os vertices da malha ja sao, porque todo key esta em
    # value 0.
    def arr(me):
        a = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", a)
        return a.reshape(-1, 3)

    co_real = arr(ob.data)
    sk_existentes = {}
    if ob.data.shape_keys:
        base_sk = np.array([list(d.co) for d in
                            ob.data.shape_keys.key_blocks[0].data])
        for k in list(ob.data.shape_keys.key_blocks)[1:]:
            sk_existentes[k.name] = np.array([list(d.co) for d in k.data]) - base_sk
        print("entrada ja tinha {} shape key(s) - removidos para recalibrar da base"
              .format(len(sk_existentes)))
        ob.shape_key_clear()
        co_real = arr(ob.data)

    # 0,3 mm: as duas primitivas sao quantizadas pelo Draco em caixas
    # diferentes, entao os vertices da costura nao voltam bit a bit iguais.
    me2 = ob.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me2)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=3e-4)
    bm.to_mesh(me2)
    bm.free()
    co_sold = arr(me2)

    edges = np.array([e.vertices[:] for e in me2.edges], dtype=int)
    lookup = {}
    for e in me2.edges:
        lookup[tuple(sorted(e.vertices[:]))] = e.index
    face_edges, tris = [], []
    for p in me2.polygons:
        if len(p.vertices) != 3:
            raise RuntimeError("malha nao triangulada")
        face_edges.append([lookup[tuple(sorted(k))] for k in p.edge_keys])
        tris.append(p.vertices[:])
    mesh = mt.Mesh(co_sold, edges, np.array(face_edges, dtype=int),
                   np.array(tris, dtype=int))
    bpy.data.meshes.remove(me2)
    return ob, co_real, co_sold, mesh, sk_existentes


def conferir_base(root, aid, base, co):
    """A regua sobre a base tem que reproduzir o library_metrics.json.

    E a unica regua EXTERNA que esta calibracao tem: aquele arquivo foi medido
    no master, por outro caminho de codigo, antes deste script existir. Se a
    base nao bate, tudo que vier depois e delta sobre um numero errado."""
    p = os.path.join(root, "metrics", "library_metrics.json")
    with open(p, "r", encoding="utf-8") as f:
        pub = json.load(f)["avatars"][aid]["circumferences_cm"]
    print("\nCONFERENCIA da regua na base (contra library_metrics.json):")
    ruim = []
    for spec in MORPHS:
        col = spec["column"]
        if col is None:            # morph de FORMA nao tem coluna de medida
            continue
        v = medir(base, co, col)
        v = v * 100 if v else None
        ref = pub.get(col, {}).get("cm")
        d = (v - ref) if (v is not None and ref is not None) else None
        print("  {:<10} aqui {:>7} | publicado {:>7} | delta {}"
              .format(col,
                      "{:.1f}".format(v) if v else "-",
                      "{:.1f}".format(ref) if ref else "-",
                      "{:+.1f}".format(d) if d is not None else "-"))
        if d is None or abs(d) > TOL_BASE_CM:
            ruim.append(col)
    return ruim


# Teto do offset da coxa, em CM: maior contaminacao ja medida na biblioteca
# foi +18,5 cm (zen_f_b08h_d3, LICOES 7.25). Acima disso o offset nao esta
# corrigindo fabrico, esta escondendo landmark errado - melhor deixar cair.
COXA_OFFSET_MAX_CM = 22.0


def calibrar_offset_coxa(root, aid, base, co):
    """Corrige a coxa por OFFSET CONSTANTE em vez de trocar qual malha e medida.

    Terceira tentativa (13/08) depois de duas mortas: filtrar a banda por
    material (fecha o laco pela pele, nao pela peca) quebrou 2 avatares que
    liam certo (a banda cai inteira debaixo do short, sem face de corpo la, o
    laco fecha por lixo); um fallback pra malha cheia quando o filtro falha
    consertou esses 2 mas achou 10 REGRESSOES NOVAS em avatares diferentes
    (o corpo-so as vezes acha um laco plausivel mas errado, pequeno demais
    pra disparar o fallback e grande demais pra ser obviamente lixo).

    A ideia aqui e nao trocar NADA na medicao - ela sempre roda pela malha
    CHEIA, exatamente como sempre rodou, sem nenhum risco de laco vazio ou
    degenerado. So se soma um numero fixo, medido UMA VEZ contra o
    library_metrics.json na base (sem deformacao), que fecha exatamente a
    diferenca ali. A suposicao que isso carrega: o excesso de tecido do short
    dentro da banda e aproximadamente CONSTANTE em cm ao longo da amplitude do
    morph - plausivel porque o tecido acompanha a perna (a mesma mascara de
    empurrao que move a pele proximo move o tecido proximo), mas NAO
    verificada contra medida real de coxa deformada (nao existe tal medida).
    Por isso o teto: se o offset que fecharia a base for maior que qualquer
    contaminacao ja vista na biblioteca, e mais provavel que o problema seja
    outro (landmark errado) do que fabrico, e a coluna cai como sempre caiu."""
    p = os.path.join(root, "metrics", "library_metrics.json")
    with open(p, "r", encoding="utf-8") as f:
        pub = json.load(f)["avatars"][aid]["circumferences_cm"]
    alvo = pub.get("thigh", {}).get("cm")
    if alvo is None:
        return 0.0, None
    base.thigh_offset = 0.0
    bruto = medir(base, co, "thigh")
    if bruto is None:
        return 0.0, None
    bruto_cm = bruto * 100
    offset_cm = alvo - bruto_cm
    if abs(offset_cm) > COXA_OFFSET_MAX_CM:
        return 0.0, offset_cm
    return offset_cm / 100.0, offset_cm


def worker_main():
    import numpy as np
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--root", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--remap", action="store_true")
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args(argv)

    root, aid = args.root, args.id
    ver_atual, src = _zp.dist_glb_current(root, aid)
    ob, co_real, co, mesh, sk_existentes = carregar(src)
    base = Base(co, mesh, aid)
    offset_m, offset_bruto_cm = calibrar_offset_coxa(root, aid, base, co)
    base.thigh_offset = offset_m
    if offset_bruto_cm is not None:
        print("\ncoxa: offset {:+.1f} cm{}".format(
            offset_bruto_cm, "" if offset_m else " (fora do teto, NAO aplicado)"))

    print("\nmalha: {} verts no disco -> {} soldados | altura {:.4f} m"
          .format(len(co_real), len(co), base.H))
    print("axila z/H {:.3f} | virilha z/H {:.3f} | queixo z/H {:.3f} | pulso z/H {:.3f}"
          .format((base.arm_split - base.zmin) / base.H if base.arm_split else -1,
                  (base.leg_split - base.zmin) / base.H if base.leg_split else -1,
                  (base.z_queixo - base.zmin) / base.H,
                  (base.z_pulso - base.zmin) / base.H))

    # ⚠️ A COLUNA CAI, O AVATAR NAO. Ate 11/08 uma coluna divergente derrubava o
    # avatar inteiro - e o `zen_m_b04_d3` mostrou o preco: 8 das 9 colunas
    # batendo EXATAS e a coxa +4,0 cm, porque naquele corpo o landmark da coxa
    # cai em cima da BAINHA do short (o master nao tem peca, o dist tem, e o aro
    # do tecido entra na circunferencia). Recusar os nove por causa de um joga
    # fora 8 morphs bons.
    #
    # Nao e excecao inventada: o `library.json` ja publica `unreliable_columns`
    # por avatar pelo mesmo motivo, e o contrato ja diz que coluna que a selecao
    # descartou nao morfa (LICOES 7.18). A regra e a mesma; aqui quem aponta e a
    # regua externa. O mapa publica `dropped_columns` para o app saber.
    ruim = conferir_base(root, aid, base, co)
    if ruim:
        print("\n⚠️ FORA DA REGUA EXTERNA: {}. Esses morphs NAO vao para o mapa -\n"
              "   calibrar sobre base errada e publicar delta de um numero que o\n"
              "   app nao usa. Os outros seguem.".format(", ".join(ruim)))
        if len(ruim) > 3:
            sys.exit("TRAVA: {} colunas fora da regua. Isso nao e landmark caindo "
                     "na peca - e a malha errada.".format(len(ruim)))

    masks = base.campo(co)
    campo_real = base.campo(co_real)
    v0_axila = base._vao_axila(co)
    v0_coxas = base._vao_coxas(co)
    print("\nvao base: axila {:.2f} cm | entre coxas {:.2f} cm".format(v0_axila, v0_coxas))

    resultado = []
    acoplado = {}     # {key do morph de tamanho: (mascara, direcao, amplitude)}
    for spec in MORPHS:
        key, col = spec["key"], spec["column"]
        if col in ruim or (spec.get("couple") and
                           spec["couple"] not in [r["key"] for r in resultado]):
            print("\n[{}] PULADO - a coluna {} nao passou na regua externa"
                  .format(key, col or spec.get("couple")))
            continue
        m, d = masks[key]
        tocados = int((m > 0.01).sum())

        # ------------------------------------------------ o morph de FORMA
        if spec.get("kind") == "flatten":
            alvo_key = spec["couple"]
            r_tam = next(r for r in resultado if r["key"] == alvo_key)
            m_t, d_t = masks[alvo_key]
            # CADA achatamento mede a SUA profundidade, na altura em que a SUA
            # regua le. Ate 16/08 isto era literal `_waist_depth`, porque so
            # existia o da cintura; com quadril e peitoral, medir a altura
            # errada calibraria a forma de uma secao olhando outra.
            dcol = spec.get("depth_column", "_waist_depth")
            regiao = {"_waist_depth": "cintura", "_hip_depth": "quadril",
                      "_chest_depth": "peitoral"}.get(dcol, dcol)

            # o estado que o app vai produzir: tamanho em +1,0 e forma junto
            def _prof(a_flat):
                P = (co + d_t * (m_t * r_tam["amplitude_m"])[:, None]
                        + d * (m * a_flat)[:, None])
                v = medir(base, P, dcol)
                return None if v is None else v * 100
            _p0 = medir(base, co, dcol)
            if _p0 is None or _prof(0.0) is None:
                # sem altura de secao nao ha criterio de calibracao, e chutar
                # amplitude de forma e pior que nao ter forma nenhuma.
                print("\n[{}] PULADO - {} nao devolveu secao para medir "
                      "profundidade".format(key, dcol))
                continue
            prof0 = _p0 * 100
            prof_sem = _prof(0.0)
            # ⚠️ SE O MORPH DE TAMANHO NAO AFUNDA A SECAO, NAO HA O QUE ACHATAR.
            # Acontece de verdade: no zen_f_b12_d1 o `morph_chest` mal cresce, e
            # a profundidade do peitoral fica identica com e sem ele. A busca
            # abaixo devolveria amplitude ~0, e uma shape key de amplitude zero
            # nao e inofensiva - ela e um target esparso de milhares de vertices
            # (7.352 naquele avatar) que o app baixa e soma para nao mover nada.
            # O corte e a resolucao da propria medida de secao.
            if prof_sem - prof0 < FLATTEN_MIN_GANHO_CM:
                print("\n[{}] PULADO - o {} nao afunda com o tamanho "
                      "({:+.1f} cm), nao ha forma a corrigir".format(
                          key, regiao, prof_sem - prof0))
                continue
            # busca a amplitude que devolve a profundidade da BASE
            lo, hi = 0.0, 0.050
            for _ in range(22):
                mid = (lo + hi) / 2
                if _prof(mid) > prof0:
                    lo = mid
                else:
                    hi = mid
            amp = (lo + hi) / 2
            print("\n[{}] FORMA do {} | mascara toca {} verts".format(
                key, regiao, tocados))
            print("  profundidade: base {:.1f} cm | so tamanho {:.1f} (+{:.1f}) | "
                  "com forma {:.1f} cm".format(prof0, prof_sem, prof_sem - prof0, _prof(amp)))
            print("  amplitude {:.4f} m, acoplada a {} quando positivo".format(amp, alvo_key))
            mr, dr = campo_real[key]
            acoplado[alvo_key] = (m, d, amp)
            resultado.append({
                "key": key, "column": None, "kind": "flatten",
                "couple": alvo_key, "couple_when": spec.get("couple_when", "positive"),
                "base_cm": round(prof0, 1), "cm_at_full": 0.0,
                "amplitude_m": round(amp, 5), "verts": tocados,
                "influence_min": 0.0, "influence_max": 1.0,
                "cm_min": 0.0, "cm_max": 0.0, "linearity_at_half": None,
                "curve": [[0.0, 0.0], [1.0, 0.0]],
                "depth_base_cm": round(prof0, 1),
                "depth_without_cm": round(prof_sem, 1),
                "depth_with_cm": round(_prof(amp), 1),
                "delta": (d * (m * amp)[:, None]),
                "delta_real": (dr * (mr * amp)[:, None]),
            })
            continue

        alvo = spec["cm_at_full"]
        # A regua que CALIBRA a amplitude pode nao ser a que se PUBLICA (ver o
        # cabecalho da tabela). Onde `cal_column` nao existe, sao a mesma.
        cal = spec.get("cal_column", col)
        b0 = medir(base, co, col) * 100
        b0_cal = medir(base, co, cal) * 100

        # amplitude que da o alvo em cm. O deslocamento e linear na amplitude,
        # a circunferencia quase - tres correcoes multiplicativas convergem.
        sg = spec.get("cal_sign", 1)
        a = 0.010
        for _ in range(5):
            v = medir(base, co + d * (m * a * sg)[:, None], cal)
            if v is None:
                a *= 0.5
                continue
            delta = (v * 100 - b0_cal) * sg      # positivo = andou na direcao calibrada
            if delta <= 0.05:
                a *= 2.0
                continue
            a = float(np.clip(a * (alvo / delta), 0.0005, 0.060))
        amp = a
        conf = medir(base, co + d * (m * amp)[:, None], col)
        conf_cm = (conf * 100 - b0) if conf else float("nan")

        print("\n[{}] coluna {}{} | base {:.1f} cm | mascara toca {} verts"
              .format(key, col,
                      "" if cal == col else " (amplitude calibrada em {})".format(cal),
                      b0, tocados))
        print("  influence 1.0 = amplitude {:.4f} m -> {:+.2f} cm (alvo {:+.1f} em {:+.0f})"
              .format(amp, conf_cm, alvo, sg))
        if key == "morph_neck":
            # 1,0 = o pescoco anda o que os vizinhos do mesmo tipo andam por
            # centimetro de fita; muito acima disso o morph esta empurrando a
            # pele mais do que a regua ve (o "cano" de antes da sessao 42).
            natural = alvo * base.pesc_s_ref / 1000.0
            print("  naturalidade: amplitude / (cm x s_ref) = {:.2f}".format(amp / natural))
            # 🔴 TETO DE NATURALIDADE. Nos 15 corpos em que a regua le na
            # papada (obesos, musculosos de pescoco muito grosso) a calibracao
            # chegava a 2-3x o natural e o maximo abria VINCO EM V no alto do
            # peito (zen_m_b09_d2, zen_m_b10_d2) - nenhuma sonda acusa, so a
            # foto. Ali a regua do pescoco mede rosto; o centimetro cede, a
            # curva continua medida e o app sabe o que o morph alcanca.
            if amp > PESCOCO_NATURAL_MAX * natural:
                amp = PESCOCO_NATURAL_MAX * natural
                print("  TETO DE NATURALIDADE: amplitude -> {:.4f} m ({:.1f}x natural)".format(
                    amp, PESCOCO_NATURAL_MAX))
                conf = medir(base, co + d * (m * amp)[:, None], col)
                conf_cm = (conf * 100 - b0) if conf else float("nan")
        print("  {:>10} {:>10} {:>8} {:>10} {:>10} {:>9}"
              .format("influence", "delta cm", "norm.inv", "axila cm", "coxas cm", "rosto cm"))

        limpo, curva = {}, {}
        for inf in SWEEP:
            P = co + d * (m * amp * inf)[:, None]
            v = medir(base, P, col)
            curva[inf] = (v * 100 - b0) if v else None
            inv, va, vc, rosto = base.sondas(P, m)
            ruim_i = (inv > 0 or v is None or va is None or vc is None
                      or va < 0.35 * v0_axila or vc < 0.35 * v0_coxas
                      or (key == "morph_neck" and rosto > 0.30))
            limpo[inf] = not ruim_i
            print("  {:>10.1f} {:>10} {:>8d} {:>10} {:>10} {:>9.2f}{}"
                  .format(inf, "{:+.1f}".format(v * 100 - b0) if v else "  -  ", inv,
                          "{:.2f}".format(va) if va is not None else "FECHOU",
                          "{:.2f}".format(vc) if vc is not None else "FECHOU",
                          rosto, "   <-- DEFEITO" if ruim_i else ""))
        # ⚠️ Faixa CONTINUA a partir do zero: se -1.0 quebra, -1.5 nao vale por
        # ter passado. A amplitude util vai ate o PRIMEIRO defeito.
        teto = INFLUENCE_CAP.get(key, INFLUENCE_CAP_PADRAO)
        teto_neg, teto_pos = teto if isinstance(teto, tuple) else (teto, teto)
        hi = min(_ate_o_defeito([s for s in SWEEP if s > 0], limpo), teto_pos)
        lo = max(_ate_o_defeito(sorted([s for s in SWEEP if s < 0], reverse=True), limpo),
                 -teto_neg)
        # LINEARIDADE: o mapa promete "cm_at_full x influence". Se meia
        # influence nao der meio centimetro, o app erra a metade de baixo da
        # faixa sem nada avisar - foi assim que o biceps deu +0,1 cm em 0,5 e
        # +4,3 em 1,0 na primeira rodada.
        meio = curva.get(0.5)
        lin = (meio / (0.5 * conf_cm)) if (meio is not None and conf_cm) else None
        # os cm saem da CURVA medida, nao de lo x cm_at_full - com o pescoco a
        # conta linear dizia -1,8 onde a medida diz -6,0
        print("  faixa limpa: {:+.1f} a {:+.1f}  ({:+.1f} a {:+.1f} cm) | "
              "linearidade em 0,5: {}"
              .format(lo, hi, curva.get(lo, 0.0) or 0.0, curva.get(hi, 0.0) or 0.0,
                      "{:.2f}x".format(lin) if lin else "-"))

        # ⚠️ O mapa publica a CURVA medida, nao so `cm_at_full`. O pescoco
        # entrega +3,2 cm em influence 0,5 e so +3,8 em 1,0 - ele e um MINIMO
        # de banda, e crescer o meio empurra o minimo para a borda travada pelo
        # queixo. Quem multiplicar cm_at_full x influence erra 68% ali. O app
        # inverte a curva por interpolacao e a promessa passa a ser medida em
        # cada ponto, nao suposta.
        pontos = [[0.0, 0.0]] + [[i, round(curva[i], 2)] for i in sorted(curva)
                                 if lo <= i <= hi and curva[i] is not None]
        pontos.sort()

        mr, dr = campo_real[key]
        resultado.append({
            "curve": pontos,
            "key": key, "column": col,
            "base_cm": round(b0, 1), "cm_at_full": round(conf_cm, 2),
            "amplitude_m": round(amp, 5), "verts": tocados,
            "influence_min": lo, "influence_max": hi,
            # das PONTAS DA CURVA, nao de `lo x cm_at_full`: com o pescoco a
            # conta linear dava -3,8 cm onde a medida diz -5,7.
            "cm_min": pontos[0][1], "cm_max": pontos[-1][1],
            "linearity_at_half": round(lin, 2) if lin else None,
            "delta": (d * (m * amp)[:, None]),
            "delta_real": (dr * (mr * amp)[:, None]),
        })

    # ⚠️ A CURVA PUBLICADA TEM QUE DESCREVER O QUE O APP VAI FAZER. O morph de
    # tamanho foi varrido sozinho, mas o app vai aplicar o de FORMA junto quando
    # a influence for positiva - e o achatamento mexe no perimetro. Entao a
    # varredura do lado positivo e refeita ACOPLADA, e e essa que vai para o
    # mapa. Publicar a curva solta seria publicar um numero que ninguem produz.
    for alvo_key, (m_f, d_f, amp_f) in acoplado.items():
        r = next(x for x in resultado if x["key"] == alvo_key)
        m_t, d_t = masks[alvo_key]
        print("\n[{}] curva REFEITA com o achatamento acoplado:".format(alvo_key))
        pontos = [p for p in r["curve"] if p[0] <= 0]
        for inf in [s for s in SWEEP if 0 < s <= r["influence_max"]]:
            P = (co + d_t * (m_t * r["amplitude_m"] * inf)[:, None]
                    + d_f * (m_f * amp_f * inf)[:, None])
            v = medir(base, P, r["column"])
            if v is None:
                continue
            cm = v * 100 - r["base_cm"]
            inv, va, vc, _ = base.sondas(P, np.maximum(m_t, m_f))
            print("   influence {:+.1f} -> {:+.1f} cm (solta era {:+.1f}) | "
                  "normais invertidas {}".format(
                      inf, cm, dict(r["curve"]).get(inf, float("nan")), inv))
            if inv == 0:
                pontos.append([inf, round(cm, 2)])
        # ⚠️ O ACHATAMENTO E MELHORIA, NAO REQUISITO - se o acoplamento quebra a
        # malha, quem cai e ELE, nao a cintura. No `zen_m_b04_d1` o lado
        # negativo da cintura ja tinha morrido na varredura e o acoplado deixava
        # 1 normal invertida em toda influence positiva: com isso o morph de
        # CINTURA - o mais importante dos nove - sumia do mapa inteiro, e o
        # `morph_waist_flatten` ficava publicado apontando para um `couple` que
        # nao existia mais. Perder a forma custa profundidade de barriga; perder
        # o tamanho custa a coluna que o app mais usa.
        if not [p for p in pontos if p[0] > 0] and [p for p in r["curve"] if p[0] > 0]:
            print("   ACOPLADO REPROVADO em toda a faixa positiva -> o achatamento "
                  "SAI deste avatar\n   e a cintura fica isotropica (curva solta).")
            resultado[:] = [x for x in resultado if x.get("couple") != alvo_key]
            continue
        pontos.sort()
        r["curve"] = pontos
        r["cm_max"] = pontos[-1][1]
        r["influence_max"] = pontos[-1][0]

    # A colisao que matou o outro projeto so aparecia no estado COMBINADO. Nao
    # basta cada morph passar sozinho - e desde 11/08 ele nao e so IMPRESSO,
    # e TRAVA: ver `_travar_combinado`.
    print("\nestado COMBINADO:")
    for nome, sinal in (("todos no maximo", +1), ("todos no minimo", -1)):
        _travar_combinado(base, co, resultado, masks, sinal, nome)

    # acoplado orfao nao se publica: o app calcularia `max(0, influence de um
    # key que nao esta no arquivo`. Foi o que o `zen_m_b04_d1` gravou.
    vivos = {r["key"] for r in resultado
             if r["influence_max"] > 0 or r["influence_min"] < 0}
    resultado[:] = [r for r in resultado
                    if not (r.get("couple") and r["couple"] not in vivos)]

    usaveis = [r for r in resultado if r["influence_max"] > 0 or r["influence_min"] < 0]
    print("\n{} de {} morphs com faixa util".format(len(usaveis), len(resultado)))

    if args.remap:
        # ⚠️ O mapa descreve um ARQUIVO. Antes de reescrever a faixa sem
        # reexportar, conferir que o deslocamento recalculado e o mesmo que ja
        # esta gravado no GLB do disco - senao o mapa passaria a falar de um
        # asset que nao existe.
        if not sk_existentes:
            sys.exit("--remap: o dist corrente nao tem shape key. Use --apply.")
        pior = 0.0
        for r in usaveis:
            se = sk_existentes.get(r["key"])
            if se is None:
                sys.exit("--remap: o GLB nao tem o shape key {}".format(r["key"]))
            pior = max(pior, float(np.abs(se - r["delta_real"]).max()) * 1000)
        print("\n--remap: maior divergencia contra o GLB do disco: {:.3f} mm".format(pior))
        if pior > 0.2:
            sys.exit("--remap: a calibracao nao reproduz o que esta no arquivo. "
                     "O deslocamento mudou - isso exige --apply e versao nova.")
        _gravar_mapa(root, aid, ver_atual, usaveis, ruim)
        return

    if not (args.apply or args.preview):
        print("\n--fit: nada gravado. Rode com --apply para gerar o dist.")
        return

    ob.shape_key_add(name="Basis", from_mix=False)
    for r in usaveis:
        k = ob.shape_key_add(name=r["key"], from_mix=False)
        k.data.foreach_set("co", (co_real + r["delta_real"]).astype(np.float32).ravel())
        k.value = 0.0
        k.slider_min, k.slider_max = -2.0, 2.0

    nova, dest = _zp.dist_glb_next(root, aid)
    # --preview: o MESMO arquivo que o --apply gravaria, fora do CDN (a regra 8
    # vale para 03_dist/glb/; qa/ nao e URL de ninguem). O ciclo e OLHA ->
    # APLICA, como no shorts.py (LICOES 4.5m).
    if args.preview:
        dest = os.path.join(root, "qa", "preview", "morph", aid + ".glb")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
    for o in bpy.context.scene.objects:
        o.select_set(o is ob)
    bpy.context.view_layer.objects.active = ob
    # ⚠️ `export_morph_normal=False` NAO e economia de esperto, e medida. Com
    # normal de morph o arquivo saiu com 4.364 KB contra 210 KB do v2, e a
    # conta e direta: a POSITION vai em accessor ESPARSO (so os 884 a 5.889
    # vertices que a mascara toca, 459 KB somando os nove), mas a NORMAL sai
    # DENSA - os 32.151 vertices em todos os nove morphs, 3.391 KB. O
    # CLAUDE.md declara orcamento de 1 a 3 MB por avatar; 4,4 MB para melhorar
    # sombreamento de um deslocamento de poucos centimetros e o lado errado da
    # troca. Sem elas o three.js usa a normal da base.
    bpy.ops.export_scene.gltf(
        filepath=dest, export_format="GLB", use_selection=True,
        export_morph=True, export_morph_normal=False, export_try_sparse_sk=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=14,
    )

    if not _conferir(src, dest, [r["key"] for r in usaveis], usaveis):
        os.remove(dest)
        sys.exit("TRAVA: o arquivo novo nao passou na conferencia - nada foi aposentado.")

    if args.preview:
        print("\npreview: {} ({:.0f} KB) - mapa e dist intocados".format(
            dest, os.path.getsize(dest) / 1024))
        return
    gone = _zp.dist_glb_retire(root, aid, keep=nova)
    print("\ndist  : {} ({:.0f} KB){}"
          .format(dest, os.path.getsize(dest) / 1024,
                  "  [aposentou {}]".format(", ".join(gone)) if gone else ""))
    _gravar_mapa(root, aid, nova, usaveis, ruim)


def _travar_combinado(base, co, resultado, masks, sinal, nome):
    """O estado combinado tambem e um estado que o APP produz - entao ele nao
    pode so ser impresso.

    Ate 11/08 cada morph era varrido SOZINHO e a faixa saia dai; o estado com
    todos ligados juntos era medido e o numero ia para a tela sem consequencia.
    Medido no `zen_m_b02_d1`: cintura em -1,0 limpa, quadril em -1,0 limpa,
    todos em -0,5 limpos - e todos em -1,0 **enruga o cos do short**, com 6
    normais invertidas que a foto confirmou (`qa/morph/{id}/onset/`). A causa e
    somar tres campos radiais com centros diferentes na mesma casca: cada um
    cabe, a soma dobra.

    Consertar isso no app custaria regra nova em TRES linguagens (o contrato e
    "clamp por morph"). Aqui custa faixa, e so de quem tem culpa: quem some do
    estado e faz as invertidas cairem apanha o fator, o resto fica intacto. Um
    avatar cujo combinado ja e limpo nao muda nada.

    ⚠️ O fator e uniforme DENTRO do grupo culpado de proposito. Procurar o
    limite de cada um separadamente e busca em N dimensoes sobre uma sonda que
    conta triangulo - a §7.12 (todo teto acima do padrao pede foto) vale aqui
    tambem, e o que se pode defender com uma foto e um numero, nao nove.
    """
    import numpy as np
    lim = "influence_max" if sinal > 0 else "influence_min"
    # ⚠️ TOLERANCIA ZERO, E ELA FOI TESTADA CONTRA A ALTERNATIVA - as fotos
    # estao em `qa/morph/{id}/` (onset, cmp, t90). Tres estados do mesmo dia:
    #   zen_m_b02_d1  combinado no minimo  inv 6 -> cos ENRUGADO, obvio
    #                 a 90% da faixa       inv 2 -> ainda tem um repuxo em V
    #                 a 80% da faixa       inv 0 -> limpo
    #   zen_m_b05h_d2 combinado no minimo  inv 2 -> foto identica a base
    # Ou seja: `inv 2` e invisivel num avatar e visivel no outro, entao a
    # CONTAGEM NAO TRANSFERE - tolerar 2 seria calibrar num corpo e aplicar no
    # outro. O que sobrevive aos dois e o criterio estrito, que ja e o mesmo da
    # varredura de um morph so (`ruim_i = inv > 0`).
    #
    # O preco esta medido e e real: o `b05h_d2`, unico avatar aprovado no olho
    # ate hoje, perde faixa NEGATIVA de peito/cintura/quadril (cintura -5,0 ->
    # -3,0 cm). Ela e a faixa de quem e MAIS MAGRO que ele - e para esse usuario
    # a selecao ja entrega outro corpo. O lado positivo, que e o dele, nao muda.
    TOL_INV = 0

    def _acoplar(infl):
        """A forma segue o tamanho, e so no lado positivo - como no app."""
        for r in resultado:
            if r.get("couple"):
                infl[r["key"]] = max(0.0, infl.get(r["couple"], 0.0))
        return infl

    def _sondar(infl):
        soma = np.zeros((len(co), 3))
        mtot = np.zeros(len(co))
        for r in resultado:
            f = infl.get(r["key"], 0.0)
            if f:
                soma += r["delta"] * f
            mtot = np.maximum(mtot, masks[r["key"]][0])
        return base.sondas(co + soma, mtot)

    infl = _acoplar({r["key"]: r[lim] for r in resultado})
    inv, va, vc, _ = _sondar(infl)
    print("  {:<16} normais invertidas {:>4} | axila {} cm | coxas {} cm"
          .format(nome, inv,
                  "{:.2f}".format(va) if va is not None else "FECHOU",
                  "{:.2f}".format(vc) if vc is not None else "FECHOU"))
    if inv <= TOL_INV:
        return
    # ONDE o combinado dobra (sessao 41): a trava corta o grupo culpado por
    # igual, e sem o lugar nao ha como saber se o culpado e o campo certo.
    soma = sum(r["delta"] * infl.get(r["key"], 0.0) for r in resultado)
    nr, area = base.normais(co + soma)
    virou = np.where(((nr * base.nrm0).sum(axis=1) < 0) & (area > base.area_min)
                     & (base.area0 > base.area_min))[0]
    for i in virou[:8]:
        c = co[base.tris[i]].mean(axis=0)
        da = min(base._dist_eixo(c[None])[0][0],
                 base._dist_eixo((c * np.array([-1.0, 1.0, 1.0]))[None])[0][0])
        quem = [r["key"][6:] for r in resultado
                if masks[r["key"]][0][base.tris[i]].max() > 0.05 and infl.get(r["key"])]
        print("    dobra: z/H {:.3f} x {:+.3f} y {:+.3f} | eixo do braco a {:.1f} cm | "
              "area {:.2f}x mediana | campos: {}".format(
                  (c[2] - base.zmin) / base.H, c[0], c[1], da * 100,
                  base.area0[i] / np.median(base.area0), ", ".join(quem)))

    # 🔴 O BRACO PAGA PRIMEIRO (sessao 41). A dobra do combinado perto da
    # axila e do empurrao do braco entrando no tronco, e a trava uniforme
    # cortava PEITO e CINTURA junto com o biceps para paga-la (f_b04_d3:
    # peito +3,8 -> +2,6; m_b06m_d3: peito a 45%). Tronco e a coluna que mais
    # pesa na selecao; o braco e absorvido pelo morph (LICOES 7.3). Entao o
    # braco encolhe SOZINHO ate deixar de contribuir para o defeito, e so o que
    # sobra passa pela trava uniforme abaixo.
    # ❌ Separar a juncao pela NORMAL (o campo do braco nao empurra pele do
    # tronco) foi testado antes e refutado: consertou 2 corpos e matou o
    # biceps de outros 2 - a transicao de dono vira gradiente novo na mascara.
    mudou = {}
    bracos = [r["key"] for r in resultado
              if r["key"] in ("morph_biceps", "morph_forearm") and infl.get(r["key"])
              and _sondar(_acoplar(dict(infl, **{r["key"]: 0.0})))[0] < inv]
    if bracos:
        sem_braco = _sondar(_acoplar(dict(infl, **{k: 0.0 for k in bracos})))[0]
        if sem_braco < inv:
            for f in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.0):
                tent = _acoplar({k: (round(v * f, 2) if k in bracos else v)
                                 for k, v in infl.items()})
                inv_f = _sondar(tent)[0]
                if inv_f <= sem_braco:
                    break
            print("    TRAVA do combinado: o braco paga primeiro - {:.0%} da faixa em {} "
                  "-> invertidas {}".format(f, ", ".join(bracos), inv_f))
            infl, inv = tent, inv_f
            mudou.update({k: infl[k] for k in bracos})
    if inv <= TOL_INV:
        _gravar_trava(base, co, resultado, mudou, sinal, lim)
        return

    # quem, tirado do estado, faz o defeito diminuir
    moveis = [r["key"] for r in resultado if infl.get(r["key"]) and not r.get("couple")]
    culpados = []
    for k in moveis:
        sem = _acoplar(dict(infl, **{k: 0.0}))
        if _sondar(sem)[0] < inv:
            culpados.append(k)
    if not culpados:
        culpados = moveis          # ninguem isolado explica: a soma e a culpada

    for f in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.0):
        tent = _acoplar({k: (round(v * f, 2) if k in culpados else v)
                         for k, v in infl.items()})
        inv_f = _sondar(tent)[0]
        if inv_f <= TOL_INV:
            break

    # ⚠️ ZERAR um morph inteiro por uma lasca e o pior desfecho (sessao 41:
    # zen_m_b06i_d3 perdeu a cintura positiva, +7,6 -> 0, por UM triangulo de
    # 0,06x a area mediana na axila). O criterio "quem, tirado sozinho, reduz"
    # achou so a cintura - peito e biceps tambem empurram ali, e nenhum deles
    # sozinho resolve. Se chegou a zero, tenta o grupo de TODOS os campos que
    # tocam as dobras, juntos; fica com ele se resolver sem zerar ninguem.
    if f == 0.0:
        soma = sum(r["delta"] * infl.get(r["key"], 0.0) for r in resultado)
        nr, area = base.normais(co + soma)
        virou = np.where(((nr * base.nrm0).sum(axis=1) < 0) & (area > base.area_min)
                         & (base.area0 > base.area_min))[0]
        tocam = [k for k in moveis
                 if len(virou) and masks[k][0][base.tris[virou]].max() > 0.05]
        if tocam and set(tocam) != set(culpados):
            for g in (0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3):
                alt = _acoplar({k: (round(v * g, 2) if k in tocam else v)
                                for k, v in infl.items()})
                if _sondar(alt)[0] <= TOL_INV:
                    print("    TRAVA do combinado: zeraria {} - o grupo das dobras resolve "
                          "a {:.0%}".format(", ".join(culpados), g))
                    f, tent, culpados, inv_f = g, alt, tocam, 0
                    break
    print("    TRAVA do combinado: {:.0%} da faixa em {} -> invertidas {}"
          .format(f, ", ".join(culpados), inv_f))
    mudou.update({k: tent[k] for k in culpados})
    _gravar_trava(base, co, resultado, mudou, sinal, lim)


def _gravar_trava(base, co, resultado, mudou, sinal, lim):
    """Reescreve a curva e o limite de quem a trava do combinado encolheu."""
    for r in resultado:
        if r["key"] not in mudou:
            continue
        novo = mudou[r["key"]]
        b0 = medir(base, co, r["column"]) * 100
        P = co + r["delta"] * novo
        for outro in resultado:                      # a forma anda junto
            if outro.get("couple") == r["key"] and novo > 0:
                P = P + outro["delta"] * novo
        v = medir(base, P, r["column"])
        cm = round(v * 100 - b0, 2) if v is not None else 0.0
        # so o lado travado encolhe - a curva do outro lado fica inteira
        pontos = [p for p in r["curve"]
                  if (p[0] > novo if sinal < 0 else p[0] < novo)]
        pontos.append([novo, cm])
        pontos.sort()
        r["curve"] = pontos
        r[lim] = novo
        r["cm_min" if sinal < 0 else "cm_max"] = cm
        print("      {:<16} {} {:+.2f} ({:+.1f} cm)".format(r["key"], lim, novo, cm))


def _ate_o_defeito(passos, limpo):
    """Ultima amplitude limpa antes do primeiro defeito, indo do zero para
    fora. `passos` vem ordenado por distancia crescente do zero."""
    ultimo = 0.0
    for p in passos:
        if not limpo.get(p, False):
            break
        ultimo = p
    return ultimo


def _conferir(src, dest, keys, resultado):
    """O arquivo novo tem que ser o velho MAIS os shape keys - nada a menos.

    Contagem de triangulos, conjunto de MATERIAIS (a regra 9 existe porque um
    script ja apagou 39 shorts em silencio), shape keys presentes em TODAS as
    primitivas e o deslocamento sobrevivendo ao round-trip."""
    import numpy as np

    def ler(p):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=p)
        obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        tris = sum(len(pl.vertices) - 2 for o in obs for pl in o.data.polygons)
        mats = sorted({m.name for o in obs for m in o.data.materials if m})
        v = []
        for o in obs:
            a = np.empty(len(o.data.vertices) * 3)
            o.data.vertices.foreach_get("co", a)
            v.append(a.reshape(-1, 3))
        return obs, tris, mats, np.concatenate(v)

    _, t0, m0, v0 = ler(src)
    obs, t1, m1, v1 = ler(dest)
    print("\nconferencia do round-trip:")
    print("  triangulos {} -> {}".format(t0, t1))
    print("  materiais  {} -> {}".format(m0, m1))
    if t0 != t1:
        print("  FALHOU: contagem de triangulos mudou")
        return False
    if m0 != m1:
        print("  FALHOU: o conjunto de materiais mudou (short apagado?)")
        return False
    # a malha base nao pode ter andado: shape key nao move o Basis
    a, b = np.sort(v0.ravel()), np.sort(v1.ravel())
    if len(a) == len(b):
        print("  base intacta: pior desvio {:.4f} mm".format(np.abs(a - b).max() * 1000))

    # ⚠️ A checagem tem que ser no glTF, nao no Blender: o importador FUNDE as
    # primitivas num objeto so, entao "o objeto tem shape key" nao responde se
    # o SHORT tem. E e o short que ficaria parado no app, porque cada primitiva
    # vira um THREE.Mesh com o seu proprio morphTargetInfluences.
    prims, nomes, esparsos, densos = _gltf_targets(dest)
    print("  primitivas com target: {} de {} | targetNames: {}"
          .format(sum(1 for t in prims if t == len(keys)), len(prims), ", ".join(nomes)))
    if not prims or any(t != len(keys) for t in prims):
        print("  FALHOU: primitiva sem os {} targets (achou {})".format(len(keys), prims))
        return False
    if nomes != keys:
        print("  FALHOU: targetNames {} != {}".format(nomes, keys))
        return False
    print("  accessors de target: {} esparsos, {} densos | arquivo {:.0f} KB"
          .format(esparsos, densos, os.path.getsize(dest) / 1024))
    if os.path.getsize(dest) > 3 * 1024 * 1024:
        print("  FALHOU: passou do orcamento de 3 MB por avatar (CLAUDE.md, regra 3)")
        return False

    # A ordem dos vertices muda no round-trip, entao compara a ESTATISTICA do
    # deslocamento, que e invariante a permutacao.
    pior = 0.0
    for r in resultado:
        alvo = np.concatenate([
            np.array([list(d.co) for d in o.data.shape_keys.key_blocks[r["key"]].data])
            for o in obs])
        lido = np.sort(np.linalg.norm(alvo - v1, axis=1))
        posto = np.sort(np.linalg.norm(r["delta_real"], axis=1))
        if len(lido) == len(posto):
            pior = max(pior, float(np.abs(lido - posto).max()) * 1000)
    print("  maior erro de deslocamento no round-trip: {:.3f} mm".format(pior))
    if pior > 0.5:
        print("  FALHOU: a quantizacao comeu o deslocamento")
        return False
    return True


def _gltf_targets(path):
    """(targets por primitiva, targetNames, accessors esparsos, densos) lidos
    do JSON do GLB - sem passar pelo importador."""
    import struct
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[12:16])[0]
    j = json.loads(d[20:20 + n])
    prims, nomes, esp, den = [], [], 0, 0
    for m in j["meshes"]:
        nomes = m.get("extras", {}).get("targetNames", nomes)
        for pr in m["primitives"]:
            alvos = pr.get("targets", [])
            prims.append(len(alvos))
            for t in alvos:
                for ai in t.values():
                    if "sparse" in j["accessors"][ai]:
                        esp += 1
                    else:
                        den += 1
    return prims, nomes, esp, den


def _gravar_mapa(root, aid, versao, resultado, dropped=()):
    """Le-modifica-grava do mapa, com TRAVA de arquivo e gravacao atomica.

    ⚠️ Sessao 42 (01/10): o lote passou a rodar em paralelo. Sem trava, dois
    workers leem o mesmo mapa e o ultimo a gravar apaga a entrada do outro; e
    se um le no meio da gravacao do outro, o JSON vem truncado - e o fallback
    antigo (`data = {}`) gravaria um mapa com UM avatar so. Agora JSON ilegivel
    PARA o script, em vez de recomecar do zero."""
    import time
    p = os.path.join(root, MAP_PATH)
    trava = p + ".lock"
    for _ in range(600):
        try:
            fd = os.open(trava, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            time.sleep(0.5)
    else:
        sys.exit("TRAVA: {} preso ha 5 min - apagar so se nenhum morph.py "
                 "estiver rodando".format(trava))
    try:
        _gravar_mapa_travado(p, aid, versao, resultado, dropped)
    finally:
        os.remove(trava)


def _gravar_mapa_travado(p, aid, versao, resultado, dropped):
    data = {}
    if os.path.isfile(p):
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[aid] = {
        "glb_version": versao,
        "dropped_columns": list(dropped),
        "calibrated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": ("influence = interp(usuario_cm - avatar_cm, curve[cm], "
                 "curve[influence]), ja limitada por construcao a "
                 "[influence_min, influence_max]. NAO usar cm_at_full x "
                 "influence: a relacao nao e linear em todo morph (ver "
                 "linearity_at_half). Morph com kind=flatten NAO tem coluna: "
                 "ele e acoplado - influence = max(0, influence do morph em "
                 "`couple`) quando couple_when=positive. O GLB tem 2 primitivas "
                 "(corpo e short): setar morphTargetInfluences em TODAS."),
        "morphs": [{k: r[k] for k in ("key", "column", "base_cm", "cm_at_full",
                                      "amplitude_m", "verts", "influence_min",
                                      "influence_max", "cm_min", "cm_max",
                                      "linearity_at_half", "curve", "kind",
                                      "couple", "couple_when", "depth_base_cm",
                                      "depth_without_cm", "depth_with_cm")
                    if k in r}
                   for r in resultado],
    }
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)
    print("mapa  : {}".format(p))


if __name__ == "__main__":
    if IN_BLENDER and "--worker" in sys.argv:
        worker_main()
    else:
        driver_main()
