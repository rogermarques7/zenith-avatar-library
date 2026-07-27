# Grade de Arquétipos

Define **quais** avatares existem, **como se chamam** e **como o app escolhe** um deles.

> **Status:** grade masculina definida (32 avatares). Grade feminina pendente — será espelhada com a mesma estrutura após a produção masculina.

---

## 1. Princípio da granularidade

A grade é fina onde os usuários estão e grossa onde eles não estão.

O eixo refinado é o **IMC**, não a definição. IMC vem de peso e altura — dados que o app mede com precisão. O nível de definição vem de percentual de gordura estimado, que é um dado ruidoso; refinar demais esse eixo seria falsa precisão.

Faixas de ~1,5 ponto de IMC na zona densa (20–29) significam que **~4,5 kg de mudança já trocam o avatar** para um homem de 1,75 m. Na grade anterior, de faixas largas, eram necessários ~15 kg — o usuário via o próprio corpo parado por meses de esforço, o que contradiz a proposta do app.

---

## 2. Eixos

### Sexo
`m` masculino · `f` feminino

### Faixa de IMC (12)

| ID | Faixa | Rótulo | Largura |
|---|---|---|---|
| `b01` | < 18,5 | Abaixo do peso | ampla |
| `b02` | 18,5 – 19,9 | Muito magro | 1,5 |
| `b03` | 20,0 – 21,4 | Magro | 1,5 |
| `b04` | 21,5 – 22,9 | Normal baixo | 1,5 |
| `b05` | 23,0 – 24,4 | Normal | 1,5 |
| `b06` | 24,5 – 25,9 | Normal alto | 1,5 |
| `b07` | 26,0 – 27,4 | Sobrepeso leve | 1,5 |
| `b08` | 27,5 – 28,9 | Sobrepeso | 1,5 |
| `b09` | 29,0 – 30,9 | Sobrepeso alto | 2,0 |
| `b10` | 31,0 – 33,9 | Obesidade I | 3,0 |
| `b11` | 34,0 – 37,9 | Obesidade II | 4,0 |
| `b12` | ≥ 38,0 | Obesidade III | ampla |

### Nível de definição (3)

| ID | Rótulo | Descrição visual |
|---|---|---|
| `d1` | Baixa | Sem tônus, superfície lisa e mole, sem musculatura aparente |
| `d2` | Média | Tônus visível, contornos suaves, sem cortes marcados |
| `d3` | Alta | Musculatura definida, gomos abdominais, separação muscular clara |

---

## 3. A grade masculina (32 avatares)

Produto cartesiano = 36. Removidas **4 combinações fisicamente implausíveis**:

| Removida | Motivo |
|---|---|
| `b01_d3` | Abaixo do peso não comporta massa muscular alta |
| `b11_d3` | IMC 34–38 com alta definição: apenas fisiculturismo de elite |
| `b12_d3` | IMC ≥ 38 com alta definição: fora da realidade da base de usuários |
| `b12_d2` | IMC ≥ 38 com tônus visível: obesidade III tem essencialmente uma apresentação visual |

|  | d1 | d2 | d3 |
|---|:---:|:---:|:---:|
| **b01** | ✅ | ✅ | ❌ |
| **b02** | ✅ | ✅ | ✅ |
| **b03** | ✅ | ✅ | ✅ |
| **b04** | ✅ | ✅ | ✅ |
| **b05** | ✅ | ✅ | ✅ |
| **b06** | ✅ | ✅ | ✅ |
| **b07** | ✅ | ✅ | ✅ |
| **b08** | ✅ | ✅ | ✅ |
| **b09** | ✅ | ✅ | ✅ |
| **b10** | ✅ | ✅ | ✅ |
| **b11** | ✅ | ✅ | ❌ |
| **b12** | ✅ | ❌ | ❌ |

**Total: 32 avatares masculinos.**

> `b10_d3` (IMC 31–34 com alta definição) **permanece na grade** e é importante. Um homem de 1,75 m com 100 kg e baixa gordura tem IMC 32,6 — é o arquétipo do fisiculturista, público-alvo direto de um app de musculação, não uma exceção.

---

## 4. Convenção de nomes

```
zen_{sexo}_{imc}_{definicao}_v{versao}
```

Exemplo: `zen_m_b07_d1_v1`

| Etapa | Arquivo |
|---|---|
| Folha de 3 vistas (manual) | `zen_m_b07_d1_sheet.png` |
| Recortes | `zen_m_b07_d1_ref_front.png` · `_ref_side.png` · `_ref_back.png` |
| GLB baixado da Meshy | `zen_m_b07_d1_raw.glb` |
| GLB master normalizado | `zen_m_b07_d1_master.glb` |
| GLB distribuição | `zen_m_b07_d1_v1.glb` |
| Turntable | `zen_m_b07_d1_v1.webp` |

O ID da faixa usa **dois dígitos** (`b07`, não `b7`) para que a ordenação alfabética dos arquivos coincida com a ordem da grade. Isso importa na folha de contato do QA, onde os vizinhos precisam aparecer lado a lado.

### Avatares inseridos

Um avatar produzido para **preencher um buraco de cobertura** leva o sufixo `h`
na banda: `zen_m_b06h_d3` foi gerado mirando o vão entre `b06` e `b07`.

> **O sufixo registra a INTENÇÃO, não o resultado.** O `zen_m_b05h_d1` foi
> pedido para o vão `b05`→`b06` e o corpo saiu em IMC 26,2, ou seja **entre
> `b04` e `b05`**. O nome ficou "errado" e **isso não importa**: desde o
> schema 3 quem ordena a biblioteca é o `measured_bmi`, não o nome do arquivo.
> Renomear o asset só moveria a inconsistência para o `logs/process.log`, que
> é append-only.

Consequência: a antiga regra de "ordenação alfabética = ordem da grade" só vale
para a grade nominal original. **A folha de contato do QA deve ser ordenada por
`measured_bmi` do `library.json`**, que é a ordem real dos corpos.

**O nome do arquivo é o contrato com o pipeline.** O script extrai o ID do arquétipo do nome do GLB em `01_raw/`. Nome errado = avatar errado na biblioteca.

### Versionamento

O sufixo `_v1` só existe nos arquivos de distribuição. Ao substituir um avatar reprovado, incrementa-se para `_v2` e atualiza-se o `library.json`. O app sempre lê o caminho do índice, nunca monta a URL por conta própria — assim uma troca de asset não exige atualização do app.

---

## 5. Classificação: medidas → arquétipo

> **Revisado em 26/07/2026 (schema 3).** A classificação deixou de usar a faixa
> nominal do ID e passou a usar o **IMC medido de cada avatar**. Motivo: o
> `scripts/metrics.py` mediu o volume dos masters e mostrou que o corpo
> produzido não corresponde à faixa que o nome promete — o `zen_m_b12_d1` foi
> pedido para IMC ≥ 38 e o corpo tem IMC **147**. O ID virou apenas nome de
> arquivo; quem classifica é a medida.
>
> Isso não descarta nenhum asset: os corpos formam uma escada bem ordenada,
> só estavam rotulados errado. Avatar novo é **inserção** — vira mais um ponto
> no eixo de IMC, sem renomear nem substituir nada.

### Passo 1 — IMC do usuário → IMC alvo (corrigir pela altura)

```
IMC_usuario = peso_kg / (altura_m ** 2)
IMC_alvo    = IMC_usuario * (1.75 / altura_m)
```

**Escala uniforme não preserva IMC.** Ao escalar por `s`, o volume vai com `s³`
e a altura com `s²`, então o IMC representado vai com `s`. O mesmo avatar
exibido para alguém de 1,90 m representa ~8,6% mais IMC do que para alguém de
1,75 m. Sem essa correção, o app entrega um corpo sistematicamente errado nos
extremos de altura.

### Passo 2 — % gordura → definição

| Sexo | d3 (alta) | d2 (média) | d1 (baixa) |
|---|---|---|---|
| Masculino | < 13% | 13 – 20% | > 20% |
| Feminino | < 21% | 21 – 29% | > 29% |

> Cortes heurísticos para **seleção de asset**, não classificação clínica. Servem para escolher qual corpo desenhar, nada além disso.

### Passo 3 — selecionar o avatar mais próximo

Dentro da linha de definição escolhida, pegar o avatar de **menor
`|measured_bmi − IMC_alvo|`**. Não existe mais tabela de faixas: a lista de
avatares É o eixo, e cada um é um ponto nele.

Por isso não há mais "combinação inexistente" — sempre existe um mais próximo.
O fallback de definição (`d3 → d2 → d1`) só entra se a linha inteira estiver
vazia, o que hoje só vale para o feminino.

Se nem isso resolver, usar `default` do índice. O app **nunca** deve exibir
tela vazia por falta de arquétipo.

> **Vantagem estrutural:** inversões se resolvem sozinhas. Na grade nominal
> `b02_d2` e `b03_d2` estavam trocados (IMC medido 20,8 contra 20,4);
> ordenados pela medida, cada um cai no seu lugar sem intervenção.

### Passo 3b — buracos de cobertura

O `build_index.py` emite `coverage_gaps`: onde o salto de IMC entre vizinhos é
grande, o usuário que cai no meio recebe um corpo distante do dele. **Não é
erro — é a lista de onde inserir os próximos avatares.** Os buracos marcados
`high` estão na faixa onde há usuário de verdade (IMC 17–40); os `low` estão na
obesidade extrema e quase não têm população, por maior que seja o salto.

### Passo 4 — avatar da meta (tela Objetivo)

Mesma função, alimentada pelos valores-alvo:

```
IMC_meta      = peso_meta / (altura ** 2)
gordura_meta  = % gordura alvo do objetivo
```

Nenhum asset adicional é necessário — a tela de Objetivo consome a mesma biblioteca.

---

## 6. Esquema do `library.json`

Gerado por `scripts/build_index.py` a partir de `metrics/library_metrics.json`.

```json
{
  "schema_version": 3,
  "generated_at": "2026-07-26T22:00:00Z",
  "cdn_base": "https://cdn.exemplo.com/avatars/",
  "reference_height_m": 1.75,
  "selection": {
    "rule": "nearest_measured_bmi_within_definition",
    "target_bmi_formula": "bmi_usuario * (reference_height_m / altura_usuario_m)",
    "definition_thresholds_bodyfat_pct": {
      "m": { "d3_below": 13.0, "d2_below": 20.0 }
    },
    "definition_fallback": ["d3", "d2", "d1"]
  },
  "default": { "m": "zen_m_b04_d2", "f": null },
  "coverage_gaps": [
    { "sex": "m", "definition": "d1", "between": ["zen_m_b05_d1", "zen_m_b06_d1"],
      "bmi_from": 27.8, "bmi_to": 38.8, "bmi_step": 11.0, "priority": "high" }
  ],
  "avatars": [
    {
      "id": "zen_m_b07_d3",
      "sex": "m",
      "definition": "d3",
      "measured_bmi": 35.7,
      "measured_mass_kg": 109.3,
      "waist_to_height": 0.488,
      "label": "magro",
      "body_shape": "medium",
      "version": 1,
      "assets": { "glb": "zen_m_b07_d3_v1.glb", "turntable": null },
      "circumferences_cm": { "chest": 116.1, "waist_navel": 85.4, "thigh": 69.9 },
      "approved": true
    }
  ]
}
```

**Não existe mais `bmi_bands`.** A lista de avatares é o próprio eixo: cada um
carrega o IMC que tem, e o app pega o mais próximo. Refinar a grade continua
não exigindo atualização do app — e agora **acrescentar** avatar também não.

`bmi_band` saiu do avatar: a faixa nominal do ID não descrevia o corpo.

`label` e `waist_to_height` são para leitura humana. O rótulo vem de
**cintura/altura, não de IMC** — o IMC não separa músculo de gordura, e o
`zen_m_b07_d3` (IMC 35,7) sairia como "obesidade II" sendo um fisiculturista de
cintura 85 cm. Por cintura/altura ele dá 0,488, que lê corretamente como magro.

`circumferences_cm` viaja no índice porque é o insumo das **shape keys** do
sistema híbrido: ajustar um membro exige saber a medida de base dele.

O campo `body_shape` fica fixo em `"medium"` na Onda 1 e existe para acomodar formatos corporais (pera / maçã / retângulo) numa onda futura sem migração de esquema.

---

## 7. Ordem de produção

Produzir **em sequência pela grade**, nunca aleatoriamente:

```
b01_d1 → b02_d1 → b03_d1 → ... → b12_d1
b01_d2 → b02_d2 → ... → b11_d2
b02_d3 → b03_d3 → ... → b10_d3
```

Cada folha nova é gerada tendo o **vizinho imediato** como referência anexa. Isso é o que produz uma progressão visual contínua em vez de 32 modelos isolados.

---

## 8. Checklist de QA

Como o avatar gira no app, a avaliação é em 360°.

**Automático (`process.py`):**
- [ ] Triângulos dentro do alvo (~18k ± 15%)
- [ ] Altura normalizada idêntica à referência
- [ ] Pés em Y=0, centralizado em X/Z
- [ ] Malha fechada (sem furos)
- [ ] Simetria esquerda/direita dentro da tolerância

**Humano (folha de contato):**
- [ ] Anatomia crível de frente, lado e **costas**
- [ ] Nenhum membro derretido, fundido ou deformado
- [ ] Rosto neutro e consistente com os demais avatares
- [ ] O tipo de corpo corresponde ao arquétipo pedido
- [ ] **Continuidade com os vizinhos** — ver abaixo

### O teste da continuidade

O item mais importante do QA. Com as folhas de contato ordenadas por faixa, percorrer a sequência `b01 → b12` dentro de cada nível de definição.

A progressão precisa parecer **a mesma pessoa mudando gradualmente**. Se um avatar salta — muda de altura, de proporção, de identidade — ele reprova mesmo que esteja bonito isoladamente.

Faixas vizinhas estão a 1,5 ponto de IMC de distância: a diferença deve ser **perceptível mas sutil**. Se dois vizinhos parecerem idênticos, a faixa não está sendo respeitada na geração da imagem. Se parecerem pessoas diferentes, houve deriva do personagem.
