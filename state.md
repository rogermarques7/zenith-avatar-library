# state.md — o presente

Última atualização: **25/09/2026, sessão 39**

> ## 🔴 ABRIR AQUI — SESSÃO 39 (25/09): OS TOPS FEMININOS E A QUINA LATERAL — ✅ **55 DE 55 APROVADOS POR ELE**
>
> ✅ **Veredito dele no testador:** *"o restante está 100%, parabéns"* — só
> reprovou quatro: `b09_d2` e `b11_d1` (short), `b12_d1` e `b07_d3` (top).
> Ordem dele: *"corrija somente estes pra gente finalizar essa sessão"*; a
> próxima sessão é o **morph**.
>
> **Os quatro, consertados em prévia e aplicados** (`LICOES.md` §4.5q):
> - `b12_d1`: eixo do braço pela **calota lateral** (`w_arm_calota`) — o
>   topológico era só antebraço. As abas sumiram.
> - `b07_d3`: lascas serrilhadas nas quinas de trás → topo das costas plano em
>   0,735, **abaixo** dos dentes da borda.
> - `b09_d2`: tinta na barriga → cós da frente desce ao "V" do tecido.
> - `b11_d1`: reprovou **duas vezes**. Eu subi as costas até um anel a 0,62
>   que era a DOBRA DE PELE; ele mostrou a borda real atravessando o preto. O
>   defeito era a FRENTE (tinta na barriga, acima da dobra do avental). Ficou a
>   borda viva lida da sessão 38 (cobertura 0,71), espelhada.
>   O cós do `b09_d2` é **manual** (`borda_viva.cos_s39`), com `CANTO` limpo.
>
> ✅ **Veredito final dele (25/09): "aprovadíssimo".** A roupa feminina está
> fechada. Commitado e enviado por ordem dele; nada copiado para o app, nada no
> Storage.
>
> ➡️ **A PRÓXIMA SESSÃO É O MORPH DOS 27 NOVOS** — ordem dele.
>
> Pedido dele: *"essa sessão vc vai tratar dos tops femininos e da quina
> lateral"*, em modo automático. Tudo foi julgado em **prévia com lente de
> 250 mm** (5 azimutes) antes de qualquer `--apply` — as 54, uma a uma.
>
> ### 1. O que estava errado, e o que entrou no lugar
>
> - **Tríceps / abas no braço** (§2 da revisão): o `w_arm_wide` corta cada
>   fatia por um plano vertical em x; a face do braço que olha para o tronco
>   fica aquém do plano e saía preta, quantizada por triângulo.
> - **Quina lateral sem tinta**: a sessão 38 travou o topo nos laterais em
>   +0,7 cm porque subir ali manchava o braço.
> - **Conserto:** `shorts.w_arm_dono_field` — por vértice, a normal olha para
>   longe do eixo do BRAÇO ou do eixo do TRONCO? Vira campo contínuo, entra no
>   `w_field` da faixa e é **cortado exato** (`w_cut_boundary` interpola a
>   camada). Com o braço separado de verdade, `borda_viva_grava.py --quina`
>   tirou a trava lateral e o topo segue o tecido até a axila.
> - ❌ **Refutado no caminho:** tubo de raio fixo (o braço cresce 30% acima da
>   fusão) e `ARM_DONO_LONGE = 1,8` (abriu aba nova no `zen_f_b11h_d1`; 2,5).
>   Os dois foram pegos na **prévia**, nenhuma régua acusou. `LICOES.md` §4.5q.
>
> ### 2. O que ficou de fora, de propósito
>
> - **`zen_f_b12_d1`** (IMC 114): na primeira rodada o modelo foi recusado e ele
>   saiu igual ao entregue — reprovado; resolvido pela calota (acima).
> - As §1/§3/§4 da revisão (short) não foram tocadas: o short das femininas
>   **não muda uma face** (conferido em 3; por construção, o campo novo só
>   entra na faixa). Masculinos intocados.
>
> ### 3. Estado do disco no fecho
>
> - `config/shorts_map.json`: 53 femininas com `borda_viva.quina = 39`
>   (faixa_hi/faixa_lo sem trava lateral; `b07_d3` revertido e `b12_d1` nunca
>   teve), e cós manual em `b09_d2` e `b11_d1` (`borda_viva.cos_s39`). Backup
>   do antes: `qa/probe/_mapa_antes_s39.json`.
> - `03_dist/glb/`: **as 55 femininas com versão nova** e **37 com `morph
>   --apply` por cima** (regra 9 — repor shape keys, não morph novo).
> - Réguas: `probe_material_dist` **103/103** · `shorts --check --all`
>   **103/103** · `_confere_lote` limpo (uma versão por id, `morph_map`
>   alinhado 76/76) · `select --check` **34/34** (banco regerado: só o
>   carimbo mudou) · `morph_cases --check` **608/608** (banco regerado, nenhum
>   `expect_id` mudou) · round-trip do morph 0,000 mm nos 37. Tudo refeito
>   depois dos 4 consertos.
> - ⚠️ **O morph recalibrado mexeu nos intervalos**, como sempre que a costura
>   muda: 21 intervalos cresceram e 15 encolheram (−22,0 cm no total contra
>   +24,6 cm; a sessão 38 perdeu 121 cm no mesmo exercício). Os maiores:
>   `b02_d3` quadril −4,0 cm, `b01_d1` e `b10_d1` peito positivo −3 cm (os dois
>   ganharam `morph_chest_flatten`); no conserto, `b11_d1` perdeu a cintura
>   positiva (+3,0 → 0, ganhou `waist_flatten`) e ganhou peito/bíceps/antebraço.
>   Nenhuma coluna caiu.
> - **Commitado e enviado (push) em 25/09 por ordem dele. Nada copiado para o
>   app, nada no Storage** — a subida não foi pedida.
> - Folhas para ele: `qa/revisao/_top/{id}/folha_ab.png` (entregue × prévia,
>   os 13 do piloto) e `folha_previa.png` (as 42 do lote). Sondas novas:
>   `top_vistas.py`, `braco_normal_dono.py` (campo em 3 cores),
>   `braco_tubo_mede.py`, `_varre_eixo.py`.
>
> ### 4. ⏸️ Continua valendo
>
> Morph dos 27 novos só em sessão dedicada, depois que a peça fechar no olho
> dele (ordem de 25/09).

> ## 🔴 ABRIR AQUI — SESSÃO 38 (24–25/09): OS SHORTS FORAM REFEITOS NOS 103 PELA **BORDA VIVA** — ✅ **APROVADOS POR ELE**
>
> ✅ **Veredito dele no testador, 25/09:** *"os shorts ficaram excelentes"*.
> Barra e cós estão fechados.
>
> ➡️ **A PRÓXIMA SESSÃO É OS TOPS FEMININOS** — pedido dele. A fila está no
> `docs/REVISAO_ROUPA_2026-09-23.md` **§2 (faixa/top vazando no braço, axila e
> tríceps)**, 9 avatares, mais o que ficou de fora aqui (quina lateral de cima
> da faixa nas pesadas, tríceps do `f_b09i_d3`). O caminho que já está anotado:
> levar a máscara do braço para o corte exato do `w_cut_boundary` (§4.5h/§4.5l).
> A borda viva já lê base e topo da faixa; o que falta é a fronteira com o braço.
>
> Ele pediu proposta nova (*"liberdade pra propor uma nova abordagem"*), aprovou
> o passo 1 e saiu por 12 h pedindo que eu validasse sozinho e seguisse
> corrigindo. **A saída A (ler a barra na folha) NÃO foi feita** — foi trocada
> por um sinal que estava na malha o tempo todo.
>
> ### 1. O sinal: a borda do tecido é ARESTA VIVA, a prega de pele não
>
> A Meshy modela a borda do tecido com ângulo diedro > 30°; virilha, sulco
> glúteo e vinco de músculo são vales lisos. A barra aparece como anel fechado
> separado da virilha — inclusive nos dois corpos que mataram as tentativas 3
> e 5. E a tinta de hoje estava sempre no **fundo** do anel inclinado (o
> quantil baixo do `w_ring_map`), que é o "tinta além da barra" e o "pior nos
> d3". Tudo em `LICOES.md` §4.5p.
>
> ### 2. O que existe agora
>
> | arquivo | o que faz |
> |---|---|
> | `qa/probe/sondas/borda_viva.py` | lê as 5 bordas (barra E/D, cós, base e topo da faixa) nas arestas vivas; RANSAC por cobertura + envelope externo; clay rasante com azul (proposta) × vermelho (tinta) em 6 vistas |
> | `qa/probe/sondas/borda_viva_folha.py` | risca as linhas e monta `qa/revisao/_viva/_folha_{id}.png` |
> | `qa/probe/sondas/borda_viva_grava.py` | passa para o mapa com a política de confiança; `source: manual`, `hem_fonte: borda_viva` e o bloco `borda_viva` com o que foi aceito/recusado |
>
> `shorts.py --report`, `shorts_ref.py` e `faixa_ref.py` passaram a aceitar
> bainha e base da faixa como **curva** (mediana), não só escalar.
>
> ### 3. O ciclo: QUATRO rodadas de prévia pintada antes do primeiro `--apply`
>
> Cada uma pegou um defeito meu que régua nenhuma acusava — abinhas no braço,
> faixa inclinada, lascas da barra serrilhada, o **alisamento derrubando o
> elástico nas costas** (era o elástico branco dos masculinos pesados que já
> está no entregue), pico do cós na coluna. Consertados todos antes de gravar.
>
> ### 4. Estado do disco no fecho
>
> - `config/shorts_map.json`: **103 entradas** com a borda viva (`source: manual`,
>   bloco `borda_viva` por avatar). Backup do antes: `qa/probe/_mapa_antes_s38.json`.
> - `03_dist/glb/`: **103 com versão nova** (short) e **76 com `morph --apply` por
>   cima** (regra 9 — repor shape keys, não morph novo).
> - Réguas: `probe_material_dist` **103/103** · `shorts --check --all` **103/103** ·
>   `_confere_lote` limpo (uma versão por id, `morph_map` alinhado 76/76) ·
>   `select --check` **34/34** · `morph_cases --check` **608/608** · índice e os
>   dois bancos regerados (o de seleção só mudou o carimbo).
> - **Commitado e enviado (push) em 25/09 por ordem dele. Nada copiado para o app,
>   nada no Storage** — a subida não foi pedida; a receita continua a do bloco
>   "OS DOIS REPOSITÓRIOS" (índice, mapas e os dois bancos viajam juntos).
> - Mosaicos para ele: `qa/revisao/_s38/_ab_*.png` (antes = entregue de 22/09,
>   depois = o de hoje).
>
> ### 5. O que ficou de fora, de propósito
>
> - **Quina lateral de cima da faixa** nas pesadas: abinha igual à do entregue.
>   O tecido sobe ali para a axila e acima da fusão a máscara do braço não separa
>   nada. Frente própria (máscara do braço no corte exato).
> - **Tríceps do `f_b09i_d3`**: máscara do braço, mesma frente.
> - **Cós de `f_b11_d1`, `m_b11_d1`, `m_b11_d2`, `m_b12_d1`**: recusado pela
>   política (avental grande), ficou como estava.
>
> ### 6. ⏸️ ORDEM DELE (25/09): morph dos 27 NOVOS só em sessão dedicada
>
> *"não precisa aplicar morph nos novos avatares nessa sessão, isso a gente vai
> fazer em sessão dedicada apos finalizar as peças de roupas"*. A peça fecha
> primeiro — veredito dele no testador —, depois uma sessão só de morph.

> ## 🔴 ABRIR AQUI — SESSÃO 37 (23–24/09): O CÓS FOI APLICADO E **REPROVADO**; A BAINHA TEM MECANISMO PROVADO E DETECTOR NÃO RESOLVIDO
>
> **A frente continua ABERTA.** Nada do que foi aplicado está aprovado, e a
> decisão dele para a próxima sessão já está tomada — é a **saída A**, no §6
> deste bloco. Ler o bloco inteiro antes de tocar em peça.
>
> ### ⚠️ 1. O CÓS — 12 avatares regravados, e ele REPROVOU a maioria
>
> Foram aplicados 12 (só `waist_zh`; **nenhuma bainha foi tocada**), ancorando o
> arco da frente na FOLHA e alisando com `w_waist_liso`. Contra a folha os
> números ficaram ótimos — o `zen_f_b03h_d1`, que ele chamara de *"o defeito mais
> visível de todos"*, foi de −0,063 para −0,001. **No testador ele reprovou assim
> mesmo:**
>
> ```
> m: b07k_d1 (cós + barra) · b07j_d1 (cós, "faixa branca no cinto")
>    b06_d3 (falta tinta na barra) · b05n_d1 (recorte abaixo da barriga errado)
> f: b03h_d1, b05h_d2, b07h_d1, b07i_d1  (todos "falta tinta no short")
>    b07j_d1 (tinta no tríceps) · b09j_d1 (tinta na barriga)
> ```
>
> 🔴 **A causa é a mesma da bainha, e eu não liguei as duas na hora:** ancorei o
> cós na FOLHA, e **a folha é MENOR que o tecido que a Meshy modelou**. Eu tinha
> acabado de escrever exatamente isso sobre a faixa (`LICOES.md` §4.5l) e não
> apliquei ao cós. No `zen_f_b07h_d1` vê-se a borda alta do tecido atravessando o
> quadril com o preto bem abaixo dela — e a minha própria tabela marcava −0,023
> (4,0 cm), o pior resíduo dos 12, que eu registrei como "aceito".
>
> **As três bordas — cós, bainha e topo da faixa — são o MESMO defeito:** a tinta
> segue o desenho; o tecido que existe no corpo é maior.
>
> ### ✅ 2. O INSTRUMENTO QUE MUDOU O CICLO — `shorts.py --preview`
>
> O ciclo era **aplica → olha**, e cada volta custava uma versão de GLB (regra 8)
> mais `morph --apply` por cima (regra 9). Sendo caro, o julgamento visual era
> sempre empurrado para depois da entrega. **Ciclo caro não fica devagar: fica
> cego, porque a etapa que dói é a que se pula.**
>
> `--preview` pinta exatamente como o `--apply` (mesma malha, mesmo corte, mesmos
> materiais, mesmo Draco) e grava em `qa/preview/`, que não é URL de CDN. O
> `qa/probe/sondas/previa_peca.py` renderiza por cima com alumínio + HDR **no
> mesmo enquadramento do `revisao_peca.py`** — prévia com outro corte não
> antecipa veredito nenhum.
>
> **Pagou-se no mesmo dia:** a prévia do conserto de bainha foi reprovada por ele
> em 3 de 4. Sem ela, essa descoberta teria custado **73 versões de GLB**.
>
> ### 🔬 3. A BAINHA — mecanismo PROVADO, detector NÃO resolvido, ZERO GLB tocado
>
> ✅ **Provado, com imagem e com ele confirmando no olho:** a bainha modelada está
> **acima** da tinta em praticamente todo o acervo, e a diferença vai de 0,5 cm a
> quase 7 cm. O instrumento que provou é o clay **sem pintura, luz rasante,
> câmera ortográfica nivelada**, com a linha do mapa desenhada em 1 px no PNG
> (`bainha_rasante.py` → `bainha_pixel.py` → `bainha_mosaico.py`).
>
> ```
> vinco (azul) − tinta (vermelho)   mediana +0,0107 da altura = 1,9 cm
> vinco (azul) − folha (verde)      mediana +0,0058           = 1,0 cm
> viés da folha contra a tinta      −0,0061 · 81 neg de 103 · pior nos d3
> ```
>
> 🔴 **Ele validou o azul da vista FRONTAL** em 6 avatares escolhidos do extremo
> (4,0 cm) ao mínimo (0,6 cm): *"as linhas azuis estão nos locais corretos, pode
> seguir"*. **Essa medida vale.** O que não fecha é transformá-la em detector do
> anel inteiro.
>
> ### 🔴 4. AS CINCO TENTATIVAS DE DETECTOR, E POR QUE CADA UMA MORREU
>
> | # | tentativa | por que morreu |
> |---|---|---|
> | 1 | degrau de RAIO na malha | a 60k o ruído do raio é ±0,7 cm; o tecido tem 4 mm |
> | 2 | cume por DP na malha, janela na virilha | sobe pelo vinco inguinal; λ não serve à série |
> | 3 | teto por setor ancorado na virilha | a prega inguinal mora **abaixo** da virilha também |
> | 4 | escalar por perna, medido no pixel da frente | **ele reprovou 3 de 4**: frente e costas têm alturas diferentes |
> | 5 | anel fechado (frente + costas emendadas) | **a virilha TAMBÉM é um anel fechado** — ver abaixo |
>
> 🔴 **A tentativa 5 é a mais importante de registrar, porque o raciocínio parecia
> sólido e estava errado.** A ideia: a barra dá a volta na perna; a prega inguinal
> (só na frente) e o sulco glúteo (só atrás) não dão — então rastrear no anel
> inteiro elimina os falsos. **Mas a prega inguinal e o sulco glúteo são as duas
> metades do MESMO anel: a virilha.** Ele fecha a volta igualzinho, e é mais
> forte que a barra. Medido:
>
> ```
>                  hem no mapa   virilha    anel detectado
> zen_m_b09h_d1       0.4188     +6,9 cm       +7,1 cm   ← é a virilha
> zen_f_b01_d1        0.4646     +3,6 cm       +3,4 cm   ← é a virilha
> ```
>
> E no `zen_f_b01_d1` a barra real está a **+3,0 cm** e a virilha a **+3,6 cm**:
> 6 mm de diferença. **Nenhuma janela de altura separa os dois nesse corpo.**
>
> ### ⚠️ 5. DOIS DEFEITOS NO PRÓPRIO INSTRUMENTO, achados antes de virar conserto
>
> 1. **A luz rasante não girava com a câmera** — ficava fixa na frente do corpo,
>    então a vista de costas era medida em contraluz. Força do vinco **3,5 na
>    frente contra 1,2 atrás**. Corrigido (`_posiciona_luz`), a força foi a 4,5 e
>    os 103 foram refeitos de costas.
> 2. **A silhueta não serve para achar o eixo da perna** — no enquadramento de
>    0,22 da altura a coxa de um corpo largo **sai do quadro**, e `cx`/`R` saem
>    errados sem avisar. Hoje vêm da malha (`secao_peca.py`), com **semi-eixos
>    a/b**, porque o `w_field` mede o azimute do cós em volta da ORIGEM e a seção
>    do tronco é uma elipse deslocada.
>
> ### ➡️ 6. A DECISÃO DELE PARA A PRÓXIMA SESSÃO — **saída A**
>
> > **Medir a barra na FOLHA de referência, na vista de COSTAS, lendo o CONTORNO
> > da divisa de cor — e usar o clay da frente para amarrar a altura.**
>
> O motivo é direto: na folha o short é **preto sobre cinza claro**, uma divisa de
> cor. **Não existe vinco de pele para confundir** — nem prega inguinal, nem sulco
> glúteo. Foi esse confundimento que matou as cinco tentativas.
>
> O `shorts_ref.py` já lê a folha; o que ele nunca leu é o **contorno** da barra,
> só a altura média da corrida escura (`medir()` devolve `base` como um número).
> É trabalho de horas, sem render novo.
>
> ⚠️ **A ressalva que tem de ser respeitada, e ela é a lição desta sessão:** a
> folha é o DESENHO, e a Meshy reinterpreta proporção — foi por confiar nela que o
> cós saiu reprovado. Então a folha entra como **forma do contorno**, e a
> **altura** tem de ser amarrada no que o clay da frente mediu, que é onde o
> tecido de verdade está. Uma calibra a outra; nenhuma das duas sozinha.
>
> ### 📦 7. ESTADO DO DISCO NO FECHO
>
> - `config/shorts_map.json`: **12 entradas mudadas, só em `waist_zh`.** Nenhuma
>   bainha tocada no acervo inteiro.
> - `03_dist/glb/`: **103 arquivos**, 12 com versão nova (o lote do cós).
> - **Nada copiado para o app, nada no Storage.**
> - Backups do mapa: `qa/probe/_mapa_antes_s37.json` (antes do cós) e
>   `qa/probe/_mapa_antes_bainha.json` (= estado atual; a prévia de bainha foi
>   revertida).
> - Réguas no fecho: `probe_material_dist` **103/103** · `select --check` 34/34 ·
>   `morph_cases --check` 608/608 · `_confere_lote` limpo · `CANTO` limpo nos 12.
> - 🆕 `shorts_ref.py` imprime **VIES DA SERIE** no fim da tabela (média, mediana,
>   contagem de sinal e quebra por `d1/d2/d3`). Hoje ele acusa `bainha <<< VIES`.
> - ⚠️ Os clays dos 103 vivem em `qa/revisao/_hem/` e **não vão para o git**
>   (`qa/` é ignorado, só os `.py` entram). Refazer custa ~2 h por passada.
>
> ### 🧰 8. SONDAS NOVAS DESTA SESSÃO
>
> | sonda | para quê |
> |---|---|
> | `bainha_rasante.py` | clay sem pintura, luz rasante, ortográfica. `--alvo hem/cos`, `--vistas` |
> | `bainha_pixel.py` | traça o vinco coluna a coluna no clay. `--alvo`, `--vista` |
> | `bainha_mosaico.py` | folha de contato dos 103, 6 por imagem, com as 3 linhas |
> | `bainha_anel.py` | junta frente+costas e rastreia o anel — **não resolvido, §4** |
> | `secao_peca.py` | centro e semi-eixos da seção, por perna e no tronco |
> | `previa_peca.py` | `--preview` + folha de contato, sem gastar versão |
> | `bainha_degrau.py` | ❌ hipótese morta (degrau de raio); fica como registro |

> ## 🔴 A VALIDAÇÃO DA ROUPA REPROVOU (22–23/09) — `docs/REVISAO_ROUPA_2026-09-23.md`
>
> Ele navegou os 103 no testador (com os 27 novos destacados em laranja) e ditou
> defeito por defeito. **20 dos 27 novos têm pelo menos um defeito**, em quatro
> classes. O detalhe inteiro — tabela por avatar, versão do GLB que ele julgou,
> hipóteses e o que NÃO fazer — está naquele arquivo. Aqui só o que decide a
> pauta:
>
> 1. **🔴 Tinta além do limite da barra da perna — 16 avatares, e ele mandou
>    revisar o ACERVO INTEIRO**, novos e antigos, em **sessão dedicada**. Disse
>    duas vezes, a segunda como *"agora é definitivo"*. É a próxima frente.
> 2. **Faixa/top vazando no braço, axila e tríceps** — 9 avatares.
> 3. **Cós** — 6 avatares, e **cinco deles são os que a sessão 36 deixou com cós
>    ESCALAR manual**. Pode ser o conserto de ontem abrindo defeito hoje; decidir
>    com sonda, não no olho.
> 4. **Pintura faltando** — o oposto da classe 1, e na mesma lista. O pior da
>    coleção pelo veredito dele é o `zen_f_b03h_d1`, que é **magro** (IMC 21,5).
>
> ⏸️ **O morph continua sendo a frente seguinte, não esta.** Os 27 novos seguem
> sem shape key; a roupa deles ainda não passou.

> ## 🆕 SESSÃO 36 — A ROUPA: OS 27 NOVOS VESTIDOS E A CUNHA DA QUINA FECHADA
>
> Frente escolhida por ele: **peça**. Modo automático, com ele fora por 10 h e
> liberdade para decidir: *"se tiver alguma escolha pra fazer vc faz e depois
> justifica"*. Morph não foi tocado como frente — só re-aplicado por cima de cada
> short, que é a regra 9.
>
> ### ✅ 1. OS 27 QUE NÃO TINHAM ROUPA — 18 f + 9 m, todos vestidos
>
> Eram `library.json` 103 contra `shorts_map.json` 76. Hoje o `shorts_map` tem
> **103 de 103**. Os 9 masculinos e as 18 femininas saíram de `_v1.glb`.
>
> 🔴 **A régua externa achou defeito que o detector não acusa, em 7 femininos:**
> a bainha do 3D errava de −0,027 a −0,070 contra a corrida escura da folha,
> enquanto os outros 11 erravam no máximo 0,013. É o modo de falha do
> `_set_virilha.py` — o `w_limbs` acha a fusão das COXAS e chama de virilha — e
> desta vez ele foi **procurado**, não tropeçado.
>
> Corrigido pela regra de sempre (pico do anel do TRONCO entre 0,33 e 0,55, mais
> 0,0045 — **do anel, nunca da folha**). Erro máximo depois: **0,0085**. O
> `b08_d2` foi de −0,070 para **+0,001**. Tabela no docstring do `_set_virilha`.
>
> O `faixa_topo_frente_zh` da folha foi gravado nos **55** femininos.
>
> ### ✅ 2. A CUNHA PRETA NA QUINA DA FAIXA — e ela não era "franja de 1 triângulo"
>
> A fila viva a descrevia assim desde 15/08. No GLB entregue, com material e HDR,
> é uma **aba preta** visível de costas em todas as femininas pesadas. A descrição
> errada durou cinco semanas porque ninguém tinha olhado no arquivo entregue.
>
> **Causa:** uma fatia da banda sem corte braço/tronco. Fatia sem corte não é
> "fatia sem braço" — é fatia que **não mascara nada**, e ali a faixa sai pintada
> por cima do braço. Uma fatia de 0,9 cm já aparece.
>
> **Conserto:** preencher o buraco **interior** da curva pela própria parábola.
> A ressalva de 15/08 (*"preencher os None inventaria braço"*) proíbe
> **extrapolação**, e continua valendo — fora do intervalo medido nada é
> inventado. Dentro dele é interpolação entre duas fatias que mediram.
>
> 🆕 **Quem achou foi a terceira cor.** `faixa_tres_cores.py` pinta a máscara de
> **vermelho**: o banco de duas cores mostra o resultado e esconde a causa, e as
> duas causas possíveis (máscara curta × máscara inexistente) pedem consertos
> opostos. Duas hipóteses minhas morreram antes, as duas por medida — detalhe e
> números no `LICOES.md` §4.5h.
>
> 🔴 **E O DEFEITO VISÍVEL NÃO EXISTIA — ERA PERSPECTIVA.** Com o conserto
> aplicado, o A/B na mesma câmera deu **imagem igual**. Com **lente de 300 mm a
> 6 m** a faixa é uma barra horizontal limpa de ponta a ponta: a "aba" era o
> braço, mais perto da câmera, projetando o mesmo corte horizontal mais baixo e
> mais grosso, com a silhueta dele recortando a faixa por cima.
>
> **Saldo honesto:** o buraco na curva era real e está consertado (máscara 611 →
> 620 no `b12_d1`, 541 → 554 no `b11_d2`, nenhuma fatia sem corte) — **e é
> invisível no entregue**. Custou uma versão de GLB em 37 femininas. O defeito
> que motivou tudo não era defeito. `LICOES.md` §4.5h.
>
> ⚠️ **Regra que sai daqui:** num corpo largo, defeito perto da silhueta lateral
> só conta depois de reproduzir com **lente longa**. Se some, era paralaxe — e o
> enquadramento apertado que faz uma tira de 1 cm aparecer é o mesmo que faz a
> perspectiva dominar.
>
> ### 🔴 3. O DEFEITO DE VERDADE: O CÓS MERGULHA NA FRENTE EM 6 DA LEVA NOVA
>
> Enquanto eu perseguia o fantasma da quina, a varredura do acervo achou um
> defeito **grande e visível de frente**: o cós desce em V até a virilha e o
> short vira **cavada de biquíni**, com tecido modelado sem pintura acima do
> preto. `zen_f_b05h_d2` `zen_f_b05i_d2` `zen_f_b08_d2` `zen_f_b07h_d1`
> `zen_m_b10i_d2` `zen_m_b07i_d1` — **os seis são de hoje**.
>
> **Régua que separa: a queda contra o ANEL medido** (amplitude alta em corpo
> pesado é a barriga caindo, e é o certo). Mediana do acervo **0,029**, teto da
> série sã **0,046**, os seis **0,075 a 0,108**. O `zen_m_b12_d1` dá 0,168 e não
> entra: nele a queda é barriga de verdade.
>
> ✅ **Consertado** com cós **escalar na altura do anel medido** e `source:
> manual`. Conferido no entregue. ⚠️ A janela do `w_waist_curve` não foi mexida —
> o piso dela é global e mexer nele mexe nos 103 para consertar 6.
> `LICOES.md` §4.5i.
>
> ### ✅ 4. E DOIS AVENTAIS QUE FALTAVAM
>
> Rodei o detector de avental nos 9 masculinos novos e **esqueci as femininas** —
> lacuna achada na revisão. Medido depois: `zen_f_b11h_d1` (−0,0163 em 9 setores)
> e `zen_f_b12h_d1` (−0,0200 em 8) pedem descida, acima dos 2,1 cm que a sessão
> 29 já aplicava. Ligados e regravados em v3.
>
> ### 🆕 SONDAS NOVAS
>
> - **`revisao_peca.py`** — folha de contato do GLB entregue com **duas linhas de
>   vistas**, quadril e faixa. O `peca_folha.py` só enquadra o quadril, e foi no
>   topo da faixa que a listra branca passou por 37 avatares na sessão 26.
>   `--mosaico` monta grade de 6 para varrer o acervo.
> - **`faixa_tres_cores.py`** — a máscara do braço em vermelho. Ver acima.
> - **`faixa_normal_mapa.py`** — banco da PASSADA 4 (normal).
> - **`_confere_lote.py`** — contabilidade depois de lote: quem recebeu short
>   novo e ficou **sem shape key**. É o estado que dá medo se um lote parar no
>   meio, e nenhuma régua de material ou de peça o enxerga.
>
> ### 📏 AS RÉGUAS NO FECHO
>
> `probe_material_dist` **103/103** (material + peça) · `shorts --check --all`
> **103/103** · `select --check` **34/34** · `morph_cases --check` **608/608** ·
> `_confere_lote` limpo (103 GLBs, nenhum id com duas versões, `morph_map`
> alinhado em 76/76).
>
> 🔴 **NADA FOI COPIADO PARA O APP E NADA SUBIU PARA O STORAGE** — espera o olho
> dele, como sempre. As folhas de contato para revisar estão em
> `qa/revisao/_f_01..10.png` e `_m_01..08.png`, seis avatares por imagem.
>
> ⚠️ **O banco de casos estava VELHO, e não é desta sessão:** o commitado foi
> gerado em **21/08 com 76 avatares** enquanto o índice tem 103 desde a sessão 32.
> Regerado aqui, **13 dos 22 casos de seleção trocam de avatar** — efeito dos 27
> corpos novos entrando na seleção, não da roupa. Quando ele aprovar a subida,
> índice, mapas e os dois bancos **viajam juntos**; copiar um sem o outro é o
> teste vermelho de 16 a 19/08 de novo.
>
> ### ⏭️ O QUE NÃO FOI FEITO, E POR QUÊ
>
> - **Os 27 novos continuam sem morph.** É a outra frente, e a ordem dele é uma
>   por sessão. Eles têm peça e material, mas **não respondem às medidas do
>   usuário** — não subir para o app antes disso.
> - **A borda exata da máscara do braço** (levar a máscara para o mesmo corte do
>   `w_cut_boundary`, como o cós) continua não tentada. Deixou de ser a
>   explicação do defeito visível, mas segue sendo o caminho para a borda ficar
>   exata.
> - **`zen_m_b12_d1` e `zen_m_b11_d1`** seguem com a fresta de pele abaixo da
>   barriga. Confirmado na revisão desta sessão; é limite de forma, já
>   documentado.

> ## 🆕 SESSÃO 35 — A PRODUÇÃO DE AVATARES **ACABOU**: 98 → 103
>
> Cinco corpos novos, os dois vãos `high` masculinos fechados, e **nenhuma
> célula de forma em aberto nos dois sexos**. O que sobra é decisão, não
> produção — ver "o que ficou parado", no fim deste bloco.
>
> | id | IMC | SHR | WHR | o que fechou |
> |---|---:|---:|---:|---|
> | `zen_m_b10h_d2` | 30,7 | **1,309** | 0,942 | **M-D1** — o único V não-atlético da coleção (os outros 5 V são `d3` com WHR 0,76–0,82) |
> | `zen_m_b10i_d2` | 64,5 | *(denunciada)* | *(denunciada)* | partiu o vão `low` `m d2` 53,6→74,4 |
> | `zen_m_b05n_d1` | 28,9 | 1,074 | **1,029** | **M-B2** — maçã no vão 27,7→33,3, que estava vazio |
> | `zen_m_b06m_d3` | 28,6 | 1,243 | 0,813 | **vão `high` `m d3` 27,4→32,4** |
> | `zen_f_b09j_d3` | 37,4 | 1,142 | 0,675 | quase nada — ver abaixo |
>
> ### 🆕 O CICLO DE CORREÇÃO — ideia dele, e é a maior mudança de método do ano
>
> Em vez de re-rolar a folha inteira quando um eixo erra, **pedir a correção na
> mesma conversa do gerador**, com a imagem já feita à vista. Entrou em 19/09 e
> entregou 3 dos 5 corpos desta sessão. Antes disso eu tinha queimado quatro
> folhas re-rolando o dado e perdendo, a cada vez, os eixos que já estavam certos.
>
> **As cinco regras, todas medidas** (detalhe e números no `LICOES.md` §3.7):
>
> 1. **Uma instrução por passada**, local e nomeada numa região **contígua**. O
>    pedido difuso rendeu −0,33 pp; o nomeado, −1,61 pp na mesma folha.
> 2. **Declarar o que NÃO pode mudar.** Escrito, congela: quadril −0,38 pp e
>    coxa −0,13 quando nomeados. Sem nomear, o vazamento come metade do movimento.
> 3. **Magnitude não se controla.** Direção e região o ciclo acerta sempre;
>    quanto, nunca — previ +1,5 pp e vieram **+6,11**.
> 4. **Ele corrige EIXO, não MIRA.** Se a geração 1 nasceu no corpo errado, é
>    folha nova. Medir a geração 1 **antes** de corrigir virou passo obrigatório.
> 5. **Duas razões que dividem o denominador não se ajustam separadas.** Mexer no
>    quadril move `cintura/quadril` e `ombro/quadril` juntas, sempre no mesmo
>    sentido. Foi o que estourou os dois gates no `b06k_d3`.
>
> ✅ Funciona também com **folha antiga anexada em conversa nova** — o acervo
> inteiro vira ponto de partida.
>
> ### 🔴 EXISTE UMA CLASSE DE DEFEITO QUE NENHUMA RÉGUA NOSSA VÊ
>
> Duas malhas reprovadas nesta sessão por **defeito de superfície**, e as duas
> passariam 8/8 no `process.py`:
>
> - `zen_m_b05n_d1` 1ª tentativa — **short ausente na frente** (só existia atrás).
>   Fatal: a regra 3b lê a peça da malha, pelo vinco. Sem tecido, não há o que detectar.
> - `zen_m_b06k_d3` — **mamilos ausentes** nos dois peitorais + costura rasgada
>   sob o peitoral. A folha tinha os mamilos desenhados; quem perdeu foi a Meshy.
>
> As 8 validações olham contagem, altura, piso, centro, borda, ilha, simetria e
> material. **Nenhuma pergunta se a superfície está certa.** Quem viu foi o
> Rogério, no primeiro caso — e no segundo eu só vi depois de ele cobrar.
>
> 🆕 **`qa/probe/sondas/probe_superficie.py`** — render com **luz rasante** e close
> nas regiões onde os artefatos moram. **Passo obrigatório ANTES do `process.py`.**
> Ele falha duro se a engine não existir, porque foi exatamente assim que eu errei:
> meu render caiu em Workbench por um `try/except` que engoliu o erro, e relevo de
> milímetros é invisível com luz chapada. `LICOES.md` §1.12.
>
> ### 🔴 A FOLHA PREVÊ FORMA E NÃO PREVÊ TAMANHO
>
> Três previsões de pouso nesta sessão, três erros sem sinal nem magnitude
> consistentes: **−3,2 · −2,4 · +1,4**. Enquanto isso os offsets de forma
> acertaram dentro de ±0,05 em todas.
>
> **Parar de publicar estimativa de IMC como se fosse conta.** Declarar faixa
> larga, mandar para a Meshy e medir. `LICOES.md` §2.6.
>
> ### ⏸️ O QUE FICOU PARADO — e é decisão dele, não trabalho
>
> **1. Dois vãos `high` femininos:** `f d3` 32,4→37,4 (salto 5,0) e `f d1`
> 34,1→39,7 (5,6). Recomendei **deixar**: o usuário cai no máximo a 2,5 e 2,8 de
> IMC do vizinho, e o `morph_waist` cobre ±10 cm. Mesmo argumento que aposentou
> o M-D2. O `f d3` custou 2 créditos para encolher 1,1 — o `b09j_d3` pousou em
> 37,4 com a forma **idêntica à âncora na terceira casa decimal**, ou seja quase
> um clone. Crédito fraco, e a culpa foi da minha previsão de tamanho.
>
> **2. M-C1/C2/C3 (ampulheta masculina) — PARKADAS, para tentar com o ciclo de
> correção.** Não são mais "impossíveis": a M-C1 **já está praticamente ocupada
> pela `b05_d2`** (IMC 26,8 · SHR 1,153 · WHR **0,813**, errando o corte de 0,80
> por 0,013) — as seis folhas de 19/09 miravam um lugar que já tinha dono. E a
> saída de emergência que o `COBERTURA_FORMAS.md` deixava em aberto foi testada e
> **não abre**: entre IMC 24 e 34 só 4 corpos têm `WHRmin ≤ 0,80`, e os quatro
> são `d3`. Detalhe em `COBERTURA_FORMAS.md` §11.
>
> **3. M-D2 aposentada** — o que faltava eram 2,3 de IMC numa forma que já existe
> (`b10h_d2`), e isso é trabalho do morph, não de crédito.
>
> ### ⚠️ Meshy 7: a taxa de reprovação se confirmou em ~37%
>
> **7 reprovações em 19 gerações** acumuladas. Nesta sessão: 1 por simetria
> (29,76 mm, teto 20) e 2 por superfície. ✅ **Melhoria de imagem ligada como 2ª
> tentativa: terceira amostra a favor** — o `zen_f_b09j_d3` saiu de 29,76 mm para
> **4,91 mm** só com o botão ligado, sem tocar na folha.
>
> ### ➡️ A PRÓXIMA SESSÃO — **uma frente só, decisão dele**
>
> 🔴 **27 corpos sem peça e sem morph** (103 − 76). É isso que trava a entrega,
> não cobertura. Nada vai para o app enquanto a lista não zerar: corpo sem entrada
> no `morph_map.json` aparece e **não responde às medidas do usuário**.
>
> ```
> f: b03h_d1  b05h_d1  b05h_d2  b05i_d2  b06i_d3  b07h_d1  b07h_d2  b07i_d1
>    b07j_d1  b08_d2   b08h_d2  b09h_d1  b09i_d1  b09i_d3  b09j_d1  b09j_d3
>    b11h_d1  b12h_d1
> m: b05n_d1  b06m_d3  b07h_d1  b07i_d1  b07j_d1  b07k_d1  b09h_d1  b10h_d2
>    b10i_d2
> ```
>
> A lista se refaz com `set(library.json) − set(config/morph_map.json)`.
>
> 🔴 **ORDEM DELE, 22/09: atacar UMA frente por sessão — morph OU pintura de
> peça, nunca as duas.** E **perguntar a ele qual**, na abertura da conversa
> seguinte. A ordem técnica continua a de sempre (`shorts.py` antes de `morph.py`,
> porque o `restyle`/morph leem o dist e a peça tem que estar lá), mas **quem
> escolhe a frente da sessão é ele.**

> ## 🚀 A BIBLIOTECA ESTÁ NO AR — subida em 16/08, a primeira desde 11/08
>
> **76 GLBs enviados, 0 falhas.** O HDR já estava lá e foi pulado (`upsert=false`
> é o padrão — nome novo entra, nome existente não se regrava). Conferido no CDN
> público depois: `zen_f_b12_d1_v20.glb` 200, `zenith_env.hdr` 200.
>
> Índice, mapa de morph e os dois bancos de casos foram copiados para o app antes
> do upload (**índice primeiro, upload depois** — o `publish_avatars.py` recusa
> rodar se o índice promete GLB que não está no disco daqui).
>
> **O que subiu junto:** a quina do cós (30 femininos), a máscara do braço (23
> femininos), a trava `CANTO` nos 14, a coxa resolvida por offset (14/08), o
> bíceps refeito (14/08) e os **dois achatamentos novos** (quadril e peitoral).
>
> ⚠️ **Os GLBs antigos continuam no bucket.** É de propósito: URL de CDN não se
> reescreve (regra 8), então versão velha fica órfã até alguém limpar. Ninguém
> limpa hoje, e o custo é ~1 MB por versão aposentada.
>
> ### ✅ ACHATAMENTO DE QUADRIL E PEITORAL — a pendência de 06/08 fechou
>
> `morph_hip_flatten` e `morph_chest_flatten`, pelo mesmo raciocínio da cintura:
> morph radial uniforme PRESERVA a forma da seção, então fechar centímetro de
> perímetro custa profundidade — e profundidade é o que aparece de perfil.
>
> O `_achatar()` já era genérico; o que estava preso à cintura era o **critério de
> calibração**. Hoje cada um mede a sua profundidade na altura em que a sua régua
> lê (`_waist_depth` · `_hip_depth` · `_chest_depth`). Validado no
> `zen_m_b05h_d2`: quadril 27,5 → 30,4 só com tamanho → **27,5 com forma**;
> peitoral 29,8 → 32,2 → **29,8**; cintura idêntica ao publicado (nada regrediu).
>
> **Distribuição nova de shape keys: 33 com 12 · 25 com 11 · 11 com 10 · 5 com 9 ·
> 2 com 8.** Achatamentos publicados: cintura 64, quadril 48, peitoral 65.
> Tamanho do GLB: mediana 1.162 KB, máximo 1.395 KB — dentro do orçamento de 1–3
> MB do `README`.
>
> 🔴 **Trava nova, e ela veio de um caso de borda real:** se o morph de tamanho não
> afunda a seção, não há o que achatar. No `zen_f_b12_d1` o peitoral não afunda e
> a busca devolveria amplitude ~0 — uma shape key morta de **7.352 vértices** que
> o app baixaria para não mover nada. `FLATTEN_MIN_GANHO_CM = 0.2`. `LICOES.md`
> §7.22b.
>
> ⚠️ **O app não precisou mudar:** o `avatar_morpher.dart:116` já trata `couple`
> de forma genérica, então os dois achatamentos novos entram como dado.
>
> ### ✅ A TRAVA `CANTO` RODOU NOS 14 — sobraram 3, e o motivo é geometria
>
> Decisão dele em 16/08: rodar nos 14 que a trava reprovava e ele nunca tinha
> apontado. 8 pelo `--fit` normal. 🔴 **Os outros 6 estavam `source: manual`** — e
> o que é manual neles é a **bainha** (`hem_fonte: anel-xsign`), corrigida à mão
> em sessões anteriores. Um `--refit` teria jogado isso fora; para eles o
> alisamento foi aplicado em cima da curva do mapa
> (`cos_liso_mapa.py --escrever`, que só toca o `waist_zh`).
>
> **Sobraram 3 acima do corte e eles NÃO devem ser "consertados":**
> `zen_m_b12_d1` 0,042 · `b11_d2` 0,022 · `b11_d1` 0,021. A causa é medida — o cós
> encosta no **piso da bainha** e a curva achata contra ele; a quina é a entrada
> nesse platô. É o mesmo limite que este arquivo já registrava para o `b12_d1`
> ("não se move"). Iterar o filtro até a trava passar derrubaria a curva 2,4 cm
> para esconder geometria: **é tunar contra a própria trava**, e este projeto já
> pagou por isso (regra 3 do `CLAUDE.md`).
>
> ### ✅ Backup refeito em 16/08 — `_backup_zenith/zenith_assets_2026-08-16.zip`
>
> **492 MB**, integridade conferida (`testzip`), **lista de pastas batida contra o
> zip de 12/08** (é essa comparação, não o tamanho, que pegou o `01_raw` faltando
> daquela vez) e os 76 GLBs do índice conferidos um a um dentro do zip.
> ⚠️ Continua **no mesmo disco** — protege contra erro meu, não contra falha de
> disco.


> ## 🔀 OS DOIS REPOSITÓRIOS VIRARAM SESSÕES SEPARADAS (06/08)
>
> Decisão do Rogério. **Abriu a `zenith-avatar-library`** → o trabalho é o desta
> lista: shape keys nos 75 que faltam e correção de short/faixa. **Abriu o
> `zenith`** → é implementação do app, e a primeira é a tela de objetivo.
>
> O que atravessa os dois é o **contrato**, e ele mora em
> `docs/INTEGRACAO_ZENITH.md` §11 e §12. A cada lote fechado aqui, a biblioteca
> sobe para o app:
>
> ```
> python scripts/build_index.py          # o nome do GLB muda a cada versão
> python scripts/select.py  --cases      # os 34 casos são ids de avatar
> python scripts/morph_cases.py          # os 608 casos seguem o glb_version
> git diff test/                         # ⬅ A REVISÃO É O DIFF. Ver abaixo.
> python scripts/select.py --check       # 34/34
> python scripts/morph_cases.py --check  # 608/608
> cp library.json          ../zenith/assets/avatars/library.json
> cp config/morph_map.json ../zenith/assets/avatars/morph_map.json
> cp test/selection_cases.json ../zenith/test/fixtures/selection_cases.json
> cp test/morph_cases.json     ../zenith/test/fixtures/morph_cases.json
> cd ../zenith && python scripts/publish_avatars.py
> ```
>
> ⚠️ **O `morph_cases.json` entrou nesta receita em 15/08** e faltava: ele tem uma
> trava que recusa gerar se o `glb_version` do mapa não bater com o do índice,
> então depois de qualquer `morph --apply` ele precisa ser **regerado**, não só
> conferido. Rodar só o `--check` devolve divergência e parece defeito.
>
> 🔴 **O `select.py --cases` entrou em 20/08, pelo MESMO motivo, e a falta dele
> custou quatro dias de teste vermelho no app.** A receita regerava um banco e só
> **conferia** o outro — mas os `expect_id` do `selection_cases.json` são ids de
> avatar, então ele depende do índice exatamente como o do morph. Em 16/08 o
> `build_index.py` carimbou `2026-08-16T13:47:44Z`, o banco ficou em
> `2026-08-14T18:04:45Z`, e o `avatar_selection_test.dart` reprovou de 16 a 19/08
> — enquanto o `select.py --check` respondia **34/34 o tempo todo**.
>
> **Conferir RESPOSTA é cego para PROCEDÊNCIA**, e das três implementações da
> regra só o Dart cobrava o carimbo. Hoje os dois `--check` daqui cobram também
> (`select.py` e `morph_cases.py`), com mensagem própria — banco velho e regra
> mudada pedem ações opostas e não podem sair com o mesmo texto.
>
> ### ✅ AS TRÊS CÓPIAS FECHADAS EM 20/08 — e o testador não tinha árbitro nenhum
>
> Ao fechar o carimbo nas três apareceu um buraco maior que ele. O
> `avatar_tester.html` é a **terceira implementação da regra de MORPH** (junto
> com o Python e o Dart) e **não rodava nenhum dos 608 casos** — eles só corriam
> aqui e no app. A regra morava dentro do `aplicarMorph()`, que lê slider e
> escreve em malha: **regra amarrada à tela é regra sem árbitro.**
>
> ✅ **`resolverInfluences()`** — a regra pura, espelhando o `solve()` do
> `morph_cases.py`, e o `aplicarMorph()` passou a consumi-la no modo automático.
> Os 608 rodam no load, ao lado dos 22 de seleção. Placar: **608/608**.
>
> 🔴 **E o `influenceDaCurva()` do testador tinha DUAS divergências latentes**
> contra a referência, nenhuma visível sem banco de casos: (a) não ordenava a
> curva por influence; (b) não protegia vão zero — dois pontos com o mesmo cm
> davam divisão por zero e a influence saía `Infinity`, ou seja, **slider no
> teto**. Reescrito ponto a ponto; conferido contra o Python em **6.736 amostras
> de curva, delta máximo 0,0**.
>
> ⚠️ **O carimbo do testador cobria só a data.** Hoje cobra os três campos, como
> o Dart. E no lado do app o teste de morph cobria só `glb_versions` — índice
> regerado com os mesmos GLBs (recalibração de medida, coluna nova, avatar
> reprovado) não move versão nenhuma e passava batido. Duas asserções novas lá:
> `index_generated_at`, e **todo avatar do mapa tem que estar no banco** (o
> sentido que faltava: avatar novo chegava sem caso nenhum cobrindo o morph
> dele). Suíte do app: **87/87**.
>
> ### 📐 A REVISÃO DO LOTE É O `git diff test/` — e ela tem duas leituras
>
> Regerar não é revisar. Depois de `--cases` e `morph_cases.py`, **olhar o diff
> antes do `cp`**:
>
> - **só o carimbo mudou** (1 linha em cada banco) → a recalibração **não moveu
>   resposta nenhuma**. Copiar. Foi exatamente este o caso em 20/08: o
>   `selection_cases.json` regerado deu **uma linha de diff**, o `generated_at`.
> - **algum `expect_id` ou `expect_influences` no diff** → mudou **qual corpo o
>   usuário vê**, ou como ele é esculpido. Aí alguém olha caso a caso **antes** do
>   `cp`. Nunca copiar um diff de resposta sem ler: toda resposta errada continua
>   sendo um avatar plausível na tela.
>
> ⚠️ **Não regerar de dentro do `--check`.** A trava tem que reprovar e parar; que
> se auto-conserta não é trava, e o `expect_id` errado entraria no app calado.
>
> 🔴 **ÍNDICE PRIMEIRO, UPLOAD DEPOIS.** O `publish_avatars.py` recusa rodar se o
> índice do app promete um GLB que não está no disco daqui — e depois de um
> `morph.py --apply` a versão anterior não está mais. Ordem invertida = ele
> aborta (o que é o comportamento certo, mas custa tempo).

> ## 🔴 ABRIR AQUI NA SESSÃO NOVA
>
> ### ✅ A INTEGRAÇÃO COM O APP ESTÁ NO AR — o avatar 3D aparece na home
>
> Os passos §6.3, §6.4 e §6.5 do `INTEGRACAO_ZENITH.md` foram fechados na sessão
> 23, e o app **está rodando com avatar 3D no device**. O que existe hoje:
>
> - **`library.json` schema 4** — seleção por MEDIDAS, não mais por IMC dentro de
>   linha de definição. `definition_thresholds_bodyfat_pct` aposentado (o app não
>   estima gordura). Publica escala por sexo, `unreliable_columns` por avatar,
>   `z_cap`, `plausible_range_cm`, pesos e vetor de objetivo.
> - **`scripts/select.py`** — a regra em Python, que é a implementação de
>   REFERÊNCIA. As outras duas (Dart no app, JS no tester) se ajustam a ela.
> - **`test/selection_cases.json`** — 34 casos. Rodam nas três linguagens.
>   **Ao mexer na regra: muda no Python, `--cases`, e copia os DOIS arquivos para
>   o app** (`assets/avatars/library.json` e `test/fixtures/selection_cases.json`).
> - **76 GLBs + o HDR no Supabase Storage**, bucket público `avatars`. O
>   `cdn_base` do índice aponta para lá. Sobe com
>   `python scripts/publish_avatars.py` (mora no repo do APP).
>
> ### 🧬 OS 76 TÊM SHAPE KEY — o lote inteiro rodou em 11/08 (sessão 25)
>
> **76 de 76 no `config/morph_map.json`**, cada um com `--apply` próprio, versão
> nova de GLB e a anterior aposentada. Distribuição **na época**: 35 com 10 shape
> keys, 33 com 9, 5 com 8, 3 com 7 — o que falta em cada um está em
> `dropped_columns` no mapa, e o motivo é sempre régua, nunca desistência.
> ✅ **Hoje é 54/16/3/3**, depois da coxa ter sido resolvida em 14/08.
>
> Réguas externas rodadas DEPOIS do lote, as duas limpas:
> - `probe_material_dist.py` → **76/76** em `#B9BCC2` / 0.25 / 0.45 com a peça
>   cobrada de quem está no `shorts_map` (é a trava do apagão de 31/07, e o
>   morph reescreveu os 76 arquivos — era obrigatório rodar).
> - `select.py --check` → **34/34** · `morph_cases.py --check` → **608/608**.
> - Índice reconstruído: **nenhum id com duas versões no disco**, e nenhum
>   `assets.glb` apontando para arquivo que não existe.
>
> 🔴 **NADA FOI PARA O APP.** O contrato do `INTEGRACAO_ZENITH.md` §12 não mudou,
> mas os arquivos novos (`library.json`, `morph_map.json`, `morph_cases.json`) e
> os 76 GLBs **estão só aqui**, esperando o olho dele no testador. Ele pediu
> explicitamente aprovação visual antes de subir.
>
> **A receita continua a mesma, e agora está exercitada 76 vezes:**
>
> ```
> python scripts/morph.py {id} --fit      # calibra e sonda, nao grava
> python qa/probe/sondas/morph_folha.py {id}   # base x max x min, 4 vistas
> python scripts/morph.py {id} --apply    # grava o dist v(n+1) + o mapa
> python scripts/morph.py {id} --remap    # so o mapa, sem gastar versao
> ```
>
> 🆕 **`morph_folha.py`** é a folha de contato do morph: base × todos-no-máximo ×
> todos-no-mínimo, em corpo/perfil/3-quartos/axila, **numa imagem só**. Defeito de
> morph é DIFERENÇA contra a base — olhar 12 PNGs em sequência perde a
> comparação. As 76 estão em `qa/morph/{id}/folha.png`.
>
> ### 🔴 O QUE O LOTE ACHOU — três travas novas, e uma pendência grande
>
> **1. O estado COMBINADO era relatório e virou trava (§7.23).** Cada morph
> passava sozinho e a soma enrugava o cós do short. Hoje a faixa do **grupo
> culpado** (quase sempre cintura+quadril) é reduzida até zerar as normais
> invertidas. Disparou em ~2/3 dos 76. Tolerar `inv ≤ 2` foi **testado e
> refutado com foto** — o mesmo número é invisível num corpo e visível no outro.
>
> ⚠️ **Isso mexeu no `b05h_d2`, o avatar que ele aprovou:** perdeu faixa
> NEGATIVA de peito/cintura/quadril (cintura −5,0 → −3,0 cm), que é a faixa de
> quem é mais magro que ele. O lado positivo — o dele — não mudou, e o **GLB não
> foi tocado** (só o mapa, via `--remap`).
>
> **2. Uma coluna fora da régua derrubava o avatar inteiro (§7.24).** Hoje cai só
> a coluna, e o mapa publica `dropped_columns`. O `b04_d3` tinha 8 de 9 colunas
> EXATAS e perdia os nove morphs por causa da coxa.
>
> **3. O achatamento acoplado derrubava a cintura (§7.24).** No `b04_d1` o
> `morph_waist` sumia do mapa e o `morph_waist_flatten` ficava publicado
> apontando para um `couple` inexistente. Hoje quem sai é o achatamento.
>
> **4.** ~~A COXA NÃO É MEDÍVEL NO DIST~~ ✅ **RESOLVIDA em 14/08** — ver o bloco
> logo abaixo. Era o maior buraco do morph (28 dos 76 sem coxa) e hoje são
> **75 de 76**.

> ### ✅ O MORPH DE CINTURA ERA ISOTRÓPICO E ENGORDAVA — CONSERTADO EM 06/08
>
> Reclamação do Rogério, medida e **confirmada**: com os shape keys o avatar fica
> mais gordo do que sem. Não é impressão, e não é a cintura estar errada.
>
> Seção da cintura, na altura em que a régua mede:
>
> | | perímetro | largura X | profundidade Y | **X/Y** |
> |---|---:|---:|---:|---:|
> | **ele** (fita + foto de perfil) | 107,5 | 40,1 | **27,8** | **1,44** |
> | avatar base | 101,3 | 33,4 | **29,7** | 1,12 |
> | avatar com o morph dele (+5,6) | 106,7 | 35,2 | **31,4** | 1,12 |
>
> Duas coisas, e as duas importam:
>
> 1. **A barriga do avatar já era mais funda que a dele ANTES do morph** — 29,7
>    contra 27,8. Ele é mais largo e mais raso; o avatar é mais estreito e mais
>    fundo.
> 2. **O morph é radial uniforme, então preserva a forma errada**: X/Y fica em
>    1,12 nos dois estados. Fechar os +5,6 cm de perímetro custou **+1,7 cm de
>    profundidade** — e profundidade é exatamente o que se vê de perfil e de 3/4.
>    O morph piorou o eixo em que o avatar já estava errado.
>
> **Não é só deste avatar.** Na faixa de usuário o X/Y da coleção vai de **1,02 a
> 1,45, mediana 1,31** — e ele correlaciona com IMC: os gerados gordos são
> ROLIÇOS (b07_d1, IMC 39,9 → 1,02) e os magros são achatados (b03_d3, IMC 20,8 →
> 1,44). O Rogério tem IMC 30,3 e X/Y 1,44: ele carrega peso **em largura**, e a
> biblioteca só oferece profundidade nessa faixa. É a §7.19 de novo, num eixo que
> a seleção **nem mede** — circunferência é cega para forma, e duas cinturas de
> 101 cm podem ser redonda ou chata.
>
> ✅ **CONSERTADO: `morph_waist_flatten`, a 10ª shape key.** Ela muda a forma da
> seção (largura contra profundidade) a perímetro ~constante, e é **acoplada**:
> o app aplica `influence = max(0, influence do morph_waist)`. Só no
> crescimento — reduzir cintura tem que perder profundidade, que é o que
> emagrecer faz.
>
> **Calibração — o default conservador:** a amplitude é a que devolve a
> profundidade da BASE quando a cintura está em +1,0. Medido: base **29,6 cm** ·
> só tamanho **32,6** · com forma **29,6**. O morph deixou de piorar o eixo
> visível, sem apostar em nenhuma forma de corpo.
>
> ⚠️ **A curva publicada do `morph_waist` foi REFEITA acoplada**, porque é isso
> que o app vai produzir: +10,8 cm em influence 1,0 contra +10,0 solta. Publicar
> a curva solta seria publicar um número que ninguém gera.
>
> 🔴 **Não se mirou a forma DELE (X/Y 1,44), e o motivo é doutrina:** a fita dá
> perímetro, não seção. Mirar 1,44 seria embutir *um corpo* como padrão de todo
> mundo, com **um único corpo real medido** no projeto inteiro. Quando houver
> entrada de forma — ou mais corpos medidos — a chave já existe para receber.
>
> **Falta o mesmo para QUADRIL e PEITORAL**, pelo mesmo raciocínio. Não feito.
>
> ⚠️ A medida da profundidade dele saiu da foto de perfil calibrada pela fita de
> 1,5 m; a largura é DERIVADA pelo modelo de elipse a partir do perímetro da fita.
> A elipse subestima seção achatada, então o 1,44 dele é **piso**, não teto. A
> direção não depende disso: 1,44 contra 1,12 sobrevive a qualquer erro de ±4%.
>
> ### ✅ A FILA DAS PEÇAS está em `docs/FILA_PECAS.md` — e ela é o produto
>
> Ele manda a fila por **print do testador**; o que não está nela não está na
> fila (regra §6.1). Quatro rodadas fechadas: tops femininos (26), shorts
> masculinos (27), cós-avental feminino (29), quina do cós + máscara do braço
> (30). O arquivo guarda o placar de cada uma.
>
> 🔴 **O que sobrou de fila viva está no bloco da sessão 30, no topo:** 3
> femininos e 11 masculinos que a trava `CANTO` reprova, e a franja de 1
> triângulo na quina faixa/braço. Nenhum foi tocado — entram por decisão dele.
>
> ### ✅ A COXA FOI RESOLVIDA EM 14/08 — por OFFSET, não por medir melhor
>
> Trabalho de uma sessão que **não deixou registro aqui** (o mesmo dia da
> recalibração dos 76 no working tree). Descoberto em 15/08 ao conferir os
> números antes de escrever esta documentação, e é o item mais importante que
> estava desatualizado: o `state.md` dizia "28 dos 76 sem morph de coxa".
>
> **Hoje são 75 de 76** — só o `zen_m_b06h_d3` não tem. O `dropped_columns` da
> biblioteca inteira é `forearm` 3 · `biceps` 2 · `waist_min` 1; **a coxa saiu
> da lista.** É isso que explica a distribuição de shape keys ter ido de
> 35/33/5/3 para **54/16/3/3**.
>
> **O conserto foi parar de tentar trocar a medida.** As três tentativas de mexer
> em *qual malha é medida* (`PROBLEMA_COXA.md` §5) consertavam quem falhava e
> quebravam quem já passava — a última achou **10 regressões novas** entre os 48
> que passavam. `calibrar_offset_coxa` mede o desvio **uma vez** contra o
> `library_metrics.json` na base e soma um offset constante; a medição segue pela
> malha cheia, sem risco de laço vazio. Teto `COXA_OFFSET_MAX_CM = 22`.
>
> ⚠️ **A suposição não verificada:** o excesso de tecido é constante em cm ao
> longo da amplitude do morph. Plausível, sem medida que comprove — não existe
> medida de coxa deformada no projeto. `LICOES.md` §7.25b e `PROBLEMA_COXA.md`
> §7b.
>
> 🔴 **O `metrics.py` continua medindo a coxa errado no dist.** O offset conserta
> o morph, que é quem precisa da leitura. Se algo mais passar a medir coxa no
> dist, o problema volta inteiro.
>
> 🆕 **Na mesma sessão de 14/08 o morph do BÍCEPS foi refeito** (3ª versão, as
> duas anteriores reprovadas por ele com print): a máscara deixou de ser faixa
> em Z e passou a ser faixa no **eixo do próprio braço** — em A-pose o braço sai
> a ~24° da vertical, então fatia de Z global corta o membro na diagonal e pega
> bíceps de um lado e cotovelo do outro. Está no docstring do `morph.py`.

> ### 🔴 A LISTA DO QUE FALTA AQUI — é esta a pauta das sessões da biblioteca
>
> **1. O morph isotrópico da cintura** — o bloco acima. É o único item com defeito CONFIRMADO no olho dele.
>
> **2.** ~~Shape keys nos 75 restantes~~ ✅ **FEITO em 11/08 — 76 de 76.** Ver o
> bloco de morph acima. O que sobra dessa frente é **o olho dele no testador** e,
> depois, a subida para o app.
>
> ⚠️ **Correção de fato:** o GLB feminino tem **duas** primitivas, não três —
> short e faixa dividem o material `Zenith_Shorts`. O que este arquivo dizia
> antes estava errado, e a trava do round-trip confirma 2 de 2 em todas as 37.
>
> **3.** ~~As peças~~ ✅ **as quatro rodadas fecharam** (sessões 26, 27, 29 e 30).
> O que sobra é a fila viva do bloco da sessão 30, no topo, e ela depende de
> decisão dele — não de trabalho de máquina.
>
> **4.** ~~Não existe banco de casos para o MORPH~~ ✅ **existe:**
> `scripts/morph_cases.py` + `test/morph_cases.json`, **608 casos** (era 8, de um
> avatar só). ⚠️ O arquivo tem **497 KB** — se isso pesar como fixture no app, o
> corte é gerar casos de um subconjunto, não deixar de ter árbitro.
>
> **5. `approved` NÃO é campo morto — falta só a metade que escreve.** Corrigido
> em 16/08: `select.py:61` e `:201` filtram por ele, e o `avatar_tester.html:323`
> também. O que não existe é alguém que grave `False` — `build_index.py:432` põe
> `True` fixo. Ou seja: **o mecanismo de não-servir um avatar já está pronto nas
> três implementações da regra; falta a lista de ids reprovados.** O `b09_d3`
> (32,4) e o `b10_d3` (45,1) leem masculinos e continuam sendo servidos.
>
> **6.** ~~O backup está desatualizado~~ ✅ **refeito em 16/08** —
> `zenith_assets_2026-08-16.zip`, 492 MB, conferido. Ver o bloco no topo.
> ⚠️ Continua no mesmo disco.
> ⚠️ **A primeira tentativa saiu sem o `01_raw`** e por isso 120 MB menor que o
> zip anterior — o que denunciou foi comparar a LISTA de pastas com a do zip de
> 31/07, não o tamanho. `01_raw` é o único material irreproduzível (custou
> crédito na Meshy); tudo o mais se refaz a partir dele.
> ⚠️ Continua **no mesmo disco** — protege contra erro meu, não contra falha de disco.
>
> ### 🎯 A FRENTE É INTEGRAÇÃO com o app Zenith
>
> A produção de avatares está parada (sem crédito na Meshy) e **não é o gargalo.**
>
> **➡️ LER `docs/INTEGRACAO_ZENITH.md` ANTES DE QUALQUER COISA** (4,4k). Ele abre
> com um §1b que resume o que a sessão 20 fechou. O que está aqui embaixo é só o
> essencial.
>
> ### 🔴 A DECISÃO PENDENTE QUE BLOQUEIA O PRÓXIMO PASSO — o peso do `chest`
>
> `chest` está marcado **`below_band` em 21 dos 51** avatares da faixa de usuário:
> em A-pose os braços fundem com o tronco abaixo da linha do mamilo, e aí o número
> deixa de ser peito. **Recomendação: não consertar a medida — dar peso menor (ou
> zero) ao `chest` na distância nesses avatares.** É decisão do Rogério, e ela
> define a função de distância. Ver `INTEGRACAO_ZENITH.md` §6b.
>
> **➡️ Próximo passo depois dela:** §6.3 — `build_index.py` indexando por medidas,
> com `waist_min`, aposentando `definition_thresholds_bodyfat_pct`.
>
> 📦 **O resto da sessão 20 saiu daqui** (contrato de medidas em 9 de 9 ·
> panturrilha medindo o joelho em 50 dos 76 · `chest` refutado como máximo de
> banda · trava `at_band_edge`). Está **inteiro** no `INTEGRACAO_ZENITH.md` §1b,
> que é leitura obrigatória antes de tocar o app — e as duas doutrinas que se paga
> caro para reaprender estão no `CLAUDE.md` (medida de fita é landmark) e no
> `LICOES.md` §1.8/§1.8b.
>
> ### 📤 O LADO DO APP está com ele, em outra sessão
>
> Prompt entregue: `docs/PROMPT_APP_INTEGRACAO.md`. Quatro tarefas:
> 1. rótulo `Abdômen` → `Cintura` — ✅ **liberado**, query rodada: 1 usuário, 2
>    linhas com `waist_cm`, e são dele. Sem migração.
> 2. texto do guia de ombro (largura → circunferência)
> 3. campo de ombro no onboarding + chave l10n `shoulder`
> 4. `coxa.png` — ✅ **feito aqui**: anel de 0,394 para **0,441**, dentro da banda
>    0,432–0,466 do `metrics.py`. Já gravado no repositório do app, **aguardando
>    commit do lado de lá**.
>
> ⚠️ **Três afirmações do §8 antigo eram falsas** (peitoral e ombro já eram anéis;
> ombro já era coletado). Eu tinha lido o **cabeçalho de comentário** do `.dart` em
> vez dos pixels. `LICOES.md` §1.7b.
>
> ### 🧪 TESTE DE CALIBRAÇÃO COM O CORPO DO ROGÉRIO — combinado, depois da integração
>
> Ele vai se medir com fita e balança. **Duas coisas diferentes, nesta ordem:**
>
> 1. **Só fita e balança, zero crédito** — testa se a *seleção* achou o melhor
>    corpo entre os 76 dados os números certos. Se isso já erra, avatar da Meshy
>    não conserta.
> 2. **Depois, um avatar dele na Meshy** — é a **única calibração da régua contra
>    uma pessoa real** que o projeto vai ter (os 76 são medidos por um script nunca
>    conferido contra fita), e dá o padrão-ouro visual lado a lado no testador.
>
> ⚠️ **Ressalva dita a ele:** com um sujeito só, o erro medido é a SOMA de (Meshy
> errando o corpo dele) + (`metrics.py` errando a leitura). Se der pequeno, os dois
> estão bons; se der grande, não dá para saber de qual lado.
>
> ⚠️ **Foto sozinha não dá centímetro** — sem escala e câmera calibrada, foto dá
> proporção. E prever corpo em cm a partir de folha 2D tem placar **0 de 5** neste
> projeto (`LICOES.md` §2.6).
>
> ⚠️ Altura: o `process.py` normaliza para 1,75 m. Comparar por
> `medida_avatar × (altura_real / 1,75)`, ou pelas razões.
>
> ### ▶️ A PRODUÇÃO REABRIU EM 14/09 — assinatura renovada, ~1000 créditos
>
> ~~A produção segue parada por falta de crédito~~ — **destravada.** A pauta é
> **`docs/COBERTURA_FORMAS.md`**, criado nesta sessão: o que falta não é só
> tamanho (o `handoff_biblioteca_corpos_faltando.md` do app conta o eixo de IMC),
> é **FORMA**. Feminino tem **zero** retângulo e **zero** maçã na faixa de
> usuário, e cintura-fina-com-glúteo-largo só existe em corpo de atleta `d3`.
> **Ordem dele: femininos primeiro** (1ª onda, 17 corpos).
>
> ### ✅ OS 39 SHORTS MASCULINOS ESTÃO DE VOLTA — 38 reaplicados na sessão 21
>
> O `restyle.py --all` da sessão 18 tinha apagado os 39 (leu os masters, que não
> têm peça). **Reaplicados 38/38 em 01/08**, todos em **v2**, com as v1
> aposentadas. Régua externa confirma: `probe_material_dist.py` lê os 76 do disco
> e devolve **76/76 no material certo, 39 com `Zenith_Shorts`**.
>
> ✅ **Nada se perdeu de decisão:** `config/shorts_map.json` estava intacto com os
> **39 ids** — *o mapa é o produto* (regra 3b). Custou tempo de máquina.
> ✅ **Duas travas novas, e as duas são a mesma pergunta:** o `restyle.py`
> **recusa** avatar com entrada no mapa (§4.2f), e o `probe_material_dist.py`
> agora **cobra a peça** de quem está no mapa em vez de exigir 1 material — era
> ele quem tinha lido os 76 apagados sem achar nada. Ver `LICOES.md` §4.2f.
>
> ### 🆕 O GLB entregue agora carrega VERSÃO NO NOME — não se sobrescreve mais
>
> `{id}_v{n}.glb`. A regra mora em `scripts/zenith_paths.py`
> (`dist_glb_current` / `dist_glb_next` / `dist_glb_retire`), e os cinco lugares
> que montavam `_v1` na mão passaram a usá-la: `process.py`, `restyle.py`,
> `shorts.py`, `qa_render.py` e o `avatar_tester.html` (que agora lê o nome do
> `assets.glb` do índice). **Sem flag `--bump`** — mudou o conteúdo, mudou o
> número. Motivo e efeitos em `LICOES.md` §4.2g.
>
> Versões correntes: **todas mudaram em 11/08** — o lote de morph gravou v(n+1)
> nos 76 e aposentou a anterior. Conferido depois: 76 arquivos, 76 ids, **nenhum
> id com duas versões no disco**, e nenhum `assets.glb` do índice apontando para
> arquivo que não existe. 🔴 **O Storage do app está com os GLBs VELHOS** — a
> subida só acontece depois da aprovação visual dele.
> ⚠️ **O `library.json` foi reconstruído** — ele estava parado em 31/07 e agora
> carrega também a panturrilha e o ombro corrigidos na sessão 20.
>
> ### 🔴 TRÊS DEFEITOS DO ÍNDICE, medidos, que bloqueiam a tela de objetivo
>
> 1. ~~**O índice usa a cintura errada.**~~ ✅ **RESOLVIDO em 21/08, e pelo lado
>    OPOSTO ao que este item propunha** — quem se mudou foi o app, não o índice.
>    Ver o bloco da sessão 31, no topo. Os dois corpos reais mediram no UMBIGO
>    apesar do rótulo já corrigido, e o viés é +2,8 cm no masculino contra
>    **+13,7 cm no feminino**. `waist_cm` → `waist_navel`.
> 2. **`definition_thresholds_bodyfat_pct` é inutilizável.** O app **não estima
>    gordura** em lugar nenhum; o campo é opcional e quase sempre nulo. E os 12
>    `f d3` medem 22,7–52,6% contra o `d3_below: 21.0` que o índice declara.
> 3. **Seleção por IMC sozinha quebra em 2 dos 6 objetivos do app** — `recomp`
>    devolve o avatar atual como meta, e `gain_muscle` devolve um corpo mais gordo
>    como "sua melhor versão".
>
> ✅ **Os defeitos 2 e 3 foram fechados pelo schema 4.** O 1 caiu em 21/08 pelo
> lado contrário: o anel do guia do app media **0,637** (cintura mínima), e quem
> estava errado passou a ser o **desenho**, não o índice. ✅ **Já desceu para
> 0,599** — `qa/probe/sondas/anel_guia.py`, sonda nova.
>
> ✅ **A pendência do `ombro.png` morreu:** o arquivo commitado é um **anel**. Foi
> ele quem estava certo.
>
> ### ✅ 76 avatares — 39 masculinos e 37 femininos
>
> A sessão 18 fechou **2**, os dois 8/8. `f d1` e `f d3` continuam completas.
>
> | linha | grade | slots | insrç. | faltam | quais |
> |---|---:|---:|---:|---:|---|
> | `f d1` | 12 (b01–b12) | **12** | 2 | **0** | ✅ completa |
> | **`f d2`** | 11 (b01–b11) | 9 | 2 | **2** | b07 b08 |
> | `f d3` | 9 (**b02–b10**) | **9** | 3 | **0** | ✅ completa |
>
> **Contar SEMPRE rodando `python scripts/contagem_slots_f.py`**, que deriva do
> `library.json` (§5.4). Ele nasceu na sessão 17 justamente porque contar à mão já
> errou duas vezes — a `d3` começa em `b02` e termina em `b10`, e um range
> `b01..b09` inventa um slot e esconde o `b10`.
>
> ### 🔴 OS 2 SLOTS QUE FALTAM SÃO O PIOR LUGAR PARA GASTAR O PRÓXIMO CRÉDITO
>
> Medido na sessão 18, e é o achado que decidiu onde o último crédito foi parar.
> O vão que `b07` e `b08` fechariam é `f d2` **34,4 → 52,6**, cujo **meio é 43,5**
> — fora do `USER_BMI_RANGE = (17, 40)` do `build_index.py:188`. O próprio índice
> classifica esse vão como **`low`**, e ele nem aparece na lista impressa (que é
> truncada em `gaps[:8]`). Somado a isso, ele é **zona morta medida** — duas
> categorias pesadas distintas pousaram em ~58–60.
>
> **Fechar `b07`/`b08` é fechar CONTAGEM, não cobertura**, e o `CLAUDE.md` é
> explícito: *"a meta é COBERTURA do eixo de IMC, não contagem."* Quando houver
> crédito de novo, **a decisão volta a ser do Rogério** — mas a recomendação é
> gastar em **inserção num vão `high`**, não nesses dois slots.
>
> ### 🎨 O MATERIAL MUDOU EM 31/07 — alumínio semifosco, aplicado nos 76
>
> `#B9BCC2` · metallic **0.25** · roughness **0.45** (era titânio `#6D737B` /
> 0.50 / 0.35). Escolhido pelo Rogério **no banco de ensaio do
> `avatar_tester.html`**, que agora troca cor/acabamento/luz em tempo real sobre o
> GLB real — decidido olhando os corpos sob o HDR de produção, não por argumento.
>
> Já rodado: `restyle.py --all` → **76/76**, confirmado por régua externa
> (`probe_material_dist.py` lê os 76 do disco). **O HDR não mudou** — a identidade
> Zenith continua sendo a luz.
>
> ⚠️ **O `restyle.py` estava QUEBRADO e ninguém sabia** — colisão do material novo
> com o nome do que vem do master (`Zenith_Body.001`), latente desde que os masters
> deixaram a fase roxa. Consertado; a lição inteira está em `LICOES.md` §4.2d,
> inclusive o driver que engolia a causa da falha.
>
> ### 🧭 A VISÃO DE API — avaliada, e os dois bloqueadores CAÍRAM (31/07)
>
> Tudo em **`docs/VISAO_PRODUTO.md`**. O que a sessão nova precisa saber:
>
> ✅ **Licença da Meshy: liberada.** Plano pago dá propriedade dos assets, sem
> atribuição, com direito de distribuir e vender. **Única restrição relevante
> (§2.6 dos Terms): não usar os assets para treinar modelo de IA concorrente da
> Meshy** — não afeta o plano atual, afeta um futuro plausível.
>
> ✅ **Backup feito e conferido:**
> `Desktop\ProjetosFlutter\_backup_zenith\zenith_assets_2026-07-31.zip`, 448 MB,
> batido pasta a pasta contra o disco. 🔴 **Está no MESMO disco** — protege contra
> apagão e reclassificação errada, **não** contra falha de disco. Tem que sair da
> máquina. Refazer a cada lote novo.
>
> ⚠️ **A topologia NÃO bloqueia o plano dele — eu avaliei o plano errado.** A
> medida (`LICOES.md` §4.4b) é verdadeira: morphar de um avatar para OUTRO é
> impossível. Mas o plano é shape key **local dentro de cada avatar** (bíceps,
> panturrilha), e para isso **cada malha carrega as suas** — topologia compartilhada
> não é exigida. Ele já tentou a via do avatar único num projeto anterior e falhou;
> a biblioteca de 76 existe justamente para o ajuste que sobra ser pequeno.
>
> ### ✅ A ORDEM DE TRABALHO — revista em 01/08
>
> 1. **Alinhar a biblioteca para a integração** — os 6 passos do
>    `INTEGRACAO_ZENITH.md` §6: medir ombro nos 76 · `chest` vira máximo na banda ·
>    índice por medidas com `waist_min` · `selection_cases.json` · vetor de
>    objetivo · integrar.
> 2. ~~**Reaplicar os 38 shorts masculinos**~~ ✅ **feito na sessão 21**, junto com
>    4 dos 11 da fila de correção. O que sobra dessa frente depende do olho dele.
> 3. ~~**Pintura das peças femininas**~~ ✅ **feita na sessão 22** — as 37 com
>    short **e** faixa, 76/76 no dist, réguas externas limpas. O que sobra é o
>    **olho dele no app**, não trabalho de máquina.
>
> O item 1 subiu na frente porque **o defeito do short se corrige no olho, e o
> lugar de olhar é o app** — corrigir 38 shorts em PNG e só depois descobrir no
> app é a ordem errada.
>
> O template/wrap **fica fora dessa ordem de propósito** — ele eliminaria o trabalho
> de short por-avatar, mas o app precisa do short agora. Custo de refazer visto e
> aceito; não é dívida esquecida.
>
> Pendente: **botões de cor no APP** (não no testador), círculos sem rótulo, default
> intocado se ninguém clicar — para responder a acusação de "app só gera avatar
> branco". **Cores de MATERIAL, nunca tons de pele:** o corpo é deliberadamente
> metálico e não-humano, e é isso que responde à crítica; tom de pele abre uma
> discussão de representatividade que hoje não existe.
>
> ### ⛔ DUAS ZONAS MORTAS CONFIRMADAS — parar de gastar geração nelas
>
> **1. `f d1` 34,1 → 42,6** (desde a sessão 16): cinco folhas, dois geradores.
>
> **2. `f d2` 34,4 → 52,6, medido na sessão 17.** Duas categorias pesadas
> distintas no ChatGPT pousaram no **mesmo ponto**: rugby de primeira linha
> **59,7** e arremesso de peso (folha reprovada, medida como duplicata do rugby).
> O atrator feminino pesado do ChatGPT mora em **~58–60**, e a faixa 35–50 não
> existe nele. É a mesma banda de peso da zona morta nº 1.
>
> **É caso de shape key no híbrido, não de mais uma redação.** A célula ainda não
> testada nas duas é **âncora intermediária (~28–31) no Gemini** — mas isso é uma
> receita de SUBIDA, escrita antes da §2.4c. **Reescrever para descida antes de
> gastar crédito nela:** ancorar em 52,6 e pedir mais leve.
>
> ### 🔴 O SINAL do passo domina o TAMANHO (§2.4c) — e o envelope de descida SUBIU
>
> **Subindo, o menor passo medido foi +7,6. Descendo, o maior agora é −5,4** — era
> −4,9 até a sessão 18, e o `b04i_d1` estourou para BAIXO a faixa declarada
> (previ 27–29, mediu 26,5). **Descida também erra**; a diferença é que erra por
> ~1 ponto, não por 20.
>
> **Consequência: vão estreito só se fecha DESCENDO** — ancorar ACIMA do alvo e
> pedir corpo mais leve. Ancorar abaixo e pedir mais pesado atravessa o vão inteiro
> e pousa do outro lado. Foi o que enterrou o `f d1` 24,1→31,9 (pousou em 44,4) e
> o `f d2` 34,4→52,6 (pousou em 59,7). Os dois acertos da sessão 18 foram descidas.
>
> **A causa é empilhar dois levers na mesma direção:** âncora-com-direção é um
> lever, categoria mais pesada que a da âncora é outro. **Um lever por folha vale
> para a direção também.**
>
> ### ✅ MEDIDO NA 18: para vão menor que ~6, o lever é a ÂNCORA, não a categoria
>
> O `CHARACTER_BIBLE` já dizia que passo menor que ~6,3 não se fecha trocando
> descritor. A sessão 18 usou isso **de propósito** no `b04i_d1`: manteve a
> categoria da âncora (sedentária sem tônus) e mandou só *"o MESMO tipo de corpo,
> porém mais leve"*, com uma lista do que muda e outra do que **não** muda. Passo
> −5,4 num vão de 7,8. É a primeira vez que o lever-âncora foi usado isolado, e
> funcionou.
>
> ### ⚠️ A SESSÃO 17 saiu daqui — está no `docs/historico/diario-2026-07.md`
>
> As doutrinas dela que continuam valendo seguem neste arquivo (§2.4c/d, régua
> `ombro/quadril`, zonas mortas). A narrativa de 7 avatares e 3 folhas reprovadas
> desceu para o diário, que é onde história mora.
>
> ### 🔴 NEGAÇÃO NÃO VENCE ATRATOR — três medidas na mesma sessão (§2.4d)
>
> *"Ela NÃO É OBESA"* → **44,4**. *"ELA É UMA MULHER, NÃO tem peitoral
> masculino"* → fisiculturista **masculino caricato**. *"os OMBROS DELA SÃO
> ESTREITOS"* → ombro **alargou**. A mesma cláusula funcionou nos dois acertos da
> sessão, onde não havia atrator puxando contra. **Contra atrator: trocar o
> gerador ou trocar o alvo, nunca reescrever.**
>
> ### ✅ RÉGUA NOVA E ÚTIL: `ombro/quadril` na folha 2D (§1.4d)
>
> As seis folhas `d3` que geraram corpo feminino ficam em **0,940 a 1,050**; a que
> gerou o `b09_d3` masculino dá **1,212**. Reprovou duas folhas do `b03_d3` antes
> da Meshy (1,103 e 1,104) e aprovou a terceira (1,059) e o `b02_d1` (1,029).
>
> ⚠️ **O que ela NÃO pega:** busto virado peitoral e mandíbula. O par 3D
> `quadril/peito` só acusa o caso extremo (`b10_d3` em 0,879); o `b09_d3` dá 1,142,
> no meio do pelotão. Esses dois defeitos continuam sendo **olho no preview**.
>
> ⚠️ **E a §1.4c dá FALSO POSITIVO em passo descendente** — quando o corpo inteiro
> encolhe, o quadril cai em absoluto por construção. As três descidas aprovadas
> desta sessão disparam a assinatura e vieram femininas.
>
> ### ⚠️ `zen_f_b10_d3` — o segundo asset que lê MASCULINO
>
> IMC 45,1, 8/8. Mas é **caricatura**: trapézio engolindo o pescoço, deltoides e
> braços fora de escala humana, mandíbula masculina, busto virado peitoral. Não
> existe competidora de Ms. Olympia assim. **A trava de identidade feminina estava
> no prompt, literal, e não segurou.**
>
> Regra 5b: **fica**. Mas agora a `f d3` tem os **dois** corpos do topo lendo
> masculino — 32,4 (`b09_d3`) e 45,1 — e como o campo `approved` é morto, os dois
> são servidos. **Não gastar geração acima de IMC ~30 na `d3` no ChatGPT.**
>
> 🔴 **PENDÊNCIA DE PRODUTO ABERTA (agora com 2 assets):** o `approved` é **lido**
> pelas três implementações da regra (`select.py:61` e `:201`, tester `:323`),
> mas o `build_index.py:432` grava **`True` fixo** — então não existe como manter
> um asset no acervo sem servi-lo. Falta a lista de ids reprovados.
> ⚠️ Este parágrafo dizia "nada o lê" até 16/08, e estava errado.
>
> 🔴 **O método de QA, cobrado por ele:** *"você é o especialista em corpo humano,
> não tem como eu decidir algo no olho assim, a menos que seja uma inconsistência
> grande ou defeito na pintura do short."* **Não pedir a ele veredito de
> anatomia.** Anatomia é medida e julgada aqui.
>
> ### ✅ Bandas fora de ordem no id — DECIDIDO em 16/08: são rótulo histórico
>
> **Decisão dele, tomada com a medida na mão.** São **10 inversões em 5 linhas**
> (ex.: `b07_d1` 31,9 antes do `b06_d1` 32,4; `b09_d1` 34,1 antes do `b08_d1`
> 42,6). Ficam como estão.
>
> ⚠️ **E o que eu tinha reportado como "o nome mente" estava impreciso:** o campo
> `label` do índice **não** vem da banda — `build_index.py:259` o deriva da razão
> **cintura/altura medida** (0,43 muito magra · 0,50 magra · 0,55 média · 0,63
> cheia · 0,75 muito cheia). O label é honesto. O que está fora de ordem é só o
> número `b01..b12` **dentro do id**.
>
> **E nada no produto lê esse número:** a seleção usa medidas, o índice ordena por
> `measured_bmi`, o tester ordena por `measured_bmi`, os vãos de cobertura também.
> Renomear custaria 76 GLBs + as chaves dos dois mapas + invalidar a URL de CDN
> de todo mundo que já baixou — a regra 8 inteira, para consertar um sintoma que
> só existe para quem lê nome de arquivo.
>
> ⚠️ **`b03_d3` e `b02_d1` são quase-empates com os vizinhos** — 16,1 contra 16,9
> e 16,4 contra 16,5. Fecharam slot de grade; **cobertura de IMC, quase nenhuma.**
> O que separa o `b02_d1` do `b01_d1` é a coxa: 52,2 cm contra 46,1.
>
> ✅ **Os dois da sessão 18 NÃO entraram fora de ordem** — `b03_d2` (19,8) caiu
> entre o `b02_d2` (18,3) e o `b04_d2` (22,2), e o `b04i_d1` (26,5) entre o
> `b04h_d1` (24,1) e o `b07_d1` (31,9). É consequência direta de descer: quem
> ancora acima e pede mais leve não pula vizinho.
>
> ⚠️ **Busto no limite alto do "PEQUENO A MÉDIO"** — a linha de reforço
> (*"não aumentá-lo, ele é pequeno"*) segue em todos os prompts e deve continuar.
>
> ### 🔴 O QUE NÃO SE FAZ MAIS: prever IMC pela folha
>
> **Cinco preditores construídos, cinco mortos** (`LICOES.md` §2.6). A folha 2D
> serve para (a) **reprovar geometria** e (b) **reprovar forma** (§1.4b/c/d) — dois
> usos que na sessão 17 pegaram 3 folhas ruins antes da Meshy. Quem diz o número é
> o `metrics.py`. **Registrar a previsão continua valendo**, porque é ela que
> revela o erro, mas é palpite declarado e não deve gastar tempo de cálculo.
>
> ### 🔧 Cinco pegadinhas de régua que se pagam caro — em `LICOES.md` §1.1 e §1.4d
>
> - **O `sheet_qa` vazou em 5 das 10 folhas medidas nesta sessão** — leu figura a
>   partir de `y=0`, base 45 px abaixo do pé, altura 8,54% divergente onde o
>   `crop.py` lia 0,43%. **Cruzar sempre com o `crop.py`**, que é o detector do
>   caminho do produto. Para testar folha duvidosa, usar id descartável
>   (`zen_f_b99_d3`) + `--force`, nunca o id real.
> - **A leitura do OMBRO quebra sozinha** (`at_frac` 0,194 fixo): já deu
>   `cintura/ombro` 1,543 e 70 px contra 189 px. Fora de 0,9–1,3, descartar.
> - **A sonda de tônus AFIRMA, mas não NEGA.** Silêncio dela não reprova `d3`.
> - **`thigh` e circunferências de tronco não valem por avatar** — `at_frac` fixo
>   contra virilha que se move. Usar `volume_l`.
> - **Nenhuma trava valida orientação frontal** (§4.2c) — isso é olho, no preview.
>
> ### ✅ Corpo feminino vem ~2,8 mais leve que o masculino no mesmo descritor `d3`
>
> Escada da `m d3` para planejar: 19,9 · 20,8 · 21,1 · 23,8 · 27,0 · 27,4 · 32,4 ·
> 34,7 · 35,7 · 53,8.

> **Este arquivo só guarda o AGORA.** Doutrinas duráveis estão em
> `docs/LICOES.md`; a narrativa de como cada uma foi descoberta está em
> `docs/historico/diario-2026-07.md`. Se algo aqui virar história, **mover** —
> não deixar crescer. Ele já teve 1631 linhas e não cabia numa leitura.

---

## ➡️ O fluxo, passo a passo

> **Não listar render como pendência.** O Rogério avalia no app de testes e **não
> dá veredito de anatomia**. Quem mede e decide se o avatar presta é o Claude Code.

As duas primeiras linhas valem **só em folha do ChatGPT** (§1.1). A referência
delas é a **âncora usada**, não a folha-mãe. Usar `--from` sempre que houver mais
de uma folha em Downloads — não depender de qual é a mais recente.

```
python scripts/sheet_qa.py "<folha em Downloads>" 00_input/sheets/f/<ancora>_sheet.png
   -> conferir: ombro/quadril em 0,94-1,05 (§1.4d) · razoes nao paradas (§1.4b)
   -> se a assinatura de vazamento aparecer, remedir pelo crop.py:
      python scripts/intake.py zen_f_b99_d3 --from "<folha>" --force
      python scripts/crop.py   zen_f_b99_d3 --check   (e apagar a folha b99 depois)
cd qa/probe/sondas && python probe_tonus_f.py "<ancora COMPLETO>" "<folha>"
   (recebe CAMINHOS de arquivo, nao ids - passar id da erro de arquivo nao achado)
python scripts/intake.py  zen_f_bXX_d3 --from "<caminho da folha>"
python scripts/crop.py    zen_f_bXX_d3
   (Meshy 14/09/2026: Multi-View so roda em MESHY 7 - Flagship / Alto Detalhe.
    Trocar para Meshy 6 ou Smart Topology FAZ O MULTI-VIEW SUMIR - nao da mais
    para reproduzir o caminho dos 76. Resolucao PADRAO (20 cr; Ultra 2K custa
    25), SEM textura (+10), SEM dividir (+10), Pose DESLIGADA, licenca Privado.
    O slot da lateral tanto faz - medido.
    ⚠️ Os 76 sao Meshy 6: a troca de gerador de MALHA nao foi medida. Ver
    docs/COBERTURA_FORMAS.md §8.)
python scripts/process.py zen_f_bXX_d3      # 60k, 8/8
python scripts/metrics.py zen_f_bXX_d3
python scripts/build_index.py               # imprime os vaos
python scripts/contagem_slots_f.py         # imprime os slots de grade que faltam
python scripts/restyle.py --preview zen_f_bXX_d3
```

O GLB do Downloads vira `01_raw/{id}_raw.glb` — **com o sufixo `_raw`**, senão o
`process.py` diz que não existe.

**Os passos que eu pulo são sempre os do FIM** (§6.2b): `probe_tonus_f` e
`restyle --preview` não bloqueiam nada e por isso somem quando a sessão acelera.
Reler este bloco linha a linha antes de dizer que um avatar acabou.

> ### 🔴 RITMO DA ESTEIRA — cobrado pelo Rogério em 30/07, sessão 15
>
> *"É só pra seguir o fluxo: gera prompt, passou, cropa, gero GLB, você recebe,
> organiza na biblioteca e já manda próximo prompt."* E: *"você parece que a cada
> sessão vem com uma personalidade diferente, preciso de consistência."*
>
> 1. **UM prompt por vez.** Ele recusou explicitamente a ideia de mandar 2–3
>    prompts adiantados: *"se mandar 3 e der erro em um, ficam 2 travados no meio
>    da conversa, eu preciso voltar ou pedir de novo, e vira bagunça."* **Não
>    propor isso de novo.**
> 2. **O prompt vai SEMPRE completo**, nunca só o bloco `TIPO DE CORPO` a trocar.
> 3. **Não documentar entre um avatar e outro, e não commitar sem ele mandar.**
>    Documentação é despejada de uma vez no fim da sessão, quando ele pedir. Na
>    sessão 15 a escrita entre avatares custou mais tempo que a produção.
> 4. Entre um avatar e o próximo, a saída é só: **veredito da medida, o número, e
>    o prompt seguinte.**
>
> **O gargalo real são 3 dias sem fechar a biblioteca** — e a causa não é a Meshy,
> é tudo que eu escrevo em volta.

**Ao olhar o preview, olhar DUAS coisas:** se o relevo sobreviveu ao 60k **e se a
identidade do personagem se manteve**. Foi a segunda que falhou no `b09_d3`,
enquanto eu vigiava a primeira.

---

## ✅ AS 37 FEMININAS ESTÃO PINTADAS — short **e** faixa, 76/76 no dist (sessão 22)

`shorts.py --apply` nas 37, cada uma gravando versão nova e aposentando a
anterior. **Nenhum id com duas versões no disco; `library.json` bate 76 de 76.**

Réguas externas rodadas depois, as duas limpas:
- `probe_material_dist.py` → **76/76** em `#B9BCC2` / 0.25 / 0.45, e **ninguém do
  mapa sem `Zenith_Shorts`** (é a trava que teria pego o apagão de 31/07).
- `--check --all` → **76/76 ok**, zero `CONFERIR`, zero `ILHAS`, pior peça 100,0%
  em todos — inclusive nos 4 em que a faixa é legitimamente partida em duas
  (`b10_d2`, `b10_d1`, `b11_d2`, `b12_d1`).

🔍 **A faixa NÃO invade braço em nenhum dos 37** — varredura visual das 37 em
tiras recortadas na região da peça (`qa/probe/sondas/_tira_faixa.py`), de IMC 18 a
114. O que parecia serrilha no `b09_d2` é o degrau de **24 setores de azimute**,
por construção, mais a faixa aparecendo **atrás** do braço, corretamente.

🔴 **Um achado grande, e a decisão é dele:** a **subida frontal da faixa não é
medida em avatar nenhum** — de 4 a 9 dos 9 setores da frente não têm aro, e o
traçado sai de ruído alisado pela mediana. Piso sobre o pico foi **testado e
refutado** (reescreve 9–24 setores de todos os 37, inclusive dos certos). O
conserto é **modelar** a subida, muda os 37 e **não tem régua externa**. Válvula
em uso: `"faixa_topo_reto": true`, hoje só no `b08_d3`. Detalhe em
`LICOES.md` §4.5b.

⚠️ **Uma trava foi trocada, com medida:** a de crescimento da costura dividia por
contagem total de triângulos (**área**) o custo de uma **curva**, e reprovava o
`zen_f_b11_d1` a +6,2% — que, normalizado por `frac`, está **abaixo da mediana
feminina**, enquanto o campeão do acervo (0,265) é **masculino aprovado**. Agora
é `costura / frac`, teto 0,40. `LICOES.md` §4.3d.

---

## ▶️ Frente do SHORT — os 39 estão no dist, e a fila de correção caiu de 11 para 7

✅ **Reaplicados 38/38 em 01/08 (sessão 21)**, `build_index.py` rodado depois — o
nome do arquivo mudou para `_v2`.

✅ **A fila de CORREÇÃO andou pela primeira vez desde a sessão 6.** Ele reprovou
**12 no olho**; `b12_d1` já estava feito e **mais 4 foram consertados por medida**
— `b08_d3`, `b09_d1`, `b11_d1`, `b11_d2`, que eram os quatro com a **bainha nunca
medida** (`hem_peaks_zh` vazio nas duas pernas, short 7–8 cm comprido demais). O
erro contra a folha caiu de −0,041…−0,048 para **±0,015**. Receita e calibração em
`LICOES.md` §4.3b.

🔴 **Sobram 7, e para esses NÃO existe defeito medido:** `b07_d1` `b07_d3`
`b08_d1` `b08_d2` `b09_d2` `b10_d1` `b10_d2`. As três réguas passam neles (altura
contra a folha, traçado do cós, região conexa). **Como o combinado é um por vez
com print dele, essa fila só anda com o olho dele no app** — não gastar sessão
adivinhando qual é o defeito.

🆕 **`BAINHA-CHUTE` no `--report`.** O chute da bainha caía no meio da faixa da
trava *por construção* (a faixa é ancorada na virilha, e o chute é
`virilha − 0,035`). Agora o mapa denuncia bainha que nunca foi medida — mesma
família do `at_band_edge` do `metrics.py`.

✅ **O feminino saiu do zero: as 37 têm as DUAS peças** (faixa + short), aplicadas
na sessão 22 — ver o bloco acima. As duas têm borda em **anel fechado**, que é a
topologia que o detector sabe achar (§4.5).

**Defeito de short É um dos dois vereditos que o Rogério dá no olho** — o outro é
inconsistência grosseira. E o lugar de dar esse veredito passou a ser **o app**,
não pasta de render: é por isso que a integração subiu na frente.

---

## 👁️ QA visual — o que ele já aprovou

### 🆕 02/08 — ele revisou **os 76**, os dois sexos, com as peças pintadas

A revisão mais completa que o projeto já teve: primeira vez que ele olhou a
biblioteca inteira **com short e faixa nos dois lados**. Veredito:

> *"eu revisei todos, tanto masculinos quanto femininos, vc fez um excelente
> trabalho, os masculinos faltam bem poucos pra gente finalizar, são pequenos
> ajustes finos. nos femininos faltam mais porem vc fez um avanço gigante e faltam
> alguns, na proxima sessão irei listar os que faltam, os femininos a maioria é
> defeito mais no top."*

**Nada a reclassificar por reprovação visual** — nenhum avatar foi condenado, e
regra 5b segue: o que falta é conserto de peça, não asset novo.

| lado | estado | tamanho do que falta |
|---|---|---|
| masculino | **quase fechado** | "bem poucos", "pequenos ajustes finos" |
| feminino | avanço grande, fila maior | "faltam alguns", **maioria no TOP** |

🔴 **A lista vem no começo da próxima sessão, começando pelos femininos.** Ver o
bloco de abrir, no topo deste arquivo — e **não adiantar a fila.**

⚠️ **Isso NÃO substitui a fila dos 7 masculinos sem defeito medido** (`b07_d1`
`b07_d3` `b08_d1` `b08_d2` `b09_d2` `b10_d1` `b10_d2`, mais abaixo). Não sei ainda
se os "poucos" que ele viu são esses sete, um subconjunto, ou outros — **não
presumir que são a mesma lista.** Confirmar quando ela chegar.

### O histórico

**Sessão 12:** *"estão bons os avatares que abri no teste."* **Sessão 13:**
*"avaliei e estão bons os avatares do ambiente de teste."* Nada a reclassificar
por reprovação visual.

Os 4 `d3` da sessão 13 ele ainda não abriu no testador, mas isso **não bloqueia**
— o `b09_d3` já tem parecer meu (lê masculino) e a decisão dele já saiu.

Servidor: **`testador.cmd` na raiz do repositório** (clique duplo) → abre o
navegador em `http://localhost:8765/test/avatar_tester.html` e deixa o
`http.server` de pé enquanto a janela preta estiver aberta.

🔴 **Sempre por http; `file://` não serve** — o testador lê o `library.json` por
`fetch` e o model-viewer carrega GLB e HDR por URL relativa; em `file://` o
navegador barra os três e a página sobe em branco.

⚠️ **Em 15/08 o ambiente "parou de abrir" e não havia nada quebrado**: o servidor
subia junto com a sessão de trabalho (`preview_start` na config `static` do
`.claude/launch.json`) e morria com ela. O `testador.cmd` existe para o servidor
não depender de sessão nenhuma. Conferido depois de subir: HTML 200,
`library.json` 200, o GLB que o índice aponta 200, o HDR 200.

Não pedir opinião sobre PNG de `qa/look/`. E se ele reprovar algum: regra 5b,
reclassificar ou inserir, nunca regerar.

## Pendências que não bloqueiam

- ✅ **As três cópias soltas do mapa saíram do repositório em 12/08**, por ordem
  dele: foram para `_backup_zenith/mapas_soltos/`. Nenhuma foi apagada — o mapa é
  o produto (regra 3b) — e a `sessao21.json` é byte a byte igual ao commit
  `531f403`, enquanto as duas `.bak` não batem com commit nenhum, que é
  justamente por que não se apaga.

- 🔴 **`approved` — falta só quem escreve `False`.** ⚠️ Corrigido em 16/08: este
  item dizia "campo morto, nada lê", e estava **errado** — `select.py:61` e
  `:201` filtram por ele e o `avatar_tester.html:323` também. O que falta é a
  metade que ESCREVE: `build_index.py:432` grava `True` fixo, então nunca há
  como um asset ficar no acervo sem ser servido. Conserto: uma lista de ids
  reprovados lida pelo `build_index.py`. O `b09_d3` (32,4) e o `b10_d3` (45,1)
  leem masculinos e **continuam sendo servidos**.
- 🔴 **A leitura padrão passou de 17,5k:** `CLAUDE.md` 6,4k + este **11,2k** antes
  de qualquer trabalho, e o `LICOES.md` está em **26,3k**. O corte da sessão 22
  não bastou e a 24 acrescentou de novo (bloco de morph aqui, §12 no
  `INTEGRACAO_ZENITH.md`, §7.9–§7.14 nas lições). **Enxugar não vence escrita
  nova.** O candidato óbvio a descer para o diário é o bloco da sessão 18 (a
  tabela de 2 avatares e a escada de categorias), que é história. Remedir com
  `(Get-Content <arquivo> -Raw -Encoding UTF8).Length / 3.6 / 1000`.
- ⚠️ **Backup feito, mas no MESMO disco** (`_backup_zenith/zenith_assets_2026-07-31.zip`,
  448 MB). Protege contra apagão e reclassificação errada, **não** contra falha de
  disco. Tem que sair da máquina. **Refazer a cada lote novo** — e agora ele está
  **76 arquivos atrás**: na sessão 21 os 39 masculinos viraram `_v2` e na 22 as 37
  femininas ganharam short+faixa, com as versões anteriores aposentadas. **O zip
  inteiro guarda GLB que não existe mais no disco.** Ver `VISAO_PRODUTO.md` §6.2.
- ✅ **Licença da Meshy: verificada e liberada** em 31/07 (plano pago dá
  propriedade, sem atribuição, com direito de distribuir e vender). A única
  restrição é a §2.6 dos Terms: não treinar modelo de IA concorrente da Meshy.
  Detalhe e ressalvas em `VISAO_PRODUTO.md` §6.1.
- 🔴 **A regra de seleção tem DUAS implementações e vai virar três.** `nearest_id`
  em Python (`build_index.py`) e de novo em JS (`avatar_tester.html`); a
  integração cria a de Dart. O conserto é o `selection_cases.json`
  (`INTEGRACAO_ZENITH.md` §6.4) — sem ele, o que diverge é *qual corpo o usuário
  vê*, em silêncio.
- ⚠️ **`intake.py` grava a folha mesmo quando o `crop.py` roda com `--check`.**
  Para testar folha duvidosa, usar id descartável (`zen_f_b99_d3`) com `--force`
  **e apagar a folha b99 depois** — usei esse padrão 4 vezes na sessão 17 e
  funcionou. Com o id real, o `intake` seguinte barra ("folha aprovada não se
  substitui") e o `crop` roda na folha velha.
- ⚠️ **Nenhuma trava cruza a vista FRONTAL com a de PERFIL.** O `sheet_qa` mede as
  duas, mas não checa se contam a mesma história — 3 vistas discordando passariam
  limpo e a Meshy fundiria três corpos. Na sessão 18 isso quase custou o último
  crédito, e o que resolveu foi **recortar e ampliar** as duas folhas lado a lado
  (`LICOES.md` §1.6b). Miniatura não é leitura de anatomia.
- ⚠️ **Duas folhas de referência não são legíveis pelo `sheet_qa`:**
  `zen_f_b09h_d2_sheet.png` (2528×1684, devolve 1 figura cobrindo a imagem) e
  `zen_f_b03_d1_sheet.png` (topo espalhado 101 px, altura 4,37%). Elas **servem
  de âncora para gerar**, mas não servem de referência para as travas de razão —
  nesses casos, bracketar contra outra folha e usar só as razões, que são
  invariantes de escala.
- ⚠️ **Os avatares NÃO entram em commit nenhum.** O `.gitignore` cobre
  `00_input/`, `02_master/` e `03_dist/` — folha, master e GLB existem só no
  disco local do Rogério. O git guarda o índice, as medidas e a documentação.
  **Não há backup dos assets**, e uma reclassificação é irreversível pelo git. Se
  isso importar um dia, a conversa é sobre LFS ou storage externo.
- ✅ **`state.md.cauda.tmp` não existe mais** — conferido na sessão 17, a pendência
  estava obsoleta.
- ❌ **`render.py` (turntable) NÃO SERÁ ESCRITO — avaliado e descartado em
  16/08, a pedido dele.** Ele existia para responder *"GLB ou turntable como
  formato de entrega?"* (README §215), e **a integração respondeu**: o app roda
  GLB no model-viewer, no device, desde 04/08, com morph em cima. Turntable é
  sequência de imagem — não gira sob controle do usuário, não recebe shape key e
  não reaproveita o HDR, que é metade da identidade Zenith. Sairia um formato
  que nada consome. O campo `assets.turntable` do índice fica como `null`; não
  custa nada e o schema já está publicado no app.
- **Dois vãos `high` masculinos seguem abertos: d1 27,8→33,3 e d3 27,4→32,4.**
  Método medido: âncora única em **IMC alvo − 7** e gerar no **Gemini**. Para o
  `m d1` dá âncora ~23,5 mirando ~30,5; para o `m d3`, âncora ~23 mirando ~30.
  ⚠️ **Reavaliar esse método à luz da §2.4c** — ele é uma receita de SUBIDA, e a
  sessão 17 mediu que subida estoura. Pode ser que o certo seja descer de cima.
- Lado do app Zenith (outro repositório): ver o fim do diário, seção 10.
