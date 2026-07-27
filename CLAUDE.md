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
3. **Decimação é obrigatória.** O GLB cru da Meshy é inviável para celular. A produção mediu de **130k a 232k triângulos** conforme o volume e a definição do corpo (não os ~211k fixos que se supunha). Alvo: ~18k triângulos — o `process.py` calcula a razão de decimação sobre a contagem real. Razões já rodadas vão de 0,15 a **0,077** (`b07_d3`, o mais pesado) sem perda visível de definição.
4. **A cor roxa Zenith é aplicada no pipeline**, nunca vem da textura da Meshy. Gerar sem textura no site.
5. **A diferença entre arquétipos é largura e volume, nunca altura.**
5c. **A régua 2D (`measure.py`) não atravessa troca de gerador nem de pose.** Ela ordena folhas do MESMO gerador com a MESMA pose, e mais nada. Quem decide onde um avatar caiu é sempre o `metrics.py`, sobre o master 3D. Errar isso já custou três previsões nesta produção.
5b. **Nunca regerar nem descartar um avatar já produzido.** Se ele não corresponde ao que o nome promete, o conserto é **reclassificar** (o rótulo é dado, vive no `library.json`) e **inserir** um novo onde faltar cobertura — nunca substituir. Decisão do Rogério, cobrada em 26/07: "quanto mais avatares tivermos, maior será nossa biblioteca".
6. Todo processamento roda em **Blender headless** via script, nunca à mão na interface.
7. Nenhum script sobrescreve arquivo em `02_master/` sem confirmação — refazer a normalização de um avatar já aprovado exige QA de novo.

## Divisão do trabalho

**Humano (fora deste repositório):**
1. Gera a folha de 3 vistas no ChatGPT seguindo o Character Bible
2. Sobe as 3 imagens (recortadas pelo `crop.py`) no site da Meshy, gera o avatar, baixa o GLB
3. Deixa o GLB em Downloads — o Claude Code renomeia e move para `01_raw/`
4. Aprova ou reprova os avatares na folha de contato do QA

**Scripts (o que este repositório faz):**
1. `crop.py` — recorta a folha em frente/perfil/costas por detecção de fundo
2. `process.py` — Blender headless: normaliza, decima, aplica material Zenith, valida
3. `measure.py` — mede a **folha 2D** (barriga/ombros em % da altura): régua rápida para julgar folha antes da Meshy
4. `qa_render.py` — renders de QA (`--raw --torso` para inspecionar o cru antes de processar)
5. `metrics.py` — mede o **master 3D**: circunferências em cm e IMC real por volume da malha. É a régua de verdade, e a base da classificação
6. `build_index.py` — monta o `library.json` a partir das medidas
7. `render.py` — gera os frames de turntable (ainda não escrito)

O contrato entre o humano e o pipeline é o **nome do arquivo**: o script extrai o ID do arquétipo do nome do GLB em `01_raw/`. Nome errado = avatar errado na biblioteca.

O script não gera imagens e não fala com a Meshy.

## Estado atual

**36 avatares masculinos produzidos e processados (27/07/2026).** Todos com 9/9 validações, medidos pelo `metrics.py`, indexados no `library.json` (schema 3) e no `test/avatar_tester.html`. `crop.py`, `process.py`, `measure.py`, `qa_render.py`, `metrics.py` e `build_index.py` escritos. Só o `render.py` (turntable) não existe — e pode nem ser necessário, porque o GLB com auto-rotate no model-viewer foi aprovado no teste do app.

**O número 32 não é meta.** A meta é COBERTURA do eixo de IMC, não contagem: produzir enquanto houver buraco `high` em `coverage_gaps`. Restam **dois**, ambos na zona de sobrepeso: d3 (27,4→34,6) e d1 (27,8→34,0). A grade feminina segue PENDENTE e não deve ser produzida ainda.

**Dois geradores de imagem em uso, de propósito.** ChatGPT e Gemini têm atratores em lugares diferentes, então o vazio de um é coberto pelo outro — o buraco de IMC 28–38 resistiu a 3 tentativas no ChatGPT e o Gemini entrou nele de primeira. Nenhum é "melhor"; usar o outro quando o alvo cair numa zona morta comprovada. **Folha do Gemini exige apagar o selo (estrelinha) antes do crop** — o `crop.py` não acusa.

Os avatares dos testes exploratórios (plano gratuito, CC BY 4.0) **não entraram na biblioteca**. Tudo em `02_master/` é do plano Pro.

**Ver `state.md` para o detalhe corrente — ele abre com um bloco "ABRIR AQUI NA SESSÃO NOVA".**

## Stack

- Python 3 para os scripts
- Blender headless para processamento de malha e render

Sem chaves de API, sem secrets, sem dependência de rede. O projeto processa arquivos locais.
