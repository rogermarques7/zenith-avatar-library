# Fila de correção das PEÇAS — a lista do Rogério

**A fila é o produto**: enquanto um item não for consertado E aprovado no olho
dele, ele fica aqui. Não varrer os outros avatares procurando defeito — o que
não está nesta lista não está na fila (regra §6.1, *um por vez é um por vez*).

> # 🔴 A FILA VIVA DE HOJE ESTÁ EM OUTRO ARQUIVO
>
> **`docs/REVISAO_ROUPA_2026-09-23.md`** — ele navegou os 103 no testador em
> 23/09 e ditou defeito por defeito: **20 dos 27 novos** com pelo menos um, em
> quatro classes. A maior é **tinta além do limite da barra da perna**, e sobre
> ela ele deu ordem explícita de **revisão completa do acervo, novos e antigos,
> em sessão dedicada**. Abrir aquele arquivo antes de qualquer conserto de peça.
>
> O que está abaixo neste arquivo é o histórico das rodadas anteriores.

## 🔴 SESSÃO 37 (23–24/09) — O CÓS FOI APLICADO E REPROVADO; A BAINHA NÃO FOI TOCADA

Modo automático pedido por ele: *"atue automaticamente pra corrigir as peças de
roupas nessa sessão, até amanhã"*. **A frente continua ABERTA.**

### ⚠️ 1. O CÓS — 12 regravados, e a maioria voltou reprovada

Ancorei o arco da frente na FOLHA e alisei com `w_waist_liso`. Contra a folha os
números fecharam (o `zen_f_b03h_d1` foi de −0,063 para −0,001). **No testador:**

```
m: b07k_d1 (cós + barra) · b07j_d1 (cós, "faixa branca no cinto")
   b06_d3 (falta tinta na barra) · b05n_d1 (recorte abaixo da barriga errado)
f: b03h_d1, b05h_d2, b07h_d1, b07i_d1  (todos "falta tinta no short")
   b07j_d1 (tinta no tríceps) · b09j_d1 (tinta na barriga)
```

🔴 **A folha é MENOR que o tecido que a Meshy modelou** — e eu tinha acabado de
escrever isso sobre a faixa (`LICOES.md` §4.5l) sem aplicar ao cós. As três
bordas (cós, bainha, topo da faixa) são o mesmo defeito.

**Os 12 que foram regravados** (só `waist_zh`, nenhuma bainha tocada):

```
f: b03h_d1 b05h_d1 b05h_d2 b05i_d2 b07h_d1 b08_d2 b09i_d1 b09j_d1
m: b07i_d1 b07j_d1 b07k_d1 b10i_d2
```

### 🔬 2. A BAINHA — mecanismo provado, detector não resolvido, ZERO GLB tocado

✅ Provado por imagem e **validado no olho dele**: a bainha modelada está acima
da tinta em praticamente todo o acervo, de 0,5 cm a quase 7 cm.

```
vinco − tinta   mediana +0,0107 da altura = 1,9 cm
vinco − folha   mediana +0,0058           = 1,0 cm
```

🔴 **Cinco tentativas de detector, cinco mortes.** A quinta (anel fechado)
morreu porque **a virilha também é um anel fechado** — a prega inguinal e o
sulco glúteo são as duas metades dela. `LICOES.md` §4.5n.

### ➡️ 3. O QUE A PRÓXIMA SESSÃO FAZ — decisão dele

> **Ler a barra na FOLHA, vista de COSTAS, pelo CONTORNO da divisa de cor.**
> Ali não existe vinco de pele para confundir. A altura fica amarrada no clay da
> frente, que é onde o tecido de verdade está.

⚠️ **EXCEÇÃO REGISTRADA EM 22/09: ele pediu a varredura.** *"aproveita e dá uma
revisada nos antigos pois alguns possuem defeitos ainda"*, com 10 h de trabalho
sozinho. A regra continua valendo por padrão — **varrer só quando ele mandar
varrer**, e o instrumento dessa vez foi o `revisao_peca.py --mosaico`, que
renderiza o GLB entregue e põe 6 por imagem.

➡️ **Começar pelo fim do arquivo**: a seção *"Ordem combinada, e o que sobrou"*
tem a tabela das frentes e os itens que continuam abertos. O resto é o histórico
de cada rodada, com o placar medido.

**Ele manda a fila por PRINT do testador**, não por lista de texto — e os prints
vêm com o cursor do mouse em cima do defeito. Quando a descrição não vem junto,
**pedir**: em 12/08 a lista chegou sem descrição, eu li o sinal ao contrário e
gravei uma versão errada (`LICOES.md` §4.5e).

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

## Ordem combinada, e o que sobrou (atualizado em 22/09)

| # | frente | sessão | estado |
|---|---|---|---|
| 1 | tops femininos — listra do topo e dente na axila | 26 | ✅ fechada |
| 2 | shorts masculinos — cós-avental | 27 | ✅ fechada, aprovada por ele |
| 3 | bainha (parte de baixo do short) | 28 · 13/08 | ❌ **revertida inteira** |
| 4 | cós-avental feminino | 29 | ✅ fechada na 30 |
| 5 | quina do cós — a poligonal | 30 · 15/08 | ✅ fechada, 7 avatares |
| 6 | quina da faixa — máscara do braço | 30 · 15/08 | ✅ fechada, 23 avatares |
| 7 | **vestir os 27 corpos novos** | 36 · 22/09 | ✅ fechada, 27 avatares |
| 8 | **o buraco na curva do braço** — a cunha preta na quina | 36 · 22/09 | ✅ fechada, 37 femininos |

## 🆕 SESSÃO 36 (22/09) — OS 27 NOVOS VESTIDOS, E A CUNHA DA QUINA

Modo automático pedido por ele: *"atue automaticamente no conserto das roupas…
aproveita e dá uma revisada nos antigos pois alguns possuem defeitos ainda"*.
Duas frentes numa: **vestir** o que nunca teve peça e **revisar** o acervo.

### 1. Os 27 que não tinham roupa nenhuma

18 femininos e 9 masculinos, todos ainda em `_v1.glb`. O `--fit` correu limpo nos
27, mas a **régua externa achou um defeito que o detector não acusa**: em 7
femininos a bainha do 3D erra de −0,027 a −0,070 contra a corrida escura da folha
(`faixa_ref.py`), enquanto os outros 11 erram no máximo 0,013.

🔴 **É o modo de falha do `_set_virilha.py` de novo**: o `w_limbs` acha a fusão
das COXAS e chama de virilha, e a virilha ancora as duas janelas. Desta vez ele
foi **procurado** em vez de tropeçado — a separação entre os dois grupos é
inequívoca e a régua da folha é quem a faz.

Corrigidos pela mesma regra de sempre (pico mais forte do anel do TRONCO entre
0,33 e 0,55, mais 0,0045 — **do anel, nunca da folha**, senão a folha deixa de
conferir). Erro máximo contra a folha depois: **0,0085**, abaixo dos 0,013 da
primeira leva. Tabela no docstring do `_set_virilha.py`.

Resultado: `b08_d2` −0,070 → **+0,001** · `b08h_d2` −0,051 → **+0,003** ·
`b09i_d3` −0,057 → **−0,002** · `b11h_d1` −0,060 → **+0,007** · `b12h_d1` −0,027
→ **−0,001** · `b05i_d2` e `b07h_d2` idem.

O `faixa_topo_frente_zh` da folha foi gravado nos **55** femininos (37 + 18).

### 2. A cunha preta na quina da faixa — e por que a fila a chamava de franja

A fila viva dizia *"sobra ~1 triângulo de franja… visível só em ângulo rasante"*.
No GLB entregue, com material e HDR, ela é **maior que isso**: uma aba preta na
quina da faixa, visível de costas e de 3/4 em **todas as femininas pesadas**
(`b12_d1`, `b11_d1`, `b11_d2`, `b10_d1`, `b09_d2`, `b05_d1`).

🔴 **Duas hipóteses minhas morreram antes da certa, e as duas por medida:**

1. *"É o `ARM_COL_OUT`, que empurra o corte 1 coluna para fora."* Não: ele só
   entra no `_arm_cut_prof`, o plano B. O `vão` decide a maioria das fatias.
2. *"É a parábola saindo mais lateral que a medida crua."* Medido: a tira entre
   as duas existe em **4 fatias de 21** no `b12_d1`, e a aba cobre a faixa
   inteira. A PASSADA 4 (normal) que nasceu dessa hipótese mexe em **2 vértices**.

✅ **A causa apareceu quando a máscara foi PINTADA DE VERMELHO** — sonda nova
`faixa_tres_cores.py`. Preto é roupa, vermelho é máscara de braço, cinza é corpo:
a máscara cobria o braço em 20 das 21 fatias e **faltava exatamente uma**
(`b12_d1` zh 0,765 à direita; `b11_d2` zh 0,725 à direita). E fatia sem corte não
é "fatia sem braço": é fatia que **não mascara nada**, então a faixa sai pintada
de ponta a ponta ali, braço incluso.

O banco de duas cores não podia achar isso: ele mostra o resultado e esconde a
causa — preto sobrando pode ser máscara que não alcançou ou máscara que não
existe, e as duas pedem consertos opostos.

✅ **Conserto: preencher o BURACO INTERIOR da curva pela própria parábola.** A
ressalva antiga (*"preencher os `None` inventaria braço"*) continua valendo para
o que ela diz de verdade — **não se extrapola**: fora do intervalo entre a
primeira e a última fatia com corte, nada é inventado. Dentro dele é
**interpolação entre duas vizinhas que mediram**, que é afirmação muito mais
fraca, e a parábola já é a forma dessa fronteira.

🔴 **E O DEFEITO VISÍVEL NÃO EXISTIA — ERA PERSPECTIVA.** Aplicado o conserto, o
A/B recortado na mesma câmera deu **imagem igual**. Com **lente de 300 mm a 6 m**
a faixa é uma barra horizontal limpa de ponta a ponta: a aba era o **braço**,
mais perto da câmera, projetando o mesmo corte horizontal mais baixo e mais
grosso, com a silhueta dele recortando a faixa por cima. A tinta está no tronco,
e sempre esteve.

**Saldo honesto desta frente:** o buraco na curva era real e está consertado
(máscara 611 → 620 no `b12_d1`, 541 → 554 no `b11_d2`, nenhuma fatia sem corte),
**e é invisível no entregue** — custou uma versão de GLB em 37 femininas. O
defeito que motivou a investigação não era defeito. `LICOES.md` §4.5h.

⚠️ **Regra nova para esta fila:** num corpo largo, defeito perto da silhueta
lateral só entra na fila depois de reproduzir com **lente longa**. O
enquadramento apertado que faz uma tira de 1 cm aparecer é o mesmo que faz a
perspectiva dominar.

### 3. 🔴 O DEFEITO QUE A VARREDURA REALMENTE ACHOU — o cós MERGULHA na frente

Visível de frente, grande, e em **seis avatares da leva nova**: o cós desce em V
até a virilha e o short vira **cavada de biquíni**, com tecido modelado sem
pintura acima do preto.

`zen_f_b05h_d2` · `zen_f_b05i_d2` · `zen_f_b08_d2` · `zen_f_b07h_d1` ·
`zen_m_b10i_d2` · `zen_m_b07i_d1`

**A régua que separa é a queda contra o ANEL medido**, não a amplitude da curva
(amplitude alta em corpo pesado é a barriga caindo, e é o certo):

| | queda `waist_ring_zh − min(waist_zh)` |
|---|---:|
| mediana do acervo | 0,029 |
| teto da série sã | 0,046 |
| **os seis** | **0,075 a 0,108** |

O `zen_m_b12_d1` dá 0,168 e **não entra**: nele a queda é a barriga de verdade.

✅ **Consertado:** cós **escalar na altura do anel que a malha mediu**, com
`source: manual` — a correção barata que o `shorts.py` já previa. A folha
confirma cós horizontal logo abaixo do umbigo nos seis. Conferido no GLB
entregue: `b05i_d2` e `b07h_d1` saíram com short de verdade.

⚠️ **A janela do `w_waist_curve` NÃO foi mexida.** A causa é ela achar
concavidade mais forte na virilha que no cós nesses corpos, mas o piso da janela
é global: mexer nele mexe nos 103 para consertar 6. Frente própria, com a régua
de queda já pronta. `LICOES.md` §4.5i.

🔴 **E a trava já apontava.** O `--report` marcava `CANTO0.023` no `b05i_d2`
desde o primeiro `--fit`, no meio de uma lista de **52 ids** em `conferir:`.
Trava que aponta 52 avatares não aponta nenhum — quem achou foi a imagem do
entregue.

### 🔴 A FILA VIVA — três itens, todos esperando decisão dele

1. ✅ ~~A trava `CANTO` reprova 3 femininos e 11 masculinos~~ **rodada nos 14 em
   16/08, por decisão dele.** Sobraram **3**, e eles NÃO são para consertar:
   `zen_m_b12_d1` 0,042 · `b11_d2` 0,022 · `b11_d1` 0,021 — nos três o cós
   encosta no **piso da bainha** e a curva achata contra ele; a quina é a entrada
   nesse platô, não defeito do detector. Iterar o filtro até passar derrubaria a
   curva 2,4 cm para esconder geometria.
   ⚠️ **6 dos 14 estavam `source: manual`** — o que é manual neles é a BAINHA, e
   um `--refit` a teria descartado. Para esses o alisamento vai por
   `cos_liso_mapa.py --escrever`, que só toca o `waist_zh`.
2. ✅ ~~A franja de ~1 triângulo na quina onde a faixa encontra a face interna do
   braço~~ **atacada em 22/09 e ela não era franja: era uma fatia sem corte.**
   Ver a sessão 36 acima. Sobra a cunha da região fundida, que é escolha e não
   detecção. A ideia antiga registrada aqui — *"a máscara é aplicada por FACE
   enquanto as bordas por altura passam pelo corte exato"* — **continua de pé e
   continua não tentada**; ela deixou de ser a explicação do defeito visível,
   mas segue sendo o caminho para a borda ficar exata como a do cós.
3. **A BAINHA continua sem conserto.** Atacada em 13/08 e **revertida inteira** a
   pedido dele; o que sobrou é o registro dos erros no `LICOES.md` §1.10 e §1.11,
   **inclusive as quatro hipóteses testadas e mortas**. Ler antes de reabrir —
   sem sinal novo, tentar de novo repete a mesma lição.

⚠️ Fora da fila de peças, mas do mesmo acervo: o `zen_m_b12_d1` **não se move**
(a frente dele já está no piso da bainha — limite de forma do corpo, não bug) e
o `zen_m_b11_d1` melhora e não zera.

## 🟡 O COS-AVENTAL NAS FEMININAS FOI APLICADO EM 6 (13/08) — 2 limpos, 2 com defeito novo, esperando o olho dele

"Ele diz que o mesmo defeito está nas femininas" virou número, e depois virou
conserto de verdade. Medido com `w_cos_avental` (o mesmo detector do
masculino) em 9 avatares pesados — **o efeito NÃO segue o IMC**, segue a forma
da barriga (`b09_d2` IMC 53,9 deu zero cm, `b08_d1` IMC 42,6 deu 4,9 cm):

| avatar | IMC | descida pedida | aplicado? |
|---|---:|---:|---|
| `zen_f_b12_d1` | 114,2 | 11,9 cm | ✅ v10 |
| `zen_f_b11_d1` | 52,5 | 10,5 cm | ✅ v10 |
| `zen_f_b11_d2` | 59,7 | 6,3 cm | ✅ v10 |
| `zen_f_b08_d1` | 42,6 | 4,9 cm | ✅ v10 |
| `zen_f_b10_d1` | 55,1 | 2,1 cm | ✅ v10 |
| `zen_f_b10_d2` | 52,6 | 2,1 cm | ✅ v10 |
| `zen_f_b09_d2` | 53,9 | 0,0 cm | — sem efeito, não aplicado |
| `zen_f_b10_d3` | 45,1 | 0,0 cm | — sem efeito, não aplicado |
| `zen_f_b05_d1` | 44,4 | 0,0 cm | — sem efeito, não aplicado |

Aplicado com `shorts.py --apply` + `morph.py --apply` por cima (regra 9), os 6
em **v10**. Réguas depois do lote: `probe_material_dist` 76/76 ·
`shorts --check --all` 76/76 · `select --check` 34/34 · `morph_cases --check`
608/608 — tudo limpo.

🔴 **Mas régua não é veredito de pintura/geometria fina — isso é olho, e é
dele.** Renderizado o GLB entregue com material+HDR reais
(`qa/look/cos_feminino/`):

- **`b12_d1` e `b11_d2` saíram limpos** — o cós acompanha a barriga até a
  virilha, sem serrilha.
- **`b11_d1` e `b08_d1` saíram com um degrau anguloso visível** na virada do
  cós — a descida por 24 setores de azimute ficou em zigue-zague nesses dois
  corpos específicos (`b11_d1` já tinha `DEGRAU0.092` no `--report` antes
  disso, então não é surpresa total). Não é a listra do topo (defeito já
  conhecido); é um defeito novo, forma de dente de serra.

**Fila viva:** `b11_d1` e `b08_d1` esperando decisão — aceitar como está,
reprovar (some a fila de novo), ou tentar suavizar mais a transição entre
setores (não tentado ainda, candidato óbvio é abrir a mediana móvel de 3 que
já suaviza o resto da curva). `b09_d2`, `b10_d3` e `b05_d1` não precisam de
nada — o detector não achou avental neles.

Resto da faixa pesada (IMC ≥ 28, ~10 avatares) ainda não foi medido —
continua o próximo passo óbvio quando a frente reabrir.

## ✅ A QUINA DO CÓS FEMININO — 7 CONSERTADOS EM 15/08 (sessão 30)

Ele mandou **7 prints do testador com o cursor em cima do defeito**, em modo
automático: *"a maioria é defeito na parte de cima do short"*. Esta lista
substitui a fila viva do cós feminino de 13/08 — `b11_d1` e `b08_d1` estavam
nela e foram fechados aqui.

| avatar | IMC | canto antes | canto depois | GLB |
|---|---:|---:|---:|---|
| `zen_f_b11_d1` | 52,5 | **0,092** (parede de 16 cm no flanco) | 0,015 | v17 |
| `zen_f_b12_d1` | 114,2 | 0,037 | 0,014 | v17 |
| `zen_f_b10_d1` | 55,1 | 0,029 | 0,009 | v17 |
| `zen_f_b06_d1` | 32,4 | 0,025 | 0,007 | v15 |
| `zen_f_b08_d1` | 42,6 | 0,023 | 0,011 | v19 |
| `zen_f_b09_d2` | 53,9 | 0,021 | 0,007 | v14 |
| `zen_f_b11_d2` | 59,7 | 0,020 | 0,010 | v17 |

O defeito é **um só nos sete**: a borda de cima do short é uma poligonal —
parede, cunha, tala diagonal ou quina, conforme o corpo. O conserto é
`w_waist_liso` (alisamento circular com teto) e a trava nova é `CANTO`, a
segunda diferença da curva. **`DEGRAU` passava limpa em 6 dos 7** porque ela
mede inclinação, e o que se vê é a mudança dela. `LICOES.md` §4.5f.

🔴 **A trava nova reprova mais gente, e é honesto:** `b06h_d3` (0,029),
`b10_d3` (0,025) e `b10_d2` (0,021) do lado feminino, e **11 masculinos** (até
0,121 no `b12_d1`). Ele mandou "os 7 com defeito **mais** visível", não "os 7
únicos". Nenhum desses foi tocado — é decisão dele se entram na fila.

## ✅ O RECORTE NA QUINA DA FAIXA — FECHADO EM 15/08 (sessão 30)

A fila viva dos tops desde 11/08 (*"sobra um recorte pequeno na quina de baixo
da faixa… é o olho dele que decide se volta para a fila"*). **Voltou:** ele
mandou 3 prints — `b09_d2`, `b10_d1`, `b05_d1` — com *"os tops que faltam
colorir"*.

**Não era a faixa, era a máscara do braço.** `w_arm_wide` cortava braço/tronco
por "60% da profundidade máxima da fatia", e num corpo com busto essa barra é
alta demais: o flanco do tronco, que é raso, não a alcança e vira braço. No
`b10_d1` o corte caía **4,2 cm dentro do tronco**.

Dois consertos, e cada um pega um defeito diferente:

- **o vão de ar** (`_arm_cut_vao`) — acima da fusão existe ar entre braço e
  tronco em toda fatia da banda, e ar é sinal binário. O critério antigo virou
  plano B para onde o braço encosta mesmo.
- **a parábola** — o corte cru varia ±2 cm entre fatias vizinhas de 0,9 cm; a
  mediana de 5 mata o disparo mas preserva degrau, e o que sobra é a borda
  serrilhada. É a §4.5f num eixo diferente.

Tronco indevidamente mascarado, dentro da banda: `b09_d2` 514 → 0 · `b10_d1`
504 → 0 · `b05_d1` 140 → 0. **23 dos 37 mudaram de fato** e foram regravados;
14 saem bit a bit idênticos e não gastaram versão. O magro `b01_d1` — a
regressão a vigiar, porque a primeira versão do `w_arm_wide` o quebrou em 11/08
— não mudou um vértice. `LICOES.md` §4.5g.

## 🖼️ O print de frente do `b12_d1` (masculino) chegou — via render_dist.py

Pendência antiga ("falta print dele de frente"). Renderizado o GLB entregue
com material e HDR de produção (`qa/look/zen_m_b12_d1/cos.png`, mira em 0,46
da altura). **Confirma "não se move": a barriga cobre o cós nos lados, mas no
centro há uma fresta de pele exposta bem onde a barriga encontra as coxas** —
o cós já está no piso da bainha ali, geometricamente não tem mais para onde
descer sem entrar na própria bainha. Não é bug do detector; é limite de forma
do corpo. Precisa de decisão dele: aceitar a fresta residual, ou tentar uma
abordagem que mexa também na bainha (frente parada, ver acima).
