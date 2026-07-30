# state.md — o presente

Última atualização: **30/07/2026, fim da sessão 15**

> ## 🔴 ABRIR AQUI NA SESSÃO NOVA
>
> **O foco é FECHAR A BIBLIOTECA FEMININA INTEIRA. Decisão do Rogério, 29/07.**
> Masculino não se toca até isso acabar — os dois vãos `high` dele já têm
> conserto conhecido e ficam anotados no fim deste arquivo.
>
> **64 avatares — 39 masculinos e 25 femininos.** A sessão 15 fechou **4**:
> `b07_d3`, `b06h_d3`, `b08h_d3` e `b06_d1`. Todos 8/8.
>
> | linha | n | IMC medido |
> |---|---:|---|
> | `f d1` | 10 | 16,5 · 19,0 · 23,3 · 24,1 · 31,9 · **32,4** · 34,1 · 42,6 · 52,5 · 114,2 |
> | `f d2` | 7 | 18,3 · 22,2 · 22,9 · 27,3 · 30,1 · 34,4 · 53,9 |
> | **`f d3`** | **8** | **21,0 · 22,1 · 22,3 · 27,7 · 28,4 · 29,0 · 30,1 · 32,4** |
>
> ### 📋 A SESSÃO 15 EM UMA TABELA — 4 avatares, 4 previsões, 4 erros
>
> | id | descritor | âncora | previsto | **medido** | erro |
> |---|---|---:|---|---:|---:|
> | `b07_d3` | atleta de **wellness** de competição | ~28,4 | — | **27,7** | — |
> | `b06h_d3` | atleta de **bikini fitness** | 22,1 | 25 | **22,3** | −2,7 |
> | `b08h_d3` | atleta de **CrossFit** de elite | 22,3 | 25–28 | **29,0** | +1,0 |
> | `b06_d1` | peso normal alto, sem tônus | 24,1 | 27–31 | **32,4** | +1,4 |
>
> **Nenhuma previsão caiu dentro** (§2.6). Narrativa completa da sessão 15 no
> `docs/historico/diario-2026-07.md`; doutrinas em §2.2b, §2.2c e §3.3b.
>
> ### 🔴 AS DUAS REGRAS QUE SAÍRAM DAQUI — usar já na próxima folha
>
> **1. Categoria do mundo real, não adjetivo.** Descritor inerte não se conserta
> com mais intensificador: troca-se o substantivo por uma **categoria que existe e
> é julgada** ("wellness", "bikini fitness", "CrossFit de elite"). Escada medida,
> feminina/ChatGPT: bikini fitness **22,3** · wellness **27,7** · fisiculturista
> **28,4** · CrossFit **29,0** · fisiculturista pesada **30,1**.
>
> **2. UM lever por folha.** Categoria governa **tamanho**, direção de volume
> governa **forma**. Empilhados com negações dão **zero**: no `b06h_d3` três freios
> juntos deram **+0,2**; tirando as negações, o mesmo lever deu **+6,7**.
> ✅ Negação legítima nomeia o **atrator a evitar** (*"NÃO é obesa"*), nunca um
> traço que o descritor pede.
>
> ### ⚠️ DOIS VÃOS RESISTIRAM — e o remédio dos dois é a ÂNCORA
>
> **`f d3` 22,3 → 27,7 (5,4)** — o vão é **mais estreito que o passo mínimo do
> substantivo (~6,3)**, então a categoria pula por cima por construção, e não
> existe nome de divisão entre "bikini fitness" e "CrossFit". **Manter "CrossFit"
> e baixar a âncora para ~19–20**, mirando ~26.
>
> **`f d1` 24,1 → 31,9 (7,8)** — duas tentativas, as duas acima. A 2ª tinha
> descritor deliberadamente contido e ainda pousou em **32,4**. **Amansar o
> descritor não tira o corpo do poço** — baixar a âncora.
>
> ### ⚠️ `b08h_d3` nasceu `b06i_d3` e foi RECLASSIFICADO
>
> Pousou em 29,0, entre o `b08` (28,4) e o `b09h` (30,1) — o id mentia sobre a
> ordem. Renomeado em todos os planos e no `library_metrics.json`.
> ⚠️ Existe um `zen_m_b06i_d3` **masculino** intocado — conferir o prefixo de sexo
> antes de qualquer renomeação em massa.
>
> ### ⚠️ Rótulos fora de ordem na `f d1`, não consertados
>
> `b09_d1` mede **34,1** e `b08_d1` mede **42,6** — invertidos, de antes desta
> sessão. E o `b06_d1` mede **32,4** contra os 31,9 do `b07_d1`. Não quebra o app
> (o `nearest_id` usa IMC medido, não o nome), mas o **nome mente sobre a ordem**.
> Decidir se vale reclassificar ou se o rótulo de banda é só histórico.
>
> ⚠️ **Busto no limite alto do "PEQUENO A MÉDIO" — 3 folhas seguidas** (`b09h_d3`,
> `b07_d3`, `b06h_d3`). Não é acaso: **reforçar essa linha no slot do descritor**,
> como já foi feito nas últimas duas (*"não aumentá-lo, ele é pequeno"*).
>
> ### ⚠️ O `b09_d3` masculino AINDA é servido acima de IMC 31,2
>
> A inserção resolve a faixa de ~29 a ~31,2, onde o `b09h_d3` passa a ser o mais
> próximo. **Acima de 31,25 (o ponto médio entre 30,1 e 32,4) o `nearest_id` volta
> a devolver o `b09_d3`**, que lê masculino. O conserto de verdade continua sendo
> o campo `approved` (ver a pendência), não mais um avatar.
>
> ### ⚠️ `zen_f_b09_d3` — o asset FICA, mas ele lê MASCULINO
>
> IMC 32,4, 8/8, relevo ótimo. Mas peitoral em vez de busto, sem afunilamento de
> cintura, quadril estreito, mandíbula masculina. Folha do **Gemini**, e o desvio
> **estava visível na folha antes da Meshy** — o Claude Code viu, anotou
> ("trapézio e pescoço lêem masculinos") e seguiu mesmo assim, passando a vigiar
> resolução em vez de identidade. Erro de julgamento registrado.
>
> **Decisão do Rogério (30/07): mantém no repositório, gera um `b09` novo.**
>
> 🔴 **E ele foi explícito sobre o método de QA:** *"você é o especialista em corpo
> humano, não tem como eu decidir algo no olho assim, a menos que seja uma
> inconsistência grande ou defeito na pintura do short."* **Não pedir a ele
> veredito de anatomia** — só de inconsistência grosseira e de short. Anatomia é
> medida e julgada aqui.
>
> 🔴 **PENDÊNCIA DE PRODUTO ABERTA:** hoje esse corpo **é entregue** a qualquer
> mulher `d3` de IMC perto de 32. O campo `approved` do `library.json` é **fixo em
> `True`** no `build_index.py:164` e **nada o lê** — nem o `avatar_tester.html`.
> Não existe mecanismo para manter o asset sem servi-lo. Não urgente (a biblioteca
> feminina não está no app), e o conserto é `build_index.py` lendo uma lista de ids
> reprovados, com o `nearest_id` ignorando-os.
>
> ### 🔴 O QUE NÃO SE FAZ MAIS: prever IMC pela folha
>
> **Cinco preditores construídos, cinco mortos** (`LICOES.md` §2.6c e §2.6d). A
> folha 2D serve para (a) **reprovar geometria** — alinhamento, altura, figura
> cortada, o uso que nunca falhou — e (b) **alarme ordinal**. Quem diz o número é
> o `metrics.py`. **Registrar a previsão continua valendo**, porque é ela que
> revela o erro, mas é palpite declarado e não deve gastar tempo de cálculo.
>
> ### ✅ O QUE FUNCIONA PARA MIRAR — medido na sessão 13
>
> **O substantivo de categoria é o único lever, e ele REPLICOU entre os sexos.**
> "Fisiculturista de competição" moveu o corpo feminino **+6,3** (22,1 → 28,4),
> contra o **+6,4** medido no masculino (§2.2). Foi a única previsão da sessão que
> caiu dentro da faixa declarada.
>
> **Passo por banda seguinte é pequeno na `d3`:** 21,0 → 22,1 foi **+1,1**. A base
> da `m d3` também é comprimida (19,9 · 20,8 · 21,1), então **não é atrator
> travando o feminino** — as bandas `b02`–`b06` da `d3` têm pouca massa entre si
> por natureza. Para andar, trocar o substantivo.
>
> **Corpo feminino vem ~2,8 mais leve que o masculino no mesmo descritor `d3`.**
> O `f_b05_d3` (21,0) caiu no nível do `m_b04_d3` (21,1), não do `m_b05_d3` (23,8).
> Escada da `m d3` para planejar: 19,9 · 20,8 · 21,1 · 23,8 · 27,0 · 27,4 · 32,4 ·
> 34,7 · 35,7 · 53,8.
>
> ### 🔴 FALTAM 13 SLOTS FEMININOS — a `f d2` é a linha mais atrasada
>
> **64 avatares; 25 femininos ocupando 19 dos 32 slots da grade.** Os outros 6 são
> inserções em slot já ocupado (`b04h_d1`, `b09h_d2`, `b09i_d2`, `b06h_d3`,
> `b08h_d3`, `b09h_d3`).
>
> | linha | grade | slots | insrç. | faltam | quais |
> |---|---:|---:|---:|---:|---|
> | `f d1` | 12 (b01–b12) | 9 | 1 | **3** | b02 b05 b10 |
> | **`f d2`** | 11 (b01–b11) | 5 | 2 | **6** | b01 b03 b07 b08 b10 b11 |
> | `f d3` | 9 (**b02–b10**) | 5 | 3 | **4** | b02 b03 b04 b10 |
>
> ⚠️ **A grade da `d3` começa em `b02` e termina em `b10`** — não existe `b01_d3`.
> Um script de contagem que assume `b01..b09` inventa um slot que não existe e
> esconde o `b10`; aconteceu nesta sessão e foi corrigido na hora.
>
> **Contar SEMPRE derivando do `library.json`**, nunca à mão (§5.4) — e conferir a
> faixa da grade contra o `docs/blocos/prompt_f.md`, que é a fonte dos descritores.
>
> **⚠️ NÃO confundir com os vãos `high` de IMC**, que medem continuidade da escada
> dentro das linhas que existem; estes medem completude da grade. Já troquei uma
> coisa pela outra e respondi errado.
>
> ### 🔧 Quatro pegadinhas de régua que se pagam caro — todas em `LICOES.md` §1.1
>
> - **Assinatura de vazamento do `sheet_qa`** (`y=0` + alturas divergindo 4–5% +
>   ombro menor que cintura): **não é do gerador, é do método.** Ao vê-la, remedir
>   em vários limiares ou rodar o `crop.py`. Sem a assinatura, a medida vale —
>   inclusive no Gemini.
> - **A sonda de tônus AFIRMA, mas não NEGA.** Amostra só a tira central
>   (`meia_frac` 0,22): silêncio dela não reprova folha `d3`.
> - **`thigh` e circunferências de tronco não valem por avatar** — `at_frac` fixo
>   contra virilha que se move. Usar `volume_l`.
> - **Nenhuma trava valida orientação frontal** (§4.2c) — isso é olho, no preview.
>   O slot do Multi-View da Meshy não muda a malha; medido em 58 masters.

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
cd qa/probe/sondas && python probe_tonus_f.py "<ancora>" "<folha>"
python scripts/intake.py  zen_f_bXX_d3 --from "<caminho da folha>"
python scripts/crop.py    zen_f_bXX_d3
   (Meshy: Multi-View, Meshy 6 Padrao, densidade alta, SEM textura,
    divisao automatica DESLIGADA. O slot da lateral tanto faz - medido.)
python scripts/process.py zen_f_bXX_d3      # 60k, 8/8
python scripts/metrics.py zen_f_bXX_d3
python scripts/build_index.py               # imprime os vaos
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

## ⏸️ Frente do SHORT — PARADA por decisão do Rogério (28/07)

> *"essas mudanças simples no short estão levando muito mais tempo que criar
> bibliotecas inteiras de avatar. Quando completarmos as duas bibliotecas aí
> foco somente na pintura dos shorts."*

**Não reabrir sem ele pedir.** Estado congelado: mapeado e aplicado nos 39
masculinos; ele reprovou **12 no olho**, `b12_d1` foi corrigido, **11 na fila**.
Ao retomar, começar por `b11_d1` (maior erro de bainha, −0,048) — a receita e a
pista dos 4 com bainha nunca medida estão no diário, sessão 6.

O feminino ainda **não tem short pintado**, e quando a frente reabrir precisará
de **duas** peças (faixa + short), as duas com borda em anel fechado.

**Defeito de short É um dos dois vereditos que o Rogério dá no olho** — o outro é
inconsistência grosseira. Quando a frente reabrir, é dele que se pergunta.

---

## 👁️ QA visual — o que ele já aprovou

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

- ✅ **`LICOES.md` enxugado na sessão 14: 14k → 10,6k tokens (−24%).** Nenhuma
  doutrina e nenhum número saíram; a narrativa foi para o diário. O que se fundiu:
  as três versões encaixadas da lição do `sheet_qa` (a doutrina errada "é do
  Gemini", a pré-condição e a correção) viraram **uma** seção com a doutrina certa;
  §2.6, 2.6b, 2.6c e 2.6d viraram **uma** §2.6 com a tabela das quatro mortes;
  §2.4 e §2.4b viraram uma tabela de passo por gerador e direção; os atratores
  espalhados em cinco citações viraram **uma tabela** na §2.5. Entraram lições
  novas que faltavam: §5.1 sobre o `approved` morto e §6.7 sobre quem dá veredito.
  **Não bateu os 8–9k estimados** — a estimativa era minha e era otimista, porque
  cortar mais começaria a tirar números que sustentam doutrina. Duas linhas novas
  na tabela da §1.1 (orientação frontal e resolução vs. identidade) também
  cresceram o arquivo de propósito.
- 🔴 **A SESSÃO 15 ESTÁ SEM COMMIT.** 7 arquivos modificados: `library.json`,
  `metrics/library_metrics.json`, `logs/process.log`, `state.md`, `CLAUDE.md`,
  `docs/LICOES.md`, `docs/blocos/prompt_f.md`. **Ele pediu para commitar só quando
  mandar** — perguntar no começo da sessão 16.

  ⚠️ **Os 4 avatares novos NÃO entram em commit nenhum.** O `.gitignore` cobre
  `00_input/`, `02_master/` e `03_dist/`, então **folha, master e GLB existem só
  no disco local do Rogério** — o git guarda apenas o índice, as medidas e a
  documentação. Consequência real: **não há backup dos assets**, e uma
  reclassificação como a do `b06i_d3`→`b08h_d3` é irreversível pelo git. Se algum
  dia isso importar, a conversa é sobre LFS ou storage externo, não sobre commit.
- ⚠️ **`intake.py --check` deixa armadilha: a folha fica gravada.** Rodei
  `crop.py --check` numa folha que depois **reprovei**, mas o `intake` já a tinha
  escrito em `00_input/sheets/f/`. Na folha seguinte com o mesmo id o `intake`
  barrou ("folha aprovada não se substitui") e o `crop` rodou na folha **velha**,
  gerando referências erradas — só apareceu porque a variação de altura veio
  1,52% em vez de 0,22%. Conserto: `--force`. **Para testar folha duvidosa, usar
  um id descartável**, nunca o id real.
- ✅ **COMMITADO em 30/07 pela manhã**, em dois commits: `c0819c8` com os 6
  avatares das sessões 12 e 13 mais o `SEAL_ISOLATION`, e `0a462ac` com a
  documentação e o diário. **Sem push** — não foi pedido.
- **O testador nunca precisou de nada.** Ele lê o `library.json` por `fetch` desde
  27/07 e não tem lista fixa. Conferido no ar: **39 masculinos e 21 femininos**,
  escada ordenada por IMC medido, zero erro de console.
  `preview_start` na config `static` → http://localhost:8765/test/avatar_tester.html
- ⚠️ **O classificador de permissão caiu na madrugada de 30/07** e bloqueou
  `python`, `git commit` e `preview_start` por horas (leitura e edição de arquivo
  seguiram; comandos read-only allowlistados como `git status` também). **Não era
  configuração** — a mensagem nomeava o modelo, e não existe `.claude/settings.json`
  neste projeto. Se acontecer de novo: não contornar reimplementando régua à mão
  (§1.3), e deixar o handoff no `state.md` com o caminho exato do arquivo parado.
- ✅ **Documentação reorganizada em 30/07, a pedido do Rogério** — ele apontou que
  ela comia ~40% do contexto antes de qualquer trabalho. Medido: 35,6k tokens em
  4 arquivos. Sessão de produção agora custa **24,7k (−31%)**, sem perder nada:
  bloco fixo e 32 descritores extraídos para `docs/blocos/prompt_{f,m}.md` (fonte
  única, verificada byte a byte), `CHARACTER_BIBLE` 11,3k → 6,9k, `state.md`
  6,4k → 3,4k, e a coluna de tamanho do `CLAUDE.md` corrigida — ela dizia 3k para
  um arquivo de 13,6k.
- ✅ **DÍVIDA DE NARRATIVA PAGA: sessões 12 e 13 escritas no diário** na sessão 14,
  reconstruídas do `logs/process.log`, do `git log` e do `state.md` da sessão 13.
  O diário passou de 49k para **54k tokens** — número já corrigido no `CLAUDE.md`,
  junto com o do `LICOES.md`.
- **`approved` é campo morto no `library.json`** — ver o bloco do `b09_d3`.
- **Conferir `git status` antes de mexer** — ver o item do commit pendente acima.
- ✅ **`state.md` enxugado no fim da sessão 15: 8,1k → 5,5k tokens (−32%).** Saíram
  os blocos narrativos das sessões 13 e 14 (`b09h_d3`, o "o que a sessão 13
  mediu", as duas contagens à mão erradas) — a narrativa foi para o diário, que
  ganhou a seção da sessão 15 inteira. As quatro pegadinhas de régua viraram uma
  lista de 4 linhas apontando para §1.1. **Não bateu os ~4k estimados**: o bloco da
  sessão 15 é o contexto corrente e precisa ficar por inteiro. Quando a sessão 16
  fechar, é ele que desce para o diário.
- 🧹 **`state.md.cauda.tmp` está untracked na raiz**, sobra do enxugamento do
  `state.md` na sessão 13. Conferir o conteúdo e apagar; não entrou em nenhum
  commit, então não há histórico a preservar.
- `render.py` (turntable) não existe — e pode não ser necessário: o GLB com
  auto-rotate no model-viewer foi aprovado no teste do app.
- **Dois vãos `high` masculinos seguem abertos: d1 27,8→33,3 e d3 27,4→32,4.**
  Método medido: âncora única em **IMC alvo − 7** e gerar no **Gemini**. Para o
  `m d1` dá âncora ~23,5 mirando ~30,5; para o `m d3`, âncora ~23 mirando ~30.
  **Anotado a pedido do Rogério para depois — não executar antes de a biblioteca
  feminina fechar.**
- Lado do app Zenith (outro repositório): ver o fim do diário, seção 10.
