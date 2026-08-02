"""Grava crotch_override_zh nos femininos de virilha baixa demais.

POR QUE SAO ONZE, e nao um. O w_limbs define a virilha como o primeiro evento
grande de fusao das duas pernas subindo do chao - "onde as pernas param de se
tocar". Em corpo magro isso E a virilha; em corpo pesado as coxas se encostam
bem abaixo dela, e o evento acontece na coxa. O modo de falha ja estava escrito
no shorts.py para o zen_m_b12_d1; o que nao se sabia e que ele nao e uma
excecao de IMC 148, e sim uma FUNCAO do IMC - ele pega 11 das 37 femininas, de
IMC 31,9 para cima, e a virilha erra de 0.05 a 0.14 da altura.

Isso importa mais do que parece porque a virilha ancora as DUAS janelas, a da
bainha e a do cos. Com ela baixa, o short inteiro desce: medido contra a folha
(faixa_ref.py), o b12_d1 saiu com cos -0.176 e bainha -0.148, ou seja uns 25 cm
fora do lugar num avatar de 1,70 m.

DE ONDE VEM CADA NUMERO. Do anel do TRONCO, nao da folha, e a ordem e o ponto:
a folha e a regua externa do short, e se ela passar a fornecer o valor que
ancora o detector, ela deixa de conferir coisa nenhuma justo nos 11 avatares
mais problematicos (LICOES 1.3). A regra e "pico mais forte do anel entre 0.33
e 0.55, mais 0.0045", e o vies de 0.0045 foi calibrado nos 23 avatares em que a
virilha ja e confiavel (desvio 0.0074). So DEPOIS a folha entra: os 11 batem
com ela dentro de 0.013.

Dois nao seguiram a regra, e por evidencia:

  b06_d1   dois picos fortes, 0.229@0.4146 e 0.192@0.4521. O mais forte e o de
           baixo e a folha aponta o de cima (0.4616): 0.4521+0.0045 erra -0.005,
           0.4146+0.0045 erra -0.043. Encosta no segundo pico - continua sendo
           medida de malha, so nao e a que a regra escolheria.
  b10_d3   nenhum pico forte: o maior no trecho e 0.042, contra 0.1-0.2 dos
           outros. Os candidatos fortes ficam em 0.335 e 0.356, que sao vinco de
           coxa. Ha um pico FRACO em 0.4562 (forca 0.009, abaixo do piso de
           0.015 da regra) e e ele que bate com a folha (-0.005). Evidencia mais
           fraca que as outras dez, e anotada como tal.

NAO corrigidos, de proposito:

  b11_d1   a virilha dele ja esta certa (0.4072) e a folha confirma o short nas
           duas bordas (-0.003 / +0.002). Ele entrou na lista de suspeitos por
           artefato da minha triagem, que comparou o cos pelo MAXIMO da curva em
           vez da mediana do setor de costas; num corpo de IMC 52 a curva sobe
           0.13 do setor da frente ao de tras e o maximo estoura qualquer
           limiar. Corrigir aqui quebraria o unico pesado que esta bom.
  b08h_d3  virilha praticamente identica a proposta (0.4790 x 0.4815). A bainha
           baixa dele e do RECUO, nao da ancora, e o recuo foi corrigido no
           shorts.py (HEM_RECUO_F).
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
MAPA = os.path.join(ROOT, "config", "shorts_map.json")

CORRECOES = {
    "zen_f_b07_d1": 0.4649,
    "zen_f_b06_d1": 0.4566,   # 2o pico
    "zen_f_b09_d1": 0.4565,
    "zen_f_b08_d1": 0.4149,
    "zen_f_b05_d1": 0.4357,
    "zen_f_b10_d3": 0.4607,   # pico fraco
    "zen_f_b10_d2": 0.4524,
    "zen_f_b09_d2": 0.4565,
    "zen_f_b10_d1": 0.4524,
    "zen_f_b11_d2": 0.4565,
    "zen_f_b12_d1": 0.4065,
}

with open(MAPA, "r", encoding="utf-8") as f:
    m = json.load(f)

for aid, v in CORRECOES.items():
    e = m[aid]
    print("%-15s virilha %.4f -> %.4f" % (aid, e["diag"]["crotch_zh"], v))
    e["crotch_override_zh"] = v
    e["source"] = "manual"

with open(MAPA, "w", encoding="utf-8") as f:
    json.dump(m, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("gravado: config/shorts_map.json  (rode --fit --refit nos 11)")
