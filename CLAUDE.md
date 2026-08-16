# Zenith Avatar Library

Projeto de **produção de assets**, não de software de produto. Entra especificação de arquétipo, sai avatar 3D otimizado + índice consumido pelo app Zenith.

O app Zenith é separado e apenas consome o resultado. Não editar nada do app aqui.

## Mapa da documentação — LER SOB DEMANDA, não tudo de uma vez

Este arquivo e o `state.md` são os únicos de leitura padrão. Os outros são **de
consulta**: abrir o que a tarefa da vez exige, e abrir INTEIRO quando exigir.

| quando a tarefa for… | ler ANTES de agir | tamanho |
|---|---|---:|
| **QUALQUER COISA que toque o app Zenith** — medida, seleção, objetivo, contrato | `docs/INTEGRACAO_ZENITH.md` | **7,5k** |
| **montar prompt de folha** | `docs/blocos/prompt_f.md` ou `prompt_m.md` | 5,2k / 2,4k |
| decidir *qual* descritor usar, ou mexer no bloco fixo / na roupa | `docs/CHARACTER_BIBLE.md` | 6,5k |
| mexer em grade, banda, classificação ou schema do `library.json` | `docs/ARCHETYPES.md` | 4,0k |
| discutir arquitetura, formato de entrega, custo, CDN, plano Meshy | `README.md` | 3,9k |
| **falar em API, shape key, provador virtual, licença Meshy ou comercializar a biblioteca** | `docs/VISAO_PRODUTO.md` | 3,7k |
| **consertar peça (top feminino ou short)** — a fila é dele, não se adivinha | `docs/FILA_PECAS.md` | 3,9k |
| investigar a coxa (RESOLVIDA em 14/08 por offset — ler antes de reabrir) | `docs/PROBLEMA_COXA.md` | 3,7k |
| **qualquer decisão técnica** — antes de propor método, régua ou hipótese | `docs/LICOES.md` | **37,5k** |
| entender COMO uma decisão foi tomada, ou reabrir uma | `docs/historico/diario-2026-08.md` (11,5k) · `diario-2026-07.md` (**grep**) | 61,3k |
| o que foi pedido ao repositório do app (referência, já entregue) | `docs/PROMPT_APP_INTEGRACAO.md` | 2,5k |

> Leitura padrão: `CLAUDE.md` **8,0k** + `state.md` **16,5k** = **24,5k** antes de
> qualquer trabalho. O `LICOES.md` seguiu subindo (14,9k → 18,3k → 19,9k → 21,1k →
> 26,3k → 28,6k → 29,9k → 31,2k → 32,3k → **37,5k**, com a §4.5f, a §4.5g, a
> §7.22b e a §7.25b da sessão 30).
>
> ✅ **O corte do `state.md` FUNCIONOU na sessão 30, e é o primeiro que funciona.**
> Ele vinha de 9,4k → 10,0k → 12,6k → 14,0k → 14,9k → 17,9k; desceram os blocos
> narrativos das sessões 26, 27 e 29 para o diário e ele fechou em **16,5k** —
> cortou 4,7k contra 3,7k de escrita nova. Empatou por pouco: a sessão seguiu
> depois do corte e acrescentou o lote de subida, o achatamento e a coxa. É essa a conta: *o corte tem que
> ser maior que o que se pretende acrescentar, ou não é corte.* **Enxugar não
> vence escrita nova** — as cinco tentativas anteriores provaram isso.
>
> Próximos candidatos a descer, quando a frente deles fechar: o bloco de morph
> da sessão 25 e o do material de 31/07.
>
> **Toda a coluna foi remedida na sessão 18** com um divisor único de 3,6
> chars/token, calibrado contra os números que já estavam certos (`prompt_m.md`
> declarava 2,4k e mediu 2,4k). Para remedir qualquer um:
> `(Get-Content <arquivo> -Raw -Encoding UTF8).Length / 3.6 / 1000`.

> ### ⚠️ Manter a coluna de TAMANHO honesta — o número errado já custou
>
> Ela dizia **3k** para o `LICOES.md` quando ele já estava em **13,6k**, e ficou
> assim por várias sessões. O efeito não é cosmético: número desatualizado faz a
> leitura *parecer barata* e destrói o critério de decidir se vale abrir. Em 30/07
> o Rogério apontou que a documentação comia ~40% do contexto antes de qualquer
> trabalho; medido, eram **35,6k tokens** em quatro arquivos. **Ao crescer um
> destes arquivos, atualizar o número aqui na mesma edição.**

> ### 📄 Por que o bloco de prompt saiu do CHARACTER_BIBLE (30/07)
>
> Montar um prompt exige o bloco fixo literal e **uma** linha de descritor: ~0,8k
> tokens. O `CHARACTER_BIBLE` inteiro custava 11,3k, e o resto dele é a
> **justificativa** de cada decisão — que se lê ao *decidir método*, não ao
> *produzir*.
>
> `docs/blocos/prompt_{f,m}.md` é a **FONTE ÚNICA** do bloco fixo e das 32 linhas
> de descritor. O `CHARACTER_BIBLE` aponta para lá e **não guarda segunda cópia**:
> duas cópias do bloco fixo divergiriam, e divergência do bloco fixo é exatamente
> o que a §1 daquele arquivo proíbe. A extração foi verificada byte a byte.
> **Não recolar o bloco de volta no CHARACTER_BIBLE.**

**As decisões nesses arquivos foram tomadas com base em testes reais e não devem
ser revisitadas sem motivo novo.** Não adivinhar o conteúdo deles a partir deste
resumo — se a tarefa toca o assunto, abrir o arquivo.

> **Por que não são carregados automaticamente (mudou em 29/07).** Os três
> primeiros entravam via `@` e custavam **23,6k tokens em toda sessão**, mais o
> `state.md` de 43,7k que nem cabia numa leitura. O contexto acabava antes do
> trabalho — e no fim de uma sessão longa isso já me fez **pular etapa do
> fluxo**. O acerto não é resumir o conteúdo (as lições são o ativo do projeto):
> é **não carregar o que a tarefa da vez não usa**.

## Regras que não se negociam

1. **A Meshy é operada manualmente pelo humano, no site.** Não existe integração com a API da Meshy neste projeto. Não escrever código que chame a API, não pedir chave de API, não criar `.env` para isso.
2. **Normalização é crítica.** Todos os avatares saem com altura idêntica, pés em Y=0, centralizados em X/Z, mesma orientação frontal. Um avatar desalinhado faz o corpo "pular" na tela do usuário ao trocar de arquétipo.
3. **Decimação é obrigatória, e o alvo é 60k (revisto em 27/07).** O GLB cru da Meshy é inviável para celular; a produção mediu de **130k a 317k triângulos** conforme o volume e a definição do corpo. O `process.py` calcula a razão sobre a contagem real (`--tris N`).

   **O `TARGET_TRIS` do `process.py` só passou a valer 60000 em 29/07** — de 27 a 29/07 a constante ficou em 18000 enquanto esta regra já dizia 60k e os 39 masters já estavam em 60000 (foram feitos com `--tris` explícito). O primeiro avatar feminino saiu em 17.988 **com todas as validações passando** por causa disso. *Doutrina: trava que confere o alvo contra ele mesmo não valida o alvo* — a checagem `tris` compara o resultado com `TARGET_TRIS ± 15%`, então alvo errado passa limpo. Hoje o padrão está certo e **não é preciso passar `--tris`**.

   O alvo era 18k e **subiu para 60k** quando o corpo deixou de ser roxo: com material claro e specular, a faceta da decimação passou a aparecer e o relevo muscular ficava borrado — o roxo saturado vinha escondendo isso. Custo medido: **~183 KB por avatar** com Draco (contra ~64 KB em 18k), bem dentro do orçamento de 1–3 MB. Os masters 18k anteriores estão em `02_master_18k/` (fora do git) até o 60k ser aprovado.
3b. **O short é lido da MALHA, um avatar por vez — nunca da imagem.** Em 60k a bainha e o cós existem como geometria de verdade. Achá-los projetando a imagem frontal (o que o `process.py` fazia, e por isso `SHORTS_ENABLED=False`) **não sobrevive a corpo obeso**: a barriga cai por cima do cós, e aí imagem e malha discordam sobre onde o tecido começa. O `scripts/shorts.py` detecta pelo vinco, **corta a malha na linha exata** e grava dois materiais. Os números de cada avatar vivem em `config/shorts_map.json` — **o mapa é o produto; o detector só propõe.** Ver `state.md`.

4. **A textura da Meshy nunca é usada** — gerar sem textura no site. O visual é aplicado aqui e, desde 27/07, tem **duas metades**:
   - **material** — `scripts/zenith_material.py`: alumínio claro `#B9BCC2`, metallic **0.25**, roughness **0.45** (revisto em 31/07; era titânio `#6D737B` / 0.50 / 0.35). Fonte única, lida pelo `process.py` *e* pelo `restyle.py`.
   - **iluminação** — `scripts/make_env.py` → `03_dist/env/zenith_env.hdr`: rim roxo + key fria + kicker traseiro.

   ⚠️ **Mudar a constante NÃO muda os GLBs** — é preciso `python scripts/restyle.py --all`, e depois conferir com `blender -b -P qa/probe/sondas/probe_material_dist.py`, que lê os 76 arquivos do disco e compara com a fonte única. O restyle valida o próprio export; a sonda é a régua externa. **Ela também cobra a PEÇA** desde 01/08: quem tem entrada no `config/shorts_map.json` precisa sair com `[Zenith_Body, Zenith_Shorts]` — é a régua que teria acusado o apagão dos 39 shorts.

   **O corpo NÃO é mais roxo.** O roxo saturado achatava o relevo muscular, que é o foco do app. A identidade Zenith virou **luz**, não cor de corpo. Consequência que o app precisa saber: **metade do visual mora fora do GLB.** glTF não transporta iluminação de forma portável — o model-viewer ilumina por IBL (`environment-image`). Sem carregar o HDR, o avatar aparece cinza e sem identidade.
5. **A diferença entre arquétipos é largura e volume, nunca altura.**
5c. **A régua 2D (`measure.py`) não atravessa troca de gerador nem de pose.** Ela ordena folhas do MESMO gerador com a MESMA pose, e mais nada. Quem decide onde um avatar caiu é sempre o `metrics.py`, sobre o master 3D. Errar isso já custou três previsões nesta produção.
5b. **Nunca regerar nem descartar um avatar já produzido.** Se ele não corresponde ao que o nome promete, o conserto é **reclassificar** (o rótulo é dado, vive no `library.json`) e **inserir** um novo onde faltar cobertura — nunca substituir. Decisão do Rogério, cobrada em 26/07: "quanto mais avatares tivermos, maior será nossa biblioteca".
6. Todo processamento roda em **Blender headless** via script, nunca à mão na interface.
7. Nenhum script sobrescreve arquivo em `02_master/` sem confirmação — refazer a normalização de um avatar já aprovado exige QA de novo.
8. **Nada sobrescreve arquivo em `03_dist/glb/` — a versão vai no NOME** (`{id}_v{n}.glb`, desde 01/08). Aquele caminho é URL de CDN, e URL de CDN fica em cache: regravar o mesmo nome entrega o conteúdo VELHO para quem já baixou, para sempre — a correção fica invisível justamente para quem já usa o app. Todo escritor passa por `zenith_paths.dist_glb_next()` e a versão anterior só é aposentada **depois** que a nova passa nas travas. **Não criar flag `--bump`**: flag se esquece, e esquecê-la reintroduz o bug em silêncio. Ver `docs/LICOES.md` §4.2g.
9. **`restyle.py` e `shorts.py` gravam o MESMO destino, e o `restyle` apaga o short.** Ele lê o master, que não tem peça. Em 31/07 um `restyle --all` zerou os 39 shorts masculinos sem avisar. Hoje o `restyle` **recusa** avatar com entrada no `config/shorts_map.json` e manda rodar `shorts.py --apply`, que aplica material e short juntos. Ver `docs/LICOES.md` §4.2f.

## Divisão do trabalho

**Humano (fora deste repositório):**
1. Gera a folha de 3 vistas no ChatGPT/Gemini seguindo o Character Bible e **deixa em Downloads**
2. Sobe as 3 imagens (recortadas pelo `crop.py`) no site da Meshy, gera o avatar, baixa o GLB
3. Deixa o GLB em Downloads — o Claude Code renomeia e move para `01_raw/`
4. Aprova ou reprova os avatares na folha de contato do QA

> **Arquivo nenhum entra no repositório pela mão do humano.** Ele larga em Downloads; o Claude Code busca, renomeia, limpa e move — folha (`intake.py`) e GLB. **Pedir para ele salvar, renomear ou apagar selo à mão é regressão de fluxo**, e já aconteceu (27/07): o certo é `python scripts/intake.py {id}`, que pega a imagem mais recente do Downloads sozinho.

**Scripts (o que este repositório faz):**
0. `intake.py` — traz a folha do Downloads, **apaga o selo do Gemini** e grava em `00_input/sheets/{m|f}/{id}_sheet.png`
1. `crop.py` — recorta a folha em frente/perfil/costas por detecção de fundo
2. `process.py` — Blender headless: normaliza, decima, aplica material Zenith, valida
3. `measure.py` — mede a **folha 2D** (barriga/ombros em % da altura): régua rápida para julgar folha antes da Meshy
4. `qa_render.py` — renders de QA (`--raw --torso` para inspecionar o cru antes de processar)
5. `metrics.py` — mede o **master 3D**: circunferências em cm e IMC real por volume da malha. É a régua de verdade, e a base da classificação. **São 11 colunas, e `shoulder` entrou em 01/08** para fechar o contrato com o app em 9 de 9.

    ⚠️ **Medida de fita é LANDMARK, não extremo.** `chest` (0,720) e `shoulder` (0,795) são fração fixa **de propósito** — os dois foram testados como "máximo numa banda" e os dois falharam: o peito foge para a **axila** (+8 cm) e o ombro desce para o **tórax**. Máximo ao longo do eixo vertical sempre acha uma junção, porque é lá que dois volumes se somam. **Não reabrir** — `LICOES.md` §1.8b.

    ⚠️ **Quem procura extremo numa banda tem que denunciar a borda.** Toda medida de extremo grava `at_band_edge: hi|lo` quando o pico encosta no limite da faixa. Isso existe porque a `CALF_BAND` media o **joelho** em 50 dos 76 avatares sem nada acusar: o máximo travava em 0,320 exato, a própria borda. **Exceção: na coxa o `hi` é anatomia, não defeito** (ela é mais larga colada na virilha) — por isso está fora do aviso. `LICOES.md` §1.8
6. `build_index.py` — monta o `library.json` a partir das medidas. **Schema 4 desde 03/08: a seleção é por MEDIDAS**, não mais por IMC dentro de linha de definição, e publica escala por sexo, `z_cap`, faixa plausível, pesos e vetor de objetivo
6b. `select.py` — **a REGRA de seleção, e é a implementação de REFERÊNCIA.** A mesma regra vive em três linguagens (aqui, no `avatar_tester.html` em JS, e no app em Dart); o que diverge entre elas é *qual corpo o usuário vê*. A defesa é `test/selection_cases.json`: 34 casos que as três rodam. **Mexeu na regra → muda AQUI primeiro, `--cases`, e copia índice e casos para o app.** `--demo` responde com medidas na linha de comando
7. ~~`render.py` — frames de turntable~~ ❌ **não é necessário e não vai ser
   escrito (avaliado em 16/08).** Ele existia para uma pergunta em aberto do
   README — *"GLB ou turntable como formato de entrega?"* — e essa pergunta **foi
   respondida pela integração**: o app roda GLB no model-viewer, no device, desde
   04/08, com o morph em cima. Turntable é sequência de imagem: não gira sob
   controle do usuário, não recebe shape key e não reaproveita o HDR. Escrever o
   script hoje seria produzir um formato que nada consome
8. `zenith_material.py` — **não é executável**: é a fonte única do material (cor/metallic/roughness), importada pelo `process.py` e pelo `restyle.py`
9. `make_env.py` — gera o ambiente de iluminação (`03_dist/env/zenith_env.hdr`). A identidade Zenith mora aqui
10. `restyle.py` — reaplica o material nos 39 `03_dist/glb/` **lendo os masters, sem re-decimar e sem tocar em `02_master/`**. É o jeito de mexer em cor sem refazer QA. `--preview {id}` renderiza 4 vistas com o ambiente em `qa/look/{id}/`
11. `shorts.py` — segmenta e pinta as peças, **um avatar por vez**, lendo o vinco da malha: short no masculino, **short + faixa** no feminino desde 01/08. `--fit` propõe e renderiza QA · `--report` confere contra a série · `--check` roda só as travas · `--apply` grava em `03_dist/glb/`

    ✅ **A borda de CIMA da faixa é MODELADA, não procurada (11/08).** Ela nunca foi medível — de 4 a 9 dos 9 setores da frente não têm aro. Hoje o topo frontal vem do `faixa_topo_frente_zh` no mapa, que é **régua externa por avatar** (o `faixa_ref.py` lê a folha), e o traçado é platô na frente inteira + descida nos lados. Erro: **±0,002 em 37 de 37**. A válvula `faixa_topo_reto` morreu. `LICOES.md` §4.5c.

    🔴 **O corte é por ALTURA, e num corpo com avental a barriga desce abaixo
    dele e sai PINTADA (12/08).** Veredito dele com print: *"a tinta não segue o
    cós"*. `w_cos_avental` desce o cós da frente até o fundo da dobra — a face de
    baixo do avental aponta para baixo (nz ≤ −0,70) e é isso que separa pele de
    tecido. Só na frente (nas costas o mesmo sinal é o sulco glúteo, que é short),
    com piso acima da virilha e **rampa de 0,045 por setor**: sem ela a descida
    de 10 cm vira recorte retangular. Ligado por `"cos_avental": true` no mapa.
    `LICOES.md` §4.5e.

    ⚠️ **O cós é ALISADO no fim, e a trava é a QUINA, não o degrau (15/08).** A
    borda de cima saía poligonal — parede de 16 cm no flanco do `zen_f_b11_d1`,
    cunha e tala diagonal nos outros seis que ele apontou. O `DEGRAU` mede
    inclinação e passava limpa em 6 dos 7, porque inclinação alta é legítima; o
    que se vê é a **mudança** dela. `CANTO` = segunda diferença, corte 0,018.
    `w_waist_liso` alisa com teto de 2 bins — e o teto é a **mediana de 3** da
    curva, senão sobra um V no centro da frente vindo da rampa do avental.
    `LICOES.md` §4.5f.

    ⚠️ **A máscara do braço na faixa é o VÃO DE AR, não a profundidade (15/08).**
    `PROF_FRAC` responde *"esta coluna já é tronco?"* e num corpo com busto a
    barra de 60% fica alta demais — o corte caía 4,2 cm DENTRO do tronco e comia
    a quina de baixo da faixa. Acima da fusão existe ar entre braço e tronco em
    toda fatia da banda; `_arm_cut_vao` corta ali e o critério antigo virou plano
    B. E o corte é alisado por **parábola em zh** — a mediana de 5 mata o disparo
    mas preserva degrau, e o que sobrava era borda serrilhada. `LICOES.md` §4.5g.

    🔴 **Veredito de PINTURA não se dá no render do `--fit`** — ele é clay com luz chapada, e tecido sem pintar tem quase o tom do corpo. Uma listra branca passou por 37 avatares e por uma régua verde assim; quem a viu foi o Rogério, no testador. Usar `qa/probe/sondas/render_dist.py`, que renderiza o GLB entregue com o HDR. §4.5c.

    ⚠️ **Régua verde não é avatar certo.** A régua da folha compara a **mediana do quarto frontal**: ela mede o *pico*, não a *forma*. Deu ±0,002 nos 37 com o traçado caindo cedo demais para os lados — o defeito que ele viu. §1.5 num eixo novo.
12. `sheet_qa.py` — mede a folha **ainda em Downloads**, antes de ela entrar no repositório: alinhamento das 3 vistas, espaçamento, **largura do tronco na frente** (ombro/cintura/quadril/coxa, com o braço fora da conta), **profundidade no perfil** (barriga/glúteo/coxa) e extensão do tecido. Aceita uma 2ª folha como referência e imprime o delta. O `measure.py` só roda depois do `crop.py`, e não se grava folha que pode reprovar. **Passo padrão antes de aprovar qualquer folha, dos dois geradores.**

    ⚠️ **O critério é a ASSINATURA DE VAZAMENTO, não o gerador — este parágrafo já ensinou o contrário e estava errado.** Até 30/07 ele dizia "em folha do Gemini ele não mede nada", e o `LICOES.md` §1.1 já tinha derrubado isso: **o gerador nunca foi a variável.** A folha do `zen_f_b06_d3` é do **ChatGPT** e vazou (5,05% de variação, `cintura/ombro 1,245`), enquanto a folha do Gemini medida em 30/07 leu **sã** — 0,14% de variação, 0 px nos pés, `cintura/ombro 0,554` — e a leitura dela decidiu uma escolha entre duas folhas. Pela redação antiga eu teria jogado fora uma medida válida.

    **A assinatura a procurar:** figura começando em `y=0` **e** alturas das 3 vistas divergindo 4–5% **e** razões impossíveis (ombro menor que cintura). Ao vê-la: remedir o topo em vários limiares, ou rodar o `crop.py`, que é o detector do caminho do produto. Sem a assinatura, a medida vale — inclusive no Gemini. Ver `docs/LICOES.md` §1.1

    **Reescrito em 29/07 (sessão 8) — a versão anterior media outra coisa.** Ela dava "quadril 52% da altura" na mãe *e* na filha, porque media `cols[-1]−cols[0]` da linha inteira: em A-pose isso é **mão a mão**, não osso a osso. E o `BG_TOL=28` herdado do `measure.py` não acha o corpo nas folhas femininas — não é o limiar, é que **a pele iluminada mede diferença ZERO do fundo** por dezenas de pixels; a silhueta agora vem por preenchimento a partir do contorno. Os três defeitos apareceram de uma vez ao rodar a régua nova na **folha-mãe já aprovada**, que é a calibração que se deve fazer sempre.

    **Largura não é volume — o perfil não é enfeite.** No `f_b04_d2` a largura frontal ficou parada (ombro **+0,17 pp**) enquanto barriga, glúteo e coxa perderam **4–5% de profundidade**: a folha tinha dado o passo, e a régua frontal sozinha teria **reprovado uma folha boa**.

    **O `measure.py` NÃO precisa da mesma correção** — ele usa os *extremos* da linha (buraco no meio não move extremo) e mede barriga na vista de **perfil**, onde não há braço aberto. Não propagar a mudança por analogia.

    **O que ele NÃO mede é TÔNUS** — largura e profundidade não veem relevo de superfície, que foi como duas folhas com abdomens diferentes passaram como "o mesmo corpo" na sessão 7. Para isso, `qa/probe/sondas/probe_tonus_f.py`.
13. `zenith_paths.py` — **não é executável**: fonte única de **duas** coisas. (a) o layout de `00_input/`, **separado por sexo** desde 28/07 (`sheets/{m,f}/`, `references/{m,f}/`); (b) desde 01/08, o **nome versionado** do entregue em `03_dist/glb/` — `dist_glb_current` (para quem lê), `dist_glb_next` (para quem grava), `dist_glb_retire` (aposenta a anterior). Importado por `intake.py`, `crop.py`, `measure.py`, `process.py`, `restyle.py`, `shorts.py`, `qa_render.py` e `shorts_ref.py`. **Não montar esses caminhos à mão em script novo, e nunca escrever `_v1` literal** — `01_raw/`, `02_master/` e `03_dist/glb/` seguem planos de propósito (ver README §3)
14. `shorts_ref.py` — **régua externa**: mede o short na folha de referência (preto sobre cinza) e compara com o 3D. Existe porque o `--report` compara cada avatar com a SÉRIE, e uma série pode estar inteira errada — foi assim que o `b12_d1` passou com o cós 25 cm fora do lugar
15. `morph.py` — grava os **9 shape keys** de ajuste fino (um por coluna de medida) no avatar entregue. `--fit` calibra e sonda sem gravar · `--apply` grava o dist v(n+1) · `--remap` reescreve só o mapa. Os números de cada avatar vivem em `config/morph_map.json`, e **o mapa é o produto**, como no short.

    ⚠️ **Ele lê o DIST, não o master** (regra 9: quem lê o master e grava o dist apaga o short) — e por isso mede numa **cópia soldada**: o dist chega com a costura corpo/short duplicada, o `metrics.py` separa por topologia e lendo o dist cru o antebraço mede **48,3 cm** onde o índice diz 29,8. A trava é externa e barata: **a régua sobre a base tem que reproduzir o `library_metrics.json`** (hoje 9 de 9). `LICOES.md` §7.10

    ⚠️ **Máscara de morph cobre a BANDA INTEIRA da régua, com platô.** Régua de extremo dentro de banda não se move enquanto o extremo não for ultrapassado, e foge para a borda descoberta: com a máscara começando 1% dentro da banda, a cintura travou em **+2,5 cm** para qualquer amplitude. Mesma família do joelho na banda da panturrilha. `LICOES.md` §7.9

    ⚠️ **O teto de influence é POR MORPH e veio da FOTO.** Padrão ±1,0; a panturrilha vai a ±2,0 porque é cilindro isolado e o render aprovou. **Todo valor acima de 1,0 exige render olhado naquele extremo** — generalizar veredito visual de uma região para outra custou metade da faixa da panturrilha. `LICOES.md` §7.12 e §7.15

    ⚠️ **Morph com um lado SATURADO calibra pelo outro** (`cal_sign`). O pescoço é mínimo de banda travado pelo queixo: crescer satura em +2,2 cm, e calibrar por lá fazia a amplitude fugir para o teto — o lado negativo virava −19 cm com 206 triângulos invertidos. `LICOES.md` §7.16

    ⚠️ **Coluna que a seleção descartou não morfa.** `LICOES.md` §7.18

    ⚠️ **Cada morph passa sozinho e a SOMA quebra.** O estado com todos ligados
    juntos enruga o cós do short, e desde 11/08 ele é **trava**, não relatório: a
    faixa do grupo culpado (quase sempre cintura+quadril) é reduzida até zerar as
    normais invertidas. Tolerar `inv ≤ 2` foi **testado e refutado** — o mesmo
    número é invisível num corpo e visível no outro. `LICOES.md` §7.23

    ⚠️ **Uma coluna fora da régua externa derruba a COLUNA, não o avatar** — o
    mapa publica `dropped_columns`. E se o achatamento reprovar a faixa positiva
    inteira, quem sai é ele, não a cintura. `LICOES.md` §7.24

    ✅ **A COXA foi resolvida em 14/08 por OFFSET, não por medir melhor.** A banda
    lê a peça (até +14,5 cm no feminino) e as **três** tentativas de trocar qual
    malha é medida quebraram avatar que já passava. `calibrar_offset_coxa` mede
    o desvio UMA VEZ contra o `library_metrics.json` na base e soma um número
    fixo — a medição segue pela malha cheia. **75 de 76 têm morph de coxa** (só
    o `zen_m_b06h_d3` não). Teto `COXA_OFFSET_MAX_CM = 22`. `LICOES.md` §7.25b.

**O testador visual é o `testador.cmd` na raiz** — clique duplo, sobe um
`http.server` na 8765 e abre `test/avatar_tester.html`. **Sempre por http;
`file://` não serve** (o testador lê o `library.json` por `fetch` e o
model-viewer carrega GLB e HDR por URL relativa). Ele existe porque até 15/08 o
servidor subia junto com a sessão de trabalho e morria com ela — o ambiente
"parou de abrir" sem nada ter quebrado. **Abrir só quando ele pedir.**

O contrato entre o humano e o pipeline é o **nome do arquivo**: o script extrai o ID do arquétipo do nome do GLB em `01_raw/`. Nome errado = avatar errado na biblioteca.

O script não gera imagens e não fala com a Meshy.

## Estado atual

**O número corrente vive no `state.md`** — avatares, IMC medido, próximo passo e
o que está parado. Não duplicar aqui: a lista já ficou desatualizada duas vezes
por estar em dois lugares.

O que é estrutural e não muda de sessão para sessão:

**A meta é COBERTURA do eixo de IMC, não contagem.** O número 32 nunca foi meta.
Para saber quais vãos existem hoje, **rodar `build_index.py`, que imprime** —
contar à mão já deu errado.

**⏸️ A frente do SHORT está PARADA por decisão do Rogério (28/07)**, até as duas
bibliotecas existirem. O motivo é custo relativo, e é medido. **Não reabrir sem
ele pedir.** Detalhe em `state.md`.

**Sexo é COLEÇÃO SEPARADA, não filtro de exibição.** Trocar a chave troca também
os limiares de gordura (21/29% feminino contra 13/20% masculino) e o `default`
do índice. Os GLBs continuam todos em `03_dist/glb/`, sem subpasta por sexo — o
id já diz `zen_m_`/`zen_f_` e o `library.json` carrega o campo `sex`.

**A roupa feminina é FAIXA RETA + short, não top nadador.** Decidido com medida:
o racerback cobria 60,7% do dorsal alto, e o app é de musculação. Além do
músculo, a faixa é o único corte cuja borda é **anel fechado** — a topologia que
o detector sabe achar. Ver `CHARACTER_BIBLE.md` §5.

**O bloco fixo feminino traz um parágrafo "NATUREZA DA IMAGEM" — não removê-lo.**
Ele declara que a folha é prancha de referência anatômica, e existe porque o
gargalo de filtro de conteúdo é a GERAÇÃO DA IMAGEM, não a Meshy. Se uma folha
for recusada, reforçar esse parágrafo — **não mudar o corte da roupa.**

> **O placar do `process.py` é 8/8 hoje e era 9/9 no masculino, e nenhuma trava
> sumiu.** A 9ª é `shorts_frac`, que só existe com `SHORTS_ENABLED` — desligado
> desde que o short passou a ser lido da malha (regra 3b). Não procurar
> validação perdida.

**Quando ele disser "um por vez", é um por vez.** Sem o print do avatar da vez,
não mexer nos outros — nem para procurar padrão. Mais em `docs/LICOES.md` §6.

**Dois geradores de imagem em uso, de propósito.** ChatGPT e Gemini têm atratores em lugares diferentes, então o vazio de um é coberto pelo outro — o buraco de IMC 28–38 resistiu a 3 tentativas no ChatGPT e o Gemini entrou nele de primeira. Nenhum é "melhor"; usar o outro quando o alvo cair numa zona morta comprovada. **Folha do Gemini tem um selo (estrelinha) que o `crop.py` não acusa** — o `intake.py` acha e apaga sozinho, sempre; não pedir isso ao humano.

Os avatares dos testes exploratórios (plano gratuito, CC BY 4.0) **não entraram na biblioteca**. Tudo em `02_master/` é do plano Pro.

**A INTEGRAÇÃO COM O APP ESTÁ NO AR desde 04/08.** O avatar 3D aparece na home,
escolhido pelas 9 circunferências. Os 76 GLBs e o HDR vivem no Supabase Storage
(bucket público `avatars`), e o `library.json` vai embutido no app. Contrato
completo em `docs/INTEGRACAO_ZENITH.md` §11 — **ler antes de tocar em seleção,
índice ou GLB entregue.**

✅ **O Storage foi atualizado em 16/08** — 76 GLBs, 0 falhas. Todo lote de peça
ou de morph grava versão nova aqui e aposenta a anterior, então **depois de
qualquer `--apply` o Storage fica atrás até a próxima subida.** A receita
(índice primeiro, upload depois) está no `state.md`.

**A pesquisa de MORPH está aberta e mudou a conta de avatares.** Quatro
experimentos em `qa/probe/sondas/morph_lab*.py`: a axila não quebrou em nenhum, e
com morph a biblioteca quase não precisa crescer (falta **1** avatar em vez de
~90). Faixas medidas e as armadilhas em `docs/LICOES.md` §7. **Não é decisão
tomada** — é pesquisa, e ainda falta enforcer, calibração e device.

**Ver `state.md` para o detalhe corrente — ele abre com um bloco "ABRIR AQUI NA SESSÃO NOVA".**

## Stack

- Python 3 para os scripts
- Blender headless para processamento de malha e render

Sem chaves de API, sem secrets, sem dependência de rede. O projeto processa arquivos locais.
