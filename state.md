# state.md — o presente

Última atualização: **29/07/2026 (sessão 9)**

> ## 🔴 ABRIR AQUI NA SESSÃO NOVA
>
> **O foco é FECHAR A BIBLIOTECA FEMININA INTEIRA. Decisão do Rogério, 29/07.**
> Masculino não se toca até isso acabar — inclusive os dois vãos `high` dele,
> que já têm conserto conhecido e **ficam anotados para depois**.
>
> A cobertura de IMC da linha `f d2` está **resolvida**: 7 avatares, 18,3 a
> 53,9, nenhum vão `high`. O que falta são as **outras duas linhas de
> definição**: `f d1` (12 arquétipos) e `f d3` (9), as duas **vazias**.
>
> Ordem: **`d1` primeiro, depois `d3`** (`ARCHETYPES.md` §5 — um nível por vez).
>
> **A receita que funciona, medida hoje:** âncora ÚNICA em **IMC alvo − 7**,
> substantivo de categoria positivo (sem negar o atrator), gerar no **Gemini**.
> Registrar a previsão ANTES de gerar. Ver `LICOES.md` §2.4b.

> **Este arquivo só guarda o AGORA.** Doutrinas duráveis estão em
> `docs/LICOES.md`; a narrativa de como cada uma foi descoberta está em
> `docs/historico/diario-2026-07.md`. Se algo aqui virar história, **mover** —
> não deixar crescer. Ele já teve 1631 linhas e não cabia numa leitura.

---

## Onde estamos

**46 avatares no `library.json`.** Onda masculina ENCERRADA (39). Onda feminina
EM PRODUÇÃO (7) — e **sem nenhum vão `high` restante**.

| linha | avatares | IMC medido |
|---|---:|---|
| m d1 | 17 | 16,1 – 147,7 |
| m d2 | 12 | 19,7 – 111,7 |
| m d3 | 10 | 19,9 – 53,8 |
| **f d2** | **7** | **18,3 – 53,9** |

Os sete femininos, todos 8/8 em 60k:

| id | IMC | banda nominal | onde caiu | gerador |
|---|---:|---|---|---|
| `zen_f_b02_d2` | 18,3 | 18,5–19,9 | 0,2 abaixo (é `b01`) | ChatGPT |
| `zen_f_b04_d2` | 22,2 | 21,5–22,9 | ✅ no meio | ChatGPT |
| `zen_f_b05_d2` (mãe) | 22,9 | 23,0–24,4 | 0,1 abaixo | ChatGPT |
| `zen_f_b06_d2` | 27,3 | 24,5–25,9 | ⚠️ 1,4 acima | ChatGPT |
| `zen_f_b09i_d2` | 30,1 | — (inserção) | ✅ previsto 29–31 | **Gemini** |
| `zen_f_b09h_d2` | 34,4 | — (inserção) | ✅ no alvo | **Gemini** |
| `zen_f_b09_d2` | 53,9 | 29,0–30,9 | ⚠️ muito acima (é `b12`) | ChatGPT |

**Tudo em `d2` de propósito, e não é rótulo errado por descuido.** O
`build_index.py` lê o nível de definição do NOME, e o fallback `d3→d2→d1` só
entra com a linha vazia — um avatar sozinho numa linha `f d1` seria entregue a
qualquer mulher classificada `d1`, de qualquer IMC. Enquanto a biblioteca
feminina for uma linha só, é onde tudo tem que ficar. Ver `LICOES.md` §5.2.

O eixo feminino cobre **18,3 a 53,9**: 18,3 · 22,2 · 22,9 · 27,3 · 30,1 · 34,4
· 53,9. Sobrou **um** vão, e ele é `low`: 34,4 → 53,9 (salto 19,5), na faixa de
população mínima. Os dois saltos baixos (3,9 e 4,4) ficam abaixo do limiar do
`build_index.py` e são menores que o passo do gerador.

---

## ➡️ O próximo passo

> **Não listar render como pendência.** O Rogério avalia no **app de testes**,
> não em PNG de `qa/look/`. Quem tira medida e decide se o avatar presta é o
> Claude Code, com `metrics.py` e as travas do `process.py`. Cobrado em 29/07.

**Abrir a linha `f d1`** — 12 arquétipos, descritores prontos em
`CHARACTER_BIBLE.md` §5. É a linha de **> 29% de gordura**: mulher sedentária,
corpo sem tônus. Depois dela, `f d3`.

**Uma decisão a tomar logo na primeira folha da linha nova.** Hoje TUDO é `d2`
por um motivo bom (o aviso acima): avatar sozinho numa linha é entregue a
qualquer IMC daquela linha. Ao começar a `d1`, a linha fica esparsa por algumas
folhas e a seleção degrada nesse intervalo. **Isso é aceitável** — a biblioteca
feminina ainda não está no app —, mas a consequência é produzir a `d1`
**inteira e em sequência**, sem intercalar com outra linha e sem parar no meio.

Se por algum motivo a produção precisar parar com a `d1` pela metade, a saída é
nomear as folhas restantes como `d2` até haver densidade — nunca deixar uma
linha com 2 ou 3 avatares soltos.

**Fluxo, quando voltar a produzir:**
```
python scripts/sheet_qa.py "<folha em Downloads>" 00_input/sheets/f/_mother_f.png
python scripts/intake.py  zen_f_bXX_d2
python scripts/crop.py    zen_f_bXX_d2
   (Meshy: Multi-View, Meshy 6 Padrao, densidade alta,
    SEM textura, divisao automatica DESLIGADA)
python scripts/process.py zen_f_bXX_d2      # 60k, 8/8
python scripts/metrics.py zen_f_bXX_d2
python scripts/build_index.py
python scripts/restyle.py --preview zen_f_bXX_d2
```

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

---

## Pendências que não bloqueiam

- `render.py` (turntable) não existe — e pode não ser necessário: o GLB com
  auto-rotate no model-viewer foi aprovado no teste do app.
- **Dois vãos `high` masculinos seguem abertos: d1 27,8→33,3 e d3 27,4→32,4 — e
  a recomendação antiga ("aceitar e cobrir por shape keys") está SUPERADA.**
  Ela foi escrita quando não havia método para mirar o meio de um vão. Hoje há,
  e é medido: âncora única em **IMC alvo − 7** e gerar no **Gemini**. Para o
  `m d1` isso dá âncora ~23,5 mirando ~30,5; para o `m d3`, âncora ~23 mirando
  ~30. **Anotado a pedido do Rogério (29/07) para depois — não executar antes
  de a biblioteca feminina fechar.**
- Lado do app Zenith (outro repositório): ver o fim do diário, seção 10.
