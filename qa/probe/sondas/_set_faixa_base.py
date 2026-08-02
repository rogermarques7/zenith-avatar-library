"""Grava as correcoes manuais de ancora da faixa no shorts_map.json.

CADA VALOR AQUI E UM PICO QUE O DETECTOR VIU, nao um numero copiado da folha -
com uma excecao, anotada. O criterio foi: o prior gaussiano preteriu um pico
mais fraco que a regua externa confirma? Entao a correcao e encostar naquele
pico, e continua sendo medida de malha. Ver qa/probe/sondas/_base_picos.py, que
imprime os picos ao lado da folha.

  b05_d1   picos 0.6521(0.142) e 0.6771(0.110); folha 0.654. O prior, centrado
           em 0.672, ficou com o de cima. O de baixo e o mais forte E o que a
           folha confirma (-0.002). Caso ideal.
  b04_d3   picos 0.6521(0.023) e 0.6687(0.017); folha 0.667. Os dois sao fracos
           e o prior decidiu por uma margem minima (0.0185 x 0.0169). A folha
           aponta o segundo (+0.002). E o unico com FRENTEv9 - a curva da frente
           tinha desabado abaixo do anel das costas -, e por isso a ancora nova
           precisa RETRACAR a curva em vez de deslocar a antiga.
  b09_d2   picos 0.6937(0.150) e 0.6771(0.054); folha 0.663. Nenhum bate com a
           folha, mas o de baixo erra +0.014 contra +0.031 do escolhido.
           Correcao parcial, e assumida como tal.
  b09i_d2  UNICO pico da janela em 0.6979, e ele encostou no teto (BORDA-BASE):
           quem decidiu foi o limite da janela, nao o vinco. Nao ha pico para
           onde ir, entao aqui - e so aqui - o valor e o da folha. Evidencia
           mais fraca que as outras tres.

NAO corrigidos de proposito: b11_d2 (+0.018) e b10_d3 (+0.015). Os dois tem UM
pico, forte (0.193 e 0.116), e nenhum concorrente. Discordancia de folha nessa
ordem cabe no ruido do modelo, cujo erro maximo e 0.031, e a propria faixa_ref
avisa que a Meshy reinterpreta proporcao - ela acha erro grosso, nao centesimo.
Trocar medida de malha por numero de folha sem um pico que sustente seria
inverter a ordem das reguas.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
MAPA = os.path.join(ROOT, "config", "shorts_map.json")

CORRECOES = {
    "zen_f_b05_d1": 0.6521,
    "zen_f_b04_d3": 0.6687,
    "zen_f_b09_d2": 0.6771,
    "zen_f_b09i_d2": 0.6670,
}

with open(MAPA, "r", encoding="utf-8") as f:
    m = json.load(f)

for aid, base in CORRECOES.items():
    e = m[aid]
    print("%-14s %.4f -> %.4f" % (aid, e["faixa_lo_zh"], base))
    e["faixa_base_override_zh"] = base
    e["source"] = "manual"

with open(MAPA, "w", encoding="utf-8") as f:
    json.dump(m, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("gravado: config/shorts_map.json  (rode --fit --refit nos 4)")
