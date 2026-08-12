# Lições — o que este projeto aprendeu errando

Doutrinas duráveis, organizadas por tema. Cada uma traz **o número que a
comprovou**, porque sem o número ela vira opinião e alguém a revoga na sessão
seguinte.

**Como usar:** ler o tema que interessa à tarefa da vez, não o arquivo inteiro.
A narrativa de **como** cada uma foi descoberta está em
`docs/historico/diario-2026-07.md` — vir aqui primeiro, ir lá só se a doutrina
não bastar. Este arquivo foi enxugado em 30/07 (sessão 14): a narrativa saiu, a
doutrina e o número ficaram.

---

## 1. Réguas — a família de erro mais cara do projeto

Seis vezes uma verificação passou porque **a pergunta que ela fazia não era a
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
| sonda `probe_tonus_f` | relevo da faixa **CENTRAL** do abdômen | **definição nos OBLÍQUOS e no andar de cima** | disse "−1,1%" numa folha com gomos e linha alba visíveis |
| `sheet_qa` com a silhueta vazada | nada de útil | **que o próprio detector falhou** | quase reprovei duas folhas boas por "altura 4–5%" |
| `coxa` do `sheet_qa` em corpo pesado | largura da coxa | **que o short desceu por cima do ponto de medida** | devolveu "coxa 2,10% da altura" |
| alarme ordinal (`quadril +15,61 pp`) | que o corpo é **muito** maior | **quanto** maior — ele não tem TETO | previ 48–55, mediu **114,2** |
| contagem de tri crua da Meshy | ordem de grandeza do volume, **só nos extremos** | a ordem no MEIO da linha | — (não usar como preditor) |
| `circumferences_cm` do `metrics.py` | perímetro da seção naquela altura | **que o braço/a barriga entrou na seção** | `b12_d1` saiu com cintura marcada `*` e tronco inflado |
| `thigh` do `metrics.py` | perímetro em `at_frac` **fixo** (0,460) | **que a virilha se move** | dispersa 53,1–63,0 cm entre corpos de IMC 23–24 |
| as 8 travas do `process.py` | malha, altura, simetria, material | **orientação frontal** | nenhuma acusaria frente e costas trocadas |
| resolução da folha | se o relevo vai sobreviver | **identidade do personagem** | `b09_d3` saiu 8/8 e lê masculino |

> **O IMC não se contamina em corpo pesado; as circunferências de TRONCO sim.**
> No `zen_f_b12_d1` (IMC 114,2) o `arm_split_frac` caiu para **0,606** contra
> ~0,710 da âncora esquelética: o braço encostou no tronco e entrou na seção, e
> a cintura saiu marcada com `*`. **Usar o IMC e ignorar cintura/quadril/coxa** —
> o volume vem do teorema da divergência sobre a malha fechada, não de casco
> convexo, então ele não se contamina.

> ### ⚠️ Constante em fração FIXA contra referência que se MOVE
>
> Duas réguas, o mesmo defeito, mesma família do `SEAL_ISOLATION` (§4.2b) e do
> `TARGET_TRIS` (§1.2):
>
> - **`thigh`** amostra em `at_frac` 0,460 e a **virilha não é fixa**. No
>   `f_b06_d3` deu **+9,9 cm** sobre a âncora enquanto o volume subia só 3,3 L,
>   porque 0,460 caiu **4,6 cm abaixo da virilha** daquele corpo
>   (`leg_split_frac` 0,486), onde o afunilamento é mais íngreme. **Julgar avatar
>   sozinho por `volume_l`.**
> - **`coxa` do `sheet_qa`** amostra em ~0,56 e o **short não é fixo**: na mãe o
>   tecido termina em 0,535 e a medida cai na pele; em corpo pesado desce a 0,571 e
>   cai dentro do tecido. **Ignorar `coxa` quando a 2ª peça passar de ~0,56** — o
>   relatório imprime esse limite.
>
> **Doutrina:** quando uma rota nova muda a resolução, a roupa ou o tamanho típico
> do sujeito, **varrer as constantes absolutas e as frações fixas.**

> ### ⚠️ O vazamento da silhueta do `sheet_qa` — e a doutrina ERRADA que ele gerou
>
> **A assinatura:** as figuras saem começando em **`y=0`** e as alturas das três
> vistas divergem (4–5%). A causa é o **preenchimento a partir do contorno**, que
> escapa quando o contorno tem uma abertura. Como a altura da figura é o
> denominador de todas as porcentagens, **todas** saem deflacionadas.
>
> **❌ Por duas sessões esta seção dizia "o `sheet_qa` não lê folha do Gemini". O
> gerador nunca foi a variável.** A folha do `zen_f_b06_d3` é do **ChatGPT** e
> vazou igual: alturas 971 · 927 · 922 (**5,05%**) e `ombro 10,50%` com
> `cintura/ombro 1,245` — a tira de amostragem subiu ~36 px e foi medir o pescoço.
> Remedida em três limiares (10 · 18 · 28) exigindo ≥3 px por linha: os três topos
> em **`y=44`** e alturas 926 · 926 · 921 → **0,54%**. O `crop.py` confirmou
> sozinho. Pela redação anterior eu teria **descartado três folhas boas** por
> violar a §3.3.
>
> **E o erro simétrico já tinha custado caro:** no `zen_f_b08_d1` a folha veio
> **sã** (figura em `y=36`, três vistas concordando em **0 px**) e eu invoquei "é
> Gemini, ignorar" sobre as porcentagens. Elas diziam **quadril +7,10 pp**,
> cintura +6,06 pp, ombro +3,92 pp — e a pose do Gemini é mais fechada, o que
> *subestima* largura, então +7,10 pp era gritante. O corpo mediu **IMC 42,6**
> mirando 27–31. O aviso estava na tela.
>
> **Operacional:** ler primeiro a seção de detecção — 3 figuras · `y` do topo > 0
> · variação de altura < 1% · fundo ~200.
> - **Passou** → as porcentagens valem como **alarme ordinal** ("esse passo é
>   grande demais"), nunca como previsão de IMC (§2.6).
> - **Reprovou** → **não descartar a folha.** Medir o topo à mão em limiares
>   variados, ou rodar o `crop.py`, que é o detector do caminho do produto. Só
>   depois decidir.
>
> **A lição de segundo nível é a que importa:** aplicar uma doutrina sem conferir
> se a condição que a gerou está presente é o mesmo erro que a §1.1 inteira
> combate — usar uma régua sem perguntar o que ela mede. Aqui eu atribuí uma
> assinatura de defeito a um *gerador*, e depois a uma folha que não a tinha.

> ### ⚠️ A sonda de tônus AFIRMA, mas não NEGA
>
> Ela lê só uma tira estreita em volta do eixo (`meia_frac` 0,22), então **vê
> gomo central e não vê gomo lateral**. As quatro leituras femininas conhecidas:
>
> | folha | leitura | o corpo real |
> |---|---:|---|
> | `f_b05_d3` | **2,058** (−1,1% vs. mãe) | linha alba, gomos superiores, oblíquos separados |
> | `f_b05_d2` (mãe) | 2,080 | abdômen liso, sem gomos, por descritor |
> | `f_b01_d1` | **2,171** | corpo *sem nenhum tônus* — leu **acima** da mãe |
> | `f_b06_d3` | **2,560** (+24,4%) | gomos centrais fortes |
>
> **Não está cega:** calibrada no par masculino aprovado, com o mesmo salto de
> descritor (`m_b05_d2` "SEM gomos" → `m_b05_d3` "gomos evidentes"), lê **+15,7%**
> (1,865 → 2,159). E o +24,4% do `f_b06_d3` supera essa calibração. Mas as três
> primeiras leituras femininas (2,058 · 2,080 · 2,171) **não têm relação com a
> definição real** — nessa linha ela nunca demonstrou ordenar tônus.
>
> **Operacional:** `abdomen` baixo **NÃO reprova folha `d3`**. Antes de decidir,
> recortar a região 0,28–0,46 da vista frontal, ampliar 3× e olhar — resolveu em
> 5 segundos. Subiu = veio relevo central; silêncio não é evidência de ausência.
>
> **E ela só vale no ABDÔMEN no feminino.** A janela `peitoral` vai de 0,245 a
> 0,300 da altura e a faixa de compressão ocupa ~0,240 a 0,315: cai **inteira
> dentro do tecido preto**. As regiões foram calibradas no masculino, que é torso
> nu. `coxas` já devolve "sem linha útil".

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

### 1.4b ✅ AS RAZÕES separam "corpo novo" de "âncora reescalada" — a trava que faltava

**A régua de largura não distingue um arquétipo novo de um zoom da âncora.** Se
todas as larguras sobem os mesmos ~0,5 pp e as **razões ficam paradas**, o que
voltou foi a mesma figura 2% maior, e o avatar sairia duplicado.

| folha | `cintura/quadril` | `cintura/ombro` | veredito |
|---|---:|---:|---|
| `b06h_d3` (§2.5: "0,2 de IMC e ainda é outro corpo") | 0,614 → **0,584** | — | corpo novo |
| tentativa `b03_d2` "magra e levemente atlética" | 0,594 → **0,595** | 0,587 → **0,583** | **âncora reescalada — reprovada** |
| tentativa `b03_d2` "bailarina clássica" | 0,594 → 0,589 | 0,587 → **0,549** | corpo novo (mas leve demais) |

**Limiar de trabalho: ~0,030 de movimento em alguma razão.** Abaixo de ~0,005 em
todas, é cópia. Este é o único jeito barato de pegar duplicata **antes** da
Meshy — o IMC próximo, sozinho, não decide nada (§2.5 proíbe tratar proximidade
como redundância).

### 1.4c ✅ A identidade feminina TEM assinatura na folha: cintura sobe E quadril encolhe

O `zen_f_b09_d3` lê masculino por três traços — *peitoral em vez de busto, sem
afunilamento de cintura, quadril estreito*. Os dois últimos são **mensuráveis na
folha**: `cintura/quadril` subindo **ao mesmo tempo** que o quadril absoluto cai.

Pego em 30/07 numa folha do Gemini antes da Meshy: `cintura/quadril` 0,594 →
**0,651** com quadril **−0,62 pp**. Massa tinha ido na direção certa e o
alinhamento era o melhor do dia (0,14%) — a folha teria passado por qualquer
outra trava. **Rodar esta conferência em toda folha feminina**, e não confundir
com a 1.4b: lá a razão parada reprova, aqui é a razão subindo *com quadril
caindo* que reprova.

⚠️ **Esta trava dá FALSO POSITIVO em passo descendente** — descoberto na sessão
17. Quando o corpo inteiro encolhe, o quadril cai em absoluto por construção, e
`cintura/quadril` sobe em quase toda folha mais leve. As três descidas aprovadas
da sessão 17 disparam esta assinatura e **as três geraram corpo feminino
limpo**. Ao ver o padrão numa folha mais leve que a âncora, não reprovar por ele
— usar a §1.4d, que é a régua que separou os casos de verdade.

### 1.4d ✅ A régua que PEGA a leitura masculina: `ombro/quadril` na folha 2D

Construída na sessão 17 medindo as **dez folhas `d3` que já viraram avatar**, e
comparando com o parecer de anatomia de cada corpo. As seis que geraram corpo
feminino ficam num cluster estreito:

| folha | `ombro/quadril` | lê |
|---|---:|---|
| `b07_d3` · `b08h_d3` · `b06h_d3` · `b05_d3` · `b04_d3` · `b08_d3` | **0,940 a 1,050** | feminino |
| `b09_d3` | **1,212** | **masculino** |

Duas folhas medem 0,462 e 0,148 — é a régua do ombro quebrando (ver abaixo), não
corpo. **Descartar leitura de ombro fora de 0,9–1,3.**

Isso reprovou duas folhas do `b03_d3` antes da Meshy (**1,103** e **1,104**) e
aprovou a terceira (**1,059**) e o `b02_d1` (**1,029**), que vieram femininos.

⚠️ **O que ela NÃO pega.** O par 3D `quadril/peito` só acusa o caso extremo: na
biblioteca feminina inteira o único fora do cluster é o `b10_d3` em **0,879** (a
caricatura), enquanto o `b09_d3` — que também lê masculino — dá **1,142**, no
meio do pelotão. Ou seja: **proporção pega estrutura de tronco, e não pega busto
virado peitoral nem mandíbula.** Esses dois continuam sendo olho no preview.

⚠️ **A leitura do ombro quebra sozinha.** O `sheet_qa` mede a `at_frac` fixa
0,194, e num corpo de proporção diferente essa linha cai fora do deltoide: já deu
`cintura/ombro` **1,543** (ombro mais estreito que a cintura, o que não existe) e
70 px contra 189 px da âncora. É a mesma família da pegadinha do `thigh`.
**Descartar a medida e resolver pela imagem quando ela sair dessa faixa.**

### 1.5 Duas estimativas concordando não são uma confirmação

Estimei o IMC de uma folha por volume (~28) e pela regra aditiva (29,4), vi as
duas baterem e escrevi que a regra estava confirmada no feminino. Medido:
**27,3**. Eram dois palpites meus, e palpites que partilham o método partilham o
viés. Antes de escrever "confirmado", separar o que é **medida** do que é
**estimativa minha**.

### 1.6 Calibrar régua nova rodando na peça já aprovada

Os três defeitos do `sheet_qa` apareceram de uma vez ao rodar a versão nova na
folha-mãe aprovada. Não é passo extra — é o método.

#### 1.6b 👁️ MINIATURA não é leitura de anatomia — recortar e ampliar

Meu olho também é uma régua, e ela tem resolução. Uma folha de 1536×1024 chega
até mim perto de **384×256**, e nessa escala a diferença entre *"o mesmo corpo
mais leve"* e *"outro corpo"* simplesmente não existe.

Na sessão 18, com o **último crédito da Meshy** em jogo, li a vista de perfil do
`f_b04i_d1` como mais magra que a frente e as costas — o que, se fosse verdade,
faria a Meshy fundir três corpos diferentes. As medidas não acusavam nada (razão
perfil/frente do quadril **0,613**, dentro do padrão da série). Recortei o perfil
da folha nova e o da âncora, colei lado a lado ampliados 1,4×, e **eu estava
errado**: mesma família de corpo, só mais leve. Repeti com a frente. Coerentes.

**O reflexo certo quando o olho e a medida discordam não é escolher um dos dois
— é melhorar o olho.** Recortar a região em disputa das duas folhas, colar lado a
lado, ampliar, olhar de novo. Custa segundos, e é a diferença entre reprovar uma
folha boa e aprovar uma ruim. Apagar o arquivo de comparação depois.

⚠️ **Vale também para a divergência frente × perfil.** O `sheet_qa` mede as duas
vistas mas **não cruza uma com a outra**: nenhuma trava dispara se as 3 vistas
mostrarem corpos diferentes. Delta de perfil muito maior que o frontal (aqui:
barriga −3,24 pp contra ombro −1,01 pp) pode ser o descritor pegando **ou** as
vistas discordando, e só o olho ampliado separa os dois casos.

### 1.6c ⚠️ NÃO dispensar um alarme ANTES de ele tocar

Variante pior das anteriores: nas outras eu deixei de perguntar o que a régua
media; aqui eu emiti **dispensa antecipada para um sinal que ainda não tinha
visto**.

Ao mandar o `zen_f_b12_d1` para a Meshy, escrevi: *"se este vier acima de
188.310 tri, é normal e não é defeito"*. Veio com **245.594**, 30% acima do
recorde da biblioteca, e a dispensa já estava dada. O corpo mediu **IMC 114,2**
contra 48–55 previstos.

**O gatilho é reconhecível:** toda vez que a frase começa com "se vier X, é
normal", estou construindo a razão de ignorar a medida antes de ela existir — o
espelho da §6.6, que proíbe explicar um desvio antes da medida. Lá eu inventava
culpado cedo demais; aqui, inocência.

**Regra:** avisar sobre a FAIXA esperada é legítimo; declarar de antemão que um
valor fora dela não é defeito, não é.

> **E o alarme ordinal não tem TETO.** O `sheet_qa` da mesma folha deu **`quadril
> +15,61 pp`**, contra os +7,10 pp da folha que já tinha estourado em 42,6. Eu li
> como *coerente com o pedido*, porque o pedido era mesmo um passo grande. A
> leitura ordinal estava **correta** — e é por isso que ela não protege: "muito
> maior que a âncora" é compatível com 55 e com 114. **O alarme ordinal distingue
> direção e ordem de grandeza, nunca magnitude.** Quando o pedido já é "vá para o
> extremo", ele concorda com qualquer resultado grande e perde todo o poder de
> discriminar. **Ao mirar um extremo, nenhuma régua pré-Meshy informa nada** —
> mirar por palavra de categoria (§2.2) e aceitar que o pouso é descoberta.

> **A contagem de tri crua da Meshy é alarme ordinal, e SÓ nos extremos.** Ela
> não ordena o meio da linha feminina: o `b07_d1` tem **153.859** tri e 96,6 L, o
> `b08_d1` tem **142.410** e **129,0 L** — mais triângulos, menos corpo. Nos
> extremos fala alto (245.594 → 346,4 L, contra o recorde anterior de 188.310 →
> 163,6 L). **Não construir preditor com isso** — seria o quinto, e os quatro
> anteriores morreram do mesmo jeito (§2.6).

### 1.7 🔴 A régua tem que ser a MESMA dos dois lados — e "mesmo nome" não basta

Descoberto em 01/08 ao ler o app Zenith para a integração. A biblioteca mede
`waist_navel` (altura fixa do umbigo) **e** `waist_min` (ponto mais estreito), e o
`build_index.py` indexava pelo primeiro. O guia do app ensina o usuário a medir
*"a parte mais estreita do abdômen"* — ou seja, o **segundo**.

| | diferença `waist_navel − waist_min` |
|---|---|
| mediana, faixa de usuário (IMC 17–40) | **6,5 cm** |
| máximo na faixa de usuário | **24,2 cm** |

6,5 cm é mais do que separa dois avatares vizinhos da grade, o erro é
**sistemático para o lado gordo**, e **nenhuma trava o pegaria** — os dois lados
estão internamente corretos. É a §1.3 (consistência interna não é correção)
aplicada a uma fronteira entre repositórios.

**O `shoulder_cm` do app é o mesmo caso, pior:** o campo mora ao lado de
`chest_cm` e `hip_cm`, todas circunferências, mas o guia manda medir **largura**
de um deltoide ao outro. Nome igual, grandeza diferente.

> **Ao integrar com outro sistema, o contrato não é o NOME do campo — é a
> DEFINIÇÃO OPERACIONAL de como aquele número é obtido.** Antes de comparar
> qualquer medida com a de fora, ler como o outro lado instrui a coletá-la.

### 1.7b Ler o TEXTO da especificação não é ler a especificação

Derivei a metodologia de medida do app do **texto** das instruções e concluí que
ombro era largura. O Rogério me parou: *"tem que ver se a tela que guia o usuário
a medir o ombro segue essa metodologia sua"*.

Auditados os 10 PNGs de `assets/medidas/` contra os próprios textos, saiu uma
lista de três divergências: peitoral, coxa e ombro.

**O usuário não lê o parágrafo — ele olha o desenho.** Quando a especificação
existe em dois suportes, quem manda é o que o usuário consome, e conferir só um
é a mesma falha de §1.3 com outra roupa.

> ### 🔴 E na sessão 20 a MESMA lição me pegou de novo, um nível abaixo
>
> Dos três defeitos acima, **dois estavam errados.** Medidos os pixels em 01/08:
> o peitoral **é anel** e o texto pede circunferência — coerente, nada a fazer; o
> ombro **é anel** no arquivo commitado, e o único problema é o texto. Só a coxa
> se confirmou.
>
> **Como eu errei tendo acabado de aprender a olhar o asset:** eu li o
> **cabeçalho de comentário** do `measurement_guide_page.dart`, que diz *"v4.2 —
> Peitoral entrou (a barra horizontal no peito era peitoral, não ombro)"*, e
> descrevi o PNG a partir dele. Cabeçalho de arquivo é **texto sobre o asset**,
> não o asset. Troquei um parágrafo por outro parágrafo e me convenci de que
> tinha olhado o desenho.
>
> **Abrir o arquivo binário e medir é o único ato que conta.** "Consultei o
> arquivo" não é o mesmo que "consultei o conteúdo do arquivo" — e a versão
> anterior deste próprio parágrafo é a prova, porque ela publicou três defeitos e
> dois não existiam.

### 1.7c ✅ O render do OUTRO lado vira régua externa — e ele se auto-calibra

Os 9 renders do guia do app desenham um anel roxo na altura em que a fita deve
passar. Isolando o anel por componente conexa e dividindo pela altura da figura,
sai um `at_frac` **na mesma unidade** que o `metrics.py` usa. Ele nasceu no outro
repositório, sem combinação — é a §1.3 satisfeita de verdade.

E ele **prova a própria calibração antes de acusar ninguém**:

| guia do app | anel | `metrics.py` | |
|---|---:|---:|---|
| Glúteo | 0,507 | `hip` 0,507 | ✅ 0,000 |
| Cintura | 0,645 | `waist_min` 0,644 | ✅ 0,001 |
| Pescoço | 0,862 | `neck` 0,873 | ✅ |
| Coxa | 0,394 | `thigh` 0,460 | 🔴 app errado — 11,6 cm |
| Panturrilha | 0,214 | `calf` 0,320 | 🔴 **biblioteca errada** |

> **Duas concordâncias em 0,001 é o que dá direito de chamar as outras de
> divergência.** Régua externa que só discorda não distingue "o outro errou" de
> "eu não sei ler o outro".

⚠️ **Braço e antebraço ficam FORA da tabela**: o master está em A-pose e o desenho
tem braço caído, então as alturas não são comparáveis. Divergência ali não é
defeito — é a §1.1 (perguntar o que a régua NÃO mede) aplicada antes de acusar.

### 1.8 🔴 Extremo que pousa na BORDA da banda não é extremo — é corte

O achado mais caro da sessão 20, e ele viveu na produção inteira sem ninguém ver.

`CALF_BAND` procurava o máximo em 0,180–0,320 da estatura. **50 dos 76 avatares
travavam em 0,320 exato — a borda da própria banda.** A 0,320 (56 cm do chão) a
fatia pega a base da coxa, porque a linha do joelho fica em ~0,285. Os 16 que
escapavam achavam o pico em 0,206–0,223, que é onde o ventre da panturrilha
realmente está. **A coluna media duas partes do corpo diferentes sob o mesmo
nome**, e é uma das que o app consome.

Correção mediana ao arrumar a banda: **−2,2 cm** na faixa de usuário, máxima
−5,6 cm.

**Por que nada pegou:** todas as travas olhavam **quanto** a medida valia, e
nenhuma olhava **onde** ela tinha caído. Um valor de panturrilha de 48 cm num
corpo grande não parece absurdo — o absurdo estava no `at_frac`, que ninguém
lia. É a §1.2 (trava que confere o alvo contra ele mesmo) na família das bandas.

> **Toda busca por extremo dentro de um intervalo tem que denunciar quando o
> extremo encosta na borda.** Se o máximo está na borda, o verdadeiro máximo
> provavelmente está do lado de fora, e o número entregue é o limite da banda
> disfarçado de medida.

Feito: o `metrics.py` grava `at_band_edge: hi|lo` em toda medida de extremo, e o
console lista os casos. **Exceção documentada:** na coxa o `hi` é *esperado* — ela
é mais larga colada na virilha, então o máximo cai no teto por anatomia. Mesmo
sinal, significados opostos; por isso a coluna está excluída do aviso, com
comentário no código dizendo por quê.

### 1.8b 🔴 Medida de fita é LANDMARK, não extremo — e a trava nova provou isso na hora

O `INTEGRACAO_ZENITH.md` §6.2 mandava trocar o `chest` de fração fixa (0,720) para
"máximo numa banda", porque o guia do app pede *"a parte mais larga do peitoral"*.
Implementei, e criei o `shoulder` novo pelo mesmo desenho. **As duas estavam
erradas, e o `at_band_edge` da §1.8 denunciou na primeira rodada de teste:**

| | banda testada | para onde o máximo fugiu |
|---|---|---|
| `chest` | 0,715–0,775 | subiu para a **axila**: 78,2 → 86,2 cm no `b01_d1`, onde dorsal e deltoide entram no casco convexo |
| `shoulder` | 0,760–0,825 | desceu para o **tórax** em 2 de 3 avatares, travando no piso da banda |

O comentário que já estava no arquivo avisava do risco pela **barriga**; o risco
real era o oposto, e só aparece em corpo magro — no obeso o `arm_split` corta
antes e esconde.

> **"A parte mais larga" na instrução ao usuário quer dizer *onde na circunferência
> encostar a fita*, não *procure o máximo ao longo do corpo*.** Peito é a linha do
> mamilo, ombro é a linha dos deltoides. São pontos anatômicos. Máximo ao longo do
> eixo vertical sempre acha uma junção — axila, virilha, joelho — porque é lá que
> dois volumes se somam.

As duas voltaram a landmark fixo: `CHEST_FRAC = 0.720` (byte a byte igual ao de
antes) e `SHOULDER_FRAC = 0.795`, esta última **adotando a altura que o render do
app define** (§1.7c). A §1.8 se pagou antes de a §1.8 terminar de ser escrita.

### 1.8c ⚠️ A tolerância que eu invento não é o critério — o critério está no código

Ao mandar regerar o `coxa.png`, declarei alvo `at_frac 0,460 ± 0,010`. O render
novo veio em **0,441** e errou a tolerância. Aprovei mesmo assim, e isso só não é
mover a trave porque **o ±0,010 nunca foi derivado de nada** — inventei como
"precisão de medição", que não é a pergunta.

O critério certo já existia: o `metrics.py` define coxa como o máximo nos **6 cm
abaixo da virilha** (`THIGH_BAND_M`), ou seja a faixa **0,432–0,466**. O anel novo
caiu em 0,441, **dentro da banda que a própria biblioteca usa para dizer o que é
coxa**; o antigo, em 0,394, estava fora por 7 cm.

> **Antes de arbitrar tolerância, procurar se o sistema já define a faixa
> aceitável em algum lugar.** Número que eu invento na hora de julgar tende a
> virar discussão sobre o número; constante que já está no código é critério
> verificável e não precisa de defesa.

---

## 2. Mirar um IMC — o que funciona e o que não funciona

O gerador de imagem tem **atratores**: pontos para onde o corpo cai
independentemente do que se pede. Mirar é escolher atrator, não ajustar número.

### 2.1 O que NÃO move o corpo

- **adjetivo de intensidade** ("bem mais musculoso", "passo contido")
- **número relativo** ("~10% mais massa")
- **interpolação** — pedir o meio-termo exato entre duas anexas devolve a folha
  maior. Testado, falhou.
- **baixar a âncora**, se o substantivo não mudar: baixar 3,4 moveu o pouso 0,7

### 2.2 O que move: o SUBSTANTIVO DE CATEGORIA

Trocar "homem musculoso e seco de academia" por "FISICULTURISTA DE COMPETIÇÃO"
moveu o pouso **6,4** pontos de IMC no masculino, e **+6,3** no feminino (22,1 →
28,4, `f_b08_d3`) — **a única constante que replicou entre os sexos.**

**Um vão é o vazio entre dois atratores nomeáveis.** Se não existe palavra de
categoria entre os dois, nenhuma âncora e nenhum adjetivo colocam corpo ali.

⚠️ Cuidado com o inverso: **nomear o atrator e negar a saída** ("musculoso e
seco, NÃO um fisiculturista") trava o passo — no `b06i_d3` o delta caiu de +6,5
para +3,3, e no `f_b05_d3` o corpo veio em 21,0 contra 22–26 previstos.

⚠️ E **passo por banda seguinte é pequeno na `d3`**: 21,0 → 22,1 foi **+1,1**. A
base da `m d3` também é comprimida (19,9 · 20,8 · 21,1), então não é atrator
travando o feminino — as bandas `b02`–`b06` da `d3` têm pouca massa entre si por
natureza. Para andar ali, trocar o substantivo.

### 2.2b Descritor inerte se conserta com CATEGORIA DO MUNDO REAL, não com adjetivo

O `f_b07_d3` era *"Muito musculosa. Massa alta com baixa gordura, ombros muito
largos…"*: só intensificador, e o `state.md` já o tinha marcado como inutilizável
por causa da §2.1. Trocado por **"ATLETA DE WELLNESS DE COMPETIÇÃO"** — uma
divisão de fisiculturismo que existe, com regras de julgamento próprias — rendeu
**IMC 27,7** e um corpo inédito na biblioteca.

**O critério não é "substantivo em vez de adjetivo", é se a palavra nomeia algo
que o gerador já viu julgado.** "Wellness" carrega uma forma inteira; "muito
musculosa" não carrega nenhuma. É a §2.2 vista pelo avesso: um vão é o vazio
entre atratores nomeáveis, então **procurar o nome antes de concluir que o vão é
intransponível.**

### 2.2c A DIREÇÃO DO VOLUME é um 2º lever, independente do tamanho

Junto do descritor de wellness foi ao slot: *"o volume cresce principalmente na
METADE DE BAIXO do corpo — glúteos, quadril e coxas […] enquanto a cintura
permanece estreita"*. Contra o `f_b08_d3`, com **0,7 de IMC a menos**:

| | `b07_d3` | `b08_d3` | Δ |
|---|---:|---:|---:|
| coxa | 74,1 | 75,0 | −0,9 |
| quadril | 122,7 | 120,4 | **+2,3** |
| peito | 93,2 | 100,0 | **−6,8** |
| bíceps | 31,1 | 34,3 | **−3,2** |
| cintura mín | 64,3 | 68,5 | **−4,2** |

Cresceu embaixo **e encolheu em cima**. `cintura/quadril` **0,524** e
`quadril/peito` **1,317** são os extremos da série `d3` inteira, e a cintura de
64,3 cm é mais fina que a da `b05_d3`, que tem **IMC 21,0**.

**Consequência de método: dá para mover FORMA sem mover IMC.** A grade de bandas
só indexa tamanho, então esse eixo é invisível nela — dois avatares a 0,7 de IMC
podem ser corpos diferentes para o usuário. Não é motivo para abandonar a grade,
é motivo para **não tratar proximidade de IMC como redundância**.

✅ **Confirmado no extremo, no mesmo dia:** o `f_b06h_d3` saiu a **0,2 de IMC** da
âncora (22,1 → 22,3) e ainda assim é outro corpo — cintura **−1,9 cm**, quadril
**+2,2**, coxa **+2,1**, bíceps **−1,7**, `cintura/quadril` 0,614 → **0,584**.
Forma andou, tamanho não andou nada.

⚠️ **Mas esse mesmo avatar é o contraexemplo: eu queria +2,9 e recebi +0,2.**
Mirando o vão 22,1→27,7 eu empilhei **três freios de uma vez**: a categoria mais
leve que existe ("bikini fitness… **NÃO** por volume muscular"), a instrução *"o
passo é PEQUENO"*, e três negações — *"NÃO aumentar ombros, NÃO aumentar braços,
NÃO engrossar as coxas"*. É exatamente o "nomear o atrator e negar a saída" da
§2.2, que já tinha custado o `b06i_d3` (+3,3 contra +6,5) e o `f_b05_d3`.

**A regra que faltava: escolher UM lever por folha.** Categoria governa tamanho,
direção de volume governa forma. Querendo tamanho, trocar a categoria e **não
pôr negação nenhuma**; querendo forma sem tamanho, manter a categoria e só dirigir
o volume. Empilhar os dois com negações não dá "um passo médio" — dá zero.

⚠️ **E o medo veio do lugar errado:** o fator ~2× da §2.3 é de *bracketing*, e eu
apliquei o freio dele a um lever que não é bracketing. **Régua de um método não
calibra outro** — é a 5c aplicada ao próprio prompt.

⚠️ **E isso quebra o alarme ordinal se ele for lido no eixo errado.** Antes da
Meshy, minha primeira leitura da folha foi de *massa total* — "lê no nível do
`b08`, redundante" — e teria reprovado uma folha boa. A leitura certa saiu ao
comparar o pedido com a medida: ombro −0,72 pp e quadril +2,29 pp contra o `b08`.
**Perguntar que eixo o prompt mandou mover, e medir esse.** Mesma família do
`f_b04_d2`, onde a largura frontal parada escondia +4–5% de profundidade.

### 2.3 Bracketing — e seus três limites

Anexar **duas** folhas consecutivas aprovadas e pedir "a próxima etapa, com um
passo do MESMO TAMANHO". Entrega **~2× o passo pedido** (medido 1,9× · 2,0× ·
2,2×).

⚠️ **Não funciona com âncoras coladas.** O modelo tem passo mínimo e ignora
pedido menor que ele. Com par a **0,7 de IMC**, pedi 24,5–25,9 e recebi **27,3**.

⚠️ **O fator 2× só vale em espaço aberto.** Perto de um atrator forte o passo
explode — medido **8×** (`b05i_d1`: pediu passo 1,6 mirando ~31, entregou +12,9 e
aterrissou em 40,7, acima do próprio vizinho superior do vão).

⚠️ **Para pares muito parecidos, não pedir identificação** — pedir "um corpo
mais pesado que os DOIS anexos, com um passo do tamanho da diferença entre eles"
dispensa a ordenação e a direção sai correta.

### 2.4 O passo é do GERADOR e tem SINAL — não é do sexo

`pouso ≈ âncora de topo + passo do gerador`, quase independente do que se pede.
**Fator multiplicativo não prevê nada** (as mesmas amostras dão de 1,9× a 8,0×);
a regra que funciona é **aditiva**.

| gerador | subindo | descendo |
|---|---|---|
| ChatGPT | +4,4 · +6,8 · **+8,6** | −3,9 · −1,8 · **−7,8** |
| Gemini | +7,1 · +7,2 · **+19,3 · +20,6** | **−4,3** |
| masculino (Gemini) | +6,2 · +7,2 · +8,1 · +8,3 | — |

**Escrevi "passo ~4 no feminino" e estava errado** — as duas amostras eram do
ChatGPT. O Gemini feminino deu +7,1 e +7,2 (duas amostras a 0,1 uma da outra),
que bate com o +6,5 masculino do mesmo gerador. **O que muda o passo é a
ferramenta, não o sexo.**

**Receita, e ela tem duas metades:**
- **subindo no Gemini:** âncora em **alvo − 7**. Fechou o vão 27,3→34,4 com
  previsão declarada de 29–31 e medido **30,1** — a primeira vez no projeto que
  um alvo de IMC foi previsto e acertado.
- **descendo no Gemini:** âncora em **alvo + 4,3**. Fechou o vão 16,5→23,3 com
  previsão 18,5–21,5 e medido **19,0**.

⚠️ **Acima de ~30 o passo do Gemini feminino TRIPLICA**, e duas amostras
concordam: `f_b08_d1` (âncora 23,3, previsto 27–31, medido **42,6**, +19,3) e
`f_b11_d1` (âncora 31,9, previsto 36–45, medido **52,5**, +20,6). O +7,15 vale
só nas bandas onde foi medido (22,9–27,3); acima disso, **prever faixa larga**.

⚠️ **A regra aditiva quebra em cima de um atrator**, igual ao fator
multiplicativo: no `zen_m_b06i_d3` o delta foi **+3,3** em vez de +6,5, porque o
descritor nomeava o atrator e negava a saída (§2.2). Antes de aplicar, conferir
se o descritor não está apontando para um atrator conhecido.

⚠️ **Ao subir no Gemini, não repetir no parágrafo de âncora os traços que o
descritor já nomeia** — reforço redundante de volume é candidato a causa do
estouro do `f_b08_d1`. Usar o parágrafo só para direção e continuidade de
personagem.

#### 2.4c 🔴 O SINAL domina o TAMANHO: subindo estoura, descendo é fino

Sete gerações da sessão 17, todas no ChatGPT feminino, todas com âncora anexa e
cláusula de direção. **A assimetria é de uma ordem de grandeza:**

| direção | avatar | âncora | previsto | medido | passo |
|---|---|---:|---|---:|---:|
| ⬆️ | `f_b11_d2` | 34,4 | 42–46 | 59,7 | **+25,3** |
| ⬆️ | `f_b05_d1` | 24,1 | 28–31 | 44,4 | **+20,3** |
| ⬆️ | `f_b10_d3` | 30,1 | 36–42 | 45,1 | **+15,0** |
| ⬆️ | `f_b04_d3` | 22,3 | ~25 | 29,9 | **+7,6** |
| ⬇️ | `f_b03_d3` | 21,0 | ~19 | 16,1 | **−4,9** |
| ⬇️ | `f_b02_d1` | 19,0 | 17,5–18,5 | 16,4 | **−2,6** |
| ⬇️ | `f_b01_d2` | 18,3 | 16–17 | **17,2 ✅** | **−1,1** |

**Subindo, o menor passo medido foi +7,6** — e veio da categoria mais moderada
que existe (Figure, uma divisão entre duas já medidas). **Descendo, o maior foi
−4,9.** As quatro subidas estouraram a faixa declarada; a única previsão que caiu
dentro em toda a sessão foi uma descida.

**Consequência prática: vão estreito só se fecha DESCENDO.** Ancorar acima do
alvo e pedir corpo mais leve. Ancorar abaixo e pedir mais pesado atravessa o vão
inteiro e pousa do outro lado — foi o que enterrou o `f d1` 24,1→31,9 (pousou em
44,4) e o `f d2` 34,4→52,6 (pousou em 59,7).

**A causa é empilhamento de lever, e é a §2.2c aplicada à direção.** Âncora com
cláusula de direção **é um lever**; categoria mais pesada que a da âncora **é
outro**. Os dois apontando para o mesmo lado somam. Descendo eu usei categoria
moderada e o passo ficou fino; subindo eu usei categoria extrema *e* direção, e
estourou. **Um lever por folha vale para a direção também.**

⚠️ **A sessão 18 esticou o envelope de descida para −5,4, e mediu que descida
TAMBÉM erra.** As duas gerações foram descidas no ChatGPT feminino:

| avatar | lever | âncora | previsto | medido | passo |
|---|---|---:|---|---:|---:|
| `f_b03_d2` | categoria (bailarina clássica) | 22,2 | ~20 | **19,8 ✅** | −2,4 |
| `f_b04i_d1` | âncora-com-direção, sem trocar categoria | 31,9 | 27–29 | **26,5** | **−5,4** |

O `b04i_d1` **estourou a faixa declarada para baixo**. A assimetria da §2.4c
continua valendo — descida erra por ~1,5 ponto, subida erra por 7,6 a 25,3 — mas
**"descendo é fino" não quer dizer "descendo é previsível"**. Ao declarar faixa
numa descida, abrir ±2 em torno do alvo, não ±1.

#### 2.4e ✅ Vão menor que ~6: o lever é a ÂNCORA, e ela funciona SOZINHA

O `CHARACTER_BIBLE` já dizia que passo menor que ~6,3 não se fecha trocando
descritor, porque o passo mínimo entre duas categorias do mundo real é ~6,3. O
que faltava era medir o lever-âncora **isolado** — sem categoria nova junto.

O `f_b04i_d1` fez isso: manteve a categoria da âncora (mulher sedentária sem
tônus, a mesma do `f_b07_d1`) e o slot `{TIPO_DE_CORPO}` disse apenas *"é
EXATAMENTE O MESMO TIPO DE CORPO da folha anexada, porém MAIS LEVE"*, seguido de
**duas listas explícitas**:

- **o que MUDA** — barriga menos projetada de perfil, quadril menos largo, coxas
  menos grossas, braços menos cheios;
- **o que NÃO MUDA** — a ausência total de tônus, os contornos redondos, a
  cintura sem afunilamento, os ombros caídos.

Passo −5,4 num vão de 7,8, com a linha de definição preservada (a sonda de tônus
deu abdômen −6,8%, e o preview veio sem nenhum músculo desenhado). **A lista do
que NÃO muda é o que segura a linha `d1`** — sem ela, "mais leve" tende a virar
"mais tonificada", que é outro eixo.

#### 2.4d ❌ NEGAÇÃO NÃO VENCE ATRATOR — três medidas na mesma sessão

Cláusula de negação explícita, literal, em maiúsculas, falhou **três vezes em
sete folhas** — sempre quando o atrator do gerador estava do outro lado:

| negação escrita no prompt | o que saiu |
|---|---|
| *"Ela NÃO É OBESA: sem dobras, sem avental"* | IMC **44,4** — obesidade grau III |
| *"ELA É UMA MULHER… NÃO tem peitoral masculino"* | `f_b10_d3`, fisiculturista **masculino caricato** |
| *"os OMBROS DELA SÃO ESTREITOS"* | ombro **alargou**, `ombro/quadril` 1,030 → 1,103 |

A §2.2 já dizia que adjetivo de intensidade não move corpo. Isto é mais forte:
**a negação não é lever nenhum quando o atrator é forte.** Ela só funciona onde
o corpo pedido já está perto do que sairia de qualquer jeito — nos dois acertos
da sessão (`b01_d2` e `b02_d1`) a mesma cláusula de quadril pegou, porque ali não
havia atrator puxando contra.

**O que fazer no lugar:** trocar o gerador, ou trocar o alvo. Redação nova sobre
o mesmo atrator é a definição de gastar geração (§2.5b).

### 2.5 As lacunas são do GERADOR — e são a falta de uma PALAVRA

Nenhum gerador é melhor; eles têm atratores em lugares diferentes, então o vazio
de um é coberto pelo outro. Os atratores medidos até 30/07:

**ChatGPT feminino — ~18 · ~22–27 · ~32–35 · ~54 · ~114:**

| descritor | pousou |
|---|---:|
| "magra" (mirando 20–21,5) | ~17,0 · ~17,5 |
| "peso normal" | 23,3 |
| `f_b08_d3` "Físico de fisiculturista feminina" | 28,4 |
| `f_b07_d1` "Sobrepeso leve" | **31,9** |
| `f_b06_d1` "Peso normal alto" | **34,1** |
| `f_b09_d2` "Corpo grande e forte" | 53,9 |
| `f_b12_d1` "Obesidade grau III" | **114,2** |

**Gemini feminino:** "Obesidade grau I" → 34,4 · "Sobrepeso" → 42,6 ·
"Obesidade grau II" → 52,5 · `f_b09_d3` "Fisiculturista pesada" → 32,4.
**Masculino (Gemini):** "OBESIDADE GRAU I" → 33,3 e 34,0 · "SOBREPESO, não
obeso" → 26,9.

**O mesmo substantivo pousa 10 pontos diferente em cada gerador** — `f_b07_d1`
"Sobrepeso leve" dá 31,9 no ChatGPT e ~42 no Gemini. Atrator medido num gerador
**não transfere**, do mesmo jeito que o passo não transfere. Ao trocar de
gerador, a previsão volta a ser faixa larga.

**A única constante que atravessou os dois sexos é "OBESIDADE GRAU I" no Gemini,
em ~33–34** (33,3 · 34,0 masculinos, 34,4 feminino). Quando o alvo for essa
faixa, é tiro de uma geração.

**Entradas novas (30/07, sessão 16) — ChatGPT feminino, extremo pesado:**

| descritor | âncora anexa | pousou |
|---|---|---:|
| "powerlifter feminina / obesidade grau I" | **nenhuma** | **52,6** |
| "mulher no começo da obesidade, NÃO mórbida" | **nenhuma** | **55,1** |
| "corredora de maratona de elite" (`d3`) | 18,3 | **16,9** |

### 2.5b ⛔ SATURADO: o vão `f d1` 34,1 → 42,6 — os dois geradores falham, em direções opostas

**Cinco gerações em 30/07, e o resultado é uma medida, não um fracasso.** Este vão
já não é candidato a folha: é caso para **shape key** no sistema híbrido, que é o
4º degrau da escada de escalonamento e onde ela de fato termina.

| gerador | âncora anexa | descritor | resultado |
|---|---|---|---|
| ChatGPT | nenhuma | "começo da obesidade" | **55,1** medido |
| ChatGPT | par 24,1 + 31,9 | "obesidade grau I" | folha ordinalmente **maior** que a de 55,1 |
| ChatGPT | 31,9 | "obesidade grau I" | idem |
| Gemini | 19,0 | "obesidade grau I" | **Δ 0** — copiou a âncora |
| Gemini | 19,0 **+ cláusula de direção explícita** | "obesidade grau I" | **Δ 0** — copiou a âncora |

- **ChatGPT não tem corpo entre ~34 e ~52** na direção `d1`. É a mesma zona morta
  da §2.5 documentada para 28–38, uma banda acima.
- **Gemini com âncora muito abaixo do alvo devolve a âncora.** Δ de 0,1 a 0,5 pp
  em todos os eixos, e a segunda tentativa trazia *"gere um corpo MUITO MAIS
  PESADO e MUITO MAIS VOLUMOSO"* em parágrafo próprio. **Não adianta gritar a
  direção**: com âncora a 19 pontos do alvo, a imagem ganha do texto.

⚠️ **Não reabrir com "mais uma formulação".** Cinco redações diferentes já foram
gastas. O que falta testar, se algum dia valer, é âncora **intermediária** no
Gemini (~28–31), que é a única célula da matriz que nenhuma das cinco cobriu.

**Os buracos medidos, e cada um é a falta de uma palavra:**

- **ChatGPT feminino 27 → 32**, firme: dois substantivos diferentes, um deles
  *nominalmente mais leve*, caíram no mesmo poço de ~32–35. **A ordem da tabela de
  descritores NÃO é a ordem dos pousos** — não usar a numeração da banda como
  escala de intensidade.
- **Gemini feminino 34,1 → 42,6:** entre "obesidade grau I" (~34) e "grau II"
  (~52) o gerador pula o 35–45 inteiro.
- **ChatGPT feminino, lado magro, 16,5 → 23,3:** duas gerações mirando 20–21,5
  caíram em ~17,0 e ~17,5; a única coisa que mudou até a folha que pousou em 23,3
  foi o substantivo ("magra" contra "peso normal") — passo de +6,8 com um, +1,1
  com o outro. O mesmo alvo no Gemini pousou em **19,0 de primeira**.
- **Acima de ~54 não há palavra nenhuma:** um único degrau de categoria no topo
  vale **+71,6**, quase 8× o maior passo já medido. Para um corpo em ~60–80, **não
  pedir por palavra de categoria** — não há uma.
- **ChatGPT feminino `d1`, poço em ~32:** duas tentativas na sessão 15 mirando
  ~28 a partir de 24,1. A 1ª (descritor pesado: "nunca treinou", "culote", "coxas
  que se tocam") foi reprovada pelo alarme ordinal antes da Meshy — deltas de
  **+8 a +12 pp** contra os +3 a +4 de um passo de +6,7. A 2ª, deliberadamente
  contida (*"peso normal alto… NÃO é obesa e NÃO tem sobrepeso marcado"*), pousou
  em **32,4** — colada nos 31,9 do `b07_d1`. **Amansar o descritor não tira o
  corpo do poço.**

⚠️ **Vão MAIS ESTREITO que o passo mínimo não se fecha por descritor.** A `f d3`
tem um vão de **5,4** (22,3 → 27,7) e o passo do substantivo é **~6,3**: a troca
de categoria pula por cima por construção. E entre "bikini fitness" e "CrossFit"
**não existe nome de divisão** para pôr no meio. Quando o vão for menor que o
passo, o lever é a **âncora**, não o descritor.

**Escada de categorias femininas medida na sessão 15 (ChatGPT, todas `d3` salvo
a última):** bikini fitness **22,3** · wellness **27,7** · fisiculturista
**28,4** · CrossFit de elite **29,0** · fisiculturista pesada **32,4**.

⚠️ **Inverter a direção ATRAVESSA o poço, mas não mira.** O mesmo `f_b07_d1` que
pousou em 31,9 subindo de 23,3 pousou em **24,1 descendo de 31,9**, mirando ~28.
Provou que o poço é atravessável — o corpo saiu do outro lado —, não que ele
para no meio. **Um vão ladeado por dois atratores devolve corpos nas MARGENS,
seja qual for a direção do ataque.** Resultado prático daquela folha: ganhou-se
um avatar e quase nenhuma cobertura.

**Ordem quando um alvo não sai:** (1) bracketing · (2) trocar o substantivo de
categoria · (3) descer pelo lado de cima, sabendo que o pouso sai numa margem ·
(4) trocar de gerador · (5) aceitar e cobrir por shape keys (os insumos,
`circumferences_cm`, já viajam no `library.json`).

⚠️ **Aviso de método:** eu retirei a doutrina inteira do buraco 27→54 quando só
o número de cima estava errado. "N tentativas falharam" prova que *aquelas N
formulações* falharam — e **uma amostra que derruba um limite não derruba o
fenômeno.** O buraco existia; só não ia até 54.

### 2.6 ❌ A folha 2D NÃO prevê IMC — quatro preditores, quatro mortes

**Esta seção é um registro de erro, não uma receita. Não reconstruir nada do que
ela descreve.**

A conta era `secção ≈ largura(frente) × profundidade(perfil)`, média das razões
contra a referência, um fator de desconto, aplicado ao volume conhecido. O
desconto existe porque a conta trata o corpo como elipse e ignora que cabeça,
braços, mãos e pés quase não mudam entre bandas.

**Nove amostras femininas, e o fator real vai de 0,50 a 1,62 sem estrutura que
sobreviva a amostra nova** — não em função do tamanho do cru (que vai de −22,6% a
+97,2%), não em função do Δombro, não monotônico dentro de cada direção.

**As quatro tentativas e como cada uma morreu — todas no mesmo roteiro: a
estrutura aparece nas amostras que a geraram e some na primeira de fora.**

| preditor | morreu em | custo |
|---|---|---|
| fator fixo ×0,55 | `f_b02` | previ 19,8–20,3, mediu **18,3** |
| reta em \|Δombro\| | `f_b04_d1` | reta mandava 1,00, real **0,64**; previ 25–27, mediu **23,3** |
| monotonicidade no tamanho do cru | `f_b07_d1` | 46% deu fator **maior** que 64%; previ 28,7–29,8, mediu **31,9** |
| limiar `\|cru\| < 15%` + duas âncoras | `f_b04h_d1` | as duas réguas concordaram em 27,1–28,8, mediu **24,1** |

O quarto é o mais instrutivo: eu o construí com **duas** amostras uma mensagem
depois de escrever *"não construir preditor novo com 4–6 amostras"*, e as duas
réguas que "confirmavam" uma à outra partilhavam o método, logo o viés (§1.5). O
fator real foi **1,62**, fora dos 0,50–1,00 que os oito anteriores ocupavam.

**A conclusão a manter é negativa, e é definitiva o bastante para parar de
tentar.** A folha 2D serve para:

- **(a) reprovar geometria** — alinhamento, altura, figuras cortadas. É o uso que
  nunca falhou.
- **(b) alarme ordinal** — "esse corpo é maior que aquele", "esse passo é grande
  demais". Crua +89% na folha do `f_b08_d1` gritava "isso é muito mais que um
  passo", e era.

Quem diz o número é o `metrics.py`, depois da Meshy (§5.5). **Registrar a
previsão continua valendo**, porque é ela que revela o erro — mas é palpite
declarado e não deve gastar tempo de cálculo.

---

## 3. Produção de folhas

### 3.1 Largar a folha-mãe no trecho magro

A mãe é um corpo atlético. Quando o alvo é bem mais magro que ela, o modelo copia
a musculatura dela e quebra a continuidade com o vizinho slim. Nesses casos,
anexar **só o vizinho imediato**. Confirmado na produção (`b03_d2` e `b04_d2` só
fecharam ao largar a mãe). A mãe volta a ser útil quando a banda-alvo se aproxima
ou passa do corpo dela.

### 3.2 Identificar anexos por CONTEÚDO, nunca por ordem ou nome

Não dá para contar que o modelo veja o nome do arquivo, e a ordem de upload ele
confunde. Escrever *"uma das folhas é visivelmente menos musculosa: essa é a
etapa anterior"*. Custa uma linha e você vê o erro antes de gastar a geração.

### 3.3 Altura é o único erro que o pipeline não corrige

Folha com altura diferente das anteriores: descartar sem tentar aproveitar.
⚠️ Mas conferir antes se a altura divergente não é o vazamento do `sheet_qa`
(§1.1) — foi por pouco que essa regra não descartou três folhas boas.

### 3.3b `--check` que grava não é `--check`

`crop.py --check` não escreve nada, mas ele **exige a folha já em
`00_input/sheets/`** — ou seja, o `intake.py` roda antes e **grava**. Na sessão 15
usei isso para auditar uma folha duvidosa, **reprovei a folha**, e ela ficou no
repositório. Na folha seguinte, com o mesmo id, o `intake` barrou corretamente
("folha aprovada não se substitui") e o **`crop` rodou na folha velha**, gerando
as 3 referências do avatar errado.

**Só apareceu porque a variação de altura veio 1,52% em vez dos 0,22% que o
`sheet_qa` tinha acabado de medir na folha nova.** Sem esse número, teria ido
para a Meshy uma folha reprovada.

**Regra: para auditar folha que pode reprovar, usar um id descartável** (ex.
`zen_f_tmp`), nunca o id real. E ao ver o `intake` recusar, **parar** — não seguir
para o `crop`, porque ele vai rodar em conteúdo antigo sem avisar.

### 3.4 Marca d'água na folha é proibida

Vira uma 4ª mancha sobre o fundo liso, quebra a detecção do `crop.py` e pode
chegar na Meshy como geometria. Para rótulo visível, rotular uma **cópia** fora
de `00_input/sheets/`.

### 3.5 A ÂNCORA move o IMC; o DESCRITOR move o TÔNUS — e são independentes

Abrir uma linha de definição nova **não exige folha-mãe própria daquela linha**.
Medido nas duas direções:

- **Abrindo a `f d1`:** anexo único `zen_f_b02_d2` (uma folha *com* tônus) e
  descritor `d1` mandando "sem nenhum tônus". Volume **−9,6%** (18,3 → 16,5) e
  relevo abdominal **2,171**, na mesma casa da mãe (2,080) — o corpo encolheu e o
  tônus não veio junto.
- **Abrindo a `f d3`:** âncora única na mãe `f_b05_d2` (22,9) e descritor `d3`
  pedindo a queda de gordura de ~25% para ~18%. Mediu **21,0** (63,6 L), 8/8, e o
  relevo **veio** (gomos e oblíquos legíveis já no GLB de 60k) — o descritor moveu
  o tônus e o IMC quase não andou.

Os dois eixos respondem a comandos diferentes sem interferir um no outro.

**Consequência operacional:** escolher a âncora pelo IMC que se quer (§2.4) e
deixar o tônus por conta do descritor. A trava é conferir o relevo com
`qa/probe/sondas/probe_tonus_f.py` **antes** de subir na Meshy — a régua de
largura não vê tônus (§1.1), e é justamente o eixo que o descritor está movendo.
Lembrando que a sonda afirma e não nega (§1.1).

### 3.6 O Gemini às vezes GRAVA um quadro incompleto do render

A imagem aparece **completa e correta na conversa**, mas o arquivo baixado é um
quadro intermediário — desenho borrado, membros dissolvidos, roupa faltando, e o
conteúdo ocupando só parte da tela (**x até 74,4%**, **y até 89,6%** de um canvas
2752×1536, o resto cinza vazio).

**Baixar de novo NÃO resolve** — três downloads do mesmo item vieram byte a byte
idênticos (SHA-256 igual): o asset armazenado é o quebrado. E **não é
intermitente**: três *gerações distintas* (4,55 · 4,42 · 4,76 MB) saíram
quebradas em 23 minutos. Screenshot também não serve (tela de 768 px, figura de
folha boa tem ~1340 px).

**✅ A saída é o botão "COMPARTILHAR IMAGEM"** — descoberto pelo Rogério, depois
que a versão anterior desta lição ("a saída é regerar") custou 25 minutos e três
gerações. Abrir a imagem → compartilhar → abrir o link em janela nova → baixar
por lá. A cópia vem íntegra, em **metade da resolução** (1376×768).

⚠️ **A saída do "compartilhar" também falha — medido na sessão 17.** Duas folhas
do Gemini chegaram inúteis naquela noite, e por dois motivos diferentes: uma veio
**byte a byte idêntica à âncora anexada** (SHA-256 igual ao
`zen_f_b05_d3_sheet.png` — o download trouxe o anexo de volta, não a geração), e
a outra veio com **terço direito cinza vazio, faixa marrom no rodapé, fundo de
ruído 187** (contra ~10 numa folha sã) e os braços dissolvidos. O `crop.py` acha
1 vista em vez de 3.

**Conferir SHA-256 da folha contra a âncora antes de medir** — é barato e evita
medir a própria referência achando que se está medindo uma folha nova. E
**nenhuma dessas duas falhas é evidência sobre o Gemini como gerador**: as duas
são do caminho de entrega, e confundi-las com atrator de gerador desperdiça a
única alternativa que existe quando o ChatGPT satura.

**Meia resolução é aceitável, inclusive em `d3`.** O `crop.py` normaliza toda
vista para 1200 px de altura, então a Meshy recebe o mesmo canvas das outras
folhas. A ressalva antiga (*"em `d3` com gomo abdominal, preferir regerar"*) era
hipótese minha nunca medida, e **caiu**: o `zen_f_b09_d3` é exatamente esse pior
caso — figura de **718 px ampliada 1,67×** — e saiu 8/8, com gomos, deltoide e
separação de quadríceps todos legíveis. **Não gastar geração por causa disso.**

> ⚠️ **Mas o mesmo avatar falhou no que eu NÃO vigiava:** saiu com **identidade
> masculina** (peitoral em vez de busto, sem afunilamento de cintura, quadril
> estreito), e o desvio estava visível na folha antes da Meshy. Eu declarei o
> risco *errado* e depois comemorei que o risco declarado não aconteceu.
> **Resolução não protege identidade** — ao olhar folha e preview, olhar as duas
> coisas.

**Como reconhecer folha quebrada em 5 segundos:** rodar o `sheet_qa.py` e ler
**só** a seção de detecção. Folha quebrada devolve **"figuras detectadas: 1"** e
fundo escuro (RGB ~139 em vez de ~200), porque a área cinza vazia domina a
imagem. O `crop.py` também barra, mas o `sheet_qa` responde sem escrever nada no
repositório.

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

### 4.2b O selo do Gemini passou: raio de isolamento em px absolutos

O `find_seal` do `intake.py` rejeitou uma estrelinha 48×48 na folha do
`zen_f_b11_d1`. Ela passava em tamanho, preenchimento e "mais clara que o fundo";
caiu **só no isolamento** — exigia 20 px de fundo limpo em volta, e a perna da
vista de costas passava a menos de 6 px. Corpo largo + meia resolução (a rota do
§3.6, hoje padrão) = folga pequena **em pixels**.

Banco de ensaio com 2 selos vistos a olho e 6 candidatos confirmados como corpo,
medindo a fração do anel que é corpo: **só o raio de 3 px separa os grupos** (0,0%
nos dois selos contra 1,4%…76,7% no corpo; a 6 px um selo já dá 1,1% e o grupo
encosta em 1,1%; a 20 px o selo é rejeitado). `SEAL_ISOLATION` passou de 20 para
**3**, e o detector corrigido acha os 2 selos reais nas 55 folhas com **zero falso
positivo**.

**A doutrina:** o critério sempre quis dizer *"não encosta no corpo"*; com 20 px
ele media **quanto vazio havia em volta**, que depende do tamanho do corpo e da
resolução da folha. Mesma família da §1.1 e do `TARGET_TRIS` (§1.2).

> **Pendência:** a folha `zen_m_b06i_d3` tem selo remanescente. Masculina, avatar
> já produzido — não se regera (§5.1). Anotado para quando a onda masculina
> reabrir.

### 4.2c O SLOT do Multi-View da Meshy não muda a malha — medido em 58 masters

O Rogério subiu a vista de perfil no slot **esquerdo** nos 39 masculinos e no
`zen_f_b08_d3`, e no slot **direito** nos outros femininos. O `logs/process.log`
só guarda `PASS/FAIL` da trava de simetria, então o número foi remedido sobre os
masters com `qa/probe/sondas/probe_simetria.py` (read-only, mesmo método
`symmetry_dev` do `process.py`).

| grupo | n | média | mediana | faixa |
|---|---:|---:|---:|---|
| slot esquerdo (39 m + `f_b08_d3`) | 40 | 0,288 mm | 0,247 | 0,133–0,633 |
| slot direito (18 f) | 18 | 0,334 mm | 0,297 | 0,121–0,667 |

**Sem efeito, e a prova é a estratificação:** por faixa de IMC o sinal troca de
lado — 16–22 dá 0,260 contra **0,186**; 22–30 dá **0,228** contra 0,272; 30–60 dá
**0,266** contra 0,423. Direção inconsistente entre estratos é ruído, não efeito.

**O que governa a assimetria é o TAMANHO DO CORPO**, não o slot: correlação com
IMC **r = 0,544** sobre 58 avatares. E a tolerância é 5 mm de média — a
biblioteca inteira vive entre 0,12 e 0,67 mm, **7 a 40× dentro da trava**.

⚠️ **O que essa régua NÃO decide: orientação frontal.** Se um slot invertesse
frente e costas, o placar sairia 8/8. Conferido no render lateral do `f_b08_d3`
(busto e barriga à frente, glúteo atrás): correto com o slot esquerdo. **Não
existe trava para isso; é olho no preview.**

### 4.2d 🔴 O `restyle.py` colidia com o PRÓPRIO nome de material — 76/76 falharam

Em 31/07, ao trocar o material de titânio para alumínio, o `restyle.py --all`
devolveu **0/76 ok**. A causa:

```python
obj.data.materials.clear()          # esvazia o SLOT do objeto...
obj.data.materials.append(zm.make_body_material(bpy))   # ...mas o datablock fica
```

`clear()` não apaga o datablock importado do master — ele permanece em
`bpy.data.materials` com **0 usuários**, ainda ocupando o nome `Zenith_Body`. O
material novo nasce então como **`Zenith_Body.001`**, e a trava de nome do próprio
script derruba o avatar. Conserto: remover os órfãos (`m.users == 0`) antes de
criar o novo.

**O defeito estava latente havia semanas e não era do dia.** Na fase roxa o master
trazia `Zenith_Purple` — nome diferente, sem colisão. Quando os masters passaram a
carregar `Zenith_Body`, o restyle passou a colidir **consigo mesmo**, e nada
exercitou esse caminho até alguém mudar a cor.

✅ **A trava salvou a biblioteca.** Sem a reimportação que confere nome de material
e contagem de triângulos, os 76 teriam sido regravados com `Zenith_Body.001` e o
defeito apareceria no app, meses depois.

❌ **Mas o driver ENGOLIA a causa.** Na linha 147, o modo `restyle` roda o worker
com `stdout=PIPE, stderr=STDOUT` e descarta; o modo `preview` não. A saída de 76
falhas era só `[FAIL] {id} (codigo 1)`, sem uma linha de motivo — a mensagem certa
já existia e nunca chegava à tela. Foi preciso rodar o worker à mão para vê-la.
**Trava que detecta e não conta o porquê custa uma sessão inteira de diagnóstico.**

#### 4.2e ✅ Régua EXTERNA para o material: `probe_material_dist.py`

O `restyle.py` valida reimportando o que **ele mesmo** acabou de exportar — isso
responde *"gravei o que quis?"*, nunca *"o que está em `03_dist/glb/` é o que a
fonte única manda hoje?"*. É a §1.3 aplicada ao material.

`blender -b -P qa/probe/sondas/probe_material_dist.py` lê os 76 arquivos do disco e
compara cor/metallic/roughness/nome com o `zenith_material.py`. Depois de qualquer
`restyle --all`, rodar isto — foi assim que o 76/76 de 31/07 foi confirmado.

#### 4.2f 🔴 DOIS escritores no mesmo arquivo: quem roda por último vence, e apaga

Em 01/08 os **76 GLBs de `03_dist/glb/` estavam com 1 material**. Os 39 shorts
masculinos, mapeados e aplicados ao longo de semanas, não existiam mais. Ninguém
notou porque **nada avisou**.

A causa não é bug, é arquitetura: o `restyle.py` lê o **master** (que não tem
peça) e regrava o dist; o `shorts.py` lê o master **mais o mapa** e regrava o
**mesmo arquivo**. Os dois disputam o destino, e o `restyle --all` da sessão 18
rodou por último.

✅ **O que salvou:** `config/shorts_map.json` — *o mapa é o produto, o detector só
propõe* (CLAUDE.md regra 3b). Nenhuma decisão se perdeu, só tempo de máquina.

**Conserto: o `restyle.py` RECUSA avatar que tem entrada no mapa** e imprime o
`shorts.py --apply` correspondente. Recusar, e não reaplicar sozinho — reaplicar
em lote poria o **detector** no caminho do material, e o mapa existe justamente
porque o detector erra. O `shorts.py` já aplica o material corrente junto do
short, então não é remendo: é o comando completo para quem tem peça.

> **Doutrina geral:** quando dois scripts podem gravar o mesmo destino, um deles
> tem que saber da existência do outro. "Rodar na ordem certa" não é proteção —
> é uma regra que vive na cabeça de quem digita.

✅ **E em 01/08 nasceu a régua que teria acusado o apagão no dia.** O
`probe_material_dist.py` exigia **um** material — verdade quando ele foi escrito,
e por isso ele leu os 76 sem peça e não achou nada de errado. Agora ele pergunta
outra coisa: *os materiais deste avatar são os que o `config/shorts_map.json`
manda?* Quem tem entrada no mapa precisa de `[Zenith_Body, Zenith_Shorts]`; quem
não tem, só o corpo. Saída de 01/08: **76/76, 39 com peça.**

> **Sonda que grita onde está certo é pior que sonda nenhuma:** se ela tivesse
> ficado como estava, a primeira leitura depois de reaplicar acusaria 39 falsos
> defeitos — e o reflexo para "consertar material" é `restyle --all`, que é
> exatamente o comando que apagou os shorts.

#### 4.2g 🔴 Arquivo servido ao usuário não se SOBRESCREVE — a versão vai no nome

O caminho de `03_dist/glb/` é URL de CDN, e URL de CDN fica em cache (no CDN e no
celular). Regravar o mesmo `{id}_v1.glb` com um short corrigido entrega, para
quem já baixou, **o short velho, para sempre** — o app não tem como saber que o
conteúdo mudou se o nome não mudou. **A correção fica invisível exatamente para
quem já usava o app.**

Desde 01/08 todo escritor passa por `zenith_paths.dist_glb_next()` e grava a
versão seguinte; o `build_index.py` deriva o campo `version` do nome e escolhe a
**mais alta** por id (numérica — `v10 > v2`, que ordenação alfabética erraria).

**Sem flag `--bump`, de propósito:** flag se esquece, e esquecê-la reintroduz o
bug em silêncio. A regra é *mudou o conteúdo, mudou o número*.

✅ **Efeito colateral que vale mais que o bump:** as travas do `restyle` e do
`shorts` rodam **depois** do export. Antes elas rodavam em cima do arquivo que o
app serve — um export inválido já tinha estragado o asset. Agora escrevem no
`_v{n+1}`, e a falha apaga o arquivo novo; a versão anterior fica intacta e só é
aposentada quando a nova passa.

### 4.3 `crotch_override_zh` conserta a ÂNCORA, não a SEGMENTAÇÃO

Quem usar override de virilha precisa conferir se `hem_peaks_zh` voltou vazio —
**o chute não se anuncia**. Cinco avatares tinham a bainha 100% chutada.

#### 4.3b ✅ Resolvido em 01/08 — e o que fez o chute sobreviver foi a TRAVA ser ancorada nele

Os cinco eram `b12_d1` (consertado na sessão 6), `b08_d3`, `b09_d1`, `b11_d1` e
`b11_d2` — **exatamente os quatro maiores erros de bainha da biblioteca**, todos
com o mesmo sinal (short comprido demais): −0,045 · −0,046 · −0,048 · −0,041 da
altura contra a folha, ou uns 8 cm de perna preta a mais.

**Por que nenhuma trava pegou, e é uma variante nova da §1.2.** A única régua da
bainha era `HEM_BELOW_CROTCH`: `virilha − bainha` tem que cair em 0,015–0,065. O
chute é `virilha − 0,035`. **Ele cai no meio da faixa por construção**, porque a
faixa é ancorada no mesmo número que gerou o chute. Não é trava fraca — é trava
que mede a distância de um valor até a sua própria origem.

Feito: `_hem_flags` no `shorts.py` grava **`BAINHA-CHUTE`** quando
`hem_peaks_zh` volta vazio nas duas pernas, e `chute:1perna` quando é só uma.
Mesma família do `at_band_edge` da §1.8 — *as travas olhavam QUANTO a bainha
valia e nenhuma olhava se ela tinha sido MEDIDA.*

**O conserto do número: perna por SINAL DE X, e a janela vinda da folha.** O
`w_limbs` só rotula perna abaixo da altura em que as duas se separam, e num
IMC 107 as coxas se tocam **abaixo da bainha real** — a janela cai num trecho sem
vértice de perna nenhum. Selecionando a perna por `x < 0` / `x >= 0` até um teto
acima da virilha, o anel aparece forte e simétrico nos quatro.

| avatar | bainha antes | **depois** | folha | erro vs. folha |
|---|---:|---:|---:|---:|
| `b08_d3` | 0,385 | **0,427 / 0,431** | 0,430 | −0,045 → **−0,003** |
| `b09_d1` | 0,348 | **0,398** | 0,394 | −0,046 → **+0,004** |
| `b11_d1` | 0,294 | **0,356** | 0,342 | −0,048 → **+0,015** |
| `b11_d2` | 0,323 | **0,360** | 0,364 | −0,041 → **−0,003** |

#### 4.3c ❌ E a correção NÃO virou detector — a série refutou a versão genérica

A tentação era óbvia: se subir o teto da janela acima da virilha conserta os
quatro, subir para todos. **Medido no cache dos 39 (`varre_bainha.py --virilha`),
isso quebra dois avatares que hoje estão certos** — no `b10_d2` a bainha pula de
0,377 para **0,415** e no `b01_d2` para **0,463**, porque com o teto alto o anel
da própria **virilha** ganha. É a mesma armadilha que o `HEM_BELOW_CROTCH`
existe para evitar (bainha grudando na virilha em cima, ou no joelho embaixo).

Então o resgate ficou como **sonda**, não como produção, e o número foi para o
mapa marcado `hem_fonte` — *o mapa é o produto, o detector só propõe* (regra 3b).

> **A calibração que deu direito de gravar:** a janela ancorada na folha reproduz
> **exatamente** a bainha de produção em **31 dos 32** avatares que a detecção já
> acertava (o 32º difere 0,008), **e reproduz o `b12_d1` consertado à mão na
> sessão 6 no centésimo** — 0,3479. Régua nova se calibra rodando na peça já
> aprovada (§1.6). Sem esses dois testes, o número novo seria só outro chute.

⚠️ **E ela mudou o que o `--report` diz, de propósito.** Nesses quatro corpos
`virilha − bainha` fica **negativo**, porque a `virilha` do `w_limbs` não é a
virilha anatômica e sim a altura de fusão das pernas. A entrada com `hem_fonte`
troca a reprovação por uma nota (`v-b:fusao`); quem julga ali é a régua externa.
Mesma tensão registrada na sessão 6 quando duas réguas passaram a reclamar de
propósito — **não "consertar" de volta.**

#### 4.3d 🔴 Trava calibrada numa coleção só: a costura é CURVA, o limiar dividia por ÁREA

O `--apply` do `zen_f_b11_d1` reprovou em **+6,2%** contra um teto de 6% de
crescimento de triângulos. O avatar não tinha defeito: a **trava** tinha.

O corte da costura acrescenta triângulos ao longo da **borda** da roupa — é uma
**curva**, e o custo dela cresce com o **comprimento** dessa borda. Dividir isso
pela contagem total de triângulos, que é grandeza de **área**, mistura duas
dimensões: corpo com mais roupa, ou com borda mais recortada, paga mais **sem
estar errado**. O teto de 6% foi calibrado no acervo masculino, que tem **uma
peça** (máximo medido 3,60%, folga de 67%) — e não sobreviveu ao feminino, que
tem **duas**.

Medido em `qa/probe/sondas/_costura.py`, sobre os 76 do mapa:

| | cresce p50 | **por `frac`** p50 | máx do acervo |
|---|---:|---:|---:|
| feminino (2 peças) | 4,45% | **0,198** | — |
| masculino (1 peça) | 2,74% | **0,185** | — |
| `zen_f_b11_d1` | **6,21%** | **0,204** | abaixo da mediana feminina |
| campeão | — | **0,265** | e é **masculino aprovado** |

Trocado para `costura / frac`, teto **0,40** (mesma folga de ~50% sobre o máximo
medido). ✅ **E a razão nova serve MELHOR ao que a trava diz vigiar** — *"o campo
cruzou zero onde não devia"*: costura perdida acrescenta comprimento **sem**
acrescentar roupa, então sobe em `costura/frac`; na razão velha ela sumia num
corpo grande. A preocupação já tinha, aliás, régua direta — a trava de ilha, que
o `b11_d1` passou com duas peças conexas e 100% na pior.

**A marca a reconhecer:** limiar numérico calibrado quando a coleção tinha uma só
população, aplicado depois a outra. Não é a §1.2 (trava que confere o alvo contra
ele mesmo) — é a irmã dela: **trava cuja unidade não é invariante ao que mudou.**
Antes de mexer no número, perguntar de que **grandeza** ele é.

### 4.4 Duas hipóteses de segmentação REJEITADAS (não repetir)

- **máscara pela normal** (`nz < −0,55`): come a prega do glúteo
- **folha externa por raio**: perto da dobra as duas folhas se encontram por
  definição; apertar cortava 47% das faces

### 4.4b 🔴 Os avatares NÃO compartilham topologia — shape key entre eles é impossível

Medido em 31/07 com `qa/probe/sondas/probe_topologia.py`, no par **mais favorável**
que existe: `zen_f_b03_d2` × `zen_f_b04i_d1`, ambos com **29992 vértices, 90000
arestas e 60000 faces** — contagens idênticas.

- vizinhos iguais por índice: **0,0%** (0 de 4285 amostrados);
- distância entre vértices de mesmo índice: mediana **0,313 m**, ou **17,9% da
  altura do corpo**;
- valência ordenada: **diferente**.

**Contagem igual é coincidência do ALVO de decimação, não correspondência** — é a
§1.2 outra vez: um número que confere com ele mesmo não valida nada. Um par ao
acaso nem isso tem (`zen_m_b05_d2` × `zen_m_b06_d3`: 29988 × 29997).

**A causa é estrutural, não de parâmetro:** cada avatar é uma geração independente
da Meshy, decimada por colapso de arestas guiado pela geometria daquele corpo.
Nenhum ajuste cria correspondência de índice.

**Consequência:** morphar de um avatar **para outro** é impossível hoje, não
difícil. O caminho para isso é malha-base única + wrap.

#### ⚠️ E o erro que eu cometi ao interpretar esta medida — no mesmo dia

Com a medida na mão, escrevi que ela bloqueava **a visão de produto inteira**. O
Rogério corrigiu: o app dele **não interpola entre avatares**. Ele escolhe o vizinho
mais próximo (que o `nearest_id` já faz) e aplica **shape key local** naquele
avatar — bíceps, panturrilha. **Cada malha carrega as suas próprias shape keys, e
para isso topologia compartilhada não é exigida.**

| o que se quer fazer | precisa de topologia compartilhada? |
|---|---|
| morphar o corpo A **até virar** o corpo B | **sim** |
| dar ao corpo A shape keys **próprias** | **não** |

**A medida estava certa; a conclusão que tirei dela, não.** Eu medi bem e depois
apliquei o resultado a um plano que ninguém tinha proposto — e o erro tem uma marca
reconhecível: eu não perguntei *qual* operação ele pretendia, presumi a mais
ambiciosa e a declarei impossível. É a §1.1 virada do avesso: em vez de perguntar o
que a régua não mede, deixei de perguntar **o que a régua estava sendo usada para
decidir**.

Ver `docs/VISAO_PRODUTO.md` §2 e §3.

### 4.5 Topologia: anel fechado é o que o detector sabe achar

A bainha dá a VOLTA no membro; sulco de músculo cobre um arco. Foi por isso que a
roupa feminina virou **faixa reta** (borda em anel, como o cós) em vez de top
nadador — que, além disso, cobria **60,7% do dorsal alto** num app de musculação.

#### 4.5b 🔴 A subida frontal da faixa NÃO é medida em avatar nenhum — e o traçado parece bom mesmo assim

Descoberto ao consertar uma cunha no esterno do `zen_f_b08_d3`. O
`w_faixa_curve` procura, setor a setor, o pico de concavidade da borda de cima.
Contando os **9 setores da frente** em que a concavidade na âncora é **nula**,
`qa/probe/sondas/_topo_piso.py` mediu nos 37 femininos: **de 4 a 9 de 9**.
**Não há um só avatar com a frente inteira medida.** O volume do busto (ou do
peitoral) apaga o vinco justamente onde a borda deveria subir.

**E o resultado parece bom** — onde não há aro, o `argmax` pega ruído de
decimação e a mediana circular de 7 alisa aquilo num traçado plausível. É a mesma
patologia da bainha (§4.3b), com um agravante: lá o chute se anunciava com
`hem_peaks_zh` vazio, aqui ele sai **como se fosse medida**.

❌ **Piso sobre a força do pico: testado e refutado.** Era a correção óbvia. O
mesmo sweep mediu que **qualquer** piso (0,005 · 0,02 · 0,05) reescreve de **9 a
24 setores de TODO avatar**, com deltas de até 0,054 — inclusive dos 36 que estão
certos. E os avatares que renderizam impecáveis (`b02_d1`, `b03_d1`, `b04_d1`,
`b04h_d1`) estão em **9/9 sem aro**, enquanto o `b08_d3`, o defeituoso, é um dos
**melhores** (4/9). **A contagem de setores sem aro não separa bom de ruim** —
então não serve de gatilho. Doutrina §1.6c ao contrário: o alarme que toca em
todo mundo não é alarme.

✅ **A válvula, que é o que existe hoje:** `"faixa_topo_reto": true` no
`config/shorts_map.json` faz a borda de cima ser **reta na âncora**, sem procurar
pico. Aplicada no `b08_d3`, que ficou `faixa 0,673..0,673 / 0,723..0,723` — a
altura exata do `FAIXA_ALTURA_ZH`. Não fossiliza nada: continua **retraçada a
cada `--fit`**, como os outros overrides manuais.

🔴 **O conserto de verdade é decisão do Rogério, não minha.** Não é limiar: é
**parar de procurar a segunda incógnita e MODELAR a subida** frontal, como já foi
feito para o topo escalar. Isso muda **os 37**, e **não existe régua externa para
o traçado por setor** — o `shorts_ref.py` mede altura do cós e da faixa na folha,
não a curva. Mudar 37 avatares certos com base em julgamento visual meu é
exatamente o que a regra 5b e o §6.7 mandam não fazer sozinho.

##### ✅ E ele confirmou por fora, sem saber da medida (02/08)

Revisando os 76 no testador, o veredito dele sobre o feminino foi: *"a maioria é
defeito mais no top."* **Ele não tinha lido esta seção** — é o olho dele, no app,
contra o sweep aqui, e os dois apontam o mesmo lugar.

Isso muda o peso da decisão pendente, mas **não a toma**. Duas coisas continuam
faltando, e as duas são a §1.1 de novo:

1. **"Defeito no top" não diz QUAL defeito.** Subida frontal errada, altura
   errada, largura errada e borda serrilhada são quatro consertos diferentes, e
   só um deles é o que esta seção mede. **Pedir print antes de escolher método.**
2. **Nada aqui virou régua.** O olho dele é o único juiz do traçado, e juiz que
   precisa ser convocado avatar a avatar não é trava — é a mesma dependência que
   deixou os 7 masculinos parados desde a sessão 6.

⚠️ **A tentação a nomear:** com a queixa dele na mão, fica fácil concluir *"então
é a subida frontal, vamos modelar"* e reescrever os 37. Seria trocar uma medida
por uma **coincidência de direção** — §1.5, *duas estimativas concordando não são
uma confirmação*. A queixa dele confirma que **existe defeito no topo**; ela não
confirma que **é este**.

#### 4.5c ✅ RESOLVIDO em 11/08 (sessão 26) — e as duas lições valem mais que o conserto

A subida frontal **deixou de ser procurada e passou a ser modelada**, ancorada na
folha. Erro contra a régua externa: **±0,002 em 37 de 37**, contra −0,041 no pior
antes. A válvula `faixa_topo_reto` morreu — era o mesmo modelo com amplitude
zero, e amplitude zero é a única escolha que a folha nunca endossa.

**A régua que faltava existia, e a §4.5b não a creditou.** Ela diz *"não existe
régua externa para o traçado por setor"* — verdade, e continua verdade. O que
faltou notar é que a **altura do pico** tem uma, por avatar: o `faixa_ref.py` lê
a corrida escura na vista **frontal** da folha. E o pico é a única incógnita que
um modelo precisa. *Perguntar o que a régua não mede é metade; a outra metade é
perguntar o que ela mede e ninguém está usando.*

##### 🔴 A hipótese óbvia estava errada, e o jeito de saber foi medir

O `b08_d3` era o único com a válvula **e** o exemplo do defeito maior — parecia
causa. Tirar a válvula deixou o erro **idêntico** (−0,041 antes e depois) e
trouxe de volta a cunha do esterno: dos 24 setores, **22 na própria âncora e 2
disparando +0,046**. A válvula era o curativo, não a doença. E a classe "maior"
não tinha causa única: cruzando as três classes dele com a régua, as medianas
deram −0,009 / −0,004 / −0,010 — **nenhuma separação**. Cinco dos dez "maiores"
mediam o topo certo e tinham **outro** defeito (o dente na axila, §4.5d).

##### 🔴 A RÉGUA PASSOU E O AVATAR ESTAVA ERRADO — o platô

Primeira versão do modelo: platô nos 5 setores centrais, descida começando ainda
dentro da frente. A régua deu **±0,002 nos 37** e eu dei o lote por bom. O
Rogério abriu o testador: **faixa branca no topo de absolutamente todos**, fina
no meio e larga nos lados.

A régua estava certa e era irrelevante. Ela compara a **mediana do quarto
frontal** contra a folha — ou seja, mede o **pico**. O que estava errado era o
traçado caindo cedo demais para os lados, e **pico não é forma**. É a §1.5 num
eixo novo: uma medida que confirma a altura não diz nada sobre a largura do
platô.

O conserto: o platô cobre a **máscara frontal inteira** (setores 2..10) e a
descida mora nos setores do lado. A folha sustenta isso sozinha — ela mede
frente 0,750..0,776 **e** costas 0,705..0,735, e a transição entre as duas não
atravessa o peito.

##### 🔴 E EU JULGUEI 37 AVATARES NUMA IMAGEM QUE NÃO VÊ O DEFEITO

Conferi os 37 no `qa/shorts/{id}/0_frente.png` do `--fit`. Aquilo é clay com luz
chapada: tecido não pintado e corpo saem quase no mesmo tom, e uma tira de 1 cm
é invisível. No GLB entregue, com o alumínio e o HDR, ela grita.

**Defeito de PINTURA se julga no arquivo que o usuário baixa.** O QA
intermediário serve para geometria (ilhas, costura, região conexa), não para
cobertura de material. O conserto do ciclo é `qa/probe/sondas/render_dist.py`,
que renderiza o `03_dist/glb/*.glb` com o `zenith_env.hdr` — e foi nele que os
37 foram reconferidos.

Não é a §1.1 sobre um script: é sobre uma **imagem**. Toda vez que o veredito é
visual, a pergunta *"o que esta imagem não mostra?"* vale igual à pergunta sobre
uma régua numérica.

#### 4.5d O dente na axila tinha DUAS causas empilhadas

Buracos brancos na dobra do braço, na altura da faixa. Os dois consertos são no
`w_arm_wide` e nenhum é limiar de gosto:

1. **Cada fatia de 0,005 decidia sozinha.** A fronteira braço/tronco é uma
   linha, não 20 decisões independentes; perto da axila o braço afina, o degrau
   de profundidade fica raso e uma fatia isolada acha o corte um passo mais para
   dentro. Vira dente do tamanho de uma fatia. Corrigido com **mediana móvel de
   5**, que só mexe em fatia que já cortava — interpolar onde não havia corte
   inventaria braço onde a profundidade não viu nenhum.
2. **`PROF_FRAC = 0.60` acha "já é tronco", não "aqui começa o tronco".** As
   colunas logo fora ainda são tronco, só que o tronco afina de lado e elas não
   chegam a 60%. O corte anda **uma coluna para fora** (`ARM_COL_OUT`).

⚠️ **O valor da coluna veio de render nos DOIS extremos**, que é o que a §7.12
cobra: 0 colunas → fiapo branco serrilhado; 1 → some, sobra dente pequeno na
quina; 2 → a faixa **invade o braço**. Um valor decidido por foto sem o extremo
oposto é chute com cara de calibração.

🔴 **Não zerou, e não tem régua.** Nos mais pesados (`b09_d2`, `b10_d1`,
`b11_d2`, `b12_d1`, `b07_d3`) sobra um recorte pequeno na quina de baixo. Quem
diz se incomoda é o olho dele.

#### 4.5e O corte do short é por ALTURA, e num corpo com avental isso PINTA A BARRIGA (12/08)

A fila §2 do `FILA_PECAS.md` chegou sem descrição de defeito. Eu renderizei o GLB
entregue, vi uma **faixa clara** entre a barriga e o preto, li como "falta tecido"
e subi o cós 0,015. **Estava ao contrário.** O veredito dele veio com print de 8
avatares: *"a tinta não segue o cós do short, você pinta em cima da barriga"* — a
faixa clara era a própria barriga aparecendo por cima do short, que é o certo e é
o que a folha de referência mostra. Minha subida pintou 2,6 cm A MAIS de pele.

##### 🔴 A lição de método, que vale mais que o conserto

**Eu tinha as duas leituras disponíveis e escolhi a errada sem testar a outra.**
"Falta preto" e "sobra preto" produzem a MESMA imagem quando não se sabe onde a
divisa deveria estar — e eu tinha a folha de referência, que responde: nela a
barriga cobre o short e não há preto na pele. Perguntar *"e se o sinal for o
oposto?"* custava um render; custou três rodadas e duas versões de GLB.

E as duas hipóteses geométricas que construí em cima da leitura errada morreram
medidas: **crista de raio** (não há máximo local em 4,5 cm — o raio sobe monótono
até a barriga inteira) e **dr/dz** (não separa: o controle chega a +10 mm na
frente e o `b11_d2` a +24 mm nas costas, que são os glúteos). Hipótese boa
construída sobre premissa errada continua errada — e ela *parece* boa, porque
explica a imagem que eu li mal.

⚠️ E um bug de medida sustentou a primeira: `np.convolve(..., "same")`
**zero-padda a borda**, e o primeiro ponto do perfil — o raio NO CÓS, referência
de tudo — saía a dois terços do valor real. Todo setor media "avental de 10 cm",
inclusive as costas lisas. Média móvel sobre janela que começa no ponto de
interesse tem que replicar a borda.

##### ✅ O conserto: a orientação da superfície separa pele de tecido

O campo é `z <= cos(azimute)` — corte por ALTURA. Num corpo com avental a barriga
desce abaixo dessa altura e cai dentro da região. Medido no `b09_d1`, setor 4:

| z | nz | o que é |
|---|---:|---|
| 0,564 | −0,04 | a barriga começa a virar para baixo |
| 0,524 | −0,13 | **o cós estava aqui**, no meio da face de baixo |
| 0,468 | −0,92 | o fundo da dobra: o avental acaba |

São ~10 cm de pele dentro do material do short. `w_cos_avental` desce o cós da
frente até o ponto mais baixo em que a face voltada para baixo ainda existe
(`nz <= -0,70`) — abaixo dele não há mais avental para pintar por engano.

🔴 **Só na frente, e com piso.** Nas costas o mesmo sinal é o **sulco glúteo**
(−0,6 a −0,9 no `b09_d1`), que é short de verdade: descer lá é o "cortar a bunda
no meio" que a `WAIST_WINDOW` assimétrica existe para evitar. Abaixo da virilha é
o púbis, que também aponta para baixo — daí `COS_AVENTAL_PISO`.

##### 🔴 A descida sem RAMPA vira um recorte retangular

Primeira versão aplicada: a região era a máscara frontal (±60°) e a descida ia
inteira num setor. No `b11_d1` o cós caiu 10 cm entre setores vizinhos e o short
saiu com uma **mordida retangular** — pior que o defeito original, e visível no
primeiro render. Dois consertos:

1. **A região é ±105°, não ±60°.** O avental não acaba na frente; ele sobe de
   volta indo para o flanco. Cortar em 60° era o que criava a parede.
2. **A trava de degrau passou a ATUAR.** O `WAIST_STEP_MAX_ZH = 0,045` já existia
   como *relatório* no `--report`; agora ela limita a inclinação da curva, e a
   descida se espalha por vários setores em vez de ser recusada.

⚠️ **O clamp nasceu com o sinal invertido** (`min(vizinhos) + passo` como teto em
vez de `max(vizinhos) − passo` como piso) e desfazia a correção inteira em
silêncio — o mapa saía idêntico ao de entrada, com "0 setores movidos". Trava que
pode anular o que ela deveria só suavizar precisa de um caso de teste que
distinga "não precisou" de "não funcionou".

##### O que NÃO fechou

`b11_d1` e `b12_d1`: o avental desce quase até a virilha e a rampa não deixa o cós
acompanhar. Sobra preto na barriga do `b11_d1`; o `b12_d1` não se move porque a
frente dele já está no piso da bainha. **Ele diz que o mesmo defeito existe nas
femininas** — não medido ainda.

---

## 5. Biblioteca e classificação

### 5.1 Nunca regerar nem descartar avatar já produzido

Se ele não corresponde ao que o nome promete, o conserto é **reclassificar** (o
rótulo vive no `library.json`) e **inserir** um novo onde faltar cobertura.
Decisão do Rogério: *"quanto mais avatares tivermos, maior será nossa
biblioteca"*.

⚠️ **Mas manter o asset não é servi-lo, e hoje não há mecanismo para separar as
duas coisas.** O campo `approved` do `library.json` é fixo em `True`
(`build_index.py:164`) e **nada o lê** — nem o `avatar_tester.html`. O
`zen_f_b09_d3`, que lê masculino, é entregue hoje a qualquer mulher `d3` de IMC
perto de 32. Conserto conhecido: `build_index.py` lendo uma lista de ids
reprovados, com o `nearest_id` ignorando-os.

### 5.2 O nome do arquivo registra a INTENÇÃO, não o resultado

Desde o schema 3 quem ordena a biblioteca é o `measured_bmi`. Renomear um asset
só moveria a inconsistência para o `logs/process.log`, que é append-only. Por
isso inserção em slot ocupado ganha sufixo (`h`/`i`/`j`/`k`/`m`), que marca a
**intenção, não a posição**.

**Consequência:** a folha de contato do QA deve ser ordenada por `measured_bmi`,
não por nome.

⚠️ **Vale para a BANDA, não para o nível de DEFINIÇÃO.** O `build_index.py`
extrai `d1|d2|d3` do próprio nome do arquivo (`ID_RE`, linha 66) — o
`measured_bmi` conserta banda errada, mas **nada confere o `d`**. É declaração,
não medida, e é a única parte do ID que o pipeline não audita.

**Enquanto um sexo tiver uma linha de definição só, botar avatar em outra linha é
pior que rotular errado.** O fallback `d3→d2→d1` só entra se a linha estiver
**vazia**; com um único avatar dentro dela, `nearest_id` devolve esse avatar para
qualquer IMC — um corpo de IMC 50 sozinho numa `f d1` seria entregue a uma mulher
de IMC 24. Por isso o `zen_f_b09_d2` **ficou em `d2`**.

### 5.3 A meta é COBERTURA do eixo de IMC, não contagem

O número 32 nunca foi meta.

#### 5.3b 🔴 Quando o recurso é escasso, "fechar a contagem" vira atrator

Medido na sessão 18, quando sobrou crédito para **um** avatar e faltavam **dois**
slots de grade. O reflexo — meu e de qualquer um — é gastar fechando a grade.

O `build_index.py:188` desmonta isso sozinho, e a evidência estava no repositório
o tempo todo: ele classifica cada vão pelo **meio** dele contra
`USER_BMI_RANGE = (17, 40)`. O vão que os dois slots restantes fechariam é
`f d2` **34,4 → 52,6**, meio em **43,5** → prioridade **`low`**. Pior: ele nem
aparece na lista impressa, porque o print é truncado em **`gaps[:8]`** e os
`low` vão para o fim da ordenação.

**Fechar aqueles dois slots seria gastar o último crédito num buraco que o código
do projeto já declara irrelevante para usuário real** — e ainda por cima dentro
de uma zona morta medida (§2.5b). O crédito foi para uma inserção num vão `high`
(`f d1` 24,1 → 31,9) e rendeu o `f_b04i_d1`.

⚠️ **Consequência de leitura: `gaps[:8]` esconde vão.** Ao decidir onde inserir,
não confiar só na lista impressa — ler `coverage_gaps` no `library.json`, que tem
todos.

⚠️ **E não apresentar slot de grade e vão de cobertura na mesma lista de opções.**
São contagens diferentes (§5.4) e misturá-las já produziu, na sessão 18, quatro
opções para uma pergunta de duas — o Rogério cobrou na hora: *"vc disse que
faltava apenas 2, então pq me deu 4 opções?"*. Separar as duas contagens
**antes** de perguntar, e chegar com uma recomendação só.

### 5.4 Contar vão à mão não cola

Rodar `build_index.py`, que imprime. A redação anterior do `CLAUDE.md` dizia "um
vão high" e "8 low"; o índice diz **dois** e **6**. Reincidente: o `state.md` da
sessão 13 dizia "18 femininos ocupando 15 slots" com a própria tabela ao lado
somando **20 e 17**.

⚠️ **E não confundir as duas contagens:** vão `high` de IMC mede continuidade da
escada *dentro das linhas que existem*; slot faltando mede completude da grade.
Já troquei uma pela outra e respondi errado.

✅ **Cada uma tem seu script, e nenhuma se faz a mão:**
- vão de IMC → `python scripts/build_index.py`
- slot de grade → `python scripts/contagem_slots_f.py` (nasceu na sessão 17)

O contador de slots existe porque a grade `d3` **começa em `b02` e termina em
`b10`**: um range `b01..b09` inventa um slot que não existe *e* esconde o `b10`.
As faixas da grade vivem no `docs/blocos/prompt_f.md`, que é a fonte dos
descritores — se elas mudarem, mudar o `GRADE` do script na mesma edição.

### 5.5 A régua 2D não atravessa troca de gerador nem de pose

O `measure.py` ordena folhas do MESMO gerador com a MESMA pose, e nada além. Quem
decide onde um avatar caiu é sempre o `metrics.py`, sobre o master 3D. Errar isso
já custou três previsões.

---

## 6. Processo de trabalho

### 6.1 Um por vez é um por vez

Sem o print do avatar da vez, não mexer nos outros — nem para procurar padrão.

### 6.2 "Fechar o avatar" = GLB processado e medido

Não adiantar o prompt da folha seguinte na aprovação da FOLHA. Cobrado duas vezes
(25/07 e 29/07), e na segunda o Rogério identificou a causa: **contexto no
teto**. Sintoma a vigiar — janela cheia me faz pular etapa.

### 6.2b O fluxo é uma LISTA, e os passos que eu pulo são sempre os do FIM

Cobrado com "já falamos sobre isso". O fluxo do `state.md` tem 8 passos; numa
sessão eu rodei os do meio (`intake` → `crop` → `process` → `metrics` →
`build_index`) e deixei cair o `probe_tonus_f.py` e o `restyle.py --preview`.

O padrão não é aleatório: os passos do fim são os que não **bloqueiam** o
próximo. `crop` sem `intake` falha na hora; `preview` faltando não avisa ninguém.
**Verificação que não trava o pipeline é a primeira a sumir quando a sessão
acelera** — e a aceleração vinha do próprio sucesso.

**Trava:** ao fechar um avatar, reler o bloco de fluxo do `state.md` linha a
linha antes de dizer que acabou. É o único jeito de pegar um passo que, por
definição, não reclama de estar faltando.

### 6.3 Iterar barato antes de palpitar

Na 2ª rodada cara de tentativa e erro, montar o banco de ensaio em vez de
continuar adivinhando. Foi o que destravou a sessão do short — parar de pagar
25 min por palpite.

### 6.4 Job em segundo plano contamina o mapa

Conferir que nada está rodando antes de ler estado compartilhado.

### 6.5 Arquivo nenhum entra no repositório pela mão do humano

Ele larga em Downloads; o script busca, renomeia, limpa e move. Pedir para ele
salvar, renomear ou apagar selo à mão é **regressão de fluxo**.

**Corolário, cobrado em 30/07:** ao mandar subir na Meshy, **listar os três
arquivos de referência pelo nome** (`{id}_ref_front.png`, `_ref_side.png`,
`_ref_back.png`) e o caminho da pasta. *"Subir qual? sempre fala o nome da
reference."* Repetir só os parâmetros da Meshy deixa ele parado.

### 6.5b 🔴 A ÂNCORA é IMAGEM ANEXA — dizer o número não anexa nada

**Duas gerações queimadas em 30/07 por isso.** Eu escrevia *"Âncora
`zen_f_b09_d1` (34,1)"* como se fosse só a minha régua de comparação do
`sheet_qa`, e **nunca mandava anexar a folha**. O `CHARACTER_BIBLE` §6.2 manda
anexar em toda geração; sem imagem, o substantivo vai sozinho para o atrator do
gerador. Os dois pousos batem exatamente com o passo sem âncora da §2.4:
**+18,2** e **+21,0**.

**O bloco de âncora precisa das DUAS metades**, e faltar qualquer uma quebra:
1. **continuidade** — *"mesma personagem, mesmo rosto, mesma careca, mesma roupa,
   mesma altura"*;
2. **direção** — *"gere um corpo MAIS PESADO que a anexa"*.

Só (1) → o gerador copia a âncora (Δ 0, medido duas vezes no Gemini). Só (2) ou
nenhuma → estouro para o atrator. E a §2.4 continua valendo por cima disso: **não
repetir no parágrafo de âncora traços de volume que o descritor já nomeia.**

### 6.6b Instrução que zera o passo: "é um passo pequeno"

A §2.3 já dizia que *o modelo tem passo mínimo e ignora pedido menor que ele*.
Em 30/07 eu escrevi no prompt *"É um passo pequeno"* e recebi exatamente zero —
a âncora reescalada da §1.4b. **Descrever o corpo-alvo; nunca descrever o
tamanho do passo.**

### 6.6 Não explicar um desvio antes de a MEDIDA confirmar que houve desvio

No `f_b04_d1` a conta sobre a folha deu IMC 25–27 contra os 20,5–22,5 previstos.
Anunciei o erro, achei a causa e escrevi o culpado: um parágrafo meu no descritor
pedindo *"as coxas encostam uma na outra"*, traço do `f_b08_d1`, logo eu teria
misturado as bandas.

Era uma história inteira, coerente e **falsa**. O corpo mediu **23,3**: 0,4 acima
da banda que eu pedi. O prompt estava certo; errada estava a estimativa que me
fez procurar culpado.

**O gatilho é reconhecível:** a explicação nasceu de uma régua 2D e contradizia o
que o pedido tinha feito (§5.5). Enquanto a medida não sai, o desvio é hipótese,
e hipótese não tem culpado. Se eu tivesse "consertado" o método de escrever
descritor em cima dela, teria estragado o que funciona.

### 6.7 O QA de anatomia é meu; o do Rogério é grosseria visível e short

Palavras dele, 30/07: *"você é o especialista em corpo humano, não tem como eu
decidir algo no olho assim, a menos que seja uma inconsistência grande ou defeito
na pintura do short."* **Não pedir a ele veredito de anatomia**, e não pedir
opinião sobre PNG de pasta de render — ele avalia no `avatar_tester.html`.

---

## 7. Seleção e morph (sessão 23, 03–04/08/2026)

### 7.1 🔴 A distância soma QUADRADOS — uma medida errada decide o avatar sozinha

O caso: o Rogério digitou **28 cm de panturrilha** quando o valor certo era 36.
Uma coluna em nove, errada em 8 cm.

Consequência medida: aquela coluna respondeu por **46% da distância**, e o avatar
escolhido veio com **16 cm de erro de CINTURA**. As outras oito colunas, todas
corretas, não conseguiram compensar — porque o termo é `((u−a)/s)²` e um desvio
de 1,6 dp vale 2,6 vezes mais que um de 1,0.

E quebrou **em silêncio**: o corpo entregue continua plausível na tela. Não há
como o usuário — nem eu — perceber pela imagem que a escolha foi corrompida.

**Duas defesas, e a primeira sozinha NÃO bastou:**

1. **Teto por coluna** (`z_cap = 1,5 dp`). O número foi medido, não escolhido:
   entre um corpo e seu vizinho mais próximo, o resíduo por coluna dá p50 0,21 ·
   p90 0,64 · **p99 1,49** dp. Resíduo legítimo passa de 1,5 em 0,9% dos casos.
2. **Fora da faixa da biblioteca → a coluna NÃO VOTA.** O teto sozinho reprovou
   no caso de teste: uma coluna capada ainda favorece quem estiver por acaso mais
   perto do número errado. Se o valor está fora do que a coleção inteira cobre,
   nenhum corpo o representa e ele é quase certamente fita no lugar errado.

As duas voltam em `suspect_columns`, para a tela pedir conferência em vez de
escolher calado. Trava: o caso `outlier/*` no `selection_cases.json`.

> **Regra geral:** distância euclidiana sobre entrada humana precisa de defesa
> contra outlier. Não é refinamento — é o que separa "escolheu o corpo certo" de
> "escolheu um corpo".

### 7.2 A biblioteca só tem corpos PROPORCIONAIS — e o usuário típico não é

Medido na coleção masculina, faixa de usuário: a cintura correlaciona com coxa
**r=0,90**, glúteo **0,94**, pescoço **0,78**, panturrilha **0,61**.

E o teste direto: **nenhum masculino tem cintura > 100 cm e panturrilha < 40 cm.**

A causa é o próprio pipeline: cada avatar nasce de UMA folha desenhada, e um
desenho coerente produz um corpo coerente. Desproporção nunca entra.

Só que o corpo do Rogério — cintura 106, panturrilha 36, antebraço 27 — é
exatamente isso: **tronco grande com membros finos**, gordura central. É o
fenótipo mais comum de quem começa num app de treino. A distância dele ao melhor
avatar deu **0,79 contra 0,26 de mediana** entre vizinhos: três vezes mais longe.

Consequência: **cobertura não é só resolução ao longo do IMC.** Faltam TIPOS de
corpo, e esses o gerador não produz sozinho. É o argumento mais forte a favor do
morph — ele fabrica a desproporção que a folha nunca desenha.

### 7.3 O tronco escolhe o avatar; os membros são absorvidos pelo morph

Enquanto não havia morph, pesar as nove colunas igualmente era o certo. Depois
que ele passou a existir, virou desperdício: a escolha discreta gasta precisão
tentando acertar o que uma shape key resolve, e paga isso onde a shape key NÃO
resolve.

Medido no corpo real:

| pesos | avatar | erro de cintura |
|---|---|---|
| nove colunas iguais | `b05_d1` | **+14,1 cm** (morph nenhum cobre) |
| tronco mandando | `b05h_d2` | **+5,0 cm** (peito −0,9 · ombro +1,9) |

Pesos hoje: `waist_min` 3,0 · `hip`/`chest`/`shoulder` 2,0 · membros 0,3.
**São provisórios**: a regra final é `peso ~ 1/(faixa do morph)²`, e as faixas
ainda estão sendo medidas.

### 7.4 O resíduo depois da seleção mora no TRONCO, não nos membros

Contraintuitivo num app de musculação. Leave-one-out nos 51 da faixa de usuário,
resíduo mediano por coluna: peitoral **2,3** · ombro **2,3** · glúteo 2,2 · coxa
2,2 · cintura 1,9 · pescoço 1,2 · bíceps **1,0** · antebraço **0,8** ·
panturrilha **0,6** cm.

Bíceps, antebraço e panturrilha já saem dentro do **erro da própria fita**.
Morfar ali corrige ruído. A razão: as colunas do tronco variam muito mais entre
corpos (cintura dp 15,6 cm contra bíceps 6,4), então o mesmo acerto relativo dá
erro absoluto maior.

### 7.5 🔴 Sonda numérica NÃO substitui a foto — repeti o erro que o engine já documentou

O `zenith_avatar_engine` tem isto escrito em três lugares (*"métrica certa não
substitui foto"*, v83 e v84). Eu montei sondas numéricas — normais invertidas e
raio mínimo — para varrer amplitudes sem renderizar cada passo. Elas aprovaram
o pescoço em **−11,8 cm**.

A foto mostrou **queixo e boca deformados** naquele mesmo ponto.

Se eu tivesse reportado a faixa pela sonda, teria entregue −11,8 cm como seguro,
e o defeito apareceria no device — exatamente a sequência que reprovou o v84 lá.

**E errei uma segunda vez no mesmo teste, do outro lado:** a trava que criei para
proteger o rosto classificava como "rosto" tudo acima do queixo — incluindo a
**nuca**, que deve reduzir mesmo. Ela acusou 114 vértices de defeito onde não
havia.

> **Sonda diz ONDE olhar. A foto diz SE está bom.** E trava mal definida é pior
> que trava nenhuma: gera alarme falso e ensina a ignorar o alarme.

### 7.6 O que o morph aguenta, medido (avatar `b05h_d2`, sem `morph_bmi`)

| morph | faixa limpa | onde quebra |
|---|---|---|
| cintura | **−9,3 a +21,7 cm** | −12,4 (sonda e foto concordam) |
| peitoral | **+6 cm** testado | fecha o vão da axila só 0,11 cm |
| ombro | **+6 cm** testado (e +12 no estresse) | não quebrou |
| bíceps | **+4 cm** testado (+8 no estresse) | não quebrou |
| pescoço | **−5 a −6 cm** | rosto (resolvido) → base do pescoço |

**A axila não deu sinal em nenhum teste** — a região que matou o engine cinco
vezes (v23, v77, v83, v84, v91). O mecanismo que explica: lá a **gordura inflava
o TRONCO em direção ao braço**, duas superfícies indo uma contra a outra. O morph
de músculo empurra **para fora, afastando do vão**. Sinal contrário.

No estresse (máscara de ombro descida para dentro da axila, amplitude dobrada), o
vão **abriu** de 1,94 para 2,62 cm.

> Sem `morph_bmi` a colisão não é reduzida — ela **sai da equação**. Foi a
> hipótese do Rogério, e ela se sustentou inclusive no peitoral, que é medido
> em cima da linha da axila e onde eu apostei que falharia.

### 7.7 Identidade de vértice se decide na malha BASE, nunca na deformada

Primeira versão do morph de bíceps selecionava os vértices do braço por
`distância ao eixo < 7,5 cm` sobre as posições **já morfadas**: ao empurrar para
fora, o vértice saía do próprio filtro, a medida sumia e a busca de amplitude
divergiu para 10 cm de deslocamento.

É a mesma família do *gate de propriedade* do engine (v84). **Quem é braço, quem
é rosto, quem é tronco — decide-se uma vez, na base, e não se recalcula.**

### 7.8 O avatar escolhido NÃO é persistido

O app recalcula a escolha a cada abertura, a partir da última medida. Nada é
gravado — nem o id.

Consequências: mudar peso, escala ou biblioteca **reescreve o passado** (o avatar
de março passa a ser outro), e não existe histórico de qual corpo o usuário era
em cada medição. Para a tela de evolução por avatar, esse histórico é o produto.

Pendência: gravar o id junto de cada linha de `body_measurements`.

### 7.9 🔴 A máscara tem que estar CHEIA na altura em que a régua lê

Quatro dos nove morphs saíram errados pelo mesmo motivo, e o sintoma era
diferente em cada um:

| morph | o que a régua faz | o que a máscara fazia | resultado |
|---|---|---|---|
| cintura | mínimo em 0,550–0,680 | começava em **0,560** | delta travado em **+2,5 cm** para qualquer amplitude, inclusive 6 cm |
| coxa | máximo nos 6 cm sob a virilha | platô 2 cm abaixo | precisou de **2,4 cm** de empurrão e dobrou a malha |
| bíceps | máximo entre o meio e a axila | platô abaixo do máximo | **+0,1 cm** em influence 0,5 e **+4,3** em 1,0 |
| antebraço | idem | idem | +0,8 onde devia dar +1,3 |

O mecanismo é sempre o mesmo: **régua de extremo dentro de banda**. Inflar o
meio da banda não move o extremo enquanto ele não for ultrapassado, e se a
borda da banda estiver fora da máscara o extremo simplesmente **foge para
lá** — a medida satura e mais amplitude só deforma o corpo.

É a mesma família do defeito que fez a `CALF_BAND` medir joelho em 50 dos 76
(§1.8): *extremo que pousa na borda não é extremo, é corte*. Aqui a borda é da
máscara em vez da banda, mas a conclusão é idêntica.

> **Regra:** máscara de morph cobre a **banda inteira da régua**, com platô, e
> só depois desce. Quem calibra sobre o ponto onde o extremo está *hoje*
> calibra sobre algo que o próprio morph vai mudar.

### 7.10 🔴 Ler o dist direto quebra a régua — a costura do short é uma ilha

O `metrics.py` separa medida por **topologia**. O GLB entregue quebra primitiva
por material, então corpo e short viajam separados e a costura chega com os
vértices **duplicados** (32.151 no disco contra 25.914 + 6.237). Para o
contador de laços isso é uma ilha a mais: na faixa de altura do short a fatia
devolve laços extras, o `r[1:]` que descarta o tronco descarta a peça errada, e
o número sai de outro lugar do corpo.

Medido, lendo o dist cru: **antebraço 48,3 cm** onde o `library_metrics.json`
diz 29,8, e **cintura 86,2** onde ele diz 101,3. Nenhuma trava acusaria — os
dois são valores plausíveis para *alguma* parte de *algum* corpo.

O conserto é medir numa cópia **soldada** (`remove_doubles`, 0,3 mm — as duas
primitivas são quantizadas pelo Draco em caixas diferentes e a costura não
volta bit a bit) e tratar a deformação como **função da posição**, avaliada na
cópia soldada para calibrar e na malha real para gravar o shape key. Os dois
lados da costura recebem o mesmo deslocamento e ela não abre.

> **A trava disso é externa e é barata: a régua sobre a base tem que reproduzir
> o `library_metrics.json`.** Aquele arquivo foi medido no master, por outro
> caminho de código, antes deste script existir. Hoje bate em **9 de 9** (pior
> desvio 0,1 cm no antebraço). Régua que não reproduz a medida publicada não
> calibra morph nenhum — e sem esse confronto eu teria publicado morph de
> cintura calibrado sobre 86,2 cm.

### 7.11 Fronteira de máscara não pode ser booleano — e a mão não é perna

Os três defeitos da máscara da coxa, na ordem em que apareceram, todos
denunciados pela mesma sonda de normais invertidas:

1. **538 triângulos invertidos em |x| ≈ 43 cm.** `na_perna` era só "abaixo da
   virilha", e em **A-pose a mão pousa em z/H 0,44–0,47** — dentro da faixa da
   coxa. Ela entrava no centroide da perna *e* recebia o empurrão radial. Pelo
   mesmo motivo a máscara do quadril precisou do gate de braço: a banda
   0,470–0,550 é onde o antebraço passa.
2. **177 invertidos, todos em z/H 0,459–0,461.** Era o corte `Z < leg_top`: o
   vértice logo abaixo andava e o logo acima ficava parado, e o triângulo entre
   os dois virava do avesso. Fronteira de máscara é **rampa**, nunca booleano.
3. **1 invertido em x = 0,0 exato.** O campo radial da perna vem de **dois
   centros**, e escolher a perna por sinal de X é outro corte duro: o vértice
   em x = +0,3 mm andava 2,3 mm e o de x = −0,2 mm andava 0,4 mm. Conserto:
   **misturar os dois campos** numa faixa de 2 cm em torno da linha do meio —
   que é justamente onde as coxas se tocam.

Depois dos três, a coxa passou de "quebrada em toda amplitude" para faixa limpa
de **−5,9 a +6,0 cm**, com linearidade 1,00.

> A sonda de normais invertidas **pagou sozinha o custo de existir**. Mas ela só
> presta com **piso de área**: sem ignorar triângulo lasca (< 2% da área
> mediana), um único sliver condenava a faixa inteira de um morph.

### 7.12 Sonda aprova o que a foto reprova — de novo, e agora do lado do excesso

Em influence −2,0 as sondas numéricas devolvem **zero** normal invertida no
ombro, no bíceps e no antebraço. A foto mostra **braço cordão, degrau no
deltoide e vinco na junção do trapézio**.

Por isso o teto publicado é **±1,0 em toda coluna**, e ele é um número de foto,
não de sonda. Ele não custa cobertura: em ±1,0 o morph vale de 3 a 10 cm por
coluna, e o resíduo que sobra depois da seleção (§7.4) é de 0,6 a 2,3 cm.

É a terceira vez que a §7.5 se repete neste projeto. **Sonda diz ONDE olhar.**

### 7.13 O peso do morph mora na NORMAL, não na posição

Exportado com `export_morph_normal=True`, o GLB foi de **210 KB para 4.364 KB** —
fora do orçamento de 1–3 MB do `CLAUDE.md`. A conta é direta e está no arquivo:

- **POSITION** vai em accessor **esparso** — só os 884 a 5.889 vértices que cada
  máscara toca: **459 KB** somando os nove.
- **NORMAL** sai **densa** — os 32.151 vértices em todos os nove morphs:
  **3.391 KB**.

Sem elas o arquivo fecha em **970 KB** e o three.js usa a normal da base. Para
um deslocamento de poucos centímetros, 3,4 MB de normal é o lado errado da
troca. **A trava de tamanho entrou no script** (reprova acima de 3 MB), porque
o número só aparece depois do export e ninguém olha KB de arquivo à mão.

### 7.14 Um script que lê o próprio destino tem que ser recalculável

O `morph.py` lê o **dist**, não o master — senão apagaria o short, que é a regra
9 do `CLAUDE.md`. Só que depois do primeiro `--apply` o dist corrente é o que
ele mesmo gravou: a segunda rodada empilhou **18 targets** com nomes `.001`.

Duas coisas consertaram, e as duas valem para qualquer script assim:

1. **Limpar antes de recalcular.** Os shape keys saem na entrada; os vértices da
   malha já são a base, porque todo key está em value 0.
2. **`--remap`**, que reescreve só o `config/morph_map.json` contra o GLB que já
   está no disco, conferindo que o deslocamento recalculado bate com o gravado
   (0,000 mm). Revisar faixa depois de olhar a foto é o caso normal, e sem isso
   cada revisão gastaria uma versão de CDN por nada.

E quem pegou o empilhamento foi a trava que lê o **JSON do glTF**, não o
importador: o Blender **funde as primitivas num objeto só**, então "o objeto tem
shape key" não responde se o **short** tem — e é o short que ficaria parado no app.

### 7.15 🔴 Teto de amplitude é POR REGIÃO — generalizar veredito visual custa metade da faixa

O teto de influence nasceu **±1,0 para tudo**, e o número veio da foto do
**braço**: em −2,0 o ombro e o bíceps rendem braço cordão e degrau no deltoide,
com as sondas numéricas passando limpas.

Aplicá-lo à panturrilha estava errado, e o custo foi medido: a panturrilha é um
cilindro isolado, varreu de −2,0 a +2,0 com **zero** normal invertida em todos os
passos, e as duas fotos (±6 cm) saíram limpas. O teto único cortava **metade da
faixa dela** — justo numa das duas colunas que sobravam no corpo do Rogério
(precisava −4,4 e recebia −3,0).

> **Veredito visual vale para a REGIÃO em que a foto foi tirada.** O teto virou
> `INFLUENCE_CAP` por morph, com padrão 1,0 — e a regra que acompanha é:
> **todo valor acima de 1,0 exige render olhado naquele extremo.** Quando o
> pescoço ficou sem foto em +1,5, ele voltou para 1,0 em vez de ficar na tabela.

### 7.16 Morph com um lado SATURADO tem que ser calibrado pelo outro

O `morph_neck` é um **mínimo de banda travado pelo queixo**: crescer empurra o
mínimo para a borda e satura em **+2,2 cm**, por mais amplitude que se dê.
Reduzir responde normalmente.

Calibrando pelo lado que satura, a busca de amplitude foge: ela procurava os
+6 cm alvo, batia no teto de **0,060 m** — e nesse tamanho o lado negativo virava
**−19 cm com 206 triângulos invertidos**. O morph ficava inutilizável nos dois
sentidos por causa da direção de calibração.

Conserto: `cal_sign` na tabela dos morphs. Quem tem lado saturado calibra pelo
outro, e a curva publicada carrega a assimetria (o pescoço sai −6,0 / +1,8).

> Sintoma para reconhecer: `linearidade em 0,5` muito acima de 1 **e** a curva
> achatando no fim. O pescoço marca 1,86.

### 7.17 A máscara tem que estar cheia onde a régua lê — inclusive quando não há espaço

Terceira aparição da §7.9, e a mais instrutiva: no `b05h_d2` o ponto mais estreito
do pescoço fica **a 0,4% da estatura do queixo**. Com o recuo de 1,2 cm que a
máscara usava para proteger o rosto, a frente estava **zerada exatamente na
altura em que o `metrics.py` mede** — o morph só apertava nuca e lados, e era
isso que saturava o centímetro, não a anatomia.

Recuo de 1,2 → 0,5 cm, e a redução foi de −5,7 para −6,0 cm com a mesma trava de
rosto valendo.

**E o defeito que apareceu junto:** o teto da máscara é INCLINADO (fecha embaixo
na frente, sobe até o occipital atrás) e essa inclinação vale 7,5 cm. Com a
mistura frente/costas em 6 cm e a descida em 3,5 cm, em z/H 0,860 a máscara valia
**0,04 na frente e 0,96 nas costas** — 0,92 de diferença em poucos centímetros de
circunferência. Em −1,5 isso dobrava 22 triângulos, **todos nas costas**, na faixa
exata da transição. Mistura para 11 cm, descida para 5,5.

> **Rampa de máscara se mede contra o DESNÍVEL que ela precisa vencer**, não
> contra o tamanho da região. Teto que sobe 7,5 cm precisa de rampa maior que
> teto plano.

### 7.18 Coluna que a seleção descartou não pode morfar

O Rogério digitou panturrilha **28**. A seleção marcou `suspect` (fora da faixa
que a biblioteca inteira cobre), escolheu o avatar **sem ela** — e o morph
encolheu a panturrilha 3 cm assim mesmo, porque olhava só "o campo está
preenchido".

É a mesma doutrina da §7.1 aplicada um passo adiante: valor fora da faixa é quase
certamente fita no lugar errado. **Se ele não vota em qual corpo, não pode
esculpir o corpo** — e esculpir é pior que votar, porque fica na tela.

Vale igual para `unreliable_columns`, que é a medida que a biblioteca denuncia
naquele avatar (o `chest` em A-pose): comparar aquilo é comparar ruído, morfar
por aquilo é imprimir ruído no corpo.

> Implementado no testador; **o app precisa da mesma trava** quando implementar
> morph. `INTEGRACAO_ZENITH.md` §12.

### 7.19 🔴 A biblioteca inteira é desproporcional na mesma direção — medido em 5 colunas

A §7.2 dizia "a biblioteca só tem corpos proporcionais". Com a fita do Rogério
(176 cm, 94 kg, IMC 30,3) dá para dizer **quanto**, em razão com a cintura, contra
os 27 masculinos da faixa de usuário:

| coluna | ele | menor da coleção | mediana | mais finos que ele |
|---|---:|---:|---:|:---:|
| pescoço | 0,372 | 0,389 | 0,513 | **0 de 27** |
| panturrilha | 0,335 | 0,354 | 0,446 | **0 de 27** |
| antebraço | 0,251 | 0,261 | 0,341 | **0 de 27** |
| coxa | 0,577 | 0,609 | 0,744 | **0 de 27** |
| bíceps | 0,353 | 0,273 | 0,368 | 8 de 27 |

Em quatro colunas de cinco, **nenhum avatar da faixa é tão fino quanto ele em
relação à cintura**. Não é um arquétipo de pescoço grosso: é a biblioteca inteira
desenhada em proporção "atlético pesado".

**A consequência decide estratégia:** avatar novo **não conserta isso**, porque
sairia do mesmo gerador com o mesmo viés. É vão de PROPORÇÃO, e a conta de
"falta 1 avatar" foi validada no eixo da CINTURA — justamente a coluna que o
morph resolve melhor (−5,0 a +10,0 medido, contra os ±3 que a conta supunha). A
conclusão "a biblioteca quase não precisa crescer" sobrevive; o motivo é que ela
**não cresceria na direção que falta**.

> O único lever é o morph. Confirmado no corpo real: RMS de **4,49 cm antes** para
> **1,14 cm depois**, com 8 das 9 colunas fechando exatas.

### 7.20 Script que lê o próprio destino: `--remap` é o que separa revisão de churn

Revisar a FAIXA depois de olhar a foto é o caso normal — aconteceu três vezes
nesta sessão. Sem separar "recalibrar a geometria" de "reescrever o mapa", cada
revisão gastaria uma versão de GLB e um upload ao Storage por nada.

`--remap` reescreve só o `config/morph_map.json` contra o arquivo que já está no
disco, **conferindo que o deslocamento recalculado bate com o gravado** (0,000 mm
nas três vezes). Se não bater, ele recusa e manda usar `--apply` — porque aí a
geometria mudou de verdade e a versão tem que subir.

### 7.21 O Storage responde 409 dentro de um HTTP 400

O `publish_avatars.py` classificava "já existe" por `status == 409`. O Supabase
Storage devolve **HTTP 400** com o 409 no corpo:

```
400  {"statusCode":"409","error":"Duplicate","code":"KeyAlreadyExists"}
```

Como o nome carrega a versão, uma publicação rotineira tem 76 de 77 arquivos já
existentes **de propósito** — e ela saía como **"falharam 77"**, com exit 1. Numa
tela dessas ninguém acha o único upload que importava.

> Alarme que sempre grita é alarme que se aprende a ignorar. Conferir o CORPO da
> resposta quando o serviço tem status próprio, não só o código HTTP.


### 7.22 🔴 Fechar o centímetro não é parecer com a pessoa

O `morph_waist` isotrópico fez exatamente o que foi mandado: fechou os +5,6 cm de
perímetro que separavam o avatar do corpo do Rogério. E ele olhou e disse que
**sem shape key estava mais parecido**.

Estava certo, e a medida mostra por quê — seção da cintura:

| | perímetro | largura | **profundidade** | X/Y |
|---|---:|---:|---:|---:|
| ele | 107,5 | 40,1 | **27,8** | **1,44** |
| avatar base | 101,3 | 33,4 | 29,7 | 1,12 |
| morph isotrópico | 106,7 | 35,2 | **31,4** | 1,12 |

**Perímetro é o que a fita mede; profundidade é o que o olho vê.** Otimizar o
primeiro piorou o segundo: o erro de barriga funda foi de 1,9 para **3,6 cm**. A
seleção e o morph inteiro estavam minimizando um erro que o usuário não julga.

Conserto: `morph_waist_flatten`, uma chave de FORMA separada da de tamanho,
acoplada só no crescimento, calibrada para devolver a profundidade da base.

> **A generalização:** quando a régua e o olho discordam, é porque a régua está
> medindo uma projeção do que o olho julga. Circunferência é uma projeção de
> seção — perde a forma. Toda coluna do índice tem esse ponto cego, e a cintura
> foi só onde ele apareceu primeiro (é a maior massa da silhueta).

⚠️ **E há um limite honesto que fica registrado:** não se mirou a forma DELE
(1,44), porque a fita do usuário não observa seção. Fazer isso seria embutir *um
corpo* como padrão de todos, com **exatamente um corpo real medido** no projeto.
O default escolhido não aposta em nenhuma hipótese: ele só impede que o morph
piore o eixo visível.

---

### 7.23 🔴 Cada morph passa sozinho e a SOMA quebra — o estado combinado tinha que ser trava, não relatório

Medido em 11/08, no `zen_m_b02_d1`, ao começar o lote dos 75:

| estado | normais invertidas | foto do cós |
|---|---:|---|
| `morph_waist` sozinho em −1,0 | 0 | limpa |
| `morph_hip` sozinho em −1,0 | 0 | limpa |
| todos em −0,5 | 0 | limpa |
| **todos em −1,0** | **6** | **cós enrugado, pregas em volta** |

A varredura do `--fit` sempre mediu um morph por vez, e o estado com todos
ligados era **impresso e ignorado** — apesar de o próprio comentário do código
dizer que *"a colisão que matou o outro projeto só aparecia no estado
combinado"*. Um campo radial cabe na casca; três campos radiais com centros
diferentes somados na mesma casca dobram o tecido.

**O conserto ficou no lado da biblioteca de propósito.** Tratar isso no app
custaria regra nova em **três** linguagens (o contrato é *clamp por morph*).
Aqui custa faixa, e só de quem tem culpa: `_travar_combinado` mede o estado, tira
um morph por vez para descobrir **quem** contribui, e reduz a faixa **só do grupo
culpado** em passos de 10% até zerar. Quem já é limpo não perde nada.

⚠️ **O culpado é quase sempre o par cintura+quadril**, e a razão é o cós do
short: é a única aresta rígida que os dois campos atravessam. Em 51 avatares a
trava disparou em ~2/3 deles, sempre nesse par (ou peito+cintura).

#### A tolerância foi testada e refutada — a contagem NÃO transfere entre corpos

Tentei `inv ≤ 2` para não punir avatar limpo. Três fotos derrubaram:

- `zen_m_b05h_d2` combinado no mínimo, **inv 2** → foto idêntica à base
- `zen_m_b02_d1` a 90% da faixa, **inv 2** → repuxo em V no cós, visível
- `zen_m_b02_d1` a 100%, inv 6 → enrugado óbvio

Ou seja: **o mesmo número é invisível num corpo e visível no outro.** Tolerar 2
seria calibrar num corpo e aplicar no outro — a §1.1 de novo, num eixo novo. E
agrupar os triângulos invertidos por vizinhança **também não separa**: nos dois
casos eles são singles isolados; o que muda é onde caem (no caso ruim, seis
espalhados pelo mesmo anel do cós).

O preço do critério estrito está medido e é real: o `b05h_d2`, o único avatar
aprovado no olho até hoje, perdeu faixa **negativa** de peito/cintura/quadril
(cintura −5,0 → −3,0 cm). É a faixa de quem é mais magro que ele — e para esse
usuário a seleção já entrega outro corpo. O lado positivo, que é o dele, não
mudou. **O GLB não foi tocado: só o mapa, via `--remap`.**

### 7.24 A COLUNA cai, o avatar não — e o achatamento cai antes da cintura

Duas travas que recusavam demais, achadas no mesmo lote:

**1. Uma coluna fora da régua externa derrubava os nove morphs.** O
`zen_m_b04_d3` tinha 8 das 9 colunas batendo **exatas** contra o
`library_metrics.json` e a coxa +4,0 cm — porque naquele corpo o landmark da
coxa cai **em cima da bainha do short**. O master não tem peça, o dist tem. Hoje
a coluna é pulada, o mapa publica `dropped_columns`, e os outros oito seguem. Não
é exceção inventada: o `library.json` já publica `unreliable_columns` pelo mesmo
motivo, e o contrato já diz que coluna descartada não morfa (§7.18). Acima de 3
colunas fora, aí sim para — isso não é landmark na peça, é malha errada.

**2. O achatamento acoplado derrubava a cintura inteira.** No `zen_m_b04_d1` o
lado negativo da cintura já tinha morrido na varredura, e a curva positiva
**refeita com o achatamento** deixava 1 normal invertida em toda influence: com
isso o `morph_waist` — a coluna que o app mais usa — sumia do mapa, e o
`morph_waist_flatten` ficava publicado apontando para um `couple` **que não
existia mais**. Hoje, se o acoplado reprova a faixa positiva inteira, quem sai é
o **achatamento**, e a cintura fica isotrópica. *Perder a forma custa
profundidade de barriga; perder o tamanho custa a coluna principal.*

### 7.25 🔴 A COXA não é medível no dist — e isso não é um avatar, é um padrão

A régua da coxa (`máximo nos 6 cm abaixo da virilha`) lê a **peça**, não a perna,
e o desvio contra o `library_metrics.json` chega a:

| | avatares afetados | pior desvio |
|---|---:|---:|
| masculino | 6 de 27 | +6,9 cm |
| feminino | ~11 de 24 | **+14,5 cm** |

+14,5 cm em coxa de 49,5 não é espessura de tecido (isso daria ~1 cm): é a banda
caindo onde o short ainda **une as duas pernas**, ou no aro da bainha. A trava da
§7.24 faz a coisa certa — larga a coluna — mas o efeito colateral é que **o morph
de coxa quase não existe no feminino.**

⚠️ **Não consertar por analogia.** As outras oito colunas batem em `±0,1 cm` nos
mesmos avatares, então não é a régua nem a malha: é o landmark da coxa
especificamente. O conserto provável é medir a coxa com a virilha **do master**
(o dist tem a virilha preenchida pelo tecido), e isso mexe no `metrics.py`, que a
biblioteca inteira usa. **É trabalho de sessão própria, com régua externa antes e
depois.**
