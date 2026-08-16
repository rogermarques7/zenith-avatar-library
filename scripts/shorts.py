#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shorts.py - pinta o short de PRETO em cima do corpo titanio, um avatar por vez.

    python scripts/shorts.py --fit zen_m_b05_d3     # detecta, grava proposta, renderiza QA
    python scripts/shorts.py --fit --all
    python scripts/shorts.py --apply zen_m_b05_d3   # regrava 03_dist/glb/ com 2 materiais
    python scripts/shorts.py --apply --all
    python scripts/shorts.py --render zen_m_b05_d3  # so o QA, sem gravar dist

--------------------------------------------------------------------------
PORQUE A PRIMEIRA TENTATIVA FALHOU, E O QUE MUDA AQUI
--------------------------------------------------------------------------
O `process.py` segmentava o short projetando a IMAGEM FRONTAL de referencia
sobre a malha e chamando de short todo pixel escuro (SHORTS_LUMA_MAX), com
uma faixa de altura fixa como guarda-costas. Isso tem tres furos, e os tres
aparecem justamente nos avatares pesados:

  1. a projecao frontal nao sabe o que e frente e o que e costas - qualquer
     sombra escura nas costas virava short;
  2. a faixa de altura fixa (0.35-0.65 da altura) pressupoe proporcao
     constante, e a biblioteca vai de IMC 16 a 148: no b12_d1 o short vive
     numa faixa completamente diferente da do b02_d1;
  3. num corpo obeso a BARRIGA CAI POR CIMA do cos. O short deixa de comecar
     numa linha horizontal e passa a comecar embaixo da prega - que e uma
     curva, nao um plano. Nenhum limiar de altura descreve isso.

Aqui a fonte da verdade passa a ser a PROPRIA MALHA. Em 60k a bainha e o cos
existem como geometria: sao degraus de tecido, com vinco concavo do lado do
corpo. E o mesmo relevo que o Rogerio viu aparecer quando a malha subiu de
18k para 60k. Ou seja, o short ja estava modelado - faltava le-lo.

--------------------------------------------------------------------------
COMO O VINCO E SEPARADO DO MUSCULO
--------------------------------------------------------------------------
Concavidade sozinha nao serve: gomo abdominal, sulco do quadriceps e prega
de gordura sao todos concavos, e num corpo d3 sao mais fundos que a bainha.

O que distingue a bainha e o cos e a TOPOLOGIA, nao a profundidade: eles dao
a VOLTA no membro. Um sulco de musculo cobre um arco; uma bainha fecha o
circulo. Entao a pontuacao nao e "quao fundo", e sim "quanto do perimetro
esta vincado nesta altura" (`ring_score`).

Para isso cada fatia horizontal e resolvida na geometria dela mesma: a fatia
e separada em componentes (duas = duas pernas, uma = tronco), e o azimute e
medido em volta do centroide de CADA componente. Sem isso a perna esquerda e
a direita se misturam no mesmo azimute e o anel some no ruido.

De quebra a contagem de componentes entrega o VIRILHA de graca: e a maior
altura em que a fatia ainda se parte em duas.

--------------------------------------------------------------------------
O MODELO DA REGIAO, E PORQUE ELE E ASSIM
--------------------------------------------------------------------------
    short = (z >= bainha_da_perna) E (z <= cos(azimute))

O cos e uma FUNCAO DO AZIMUTE (`waist_by_bin`), nao um numero: e isso que
acompanha a prega da barriga caindo na frente e subindo nos lados. A bainha
e um numero por perna, porque bainha de short de compressao e um corte
horizontal mesmo - e dois numeros, nao um, porque a pose das folhas nao e
perfeitamente simetrica.

Acima da virilha o teste da bainha e satisfeito de graca (z ja e maior que
ela), entao nao ha caso especial para o tronco e nao ha costura entre as
duas regras.

--------------------------------------------------------------------------
O MAPA E O PRODUTO, NAO O DETECTOR
--------------------------------------------------------------------------
`config/shorts_map.json` guarda os numeros de cada avatar. O `--fit` PROPOE;
quem decide e o olho, avatar por avatar, no render de QA. Qualquer campo
escrito a mao com "source": "manual" e preservado por um `--fit` posterior -
so proposta automatica e sobrescrita.

Isso e deliberado: 39 corpos que vao de esqueletico a obesidade III nao tem
um detector unico que acerte todos, e fingir que tem foi exatamente o erro
da primeira tentativa. O detector existe para transformar 39 trabalhos
manuais em ~5.

Nada aqui toca 02_master/ (regra 7 do CLAUDE.md): igual ao restyle.py, le o
master e regrava so 03_dist/glb/.
"""

import argparse
import glob
import json
import os
import subprocess
import sys

BG_HEX = "#0D0D12"

# --- parametros do detector -------------------------------------------------
Z_BINS        = 240      # fatias horizontais sobre a altura toda
AZ_BINS       = 16       # setores de azimute por componente de fatia
CURV_SMOOTH   = 3        # passadas de suavizacao da concavidade (mata ruido de decimacao)
RING_QUANTILE = 0.35     # quantil sobre os setores de azimute (ver w_ring_map)
RING_SMOOTH   = 2        # suavizacao do perfil de ring_score em z
WAIST_AZ_BINS = 24       # resolucao azimutal do cos

# --- de quanto um setor do cos pode se afastar do anel ----------------------
# A JANELA E ASSIMETRICA, e a assimetria e o modelo anatomico que o docstring de
# w_back_side_mask ja declarava desde a primeira versao: a barriga cobre o cos
# SO NA FRENTE; nas costas e nos lados o elastico esta sempre a vista. Ate a
# sessao 5 o codigo nao aplicava isso - chamava w_ridge_by_azimuth com a MESMA
# janela larga nos 24 setores, para os dois lados. Duas familias de defeito
# sairam exatamente dessa folga, e as duas eram invisiveis para as duas reguas:
#
#   frente subindo  -> num corpo d3 nao existe prega, e o que existe no
#                      centro-frente e o sulco do baixo-ventre / V inguinal. O
#                      argmax subia nele e o cos ganhava uma ABA RETANGULAR de 4
#                      setores por cima do baixo-ventre (b06i_d3, b07_d3,
#                      b08_d3). Foi o que o Rogerio viu.
#   costas descendo -> nos dois IMC 107+ o anel nem foi achado (ver
#                      WAIST_ABOVE_CROTCH), a janela ficou centrada num chute, e
#                      nas costas o argmax pousou no SULCO GLUTEO. O cos cortava
#                      a bunda no meio (b11_d1, b11_d2).
#
# Os numeros nao sao chute - saem da propria biblioteca, medindo desvio em
# relacao ao anel nos 31 avatares que tem anel:
#
#   frente sobe acima do anel : maximo +0.0000 em 31/31 limpos
#                               +0.0208 / +0.0208 / +0.0250 nos 3 defeituosos
#   costas/lados descem       : maximo -0.0417 (b10_d1) em 31/31 limpos
#
# A separacao e total: "a frente nunca sobe acima do anel" nao e uma tolerancia
# escolhida, e uma lei que a serie inteira obedece e que so os defeitos quebram.
#
# ---------------------------------------------------------------------------
# E A TERCEIRA FAMILIA, a que o Rogerio pegou depois: A PINTURA SUBIU NA BARRIGA
# ---------------------------------------------------------------------------
# Nos corpos pesados a barriga cai POR CIMA do cos, entao o que o usuario ve na
# frente nao e o elastico - e a PREGA. O detector entregava uma reta quase plana
# e pintava de preto a barriga acima dela. Medido na folha de referencia
# (shorts_ref.py --tracado), o cos da frente e um ARCO cuja profundidade cresce
# com o IMC, e o erro do 3D crescia junto:
#
#   b05_d2 (IMC 27)  arco na folha 0.009   3D 0.008   erro -0.008
#   b08_d1 (IMC 48)  arco na folha 0.028   3D 0.017   erro -0.013
#   b11_d2 (IMC 112) arco na folha 0.076   3D 0.021   erro -0.050
#   b12_d1 (IMC 148) arco na folha 0.120   3D 0.017   erro +0.184  (~32 cm)
#
# A conclusao INTUITIVA seria abrir a janela da frente ate 0.22, ja que a folha
# mostra uma descida de 0.184. Medido nos 39, isso PIORA de 8 para 24 fora:
# janela funda nao acha prega funda, acha ruido fundo - nos corpos sem prega ela
# so da espaco para o argmax cair em qualquer coisa. O otimo medido e 0.12.
#
# O motivo de nao adiantar e mais fundo, e vale registrar: NOS CORPOS MUITO
# PESADOS A MALHA NAO TEM O SINAL. No centro da frente do b12_d1 a concavidade e
# 0.000 em toda a faixa, e um render de emissao pura mostra a barriga preta de
# ponta a ponta - o pannus e um dome liso e convexo, faz BALANCO e nao vinco.
# Nenhum ajuste de janela acha o que nao esta la. Para esses poucos avatares a
# curva da frente vem da folha, por shorts_ref.py --escrever, marcada manual.
WAIST_WINDOW_FRONT_DOWN = 0.12   # a frente desce ate a prega
WAIST_WINDOW_FRONT_UP   = 0.00   # e NUNCA sobe acima do anel
WAIST_WINDOW_BACK_ZH    = 0.05   # costas/lados: so o jogo do proprio elastico
WAIST_PRIOR_SIGMA       = 0.70   # largura do prior, em fracao da janela
WAIST_MEDIAN            = 7      # termos da mediana circular (era 5)

# --- e o ALISAMENTO, que e o filtro que a mediana nao e (ver w_waist_liso) ---
# SIGMA escolhido por RENDER nos dois extremos, como manda a LICOES 7.12: 0.7 /
# 1.0 / 1.6 setores no zen_f_b11_d1 (a parede) e no zen_f_b09_d2 (a tala
# diagonal), no banco de ensaio qa/probe/sondas/cos_liso_mapa.py.
WAIST_LISO_SIGMA     = 1.0   # sigma do alisamento circular, em SETORES
WAIST_LISO_TETO_BINS = 2.0   # licenca para SUBIR, em bins de Z_BINS (0.0083)
WAIST_LISO_ITERS     = 12    # alterna alisar / re-aplicar o teto

# --- O AVENTAL PENDE POR CIMA DO COS, e o corte por ALTURA pinta a pele ------
# Veredito do Rogerio em 12/08, com print de 8 avatares: *"a tinta nao segue o
# cos do short, voce pinta em cima da barriga"*. Medido no b09_d1, setor 4:
#
#   z=0.564  nz=-0.04   a barriga comeca a virar para baixo
#   z=0.524  nz=-0.13   <- o cos estava AQUI, no meio da face de baixo
#   z=0.468  nz=-0.92   o fundo da dobra: e aqui que o avental acaba
#
# Sao ~10 cm de pele dentro do material do short. O campo do w_field e
# `z <= cos(azimute)`, ou seja um corte por ALTURA; num corpo com avental a
# barriga desce ABAIXO dessa altura e cai dentro da regiao. Nao e o detector
# errando o vinco por pouco: o vinco que ele acha (concavidade maxima) fica no
# MEIO da face de baixo, e nao no fim dela.
#
# ✅ O QUE SEPARA PELE DE TECIDO E A ORIENTACAO DA SUPERFICIE. A face de baixo do
# avental aponta para baixo (nz ate -0.93); o tecido do short, na altura do cos,
# tem nz perto de zero. O fundo da dobra e o ponto MAIS BAIXO em que a face de
# baixo ainda existe - abaixo dele nao ha mais avental para pintar por engano.
#
# 🔴 E SO VALE NA FRENTE. Nas costas o mesmo sinal e o SULCO GLUTEO (nz -0.6 a
# -0.9 no b09_d1), que e short de verdade: descer o cos la e o defeito de
# "cortar a bunda no meio" que a WAIST_WINDOW assimetrica existe para evitar.
# O piso acima da virilha existe pelo mesmo motivo do outro lado: a virilha e o
# pube tambem apontam para baixo, e sem piso a frente desabaria ate la.
#
# ❌ ANTES DISTO EU LI O DEFEITO AO CONTRARIO e subi o cos 0.015 no lado da
# barriga, para fechar uma "listra clara" que eu tinha visto de tres-quartos.
# Aquela listra era a barriga aparecendo por cima do short - que e o certo, e e
# o que a folha de referencia mostra. A subida pintou 2,6 cm A MAIS de pele.
# Revertida. LICOES.md §4.5e.
COS_AVENTAL_NZ = -0.70     # mediana da normal vertical na fatia
COS_AVENTAL_PISO = 0.04    # acima da virilha; abaixo disso e pube, nao avental
COS_AVENTAL_SETORES = 7    # +-105 graus da frente (7 de 24); ver w_cos_avental

# 🔴 LATERAL EM DEGRAU (13/08). No zen_m_b11_d1 (IMC 107,3) a mediana de 3 nao
# bastou: a descida de ~17,5 cm ficou em DOIS degraus de exatamente 0.045 (o
# teto do WAIST_STEP_MAX_ZH partilhado com o resto do arquivo), um entrando na
# dobra e outro saindo - vira parede vertical no quadril, visivel de lado. O
# teto compartilhado foi calibrado para o PIOR ARCO REAL da folha (0.0399,
# LICOES em WAIST_STEP_MAX_ZH); aqui nao e arco real, e o degrau que sobra
# porque so 15 dos 24 setores podem receber a descida (COS_AVENTAL_SETORES).
# Um teto proprio, mais apertado, forca a correcao a se espalhar por mais
# setores dentro da mesma janela em vez de convergir em dois degraus no teto.
COS_AVENTAL_STEP_MAX_ZH = 0.020

# ❌ E A LEITURA QUE VEIO ANTES, para nao ser refeita ------------------------
# De tres-quartos aparece uma faixa clara entre a barriga e o preto, e eu a li
# como "tecido faltando" e subi o cos 0.015 para fecha-la. Estava errado: aquela
# faixa e a propria barriga aparecendo por cima do short, que e o que a folha de
# referencia mostra. Duas hipoteses geometricas foram construidas em cima dessa
# leitura errada (subir ate a crista de raio; subir onde a superficie alarga) e
# as duas tambem morreram medidas. O veredito dele veio no print: o problema
# nunca foi falta de preto, era preto DEMAIS. LICOES.md §4.5e.


# --- janelas de busca, ancoradas na VIRILHA e calibradas pela biblioteca -----
# A virilha e o unico marco anatomico que acompanha a distorcao de proporcao de
# um corpo de IMC 148. Distancia em fracao da altura, medida nos avatares que a
# primeira rodada acertou (n=33):
#
#   bainha abaixo da virilha : 0.024 a 0.045   -> janela 0.015 a 0.065
#   pico do cos acima dela   : 0.103 a 0.155   -> janela 0.090 a 0.170
#
# Os 6 que erraram caiam FORA dessas faixas e sem sobreposicao com elas (bainha
# em +0.001..+0.007 grudada na virilha, ou +0.095 no joelho; cos em
# +0.037..+0.051). Ou seja: a serie separa certo de errado sozinha, e a janela
# so precisa cortar no vazio entre os dois grupos.
#
# TETO DO COS REVISTO EM 0.170 -> 0.230 (sessao 5), e a licao aqui e a mesma da
# doutrina da regua externa: a faixa 0.103..0.155 foi medida no que O PROPRIO
# DETECTOR acertou, ou seja um teto calibrado com dados que o teto ja tinha
# filtrado. Medindo o cos na FOLHA DE REFERENCIA (shorts_ref.py), que e externa
# ao detector, a distancia real vai de 0.100 a 0.1944 nos 39 - e o teto de 0.170
# corta 3 deles. Nos dois piores (b11_d1 0.1718, b11_d2 0.1944) nao havia
# nenhum maximo local dentro da janela, entao w_peaks voltava VAZIO, waist_b
# caia no chute "virilha + 0.12" e a janela do ridge ficava boiando. Dai o cos
# cortando a bunda no meio. Corpo muito obeso tem virilha baixa e cintura alta:
# a distancia entre as duas cresce, e a janela precisa acompanhar.
HEM_BELOW_CROTCH   = (0.015, 0.065)
WAIST_ABOVE_CROTCH = (0.090, 0.230)

# --- o RECUO da bainha quando nao ha anel -----------------------------------
# Metade das femininas nao tem vinco de bainha em perna nenhuma, entao este
# numero nao e um caso de borda: e o que sai na maioria. Mesmo assim ele nunca
# tinha sido medido - 0.035 era um valor de partida.
#
# Medido na folha (regua externa) nos 24 avatares de virilha confiavel, a
# distancia virilha -> bainha e 0.0193 com desvio 0.0057. Varrido em
# qa/probe/sondas/_varre_bainha.py, com o erro contado nos 24 e o chute
# incluido, que e o que de fato sai:
#
#   janela 0.015..0.065  recuo 0.035   rms 0.0105  |max| 0.0239  1 fora de 0.02
#   janela 0.015..0.065  recuo 0.019   rms 0.0060  |max| 0.0123  0 fora de 0.02
#   janela 0.005..0.045  recuo 0.019   rms 0.0078  |max| 0.0155  0 fora de 0.02
#
# A JANELA NAO MUDA, e esse e o resultado que surpreende: alargar para achar
# mais anel (10 chutes -> 2) PIORA o rms, porque os aneis a mais sao os errados.
# O defeito nunca foi onde se procurava, era o que se respondia ao nao achar.
# Um recuo errado nao se denuncia: ele sai com a mesma cara de uma medida.
#
# So o feminino, e nao por anatomia: e que o masculino nao tem banco de anel
# cru e 39 avatares dele estao aprovados e entregues. Trocar constante de quem
# ja passou, sem a regua correspondente, e o erro que apagou os 39 shorts em
# 31/07. Medir o lado masculino esta pendente.
HEM_RECUO   = 0.035
HEM_RECUO_F = 0.019

# --- e uma segunda janela do cos, esta ABSOLUTA ------------------------------
# Abrir o teto acima era necessario para os IMC 107+, mas sozinho ele QUEBROU o
# b08_d1: com mais espaco, o anel agarrou um pico falso (dobra da barriga) em
# 0.635 e o cos inteiro subiu 0.098 acima da folha. Uma janela mais larga nao
# custa so ruido - ela troca o marco anatomico por outro.
#
# A saida foi perguntar a folha o que ela diz da altura ABSOLUTA do cos nos 39, e
# ela e bem mais estavel do que a sessao 4 supunha ao dizer que "nao existe
# altura absoluta que signifique a mesma coisa nos dois extremos": 36 dos 39
# caem entre 0.560 e 0.587, e so os tres mais pesados descem (0.504 · 0.528 ·
# 0.553). A faixa toda, 0.504..0.587, e mais ESTREITA que a ancorada na virilha
# (0.100..0.194) - e, ao contrario dela, nao depende de a virilha estar certa.
#
# As duas janelas ficam, e vale a INTERSECAO: ancorar so na virilha erra quando a
# virilha erra; ancorar so no absoluto erra num corpo de proporcao atipica.
# Medido contra a folha (qa/probe/varre_anel.py), sobre o topo do cos:
#
#   teto 0.170 (sessao 4)              4 sem anel   rms 0.0086
#   teto 0.230 sozinho                 2 sem anel   rms 0.0144   (b08_d1 +0.069)
#   teto 0.230 + absoluta 0.48..0.60   2 sem anel   rms 0.0090
WAIST_ABS_RANGE = (0.48, 0.60)

# --- ...e ela e MASCULINA. O short feminino e de cintura alta ----------------
# Os numeros acima saem das 39 folhas masculinas. Medida a mesma coisa nas 37
# femininas (qa/probe/sondas/faixa_ref.py), a distribuicao esta deslocada para
# cima: mediana 0.587 contra ~0.573, maximo 0.612, e ONZE das 37 em 0.59 ou
# acima. O teto de 0.60 cortava a propria populacao que devia cobrir - em tres
# avatares ele descartou um anel forte por um ou dois bins (b10_d3 tinha 0.253
# em 0.602, o b11_d2 tinha 0.171 em 0.594), que e a assinatura de "quem decidiu
# foi a janela, nao o sinal" (LICOES 1.8).
#
# Varrido sobre o banco de anel cru (qa/probe/sondas/_varre_janela.py), com a
# virilha ja corrigida e medindo o erro nos 37 - inclusive quem cai no chute,
# porque o chute e o que sai:
#
#   teto 0.600   9 sem anel   rms 0.0095   2 fora de 0.02
#   teto 0.610   4 sem anel   rms 0.0079   0 fora de 0.02   <--
#   teto 0.620   1 sem anel   rms 0.0084   1 fora de 0.02   (b09_d3 +0.023)
#
# 0.620 acha mais aneis e acerta menos: e o "janela larga troca o marco
# anatomico por outro" do bloco acima, agora do lado feminino. Entre um chute
# que se denuncia (waist_ring_found=False) e um pico errado que passa calado, o
# chute e preferivel.
WAIST_ABS_RANGE_F = (0.48, 0.61)

# Onde acaba o braco e comeca o tronco, na altura da faixa: a coluna de x cuja
# profundidade passa desta fracao da profundidade da fatia. Ver w_arm_wide.
PROF_FRAC = 0.60

# Largura da coluna daquela varredura, em fracao da altura (1.4 cm num corpo de
# 1.75 m). Era literal em dois lugares do w_arm_wide e virou constante quando o
# corte passou a ser o CENTRO da coluna e nao a borda - dois numeros que tem de
# andar juntos nao podem estar escritos duas vezes.
COL_W = 0.008

# De quantas colunas o corte anda para FORA depois de achado. Nao e ajuste fino
# de um avatar: e correcao de um vies do proprio PROF_FRAC, que responde "esta
# coluna ja e funda" e nao "aqui comeca o tronco". Medido no zen_f_b09_d2, que e
# o caso mais visivel, com o mesmo render em tres valores:
#
#   0 colunas  fiapo branco vertical dos dois lados, serrilhado, altura da faixa
#   1 coluna   fiapo some; sobra um dente pequeno na quina de baixo
#   2 colunas  a faixa INVADE o braco - lingueta preta saindo pela quina de baixo
#
# Um valor decidido por render precisa do render nos dois extremos, senao e
# chute com cara de calibracao (LICOES.md 7.12). Os tres estao acima.
ARM_COL_OUT = 1.0

# Grau do ajuste que tira a ESCADA do corte braco/tronco ao longo da altura.
# 0 desliga (volta ao comportamento so-mediana de 11/08) e existe para o banco
# de ensaio poder fotografar o antes. Ver a PASSADA 2 do w_arm_wide.
ARM_AJUSTE_GRAU = 2

# A ordem das pecas no w_field(partes=True): 0 short, 1 faixa. So a faixa pode
# sair legitimamente partida em duas (braco tapando o lado do torax).
FAIXA_PECA = 1
# Fracao da altura da banda que uma ilha precisa cobrir para contar como pedaco
# de faixa, e nao como franja do corte. O vazio medido vai de 7% a 60%.
FAIXA_PECA_ALT_MIN = 0.30


# --- A SEGUNDA PECA: a FAIXA do peito (feminino, 01/08) ----------------------
# A roupa feminina e faixa reta + short (CHARACTER_BIBLE 5), e a faixa foi
# escolhida justamente porque a borda dela e ANEL FECHADO - a mesma topologia do
# cos e da bainha, que e a unica que este detector sabe achar.
#
# As janelas aqui NAO sao ancoradas na virilha, e a diferenca em relacao ao short
# e medida, nao estilistica: o short se move com a proporcao do corpo (a virilha
# de um IMC 148 esta em 0.297 e a de um IMC 16 em 0.38), enquanto a faixa mora no
# torax de um personagem que tem sempre a mesma altura. Medido na folha de
# referencia das 37 (qa/probe/sondas/faixa_ref.py, regua EXTERNA):
#
#   topo da faixa : 0.705 .. 0.735   (37 de 37)
#   base da faixa : 0.654 .. 0.686   (37 de 37)
#
# 0.030 de dispersao contra os 0.083 do cos - e sem depender de a virilha estar
# certa. Entao aqui a ancora absoluta nao e a segunda regua, e a primeira.
FAIXA_BASE_RANGE = (0.635, 0.700)

# --- O TOPO NAO E UMA SEGUNDA MEDIDA: E A BASE MAIS A ALTURA DA PECA ---------
# A primeira versao procurou as duas bordas como se fossem independentes, cada
# uma com sua janela absoluta, e o topo errou ate 0.034 contra a folha (uns 6 cm
# de tecido) - em cinco avatares o anel do topo nem existia e valia um chute.
#
# A folha explica por que: medida a altura da faixa nas costas nas 37 folhas, ela
# da 0.0504 com desvio de 0.0037. E a MESMA PECA em todo mundo. A base, essa sim,
# varia com o corpo: 0.654 .. 0.685, desvio 0.0080. Ou seja, havia UMA incognita
# e o detector procurava duas - e a segunda tinha o sinal mais fraco, porque o
# sulco inframamario e um vinco de verdade e a borda de cima e so tecido.
#
# Entao o topo passa a ser ancorado em base + FAIXA_ALTURA_ZH, e o anel das
# costas so tem licenca para ajustar dentro de FAIXA_ALTURA_TOL (3 desvios da
# folha). Medido nas 37 contra a folha, sem abrir o Blender (varre_faixa.py
# novo): erro medio do topo caiu de "ate 0.034 e cinco chutes" para 0.0075, com
# maximo 0.027 em dois avatares que ja erram na base pelo mesmo tanto.
FAIXA_BASE_MEDIANA = 0.672    # mediana da base nas 37 folhas
FAIXA_BASE_SIGMA = 0.030      # prior largo: a base desce mesmo com o IMC
FAIXA_ALTURA_ZH = 0.050       # altura da peca nas costas (folha: 0.0504 ± 0.0037)
FAIXA_ALTURA_TOL = 0.012      # licenca do anel para corrigir a ancora
FAIXA_PICO_MIN = 0.012        # abaixo disso nao e vinco, e a borda da janela

# --- e a borda de cima E CURVA, pelo motivo oposto ao do cos -----------------
# O cos e curva porque a barriga CAI POR CIMA dele. A borda de cima da faixa e
# curva porque o BUSTO A EMPURRA PARA CIMA. Nos dois casos a peca sobe onde o
# corpo tem volume, e nos dois a curva mora so na FRENTE.
#
# Isto quase passou batido: com a borda tratada como escalar, o render da frente
# do zen_f_b05_d2 mostrou o terco de cima da faixa MODELADA sem pintura, e o
# render das costas ficou perfeito. Medido nas duas vistas da folha das 37
# (faixa_ref.py):
#
#   topo nas costas : 0.705 .. 0.735
#   topo na frente  : 0.750 .. 0.776     delta +0.031 a +0.060
#
# A ancora, por isso, so pode ser medida NAS COSTAS E NOS LADOS - a mesma
# mascara que o cos usa (w_back_side_mask), e pelo mesmo motivo: o quantil baixo
# sobre TODOS os setores nao ve o anel das costas, porque na frente aquela altura
# esta no meio do tecido e nao tem vinco nenhum. Com a mascara, o anel das costas
# aparece onde a folha diz (b05_d2: 0.723 contra 0.719; b09_d1: 0.727 contra
# 0.730).
FAIXA_TOPO_UP_FRONT = 0.070   # o busto empurra a borda para cima (folha: ate 0.060)
FAIXA_TOPO_BACK_ZH = 0.025    # costas e lados: so o jogo do proprio elastico

# --- A SUBIDA FRONTAL MODELADA, ancorada na folha (11/08, sessao 26) ---------
# A busca setor a setor nao mede: em 4 a 9 dos 9 setores da frente nao ha aro
# nenhum (LICOES.md 4.5b), o argmax pega ruido e a mediana de 7 devolve a propria
# ancora. Medido no b08_d3: dos 24 setores, 22 ficaram na ancora e 2 dispararam
# para +0.046 - a "cunha no esterno". Nao e traçado, e ruido com forma.
#
# O que MUDOU em relacao a 4.5b, e que reabre a decisao: a altura do topo frontal
# TEM regua externa POR AVATAR. O faixa_ref.py le a corrida escura na vista
# FRONTAL da folha de referencia e devolve o topo em 35 das 37 (duas ilegiveis,
# b08_d1 e b11_d1, que leem 0.869 e 0.861 - a regua pega a corrida errada e se
# denuncia sozinha). A 4.5b diz "nao existe regua externa para o traçado por
# setor", e isso continua verdade: o que ela nao creditou e que a ALTURA DO PICO
# tem uma, e o pico e a unica incognita que um modelo precisa.
#
# Entao aqui a frente para de ser procurada e passa a ser MODELADA, como ja se
# fez com o topo escalar ("O TOPO NAO E UMA SEGUNDA MEDIDA", acima): plato na
# altura da folha nos setores centrais, meia-cossenoide descendo ate a ancora nos
# das costas e dos lados. Zero busca, zero argmax, zero mediana - o traçado deixa
# de ter grau de liberdade que ninguem mede.
#
# Os dois raios sao em SETORES e nao em graus porque e a resolucao real do campo
# (24 setores = 15 graus cada); o w_interp_circ suaviza o resto.
# ⚠️ O PLATO COBRE A FRENTE INTEIRA, e isso foi corrigido no olho DELE.
# A primeira versao usava plato 2 / raio 5, ou seja o teto so nos 5 setores
# centrais e a descida ja comecando dentro da frente. Ficou faixa branca no
# TERCO DE FORA da peca nos 37 - fina no meio, larga nos lados -, e eu nao vi
# porque estava julgando pelo render do --fit, que e clay com luz chapada e nao
# separa tecido de corpo. No GLB entregue, com o material e o HDR, e obvia.
# A borda de cima e reta: a folha diz frente 0.750..0.776 e costas 0.705..0.735,
# e a transicao entre as duas nao acontece ATRAVESSANDO o peito - acontece nos
# setores do LADO. Plato 4 = a mascara da frente inteira (setores 2..10), e a
# descida mora fora dela. Ver LICOES.md 4.5c.
FAIXA_FRENTE_PLATO = 4        # setores de cada lado do centro que ficam no teto
FAIXA_FRENTE_RAIO = 7         # onde a subida ja voltou a ancora, ja nos lados


def tem_faixa(aid):
    """A peca de cima e propriedade da COLECAO, nao do corpo.

    Sexo e colecao separada (CLAUDE.md), e a roupa e parte da colecao: todo
    avatar feminino tem faixa + short, todo masculino tem so short. Nao ha caso
    intermediario para detectar, entao a pergunta se responde pelo id."""
    return aid.startswith("zen_f_")


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def map_path(root):
    return os.path.join(root, "config", "shorts_map.json")


def load_map(root):
    p = map_path(root)
    if not os.path.isfile(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_map(root, data):
    p = map_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def _die(msg, code=2):
    sys.stderr.write("\n[ERRO] " + msg + "\n")
    sys.exit(code)


def find_blender():
    import shutil
    env = os.environ.get("BLENDER")
    if env:
        if os.path.isfile(env):
            return env
        _die("A variavel BLENDER aponta para arquivo inexistente:\n  {}".format(env))
    onpath = shutil.which("blender")
    if onpath:
        return onpath
    candidates = []
    for base in (r"C:\Program Files\Blender Foundation",
                 r"C:\Program Files (x86)\Blender Foundation"):
        candidates += glob.glob(os.path.join(base, "Blender *", "blender.exe"))
    candidates += glob.glob("/Applications/Blender*.app/Contents/MacOS/Blender")
    candidates += ["/usr/bin/blender", "/usr/local/bin/blender", "/snap/bin/blender"]
    existing = sorted(c for c in candidates if os.path.isfile(c))
    if existing:
        return existing[-1]
    _die("Blender nao encontrado. Defina a variavel BLENDER apontando para o executavel.")


def discover_ids(root):
    """Ordem = measured_bmi do library.json, nao alfabetica. Vizinhos de corpo
    ficam lado a lado, que e como o QA do short se julga (o short do IMC 34 tem
    que parecer o mesmo do IMC 35). Sem indice, cai para alfabetica."""
    masters = {os.path.basename(p)[: -len("_master.glb")]
               for p in glob.glob(os.path.join(root, "02_master", "*_master.glb"))}
    lib = os.path.join(root, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            data = json.load(f)
        ordered = [a["id"] for a in sorted(data.get("avatars", []),
                                           key=lambda a: a.get("measured_bmi", 0))]
        out = [i for i in ordered if i in masters]
        out += sorted(masters - set(out))
        return out
    return sorted(masters)


def composite_previews(paths, bg_hex):
    from PIL import Image
    bg = tuple(int(bg_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    for p in paths:
        im = Image.open(p).convert("RGBA")
        flat = Image.new("RGBA", im.size, bg)
        flat.alpha_composite(im)
        flat.convert("RGB").save(p)


# Salto maximo tolerado entre setores VIZINHOS do cos, em fracao da altura.
# Calibrado na FOLHA (shorts_ref.py --tracado), nao na serie 3D: o maior passo
# real da biblioteca e 0.0399 (b12_d1, o arco da barriga pendente), e o segundo
# 0.0376 (b11_d2). A primeira versao desta trava usou a serie 3D e saiu em
# 0.032 - que e MENOR que o arco verdadeiro e reprovaria o resultado certo.
# Mesma armadilha da doutrina da regua externa: calibrar um limite com dados
# que o proprio limite ja filtrou.
WAIST_STEP_MAX_ZH = 0.045

# --- ...e a QUINA, que e o degrau que o degrau nao pega (15/08, sessao 30) ---
# O Rogerio mandou 7 prints do testador com o cursor em cima do defeito, e o
# defeito e o mesmo nos sete: a borda de CIMA do short e uma poligonal. Parede
# vertical no flanco do b11_d1, cunha angulosa no b12_d1/b10_d1/b11_d2, tala
# diagonal atravessando a barriga no b09_d2 e no b08_d1, quina seca no b06_d1.
#
# A trava de DEGRAU nao via nada disso, e o motivo e que ela pergunta a coisa
# errada. Ela mede |w[j] - w[j+1]|, ou seja INCLINACAO, e inclinacao alta e
# legitima: o arco da barriga do b12_d1 desce 0.0399 por setor na folha. O que
# a vista mostra nao e a inclinacao, e a MUDANCA dela - o vinco onde um trecho
# reto encontra outro. Isso e a segunda diferenca:
#
#     canto = |w[j-1] - 2*w[j] + w[j+1]|
#
# Medida nos 37 femininos, ela separa a lista dele do resto quase sozinha:
#
#   os 7 apontados       0.020 .. 0.092   (b11_d1 0.092, b12_d1 0.037)
#   os 30 nao apontados  0.004 .. 0.029   com 27 deles <= 0.017
#
# Os tres de cima dos nao apontados (b06h_d3 0.029, b10_d3 0.025, b10_d2 0.021)
# ficam do lado errado do corte - e isso e informacao, nao ruido: ele mandou
# "os 7 com defeito MAIS visivel", nao "os 7 unicos". O corte fica em 0.018,
# que e o vao entre 0.017 e 0.020.
#
# ⚠️ Ela reprova tambem 11 masculinos, do b05i_d1 (0.021) ao b12_d1 (0.121).
# Nao e trava nova mentindo: e o mesmo defeito, na colecao que ele aprovou como
# "melhorou bastante" e nao como "pronto". Nenhum GLB masculino foi tocado.
WAIST_CANTO_MAX_ZH = 0.018


def _trace_flags(e):
    """Travas de TRACADO do cos - o que faltava nas duas reguas.

    O --report media so a ALTURA do topo do cos e o shorts_ref.py so comparava
    essa altura com a folha. Um cos com o topo certo e o CAMINHO errado passava
    nas duas: foi assim que a aba retangular dos d3 e o cos cortando a bunda dos
    b11 chegaram aos 39 aplicados sem nenhum alarme. Estava anotado como
    pendencia 3 do state.md e custou o Rogerio ver no olho, de novo.

    Sao tres perguntas, e cada uma pega uma familia diferente:

      SEM-ANEL  o anel nem foi achado, a curva boia sobre um chute
      FRENTE^   algum setor da frente esta ACIMA do anel - a barriga so pode
                empurrar o elastico para BAIXO; subir significa que o argmax
                pegou sulco de musculo (baixo-ventre / V inguinal)
      DEGRAU    salto entre setores vizinhos maior que tecido nenhum faz
      CANTO     a inclinacao MUDA de repente - dois trechos retos se encontrando
                num vinco. E o que se ve, e o DEGRAU nao pega (ver
                WAIST_CANTO_MAX_ZH)"""
    out = []
    diag = e.get("diag", {})
    w = e.get("waist_zh")
    if not isinstance(w, (list, tuple)) or len(w) < 4:
        return out

    n = len(w)
    pk = diag.get("waist_peaks_zh")
    # waist_ring_zh so existe em mapa gravado da sessao 5 em diante; antes disso
    # o anel so da para reconstruir pelo primeiro pico, que e como w_fit o escolhe.
    ring = diag.get("waist_ring_zh")
    if ring is None and pk:
        ring = pk[0][1]
    if diag.get("waist_ring_found", bool(pk)) is False:
        out.append("SEM-ANEL")

    if ring is not None:
        front = n // 4                    # mesma convencao de w_back_side_mask
        half = max(1, n // 6)
        acima = [d for d in range(-half, half + 1)
                 if w[(front + d) % n] > ring + 1e-6]
        if acima:
            out.append("FRENTE^{}".format(len(acima)))

    salto = max(abs(w[i] - w[(i + 1) % n]) for i in range(n))
    if salto > WAIST_STEP_MAX_ZH:
        out.append("DEGRAU{:.3f}".format(salto))

    canto = max(abs(w[(i - 1) % n] - 2 * w[i] + w[(i + 1) % n]) for i in range(n))
    if canto > WAIST_CANTO_MAX_ZH:
        out.append("CANTO{:.3f}".format(canto))
    return out


def _hem_flags(e, gap):
    """Travas da BAINHA - e a primeira delas denuncia o CHUTE.

    Ate 01/08 a bainha so tinha a trava de faixa (v-b dentro de
    HEM_BELOW_CROTCH), e ela e cega para o defeito que mais custou nesta frente:
    quando w_peaks volta VAZIO, w_fit grava `virilha - 0.035` e segue em frente.
    O chute cai dentro da faixa por construcao - a faixa E ancorada na virilha -
    entao ele passa limpo, para sempre. Cinco avatares viveram assim, e os
    QUATRO maiores erros de bainha da biblioteca eram exatamente eles
    (-0.041 a -0.048 contra a folha, ou uns 8 cm de perna preta a mais).

    E a mesma familia do `at_band_edge` do metrics.py (LICOES.md 1.8): as travas
    olhavam QUANTO a bainha valia e nenhuma olhava se ela tinha sido MEDIDA.

      BAINHA-CHUTE  hem_peaks_zh vazio nas DUAS pernas e ninguem corrigiu
      chute:1perna  vazio em UMA perna - a outra sustenta a altura, entao e
                    nota e nao reprovacao (b01_d2 e b04_d3, os dois com erro
                    normal contra a folha: -0.012 e -0.011)
      BAINHA        medida, mas fora da faixa da serie

    E quando a bainha vem do resgate por anel (hem_fonte), a faixa v-b DEIXA DE
    VALER, de proposito: ela mede a distancia ate a `virilha` do w_limbs, que
    nesses corpos nao e a virilha anatomica e sim a altura em que as coxas param
    de se tocar - nos IMC 100+ isso fica ABAIXO da bainha real, e v-b sai
    negativo. A regua que vale ali e a externa (shorts_ref.py), e ela concorda:
    b08_d3 -0.003, b09_d1 +0.004, b11_d1 +0.015, b11_d2 -0.003 contra a folha."""
    diag = e.get("diag", {})
    pk = diag.get("hem_peaks_zh", [[], []])
    vazias = sum(1 for p in pk if not p) if isinstance(pk, list) else 0
    na_faixa = HEM_BELOW_CROTCH[0] <= gap <= HEM_BELOW_CROTCH[1]
    if e.get("hem_fonte"):
        return [] if na_faixa else ["v-b:fusao"]
    if vazias == 2:
        return ["BAINHA-CHUTE"]
    out = ["chute:1perna"] if vazias == 1 else []
    if not na_faixa:
        out.append("BAINHA")
    return out


FAIXA_MIN_ALTURA_ZH = 0.030   # folha: 0.045 nas costas; abaixo disso ja e tira


def _faixa_flags(e):
    """Travas da FAIXA. Escritas junto com a peca, e nao depois dela, porque a
    licao do cos foi essa: o tracado errado passou 39 vezes por nao ter pergunta
    que olhasse para o CAMINHO.

      FAIXA-CHUTE   o anel de uma das bordas nao foi achado e valeu a mediana da
                    folha. Cai dentro da janela por construcao, entao nenhuma
                    trava de valor pega - so esta (mesma familia do BAINHA-CHUTE)
      BORDA-BASE    o pico encostou no limite da janela de busca: a janela e que
                    decidiu, nao o vinco. Doutrina do at_band_edge (LICOES 1.8)
      FRENTEv       setor da frente ABAIXO do anel das costas - o busto so pode
                    empurrar o tecido para CIMA; descer e sulco de musculo
      DEGRAU-F      salto entre setores vizinhos maior que tecido nenhum faz
      TIRA          topo e base perto demais: a faixa fechou

    NAO EXISTE BORDA-TOPO, E ISSO E DE PROPOSITO. Cheguei a escrever uma, e ela
    nao podia falar coisa alguma: o topo das costas e `base + FAIXA_ALTURA_ZH`
    com licenca de +-FAIXA_ALTURA_TOL, ou seja a janela toda tem ~6 bins e a
    maior correcao possivel sao 2. Uma trava ali perguntaria ao topo se ele bate
    com o alvo que o proprio codigo lhe deu - e a regra 3 do CLAUDE.md ja diz
    que trava que confere o alvo contra ele mesmo nao valida o alvo. Quem julga
    a ancora e regua EXTERNA: a coluna 3D-folha do faixa_ref.py, que le a folha
    de referencia. O delta continua no diag (faixa_topo_alvo_zh contra
    faixa_topo_anel_zh) para quem quiser olhar, mas nao vira reprovacao."""
    hi = e.get("faixa_hi_zh")
    if hi is None:
        return []
    hi = list(hi) if isinstance(hi, (list, tuple)) else [hi]
    lo = e["faixa_lo_zh"]
    diag = e.get("diag", {})
    out = []

    # SO A BASE REPROVA. Chutar a base e grave: cai numa mediana global que
    # ignora o corpo. Chutar o topo nao e a mesma coisa desde que ele virou
    # ancora - o "chute" ali e `base + altura da folha`, que continua sendo um
    # numero DAQUELE corpo, e e o caso NORMAL: o anel das costas so refina.
    # Reprovar os dois junto marcava 17 das 37 e transformava a trava em ruido.
    if not diag.get("faixa_anel_base", True):
        out.append("FAIXA-CHUTE")
    elif not diag.get("faixa_anel_topo", True):
        out.append("topo:ancora")

    passo = 1.0 / Z_BINS
    if min(abs(lo - FAIXA_BASE_RANGE[0]), abs(lo - FAIXA_BASE_RANGE[1])) <= passo:
        out.append("BORDA-BASE")

    anel = diag.get("faixa_topo_anel_zh")
    if anel is not None:
        n = len(hi)
        front = n // 4
        half = max(1, n // 6)
        abaixo = [d for d in range(-half, half + 1)
                  if hi[(front + d) % n] < anel - 1e-6]
        if abaixo:
            out.append("FRENTEv{}".format(len(abaixo)))

    if len(hi) > 1:
        salto = max(abs(hi[i] - hi[(i + 1) % len(hi)]) for i in range(len(hi)))
        if salto > WAIST_STEP_MAX_ZH:
            out.append("DEGRAU-F{:.3f}".format(salto))

    if min(hi) - lo < FAIXA_MIN_ALTURA_ZH:
        out.append("TIRA{:.3f}".format(min(hi) - lo))
    return out


def report(root):
    """Tabela de coerencia ANATOMICA do mapa. Nao abre o Blender: le so o
    shorts_map.json, entao roda em um piscar e da para conferir a cada mudanca.

    Foi este relatorio - e nao a folha de contato - que achou os 6 avatares
    errados da primeira rodada. O motivo e que short se julga na SERIE: um
    short isolado quase sempre parece plausivel, mas 'bainha 9,5% da altura
    abaixo da virilha' salta aos olhos quando os outros 33 estao em 2,4-4,5%.
    Numa biblioteca que vai de IMC 16 a 148 nao existe altura absoluta que
    signifique a mesma coisa nos dois extremos; ancorar na virilha, sim."""
    smap = load_map(root)
    if not smap:
        print("mapa vazio - rode --fit antes.")
        return 1

    bmi = {}
    lib = os.path.join(root, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            bmi = {a["id"]: a.get("measured_bmi", 0) for a in json.load(f)["avatars"]}

    def _one(v):
        return v[0] if isinstance(v, (list, tuple)) else v

    print("{:<15} {:>6}  {:>7} {:>7} {:>8}  {:>7} {:>8}  {:>13}  {}".format(
        "id", "imc", "virilha", "bainha", "v-b", "cos-topo", "topo-v",
        "faixa b/t/fre", "obs"))
    print("-" * 104)
    fora = []
    for aid in sorted(smap, key=lambda k: bmi.get(k, 0)):
        e = smap[aid]
        c = e.get("diag", {}).get("crotch_zh")
        if c is None:
            continue
        hem = _one(e["hem_l_zh"])
        w = e["waist_zh"]
        wmax = max(w) if isinstance(w, (list, tuple)) else w
        gap, rise = c - hem, wmax - c
        obs, notas = [], []
        for f in _hem_flags(e, gap):
            (notas if f.islower() else obs).append(f)
        if not (WAIST_ABOVE_CROTCH[0] <= rise <= WAIST_ABOVE_CROTCH[1] + 0.06):
            obs.append("COS")
        obs += _trace_flags(e)
        for f in _faixa_flags(e):
            (notas if f.islower() else obs).append(f)
        pp = e.get("por_peca") or [e.get("islands", 1)]
        # ZERO ilha nao e "menos defeito que duas", e a peca faltando. O
        # max(pp)>1 sozinho passava batido no zen_f_b05_d3, que saiu [1, 0]:
        # o --apply recusava (vazias -> suspect) mas o RELATORIO dizia que
        # estava tudo bem, e o relatorio e por onde eu decido.
        if min(pp) < 1:
            obs.append("PECA-VAZIA{}".format(pp))
        if max(pp) > 1:
            obs.append("ILHAS{}".format(pp))
        if obs:
            fora.append(aid)
        fx = "{:>13}".format("-")
        hi = e.get("faixa_hi_zh")
        if hi is not None:
            hi = list(hi) if isinstance(hi, (list, tuple)) else [hi]
            n = len(hi)
            fx = "{:.3f}/{:.3f}/{:.3f}".format(
                e["faixa_lo_zh"],
                e.get("diag", {}).get("faixa_topo_anel_zh", max(hi)),
                hi[n // 4])
        print("{:<15} {:>6.1f}  {:>7.3f} {:>7.3f} {:>+8.3f}  {:>7.3f} {:>+8.3f}  {}  {} {}".format(
            aid, bmi.get(aid, 0), c, hem, gap, wmax, rise, fx,
            " ".join(obs + notas), "<<" if obs else ""))
    print("-" * 104)
    print("faixas da serie: v-b {} .. {}   topo-v {} .. {}".format(*HEM_BELOW_CROTCH,
                                                                  *WAIST_ABOVE_CROTCH))
    print("{}/{} dentro da faixa".format(len(smap) - len(fora), len(smap)))
    if fora:
        print("conferir: {}".format(", ".join(fora)))
    return 0


def contact_sheet(root, ids, out_path):
    """Folha de contato das frentes: o short so se julga na SERIE. Um short
    isolado quase sempre parece plausivel; o que denuncia erro e o vizinho de
    IMC ao lado com a bainha noutra altura."""
    from PIL import Image
    tiles = []
    for aid in ids:
        p = os.path.join(root, "qa", "shorts", aid, "0_frente.png")
        if os.path.isfile(p):
            tiles.append((aid, p))
    if not tiles:
        return None
    cols = 8
    tw, th = 200, 290
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (13, 13, 18))
    for i, (aid, p) in enumerate(tiles):
        im = Image.open(p).convert("RGB")
        im.thumbnail((tw, th - 14))
        x = (i % cols) * tw + (tw - im.width) // 2
        y = (i // cols) * th
        sheet.paste(im, (x, y))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path)
    return out_path


# ============================================================================
# DRIVER
# ============================================================================

def driver_main():
    ap = argparse.ArgumentParser(
        description="Segmenta e pinta o short dos avatares Zenith, um a um.")
    ap.add_argument("id", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--fit", action="store_true",
                    help="detecta a regiao, grava a proposta no mapa e renderiza QA")
    ap.add_argument("--apply", action="store_true",
                    help="regrava 03_dist/glb/ com corpo + short")
    ap.add_argument("--render", action="store_true",
                    help="so o render de QA, a partir do que ja esta no mapa")
    ap.add_argument("--check", action="store_true",
                    help="so as travas (regiao conexa), sem render - varredura rapida")
    ap.add_argument("--refit", action="store_true",
                    help="com --fit, sobrescreve tambem entradas marcadas manual")
    ap.add_argument("--sheet", action="store_true",
                    help="monta a folha de contato a partir dos QA existentes")
    ap.add_argument("--report", action="store_true",
                    help="tabela de coerencia anatomica do mapa (instantanea)")
    args = ap.parse_args()

    root = repo_root()

    if args.report:
        return report(root)

    if args.sheet:
        out = contact_sheet(root, discover_ids(root),
                            os.path.join(root, "qa", "shorts", "_contato.png"))
        print("folha de contato: {}".format(os.path.relpath(out, root) if out else "nada a montar"))
        return 0

    modes = [m for m in ("fit", "apply", "render", "check") if getattr(args, m)]
    if len(modes) != 1:
        _die("Escolha exatamente um de --fit / --apply / --render / --check.")
    mode = modes[0]

    if args.all and not args.id:
        ids = discover_ids(root)
    elif args.id and not args.all:
        ids = list(args.id)
    else:
        _die("Informe ao menos um id OU --all.")

    blender = find_blender()
    smap = load_map(root)

    print("Blender : {}".format(blender))
    print("Modo    : {}".format(mode))
    print("IDs     : {}".format(len(ids)))
    print("-" * 74)

    failures = []
    for aid in ids:
        master = os.path.join(root, "02_master", aid + "_master.glb")
        if not os.path.isfile(master):
            print("[SKIP] {}: sem master".format(aid))
            failures.append(aid)
            continue
        entry = smap.get(aid)
        if mode == "fit" and entry and entry.get("source") == "manual" and not args.refit:
            print("[keep] {}: manual, preservado (use --refit para sobrescrever)".format(aid))
            mode_i = "render"
        else:
            mode_i = mode
        if mode_i in ("apply", "render", "check") and not entry:
            print("[SKIP] {}: sem entrada no mapa - rode --fit antes".format(aid))
            failures.append(aid)
            continue

        cmd = [blender, "--background", "--python", os.path.abspath(__file__), "--",
               "--worker", "--mode", mode_i, "--id", aid, "--root", root]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.stdout.decode("utf-8", "replace")
        if proc.returncode != 0:
            print("[FAIL] {} (codigo {})".format(aid, proc.returncode))
            for line in out.splitlines()[-25:]:
                print("       | " + line)
            failures.append(aid)
            continue

        # O Blender sai com codigo 0 mesmo quando o script levanta excecao, entao
        # returncode NAO e prova de sucesso - um worker que estourou ja foi
        # reportado como [ok] aqui. A prova e a linha RESULT.
        for line in out.splitlines():
            if line.startswith("RESULT "):
                res = json.loads(line[len("RESULT "):])
                if mode_i == "fit":
                    res["source"] = "auto"
                    smap[aid] = res
                    save_map(root, smap)
                print("[ok]   {}".format(res.get("summary", aid)))
                break
        else:
            print("[FAIL] {}: worker terminou sem RESULT".format(aid))
            for line in out.splitlines()[-15:]:
                print("       | " + line)
            failures.append(aid)

        look = os.path.join(root, "qa", "shorts", aid)
        pngs = sorted(glob.glob(os.path.join(look, "*.png")))
        if pngs:
            composite_previews(pngs, BG_HEX)

    print("-" * 74)
    print("{}/{} ok".format(len(ids) - len(failures), len(ids)))
    if len(ids) > 1:
        sheet = contact_sheet(root, ids, os.path.join(root, "qa", "shorts", "_contato.png"))
        if sheet:
            print("folha de contato: {}".format(os.path.relpath(sheet, root)))
    if failures:
        print("falharam: {}".format(", ".join(failures)))
        return 1
    return 0


# ============================================================================
# WORKER (dentro do Blender)
# ============================================================================

def w_curvature(me, np, passes=None):
    """Concavidade por vertice: media de dot(normalize(u-v), n) no 1-ring.
    >0 = vizinhos acima do plano tangente = vale. Suavizada, porque a 60k a
    decimacao deixa um ruido de ~5 graus por aresta que abafa a bainha."""
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    nor = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("normal", nor)
    nor = nor.reshape(n, 3)

    ei = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ei)
    ei = ei.reshape(-1, 2)
    a, b = ei[:, 0], ei[:, 1]

    d = co[b] - co[a]
    L = np.linalg.norm(d, axis=1)
    L[L == 0] = 1e-9
    dn = d / L[:, None]

    acc = np.zeros(n)
    cnt = np.zeros(n)
    np.add.at(acc, a, np.einsum("ij,ij->i", dn, nor[a]))
    np.add.at(cnt, a, 1.0)
    np.add.at(acc, b, np.einsum("ij,ij->i", -dn, nor[b]))
    np.add.at(cnt, b, 1.0)
    cnt[cnt == 0] = 1.0
    k = acc / cnt

    for _ in range(CURV_SMOOTH if passes is None else passes):
        s = np.zeros(n)
        c = np.zeros(n)
        np.add.at(s, a, k[b])
        np.add.at(c, a, 1.0)
        np.add.at(s, b, k[a])
        np.add.at(c, b, 1.0)
        c[c == 0] = 1.0
        k = 0.5 * k + 0.5 * (s / c)
    return k, co


def w_adjacency(me, np):
    """CSR de vizinhanca de vertices, a partir das arestas da malha."""
    n = len(me.vertices)
    ei = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ei)
    ei = ei.reshape(-1, 2)
    src = np.concatenate([ei[:, 0], ei[:, 1]])
    dst = np.concatenate([ei[:, 1], ei[:, 0]])
    o = np.argsort(src, kind="stable")
    src, dst = src[o], dst[o]
    start = np.searchsorted(src, np.arange(n + 1))
    return start, dst


def w_limbs(me, np, co, H):
    """Acha VIRILHA e BRACOS pela CONEXAO da malha, nao por limiar de altura.

    Porque nao por altura: a primeira versao procurava o vao entre as pernas
    numa fatia horizontal e achou 0.81 da altura - o vao que ela viu era entre
    o BRACO e o tronco. Em A-pose nao existe altura em que a fatia contenha so
    as pernas: na altura da coxa a fatia tem duas coxas E duas maos.

    O que separa mao de coxa nao e distancia no espaco, e CONEXAO na superficie.
    Entao varre-se a malha de baixo para cima com union-find: cada minimo local
    abre uma componente e cada fusao e um evento. Anatomicamente os eventos
    grandes saem em ordem fixa - os dois pes sao os pontos mais baixos, as duas
    pernas se fundem na VIRILHA, e mais acima cada braco (que comeca na ponta
    dos dedos) se funde no tronco na AXILA.

    Devolve (crotch_z, leg_id, is_arm). leg_id: 0/1 por perna abaixo da
    virilha, -1 fora. is_arm cobre braco+mao ate a axila."""
    n = len(co)
    z = co[:, 2]
    start, dst = w_adjacency(me, np)

    order = np.argsort(z, kind="stable")
    rank = np.empty(n, dtype=np.int64)
    rank[order] = np.arange(n)

    parent = list(range(n))

    def find(x):
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r

    members = {}
    events = []                      # (z, membros_menores, membros_maiores)
    sig = max(200, int(0.015 * n))   # fusao "significativa"

    for v in order:
        v = int(v)
        parent[v] = v
        members[v] = [v]
        for j in range(start[v], start[v + 1]):
            u = int(dst[j])
            if rank[u] >= rank[v]:
                continue
            ra, rb = find(u), find(v)
            if ra == rb:
                continue
            ma, mb = members[ra], members[rb]
            if len(ma) < len(mb):
                ra, rb, ma, mb = rb, ra, mb, ma
            if len(mb) >= sig and len(ma) >= sig:
                events.append((float(z[v]), list(mb), list(ma)))
            parent[rb] = ra
            ma.extend(mb)
            del members[rb]

    leg_id = np.full(n, -1, dtype=np.int64)
    is_arm = np.zeros(n, dtype=bool)
    crotch_z = 0.45 * H

    if events:
        # 1o evento grande = virilha (os pes sao os pontos mais baixos da malha)
        cz, small, big = events[0]
        crotch_z = cz
        leg_id[np.array(small, dtype=np.int64)] = 0
        other = np.array(big, dtype=np.int64)
        leg_id[other[z[other] <= cz]] = 1
        # Eventos grandes seguintes cujo lado menor NAO encosta no chao = bracos.
        #
        # Varre TODOS os eventos, e nao events[1:3] como ate 01/08. A janela fixa
        # supoe que os dois bracos sao os dois proximos eventos grandes depois da
        # virilha, e no zen_f_b01_d1 um evento intruso entrou no meio: sobrou UM
        # braco na mascara (3700 vertices contra 5900-7100 nas vizinhas) e o outro
        # saiu pintado de preto inteiro, do deltoide ao pulso. A trava de ilha
        # pegou - e essa e a prova de que ela vale -, mas a mascara nao podia ter
        # deixado passar.
        #
        # O teto de 0.85 H existe para o caso oposto: se os dois bracos se fundirem
        # num evento so, o "segundo braco" que a varredura acharia seria o pescoco
        # ou o cabelo. Braco nenhum se funde no tronco tao alto.
        # A EXTENSAO minima tambem e nova, e pelo mesmo avatar: o primeiro evento
        # que ele oferecia depois da virilha era um blob de 489 vertices entre
        # zh 0.554 e 0.582 - a MAO encostada na coxa. Ele nao e braco, e gastava
        # uma das duas vagas. O que separa os dois nao e o TAMANHO (um braco do
        # b12_d1 tem 1340 vertices, menos que tres blobs desses) e sim o quanto
        # ele se estende na vertical: braco vai do pulso a axila, uns 0.34 da
        # altura; o blob tem 0.03.
        #
        # O QUARTO teste, o LATERAL, entrou em 01/08 e e ele que de fato separa
        # braco de blob - os outros tres so ordenavam. Medido nos 76
        # (qa/probe/sondas/_varre_braco.py, sobre o banco de eventos):
        #
        #   afastamento lateral   braco aceito   0.196 .. 0.339   (150 eventos)
        #   |x - centro| / H      recusado       0.009 .. 0.031   ( 14 eventos)
        #
        # Sao 6x de folga, contra 2x do `ext` (blob de 0.073 x braco de 0.147), e
        # a razao e anatomica: braco fica na lateral, e mao na coxa, pescoco e
        # cabelo ficam no meio. O `ext` era uma PROXY disso.
        #
        # Por isso o `ext` pode cair de 0.15 para 0.10 sem afrouxar nada: o filtro
        # passa a ter duas margens em vez de uma, e fica mais forte que antes. O
        # que ele custava era o zen_f_b12_d1 - em IMC 114 a mao funde na coxa
        # cedo, o componente do braco so comeca no antebraco e mede 0.1466 de
        # extensao, reprovando por 0.004. Os dois bracos saiam pintados de preto
        # do deltoide ao pulso, com a faixa atravessando os dois, e ele era o
        # unico dos 76 com arm_verts = 0.
        #
        # A trava de ilha nao pega esse caso: com os bracos colados no tronco, a
        # faixa errada continua sendo UMA peca conexa. Trava de ilha ve peca
        # partida, nao peca conectada no lugar errado.
        #
        # Conferido antes de mexer: com ext>=0.10 e lat>=0.10 a mascara dos outros
        # 75 sai IDENTICA a de hoje, e os 76 passam a achar os dois bracos. Mudar
        # so o b12_d1 era o criterio - 39 masculinos aprovados atravessam aqui.
        cx = np.median(co[:, 0])
        achados = []
        for ez, sm, _bg in events[1:]:
            sm = np.array(sm, dtype=np.int64)
            if (z[sm].min() > 0.20 * H and ez < 0.85 * H
                    and ez - z[sm].min() >= 0.10 * H
                    and np.median(np.abs(co[sm, 0] - cx)) >= 0.10 * H):
                achados.append(sm)
                if len(achados) == 2:
                    break
        for sm in achados:
            is_arm[sm] = True

        if len(achados) == 1:
            is_arm |= w_mirror_arm(np, co, H, achados[0])

    leg_id[is_arm] = -1
    return crotch_z, leg_id, is_arm


# Profundidade minima, em fracao da profundidade da fatia, para uma coluna
# depois do vao contar como TRONCO e nao como lasca de malha. As lascas existem
# e sao pequenas: no zen_f_b05_d1 aparece 0.013 no meio do vao, e no zen_f_b10_d1
# aparecem 0.010 e 0.012 dentro do peito. O tronco logo depois do vao mede 0.34 a
# 0.45 da profundidade da fatia nos casos medidos, entao 0.25 separa com folga.
ARM_VAO_TRONCO_FRAC = 0.25

# Quantas colunas vazias seguidas contam como VAO de verdade. Uma coluna solta
# pode ser buraco de decimacao; nos casos medidos o vao braco/tronco tem de 2 a 6
# colunas (2,8 a 8,4 cm) em toda fatia da banda da faixa.
ARM_VAO_MIN_COLS = 2


def _arm_cut_vao(perfil, fundo):
    """O corte pela TOPOLOGIA: o vao de ar entre o braco e o tronco.

    `perfil` e a lista [(b, profundidade|None)] de fora para dentro. Devolve o
    `b` da primeira coluna de TRONCO depois do vao, ou None se nao houver vao.

    ---------------------------------------------------------------------
    POR QUE ESTE CRITERIO, E POR QUE O DE PROFUNDIDADE COMIA TRONCO
    ---------------------------------------------------------------------
    O de profundidade pergunta "esta coluna ja tem 60% da profundidade da
    fatia?". Num corpo com busto a fatia e MUITO funda no meio, entao 60% dela e
    uma barra alta, e o flanco do tronco - que e raso porque o tronco afina de
    lado - nao a alcanca. Medido no zen_f_b10_d1, zh 0.680, lado esquerdo:

        0.329:0.054  0.315:0.087  [6 colunas VAZIAS]  0.231:0.120  0.217:0.097
          braco         braco            o vao          <- o tronco comeca aqui

    60% de 0.3557 e 0.2134, e a primeira coluna que chega la esta em 0.175. Com
    o ARM_COL_OUT o corte sai em 0.189, ou seja **4,2 cm dentro do tronco** - e
    e essa a mordida que ele viu na quina de baixo da faixa. Nao e limiar mal
    escolhido: a pergunta e que estava errada.

    O vao responde a pergunta certa, e e a mesma doutrina do resto do arquivo:
    o que separa braco de tronco e TOPOLOGIA, nao profundidade. Acima da fusao
    do w_limbs existe ar entre os dois em toda fatia da banda nos corpos
    medidos, e o ar e um sinal binario - nao tem limiar para calibrar errado.

    ⚠️ Varre de FORA para dentro e para no primeiro vao: assim o `b` devolvido e
    o do tronco, e tudo que estiver mais lateral que ele (braco + o proprio ar)
    fica marcado. Varrer do eixo para fora nao serve - no peito ha coluna vazia
    de verdade perto do esterno (zen_f_b10_d1 em zh 0.765), e a varredura pararia
    la."""
    n = len(perfil)
    i = 0
    while i < n and perfil[i][1] is None:      # nada antes do braco, mas guarda
        i += 1
    while i < n and perfil[i][1] is not None:  # o braco
        i += 1
    vazias = 0
    while i < n and perfil[i][1] is None:      # o vao
        vazias += 1
        i += 1
    if vazias < ARM_VAO_MIN_COLS or i >= n:
        return None
    while i < n:                               # a primeira coluna de TRONCO
        b, p = perfil[i]
        if p is not None and p >= ARM_VAO_TRONCO_FRAC * fundo:
            return b
        i += 1
    return None


def _arm_cut_prof(perfil, fundo, col_w):
    """O corte pela PROFUNDIDADE - hoje o plano B, quando nao ha vao.

    Era o unico criterio ate 15/08. Continua valendo onde o braco encosta mesmo
    no tronco e nao ha ar para achar: ali nao existe fronteira topologica e
    qualquer corte e escolha, entao a escolha antiga fica.

    PROF_FRAC acha "JA E TRONCO", nao "COMECA O TRONCO", e a diferenca entre as
    duas coisas e um fiapo branco: com 0.60 a coluna que passa no teste e a
    primeira SOLIDAMENTE funda, e as de fora dela ainda sao tronco, so que o
    tronco afina de lado e elas nao chegam a 60%. ARM_COL_OUT devolve esse
    deslocamento."""
    for b, p in perfil:
        if p is not None and p >= PROF_FRAC * fundo:
            return b + ARM_COL_OUT * col_w
    return None


def w_arm_wide(np, co, H, is_arm, lo_zh, hi_zh, diag=None):
    """O braco na ALTURA DA FAIXA, que a mascara topologica nao alcanca.

    O w_limbs devolve o braco ate onde ele FUNDE no tronco. Em corpo magro a
    fusao e a axila e fica acima da faixa, entao a mascara cobre tudo e o
    resultado sai limpo. Em corpo pesado a gordura do braco encosta na do tronco
    bem antes da axila anatomica - em 30 dos 37 femininos a fusao cai ABAIXO do
    topo da faixa -, e o pedaco de braco que sobra acima dela nao esta marcado.
    Como o campo da roupa so olha altura, a faixa sai pintada ATRAVESSANDO os
    dois bracos, com a borda serrilhada. Visto no b08_d1, no b10_d1 e no b12_d1;
    e defeito da colecao inteira, nao daquele avatar.

    Acima da fusao NAO EXISTE fronteira topologica: por cima o deltoide entra no
    trapezio numa superficie lisa, sem vinco nenhum. Qualquer mascara ali e
    ESCOLHA, nao deteccao - e por isso este corte e explicito e mora numa funcao
    so dele, em vez de virar mais um caso dentro do w_limbs.

    TRES CANDIDATOS FORAM MEDIDOS E DESCARTADOS, e cada um por um motivo que vale
    guardar (sondas em qa/probe/sondas/):

      _braco_lateral   union-find varrendo |x| de fora para dentro, esperando que
                       a superficie do braco virasse componente propria ate o
                       vinco. Nao vira: EM CORPO PESADO O TRONCO E MAIS LARGO QUE
                       O BRACO (b12_d1: peito a 0.245 da altura, braco a 0.180),
                       entao de fora para dentro quem aparece primeiro e o tronco.
      _braco_vinco     inundacao pela malha barrada em vertice concavo. Vaza ate
                       o alto da cabeca em limiar frouxo e nao corta nada em
                       limiar apertado, porque a cerca do vinco e ABERTA em cima.
      ajuste de elipse no anel: a meia-largura lateral do tronco e justamente o
                       que o braco ocluta, entao ela nao esta no sinal.

    O QUE FUNCIONA e a PROFUNDIDADE. O braco e um tubo raso e o tronco e fundo, e
    varrendo x de fora para dentro o degrau entre os dois e limpo:

      b10_d1 zh 0.72   braco 0.055 0.081 0.087 0.087 | tronco 0.142 .. 0.201
      b12_d1 zh 0.72   braco 0.066 0.126 0.145 0.151 | tronco 0.218 .. 0.280
      b01_d1 zh 0.72   braco 0.034 0.040 0.040 0.019 | tronco 0.075 .. 0.122

    O corte e a primeira coluna que passa de PROF_FRAC da profundidade maxima da
    fatia - fracao, e nao valor absoluto, porque a escala muda 3x entre um IMC 18
    e um IMC 114. Conferido a mao em 6 secoes de 3 corpos e acerta nas 6,
    inclusive no magro, onde a coluna do meio le 0.000 (ha vao de verdade).

    Roda so na FAIXA. Fora dela nao ha razao para cortar largura - o short mora
    no quadril, onde nao ha braco -, e restringir assim e o que garante que
    avatar sem faixa (os 39 masculinos) nao muda um vertice.

    E roda so ACIMA DA FUSAO, que e a segunda metade da mesma ideia. Abaixo dela
    o w_limbs mediu o braco de verdade, pela topologia, e essa medida e melhor
    que qualquer corte por profundidade; acima nao ha o que medir. A primeira
    versao ignorava isso e rodava na banda inteira - o zen_f_b01_d1, que e magro
    e cuja fusao (0.7588) ja fica ACIMA do topo da faixa (0.756), voltou com a
    borda de baixo serrilhada: nao faltava nada nele e o corte so comeu tronco.
    Nos magros a funcao agora nao processa fatia nenhuma, que e o certo.

    ------------------------------------------------------------------------
    O CORTE E ALISADO ENTRE FATIAS (11/08, sessao 26)
    ------------------------------------------------------------------------
    A primeira versao decidia cada fatia de 0.005 SOZINHA, e a fronteira
    braco/tronco nao e uma decisao independente 20 vezes seguidas: e uma linha.
    Perto da axila o braco afina e o degrau de profundidade fica raso, entao uma
    fatia isolada acha o degrau um passo mais para DENTRO e come tronco - e o que
    sai no render e um dente branco no meio da faixa, do tamanho de uma fatia.
    Era esse o defeito visivel no b09_d2 e no b10_d2, os dois com a ALTURA do topo
    certa contra a folha (+0.003 e +0.001): nao era a borda de cima, era aqui.

    A correcao e mediana movel de 5 fatias sobre o proprio corte, por lado. Ela
    so mexe em fatia que JA cortava: onde o corte nao existia (ou caiu perto do
    eixo) continua nao existindo, porque marcar por interpolacao inventaria braco
    onde a profundidade nao viu nenhum - e o comentario de SEGURANCA abaixo vale
    inteiro, pelo mesmo motivo de sempre. E a mesma familia da mediana circular
    do w_waist_curve, num eixo diferente: la nenhum setor destoa dos vizinhos,
    aqui nenhuma fatia."""
    z = co[:, 2]
    zh = (z - z.min()) / H
    cx = np.median(co[:, 0])
    out = np.zeros(len(co), dtype=bool)
    passo = 0.005
    if is_arm.any():
        lo_zh = max(lo_zh, float(zh[is_arm].max()))
    ks = list(range(int(np.floor(lo_zh / passo)),
                    int(np.ceil(hi_zh / passo)) + 1))

    # PASSADA 1 - o corte cru de cada fatia, sem marcar nada ainda.
    fatias, cortes = {}, {-1.0: [], 1.0: []}
    fontes = {-1.0: [], 1.0: []}
    for k in ks:
        fatia = np.where((zh >= k * passo) & (zh < (k + 1) * passo))[0]
        fatias[k] = fatia
        y = co[fatia, 1] if len(fatia) else None
        fundo = (y.max() - y.min()) if y is not None and len(y) else 0.0
        x = co[fatia, 0] - cx if len(fatia) else None
        for sinal in (-1.0, 1.0):
            corte = None
            fonte = "-"
            if len(fatia) >= 40 and fundo > 0:
                lado = np.where(np.sign(x) == sinal)[0]
                if len(lado) >= 20:
                    xl = x[lado] * sinal                   # sempre positivo
                    # perfil de profundidade coluna a coluna, de FORA para
                    # dentro. None = coluna sem malha (menos de 3 vertices).
                    perfil = []
                    for b in np.arange(xl.max(), 0.0, -COL_W * H):
                        col = (xl <= b) & (xl > b - COL_W * H)
                        if col.sum() < 3:
                            perfil.append((float(b), None))
                            continue
                        yc = y[lado][col]
                        perfil.append((float(b), float(yc.max() - yc.min())))

                    corte = _arm_cut_vao(perfil, fundo)
                    fonte = "vao"
                    if corte is None:
                        corte = _arm_cut_prof(perfil, fundo, COL_W * H)
                        fonte = "prof" if corte is not None else "-"
                    # SEGURANCA: se o corte cair perto do eixo, quem foi achado
                    # nao era o vinco e marcar aquilo comeria metade do tronco.
                    # Melhor nao marcar nada - a faixa atravessando o braco e
                    # feio, faixa com buraco no meio do peito e outra categoria
                    # de erro.
                    if corte is not None and corte < 0.35 * xl.max():
                        corte, fonte = None, "-"
            cortes[sinal].append(corte)
            fontes[sinal].append(fonte)

    # PASSADA 2 - mediana movel de 5 (tira o disparo) e AJUSTE (tira a escada).
    #
    # Sao dois filtros porque sao dois defeitos, e o mesmo argumento do
    # w_waist_liso: mediana e filtro de POSTO, e o filtro certo contra a fatia
    # que disparou (o vao acha buraco de decimacao dentro do tronco e devolve
    # 0.129 onde as vizinhas dao 0.22) - mas ela PRESERVA degrau, entao o que
    # sobra dela ainda zigue-zagueia meio centimetro de fatia para fatia. Numa
    # banda de 9 cm de altura isso e a ESCADA que ele viu na quina da faixa.
    #
    # A fronteira braco/tronco ao longo de 9 cm de altura e uma linha suave: uma
    # PARABOLA em zh, por minimos quadrados, tem forma de sobra para o que o
    # corpo faz ali e nao tem grau de liberdade para serrilhar. Grau 2 e nao 1
    # porque perto do deltoide a fronteira volta para dentro.
    #
    # ⚠️ O ajuste so e avaliado onde JA HAVIA corte. Preencher os None por
    # extrapolacao inventaria braco onde a varredura nao viu nenhum, que e o
    # comentario de SEGURANCA de sempre - e no magro, onde quase nao ha fatia
    # com corte, o `< 4 pontos` devolve a mediana e nada muda.
    raio = 2
    suave = {}
    for sinal in (-1.0, 1.0):
        c = cortes[sinal]
        s = []
        for i, v in enumerate(c):
            if v is None:
                s.append(None)
                continue
            viz = [c[j] for j in range(max(0, i - raio), min(len(c), i + raio + 1))
                   if c[j] is not None]
            s.append(float(np.median(viz)))
        idx = [i for i, v in enumerate(s) if v is not None]
        if ARM_AJUSTE_GRAU and len(idx) >= 4:
            zz = np.array([ks[i] * passo for i in idx], dtype=np.float64)
            vv = np.array([s[i] for i in idx], dtype=np.float64)
            grau = ARM_AJUSTE_GRAU if len(idx) >= 6 else 1
            aj = np.polyval(np.polyfit(zz - zz.mean(), vv, grau), zz - zz.mean())
            for i, v in zip(idx, aj):
                s[i] = float(v)
        suave[sinal] = s

    # PASSADA 3 - marca com o corte alisado.
    for i, k in enumerate(ks):
        fatia = fatias[k]
        if not len(fatia):
            continue
        x = co[fatia, 0] - cx
        for sinal in (-1.0, 1.0):
            corte = suave[sinal][i]
            if corte is None:
                continue
            lado = np.where(np.sign(x) == sinal)[0]
            if not len(lado):
                continue
            xl = x[lado] * sinal
            out[fatia[lado[xl > corte]]] = True

    if diag is not None:
        diag["passo"] = passo
        diag["zh"] = [k * passo for k in ks]
        diag["cru"] = {s: list(cortes[s]) for s in cortes}
        diag["suave"] = {s: list(suave[s]) for s in suave}
        diag["fonte"] = {s: list(fontes[s]) for s in fontes}
        diag["meia_largura"] = []
        for k in ks:
            f = fatias[k]
            xx = np.abs(co[f, 0] - cx) if len(f) else None
            diag["meia_largura"].append(float(xx.max()) if xx is not None
                                        and len(xx) else 0.0)
    return out & ~is_arm


def w_mirror_arm(np, co, H, sm):
    """O OUTRO braco, quando a malha nao o oferece como evento.

    No zen_f_b01_d1 a mao esquerda encosta na coxa, entao aquele braco ja esta
    fundido ao tronco quando a varredura chega nele: ele nunca vira evento, e o
    union-find nao tem como o achar - nao e limiar mal escolhido, e informacao
    que nao existe naquele sinal. O resultado foi um braco preto do deltoide ao
    pulso no --render.

    O que existe e SIMETRIA: a folha e desenhada simetrica e a Meshy a respeita
    de perto. Entao o braco achado vira MOLDE do que falta - espelha-se em x e
    marca-se quem cair perto. Se o espelho render menos de metade do molde, a
    simetria nao valia para este corpo e nao se marca nada: a trava de ilha
    denuncia depois, que e melhor do que pintar por adivinhacao."""
    from mathutils import Vector
    from mathutils.kdtree import KDTree

    out = np.zeros(len(co), dtype=bool)
    lado = 1.0 if co[sm, 0].mean() > 0 else -1.0
    zlo, zhi = co[sm, 2].min(), co[sm, 2].max()

    kd = KDTree(len(sm))
    for i, v in enumerate(sm):
        kd.insert(Vector(co[v]), i)
    kd.balance()

    tol = 0.02 * H
    cand = np.where((np.sign(co[:, 0]) == -lado) &
                    (co[:, 2] >= zlo - tol) & (co[:, 2] <= zhi + tol))[0]
    achou = []
    for v in cand:
        p = Vector((-co[v, 0], co[v, 1], co[v, 2]))
        _co, _idx, d = kd.find(p)
        if d is not None and d < tol:
            achou.append(v)

    if len(achou) < 0.5 * len(sm):
        return out
    out[np.array(achou, dtype=np.int64)] = True
    return out


def w_back_side_mask(np, az_bins):
    """Setores de azimute que NAO sao a frente do corpo.

    A frente e o unico lugar onde a barriga pode cobrir o cos; nas costas e nos
    lados o elastico esta sempre a vista. Entao a ALTURA do anel se decide so
    aqui, e a frente fica livre para descer ate a prega depois. Sem isso, num
    corpo obeso a prega da barriga (que e o vinco mais forte do tronco) puxava
    o anel inteiro para baixo e o short saia como uma tira fina.

    Convencao do pipeline: a frente do avatar aponta para -Y, ou seja
    atan2(y,x) = -pi/2, que cai no setor az_bins/4."""
    front = az_bins // 4
    half = max(1, az_bins // 6)
    m = np.ones(az_bins, dtype=bool)
    for d in range(-half, half + 1):
        m[(front + d) % az_bins] = False
    return m


def w_ring_map(np, co, kn, sel, H, center_mode, az_bins=AZ_BINS, az_mask=None):
    """Mapa (azimute x altura) da concavidade MAXIMA, e o perfil de anel.

    O perfil e o QUANTIL BAIXO da concavidade sobre os setores de azimute -
    nao a media, e nao a fracao acima de um limiar.

    E essa escolha que separa bainha de musculo. Um gomo abdominal e fundo mas
    so existe na frente: uns 6 dos 16 setores. Um sulco de quadriceps idem. A
    bainha e rasa, porem esta em TODOS os setores, porque da a volta no membro.
    Media e fracao-acima-de-limiar premiam profundidade e deixam o gomo ganhar;
    quantil baixo pergunta "o setor MAIS FRACO desta altura ainda esta vincado?",
    que e a definicao de anel fechado. Foi a troca que fez o cos parar de pousar
    no abdomen.

    center_mode: 'slice' mede o azimute em volta do centroide da propria fatia
    (uma perna nao esta no eixo do corpo); 'axis' mede em volta do eixo; uma
    tupla (cx, cy) fixa o centro - preciso quando a curva resultante vai ser
    REAVALIADA depois em w_field, que nao tem os centroides por fatia."""
    import math
    A = np.zeros((az_bins, Z_BINS))
    # occ marca a celula que TEM vertice. Sem isso nao da para distinguir
    # "superficie lisa aqui" de "nao ha superficie aqui" - as duas dao zero em A.
    occ = np.zeros((az_bins, Z_BINS), dtype=bool)
    if sel.size < 50:
        return A, np.zeros(Z_BINS), occ
    zb = np.clip((co[sel, 2] / H * Z_BINS).astype(np.int64), 0, Z_BINS - 1)
    for b in np.unique(zb):
        g = sel[zb == b]
        if g.size < 10:
            continue
        if center_mode == "slice":
            cx, cy = co[g, 0].mean(), co[g, 1].mean()
        elif center_mode == "axis":
            cx, cy = 0.0, 0.0
        else:
            cx, cy = center_mode
        az = np.arctan2(co[g, 1] - cy, co[g, 0] - cx)
        ab = np.clip(((az + math.pi) / (2 * math.pi) * az_bins).astype(np.int64),
                     0, az_bins - 1)
        np.maximum.at(A[:, b], ab, kn[g])
        occ[ab, b] = True

    ring = np.quantile(A if az_mask is None else A[az_mask], RING_QUANTILE, axis=0)
    for _ in range(RING_SMOOTH):
        ring = np.convolve(ring, np.array([0.25, 0.5, 0.25]), mode="same")
    return A, ring, occ


def w_fill_holes(np, A, occ, raio_az=1, raio_z=2):
    """Preenche as celulas VAZIAS do mapa (azimute x altura) com a media das
    vizinhas ocupadas.

    ---------------------------------------------------------------------
    ISTO E O QUE CEGAVA O DETECTOR NA FRENTE DOS CORPOS PESADOS
    ---------------------------------------------------------------------
    24 setores x 240 fatias sao 5760 celulas para ~30k vertices, e os vertices
    nao se distribuem por igual - cabeca, maos e pes levam a maior parte. No
    trecho do cos do b12_d1 medimos **32% de ocupacao**: dois tercos das celulas
    do mapa nao tinham vertice nenhum.

    O efeito disso nao e ruido, e um vies com cara de verdade: uma celula vazia
    vale ZERO, ou seja "aqui a superficie e lisa", que e indistinguivel de "aqui
    nao ha superficie". Um argmax lendo esse mapa acha vinco onde calhou de cair
    um vertice, e le prega funda como regiao sem sinal. Foi por isso que uma
    sonda anterior concluiu que "a prega da barriga nao tem sinal na malha" - o
    render de emissao pura mostrou o contrario, a faixa de concavidade esta la.

    Media normalizada pela OCUPACAO, e nao dilatacao por maximo: dilatar espalha
    o pico de um vinco para as celulas vizinhas e inventa vinco onde nao ha
    (a primeira tentativa fez isso e criou um plato de 1.00 em 4 setores).
    Ocupacao 100% devolve o mapa inalterado, entao onde o mapa ja e denso nada
    muda - o que mantem os avatares magros exatamente como estavam."""
    A = np.asarray(A, dtype=np.float64)
    occ = np.asarray(occ, dtype=np.float64)
    num = np.zeros_like(A)
    den = np.zeros_like(A)
    for dz in range(-raio_z, raio_z + 1):
        Az = np.roll(A * occ, dz, axis=1)
        Oz = np.roll(occ, dz, axis=1)
        for da in range(-raio_az, raio_az + 1):
            num += np.roll(Az, da, axis=0)
            den += np.roll(Oz, da, axis=0)
    media = np.where(den > 0, num / np.maximum(den, 1e-9), 0.0)
    return np.where(occ > 0, A, media)


def w_peaks(np, ring, lo_b, hi_b, floor=0.0):
    out = []
    for b in range(max(int(lo_b), 1), min(int(hi_b), Z_BINS - 1)):
        if ring[b] >= ring[b - 1] and ring[b] >= ring[b + 1] and ring[b] > floor:
            out.append((float(ring[b]), b))
    out.sort(reverse=True)
    return out


def w_pico_prior(np, ring, lo_zh, hi_zh, centro_zh, sigma_zh, smin=0.0):
    """Pico do anel pesado por um PRIOR, e nunca um pico de forca zero.

    O argmax puro pega o vinco mais FUNDO da janela, que nem sempre e a borda da
    peca: nos IMC 30-54 ele pousava num sulco 0.03 acima do inframamario. E o
    w_peaks, sem piso, devolve tambem maximos de forca 0.000 - numero que ninguem
    consegue distinguir de uma medida, e foi assim que o b04_d2 ganhou base 0.702
    contra 0.667 da folha.

    Devolve (bin, score, picos) com bin=None quando nao ha pico que preste."""
    pk = [(s, b) for s, b in w_peaks(np, ring, lo_zh * Z_BINS, hi_zh * Z_BINS)
          if s >= smin][:12]
    lista = [[round(s, 3), round((b + 0.5) / Z_BINS, 4)] for s, b in pk[:3]]
    if not pk:
        return None, 0.0, lista
    c, sg = centro_zh * Z_BINS, max(sigma_zh * Z_BINS, 1e-6)
    s, b = max(pk, key=lambda sb: sb[0] * np.exp(-0.5 * ((sb[1] - c) / sg) ** 2))
    return b, s, lista


def w_interp_circ(np, vals, az):
    """Interpola circularmente uma curva dada por setor de azimute."""
    import math
    v = np.asarray(vals, dtype=np.float64)
    n = v.size
    if n == 1:
        return np.full(np.shape(az), float(v[0]))
    t = (az + math.pi) / (2 * math.pi) * n - 0.5
    i0 = np.floor(t).astype(np.int64)
    f = t - i0
    return v[i0 % n] * (1 - f) + v[(i0 + 1) % n] * f


def w_resample_circ(np, vals, n_out):
    import math
    az = (np.arange(n_out) + 0.5) / n_out * 2 * math.pi - math.pi
    return w_interp_circ(np, vals, az)


def w_waist_curve(np, A, center_b, floor_b, az_bins, front_mask):
    """A curva do cos: por setor de azimute, a altura de concavidade maxima
    dentro de uma janela ASSIMETRICA em volta do anel, com prior gaussiano e
    mediana circular.

    ---------------------------------------------------------------------
    O QUE MUDOU NA SESSAO 5, E O QUE FOI TENTADO E DESCARTADO
    ---------------------------------------------------------------------
    A estrutura (prior + mediana) e a da sessao 4 e sobreviveu; o que mudou foi
    a JANELA, que era simetrica e larga nos 24 setores, e o MAPA, que era lido
    com dois tercos das celulas vazias. As duas mudancas foram medidas contra a
    folha nos 39 (qa/probe/bench.py):

        sessao 4  - simetrica 0.10, sem preencher   10 fora   rms 0.0475
        agora     - assimetrica, preenchida          8 fora   rms 0.0391

    **TENTATIVA DESCARTADA 1 - janela funda.** A folha mostra que no b12_d1 o
    cos desce 0.184 abaixo do anel, entao parecia obvio abrir a janela para
    0.16 ou 0.22 e deixar o argmax alcancar a prega. Medido: piorou MUITO,
    para 19 e 24 fora. Janela funda nao acha prega funda - acha ruido fundo,
    porque nos corpos em que nao ha prega ela da espaco para o argmax cair em
    qualquer coisa. O otimo medido e 0.12.

    **TENTATIVA DESCARTADA 2 - programacao dinamica.** Trocar prior por custo de
    degrau entre setores vizinhos era teoricamente mais bonito: deixaria a prega
    passar quando COERENTE e barraria a linha alba, sem punir distancia. Foi
    implementada e testada. Um unico lambda nao serve a serie inteira: com o
    valor que deixa o b11_d2 descer, o b08_d1 sobe para +0.061; com o que segura
    o b08_d1, o b12_d1 nao sai do lugar. Reprovada por medida, nao por gosto.

    As duas travas herdadas continuam valendo pelos motivos originais:

    1. PRIOR GAUSSIANO. O argmax puro e indefeso contra sulco VERTICAL: a linha
       alba desce pelo meio da barriga e esta forte em toda a janela, entao nos
       setores da frente o argmax pousava em qualquer altura e saia um V no meio
       do cos. O prior diz "sem razao forte, fique na altura do anel".
    2. MEDIANA CIRCULAR. Nenhum setor isolado destoa dos vizinhos. Passou de 5
       para 7 termos: com 5 um plato de 4 setores atravessa inteiro, e foi assim
       que a aba retangular dos d3 passou batida na sessao 4.

    3. JANELA ASSIMETRICA (nova). A frente desce e NAO sobe; costas e lados quase
       nao se mexem. Ver WAIST_WINDOW_* - e o modelo que o docstring de
       w_back_side_mask ja declarava e que o codigo nao aplicava."""
    out = []
    for j in range(az_bins):
        if front_mask[j]:
            lo_f = center_b - WAIST_WINDOW_FRONT_DOWN * Z_BINS
            hi_f = center_b + WAIST_WINDOW_FRONT_UP * Z_BINS
        else:
            lo_f = center_b - WAIST_WINDOW_BACK_ZH * Z_BINS
            hi_f = center_b + WAIST_WINDOW_BACK_ZH * Z_BINS
        # o cos nunca desce abaixo da bainha: ali o short acabaria antes de comecar
        lo = int(max(0, floor_b + 1, round(lo_f)))
        hi = int(min(Z_BINS - 1, round(hi_f)))
        if hi < lo:
            out.append(center_b)
            continue
        zz = np.arange(lo, hi + 1, dtype=np.float64)
        sigma = max((center_b - lo) * WAIST_PRIOR_SIGMA, 1.0)
        w = A[j, lo:hi + 1] * np.exp(-0.5 * ((zz - center_b) / sigma) ** 2)
        out.append(lo + int(w.argmax()) if w.size and w.max() > 0 else center_b)

    k = WAIST_MEDIAN // 2
    return [int(sorted([out[(j + d) % az_bins] for d in range(-k, k + 1)])[k])
            for j in range(az_bins)]


def w_cos_avental(np, co, nor, is_arm, H, crotch_zh, hem_zh, waist_zh, az_bins):
    """Desce o cos da FRENTE ate o fundo da dobra do avental.

    Devolve a curva com `min(cos, dobra)` nos setores da frente e o cos
    inalterado no resto. Ver COS_AVENTAL_NZ para o criterio e para as duas
    hipoteses que morreram antes desta.
    """
    import math
    z = co[:, 2] / H
    az = np.arctan2(co[:, 1], co[:, 0])
    ab = np.clip(((az + math.pi) / (2 * math.pi) * az_bins).astype(np.int64),
                 0, az_bins - 1)
    # A regiao e MAIS LARGA que a mascara frontal do cos: o avental nao acaba em
    # +-60 graus, ele sobe de volta indo para o flanco. Cortando em 60 o setor
    # vizinho fica 10 cm acima e a curva vira um DEGRAU - o short saiu com um
    # recorte retangular no b11_d1, visivel na hora. Ate +-105 graus a dobra
    # ainda e barriga; de 105 para tras comeca o sulco gluteo, que e short.
    frente = np.zeros(az_bins, dtype=bool)
    meio = az_bins // 4
    for d in range(-COS_AVENTAL_SETORES, COS_AVENTAL_SETORES + 1):
        frente[(meio + d) % az_bins] = True
    piso = max(crotch_zh + COS_AVENTAL_PISO, hem_zh + 0.02)
    passo = 0.008
    out = list(waist_zh)
    for j in range(az_bins):
        if not frente[j]:
            continue
        c = waist_zh[j]
        sel = (ab == j) & (~is_arm)
        achou = None
        for zz in np.arange(c + 0.02, piso, -passo):
            m = sel & (z >= zz) & (z < zz + passo)
            if m.sum() < 3:
                continue
            if float(np.median(nor[m, 2])) <= COS_AVENTAL_NZ:
                achou = float(zz)      # continua descendo: quer o MAIS BAIXO
        if achou is not None:
            out[j] = min(c, achou)
    # mediana circular de 3 DENTRO da frente: o detector decide setor a setor e
    # um setor solto vira degrau. As bordas do bloco frontal ficam intactas, que
    # e onde a curva encontra o lado - e onde alisar inventaria transicao.
    idx = [j for j in range(az_bins) if frente[j]]
    if len(idx) >= 3:
        suave = list(out)
        for k in range(1, len(idx) - 1):
            j = idx[k]
            suave[j] = float(sorted([out[idx[k - 1]], out[j], out[idx[k + 1]]])[1])
        out = suave

    # TRAVA DE DEGRAU, a mesma que o --report ja cobra (WAIST_STEP_MAX_ZH). A
    # descida do avental chega a 10 cm; despejada em um setor ela e uma parede.
    # Aqui ela so pode SUBIR o que a dobra baixou - o teto de cada setor e o
    # vizinho mais o passo -, entao a trava espalha a descida por varios setores
    # em vez de recusa-la, e nenhum setor fora da regiao e tocado.
    # ⚠️ Testada tambem uma versao SIMETRICA (puxava setor "imune" - achou=None
    # - para baixo na direcao de vizinho fundo, nao so o inverso). Piorou: no
    # zen_m_b11_d1, que esta secao ja tinha deixado limpo, a correcao cascateou
    # fundo demais e a bainha parou de ser detectada (BAINHA-CHUTE novo) junto
    # com um DEGRAU novo. Revertida no mesmo dia. So o piso (abaixo) sobrevive.
    for _ in range(az_bins):
        mudou = False
        for j in range(az_bins):
            if not frente[j] or out[j] >= waist_zh[j]:
                continue
            piso_viz = max(out[(j - 1) % az_bins],
                           out[(j + 1) % az_bins]) - COS_AVENTAL_STEP_MAX_ZH
            if out[j] < piso_viz - 1e-9:
                out[j] = min(waist_zh[j], piso_viz)
                mudou = True
        if not mudou:
            break
    return [float(v) for v in out]


def w_waist_liso(np, waist_zh, floor_zh):
    """Alisa a curva do cos: elastico nao tem QUINA.

    Entra a curva medida (24 setores, ja com o avental aplicado se houver), sai
    a mesma curva sem os vincos que o Rogerio apontou nos 7 prints de 15/08.

    ---------------------------------------------------------------------
    POR QUE O ALISAMENTO NAO ESTAVA AQUI, E POR QUE A MEDIANA NAO BASTA
    ---------------------------------------------------------------------
    O w_waist_curve ja alisa - com MEDIANA CIRCULAR de 7. Mediana e o filtro
    certo contra o defeito que ela foi escrever: um setor solto que disparou.
    Mas mediana e um filtro de POSTO, nao de media: ela preserva degrau e
    preserva plato por construcao, que e exatamente a virtude dela em outro
    contexto. O b11_d1 saiu com 0.615 em cinco setores do flanco e 0.523 no
    vizinho - 16 cm de parede vertical, e a mediana de 7 nao tem como derruba-la
    porque os dois lados sao platos largos. A DEGRAU tambem nao viu, porque
    DEGRAU e um relatorio e nao um enforcador.

    ---------------------------------------------------------------------
    O TETO E O QUE IMPEDE ISTO DE VIRAR A REGRESSAO DA 4.5e
    ---------------------------------------------------------------------
    Alisar SOBE o fundo da dobra, e subir o cos num corpo com avental e
    literalmente o defeito que a 4.5e consertou: pinta a barriga de preto. Sem
    teto, o alisamento gaussiano levantava o fundo do b11_d1 em 0.027 - uns 4,7
    cm de pele dentro do tecido.

    Entao o alisamento so tem licenca para subir DOIS BINS de Z_BINS acima da
    medida. O numero nao e gosto: e a resolucao da propria medida (1/240 da
    altura, 0.73 cm). Alisar dentro da resolucao e limpar quantizacao; alisar
    alem dela e contradizer o que se mediu.

    ⚠️ E "a medida" aqui e a MEDIANA DE 3 de w0, nao w0 - ver o comentario no
    corpo da funcao. Foi a diferenca entre entregar a borda lisa e entregar um
    bico no meio da barriga.

    O laco alterna alisar e re-aplicar o teto, que e o jeito de fazer a correcao
    se espalhar pelos VIZINHOS em vez de cortar um bico: quem nao pode subir
    puxa quem esta em volta para baixo.

    Medido nos 7 da lista dele: curvatura de 0.020..0.092 para 0.007..0.015, com
    o cos descendo no maximo 0.016 nos 5 mais leves (0.067 no b11_d1, que e a
    parede do flanco voltando para a altura do anel, onde ela deveria estar).

    ---------------------------------------------------------------------
    ❌ O QUE FOI MEDIDO E DESCARTADO ANTES DESTA VERSAO
    ---------------------------------------------------------------------
    - LIMITADOR DE INCLINACAO puro (clipar cada setor contra os vizinhos ±passo).
      Conserta o degrau e NAO conserta a quina: a saida e uma rampa reta ligada
      a um plato reto, que e um vinco igual ao que se queria tirar. Medido nos 8:
      passo cai para 0.012 e a curvatura fica em 0.010-0.017, contra 0.006-0.013
      daqui.
    - TRUNCAR HARMONICOS (K=4..6, com janela de Hann). Alisa mais que tudo
      (curvatura 0.003-0.009) mas SEM teto sobe o fundo da dobra em ate 0.035,
      e com teto o corte de banda ressoa e devolve ondulacao onde nao havia.
    - ALISAR SO A FRENTE. A parede do b11_d1 esta no FLANCO (setor 0 contra 1),
      que e borda da mascara frontal; alisar so a frente e nao tocar nela."""
    w0 = np.asarray(waist_zh, dtype=np.float64)
    n = w0.size
    if n < 4:
        return [float(v) for v in w0]

    d = np.arange(n)
    d = np.minimum(d, n - d)
    k = np.exp(-0.5 * (d / WAIST_LISO_SIGMA) ** 2)
    k /= k.sum()
    K = np.fft.fft(k)

    # 🔴 O TETO NAO E `w0`, E A MEDIANA DE 3 DE `w0` - e essa linha custou um
    # render inteiro do zen_f_b12_d1. Com o teto colado em w0, sobrava um V
    # anguloso no centro da frente dos dois mais pesados, e ele APARECIA no GLB
    # entregue: um bico no meio da barriga, feio de um jeito diferente do
    # defeito original mas igualmente visivel.
    #
    # A causa nao e o alisamento, e o que ele estava sendo obrigado a respeitar.
    # Medida a dobra sem a trava de degrau (COS_AVENTAL_STEP_MAX_ZH = 9), o
    # fundo do avental do b12_d1 e um PLATO: setores 4..7 em 0.459 0.456 0.456
    # 0.460, com penhasco de 0.066 nos dois lados. A rampa de 0.020 por setor
    # nao alcanca esse fundo, entao ela desenha um TRIANGULO - 0.503 0.483
    # 0.500 - cujo vertice e o proprio teto da rampa, e nao uma medida. Um
    # setor isolado mais fundo que os dois vizinhos nao e dobra estreita: e
    # geometria da trava. Fora o vertice, os vizinhos ja pintam 8 cm de pele
    # sobre a mesma dobra, entao subir o vertice ate a altura deles nao pinta
    # nada de novo - so tira a inconsistencia.
    #
    # E o mesmo argumento da mediana circular que este arquivo ja usa duas
    # vezes: nenhum setor isolado tem autoridade sobre os vizinhos.
    med = np.array([sorted([w0[(j - 1) % n], w0[j], w0[(j + 1) % n]])[1]
                    for j in range(n)])
    teto = med + WAIST_LISO_TETO_BINS / Z_BINS
    s = w0.copy()
    for _ in range(WAIST_LISO_ITERS):
        s = np.real(np.fft.ifft(np.fft.fft(s) * K))
        s = np.minimum(s, teto)
    # o cos nunca desce abaixo da bainha - a mesma guarda do w_waist_curve, aqui
    # de novo porque o alisamento e a ultima coisa que toca a curva.
    s = np.maximum(s, floor_zh)
    return [float(v) for v in s]


def w_faixa(np, co, kn, H, is_arm, crotch, base_override=None, topo_reto=False,
            topo_frente_zh=None):
    """A FAIXA do peito: base ESCALAR e topo CURVO por azimute.

    A assimetria entre as duas bordas nao e estetica, e medida na folha nas duas
    vistas: a borda de baixo passa sob o busto e fica na mesma altura na frente e
    nas costas (delta +0.015 em media, dentro do ruido da propria medida),
    enquanto a de cima passa POR CIMA do busto e sobe +0.031 a +0.060. Ver
    FAIXA_TOPO_UP_FRONT.

    O sinal e o mesmo ring_score do resto do arquivo: a borda de baixo cai no
    sulco inframamario e e o pico mais forte do torax em quase toda a serie.
    Devolve (base_zh, topo_por_setor_zh, diagnostico)."""
    z = co[:, 2]
    tronco = np.where((~is_arm) & (z >= crotch))[0]
    back_side = w_back_side_mask(np, WAIST_AZ_BINS)
    A, ring, occ = w_ring_map(np, co, kn, tronco, H, "axis", WAIST_AZ_BINS)
    _A2, ring_bs, _o2 = w_ring_map(np, co, kn, tronco, H, "axis", WAIST_AZ_BINS,
                                   az_mask=back_side)

    # A BASE e a unica deteccao de verdade. O chute, quando ela falha, e a
    # MEDIANA da folha e nao o meio da janela (LICOES.md 4.3 - chute que nao se
    # anuncia foi o defeito da bainha, entao ele se anuncia no diag).
    base_b, _sb, pk_b = w_pico_prior(np, ring, FAIXA_BASE_RANGE[0],
                                     FAIXA_BASE_RANGE[1], FAIXA_BASE_MEDIANA,
                                     FAIXA_BASE_SIGMA, FAIXA_PICO_MIN)
    chute_b = base_b is None
    if chute_b:
        base_b = int(FAIXA_BASE_MEDIANA * Z_BINS)

    # ANCORA DA FAIXA corrigida a mao. Terceiro da familia do crotch_override_zh
    # e do waist_ring_override_zh, e pelo mesmo motivo: a base e a ancora da
    # peca INTEIRA - o topo e o proprio contorno saem dela -, entao um numero so
    # conserta tudo. O que NAO serve e editar faixa_lo_zh e faixa_hi_zh no mapa
    # a mao: aquilo fossiliza uma curva que foi tracada a partir da ancora
    # errada, e no b04_d3 essa curva e justamente a que desabou (FRENTEv9).
    # Aqui a curva e RETRACADA a partir da ancora nova.
    manual = base_override is not None
    if manual:
        base_b = int(round(base_override * Z_BINS - 0.5))

    # O TOPO NAO E UMA SEGUNDA MEDIDA: e a base mais a ALTURA DA PECA. A folha
    # da 0.0504 +- 0.0037 nas 37 - a faixa e a mesma roupa em todo mundo - contra
    # base 0.6712 +- 0.0080, que varia com o corpo. Havia UMA incognita e o
    # detector procurava duas, e a segunda era a de sinal fraco: o topo errava
    # ate 0.034 e chutava em cinco. Ancorado, o anel das costas so tem licenca de
    # +-FAIXA_ALTURA_TOL para corrigir, e o erro cai para 0.0075 medio.
    alvo = (base_b + 0.5) / Z_BINS + FAIXA_ALTURA_ZH
    topo_b, _st, pk_t = w_pico_prior(np, ring_bs, alvo - FAIXA_ALTURA_TOL,
                                     alvo + FAIXA_ALTURA_TOL, alvo,
                                     FAIXA_ALTURA_TOL, FAIXA_PICO_MIN)
    chute_t = topo_b is None
    if chute_t:
        topo_b = int(round(alvo * Z_BINS - 0.5))

    # A SUBIDA FRONTAL, quando a folha a mede, entra aqui como BIN e nao como
    # fracao: e o mesmo eixo do topo_b, e converter num lugar so evita a familia
    # de erros de meio-bin que ja apareceu no crotch.
    frente_b = None
    if topo_frente_zh is not None:
        frente_b = int(round(topo_frente_zh * Z_BINS - 0.5))

    A_f = w_fill_holes(np, A, occ)
    curva = w_faixa_curve(np, A_f, topo_b, base_b, WAIST_AZ_BINS, ~back_side,
                          reto=topo_reto, frente_b=frente_b)

    diag = {"faixa_peaks_base": pk_b, "faixa_peaks_topo": pk_t,
            "faixa_anel_base": manual or not chute_b,
            "faixa_anel_topo": not chute_t,
            "faixa_base_fonte": "manual" if manual else "anel",
            "faixa_topo_fonte": ("folha" if frente_b is not None
                                 else "reto" if topo_reto else "curva"),
            "faixa_topo_frente_zh": (round((frente_b + 0.5) / Z_BINS, 4)
                                     if frente_b is not None else None),
            "faixa_topo_alvo_zh": round(alvo, 4),
            "faixa_topo_anel_zh": round((topo_b + 0.5) / Z_BINS, 4)}
    return ((base_b + 0.5) / Z_BINS,
            [(b + 0.5) / Z_BINS for b in curva], diag)


def w_faixa_curve(np, A, center_b, floor_b, az_bins, front_mask, reto=False,
                  frente_b=None):
    """A borda de CIMA da faixa, setor a setor. Espelho do w_waist_curve, com a
    assimetria invertida: aqui e a FRENTE que SOBE (o busto empurra o tecido) e
    nunca desce abaixo do anel das costas.

    As duas travas do cos valem pelos mesmos motivos e sao herdadas sem mudanca:
    prior gaussiano (senao o sulco entre os seios, que e vertical e forte em toda
    a janela, deixa o argmax pousar em qualquer altura e sai um pico no meio da
    faixa) e mediana circular de 7 termos (nenhum setor destoa dos vizinhos).

    ------------------------------------------------------------------------
    QUANTO ISTO AQUI MEDE DE VERDADE, medido em 01/08 (_topo_piso.py)
    ------------------------------------------------------------------------
    Pouco, e quem for mexer aqui precisa saber disso antes. Contando os setores
    da FRENTE em que a concavidade na ancora e nula - ou seja, em que nao ha aro
    nenhum para o argmax seguir -, os 37 femininos dao de QUATRO A NOVE em nove.
    Nao ha um so avatar com a frente inteira medida. O volume do busto (ou do
    peitoral) apaga o vinco justamente onde a borda deveria subir.

    Onde nao ha aro, o argmax pega ruido de decimacao e a mediana de 7 alisa
    aquilo num tracado plausivel. E a MESMA patologia ja registrada no docstring
    do w_fit para a passada fina da bainha - "com sinal fraco, o argmax dentro da
    janela encontra ruido, nao tecido" -, um andar acima.

    NAO adianta piso sobre a forca do pico: foi a primeira tentativa e o
    _topo_piso.py mediu que qualquer piso reescreve de 9 a 24 setores de TODO
    avatar, inclusive dos 36 que estao certos. Setor sem aro e a norma aqui, nao
    a anomalia - o b08_d3, que e o unico visivelmente torto, esta entre os
    MELHORES nessa conta (4 de 9). O conserto de verdade nao e limiar: e parar
    de procurar a segunda incognita e MODELAR a subida, como ja se fez com o
    topo escalar ("O TOPO NAO E UMA SEGUNDA MEDIDA", acima). Isso muda os 37 e
    nao existe regua externa para o tracado por setor - a folha da a altura da
    peca, nao a curva -, entao fica para o Rogerio decidir.

    Ate la, `reto` e a valvula: onde o ruido virou defeito visivel, a borda de
    cima e a propria ancora nos 24 setores. Nao fossiliza nada, porque continua
    sendo RETRACADA da ancora a cada --fit.

    ------------------------------------------------------------------------
    E `frente_b` e a saida dos dois (11/08): a subida MODELADA
    ------------------------------------------------------------------------
    Quando o chamador passa a altura do topo frontal - que vem da folha, ou seja
    de regua EXTERNA e por avatar -, nao se procura nada: plato ate
    FAIXA_FRENTE_PLATO setores do centro e meia-cossenoide ate FAIXA_FRENTE_RAIO,
    onde ja e a ancora. Substitui a valvula `reto`, que era o mesmo modelo com
    amplitude ZERO - e amplitude zero e a unica escolha que a folha nunca
    endossa."""
    if frente_b is not None:
        amp = max(0.0, float(frente_b - center_b))
        front = az_bins // 4
        out = []
        for j in range(az_bins):
            d = abs((j - front + az_bins // 2) % az_bins - az_bins // 2)
            if d <= FAIXA_FRENTE_PLATO:
                s = 1.0
            elif d >= FAIXA_FRENTE_RAIO:
                s = 0.0
            else:
                t = (d - FAIXA_FRENTE_PLATO) / float(FAIXA_FRENTE_RAIO
                                                     - FAIXA_FRENTE_PLATO)
                s = 0.5 * (1.0 + float(np.cos(np.pi * t)))
            out.append(int(round(center_b + amp * s)))
        return out
    if reto:
        return [center_b] * az_bins
    out = []
    for j in range(az_bins):
        if front_mask[j]:
            lo_f = center_b
            hi_f = center_b + FAIXA_TOPO_UP_FRONT * Z_BINS
        else:
            lo_f = center_b - FAIXA_TOPO_BACK_ZH * Z_BINS
            hi_f = center_b + FAIXA_TOPO_BACK_ZH * Z_BINS
        lo = int(max(0, floor_b + 1, round(lo_f)))
        hi = int(min(Z_BINS - 1, round(hi_f)))
        if hi < lo:
            out.append(center_b)
            continue
        zz = np.arange(lo, hi + 1, dtype=np.float64)
        sigma = max((hi - center_b) * WAIST_PRIOR_SIGMA, 1.0)
        w = A[j, lo:hi + 1] * np.exp(-0.5 * ((zz - center_b) / sigma) ** 2)
        out.append(lo + int(w.argmax()) if w.size and w.max() > 0 else center_b)

    k = WAIST_MEDIAN // 2
    return [int(sorted([out[(j + d) % az_bins] for d in range(-k, k + 1)])[k])
            for j in range(az_bins)]


def w_fit(me, np, co, H, crotch, leg_id, is_arm, crotch_override=None,
          waist_override=None, faixa=False, faixa_base_override=None,
          faixa_topo_reto=False, faixa_topo_frente=None, cos_avental=False):
    """Devolve (cfg em metros, diagnostico).

    A bainha sai como ESCALAR por perna e o cos como curva de 24 setores.

    ---------------------------------------------------------------------
    TENTATIVA DESCARTADA: seguir o vinco setor a setor (passada "fina")
    ---------------------------------------------------------------------
    O Rogerio apontou que a divisa parecia "pular". A hipotese era que a
    bainha modelada pela Meshy serpenteia e que a linha reta passava PERTO
    dela em vez de EM CIMA dela. A correcao natural seria uma segunda
    passada com 48 setores procurando o vinco local numa janela de ~2 cm.

    Foi implementada e PIOROU. Quem explicou foi um render de EMISSAO PURA (sem
    luz nenhuma) pintando cinza a regiao do short e vermelho a concavidade. Sem
    iluminacao porque no render normal a sombra do degrau de tecido se confunde
    com a divisa de cor - foi essa confusao que gerou a hipotese errada. O que
    apareceu:

      - o vinco da bainha EXISTE, mas e fraco - so aparece com a concavidade
        crua, sem suavizacao, e com limiar baixo;
      - e ele e praticamente HORIZONTAL. A bainha ja e um anel reto.

    Com sinal fraco, o argmax dentro da janela encontra ruido de decimacao, nao
    tecido. O resultado foi uma borda cheia de farpas verticais - visivelmente
    pior que a reta. Ou seja: a premissa estava errada. Nao havia serpenteio
    para seguir; a reta JA era a representacao fiel.

    O que o Rogerio viu como "pulando" nao era a divisa de cor - era a sombra
    do degrau de tecido logo acima dela, que e geometria da malha e continua
    la faca-se o que se fizer com a pintura.

    Licao: antes de fazer a borda perseguir um vinco, medir se o vinco tem
    sinal - e medir num render SEM LUZ, porque com luz nao se distingue sombra
    de divisa."""
    k, _ = w_curvature(me, np)
    kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
    z = co[:, 2]

    # Duas constantes do short sao por COLECAO, e o `faixa` e que diz qual e -
    # ele vem de tem_faixa(), que e o teste de id feminino. Nao ha terceiro caso.
    abs_range = WAIST_ABS_RANGE_F if faixa else WAIST_ABS_RANGE
    recuo = HEM_RECUO_F if faixa else HEM_RECUO

    # A VIRILHA e a ancora de todas as janelas, entao ela e o unico numero que
    # vale a pena poder corrigir a mao. w_limbs devolve "onde as pernas param de
    # se tocar", que na maioria dos corpos E a virilha - mas nao num IMC 148, em
    # que as coxas encostam ate quase o joelho. No zen_m_b12_d1 isso deu 0.297
    # contra ~0.37 de virilha real, e as janelas ancoradas nela levaram o short
    # inteiro 14% da altura para baixo. Corrigir a ancora conserta bainha e cos
    # de uma vez, sem escrever curva na mao.
    if crotch_override:
        crotch = crotch_override * H
    crotch_b = int(crotch / H * Z_BINS)

    # leg_id 0/1 vem da ordem de fusao do union-find, nao do lado. Reordena
    # para (esquerda = x<0, direita = x>=0), que e como w_field le.
    lids = [0, 1]
    mean_x = [float(co[leg_id == lid, 0].mean()) if (leg_id == lid).any() else 0.0
              for lid in lids]
    if mean_x[0] > mean_x[1]:
        lids.reverse()

    # ---- BAINHA: um anel por perna, medido na perna, nao no corpo ----------
    # A janela e ancorada na VIRILHA e calibrada pela propria biblioteca (ver
    # HEM_BELOW_CROTCH). O criterio do anel sozinho nao basta aqui porque os
    # dois vizinhos da bainha TAMBEM sao aneis fechados e mais fortes que ela:
    # a virilha em cima e o joelho embaixo. Com a janela larga a primeira
    # rodada perdeu para os dois - 4 avatares grudaram na virilha (b01_d2,
    # b04_d3, b09_d1, b11_d2) e o b08_d3 caiu no joelho.
    hem_curves, hem_centers, hem_peaks_d = [], [], []
    for lid in lids:
        sel = np.where(leg_id == lid)[0]
        A, ring, _ = w_ring_map(np, co, kn, sel, H, "slice")
        pk = w_peaks(np, ring,
                     crotch_b - HEM_BELOW_CROTCH[1] * Z_BINS,
                     crotch_b - HEM_BELOW_CROTCH[0] * Z_BINS)
        hem_peaks_d.append([[round(s, 3), round((b + 0.5) / Z_BINS, 4)] for s, b in pk[:4]])
        hb = pk[0][1] if pk else int(crotch_b - recuo * Z_BINS)

        # centro da perna na altura da bainha. Nao e usado pelo ajuste
        # automatico (que grava a bainha como ESCALAR), e sim para permitir
        # correcao manual por azimute no shorts_map.json.
        near = sel[np.abs(co[sel, 2] - (hb + 0.5) / Z_BINS * H) < 0.03 * H]
        if near.size < 30:
            near = sel
        hem_centers.append([float(co[near, 0].mean()), float(co[near, 1].mean())])
        hem_curves.append((hb + 0.5) / Z_BINS * H)

    # ---- COS: anel no tronco, ignorando os bracos --------------------------
    # A janela comeca ACIMA da virilha: o vinco da virilha e forte e da a volta,
    # entao satisfaz o criterio do anel e vencia como "cos" nos corpos pesados
    # (b07_d1 e b08_d1 pousaram os dois exatamente na altura da virilha).
    torso = np.where((~is_arm) & (z >= crotch))[0]
    back_side = w_back_side_mask(np, WAIST_AZ_BINS)
    A_t, ring_t, occ_t = w_ring_map(np, co, kn, torso, H, "axis", WAIST_AZ_BINS,
                                    az_mask=back_side)
    # intersecao das duas janelas: a ancorada na virilha e a absoluta
    waist_peaks = w_peaks(np, ring_t,
                          max(crotch_b + WAIST_ABOVE_CROTCH[0] * Z_BINS,
                              abs_range[0] * Z_BINS),
                          min(crotch_b + WAIST_ABOVE_CROTCH[1] * Z_BINS,
                              abs_range[1] * Z_BINS))
    waist_b = waist_peaks[0][1] if waist_peaks else int(crotch_b + 0.12 * Z_BINS)

    # ANCORA DO COS corrigida a mao, se houver. Mesmo padrao - e mesmo motivo -
    # do crotch_override_zh: o anel e a ancora de TODA a curva, entao quando ele
    # erra, erra tudo junto, e um numero so conserta. Sobrevive a --fit.
    #
    # Existe porque em dois avatares (b10_d2, b11_d2) o perfil do anel nao tem
    # maximo local nenhum dentro da janela - sobe monotono. w_peaks volta vazio,
    # waist_b cai no chute "virilha + 0.12" e o cos inteiro fica baixo: no
    # b11_d2 deu 0.485 contra 0.553 medidos na folha. Nao adianta alargar a
    # janela, porque o problema nao e onde procurar, e que nao ha pico.
    if waist_override:
        waist_b = int(waist_override * Z_BINS)
        waist_peaks = waist_peaks or [[0.0, waist_b]]

    # Janela ASSIMETRICA: funda para baixo so na frente, zero para cima na
    # frente, estreita nos dois sentidos nas costas. O piso e a bainha mais alta
    # das duas pernas: abaixo dela o short acabaria antes de comecar.
    floor_b = int(max(hem_curves) / H * Z_BINS)
    A_f = w_fill_holes(np, A_t, occ_t)  # ver w_fill_holes: 32% -> 84% de ocupacao
    wf = w_waist_curve(np, A_f, waist_b, floor_b, WAIST_AZ_BINS, ~back_side)

    waist_zh = [(b + 0.5) / Z_BINS for b in wf]
    if cos_avental:
        nor_v = np.empty(len(me.vertices) * 3, dtype=np.float64)
        me.vertices.foreach_get("normal", nor_v)
        waist_zh = w_cos_avental(np, co, nor_v.reshape(-1, 3), is_arm, H,
                                 crotch / H, max(hem_curves) / H,
                                 waist_zh, WAIST_AZ_BINS)

    # ALISAMENTO POR ULTIMO, de proposito: o avental decide ONDE o cos tem que
    # estar e este passo decide COMO ele chega la. Invertendo a ordem, o avental
    # reintroduziria a quina que o alisamento acabou de tirar.
    waist_bruto = list(waist_zh)
    waist_zh = w_waist_liso(np, waist_zh, max(hem_curves) / H + 1.0 / Z_BINS)

    cfg = {
        "hem_l": hem_curves[0],
        "hem_r": hem_curves[1],
        "hem_center_l": hem_centers[0],
        "hem_center_r": hem_centers[1],
        "waist": [v * H for v in waist_zh],
    }
    diag = {
        "crotch_zh": round(crotch / H, 4),
        "arm_verts": int(is_arm.sum()),
        "leg_verts": [int((leg_id == 0).sum()), int((leg_id == 1).sum())],
        "hem_peaks_zh": hem_peaks_d,
        "waist_peaks_zh": [[round(s, 3), round((b + 0.5) / Z_BINS, 4)]
                           for s, b in waist_peaks[:4]],
        # a altura do anel e a ancora de TODO o cos, e a trava de tracado do
        # --report compara cada setor com ela. Sem anel (lista de picos vazia) a
        # curva inteira boia sobre um chute - isso e defeito por si so e precisa
        # sobreviver ao mapa, nao ficar so no log.
        "waist_ring_zh": round((waist_b + 0.5) / Z_BINS, 4),
        "waist_ring_found": bool(waist_peaks),
        # quanto o alisamento mexeu, para o conserto ser auditavel sem refazer o
        # --fit: [maior subida, maior descida] em fracao da altura. A subida e
        # travada em WAIST_LISO_TETO_BINS/Z_BINS por construcao; a descida nao,
        # e e ela que diz se o alisamento derrubou um flanco inteiro.
        "waist_liso_dz": [
            round(max([b - a for a, b in zip(waist_bruto, waist_zh)] + [0.0]), 4),
            round(max([a - b for a, b in zip(waist_bruto, waist_zh)] + [0.0]), 4),
        ],
    }

    if faixa:
        fb, ft, fdiag = w_faixa(np, co, kn, H, is_arm, crotch,
                                base_override=faixa_base_override,
                                topo_reto=faixa_topo_reto,
                                topo_frente_zh=faixa_topo_frente)
        cfg["faixa_lo"] = fb * H
        cfg["faixa_hi"] = [v * H for v in ft]
        diag.update(fdiag)

    return cfg, diag


def w_field(np, co, cfg, partes=False):
    """Campo escalar com sinal: >0 dentro da roupa, 0 exatamente na borda.

    d_short = min(cos(azimute) - z, z - bainha(azimute da perna))
    d_faixa = min(topo - z, z - base)                    (so no feminino)
    d       = max(d_short, d_faixa)

    Existir como CAMPO CONTINUO, e nao como teste booleano, e o que permite
    cortar a malha exatamente na linha (w_cut_boundary). O MAXIMO das duas pecas
    preserva essa propriedade: as duas regioes sao disjuntas por construcao (uma
    acaba no cos, a outra comeca acima do umbigo), entao perto da borda de uma o
    campo da outra e fortemente negativo e nao mexe no cruzamento de zero.

    Cada curva aceita ESCALAR ou LISTA. O ajuste automatico grava lista no cos e
    escalar no resto; um escalar escrito a mao no shorts_map.json vale como
    altura constante. E o que mantem a correcao manual barata: para consertar um
    avatar basta escrever "waist": 0.57, sem editar 48 numeros.

    partes=True devolve a lista de campos por peca, na ordem (short, faixa) -
    e o que permite exigir que CADA peca seja conexa, em vez de exigir que o
    conjunto todo seja."""
    z = co[:, 2]
    az_body = np.arctan2(co[:, 1], co[:, 0])
    waist = w_interp_circ(np, np.atleast_1d(cfg["waist"]), az_body)

    left = co[:, 0] < 0
    hem = np.empty(len(co), dtype=np.float64)
    for side, key, ckey in ((left, "hem_l", "hem_center_l"),
                            (~left, "hem_r", "hem_center_r")):
        vals = np.atleast_1d(cfg[key])
        if vals.size == 1:
            hem[side] = float(vals[0])
        else:
            cx, cy = cfg[ckey]
            az_leg = np.arctan2(co[side, 1] - cy, co[side, 0] - cx)
            hem[side] = w_interp_circ(np, vals, az_leg)

    campos = [np.minimum(waist - z, z - hem)]
    if cfg.get("faixa_lo") is not None:
        base = w_interp_circ(np, np.atleast_1d(cfg["faixa_lo"]), az_body)
        topo = w_interp_circ(np, np.atleast_1d(cfg["faixa_hi"]), az_body)
        campos.append(np.minimum(topo - z, z - base))

    if partes:
        return campos
    out = campos[0]
    for c in campos[1:]:
        out = np.maximum(out, c)
    return out


def w_cut_boundary(bm, np, bmesh, field_of, is_arm_of):
    """Corta a malha EXATAMENTE na linha do short, em vez de aproximar por
    triangulo inteiro.

    Sem isto a fronteira e quantizada pela malha: cada triangulo e todo preto
    ou todo titanio, e como a bainha nao coincide com nenhuma aresta a borda
    sai numa franja de dente-de-serra de ~6 mm (um triangulo a 60k). Alisar por
    maioria de vizinhanca nao resolve - o dente-de-serra e o PISO de quem
    decide por face, nao ruido em cima dele.

    Aqui cada aresta que cruza a linha e partida no ponto de cruzamento e os
    novos vertices sao ligados dentro da face. A borda passa a ser aresta de
    verdade, exatamente onde o campo zera. Custo: algumas centenas de
    triangulos a mais, so na costura.

    Devolve o numero de vertices inseridos."""
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    d = {v: float(field_of[v.index]) for v in bm.verts}
    arm = {v: bool(is_arm_of[v.index]) for v in bm.verts}

    new_verts = []
    for e in list(bm.edges):
        a, b = e.verts
        da, db = d[a], d[b]
        if (da > 0.0) == (db > 0.0) or da == db:
            continue
        if arm[a] or arm[b]:
            continue
        t = da / (da - db)
        if not (1e-3 < t < 1.0 - 1e-3):
            continue
        try:
            _ne, nv = bmesh.utils.edge_split(e, a, t)
        except Exception:
            continue
        d[nv] = 0.0
        arm[nv] = False
        new_verts.append(nv)

    if new_verts:
        bmesh.ops.connect_verts(bm, verts=new_verts)
    return len(new_verts)


def worker_main():
    import bpy
    import bmesh
    import numpy as np
    import math
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree

    argv = sys.argv[sys.argv.index("--") + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--mode", required=True, choices=["fit", "apply", "render", "check"])
    ap.add_argument("--id", required=True)
    ap.add_argument("--root", required=True)
    a = ap.parse_args(argv)

    sys.path.insert(0, os.path.join(a.root, "scripts"))
    import zenith_material as zm
    import zenith_paths as zp

    master = os.path.join(a.root, "02_master", a.id + "_master.glb")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=master)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(meshes) != 1:
        sys.stderr.write("esperava 1 malha, achei {}\n".format(len(meshes)))
        sys.exit(1)
    obj = meshes[0]
    me = obj.data

    zs = [v.co.z for v in me.vertices]
    H = max(zs) - min(zs)

    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)

    # A anatomia e recalculada em TODOS os modos (nao so no --fit): a mascara
    # de braco entra na pintura, entao guardar so os numeros do cos/bainha no
    # mapa nao bastaria para reproduzir a regiao.
    crotch, leg_id, is_arm = w_limbs(me, np, co, H)

    # Cada curva pode ser ESCALAR (altura constante) ou LISTA (por azimute).
    # O ajuste automatico grava escalar na bainha e lista no cos; uma correcao
    # manual pode usar qualquer um dos dois.
    def _scale(v, f):
        return [x * f for x in v] if isinstance(v, (list, tuple)) else v * f

    def _round(v, f):
        return ([round(x * f, 5) for x in v] if isinstance(v, (list, tuple))
                else round(v * f, 5))

    if a.mode == "fit":
        # correcao manual da ancora, se houver: sobrevive a um --fit posterior
        _e = load_map(a.root).get(a.id, {})
        ov = _e.get("crotch_override_zh")
        wov = _e.get("waist_ring_override_zh")
        fov = _e.get("faixa_base_override_zh")
        fret = bool(_e.get("faixa_topo_reto"))
        ffre = _e.get("faixa_topo_frente_zh")
        cave = bool(_e.get("cos_avental"))
        cfg, diag = w_fit(me, np, co, H, crotch, leg_id, is_arm, crotch_override=ov,
                          waist_override=wov, faixa=tem_faixa(a.id),
                          faixa_base_override=fov, faixa_topo_reto=fret,
                          faixa_topo_frente=ffre, cos_avental=cave)
        entry = {
            # gravado em FRACAO DA ALTURA, nao em metros: assim um numero copiado
            # de um avatar para outro continua querendo dizer a mesma coisa
            "hem_l_zh": _round(cfg["hem_l"], 1.0 / H),
            "hem_r_zh": _round(cfg["hem_r"], 1.0 / H),
            "hem_center_l": [round(x, 5) for x in cfg["hem_center_l"]],
            "hem_center_r": [round(x, 5) for x in cfg["hem_center_r"]],
            "waist_zh": _round(cfg["waist"], 1.0 / H),
            "diag": diag,
        }
        if "faixa_lo" in cfg:
            entry["faixa_lo_zh"] = _round(cfg["faixa_lo"], 1.0 / H)
            entry["faixa_hi_zh"] = _round(cfg["faixa_hi"], 1.0 / H)
        if ov:
            entry["crotch_override_zh"] = ov
        if wov:
            entry["waist_ring_override_zh"] = wov
        if fov:
            entry["faixa_base_override_zh"] = fov
        if fret:
            entry["faixa_topo_reto"] = True
        if ffre is not None:
            entry["faixa_topo_frente_zh"] = ffre
        if cave:
            entry["cos_avental"] = True
    else:
        smap = load_map(a.root)
        entry = smap[a.id]

    cfg = {
        "hem_l": _scale(entry["hem_l_zh"], H),
        "hem_r": _scale(entry["hem_r_zh"], H),
        "hem_center_l": entry.get("hem_center_l", [0.0, 0.0]),
        "hem_center_r": entry.get("hem_center_r", [0.0, 0.0]),
        "waist": _scale(entry["waist_zh"], H),
    }
    if "faixa_lo_zh" in entry:
        cfg["faixa_lo"] = _scale(entry["faixa_lo_zh"], H)
        cfg["faixa_hi"] = _scale(entry["faixa_hi_zh"], H)

    tris_master = sum(len(p.vertices) - 2 for p in me.polygons)
    field = w_field(np, co, cfg)

    # Os DOIS slots tem que existir antes de qualquer face receber
    # material_index=1: o Blender limita o indice ao numero de slots, entao
    # atribuir primeiro e criar o slot depois pinta o short de cor de corpo -
    # sem erro nenhum, so o avatar sai inteiro titanio.
    me.materials.clear()
    # ...e PURGAR os datablocks, nao so esvaziar os slots. O master ja vem com
    # um material chamado Zenith_Body (o process.py gravou), e limpar o slot nao
    # apaga o datablock: bpy.data.materials.new("Zenith_Body") encontra o nome
    # ocupado e devolve "Zenith_Body.001", que e o que iria para o GLB do app.
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    me.materials.append(zm.make_body_material(bpy))
    me.materials.append(zm.make_shorts_material(bpy))

    # A mascara de PINTURA nao e a mascara de DETECCAO, e a separacao e o que
    # torna esta mudanca conferivel. O w_arm_wide corta o braco na altura da
    # faixa, e se ele entrasse no `is_arm` mudaria o conjunto `tronco` de onde
    # saem os aneis - ou seja, mexeria em cos, bainha e nas duas bordas da faixa
    # dos 76 de uma vez, e nenhuma regua separaria o que melhorou do que piorou.
    # Aqui ele entra depois de tudo medido: os numeros do mapa ficam identicos e
    # a unica diferenca e QUAL FACE recebe preto. Avatar sem faixa nao chama a
    # funcao, entao os 39 masculinos nao mudam um vertice por construcao.
    is_paint = is_arm
    if cfg.get("faixa_lo") is not None:
        lo = float(np.min(np.atleast_1d(cfg["faixa_lo"]))) / H
        hi = float(np.max(np.atleast_1d(cfg["faixa_hi"]))) / H
        z0h = float(co[:, 2].min()) / H
        is_paint = is_arm | w_arm_wide(np, co, H, is_arm, lo - z0h, hi - z0h)

    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.verts.layers.float.new("arm")
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    for v in bm.verts:
        v[lay] = 1.0 if is_paint[v.index] else 0.0

    added = w_cut_boundary(bm, np, bmesh, field, is_paint)

    # Partir uma aresta transforma o triangulo vizinho em QUAD, e connect_verts
    # nem sempre tem o que ligar dentro dele. Sobra malha mista. O exportador
    # triangula os quads na saida por conta propria, entao contar faces aqui e
    # comparar com triangulos no GLB acusa uma diferenca que nao existe - foi o
    # que reprovou o primeiro --apply (60857 faces contra 61716 triangulos).
    # Triangular aqui faz o que eu valido ser exatamente o que e gravado, e de
    # quebra mantem o dist com a mesma topologia so-de-triangulos do master.
    bmesh.ops.triangulate(bm, faces=bm.faces[:])

    # Depois do corte cada face esta INTEIRA de um lado da linha, entao o
    # centroide decide sem ambiguidade.
    bm.faces.ensure_lookup_table()
    cent = np.array([tuple(f.calc_center_median()) for f in bm.faces],
                    dtype=np.float64)
    campos = w_field(np, cent, cfg, partes=True)
    pilha = np.vstack(campos)
    qual = pilha.argmax(axis=0)          # de QUAL peca esta face e
    fld = pilha.max(axis=0)
    peca = np.full(len(cent), -1, dtype=np.int64)
    for i, f in enumerate(bm.faces):
        is_s = bool(fld[i] > 0.0) and not any(v[lay] > 0.5 for v in f.verts)
        f.material_index = 1 if is_s else 0
        if is_s:
            peca[i] = qual[i]
    nf = len(bm.faces)

    # ---- TRAVA: CADA PECA tem que ser UMA REGIAO CONEXA ------------------
    # Quadril + duas coxas formam uma peca unica, ligada pela virilha; a faixa
    # e um tubo em volta do torax, tambem uma so. Uma mao ou um antebraco
    # pintado por engano fica numa ILHA separada, porque nao ha caminho pela
    # superficie entre a mao e a roupa. Entao exigir conexidade pega exatamente
    # a falha que da medo: mascara de braco errada.
    #
    # A mascara de braco vem de w_limbs (eventos de fusao do union-find). Ela
    # acerta nos corpos normais, mas nao ha garantia num corpo obeso em que o
    # braco encosta no tronco e a malha funde os dois. Sem esta trava isso sairia
    # calado - um avatar de mao preta no meio de 76.
    #
    # ⚠️ A conta e POR PECA desde que a faixa existe (01/08). A versao anterior
    # perguntava "a maior ilha e 97% do pintado?", e com duas pecas legitimas a
    # maior e ~60% - a trava reprovaria justamente o resultado certo. Afrouxar o
    # limiar para caber duas pecas teria destruido a trava: 0.60 aceita tambem
    # uma mao preta do tamanho de um short. A pergunta certa nao e quantas ilhas
    # ha no total, e sim se CADA peca esperada e uma ilha so.
    def _componentes(sel_peca):
        seen = [False] * nf
        gs = []
        for f0 in bm.faces:
            if peca[f0.index] != sel_peca or seen[f0.index]:
                continue
            stack, members = [f0], []
            seen[f0.index] = True
            while stack:
                f = stack.pop()
                members.append(f)
                for e in f.edges:
                    for g in e.link_faces:
                        if peca[g.index] == sel_peca and not seen[g.index]:
                            seen[g.index] = True
                            stack.append(g)
            gs.append(members)
        gs.sort(key=len, reverse=True)
        return gs

    # ---- ILHA ESCONDIDA NAO E DEFEITO: ela nao aparece -------------------
    # A faixa do primeiro avatar feminino saiu em 4 ilhas com os dois renders
    # CERTOS. As tres ilhas extras nao eram mascara de braco falhando (a
    # fronteira delas com o braco e ZERO): sao superficie INTERNA da malha da
    # Meshy - o bolso da axila e a pele atras do cabelo, que ficam dentro do
    # corpo. Medido com raio pela normal: a ilha visivel da 6% de oclusao e as
    # tres escondidas dao 99-100%. Nao ha limiar a escolher, ha um abismo.
    #
    # Elas continuam PINTADAS de propria vontade - despintar deixaria pele
    # clara espiando por dentro da axila -, mas saem da conta de conexidade.
    # A trava nao perde forca: mao preta e visivel POR DEFINICAO, entao ela
    # continua contando como ilha. A pergunta certa nao e "quantas ilhas ha",
    # e sim "quantas ilhas alguem VE".
    #
    # O LIMIAR ESTA NO MEIO DE UM VAZIO MEDIDO, e ja errei os dois lados dele.
    #
    # 0.5 custou uma peca inteira: no zen_f_b05_d3 a faixa - 7152 faces - caiu
    # no balde de escondida e a peca saiu com ZERO ilha, ou seja um top que o
    # detector jurava nao existir. Aquela faixa mede 42% de livre, e o que
    # bloqueia os outros 58% esta a 4 mm dela: a Meshy modelou o tecido como
    # CASCA SOBRE A PELE, a regiao pega as duas camadas e a de baixo conta como
    # tapada. Uma peca 42% a vista esta a vista.
    #
    # 0.10 errou para o outro lado. Com ele, b01_d2 e b03_d2 passaram a acusar
    # ilha extra na faixa, e a sonda _ilhas_vis.py mostrou que aquelas ilhas sao
    # a mesma familia dos bolsos de axila do b01_d1. Os dois grupos, medidos:
    #
    #   interna    0.0%   7.4%  10.0%  10.7%
    #   a vista   42.0%  81.7%  86.4%  91.0%  92.2%
    #
    # O vazio vai de 0.11 a 0.42 e o limiar vai no meio dele. Antes de mexer
    # neste numero de novo, rodar a sonda e olhar os dois grupos - o erro das
    # duas vezes foi escolher limiar por raciocinio em vez de por medida.
    #
    # TENTATIVA DESCARTADA - raio para os dois lados. Antes de medir, apostei em
    # normal invertida e passei a aceitar quem escapasse por +n OU -n. Nao mudou
    # nada e a medida diz por que: o avesso da 0% de livre em TODAS as pecas de
    # todos os avatares. Nao ha normal invertida aqui, e o teste extra so dobra
    # o custo de raycast.
    VISIVEL_MIN = 0.25
    bvh = BVHTree.FromBMesh(bm)

    def _visivel(g):
        """Fracao da ilha que e a superficie mais externa no seu proprio lugar."""
        passo = max(1, len(g) // 200)
        am = g[::passo]
        livre = 0
        for f in am:
            p = f.calc_center_median()
            d = f.normal.copy()
            if d.length < 1e-9:
                continue
            if bvh.ray_cast(p + d * 0.002, d, 1.0)[0] is None:
                livre += 1
        return livre / float(len(am))

    # Lasca solta e defeito, nao ambiguidade: sao poucos triangulos pretos
    # perdidos no corpo, que o campo pegou de rasparem na linha. Some com elas
    # aqui em vez de tolerar - uma peca com menos de 5% do tamanho da maior nao
    # e short de ninguem. O que sobrevive a este corte e ou a peca principal ou
    # uma divisao de verdade (barriga descendo abaixo da bainha), e essa vale
    # ser reportada.
    slivers = 0
    escondidas = 0
    comps, por_peca, partida_ok = [], [], []
    for ip in range(len(campos)):
        gs = _componentes(ip)
        if gs:
            keep = max(1, int(len(gs[0]) * 0.05))
            for g in gs[1:]:
                if len(g) < keep:
                    slivers += len(g)
                    for f in g:
                        f.material_index = 0
                        peca[f.index] = -1
            gs = [g for g in gs if len(g) >= keep]

            # ---- A FAIXA PODE SAIR EM DUAS, e isso passou a ser CERTO ------
            # Desde que o w_arm_wide corta o braco na altura da banda, num corpo
            # pesado o braco TAPA o lado do torax e a faixa aparece em dois
            # pedacos - frente e costas. E o que se ve num corpo de verdade, e
            # nao ha nada a consertar: exigir uma ilha so aqui reprovaria
            # justamente o resultado que se acabou de acertar.
            #
            # O que separa peca legitima de lasca de braco e o PLANO SAGITAL.
            # Frente e costas cruzam o meio do corpo por construcao - a banda da
            # a volta -, enquanto o que sobra encostado na axila fica inteiro de
            # um lado. E o mesmo raciocinio das ilhas escondidas: nao afrouxar o
            # limiar, e sim perguntar outra coisa. Afrouxar aceitaria mao preta.
            # SAO DOIS TESTES porque sao dois defeitos diferentes, e nenhum dos
            # dois sozinho serve. Medido no b10_d1 e no b12_d1 (_ilhas_vis.py):
            #
            #   frente / costas   60..100% da altura da banda   cruza o meio
            #   franja no meio     2..  7%                      cruza o meio
            #   franja na axila      0.4%                       so de um lado
            #
            # A ALTURA pega a franja - fita de duas fatias que o corte deixou
            # solta na borda de cima ou de baixo. Sozinha ela nao serve: um
            # antebraco pintado por falha da mascara e VERTICAL e passaria no
            # teste de altura sem esforco.
            # O SAGITAL pega o antebraco, porque a banda da a volta e cruza o
            # meio do corpo por construcao, e braco nenhum faz isso. Sozinho ele
            # nao serve: as franjas do meio tambem cruzam.
            if ip == FAIXA_PECA and len(gs) > 1:
                cxm = float(np.median(co[:, 0]))
                alt = (float(np.max(np.atleast_1d(cfg["faixa_hi"])))
                       - float(np.min(np.atleast_1d(cfg["faixa_lo"]))))
                pecas, restos = [], []
                for g in gs:
                    c = [f.calc_center_median() for f in g]
                    xs = [p.x - cxm for p in c]
                    zs = [p.z for p in c]
                    ok = (min(xs) < 0 < max(xs)
                          and max(zs) - min(zs) >= FAIXA_PECA_ALT_MIN * alt)
                    (pecas if ok else restos).append(g)
                for g in restos:
                    slivers += len(g)
                    for f in g:
                        f.material_index = 0
                        peca[f.index] = -1
                gs = pecas

            visiveis = []
            for g in gs:
                if _visivel(g) >= VISIVEL_MIN:
                    visiveis.append(g)
                else:
                    escondidas += len(g)
            gs = visiveis
        tam = [len(g) for g in gs]
        por_peca.append(tam)
        comps += tam
        # Frente + costas com o braco no meio conta como peca inteira. Tres ja
        # nao: uma banda tem dois lados, e o terceiro pedaco e outra coisa.
        partida_ok.append(ip == FAIXA_PECA and 1 <= len(tam) <= 2)

    n_short = sum(comps) + escondidas   # a escondida continua pintada
    # "biggest" continua sendo a fracao da MAIOR ilha DENTRO DA SUA PECA, e o
    # placar do avatar e a pior das pecas. Com uma peca so, e o numero de antes.
    biggest = min([1.0 if (t and ok) else ((t[0] / float(sum(t))) if t else 0.0)
                   for t, ok in zip(por_peca, partida_ok)], default=0.0)
    vazias = [i for i, t in enumerate(por_peca) if not t]

    bm.to_mesh(me)
    bm.free()
    frac = float(n_short) / nf

    if not comps:
        sys.stderr.write("nenhuma face pintada de short\n")
        sys.exit(1)

    # MAPEAR sinaliza, ENTREGAR recusa. Nem toda ilha e erro: num corpo em que a
    # barriga desce abaixo da bainha, o short REALMENTE aparece como duas
    # manchas separadas. Abortar o --fit nessa hora jogaria fora o ajuste do
    # avatar mais dificil da biblioteca, que e justamente o que se quer guardar
    # para corrigir a mao. Entao aqui so marca; quem se recusa a gravar o GLB e
    # o --apply, mais abaixo.
    suspect = biggest < 0.97 or bool(vazias)
    if suspect:
        sys.stderr.write(
            "[AVISO] pecas em {} ilhas ({}, pior peca = {:.1%}{}). Ilha solta e "
            "quase sempre mao/antebraco pintado por falha da mascara de braco - "
            "conferir o render antes de aplicar.\n"
            .format(len(comps), por_peca, biggest,
                    ", peca(s) {} VAZIA(S)".format(vazias) if vazias else ""))

    me.update()

    if a.mode == "check":
        # so as travas, sem render: varrer a biblioteca inteira custa minutos
        # em vez de meia hora, entao da para conferir de novo a cada mudanca
        print("RESULT " + json.dumps({
            "summary": "{}: roupa {:.1%}, ilhas {}, pior peca {:.1%}, +{} costura{}".format(
                a.id, frac, por_peca, biggest, added,
                "   << CONFERIR" if suspect else "")}))
        sys.exit(0)

    if a.mode == "apply":
        # Ultimo portao antes do asset que o app consome.
        if suspect and not entry.get("allow_islands"):
            sys.stderr.write(
                "recusado: pecas em {} ilhas ({}, pior {:.1%}). Se as ilhas forem "
                "legitimas para este corpo, marque \"allow_islands\": true no "
                "shorts_map.json.\n".format(len(comps), por_peca, biggest))
            sys.exit(1)
        # Versao NOVA, nunca por cima: o dist e URL de CDN (zenith_paths.py).
        # Aqui isso vale dobrado - o short e a correcao que o usuario ja viu
        # errada, entao entregar por baixo do cache e nao corrigir nada.
        version, dist = zp.dist_glb_next(a.root, a.id)

        def reject(msg):
            """Desfaz o arquivo novo e deixa a versao anterior servindo."""
            if os.path.isfile(dist):
                os.remove(dist)
            sys.stderr.write(msg)
            sys.exit(1)

        tris_before = nf
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.gltf(
            filepath=dist, export_format="GLB", use_selection=True,
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14,
            export_draco_normal_quantization=14,
        )
        # o export tem que ter mexido so no material
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=dist)
        back = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        tris_after = sum(len(p.vertices) - 2 for o in back for p in o.data.polygons)
        if tris_after != tris_before:
            reject("geometria mudou no export: {} -> {}\n".format(
                tris_before, tris_after))
        # O corte da costura ACRESCENTA triangulos - e a unica mudanca de
        # geometria permitida aqui, e so na borda do short. Um crescimento
        # grande significaria que o campo cruzou zero onde nao devia.
        #
        # DIVIDIDO POR `frac`, E NAO PELO TOTAL DE TRIANGULOS (01/08). A costura
        # e uma CURVA: o custo dela cresce com o COMPRIMENTO da borda da roupa.
        # O total de triangulos e grandeza de AREA. A razao antiga misturava as
        # duas, entao corpo com mais roupa pagava mais sem estar errado - a
        # trava foi calibrada no acervo masculino de UMA peca (max 3,60%, folga
        # de 67%) e nao sobreviveu a corpo feminino de DUAS. O zen_f_b11_d1
        # reprovou em +6,2% estando ABAIXO da mediana feminina uma vez
        # normalizado (_costura.py: fem p50 0,198, mas p50 0,185, max do acervo
        # 0,265 e MASCULINO aprovado). A razao nova tambem serve melhor ao que
        # a trava diz vigiar: costura perdida acrescenta comprimento sem
        # acrescentar roupa, entao sobe aqui - na razao velha ela sumia num
        # corpo grande. Limiar 0,40 = mesma folga de ~50% sobre o maximo medido.
        costura = (tris_before - tris_master) / float(tris_master)
        por_frac = costura / max(frac, 1e-9)
        if por_frac > 0.40:
            reject("costura grande demais: {} -> {} ({:+.1%} para roupa de "
                   "{:.1%} = {:.3f} por frac, teto 0.40)\n".format(
                       tris_master, tris_before, costura, frac, por_frac))
        names = [m.name for m in back[0].data.materials]
        if names != [zm.MATERIAL_NAME, zm.SHORTS_MATERIAL_NAME]:
            reject("materiais inesperados no dist: {}\n".format(names))
        gone = zp.dist_glb_retire(a.root, a.id, keep=version)
        print("RESULT " + json.dumps({
            "summary": "{}: {} tri ({:+d} costura), short {:.1%}, v{}{}".format(
                a.id, tris_after, tris_after - tris_master, frac, version,
                " (aposentou {})".format(", ".join(gone)) if gone else "")}))
        sys.exit(0)

    # ------------------------------------------------------------ render QA
    env = os.path.join(a.root, "03_dist", "env", "zenith_env.hdr")
    if not os.path.isfile(env):
        sys.stderr.write("ambiente nao encontrado: {}\n".format(env))
        sys.exit(1)

    scene = bpy.context.scene
    world = bpy.data.worlds.new("Zenith")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(env)
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(tex.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    zz = [v.z for v in bb]
    center = Vector((0.0, 0.0, (min(zz) + max(zz)) / 2.0))
    height = max(zz) - min(zz)

    target = bpy.data.objects.new("target", None)
    bpy.context.collection.objects.link(target)
    target.location = center
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 85.0
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.constraints.new("TRACK_TO").target = target

    engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
    scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                           else "BLENDER_EEVEE")
    scene.render.resolution_x, scene.render.resolution_y = 560, 800
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
    except TypeError:
        pass

    out_dir = os.path.join(a.root, "qa", "shorts", a.id)
    os.makedirs(out_dir, exist_ok=True)
    dist_cam = height * 2.3
    for name, ang in (("0_frente", 0), ("1_lado", 90), ("2_costas", 180)):
        r = math.radians(ang)
        cam.location = center + Vector((math.sin(r) * dist_cam,
                                        -math.cos(r) * dist_cam, height * 0.02))
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(out_dir, name + ".png")
        bpy.ops.render.render(write_still=True)

    def _rng(v):
        v = v if isinstance(v, (list, tuple)) else [v]
        return "{:.3f}..{:.3f}".format(min(v), max(v))

    entry["frac"] = round(frac, 4)
    # POR PECA, nao o total: com duas pecas o total certo e 2, e um `islands > 1`
    # no relatorio acusaria a biblioteca feminina inteira. O `islands` continua
    # gravado para nao quebrar os 39 mapas masculinos que ja existem.
    entry["islands"] = len(comps)
    entry["por_peca"] = [len(t) for t in por_peca]
    entry["escondidas"] = escondidas
    entry["slivers"] = slivers
    entry["summary"] = "{}: roupa {:.1%} (+{} costura, -{} lasca)  bainha {} / {}  cos {}{}{}".format(
        a.id, frac, added, slivers, _rng(entry["hem_l_zh"]), _rng(entry["hem_r_zh"]),
        _rng(entry["waist_zh"]),
        "  faixa {} / {}".format(_rng(entry["faixa_lo_zh"]), _rng(entry["faixa_hi_zh"]))
        if "faixa_lo_zh" in entry else "",
        "  << ILHAS {}, pior {:.0%}".format(por_peca, biggest) if suspect else "")
    print("RESULT " + json.dumps(entry))
    sys.exit(0)


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker_main()
    else:
        sys.exit(driver_main())
