# Cobertura por FORMA de corpo — o que falta, medido

**Criado em 14/09/2026, sessão 32.** Nasceu de duas coisas que se encontraram: o
corpo da **Joice** (sessão 31, o segundo corpo real medido do projeto) não existir
na biblioteca, e o handoff `handoff_biblioteca_corpos_faltando.md` contar buracos
**só no eixo de IMC**.

> ⚠️ **Este arquivo NÃO substitui o handoff.** Ele cobre o eixo que o handoff não
> vê. Os dois valem juntos: o handoff diz *onde falta TAMANHO*, este diz *onde
> falta FORMA*. Um corpo novo costuma fechar uma célula de cada.

---

## 1. Por que a grade de IMC é cega para isto

A grade (`ARCHETYPES.md` §2) indexa **tamanho**: 12 bandas de IMC × 3 níveis de
definição. Mas a seleção do app **não usa a grade** — desde o schema 4 ela é
distância ponderada de **9 circunferências**, com `cintura 3,0 · quadril 2,0 ·
peito 2,0 · ombro 2,0`.

Ou seja: **quatro dos cinco pesos da seleção descrevem a forma do tronco**, e o
eixo em que eles vivem não aparece em lugar nenhum da grade. Dois corpos de IMC
25 com cinturas diferentes não são substituíveis — `LICOES.md` §2.2c já media
isso ("dá para mover FORMA sem mover IMC"), e o custo apareceu em gente real:

> A Joice (IMC 24,6) caía num avatar de **IMC medido 34,1**, com o quadril
> errando **26,6 cm**. Depois da correção da coluna de cintura, caiu em 26,5 — e
> **o quadril continuou errado**, porque o corpo dela não existe.

🔴 **E o morph não fecha forma.** Ele é radial uniforme: **preserva** a seção
(§7.19 e o bloco de 06/08 do `state.md`). Fechar centímetro de perímetro num
corpo da forma errada custa profundidade e entrega um corpo mais parecido com o
que já estava lá. Forma é produção na Meshy, não código.

---

## 2. A régua — e ela é discutível de propósito

Duas razões, as duas já publicadas no `library.json`:

```
WHR = waist_navel / hip          (a coluna que a seleção usa desde 21/08)
SHR = shoulder    / hip
```

| forma | feminino | masculino |
|---|---|---|
| **Maçã / oval** | WHR ≥ 0,90 | WHR ≥ 0,98 |
| **Triângulo invertido / V** | SHR ≥ 1,05 | SHR ≥ 1,25 |
| **Pera / triângulo** | SHR < 0,95 | SHR < 1,05 |
| **Ampulheta** | SHR 0,95–1,05 **e** WHR ≤ 0,78 | SHR 1,05–1,25 **e** WHR ≤ 0,80 |
| **Retângulo** | SHR 0,95–1,05 **e** WHR > 0,78 | SHR 1,05–1,25 **e** WHR > 0,80 |

⚠️ **Os cortes são arbitrados, não medidos.** Os limiares vêm da tipologia
corrente de vestuário, não de dado deste projeto — mudá-los remapeia as tabelas
abaixo. O que **não** é arbitrário é a distribuição: as células com **zero** têm
zero com qualquer corte razoável.

⚠️ **WHR pelo UMBIGO, não pela mínima.** É a coluna que a seleção consome desde
21/08, e é onde a pessoa põe a fita. Pela mínima a coleção feminina parece ainda
mais ampulheta (mediana 0,654 contra 0,753) — o que é justamente o viés de
+13,7 cm que custou o avatar da Joice.

---

## 3. O que existe hoje — 76 corpos, faixa de usuário (IMC 17–40)

### FEMININO (24 na faixa)

| forma | quantos | IMC coberto |
|---|---:|---|
| Pera / triângulo | **13** | 19,8 → 34,4, denso |
| Ampulheta | **10** | 17,2 → 22,3 · 28,4 → 30,1 |
| Triângulo invertido | **1** | só 32,4 (`b09_d3`, fisiculturista) |
| **Retângulo** | **0** | 🔴 |
| **Maçã / oval** | **0** | 🔴 |

### MASCULINO (27 na faixa)

| forma | quantos | IMC coberto |
|---|---:|---|
| Retângulo | **12** | 18,0 → 38,4, denso |
| Ampulheta | **6** | só 19,7 → 23,8 |
| V / triângulo invertido | **6** | 20,8 → 35,7, **todos `d3`** |
| Maçã / oval | **3** | só 33,3 · 38,9 · 39,9 |
| **Pera / triângulo** | **0** | 🔴 |

**Leitura:** cada coleção cobre bem **duas** formas e ignora as outras três. O
masculino é um bloco de retângulos com uma cauda de V atlético; o feminino é um
bloco de peras com uma cauda de ampulhetas atléticas.

---

## 4. 🇧🇷 O CASO BRASILEIRO — cintura fina + glúteo largo **existe, mas só de atleta**

Pergunta do Rogério em 14/09, e a medida responde direto. Os 8 corpos femininos
de menor WHR:

| id | def | IMC | WHR | quadril |
|---|---|---:|---:|---:|
| `b08h_d3` | d3 | 29,0 | 0,661 | 124,5 |
| `b04_d3` | d3 | 29,9 | 0,675 | 125,1 |
| `b08_d3` | d3 | 28,4 | 0,694 | 120,4 |
| `b03_d2` | **d2** | **19,8** | 0,701 | 101,7 |
| `b05_d3` | d3 | 21,0 | 0,704 | 106,9 |
| `b06h_d3` | d3 | 22,3 | 0,719 | 109,2 |
| `b03_d1` | **d1** | **19,0** | 0,719 | 99,1 |
| `b07_d3` | d3 | 27,7 | 0,721 | 122,7 |

**Seis dos oito são `d3`**, e os dois que não são estão abaixo de IMC 20. Entre
IMC 23 e 31, o menor WHR fora da linha atlética é **0,765** (`b06_d2`).

🔴 **A célula que falta: mulher comum (`d1`/`d2`), IMC 24–30, WHR ≤ 0,72, quadril
≥ 118 cm.** Cintura fina e glúteo/quadril largos **sem** abdômen de palco, sem
separação muscular, com tecido macio. Hoje: **zero corpos.** Quem tem esse corpo
recebe hoje ou uma atleta de wellness (definição que ela não tem) ou uma pera
genérica de cintura 10 cm mais larga.

É provavelmente a célula de maior população da base brasileira, e ela some na
grade de IMC porque **não é um buraco de tamanho** — é um buraco de forma dentro
de uma banda que a grade marca como ✅.

---

## 5. 📋 A LISTA — femininos primeiro (decisão dele, 14/09)

Passo de ~3 de IMC dentro de cada forma. Não é a grade de 1,5 do handoff: o
morph fecha resíduo de **tamanho** dentro de uma forma; o que ele não faz é
trocar de forma.

### 1ª onda — FEMININO, 17 corpos · ✅ **FECHADA em 17/09 — 17 de 17**

| # | forma | alvo IMC | def | WHR alvo | SHR alvo | estado |
|---|---|---:|---|---|---|---|
| **A1** | **Retângulo / reto** | **26** | d1 | ≥ 0,88 | ≥ 1,03 | ✅ `zen_f_b07i_d1` 27,9 · WHR 0,923 · SHR 1,009 |
| A2 | Retângulo | 23 | d2 | ≥ 0,85 | ≥ 1,00 | ✅ `zen_f_b05h_d1` 24,7 · WHR 0,905 · SHR 0,984 |
| A3 | Retângulo | 29 | d1 | ≥ 0,88 | ≥ 1,00 | ⚠️ na prática coberto pelo A1 (27,9) |
| A4 | Retângulo | 20 | d2 | ≥ 0,85 | ≥ 1,00 | ✅ **`zen_f_b03h_d1` 21,5** · WHR 0,914 · SHR 1,052 |
| A5 | Retângulo | 32 | d1 | ≥ 0,88 | ≥ 1,00 | ✅ coberto pelo C3 (`b09h_d1` 33,9 · 0,957/0,998) |
| **B1** | **Violão não-atlética** | **27** | d2 | ≤ 0,72 | < 0,92 | ✅ `zen_f_b08h_d2` 28,4 · WHR 0,743 · **WHRmin 0,552** |
| B2 | Violão não-atlética | 24 | d2 | ≤ 0,72 | < 0,92 | ✅ **`zen_f_b05i_d2` 22,8** (0,731) + **`b05h_d2` 26,7** (0,756) — ver §10 |
| B3 | Violão não-atlética | 30 | d1 | ≤ 0,74 | < 0,90 | ✅ `zen_f_b08_d2` 33,4 · WHR 0,716 · quadril 141,0 |
| — | violão extrema (passista) | — | d2 | — | — | ✅ **`zen_f_b07h_d2` 28,5** · **WHRmin 0,484** e **SHR 0,721**, os dois recordes |
| C1 | Maçã / oval | 29 | d1 | ≥ 0,92 | ≥ 0,95 | ⚠️ coberto pelo A1 |
| C2 | Maçã / oval | 26 | d1 | ≥ 0,92 | ≥ 0,95 | ⚠️ coberto pelo A2 |
| C3 | Maçã / oval | 32 | d1 | ≥ 0,92 | ≥ 0,95 | ✅ **`zen_f_b09h_d1` 33,9** · WHR 0,957 · SHR 0,998 |
| C4 | Maçã / oval | 35 | d1 | ≥ 0,92 | ≥ 0,95 | ✅ **`zen_f_b12h_d1` 39,7** · **WHR 0,994** |
| D1 | Tri. invertido não-atleta | 26 | d2 | — | ≥ 1,05 | ✅ **`zen_f_b07j_d1` 24,4** · SHR 1,097 · WHR 0,977 |
| D2 | Tri. invertido não-atleta | 22 | d2 | — | ≥ 1,05 | ✅ coberto pelo A4 (`b03h_d1` 21,5 · SHR 1,052) |
| D3 | Tri. invertido não-atleta | 30 | d1 | — | ≥ 1,05 | ✅ **`zen_f_b09j_d1` 28,4** · **SHR 1,118** · **WHR 1,047** |
| **E1** | Ampulheta (vão de tamanho) | **24,5** | d3 | — | — | ✅ **`zen_f_b06i_d3` 24,4** — matou o buraco da Aura |
| E2 | Ampulheta (vão de tamanho) | 26,0 | d3 | — | — | ✅ coberto pelo E1 (o vão `f d3` saiu do `coverage_gaps`) |

**Corpos que a onda produziu sem fechar célula, e que ficam** (regra 5b):
`zen_f_b07h_d1` 27,9 (a fresta entre pera e retângulo, de 15/09) ·
`zen_f_b11h_d1` 54,8 (erro de mira — ver §10) ·
`zen_f_b09i_d1` 33,7 (SHR 0,966, a tentativa que não alcançou o D3) ·
`zen_f_b09i_d3` 38,5 (partiu o maior buraco `high` da coleção, 32,4 → 45,1).

### 2ª onda — MASCULINO, 12 corpos

| # | forma | alvo IMC | estado |
|---|---|---|---|
| M-A1..A4 | **Pera / triângulo** (ombro estreito, quadril largo) | 22 · 26 · 30 · 34 | ✅ **M-A3: `zen_m_b09h_d1` 31,3 · SHR 0,889** (17/09) · faltam 22 · 26 · 34 |
| M-B1..B3 | **Maçã / oval** abaixo de 33 | 26 · 29 · 32 | 🔴 só existe ≥ 33,3 |
| M-C1..C3 | **Ampulheta** acima de 24 | 27 · 30 · 33 | 🔴 só existe ≤ 23,8 |
| M-D1..D2 | **V com gordura** (`d1`/`d2`) | 28 · 33 | 🔴 V só existe em `d3` |

### O tamanho do trabalho — **atualizado em 15/09**

| escopo | corpos | créditos | total da coleção |
|---|---:|---:|---:|
| ✅ feito em 15/09 | 5 | 160* | **81** |
| falta da 1ª onda feminina | **11** | 220 | 92 |
| + 2ª onda masculina | +12 | 240 | 104 |
| + os 2 vãos `high` de IMC masculinos | +2 | 40 | 106 |
| **total para fechar o plano** | **25** | **~500** | **106** |
| + 2º nível de definição nas formas novas (opcional) | +15 a 20 | ~400 | ~125 |

*160 = 5 corpos × 20 + 20 da calibração Meshy 7 + 20 de uma geração reprovada.
Saldo depois da sessão: **~980 créditos**, folga de quase 2× para os 25.

---

## 6. Como se produz FORMA — o método, e ele já foi medido

✅ **A direção do volume é um lever independente do tamanho** (`LICOES.md`
§2.2c). A cláusula *"o volume cresce principalmente na metade de baixo do corpo
[…] enquanto a cintura permanece estreita"* produziu o `zen_f_b07_d3` com WHR
mínimo **0,524** — o extremo da série inteira — a 0,7 de IMC do vizinho. E o
`b06h_d3` saiu a **0,2 de IMC** da âncora sendo outro corpo.

**Para as células deste arquivo é a mesma alavanca, invertida:** *"o volume
cresce no TRONCO — cintura e abdômen — enquanto o quadril e as coxas permanecem
estreitos"*. Essa direção **nunca foi testada** neste projeto; o mecanismo é o
mesmo, o pouso não.

### As três travas que se pagam caro (não reaprender)

1. 🔴 **UM lever por folha.** Categoria governa tamanho, direção de volume
   governa forma. Empilhar os dois, com negação, dá **zero** — medido: passo de
   +0,2 quando o alvo era +2,9. `LICOES.md` §2.2c.
   **Consequência para estas folhas: a âncora é do TAMANHO certo e a categoria
   não muda.** Só a direção do volume se move.
2. 🔴 **Negação não vence atrator** (§2.4d): 3 falhas em 7 folhas. *"os ombros
   dela são estreitos"* alargou o ombro. Negação só vale nomeando o **atrator a
   evitar**, nunca um traço que o próprio descritor pede.
3. ⚠️ **A folha 2D não prevê IMC** (§2.6, 5 preditores mortos) — **mas prevê
   FORMA**: `ombro/quadril` e `cintura/ombro` na folha são exatamente o que o
   `sheet_qa.py` mede (§1.4b/c/d). Numa folha de forma, **a régua da folha é o
   critério de aprovação**, não só alarme ordinal.

### Veredito, depois da Meshy

O `metrics.py` dá as 11 colunas; a forma é `waist_navel/hip` e `shoulder/hip`.
**A célula só fecha se o corpo medido cair dentro do WHR/SHR alvo da tabela §5.**
Corpo que pousa fora **não se descarta e não se regera** (regra 5b): ele entra na
biblioteca como inserção e a célula continua aberta.

---

## 7. ✅ Como saber que acabou

1. Nenhuma das 5 formas com **zero** corpos em nenhuma das duas coleções.
2. Toda forma com pelo menos um corpo a cada ~3 de IMC entre 20 e 33.
3. A Joice refeita no aparelho: distância ≤ 0,45 (hoje 0,73) e quadril dentro de
   ±8 cm.
4. O log `⚠️ FORA DA COBERTURA` do `onFit` (app, `avatar_selector.dart`) deixando
   de disparar nos corpos reais medidos.

---

## 8. 🔴 A MESHY TROCOU DE MODELO NO MEIO DA BIBLIOTECA (14/09/2026)

**Os 76 avatares atuais foram feitos no Meshy 6 Multi-View. Isso não é mais
reproduzível:** desde o Meshy 7 (lançado em 10/08/2026), **Multi-View roda
exclusivamente no `Meshy 7 - Flagship` / Alto Detalhe** — selecionar Meshy 6 ou
Smart Topology faz o botão de Multi-View desaparecer.

Não existe opção de ficar no pipeline antigo: ou se usa Meshy 7 com as 3 vistas,
ou se volta para vista única, que é pior (perde costas e perfil).

⚠️ **O que isso põe em risco é a MEDIDA, não a aparência.** A seleção do app é
distância de circunferências entre corpos; se o Meshy 7 lê o mesmo desenho com
outra proporção — e o anúncio dele é exatamente "alinhamento geométrico melhor"
—, os corpos novos entram numa régua diferente da dos 76. Um corpo novo com a
cintura 3 cm deslocada ganha a escolha com convicção total (§7.1).

✅ **Trava barata: um corpo de CALIBRAÇÃO antes da 1ª onda.** Rodar no Meshy 7 as
referências **já recortadas** de um avatar aprovado (`zen_f_b04i_d1`, que é a
âncora da A1) e comparar as 11 colunas do `metrics.py` contra o master de julho.

### ✅ RODADA EM 14/09 — o resultado, e ele muda a MIRA (não a lista)

As 3 referências de julho do `zen_f_b04i_d1`, sem uma linha de prompt, entraram
no Meshy 7 Multi-View / Padrão. O `process.py` passou **8/8**. Medida contra o
master de julho:

| coluna | Meshy 6 | Meshy 7 | Δ |
|---|---:|---:|---:|
| pescoço | 34,1 | 34,4 | +0,3 |
| ombro | 104,9 | 107,5 | +2,6 |
| **peito** | 98,0 | 103,6 | **+5,6** |
| cintura umbigo | 98,2 | 100,9 | +2,7 |
| cintura mín | 81,6 | 82,7 | +1,1 |
| **quadril** | 117,4 | 121,6 | **+4,2** |
| **bíceps** | 28,4 | 31,9 | **+3,5 (+12,3%)** |
| antebraço | 25,8 | 27,6 | +1,8 |
| punho | 21,5 | 21,9 | +0,4 |
| **coxa** | 64,4 | 68,9 | **+4,5** |
| panturrilha | 40,1 | 41,2 | +1,1 |
| **IMC medido** | **26,5** | **28,4** | **+1,9** |

🔴 **O Meshy 7 lê o MESMO desenho como um corpo maior — 11 colunas de 11 para
cima, erro médio 2,5 cm.** Não é ruído: ruído tem sinal trocado.

✅ **Mas a FORMA atravessa intacta**, e é isso que salva a lista do §5:

| razão | Meshy 6 | Meshy 7 |
|---|---:|---:|
| cintura/quadril | 0,836 | 0,830 |
| ombro/quadril | 0,894 | 0,884 |
| cintura mín/quadril | 0,695 | 0,680 |

**Consequências práticas:**

1. **Os alvos de WHR/SHR do §5 valem como estão.** Forma não se deslocou.
2. 🔴 **Toda a tabela de passo e atrator do `LICOES.md` §2.4/§2.5 está em
   unidades de Meshy 6.** Alvo de IMC mirado por aquelas tabelas pousa ~**+1,9**
   mais alto. Mirar 26 e receber 28 **não é folha ruim** — é a régua nova.
3. ⚠️ **Uma amostra é direção, não constante** (§1.5, §2.6: 5 preditores mortos
   com 4–6 amostras). O +1,9 se declara como previsão, não se subtrai do alvo
   nem se corrige em código. **Não** aplicar offset no `metrics.py`: o índice usa
   medida real, e o corpo é do tamanho que ele é.
4. **A malha crua é 14,6× mais densa** — 1.934.152 triângulos contra 132.040, e a
   decimação foi de 0,454 para **0,031**. As 8 validações passaram. Efeito
   colateral: o `01_raw` engorda ~35 MB por avatar (era ~7), ou seja ~600 MB na
   1ª onda — **conferir o espaço antes do próximo backup.**

O cru e o master desta calibração ficaram em `qa/calib_meshy7/`, fora de
`01_raw/` e `02_master/` para não entrarem em varredura de `--all`. O
`library_metrics.json` foi restaurado: **76 avatares, sem resíduo do id
descartável.**

⚠️ **Não empilhar variável.** `Ultra 2K` (25 créditos) e `Pose` são botões novos
do Meshy 7 e ficam **desligados** até o 6→7 estar medido — a decimação para 60k
joga fora boa parte do detalhe extra do Ultra, e `pose_mode` re-posa o
personagem, o que quebraria todas as bandas de altura do `shorts.py` e do
`morph.py` (o `b06h_d3` calibra a máscara do bíceps no eixo do braço, ~24° da
vertical, que vem da A-pose da folha).

---

## 9. O que a sessão de 15/09 MEDIU (e vale para as próximas 25 folhas)

### ✅ A cláusula de direção de volume vale **+6,1 de IMC** sobre a âncora

Reproduzida em duas gerações, com o botão de melhoria de imagem em estados
opostos: âncora 27,3 → **33,4** (+6,1) e âncora 22,2 → **28,4** (+6,2).

**É a primeira régua de mira deste projeto que reproduziu na segunda amostra.**
Ela vale para *esta* cláusula (volume desce para quadril/glúteo/coxa) e não se
transfere para outra — a de tronco, medida na mesma sessão, deu ~+1,4.

⚠️ **A cláusula ACRESCENTA volume, não redistribui.** Foi o que estourou o
`b08_d2` (previ 28–30, vieram 33,4): quadril +20,8 cm e peito +8,3 sobre a
âncora. Quem mira tamanho com ela tem que **ancorar ~6 pontos abaixo do alvo**.

### ✅ Mirar FORMA custa ~2 gerações por célula

Do `b04i_d1` (0,836 / 0,894) até fechar o retângulo foram dois passos:
`b07h_d1` (0,869 / 0,932, não fechou) e `b07i_d1` (0,923 / **1,009**). O ombro
não responde a pedido direto — **moveu +0,2 cm quando pedido, e +4,1 cm quando eu
só apertei o quadril.** `LICOES.md` §2.4d de novo: negação/pedido não vence
atrator; mexer no denominador vence.

### 🔴 Melhoria de imagem: desligar

Uma malha reprovou com **38,4 mm de assimetria no ombro esquerdo** (teto 20) —
defeito já presente no arquivo cru, não criado pelo pipeline. Regerada com
`Melhoria de imagem` **desligada**: **5,2 mm**, 8/8. Uma amostra não prova
causa, mas o custo de manter desligado é zero e o passo de IMC não mudou.
O reprovado está em `qa/reprovados/` para comparação.

### ⚠️ A segunda ilha da cicatrização é PINÇA, não pedaço solto

O `bmesh_stats` conta ilha por **face**; a solda non-manifold de 0,5–2 mm cria um
ponto onde duas superfícies se tocam por **um vértice só** — 6 triângulos de 2 mm
na axila. Por vértice a malha continua conexa, e por isso a sonda que eu escrevi
primeiro (flood fill por aresta) disse "1 ilha" e escondeu o defeito.
**Reproduzir a trava com a MESMA topologia que ela usa.**

### 🎯 A régua externa: a Joice

| | distância |
|---|---:|
| antes (coluna de cintura errada) | 0,84 |
| com `waist_navel` | 0,73 |
| com o `b07h_d1` | 0,62 |
| **com o `b07i_d1`** | **0,4205** |

Critério do §7 era ≤ 0,45. **Batido**, com 9 de 9 colunas na conta e erro médio de
3,0 cm. O resíduo é cintura +4,9 e quadril +3,7 — as duas colunas com a maior
amplitude de morph.

---

## 10. O que a sessão de 16–17/09 MEDIU — 12 corpos, e as réguas de passo caíram

**A 1ª onda fechou: 17 de 17 células.** A coleção foi de **81 para 93**.

### 🔴 NENHUMA cláusula de direção tem passo confiável em três amostras

A §9 declarou a cláusula de volume-para-baixo como *"a primeira régua de mira que
reproduziu"*. **Ela quebrou na terceira**, e o mesmo aconteceu com a segunda régua
que esta sessão achou:

| lever | amostras | veredito |
|---|---|---|
| volume-para-baixo | +6,1 · +6,2 · **+8,4** | quebrou na 3ª |
| tronco (texto neutro) | +6,0 · +5,8 · **+9,3** | quebrou na 3ª |
| **subtrativo** (encolhe embaixo) | −3,5 · −3,2 · **−5,3** | quebrou na 3ª |
| descida por âncora | −3,9 · −3,3 | 2 amostras |

**O padrão é o mesmo nos três: o passo escala com o TAMANHO DA ÂNCORA.** Quanto
mais pesada a âncora, maior o salto em pontos de IMC. Isso é aritmética de volume
(IMC vai com massa, e massa cresce com o cubo da escala linear), não capricho do
gerador — então **régua de passo medida numa faixa não vale em outra**, e é a §5c
do `CLAUDE.md` aplicada ao prompt.

**O que sobreviveu e vale usar:** a DIREÇÃO de cada lever é confiável; a
MAGNITUDE não é. Mirar célula de forma funciona; mirar IMC exato, não.

### ✅ O lever SUBTRATIVO é o mais confiável do projeto — e ele é a §2.4d aplicada

*"Encolha quadril, glúteo e coxa; não mexa em nada do tronco."* Três usos, três
acertos de forma:

| âncora → corpo | SHR | WHR |
|---|---|---|
| `b07i_d1` → `b07j_d1` | 1,009 → **1,097** | 0,923 → 0,977 |
| `b05h_d1` → `b03h_d1` | 0,984 → **1,052** | 0,905 → 0,914 |
| `b09i_d1` → `b09j_d1` | 0,966 → **1,118** | 0,955 → **1,047** |

**Ele nunca fala em ombro nem em cintura** — mexe só no denominador. O ganho de
SHR cresce com o quadril disponível: +0,068 num corpo de 105 cm de quadril,
+0,152 num de 122,6.

🔴 **O contraexemplo, na mesma sessão e com 5 minutos de diferença:** mirando o
A4 eu primeiro pedi *"mais magra, mas a cintura continua larga em relação ao
quadril"* — o quadril não se mexeu (−0,18 pp) e a cintura desabou; virou pera
magra e **reprovou**. Reescrito como subtração pura, o mesmo alvo saiu na hora
(quadril −2,06 pp, `cintura/quadril` 0,667 → 0,731). Mesma célula, mesmo gerador:
**pedir a razão falha, apertar o denominador funciona.**

### 🔴 Intensificador NÃO é inerte no lever de âncora — custou o `b11h_d1`

A §2.1 do `LICOES.md` mediu que adjetivo de intensidade não move corpo. **Aquilo
vale para descritor de CATEGORIA.** No lever de âncora ele move, e muito: trocar
*"com MAIS VOLUME — alguns quilos acima"* por *"CONSIDERAVELMENTE MAIS PESADA…
bastante acima do peso"* (mais *"barriga MUITO maior"*, *"a cintura some por
completo"*) levou o passo de **+6,0 para +20,9**. O alvo era 38–41 e veio **54,8**.

**Doutrina:** ao repetir um lever medido, repetir o TEXTO. Mudar âncora e
redação juntos invalida a régua e não se sabe qual dos dois moveu.

### 🔴 O corte WHR ≤ 0,72 da §5 é INALCANÇÁVEL na linha não-atlética

Cinco violões, cinco âncoras, três levers: **0,716 · 0,731 · 0,743 · 0,748 ·
0,756**. Não correlaciona com tamanho (o menor WHR saiu do menor quadril).

A causa é anatômica: `waist_navel` fica em 0,600 da altura e, num corpo sem
tônus, ali passa a barriga mole — que sobe junto com o quadril. Dos 8 corpos
femininos com WHR ≤ 0,72 na coleção, **6 são `d3`**: barriga chata no umbigo vem
com definição neste gerador. **O critério pede duas coisas incompatíveis.**

✅ **A régua que SEPARA de verdade é a cintura mínima:** o `b07h_d2` (passista)
mede **WHRmin 0,484** contra 0,638 da âncora — recorde da coleção, batendo até a
atleta de wellness (0,524). **Proposta: para `d1`/`d2` usar `WHRmin ≤ 0,58`**, ou
afrouxar o corte do umbigo para ≤ 0,76. Decisão do Rogério, não aplicada.

### ✅ Categoria do mundo real move FORMA, não só tamanho

*"PASSISTA DE ESCOLA DE SAMBA do Rio, julgada pelo gingado, nunca por músculo"* —
§2.2b aplicada a um corpo não-atlético. Foi o **único** tiro da sessão em que
cintura e quadril andaram em direções opostas na folha (cintura −0,92 pp, quadril
+2,69 pp); nos quatro anteriores os dois subiam juntos. Resultado: os dois
recordes de forma da coleção feminina.

### ⚠️ Conversa suja arrasta o prompt anterior

O mesmo texto, gerado em duas conversas: na antiga (que ainda tinha o prompt de
crescer-o-tronco) o quadril **subiu** +1,75 pp e a razão ficou parada em 1,074;
na nova, o quadril **caiu** −2,10 pp e a razão foi a 1,182. **Folha de forma se
gera em conversa limpa.**

### 📐 Régua de folha: o critério se declara ANTES de olhar

Toda folha desta sessão foi julgada por um número dito antes da geração
(*"`ombro/quadril` ≥ 1,13"*, *"`cintura/quadril` não pode cair de 0,728"*). Duas
reprovaram por ele e **nenhuma virou crédito perdido**: a folha do D3 recusada
virou o `b09h_d1` (C3) sem gerar imagem nova. Custo real da onda: **12 corpos,
~260 créditos**, contra os 220 orçados para 11.

### 🔴 Duas malhas reprovaram no `process.py` — e é o dobro da taxa anterior

`zen_f_b09i_d3` (furo/watertight, 470k triângulos crus) e `zen_f_b09i_d1`
(**2 ilhas**). As duas passaram na segunda geração, sem tocar na folha. Ambas
estão em `qa/reprovados/`. Com a de 15/09 são **3 malhas reprovadas em 12
corpos** no Meshy 7, contra ~1 em 76 no Meshy 6.

### ✅ O ESPELHO DO LEVER SUBTRATIVO ABRIU A 2ª ONDA (17/09)

*"Encolha ombros, costas, peito e braços; não mexa em nada do quadril para
baixo."* Primeiro uso, e fechou o **M-A3** de primeira: `zen_m_b09h_d1`, IMC 31,3,
**SHR 0,889** — ombro **−19,2 cm** e quadril **+2,5** contra a âncora `b05j_d1`
(1,073). Previsto 0,92–1,00.

**Com ele o lever subtrativo está em 4 de 4**, nas duas direções:

| âncora → corpo | o que encolheu | SHR |
|---|---|---|
| `b07i_d1` → `b07j_d1` | embaixo | 1,009 → 1,097 |
| `b05h_d1` → `b03h_d1` | embaixo | 0,984 → 1,052 |
| `b09i_d1` → `b09j_d1` | embaixo | 0,966 → 1,118 |
| `b05j_d1` → `b09h_d1` | **em cima** | 1,073 → **0,889** |

**É o único lever do projeto que nunca falhou** — e o motivo é a §2.4d: ele mexe
no denominador e **nunca nomeia a razão que quer mover.**

🔴 **A folha `zen_m_b05j_d1_sheet.png` está corrompida** e não serve de referência
para `sheet_qa`: figura em `y=0`, alturas divergindo **4,39%**, `cintura/ombro`
**1,119** — os três sinais de vazamento juntos. O avatar dele está correto (medido
no 3D). **Antes de usar folha antiga como âncora de medição, rodar o `sheet_qa`
nela sozinha.**
