# Zenith Avatar Library

Projeto de **produção de assets**, não de software de produto. Entra especificação de arquétipo, sai avatar 3D otimizado + índice consumido pelo app Zenith.

O app Zenith é separado e apenas consome o resultado. Não editar nada do app aqui.

## Mapa da documentação — LER SOB DEMANDA, não tudo de uma vez

Este arquivo e o `state.md` são os únicos de leitura padrão. Os outros são **de
consulta**: abrir o que a tarefa da vez exige, e abrir INTEIRO quando exigir.

| quando a tarefa for… | ler ANTES de agir | tamanho |
|---|---|---:|
| **montar prompt de folha** (o caso mais comum) | `docs/blocos/prompt_f.md` ou `prompt_m.md` | 4,4k / 2,5k |
| decidir *qual* descritor usar, ou mexer no bloco fixo / na roupa | `docs/CHARACTER_BIBLE.md` | 6,9k |
| mexer em grade, banda, classificação ou schema do `library.json` | `docs/ARCHETYPES.md` | 4,3k |
| discutir arquitetura, formato de entrega, custo, CDN, plano Meshy | `README.md` | 4,1k |
| **qualquer decisão técnica** — antes de propor método, régua ou hipótese | `docs/LICOES.md` | **12,2k** |
| entender COMO uma decisão foi tomada, ou reabrir uma | `docs/historico/diario-2026-07.md` (**grep**, não ler inteiro) | 54k |

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
   - **material** — `scripts/zenith_material.py`: titânio cinza `#6D737B`, metallic 0.50, roughness 0.35. Fonte única, lida pelo `process.py` *e* pelo `restyle.py`.
   - **iluminação** — `scripts/make_env.py` → `03_dist/env/zenith_env.hdr`: rim roxo + key fria + kicker traseiro.

   **O corpo NÃO é mais roxo.** O roxo saturado achatava o relevo muscular, que é o foco do app. A identidade Zenith virou **luz**, não cor de corpo. Consequência que o app precisa saber: **metade do visual mora fora do GLB.** glTF não transporta iluminação de forma portável — o model-viewer ilumina por IBL (`environment-image`). Sem carregar o HDR, o avatar aparece cinza e sem identidade.
5. **A diferença entre arquétipos é largura e volume, nunca altura.**
5c. **A régua 2D (`measure.py`) não atravessa troca de gerador nem de pose.** Ela ordena folhas do MESMO gerador com a MESMA pose, e mais nada. Quem decide onde um avatar caiu é sempre o `metrics.py`, sobre o master 3D. Errar isso já custou três previsões nesta produção.
5b. **Nunca regerar nem descartar um avatar já produzido.** Se ele não corresponde ao que o nome promete, o conserto é **reclassificar** (o rótulo é dado, vive no `library.json`) e **inserir** um novo onde faltar cobertura — nunca substituir. Decisão do Rogério, cobrada em 26/07: "quanto mais avatares tivermos, maior será nossa biblioteca".
6. Todo processamento roda em **Blender headless** via script, nunca à mão na interface.
7. Nenhum script sobrescreve arquivo em `02_master/` sem confirmação — refazer a normalização de um avatar já aprovado exige QA de novo.

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
5. `metrics.py` — mede o **master 3D**: circunferências em cm e IMC real por volume da malha. É a régua de verdade, e a base da classificação
6. `build_index.py` — monta o `library.json` a partir das medidas
7. `render.py` — gera os frames de turntable (ainda não escrito)
8. `zenith_material.py` — **não é executável**: é a fonte única do material (cor/metallic/roughness), importada pelo `process.py` e pelo `restyle.py`
9. `make_env.py` — gera o ambiente de iluminação (`03_dist/env/zenith_env.hdr`). A identidade Zenith mora aqui
10. `restyle.py` — reaplica o material nos 39 `03_dist/glb/` **lendo os masters, sem re-decimar e sem tocar em `02_master/`**. É o jeito de mexer em cor sem refazer QA. `--preview {id}` renderiza 4 vistas com o ambiente em `qa/look/{id}/`
11. `shorts.py` — segmenta e pinta o short, **um avatar por vez**, lendo o vinco da malha. `--fit` propõe e renderiza QA · `--report` confere contra a série · `--check` roda só as travas · `--apply` grava em `03_dist/glb/`
12. `sheet_qa.py` — mede a folha **ainda em Downloads**, antes de ela entrar no repositório: alinhamento das 3 vistas, espaçamento, **largura do tronco na frente** (ombro/cintura/quadril/coxa, com o braço fora da conta), **profundidade no perfil** (barriga/glúteo/coxa) e extensão do tecido. Aceita uma 2ª folha como referência e imprime o delta. O `measure.py` só roda depois do `crop.py`, e não se grava folha que pode reprovar. **Passo padrão antes de aprovar qualquer folha, dos dois geradores.**

    ⚠️ **O critério é a ASSINATURA DE VAZAMENTO, não o gerador — este parágrafo já ensinou o contrário e estava errado.** Até 30/07 ele dizia "em folha do Gemini ele não mede nada", e o `LICOES.md` §1.1 já tinha derrubado isso: **o gerador nunca foi a variável.** A folha do `zen_f_b06_d3` é do **ChatGPT** e vazou (5,05% de variação, `cintura/ombro 1,245`), enquanto a folha do Gemini medida em 30/07 leu **sã** — 0,14% de variação, 0 px nos pés, `cintura/ombro 0,554` — e a leitura dela decidiu uma escolha entre duas folhas. Pela redação antiga eu teria jogado fora uma medida válida.

    **A assinatura a procurar:** figura começando em `y=0` **e** alturas das 3 vistas divergindo 4–5% **e** razões impossíveis (ombro menor que cintura). Ao vê-la: remedir o topo em vários limiares, ou rodar o `crop.py`, que é o detector do caminho do produto. Sem a assinatura, a medida vale — inclusive no Gemini. Ver `docs/LICOES.md` §1.1

    **Reescrito em 29/07 (sessão 8) — a versão anterior media outra coisa.** Ela dava "quadril 52% da altura" na mãe *e* na filha, porque media `cols[-1]−cols[0]` da linha inteira: em A-pose isso é **mão a mão**, não osso a osso. E o `BG_TOL=28` herdado do `measure.py` não acha o corpo nas folhas femininas — não é o limiar, é que **a pele iluminada mede diferença ZERO do fundo** por dezenas de pixels; a silhueta agora vem por preenchimento a partir do contorno. Os três defeitos apareceram de uma vez ao rodar a régua nova na **folha-mãe já aprovada**, que é a calibração que se deve fazer sempre.

    **Largura não é volume — o perfil não é enfeite.** No `f_b04_d2` a largura frontal ficou parada (ombro **+0,17 pp**) enquanto barriga, glúteo e coxa perderam **4–5% de profundidade**: a folha tinha dado o passo, e a régua frontal sozinha teria **reprovado uma folha boa**.

    **O `measure.py` NÃO precisa da mesma correção** — ele usa os *extremos* da linha (buraco no meio não move extremo) e mede barriga na vista de **perfil**, onde não há braço aberto. Não propagar a mudança por analogia.

    **O que ele NÃO mede é TÔNUS** — largura e profundidade não veem relevo de superfície, que foi como duas folhas com abdomens diferentes passaram como "o mesmo corpo" na sessão 7. Para isso, `qa/probe/sondas/probe_tonus_f.py`.
13. `zenith_paths.py` — **não é executável**: fonte única do layout de `00_input/`, que desde 28/07 é **separado por sexo** (`sheets/{m,f}/`, `references/{m,f}/`). Importado por `intake.py`, `crop.py`, `measure.py`, `process.py` e `shorts_ref.py`. **Não montar esses caminhos à mão em script novo** — `01_raw/`, `02_master/` e `03_dist/glb/` seguem planos de propósito (ver README §3)
14. `shorts_ref.py` — **régua externa**: mede o short na folha de referência (preto sobre cinza) e compara com o 3D. Existe porque o `--report` compara cada avatar com a SÉRIE, e uma série pode estar inteira errada — foi assim que o `b12_d1` passou com o cós 25 cm fora do lugar

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

**Ver `state.md` para o detalhe corrente — ele abre com um bloco "ABRIR AQUI NA SESSÃO NOVA".**

## Stack

- Python 3 para os scripts
- Blender headless para processamento de malha e render

Sem chaves de API, sem secrets, sem dependência de rede. O projeto processa arquivos locais.
