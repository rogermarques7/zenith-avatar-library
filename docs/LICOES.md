# Lições — o que este projeto aprendeu errando

Doutrinas duráveis, organizadas por tema. Cada uma traz **o número que a
comprovou**, porque sem o número ela vira opinião e alguém a revoga na sessão
seguinte.

**Como usar:** ler o tema que interessa à tarefa da vez, não o arquivo inteiro.
A narrativa completa de cada descoberta está em
`docs/historico/diario-2026-07.md` — vir aqui primeiro, ir lá só se a lição não
bastar.

---

## 1. Réguas — a família de erro mais cara do projeto

Cinco vezes uma verificação passou porque **a pergunta que ela fazia não era a
que importava**. É o padrão que mais custou aqui.

### 1.1 Perguntar sempre: o que esta régua NÃO mede?

| régua | o que ela vê | o que ela NÃO viu | custo |
|---|---|---|---|
| altura do cós/bainha | posição vertical | **traçado** da peça | 39/39 passaram com 8 shorts errados |
| silhueta 2D da folha | **largura** | **tônus** (relevo) | declarei "o mesmo corpo" em folhas com abdomens diferentes |
| silhueta frontal | largura | **profundidade** | quase reprovei o `f_b04_d2`, que estava certo |
| `--report` do short | desvio contra a SÉRIE | série inteira errada | `b12_d1` passou com o cós 25 cm fora |
| validação `tris` | resultado vs `TARGET_TRIS` | **o alvo estar errado** | avatar 42.000 tri abaixo da biblioteca, placar cheio |
| sonda `probe_tonus_f` | relevo da superfície | **que a janela caiu dentro da ROUPA** | acusou "peitoral +27%" que era dobra de faixa |
| `sheet_qa` em folha do **Gemini** | nada de útil | **que não sabe ler aquele gerador** | quase reprovei uma folha boa por "altura 4,42%" |
| `coxa` do `sheet_qa` em corpo pesado | largura da coxa | **que o short desceu por cima do ponto de medida** | devolveu "coxa 2,10% da altura" |

> **A coxa do `sheet_qa` é amostrada numa fração FIXA da altura (~0,56), e o
> short não é fixo.** Na folha-mãe o tecido termina em 0,535 e a medida cai na
> pele; em corpo pesado o short desce até 0,571 e a medida cai **dentro do
> tecido preto**, devolvendo número sem sentido (2,10%, com 14 linhas
> descartadas). Acontece em toda folha pesada. Ignorar a linha `coxa` quando a
> 2ª peça de roupa passar de ~0,56 — o próprio relatório imprime esse limite.

> **O `sheet_qa` só lê folha do ChatGPT.** Ele foi reescrito na sessão 8 e
> calibrado em folha feminina do ChatGPT; a silhueta vem por *preenchimento a
> partir do contorno*, e em folha do Gemini o preenchimento vaza — as figuras
> saem começando em `y=0` e a altura vira o denominador errado de **todas** as
> porcentagens. Diagnóstico definitivo: rodar na `zen_m_b05j_d1`, folha do
> Gemini **já aprovada e produzida**, devolve a mesma patologia (4,39% de
> variação, cabeças espalhadas 55 px).
>
> **Quem decide se a folha do Gemini entra é o `crop.py`**, que usa limiar mais
> tolerante e leu a mesma folha com os três topos no mesmo pixel e 0,66% de
> variação. Na dúvida entre os dois detectores, o `crop.py` é o que importa —
> é ele que está no caminho do produto.
>
> É a §5.5 aplicada a mim mesmo: a régua 2D não atravessa troca de gerador.

> **A sonda de tônus só vale no ABDÔMEN no feminino.** A janela `peitoral` dela
> vai de 0,245 a 0,300 da altura, e a faixa de compressão ocupa ~0,240 a 0,315
> — a janela cai **inteira dentro do tecido preto**. As regiões foram calibradas
> no masculino, que é torso nu. Ler só a linha `abdomen`; `coxas` já devolve
> "sem linha útil".

### 1.2 Trava que confere o alvo contra ele mesmo não valida o alvo

A checagem `tris` compara o resultado com `TARGET_TRIS ± 15%`. Com a constante
errada (18000 quando a biblioteca estava em 60000), ela passa limpa. Mesma
família do `--report`, que comparava cada avatar com a série.

### 1.3 Consistência interna não é correção — ancorar FORA do gerador

Foi por isso que nasceu o `shorts_ref.py`, que mede a peça na folha de
referência em vez de comparar avatares entre si.

**Exceção documentada:** para o **traçado** em corpo com avental, a folha 2D não
serve — ela não enxerga que a superfície tem duas folhas. Ali o afastamento da
folha foi deliberado. A folha continua valendo para **altura**.

### 1.4 A régua é o DESCRITOR, não o vizinho

Comparar com a folha anterior responde *"mudou?"*, nunca *"está certo?"*. Se o
vizinho está fora de especificação, comparar com ele **propaga o desvio** — e
com a folha-MÃE propaga para a biblioteca inteira.

Custou duas regerações da mãe feminina: usei como referência de tônus uma folha
que tinha gomos abdominais que o descritor proibia em maiúsculas, e declarei a
folha nova (correta) "regredida".

### 1.5 Duas estimativas concordando não são uma confirmação

Estimei o IMC de uma folha por volume (~28) e pela regra aditiva (29,4), vi as
duas baterem e escrevi que a regra estava confirmada no feminino. Medido:
**27,3**. Eram dois palpites meus. Antes de escrever "confirmado", separar o que
é **medida** do que é **estimativa minha**.

### 1.6 Calibrar régua nova rodando na peça já aprovada

Os três defeitos do `sheet_qa` apareceram de uma vez ao rodar a versão nova na
folha-mãe aprovada. Não é passo extra — é o método.

---

## 2. Mirar um IMC — o que funciona e o que não funciona

O gerador de imagem tem **atratores**: pontos para onde o corpo cai
independentemente do que se pede.

### 2.1 O que NÃO move o corpo

- **adjetivo de intensidade** ("bem mais musculoso", "passo contido")
- **número relativo** ("~10% mais massa")
- **interpolação** — pedir o meio-termo exato entre duas anexas devolve a folha
  maior. Testado, falhou.
- **baixar a âncora**, se o substantivo não mudar: baixar 3,4 moveu o pouso 0,7

### 2.2 O que move: o SUBSTANTIVO DE CATEGORIA

Trocar "homem musculoso e seco de academia" por "FISICULTURISTA DE COMPETIÇÃO"
moveu o pouso 6,4 pontos de IMC. **Um vão é o vazio entre dois atratores
nomeáveis.** Se não existe palavra de categoria entre os dois, nenhuma âncora e
nenhum adjetivo colocam corpo ali.

⚠️ Cuidado com o inverso: **nomear o atrator e negar a saída** ("musculoso e
seco, NÃO um fisiculturista") trava o passo — no `b06i_d3` o delta caiu de +6,5
para +3,3.

### 2.3 Bracketing — e seu limite

Anexar **duas** folhas consecutivas aprovadas e pedir "a próxima etapa, com um
passo do MESMO TAMANHO". Entrega **~2× o passo pedido** (medido 1,9× · 2,0× ·
2,2×).

⚠️ **Não funciona com âncoras coladas.** O modelo tem passo mínimo e ignora
pedido menor que ele. Com par a **0,7 de IMC**, o bracketing vira ruído: pedi
24,5–25,9 e recebi **27,3**.

⚠️ **O fator 2× só vale em espaço aberto.** Perto de um atrator forte o passo
explode — medido 8×.

### 2.4 A regra aditiva — e onde ela vale

`pouso ≈ âncora de topo + 6,5 de IMC`, quase independente do que se pede. Seis
amostras masculinas: +6,2 · +7,2 · +8,1 · +8,3. Para mirar X, escolher o par
cujo membro **superior** esteja em ~X−6,5, mesmo que fique bem abaixo do buraco.

⚠️ **Medida SÓ no masculino.** As amostras femininas dão **passo ~4**, não 6,5.
Não transferir sem remedir.

**O passo tem tamanho, não sinal — vale para baixo também.** Primeira medida
descendente do projeto (`f_b02`, 29/07): âncora única em 22,2, pouso **18,3**,
delta **−3,9**. Contra +4,4 da única subida feminina. Uma amostra em cada
direção: usar como ordem de grandeza, **não como constante** (§1.5).

⚠️ **Consequência estrutural:** com passo ~4, os dois vãos femininos baixos —
18,3→22,2 (3,9) e 22,9→27,3 (4,4) — são **do tamanho do passo ou menores**.
Pedir corpo dentro deles é o caso do §2.3, onde o bracketing vira ruído.

### 2.4b O passo é do GERADOR, não do sexo

Escrevi "passo ~4 no feminino" pela manhã de 29/07 e estava errado: as duas
amostras eram do **ChatGPT**. Medido no mesmo dia, na mesma linha feminina, no
Gemini:

| âncora única | pouso | passo | gerador |
|---:|---:|---:|---|
| 22,2 | 18,3 | −3,9 | ChatGPT |
| 22,9 | 27,3 | +4,4 | ChatGPT |
| 27,3 | 34,4 | +7,1 | **Gemini** |
| 22,9 | 30,1 | +7,2 | **Gemini** |

**O Gemini feminino dá +7,15, duas amostras a 0,1 uma da outra** — e bate com o
+6,5 masculino do mesmo gerador. O que muda o passo é a ferramenta, não o sexo.

**⚠️ MAS o passo tem sinal: DESCER move menos que subir, nos dois geradores.**
O diário registrava isso com uma amostra de cada lado e mandava não decidir.
Agora são seis:

| gerador | subindo | descendo |
|---|---|---|
| ChatGPT | +4,4 · +6,8 | −3,9 · −1,8 |
| Gemini | +7,1 · +7,2 | **−4,3** |

**Consequência: a receita "âncora = alvo − 7 no Gemini" só vale SUBINDO.** Para
mirar X descendo no Gemini, âncora em **X + 4,3**. Foi assim que o vão feminino
16,5→23,3 fechou: âncora na folha de 23,3, previsão 18,5–21,5 registrada antes
de gerar, medido **19,0**.

**Consequência operacional:** para mirar X no feminino, âncora em **X − 7** e
gerar no Gemini. Foi assim que o vão 27,3→34,4 fechou: âncora na folha-mãe
(22,9), previsão registrada de 29–31 **antes** de gerar, medido **30,1**. É a
primeira vez no projeto que um alvo de IMC foi previsto e acertado.

### 2.5 As lacunas são do GERADOR, não do problema

A faixa de IMC 28–38 na linha d1 resistiu a 3 tentativas no ChatGPT. O mesmo
prompt no **Gemini** entrou nela de primeira. Nenhum gerador é melhor; eles têm
atratores em lugares diferentes.

**Confirmado uma segunda vez, no feminino (29/07).** O ChatGPT mostrou três
atratores femininos e nada entre eles — **~18 · ~22–27 · ~54** —, com uma folha
mirando 31 pousando em **53,9**. A mesma âncora no Gemini deu **34,4**.

**Terceira confirmação, e a primeira do lado MAGRO (29/07).** O vazio entre os
atratores ~18 e ~22–27 do ChatGPT é real e simétrico: mirando 20–21,5, duas
gerações caíram em **~17,0 e ~17,5** — e a única coisa que mudou entre elas e a
folha que pousou em **23,3** foi o substantivo ("magra" contra "peso normal").
Passo de +6,8 com um, +1,1 com o outro: **não existe palavra entre os dois.**
O mesmo alvo no Gemini pousou em **19,0 de primeira**.

> Vale registrar que isto **não** era previsível pela direção: as duas
> tentativas do ChatGPT subiam de 16,5 e a do Gemini descia de 23,3. O que
> decidiu não foi a direção nem a âncora — foi onde cada ferramenta tem corpo.

> **O atrator "OBESIDADE GRAU I" do Gemini fica em ~33–34, e é a única
> constante que atravessou os dois sexos:** 33,3 e 34,0 no masculino, **34,4 no
> feminino**. Vale registrar porque quase tudo mais aqui difere por sexo (o
> passo é ~6,5 no masculino e ~4 no feminino). Quando o alvo for essa faixa, é
> tiro de uma geração.

**Ordem quando um alvo não sai:** (1) bracketing · (2) trocar o substantivo de
categoria · (3) **trocar de gerador** · (4) aceitar e cobrir por shape keys.

### 2.6 Prever o IMC pela folha

`secção ≈ largura(frente) × profundidade(perfil)`; média das razões contra a
referência; **multiplicar o delta por 0,5–0,6**; aplicar ao volume conhecido.

| | estimado cru | medido | fator | ombro na folha |
|---|---:|---:|---:|---|
| `f_b04` (desceu) | −5,3% | −3,2% | ×0,60 | **parado** (+0,17 pp) |
| `f_b06` (subiu) | +38,3% | +19,0% | ×0,50 | ganho concentrado no tronco |
| `f_b02` (desceu) | −22,6% | −20,1% | **×0,89** | **moveu** (−1,12 pp), com coxa e braço |
| `f_b09` (subiu) | +97,2% | +97,4% | **×1,00** | **moveu** (+5,71 pp), tudo junto |
| `f_b01` (desceu) | −14,5% | −9,6% | **×0,66** | quase parado (−0,42 pp), queda no quadril/coxa |

O desconto existe porque a conta trata o corpo como elipse e ignora que cabeça,
braços, mãos e pés quase não mudam entre bandas. **Serve para dizer "vai passar
da banda", não para dizer o decimal.**

### 2.6b O desconto NÃO é constante — ele mede o quanto a mudança ficou no tronco

Aplicar ×0,55 no `f_b02` previu 19,8–20,3 e o corpo mediu **18,3**: erro de ~2
pontos, o maior da série. A causa está na própria justificativa do desconto —
ele só existe porque os membros ficam parados. **Quando os membros também se
movem, não há o que descontar.**

Discriminador barato, direto do `sheet_qa`: **olhar o delta de OMBRO.**

- ombro **parado** e só o tronco mexendo → desconto forte, **×0,5–0,6**
- ombro mexendo junto com coxa e barriga → corpo inteiro mudou de escala,
  **×0,9–1,0**, e quanto MAIOR a mudança, mais perto de 1,0

O extremo confirma o mecanismo: no `f_b09` (+97% cru) o desconto foi **zero** —
a estimativa crua acertou o IMC medido na terceira casa. Em corpo desse tamanho
nem pescoço (48,7 cm), nem rosto, nem mãos ficam parados, então **não sobra
região fixa para descontar**. O desconto nunca foi uma constante do método: é a
fração do corpo que não se mexeu.

Quatro amostras, todas femininas. Não é lei; é melhor que um fator fixo que
errou 2 pontos para baixo e depois 3 para cima.

### 2.6c ⚠️ A interpolação por |Δombro| FALHOU no primeiro teste fora da amostra

Escrevi em 29/07, com 4 amostras, que o fator saía de uma reta em |Δombro|
(`0,60 + (|Δombro| − 0,17) × 0,305`, saturando em 1,0). Ela acertou o
`f_b01_d1` — previu 0,68, o real foi 0,66. **Na amostra seguinte errou feio:**
no `f_b04_d1` o ombro moveu **+1,58 pp**, a reta mandava usar **~1,00** e o
fator real foi **0,64**. Previ IMC 25–27; o corpo mediu **23,3**.

**Não usar a reta de |Δombro|.** As seis amostras, ordenadas pelo tamanho da
estimativa crua:

| folha | cru | fator real | Δombro |
|---|---:|---:|---:|
| `f_b04_d2` (desceu) | −5,3% | 0,60 | +0,17 |
| `f_b01_d1` (desceu) | −14,5% | 0,66 | −0,42 |
| `f_b02` (desceu) | −22,6% | 0,89 | −1,12 |
| `f_b06` (subiu) | +38,3% | 0,50 | — |
| `f_b04_d1` (subiu) | +64,2% | **0,64** | +1,58 |
| `f_b09` (subiu) | +97,2% | 1,00 | +5,71 |

O que sobrevive às seis é **monotonicidade no TAMANHO da mudança**, dentro de
cada direção: subindo, 38→0,50 · 64→0,64 · 97→1,00; descendo, 5→0,60 ·
14→0,66 · 23→0,89. Bate com a explicação de sempre (quanto maior a mudança,
menos sobra de região parada para descontar) e **não precisa do ombro**.

Três amostras por direção não são uma lei (§1.5). Usar como faixa: mudança
pequena → 0,5–0,65 · mudança grande (|cru| > 60%) → 0,9–1,0. **E lembrar que
esta conta serve para dizer "vai passar da banda", não o decimal** — no
`f_b04_d1` a previsão pela folha ficou PIOR que o palpite feito só com o
prompt (20,5–22,5, que errou por 0,8 contra os 1,7–3,7 da conta).

---

## 3. Produção de folhas

### 3.1 Largar a folha-mãe no trecho magro

A mãe é um corpo atlético. Quando o alvo é bem mais magro que ela, o modelo
copia a musculatura dela e quebra a continuidade com o vizinho slim. Nesses
casos, anexar **só o vizinho imediato**. Confirmado na produção (`b03_d2` e
`b04_d2` só fecharam ao largar a mãe).

### 3.2 Identificar anexos por CONTEÚDO, nunca por ordem ou nome

E, para pares muito parecidos, **não pedir identificação** — pedir "um corpo
mais pesado que os DOIS anexos" dispensa a ordenação.

### 3.3 Altura é o único erro que o pipeline não corrige

Folha com altura diferente das anteriores: descartar sem tentar aproveitar.

### 3.4 Marca d'água na folha é proibida

Vira uma 4ª mancha sobre o fundo liso, quebra a detecção do `crop.py` e pode
chegar na Meshy como geometria.

### 3.5 A ÂNCORA move o IMC; o DESCRITOR move o TÔNUS — e são independentes

Abrir uma linha de definição nova **não exige folha-mãe própria daquela linha**.
Medido ao abrir a `f d1` (29/07): a folha do `f_b01_d1` foi gerada com anexo
único `zen_f_b02_d2` — uma folha `d2`, com tônus — e o descritor `d1` mandando
"sem nenhum tônus, magreza por ausência de massa, sem gomo/serrátil/veia".

Saiu volume **−9,6%** (18,3 → 16,5 de IMC) e relevo abdominal **2,171 contra
2,113 da âncora** — ou seja, o corpo encolheu e o tônus **não veio junto**, ficou
na mesma casa da folha-mãe (2,080). Os dois eixos responderam a comandos
diferentes sem interferir um no outro.

**Consequência operacional:** para abrir a `f d3` não é preciso produzir uma mãe
`d3` antes. Escolhe-se a âncora pelo IMC que se quer (§2.4b: alvo − passo do
gerador) e deixa-se o tônus por conta do descritor. A trava é conferir o relevo
com `qa/probe/sondas/probe_tonus_f.py` **antes** de subir na Meshy — a régua de
largura não vê tônus (§1.1), e é justamente o eixo que o descritor está movendo.

---

## 4. Malha e material

### 4.1 Não calibrar densidade de malha com material que esconde geometria

O alvo de 18k foi calibrado com o corpo roxo saturado. Quando virou titânio com
specular, a faceta apareceu e o relevo muscular ficou borrado. Subiu para 60k;
custo real **~183 KB** por avatar, dentro do orçamento de 1–3 MB. **O orçamento
nunca foi o gargalo.**

### 4.2 Metade do visual mora FORA do GLB

glTF não transporta iluminação de forma portável. O app precisa carregar
`03_dist/env/zenith_env.hdr` via `environment-image`, senão o avatar aparece
cinza e sem identidade.

### 4.3 `crotch_override_zh` conserta a ÂNCORA, não a SEGMENTAÇÃO

Quem usar override de virilha precisa conferir se `hem_peaks_zh` voltou vazio —
**o chute não se anuncia**. Cinco avatares tinham a bainha 100% chutada.

### 4.4 Duas hipóteses de segmentação REJEITADAS (não repetir)

- **máscara pela normal** (`nz < −0,55`): come a prega do glúteo
- **folha externa por raio**: perto da dobra as duas folhas se encontram por
  definição; apertar cortava 47% das faces

### 4.5 Topologia: anel fechado é o que o detector sabe achar

A bainha dá a VOLTA no membro; sulco de músculo cobre um arco. Foi por isso que
a roupa feminina virou **faixa reta** (borda em anel, como o cós) em vez de top
nadador — que, além disso, cobria **60,7% do dorsal alto** num app de musculação.

---

## 5. Biblioteca e classificação

### 5.1 Nunca regerar nem descartar avatar já produzido

Se ele não corresponde ao que o nome promete, o conserto é **reclassificar** (o
rótulo vive no `library.json`) e **inserir** um novo onde faltar cobertura.
Decisão do Rogério: *"quanto mais avatares tivermos, maior será nossa
biblioteca"*.

### 5.2 O nome do arquivo registra a INTENÇÃO, não o resultado

Desde o schema 3 quem ordena a biblioteca é o `measured_bmi`. Renomear um asset
só moveria a inconsistência para o `logs/process.log`, que é append-only.

**Consequência:** a folha de contato do QA deve ser ordenada por `measured_bmi`,
não por nome.

⚠️ **Vale para a BANDA, não para o nível de DEFINIÇÃO.** O `build_index.py`
extrai `d1|d2|d3` do próprio nome do arquivo (`ID_RE`, linha 66) — o
`measured_bmi` conserta banda errada, mas **nada confere o `d`**. É declaração,
não medida, e é a única parte do ID que o pipeline não audita.

**Enquanto um sexo tiver uma linha de definição só, botar avatar em outra linha
é pior que rotular errado.** O fallback `d3→d2→d1` só entra se a linha estiver
**vazia**; com um único avatar dentro dela, `nearest_id` devolve esse avatar
para qualquer IMC. Um corpo de IMC 50 sozinho numa linha `f d1` seria entregue
a uma mulher de IMC 24. Por isso o `zen_f_b09_d2` (IMC medido bem acima da
banda, e sem tônus no olho) **ficou em `d2`**: a linha feminina ainda é uma só.

### 5.3 A meta é COBERTURA do eixo de IMC, não contagem

O número 32 nunca foi meta.

### 5.4 Contar vão à mão não cola

Rodar `build_index.py`, que imprime. A redação anterior do `CLAUDE.md` dizia "um
vão high" e "8 low"; o índice diz **dois** e **6**.

### 5.5 A régua 2D não atravessa troca de gerador nem de pose

O `measure.py` ordena folhas do MESMO gerador com a MESMA pose, e nada além.
Quem decide onde um avatar caiu é sempre o `metrics.py`, sobre o master 3D.
Errar isso já custou três previsões.

---

## 6. Processo de trabalho

### 6.1 Um por vez é um por vez

Sem o print do avatar da vez, não mexer nos outros — nem para procurar padrão.

### 6.2 "Fechar o avatar" = GLB processado e medido

Não adiantar o prompt da folha seguinte na aprovação da FOLHA. Cobrado duas
vezes (25/07 e 29/07), e na segunda o Rogério identificou a causa: **contexto no
teto**. Sintoma a vigiar — janela cheia me faz pular etapa.

### 6.3 Iterar barato antes de palpitar

Na 2ª rodada cara de tentativa e erro, montar o banco de ensaio em vez de
continuar adivinhando. Foi o que destravou a sessão do short — parar de pagar
25 min por palpite.

### 6.4 Job em segundo plano contamina o mapa

Armadilha real de processo: conferir que nada está rodando antes de ler estado
compartilhado.

### 6.5 Arquivo nenhum entra no repositório pela mão do humano

Ele larga em Downloads; o script busca, renomeia, limpa e move. Pedir para ele
salvar, renomear ou apagar selo à mão é **regressão de fluxo**.

### 6.6 Não explicar um desvio antes de a MEDIDA confirmar que houve desvio

No `f_b04_d1` (29/07) a conta sobre a folha deu IMC 25–27 contra os 20,5–22,5
que eu tinha previsto. Anunciei o erro, achei a causa e escrevi o culpado: o
parágrafo que eu tinha acrescentado ao descritor pedia *"as coxas encostam uma
na outra"*, que é traço do `f_b08_d1` — logo eu teria misturado as bandas e
empurrado o corpo para `b07`.

Era uma história inteira, coerente e **falsa**. O corpo mediu **23,3**: 0,4
acima da banda `b04` que eu pedi. O prompt estava certo; errada estava a
estimativa que me fez procurar culpado.

**O gatilho é reconhecível:** a explicação nasceu de uma régua 2D e contradizia
o que o pedido tinha feito. É a §5.5 outra vez — a folha não decide onde o
corpo caiu, o `metrics.py` decide. Enquanto a medida não sai, o desvio é
hipótese, e hipótese não tem culpado. Custo desta vez: só uma explicação
retirada. Se eu tivesse "consertado" o método de escrever descritor em cima
dela, teria estragado o que funciona.
