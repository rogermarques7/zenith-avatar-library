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

### 1.5 Duas estimativas concordando não são uma confirmação

Estimei o IMC de uma folha por volume (~28) e pela regra aditiva (29,4), vi as
duas baterem e escrevi que a regra estava confirmada no feminino. Medido:
**27,3**. Eram dois palpites meus, e palpites que partilham o método partilham o
viés. Antes de escrever "confirmado", separar o que é **medida** do que é
**estimativa minha**.

### 1.6 Calibrar régua nova rodando na peça já aprovada

Os três defeitos do `sheet_qa` apareceram de uma vez ao rodar a versão nova na
folha-mãe aprovada. Não é passo extra — é o método.

### 1.7 ⚠️ NÃO dispensar um alarme ANTES de ele tocar

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

### 4.3 `crotch_override_zh` conserta a ÂNCORA, não a SEGMENTAÇÃO

Quem usar override de virilha precisa conferir se `hem_peaks_zh` voltou vazio —
**o chute não se anuncia**. Cinco avatares tinham a bainha 100% chutada.

### 4.4 Duas hipóteses de segmentação REJEITADAS (não repetir)

- **máscara pela normal** (`nz < −0,55`): come a prega do glúteo
- **folha externa por raio**: perto da dobra as duas folhas se encontram por
  definição; apertar cortava 47% das faces

### 4.5 Topologia: anel fechado é o que o detector sabe achar

A bainha dá a VOLTA no membro; sulco de músculo cobre um arco. Foi por isso que a
roupa feminina virou **faixa reta** (borda em anel, como o cós) em vez de top
nadador — que, além disso, cobria **60,7% do dorsal alto** num app de musculação.

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

### 5.4 Contar vão à mão não cola

Rodar `build_index.py`, que imprime. A redação anterior do `CLAUDE.md` dizia "um
vão high" e "8 low"; o índice diz **dois** e **6**. Reincidente: o `state.md` da
sessão 13 dizia "18 femininos ocupando 15 slots" com a própria tabela ao lado
somando **20 e 17**.

⚠️ **E não confundir as duas contagens:** vão `high` de IMC mede continuidade da
escada *dentro das linhas que existem*; slot faltando mede completude da grade.
Já troquei uma pela outra e respondi errado.

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
