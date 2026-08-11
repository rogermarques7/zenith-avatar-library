# state.md — o presente

Última atualização: **11/08/2026, fim da sessão 25**

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
> python scripts/select.py --check       # 34/34
> cp library.json          ../zenith/assets/avatars/library.json
> cp config/morph_map.json ../zenith/assets/avatars/morph_map.json
> cp test/selection_cases.json ../zenith/test/fixtures/selection_cases.json
> cd ../zenith && python scripts/publish_avatars.py
> ```
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
> nova de GLB e a anterior aposentada. Distribuição: **35 avatares com 10 shape
> keys, 33 com 9, 5 com 8, 3 com 7** — o que falta em cada um está em
> `dropped_columns` no mapa, e o motivo é sempre régua, nunca desistência.
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
> **4. 🔴 A COXA NÃO É MEDÍVEL NO DIST — e isso é padrão, não avatar (§7.25).** A
> banda da coxa lê a PEÇA: desvio até **+6,9 cm no masculino e +14,5 cm no
> feminino** contra o `library_metrics.json`, com as outras oito colunas batendo
> em ±0,1. Resultado: **28 dos 76 estão sem morph de coxa** (21 femininos, 7
> masculinos). O conserto provável é medir a coxa com a virilha **do master**, e
> isso mexe no `metrics.py`, que a biblioteca inteira usa — **sessão própria.**

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
> ### 🆕 A LISTA DAS PEÇAS CHEGOU (11/08) — está em `docs/FILA_PECAS.md`
>
> A fila que a sessão 22 esperava. **30 dos 37 tops femininos** em três classes
> que ele definiu com screenshot (mínima = listra fina na borda de cima ·
> mediana = listra maior + ponto sem pintar · maior = top quase todo errado) e
> **7 shorts masculinos**, que são os sete mais pesados do acervo (`b09_d1` a
> `b12_d1`, IMC 63 a 148). **Ele mandou começar pelos tops femininos.**
>
> 🔴 **A lista é o produto — não varrer os outros procurando defeito.** E há
> **duas coisas a confirmar com ele** antes de mexer: três avatares aparecem em
> duas classes, e o `b03_d3` (o exemplo que ele mandou de "mínima") não está na
> lista. Detalhe no `FILA_PECAS.md`.
>
> ✅ A classe "mínima" é a **borda de cima da faixa**, que a §4.5b do `LICOES.md`
> já tinha medido como *não medida em avatar nenhum*. Agora são duas linhas
> independentes no mesmo lugar, e a decisão de **modelar** a subida deixou de ser
> especulação: tem demanda.
>
> ### 📄 O PROBLEMA DA COXA ESTÁ ESCRITO PARA LEITOR DE FORA — `docs/PROBLEMA_COXA.md`
>
> A pedido dele, para consultar um modelo mais avançado. E **escrever mudou o
> diagnóstico**: não é o tecido do short entrando na medida. Medindo o dist com o
> `metrics.py` cru dá **+1,1 cm**; o que dá **+18,5** é a **cópia soldada** que o
> `morph.py` usa — a mesma soldagem que conserta o antebraço. Três caminhos
> plausíveis estão listados lá, nenhum testado.

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
> **3. As peças.** A fila de short masculina e o defeito de faixa feminino — ver
> os dois blocos abaixo. **A lista dele nunca chegou** e é a primeira coisa a
> pedir quando a frente voltar.
>
> **4.** ~~Não existe banco de casos para o MORPH~~ ✅ **existe:**
> `scripts/morph_cases.py` + `test/morph_cases.json`, **608 casos** (era 8, de um
> avatar só). ⚠️ O arquivo tem **497 KB** — se isso pesar como fixture no app, o
> corte é gerar casos de um subconjunto, não deixar de ter árbitro.
>
> **5. `approved` continua campo morto** — `build_index.py:164` grava `True` fixo
> e nada lê. O `b09_d3` (32,4) e o `b10_d3` (45,1) lêem masculinos e são servidos.
>
> **6. O backup está 78 arquivos atrás e no mesmo disco.**
>
> ### 📋 A FILA DE CORREÇÃO DOS SHORTS CONTINUA CONGELADA
>
> Ele revisou os 76 no testador em 02/08 e mandou congelar a frente de shorts
> para retomar a integração. **A lista dele nunca chegou** — quando a sessão de
> shorts voltar, é ela a primeira coisa. Regra §6.1: não adiantar, não varrer os
> 37 procurando defeito de faixa.
>
> ### 📋 O bloco abaixo é da sessão 22 e está mantido por contexto
>
> ### 📋 A PRIMEIRA COISA DAQUELA SESSÃO ERA RECEBER A LISTA DELE
>
> Ele revisou **os 76 no testador em 02/08** e o veredito foi de aprovação geral —
> mas com fila de correção, e **ele disse que manda a lista na sessão seguinte,
> começando pelos femininos**:
>
> > *"eu revisei todos, tanto masculinos quanto femininos… os masculinos faltam
> > bem poucos pra gente finalizar, são pequenos ajustes finos. nos femininos
> > faltam mais… os femininos a maioria é defeito mais no top."*
>
> 🔴 **NÃO ADIANTAR ESSA FILA.** Não varrer os 37 procurando defeito de faixa, não
> propor conserto em massa, não "já ir consertando os óbvios". A lista é dele e
> vem no começo da sessão — regra §6.1, *um por vez é um por vez*. O que se faz
> antes dela chegar é **nada de produção**.
>
> 🔴 **E o defeito dos femininos é no TOP — o que é evidência, não só uma queixa.**
> Ele diz que a maioria dos defeitos femininos está na faixa. A medida da sessão 22
> diz que a **borda de cima da faixa não é medida em avatar nenhum** (`LICOES.md`
> §4.5b). São **duas linhas independentes apontando o mesmo lugar**: o olho dele e
> o sweep. Quando a lista chegar, a pergunta a fazer primeiro é se o defeito
> listado é a **subida frontal** — e, se for, a decisão de **modelar** a subida
> (que muda os 37) deixa de ser especulação e passa a ter demanda.
>
> ⚠️ **O que ainda falta para poder decidir isso:** saber *como* o defeito se
> parece. "Defeito no top" pode ser subida errada, altura errada, largura errada
> ou borda serrilhada — e são consertos diferentes. **Perguntar, ou pedir print,
> antes de escolher o método.**
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
> ### 🛑 A produção de avatares segue parada por falta de crédito na Meshy
>
> **Não montar prompt de folha, não pedir geração, não propor "só mais um"** — a
> folha é grátis, o GLB não é, e uma folha aprovada esperando crédito é trabalho
> que envelhece.
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
> 1. **O índice usa a cintura errada.** O app ensina a medir a **mais estreita**;
>    o `build_index.py` usa `waist_navel`. Diferença mediana **6,5 cm** na faixa de
>    usuário, máx 24,2 cm — sistemática, para o lado gordo.
> 2. **`definition_thresholds_bodyfat_pct` é inutilizável.** O app **não estima
>    gordura** em lugar nenhum; o campo é opcional e quase sempre nulo. E os 12
>    `f d3` medem 22,7–52,6% contra o `d3_below: 21.0` que o índice declara.
> 3. **Seleção por IMC sozinha quebra em 2 dos 6 objetivos do app** — `recomp`
>    devolve o avatar atual como meta, e `gain_muscle` devolve um corpo mais gordo
>    como "sua melhor versão".
>
> ✅ **Os três seguem de pé, e o conserto é o passo 3** — mas note que o defeito 1
> ganhou confirmação independente na sessão 20: o anel do guia do app cai em
> `at_frac` 0,645, e o `waist_min` da biblioteca em 0,644. **O desenho do app mede
> a cintura mínima**, exatamente como o índice NÃO faz.
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
> 🔴 **PENDÊNCIA DE PRODUTO ABERTA (agora com 2 assets):** o campo `approved` do
> `library.json` é **fixo em `True`** no `build_index.py:164` e **nada o lê** — nem
> o `avatar_tester.html`. Não existe mecanismo para manter um asset sem servi-lo.
> O conserto é `build_index.py` lendo uma lista de ids reprovados, com o
> `nearest_id` ignorando-os.
>
> 🔴 **O método de QA, cobrado por ele:** *"você é o especialista em corpo humano,
> não tem como eu decidir algo no olho assim, a menos que seja uma inconsistência
> grande ou defeito na pintura do short."* **Não pedir a ele veredito de
> anatomia.** Anatomia é medida e julgada aqui.
>
> ### ⚠️ Rótulos fora de ordem — a lista cresceu, e não foram consertados
>
> `b09_d1` (34,1) × `b08_d1` (42,6) invertidos · `b06_d1` (32,4) × `b07_d1` (31,9)
> · `b10_d2` (52,6) × `b09_d2` (53,9) · e agora `b05_d1` medindo **44,4** entre o
> `b08_d1` e o `b11_d1`, `b03_d3` medindo **16,1** abaixo do `b02_d3`, e `b02_d1`
> medindo **16,4** abaixo do `b01_d1`. Não quebra o app (o `nearest_id` usa IMC
> medido), mas o **nome mente sobre a ordem**. Decisão do Rogério pendente:
> reclassificar, ou aceitar que o rótulo de banda é só histórico.
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
   (Meshy: Multi-View, Meshy 6 Padrao, densidade alta, SEM textura,
    divisao automatica DESLIGADA. O slot da lateral tanto faz - medido.)
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

Servidor: `preview_start` na config `static` (`.claude/launch.json`, porta 8765)
→ `http://localhost:8765/test/avatar_tester.html`. **Sempre por http; `file://`
não serve** porque o testador lê o `library.json` por `fetch`.

Não pedir opinião sobre PNG de `qa/look/`. E se ele reprovar algum: regra 5b,
reclassificar ou inserir, nunca regerar.

## Pendências que não bloqueiam

- ⚠️ **Três cópias soltas do mapa esperando decisão antes do commit:**
  `config/shorts_map.json.bak`, `.bak2` e `shorts_map.sessao21.json`. **Não
  apaguei** — o mapa é o produto (regra 3b), e apagar backup de produto sem ele
  mandar é a decisão errada de tomar sozinho. Mas eles estão **fora do
  `.gitignore`**, então entram no primeiro `git add .` como se fossem fonte.
  Decidir: apagar, ignorar, ou mover para fora do repositório. O mesmo vale para
  `qa/`, que hoje é untracked inteiro e guarda render.

- 🔴 **`approved` é campo morto, e agora com DOIS assets dependendo dele.** O
  `build_index.py:164` grava `True` fixo e nada lê — nem o `avatar_tester.html`.
  O `b09_d3` (32,4) e o `b10_d3` (45,1) lêem masculinos e **são servidos**.
  Conserto: `build_index.py` lendo uma lista de ids reprovados, com o
  `nearest_id` ignorando-os.
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
- `render.py` (turntable) não existe — e pode não ser necessário: o GLB com
  auto-rotate no model-viewer foi aprovado no teste do app.
- **Dois vãos `high` masculinos seguem abertos: d1 27,8→33,3 e d3 27,4→32,4.**
  Método medido: âncora única em **IMC alvo − 7** e gerar no **Gemini**. Para o
  `m d1` dá âncora ~23,5 mirando ~30,5; para o `m d3`, âncora ~23 mirando ~30.
  ⚠️ **Reavaliar esse método à luz da §2.4c** — ele é uma receita de SUBIDA, e a
  sessão 17 mediu que subida estoura. Pode ser que o certo seja descer de cima.
- Lado do app Zenith (outro repositório): ver o fim do diário, seção 10.
