# rules.md — Zenith Avatar Library

Regras estáveis. Mudam pouco. O que muda a cada sessão está em `state.md`.

---

## 1. Divisão de trabalho

**Humano (Rogério):** gera as folhas no ChatGPT, opera o site da Meshy, **baixa o GLB em Downloads** (o Claude Code renomeia e move), aprova/reprova no QA.

**Claude Code (aqui):** estratégia e decisões técnicas, análise de imagens por medição de pixels, recorte das folhas (`crop.py`), processamento (`process.py`), inspeção e renders de QA no Blender, e move/renomeia o GLB baixado para `01_raw/`.

> Trabalhávamos antes no Claude web (chat) passando prompt para um Claude Code separado. **Migramos para o Claude Code em 23/07** — ele faz análise e scripts no mesmo lugar. O humano só toca ChatGPT e Meshy.

O recorte das folhas é feito **por script** (`scripts/crop.py`), não à mão e não no chat. Detecção de figura por diferença de fundo, o mesmo método do `process.py`: reprodutível nas 32 folhas. Escreve em `00_input/references/{id}/` (uma subpasta por avatar, para facilitar o upload no Meshy).

---

## 2. Como o Claude deve responder

- Direto ao ponto. Decidir, não apresentar opções para o humano escolher.
- Responder em português.
- Entregar arquivo pronto quando o pedido é um arquivo.
- Quando houver erro do Claude, assumir e corrigir sem rodeios.
- Medir antes de opinar sobre imagem (altura, alinhamento, escala em pixels).
- Não repetir análise já feita e registrada em `state.md`.

---

## 3. Gestão de contexto

1. **Claude avisa PROATIVAMENTE quando o contexto ficar longo** — sem esperar o Rogério perguntar. O aviso vem no fim de uma resposta, sugerindo migrar para uma conversa nova. Sinais de contexto longo: muitas imagens analisadas, muitas execuções de script/Blender, ou uma sessão que já cobriu várias fases.
2. Ao avisar, Claude **atualiza o `state.md`** com tudo que foi decidido — ele é o handoff.
3. Abre-se **conversa nova do Claude Code** na pasta do projeto. O `CLAUDE.md` já é carregado automaticamente; na primeira mensagem, Claude lê `state.md`, `rules.md` e `runbook.md` para se orientar. Nada precisa ser anexado à mão.

Ponto natural de corte: fim de uma fase do runbook, ou quando um problema fecha (ex.: piloto validado).

---

## 4. Decisões travadas — não revisitar sem motivo novo

1. **Biblioteca + seleção, não geração por usuário.** Custo, latência, QA e consistência.
2. **Não voltar a morph entre modelos gerados separadamente.** Topologias incompatíveis. Projeto anterior (Zenith Avatar Engine) abandonado por isso.
3. **A Meshy é manual.** Sem API, sem chave, sem `.env`.
4. **Altura idêntica em todos os avatares.** A diferença entre arquétipos é largura e volume.
5. **Decimação obrigatória.** GLB cru é inviável no celular.
6. **Cor aplicada no pipeline**, nunca vinda da textura da Meshy.
7. **Nada gerado no plano gratuito entra na biblioteca.** Licença diferente.
8. **Nenhum script sobrescreve `02_master/` sem `--force`.**
9. **O nome do arquivo é o contrato** entre o humano e o pipeline.

---

## 5. Regras de conteúdo dos avatares

- Careco, rosto neutro, pele cinza na referência.
- Corpo roxo Zenith + short preto, aplicados no pipeline.
- A-pose, perfil de 90° puro.
- Nunca variar o bloco fixo do Character Bible entre gerações.
- Folha com altura divergente das anteriores: **descartar**, não aproveitar. É o único erro que o pipeline não corrige.

---

## 6. Ordem de produção

Sempre em sequência pela grade, um nível de definição por vez, cada folha usando o vizinho imediato como referência anexa. Nunca aleatória.

```
d1:  b01 → b02 → ... → b12    (12 folhas)
d2:  b01 → b02 → ... → b11    (11 folhas)
d3:  b02 → b03 → ... → b10    ( 9 folhas)
```

---

## 7. Escopo

- **Onda 1 (atual):** 32 avatares masculinos.
- **Onda 2:** feminino, ~32. Grade PENDENTE, ainda com numeração antiga de 6 faixas. Não produzir.
- **Onda 3 (se necessário):** formatos corporais. `library.json` já prevê o campo.

Este repositório entrega assets + `library.json`. **Não se edita o app Zenith aqui.**