# Zenith Avatar Library

Projeto de **produção de assets**, não de software de produto. Entra especificação de arquétipo, sai avatar 3D otimizado + índice consumido pelo app Zenith.

O app Zenith é separado e apenas consome o resultado. Não editar nada do app aqui.

## Documentação

@README.md — estratégia, arquitetura do pipeline, decisões e o porquê delas
@docs/ARCHETYPES.md — grade de arquétipos, nomes, classificação, schema do library.json
@docs/CHARACTER_BIBLE.md — prompts para gerar as imagens de referência (etapa manual)

**Ler os três antes de escrever qualquer código.** As decisões neles foram tomadas com base em testes reais e não devem ser revisitadas sem motivo novo.

## Regras que não se negociam

1. **A Meshy é operada manualmente pelo humano, no site.** Não existe integração com a API da Meshy neste projeto. Não escrever código que chame a API, não pedir chave de API, não criar `.env` para isso.
2. **Normalização é crítica.** Todos os avatares saem com altura idêntica, pés em Y=0, centralizados em X/Z, mesma orientação frontal. Um avatar desalinhado faz o corpo "pular" na tela do usuário ao trocar de arquétipo.
3. **Decimação é obrigatória, e o alvo é 60k (revisto em 27/07).** O GLB cru da Meshy é inviável para celular; a produção mediu de **130k a 317k triângulos** conforme o volume e a definição do corpo. O `process.py` calcula a razão sobre a contagem real (`--tris N`).

   **O `TARGET_TRIS` do `process.py` só passou a valer 60000 em 29/07** — de 27 a 29/07 a constante ficou em 18000 enquanto esta regra já dizia 60k e os 39 masters já estavam em 60000 (foram feitos com `--tris` explícito). O primeiro avatar feminino saiu em 17.988 **com 9/9 validações** por causa disso. *Doutrina: trava que confere o alvo contra ele mesmo não valida o alvo* — a checagem `tris` compara o resultado com `TARGET_TRIS ± 15%`, então alvo errado passa limpo. Hoje o padrão está certo e **não é preciso passar `--tris`**.

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
12. `sheet_qa.py` — mede a folha **ainda em Downloads**, antes de ela entrar no repositório: alinhamento das 3 vistas, espaçamento, silhueta (ombro/cintura/quadril) e extensão do tecido. O `measure.py` só roda depois do `crop.py`, e não se grava folha que pode reprovar. **Passo padrão antes de aprovar qualquer folha**
13. `zenith_paths.py` — **não é executável**: fonte única do layout de `00_input/`, que desde 28/07 é **separado por sexo** (`sheets/{m,f}/`, `references/{m,f}/`). Importado por `intake.py`, `crop.py`, `measure.py`, `process.py` e `shorts_ref.py`. **Não montar esses caminhos à mão em script novo** — `01_raw/`, `02_master/` e `03_dist/glb/` seguem planos de propósito (ver README §3)
14. `shorts_ref.py` — **régua externa**: mede o short na folha de referência (preto sobre cinza) e compara com o 3D. Existe porque o `--report` compara cada avatar com a SÉRIE, e uma série pode estar inteira errada — foi assim que o `b12_d1` passou com o cós 25 cm fora do lugar

O contrato entre o humano e o pipeline é o **nome do arquivo**: o script extrai o ID do arquétipo do nome do GLB em `01_raw/`. Nome errado = avatar errado na biblioteca.

O script não gera imagens e não fala com a Meshy.

## Estado atual

**40 avatares no `library.json`: 39 masculinos + 1 feminino.** A onda masculina está ENCERRADA (27/07); a feminina começou em 29/07.

**39 avatares masculinos produzidos e processados (27/07/2026) — a onda masculina está ENCERRADA.** Todos com 9/9 validações, medidos pelo `metrics.py`, indexados no `library.json` (schema 3) e no `test/avatar_tester.html`. `intake.py`, `crop.py`, `process.py`, `measure.py`, `qa_render.py`, `metrics.py` e `build_index.py` escritos. Só o `render.py` (turntable) não existe — e pode nem ser necessário, porque o GLB com auto-rotate no model-viewer foi aprovado no teste do app.

**O número 32 não é meta.** A meta é COBERTURA do eixo de IMC, não contagem. Sobrou **um** vão `high` — d1 27,8→33,3 (salto 5,5) — e **três tentativas não o fecharam**: ele é o vazio entre dois atratores do gerador, e a recomendação registrada é aceitar e cobrir por shape keys. Os 8 vãos `low` estão todos em IMC 38+, sem população. **A grade feminina saiu de "não produzir ainda" para PRIORIDADE 1** (28/07) e **foi reescrita de 6 para 12 faixas na sessão 7**: 32 arquétipos em `docs/ARCHETYPES.md` §3b e os descritores em `docs/CHARACTER_BIBLE.md` §5.

**O short está mapeado e aplicado nos 39 — e a frente está PARADA.** `shorts.py` + `config/shorts_map.json`, com três réguas (altura, série, traçado). O Rogério revisou no testador e **reprovou 12 no olho**; um (`b12_d1`) foi corrigido na sessão 6 e **11 seguem na fila**.

**⏸️ Decisão do Rogério (28/07): o short sai da frente até as DUAS bibliotecas existirem.** O motivo é custo relativo, e é medido: a onda masculina inteira (39 avatares, ponta a ponta) saiu em ~3 sessões, e o short sozinho já consumiu 3 e ainda tem 11 pendentes. **Não reabrir essa frente sem ele pedir.**

**Fase corrente: a ONDA FEMININA, EM PRODUÇÃO (29/07).** A grade está escrita (32 arquétipos, §3b), o testador tem a **chave ♂/♀**, e a **folha-mãe `f_b05_d2` está aprovada, processada e indexada** — 9/9, 60k, IMC medido 22,9, cintura/quadril 0,658 contra 0,802 do homem. **A biblioteca tem 40 avatares e a esteira está livre: daqui para frente é só produzir folha.** Próximo passo exato no `state.md`, que abre nesse bloco.

**A roupa feminina é FAIXA RETA + short, não top nadador.** Decidido em 29/07 com medida: o racerback cobria 60,7% do dorsal alto, e o app é de musculação. Além do músculo, a faixa é o único corte cuja borda é **anel fechado** — a mesma topologia do cós e da bainha, que é a que o detector sabe achar. Ver `CHARACTER_BIBLE.md` §5. **O feminino terá DUAS peças para segmentar quando a frente do short reabrir.**

**O bloco fixo feminino traz um parágrafo "NATUREZA DA IMAGEM" — não removê-lo.** Ele declara que a folha é prancha de referência anatômica, e existe porque o gargalo de filtro de conteúdo é a GERAÇÃO DA IMAGEM, não a Meshy. Se uma folha for recusada, reforçar esse parágrafo — **não mudar o corte da roupa.**

**Sexo é COLEÇÃO SEPARADA, não filtro de exibição.** Trocar a chave troca também os limiares de gordura (21/29% feminino contra 13/20% masculino) e o `default` do índice. Os GLBs continuam todos em `03_dist/glb/`, sem subpasta por sexo — o id já diz `zen_m_`/`zen_f_` e o `library.json` carrega o campo `sex`.

**Quando ele disser "um por vez", é um por vez.** Cobrado em 28/07: eu varri o mapa inteiro atrás de padrão enquanto ele tinha pedido só o avatar da vez. Vale para o short e para qualquer frente de conserto — sem o print do avatar da vez, não mexer nos outros.

**Dois geradores de imagem em uso, de propósito.** ChatGPT e Gemini têm atratores em lugares diferentes, então o vazio de um é coberto pelo outro — o buraco de IMC 28–38 resistiu a 3 tentativas no ChatGPT e o Gemini entrou nele de primeira. Nenhum é "melhor"; usar o outro quando o alvo cair numa zona morta comprovada. **Folha do Gemini tem um selo (estrelinha) que o `crop.py` não acusa** — o `intake.py` acha e apaga sozinho, sempre; não pedir isso ao humano.

Os avatares dos testes exploratórios (plano gratuito, CC BY 4.0) **não entraram na biblioteca**. Tudo em `02_master/` é do plano Pro.

**Ver `state.md` para o detalhe corrente — ele abre com um bloco "ABRIR AQUI NA SESSÃO NOVA".**

## Stack

- Python 3 para os scripts
- Blender headless para processamento de malha e render

Sem chaves de API, sem secrets, sem dependência de rede. O projeto processa arquivos locais.
