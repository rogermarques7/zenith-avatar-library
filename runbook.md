# Runbook — Produção de um Avatar

O passo a passo que se repete 32 vezes. Ler junto com `CHARACTER_BIBLE.md` (geração das imagens) e `ARCHETYPES.md` (grade e nomes).

---

## Visão geral

```
1. ChatGPT    → folha de 3 vistas
2. Você       → recorta em 3 imagens
3. Meshy      → Multi-View → GLB
4. Blender    → normaliza, decima, colore
5. Você       → QA em 360°
6. Script     → library.json
```

Etapas 1, 2, 3 e 5 são manuais. Etapas 4 e 6 são automatizadas.

---

## Fase 0 — Antes de qualquer coisa

- [x] **Assinar o plano Meshy Pro.** ✅ Concluído. Destrava Multi-View, download e licença comercial (o plano gratuito sai como CC BY 4.0, que não serve para um app comercial).

---

## Fase 1 — Folha-mãe

Esta é a etapa mais importante do projeto inteiro. A folha-mãe define o personagem dos 32 avatares.

1. No projeto do ChatGPT, conversa nova. **Sem imagem anexa** — é a primeira, não existe referência.
2. Pedir:
   ```
   Gere m_b05_d2

   Descritor: Peso normal e atlético. Peitoral e ombros com forma clara,
   braços com volume moderado, abdômen plano sem gomos. Aparência saudável
   e ativa.
   ```
3. **Iterar até ficar impecável.** Gerar quantas vezes for preciso. Trocar a folha-mãe depois obriga a refazer os 32 avatares.
4. Aprovar contra o checklist do Character Bible (seção 6).
5. Salvar duas cópias em `00_input/sheets/`:
   - `zen_m_b05_d2_sheet.png`
   - `_mother_m.png`

---

## Fase 2 — Piloto (4 avatares)

**Não produzir os 32 antes do piloto.** O piloto responde perguntas que mudariam tudo: a resolução de cada vista recortada é suficiente? A Meshy respeita o Multi-View? A definição muscular sobrevive à decimação? GLB ou turntable?

Arquétipos do piloto, escolhidos por cobrirem os extremos:

| ID | Por que está no piloto |
|---|---|
| `m_b02_d3` | Magro e definido — testa se detalhe muscular sobrevive |
| `m_b05_d2` | A folha-mãe — o meio da grade |
| `m_b08_d1` | Sobrepeso sem definição — testa volume e superfície lisa |
| `m_b11_d1` | Obesidade II — testa o extremo de volume |

Rodar o ciclo completo (Fases 3 a 6) nos quatro antes de seguir.

---

## Fase 3 — Gerar a folha

1. Projeto do ChatGPT, conversa nova (ou continuando um lote de até 4).
2. **Anexar duas imagens**: `_mother_m.png` e a última folha aprovada.
3. Pedir com o ID e o descritor copiado de `CHARACTER_BIBLE.md` seção 5:
   ```
   Gere m_b07_d1

   Descritor: [colar exatamente o texto do documento]
   ```
4. Conferir contra o checklist (Character Bible, seção 6). Atenção especial:
   - Mesma altura das folhas anteriores — **se a altura mudou, descartar**. É o único erro que o pipeline não corrige.
   - Perfil de 90 graus puro, não 3/4.
   - Espaçamento uniforme entre as vistas.
5. Salvar em `00_input/sheets/zen_m_bXX_dY_sheet.png`.

> Lotes de 3 a 4 folhas por conversa. Ver protocolo anti-deriva no Character Bible (seção 5b).

---

## Fase 4 — Recortar (automático)

```
python scripts/crop.py zen_m_bXX_dY
```

O `crop.py` detecta as 3 figuras por diferença de fundo (o mesmo método do `process.py`), recorta cada uma com margem uniforme (8% lateral / 5% vertical) e reamostra para 1200px de altura. Grava em `00_input/references/zen_m_bXX_dY/`:

- `zen_m_bXX_dY_ref_front.png`
- `..._ref_side.png`
- `..._ref_back.png`

Uma subpasta por avatar, para achar as 3 imagens fácil na hora de subir no Meshy. Rodar `crop.py zen_m_bXX_dY --check` mede o alinhamento sem gravar. Se detectar ≠ 3 vistas ou variação de altura > 2%, a folha tem espaçamento irregular → **regerar no ChatGPT, não compensar no recorte**.

---

## Fase 5 — Meshy

Configuração fixa, sempre a mesma (validada no piloto):

| Opção | Valor |
|---|---|
| Aba | Imagem → 3D (single, **não** Geração em lote) |
| Multi-View | **Ligado** — 3 slots: frente, lado, costas |
| Modelo | Meshy 6 |
| Tipo | Padrão (**não** Smart Topology) |
| Divisão automática | **Desligada** — ligada, quebra a validação de malha única |
| Pose | **Desligada** — ligada, o Meshy impõe pose própria e abre demais os braços; desligada, segue a referência (já em A-pose) |
| Melhoria de imagem | **Ligada** — não trocar no meio da biblioteca |
| Licença | Privado |
| Textura | **Sem textura** — a cor vem do Blender |
| Densidade | Alta (~200k faces). Nunca 15k: destrói a definição muscular |

Fluxo: **"Gerar Multi-visão" primeiro**, conferir as 3 vistas, só então **"Gerar"** — poupa os 20 créditos do modelo se as vistas saírem tortas.

Baixar o GLB **sem Redimensionar**. Deixar em Downloads — o Claude Code renomeia para `zen_m_bXX_dY_raw.glb` e move para `01_raw/`.

**O nome do arquivo é o contrato com o pipeline.** Nome errado = avatar errado na biblioteca.

Custo: **20 créditos por avatar** (Model Stage; a textura seria +10, mas geramos sem). Confirmado no piloto.

---

## Fase 6 — Processar

```
python scripts/process.py zen_m_bXX_dY
```

O script faz, em Blender headless:

1. **Normaliza** — altura idêntica, pés em Y=0, centralizado em X/Z, mesma orientação
2. **Decima** — cru (130k–229k conforme o volume) → ~18k triângulos
3. **Aplica o material roxo Zenith** — idêntico em todos
4. **Valida** — contagem de faces, bounding box, malha fechada, simetria
5. Salva em `02_master/` e exporta para `03_dist/`

Se alguma validação falhar, o script avisa e o avatar não segue para o QA.

---

## Fase 7 — QA

Gerar a folha de contato e revisar. Como o avatar gira no app, a avaliação é em **360°** — as costas contam.

Checklist humano em `ARCHETYPES.md` seção 8.

O item decisivo é o **teste da continuidade**: percorrer a sequência `b01 → b12` dentro de cada nível de definição. A progressão precisa parecer a mesma pessoa mudando gradualmente. Um avatar que salta reprova mesmo estando bonito sozinho.

Reprovado → refazer a folha no ChatGPT e repetir o ciclo.

---

## Fase 8 — Publicar

```
python scripts/build_index.py
```

Gera o `library.json` com todos os avatares aprovados. Subir `03_dist/` e o índice para o CDN.

---

## Ordem de produção dos 32

Nunca aleatória — sempre em sequência pela grade, para que cada folha nova tenha o vizinho imediato como referência:

```
d1:  b01 → b02 → b03 → ... → b12    (12 folhas)
d2:  b01 → b02 → b03 → ... → b11    (11 folhas)
d3:  b02 → b03 → b04 → ... → b10    ( 9 folhas)
```

Terminar um nível de definição antes de começar o próximo. Ao iniciar `d2`, a referência anexa volta a ser a folha-mãe mais a primeira folha de `d2`.

---

## Regras que não mudam

1. Altura sempre igual — a diferença entre arquétipos é largura e volume
2. Careca, rosto neutro, pele cinza (a cor roxa vem do Blender)
3. Sem textura na Meshy
4. Densidade alta na geração, decimação só no pipeline
5. Folha com altura errada se descarta, não se aproveita
6. Nada gerado no plano gratuito entra na biblioteca
