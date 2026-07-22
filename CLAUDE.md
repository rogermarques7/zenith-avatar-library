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
3. **Decimação é obrigatória.** O GLB cru da Meshy tem ~211k faces e é inviável para celular. Alvo: ~18k triângulos.
4. **A cor roxa Zenith é aplicada no pipeline**, nunca vem da textura da Meshy. Gerar sem textura no site.
5. **A diferença entre arquétipos é largura e volume, nunca altura.**
6. Todo processamento roda em **Blender headless** via script, nunca à mão na interface.
7. Nenhum script sobrescreve arquivo em `02_master/` sem confirmação — refazer a normalização de um avatar já aprovado exige QA de novo.

## Divisão do trabalho

**Humano (fora deste repositório):**
1. Gera a folha de 3 vistas no ChatGPT seguindo o Character Bible
2. Recorta em frente / perfil / costas
3. Sobe as 3 imagens no site da Meshy, gera o avatar, baixa o GLB
4. Salva o GLB em `01_raw/` com o nome do arquétipo
5. Aprova ou reprova os avatares na folha de contato do QA

**Scripts (o que este repositório faz):**
1. `process.py` — Blender headless: normaliza, decima, aplica material Zenith, valida
2. `render.py` — gera os frames de turntable
3. `build_index.py` — monta o `library.json`

O contrato entre o humano e o pipeline é o **nome do arquivo**: o script extrai o ID do arquétipo do nome do GLB em `01_raw/`. Nome errado = avatar errado na biblioteca.

O script não gera imagens e não fala com a Meshy.

## Estado atual

Nenhum código escrito. Nenhum avatar em produção.

Os avatares gerados durante os testes exploratórios estão sob licença CC BY 4.0 (plano gratuito) e **não podem entrar na biblioteca**. A produção começa do zero sob plano Pro.

Escopo da Onda 1: **32 avatares masculinos** (12 faixas de IMC × 3 níveis de definição, menos 4 implausíveis). A grade feminina está marcada como PENDENTE no Character Bible e não deve ser produzida ainda.

**Próximo passo:** piloto de 4 avatares masculinos nos extremos (`m_b02_d3`, `m_b05_d2`, `m_b08_d1`, `m_b11_d1`) para validar o pipeline ponta a ponta antes de qualquer produção em lote.

## Stack

- Python 3 para os scripts
- Blender headless para processamento de malha e render

Sem chaves de API, sem secrets, sem dependência de rede. O projeto processa arquivos locais.
