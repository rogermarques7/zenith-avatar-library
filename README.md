# Zenith Avatar Library

Projeto de **produção de assets** — separado do app Zenith.
Entra: especificação de arquétipos. Sai: biblioteca de avatares + índice consumido pelo app.

**Status:** v0 — definição concluída, produção não iniciada.

---

## 1. O problema que este projeto resolve

O app Zenith precisa mostrar o corpo do usuário em duas telas:

- **Home** — avatar do estado atual, girando sobre o próprio eixo
- **Objetivo Zenith** — dois avatares lado a lado (atual + meta)

As medidas do usuário são coletadas **a cada 30 dias**. Não existe necessidade de geração em tempo real.

### Decisão central: biblioteca, não geração por usuário

Foram avaliadas duas abordagens:

| | Gerar por usuário | **Biblioteca (escolhida)** |
|---|---|---|
| Custo | ~US$1,20/usuário/mês, recorrente | ~US$40 uma vez |
| Latência | ~1 min por avatar | zero |
| Qualidade | loteria, sem QA possível | 100% revisada |
| Consistência visual | quebra a cada mês | garantida |
| Risco de filtro de conteúdo | falha em runtime | inexistente |

O app **classifica** o usuário em um arquétipo e **seleciona** o asset correspondente.

---

## 2. Fatos técnicos comprovados (testes de 21/07/2026)

Estes achados são a base de todas as decisões abaixo. Não repetir os testes.

1. **Cada geração da Meshy tem topologia própria.** Vertex counts medidos: 143.758 / 83.634 / 105.674 / 109.681. Nunca iguais.
   → **Modelos gerados separadamente NÃO morfam entre si.** Morph exige mesmo número de vértices, mesma ordem e mesma correspondência anatômica. Semelhança visual não é correspondência topológica.
   → Por isso a biblioteca **seleciona**, não interpola. Selecionar contorna 100% do problema.

2. **Receita campeã de geração** (barata, sem plano pago):
   - Imagem de referência **frontal** de alta qualidade (ChatGPT)
   - Aba **Imagem → 3D single** (não "Geração em lote", que trata cada imagem como objeto separado)
   - **Meshy 6, tipo Padrão** (não Smart Topology)
   - Densidade alta (~200k faces). **15k polígonos destrói a definição muscular.**
   - **Divisão automática desligada** (achado do piloto, 23/07) — ligada, o Meshy separa o modelo em partes e quebra a validação de malha única do `process.py`.

3. **Smart Topology não é necessário** — o tipo Padrão do Meshy 6 produziu resultado superior.

   **Multi-View: decisão revista.** Com imagem frontal única a qualidade foi surpreendentemente boa, inclusive nas costas — mas a Meshy *infere* o que não vê. Como o avatar **gira no app**, as costas são exibidas ao usuário e deixaram de ser tolerantes a erro. Com o plano Pro, o Multi-View passa a ser usado em toda a biblioteca: elimina a inferência e remove o principal risco de QA. Confirmar o custo em créditos do Multi-View antes da produção em lote.

4. **Filtro de conteúdo:** text-to-3D bloqueia corpo humano realista com pouca roupa. Image-to-3D passa. Por isso o pipeline é sempre imagem → 3D.

---

## 3. Arquitetura do pipeline

```
[MANUAL]     ChatGPT → folha de 3 vistas: frente | perfil | costas (Character Bible)
                ↓
[AUTOMÁTICO] crop.py → recorta a folha em 3 imagens (00_input/references/{id}/)
                ↓
[MANUAL]     Site da Meshy → Multi-View → gera → baixa GLB (fica em Downloads)
                ↓ Claude Code renomeia e move para 01_raw/ com o ID no nome
[AUTOMÁTICO] process.py → Blender headless: normaliza, decima, material Zenith, valida
                ↓
[AUTOMÁTICO] render.py → GLB otimizado + frames de turntable
                ↓
[MANUAL]     QA em folha de contato → aprova/reprova em uma passada
                ↓
[AUTOMÁTICO] build_index.py → library.json
                ↓
             App Zenith consome via CDN
```

**Por que a Meshy é manual.** Para 32 avatares, a API economizaria poucos cliques por item — as imagens e o QA já são manuais de qualquer forma — em troca de auth, polling, tratamento de erro e o risco de um bug consumir créditos em lote. Se a Onda 2 (~90 avatares) for adiante, reavaliar: aí o volume justifica.

O contrato entre o humano e o pipeline é o **nome do arquivo** do GLB salvo em `01_raw/`.

### Estrutura de pastas

```
zenith-avatar-library/
├── 00_input/
│   ├── sheets/              # folhas de 3 vistas do ChatGPT
│   └── references/          # recortes: uma subpasta {id}/ por avatar (front/side/back)
├── 01_raw/                  # GLBs baixados do site da Meshy (entrada do pipeline)
├── 02_master/               # GLBs normalizados (fonte de verdade)
├── 03_dist/
│   ├── glb/                 # otimizado para o app
│   └── turntable/           # frames / WebP animado
├── qa/
│   └── inspect/             # renders de QA por avatar
├── scripts/
│   ├── crop.py              # recorta a folha em 3 vistas
│   ├── process.py           # Blender headless
│   ├── render.py            # turntable (ainda não escrito)
│   └── build_index.py       # library.json (ainda não escrito)
└── library.json
```

---

## 4. Formato de entrega — decisão adiada de propósito

O avatar **gira sozinho** no app (o usuário não controla). Isso tem uma consequência: **as costas ficam visíveis**, então o QA precisa avaliar 360°, não só a frente.

Duas rotas viáveis:

**Turntable pré-renderizado** — 36–72 frames renderizados no Blender, exportados como WebP animado ou vídeo em loop.
`+` visualmente muito superior (luz de estúdio, glow roxo, sombra) `+` ~300–600 KB `+` zero engine 3D, zero bug

**GLB com auto-rotate no model-viewer** — infraestrutura já existe no app.
`+` sem retrabalho de integração `+` sem morph = sem enforcer, sem influences zerando `−` limitado pelo que o celular renderiza

**O pipeline produz os dois.** O GLB master normalizado é a fonte; o último passo exporta GLB otimizado *e* turntable. Testa-se no app e decide-se com o olho. Custo extra: um bloco de script.

### Peso e distribuição

O output cru da Meshy é inviável para celular — a produção mediu **130k a 232k triângulos** conforme o volume *e a definição* do corpo (não os ~211k fixos que se supunha; a decimação usa a contagem real). O topo da faixa é o `b07_d3`, um fisiculturista: massa alta somada a relevo abdominal profundo. Decimar 232k → 18k (razão 0,077) **não** custou definição visível.

- Alvo pós-decimação: **~18k triângulos**
- GLB otimizado com Draco: ~1–3 MB por avatar
- Turntable WebP: ~300–600 KB por avatar

32 avatares × GLB = 30–90 MB → **não empacotar no app**. Hospedar em CDN, baixar sob demanda apenas os 2 que o usuário precisa (atual + meta), com cache local. Em turntable o total é pequeno o suficiente para considerar embutir.

---

## 5. Normalização — o requisito crítico

Todos os avatares precisam ser **intercambiáveis sem salto visual**. Se um estiver 3 cm mais alto ou deslocado, ao trocar de arquétipo o corpo "pula" na tela e quebra a ilusão de progresso.

Regras obrigatórias no `process.py`:

- **Altura idêntica** para todos (a diferença entre arquétipos é largura e volume, nunca altura)
- Pés em `Y = 0`, centralizado em X e Z
- Mesmo eixo de rotação e mesma orientação frontal
- **Material roxo Zenith aplicado no pipeline**, idêntico em todos — não usar a textura da Meshy

> Gerar **sem textura** custa 20 créditos em vez de 30, reduz o tamanho do arquivo e garante cor matematicamente idêntica em toda a biblioteca.

A altura real do usuário é resolvida no app por **escala uniforme**, não por asset separado.

---

## 6. Plano Meshy Pro — decidido

**Decisão: assinar o plano Pro antes de iniciar a produção.** Ele destrava três coisas que o projeto precisa:

1. **Licença comercial.** No plano gratuito os assets saem sob CC BY 4.0 (exige atribuição). No pago, os assets são de propriedade do assinante e podem ser distribuídos comercialmente. Um app comercial não pode carregar obrigação de atribuição embutida.
2. **Download dos modelos** — necessário para o pipeline funcionar.
3. **Multi-View** — três vistas de referência em vez de uma, eliminando a inferência das costas.

Confirmar os termos de licença vigentes no momento da produção.

> **A biblioteca inteira precisa ser gerada sob o plano pago.** Nenhum avatar produzido no plano gratuito pode entrar na biblioteca, ainda que a qualidade esteja boa — a licença é diferente. Se houver assets do período de testes, descartá-los.

---

## 7. Escopo de produção

**Onda 1 (agora): masculino, 32 avatares.** 12 faixas de IMC × 3 níveis de definição, menos 4 combinações implausíveis. Ver `docs/ARCHETYPES.md`.

**Onda 2: feminino, ~32 avatares.** Mesma estrutura, produzida depois que a masculina validar o pipeline.

**Onda 3 (se necessário):** formatos corporais (pera / maçã / ampulheta / retângulo). O esquema do `library.json` já nasce prevendo o campo, com valor fixo `"medium"` até lá.

### Por que 12 faixas e não 6

A granularidade da grade define de quanto em quanto o usuário vê o próprio corpo mudar. Com faixas largas de 5 pontos de IMC, um homem de 1,75 m precisaria perder ~15 kg para o avatar mudar — meses de esforço sem retorno visual, contradizendo a proposta do app.

Com faixas de ~1,5 ponto na zona densa (IMC 20–29, onde vive a maioria), **~4,5 kg já trocam o avatar**.

O eixo refinado é o IMC, não a definição: IMC vem de peso e altura, medidos com precisão; a definição vem de percentual de gordura estimado, que é ruidoso. Refinar o eixo ruidoso seria falsa precisão.

Racional do faseamento: o custo em créditos é irrelevante (~US$36 para 90 avatares). O gargalo real é a produção manual das imagens e o QA. Além disso, num card de ~300 px com avatar roxo liso, a diferença entre formatos corporais no mesmo IMC é quase imperceptível. Constrói-se a estrutura completa e produz-se sob demanda — o pipeline já pronto torna a Onda 2 barata.

---

## 8. Roadmap

- [x] Assinar plano Meshy Pro (licença comercial + download + Multi-View)
- [x] Definir e aprovar a folha-mãe masculina (`m_b05_d2`)
- [x] **Piloto: 4 avatares masculinos** nos extremos (`m_b02_d3`, `m_b05_d2`, `m_b08_d1`, `m_b11_d1`) — pipeline validado ponta a ponta; definição e volume sobrevivem a 18k
- [ ] Validar formato de entrega no app (GLB vs turntable) — resolve também a borda serrilhada do short
- [ ] Produzir as 32 folhas masculinas (`docs/CHARACTER_BIBLE.md`)
- [ ] Reescrever a grade feminina com 12 faixas
- [ ] Rodar pipeline completo
- [ ] QA por folha de contato
- [ ] Publicar `library.json` + assets no CDN
- [ ] Implementar classificador no app (`ARCHETYPES.md`)

---

## 9. Nota de implementação para o Claude Code

- **Não há integração com a API da Meshy.** A geração é manual no site. Os scripts processam arquivos locais.
- O `process.py` deve ser **idempotente e não destrutivo**: não sobrescrever um master já aprovado sem confirmação explícita.
- Toda execução registra log: ID do arquétipo, triângulos antes/depois, altura normalizada, resultado das validações.
- Validações automáticas antes do QA humano: contagem de faces dentro do alvo, bounding box coerente, malha fechada, simetria esquerda/direita.
- Se a Onda 2 for adiante, reavaliar a automação da Meshy via API — nesse caso, confirmar endpoints e custo em créditos na documentação oficial vigente, nunca a partir deste documento.
