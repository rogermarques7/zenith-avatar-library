# Fila de correção das PEÇAS — a lista do Rogério, 11/08/2026

**Esta é a lista que a sessão 22 esperava e nunca tinha chegado.** Ela é o
produto: enquanto um item não for consertado E aprovado no olho dele, ele fica
aqui. Não varrer os outros avatares procurando defeito — o que não está nesta
lista não está na fila (regra §6.1, *um por vez é um por vez*).

---

## ✅ A PARTE 1 FOI ATACADA EM 11/08 (sessão 26) — os 37, não os 30

> Ele mandou **modo automático**: *"o máximo de avatares que conseguir, não
> precisa me mandar print, use o print pra você identificar os erros"*. Por isso
> o conserto foi no **detector**, e rodou nos 37 femininos — a classe de cada
> avatar deixou de importar, e **as duas confirmações abaixo ficaram sem efeito**
> (o `b03_d3` foi consertado junto; `b08_d3`/`b09h_d3`/`b09i_d2` também).
>
> **O que foi consertado:**
> - **A listra do topo** — a subida frontal virou modelada, ancorada na folha.
>   Erro contra a régua externa: **±0,002 em 37 de 37**. `LICOES.md` §4.5c.
> - **O dente na axila** — duas causas no `w_arm_wide`. `LICOES.md` §4.5d.
>
> 🔴 **O que NÃO fechou:** sobra um recorte pequeno na quina de baixo da faixa
> nos mais pesados — **`b09_d2` · `b10_d1` · `b11_d2` · `b12_d1` · `b07_d3`**.
> Diminuiu muito e **não tem régua externa**; é o olho dele que decide se volta
> para a fila. **Essa é a fila viva dos tops.**
>
> ⚠️ **Duas armadilhas desta rodada, e as duas já custaram um lote inteiro:**
> o veredito de pintura **não** se dá no render do `--fit` (é clay, não mostra a
> falta de tinta) — usar `qa/probe/sondas/render_dist.py`; e a régua da folha
> **passou verde com o avatar errado**, porque ela mede o pico e não a forma.

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

### ~~Duas coisas a confirmar com ele~~ — sem efeito desde 11/08

1. ~~`b08_d3`, `b09h_d3` e `b09i_d2` aparecem NAS DUAS listas.~~
2. ~~`b03_d3` é o exemplo de correção mínima mas não está na lista.~~

O conserto foi no detector e rodou nos 37, então nenhuma das duas mudou o que
foi feito. **Ficam registradas porque a pergunta era certa** — só deixou de
bloquear quando o método parou de ser por avatar.

> 🔴 ~~A válvula `faixa_topo_reto` é a causa da classe maior.~~ **Testada e
> refutada com medida (11/08):** tirar a válvula deixou o erro **idêntico**
> (−0,041 antes e depois) e trouxe de volta a cunha do esterno. Ela era o
> curativo, não a doença. E a classe "maior" não tem causa única — cinco dos dez
> mediam o topo **certo** e tinham o defeito da axila. `LICOES.md` §4.5c.

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

## ✅ A PARTE 2 FOI ATACADA EM 12/08 (sessão 27) — os 7, em modo automático

> A lista chegou **sem descrição de defeito** (a §1 tinha três classes com
> screenshot; esta não tem nada). O defeito é **preto pintado em cima da
> barriga**: o corte do short é por ALTURA e o avental desce abaixo dele.
>
> ⚠️ **A primeira leitura estava ao contrário** e gerou uma versão errada. O
> veredito dele, com print de 8 avatares: *"a tinta não segue o cós do short,
> você pinta em cima da barriga"*. `w_cos_avental` desce o cós da frente até o
> fundo da dobra (`nz <= -0,70`), só na frente e com rampa. `LICOES.md` §4.5e.
>
> ✅ **Aprovado por ele em 12/08** — *"melhorou bastante"*. Fechados: `b09_d1`
> `b09_d2` `b10_d1` `b10_d2` `b11_d2` `b08_d2`.
> **Pendentes:** `b11_d1` (melhora, não zera) e `b12_d1` (não se move — a frente
> já está no piso; falta print dele de frente).
> 🔴 **Ele diz que o mesmo defeito está nas femininas** — não medido.

---

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

Ele disse: **"comece pelos tops femininos"** — feito na sessão 26. Os shorts
masculinos vieram depois, na 27.

➡️ **A próxima é a PARTE DE BAIXO do short (a bainha)**, marcada por ele em
12/08. E fora da fila continuam: `b11_d1` e `b12_d1` (o cós, que não zerou) e o
mesmo defeito de cós **nas 37 femininas**, que ele apontou e ainda não foi
medido.
