# Fila de correção das PEÇAS — a lista do Rogério, 11/08/2026

**Esta é a lista que a sessão 22 esperava e nunca tinha chegado.** Ela é o
produto: enquanto um item não for consertado E aprovado no olho dele, ele fica
aqui. Não varrer os outros avatares procurando defeito — o que não está nesta
lista não está na fila (regra §6.1, *um por vez é um por vez*).

---

## 1. TOPS FEMININOS — três classes, definidas por ele com screenshot

| classe | o que se vê | exemplo que ele mandou |
|---|---|---|
| **mínima** | uma **listra fina** não pintada na borda de cima do top | `b03_d3` |
| **mediana** | a listra é **maior** e ainda falta pintar **algum ponto** | `b06_d3` |
| **maior** | o top está **quase todo pintado errado** | `b08_d3` |

> A listra de cima é exatamente o defeito que a régua já denunciava sozinha:
> **a borda de CIMA da faixa não é medida em avatar nenhum** — de 4 a 9 dos 9
> setores frontais não têm aro (o busto apaga o vinco) e o traçado sai de ruído
> alisado pela mediana. `LICOES.md` §4.5b. Agora existem **duas linhas
> independentes apontando o mesmo lugar**: o sweep e o olho dele.

### mínimas (8)
`b01_d1` · `b01_d2` · `b02_d2` · `b02_d3` · `b03_d1` · `b03_d2` · `b04_d1` · `b05_d3`

### medianas (12)
`b04_d2` · `b04_d3` · `b04i_d1` · `b05_d2` · `b06_d1` · `b06_d2` · `b06_d3` ·
`b07_d1` · `b07_d3` · `b08_d1` · `b09_d1` · `b10_d3`

### maiores (10)
`b05_d1` · `b08_d3` · `b09_d2` · `b09h_d3` · `b09i_d2` · `b10_d1` · `b10_d2` ·
`b11_d1` · `b11_d2` · `b12_d1`

**30 dos 37**, todos com `zen_f_` na frente.

### ⚠️ Duas coisas a confirmar com ele antes de começar

1. **`b08_d3`, `b09h_d3` e `b09i_d2` aparecem NAS DUAS listas** (mediana e
   maior). Assumido: vale a **maior**, que é a menção mais recente. Confirmar.
2. **`b03_d3` é o exemplo que ele mandou de correção mínima, mas não está na
   lista.** Ou ele já está bom e a screenshot era só didática, ou faltou.
   Confirmar antes de mexer nele.

> 🔴 O `b08_d3` é o único avatar com a válvula `"faixa_topo_reto": true` no
> `config/shorts_map.json` — e é justamente o exemplo do defeito MAIOR. A
> hipótese óbvia a testar primeiro é que a válvula é a **causa** da classe
> maior, não o conserto.

---

## 2. SHORTS MASCULINOS — do `b09_d1` até o fim da escada

Ele listou por IMC medido:

| avatar | IMC |
|---|---:|
| `zen_m_b09_d1` | 63,2 |
| `zen_m_b09_d2` | 74,4 |
| `zen_m_b10_d1` | 83,6 |
| `zen_m_b10_d2` | 84,8 |
| `zen_m_b11_d1` | 107,3 |
| `zen_m_b11_d2` | 111,7 |
| `zen_m_b12_d1` | 147,7 |

**São 7, e são os sete mais pesados do acervo masculino** — todos fora da faixa
de usuário (17–40). Isso é informação: o detector do `shorts.py` foi calibrado
com corpo dentro da faixa, e a §3b do `CLAUDE.md` já avisa que *"achar o cós
projetando a imagem não sobrevive a corpo obeso: a barriga cai por cima do
cós"*. A fila dele confirma que a leitura pela malha também degrada no extremo.

⚠️ **Não confundir com a fila antiga dos 7 sem defeito medido** (`b07_d1`
`b07_d3` `b08_d1` `b08_d2` `b09_d2` `b10_d1` `b10_d2`). A interseção é
`b09_d2`, `b10_d1` e `b10_d2` — os outros quatro daquela fila **não** estão
nesta, e os quatro novos (`b09_d1`, `b11_d1`, `b11_d2`, `b12_d1`) nunca tinham
sido apontados.

---

## Ordem combinada

Ele disse: **"comece pelos tops femininos"**. Os shorts masculinos vêm depois.
