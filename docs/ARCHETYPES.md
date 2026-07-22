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

**O nome do arquivo é o contrato com o pipeline.** O script extrai o ID do arquétipo do nome do GLB em `01_raw/`. Nome errado = avatar errado na biblioteca.

### Versionamento

O sufixo `_v1` só existe nos arquivos de distribuição. Ao substituir um avatar reprovado, incrementa-se para `_v2` e atualiza-se o `library.json`. O app sempre lê o caminho do índice, nunca monta a URL por conta própria — assim uma troca de asset não exige atualização do app.

---

## 5. Classificação: medidas → arquétipo

### Passo 1 — IMC → faixa
```
IMC = peso_kg / (altura_m ** 2)
```
Mapear pela tabela da seção 2.

### Passo 2 — % gordura → definição

| Sexo | d3 (alta) | d2 (média) | d1 (baixa) |
|---|---|---|---|
| Masculino | < 13% | 13 – 20% | > 20% |
| Feminino | < 21% | 21 – 29% | > 29% |

> Cortes heurísticos para **seleção de asset**, não classificação clínica. Servem para escolher qual corpo desenhar, nada além disso.

### Passo 3 — fallback

Se a combinação não existir na grade, **reduzir a definição em um nível** e tentar de novo:

- `b01_d3` → `b01_d2`
- `b11_d3` → `b11_d2`
- `b12_d3` → `b12_d2` → `b12_d1`
- `b12_d2` → `b12_d1`

Se ainda assim falhar, usar o padrão do sexo: `zen_m_b05_d2`.

O app **nunca** deve exibir tela vazia por falta de arquétipo.

### Passo 4 — avatar da meta (tela Objetivo)

Mesma função, alimentada pelos valores-alvo:

```
IMC_meta      = peso_meta / (altura ** 2)
gordura_meta  = % gordura alvo do objetivo
```

Nenhum asset adicional é necessário — a tela de Objetivo consome a mesma biblioteca.

---

## 6. Esquema do `library.json`

```json
{
  "schema_version": 2,
  "generated_at": "2026-07-22T00:00:00Z",
  "cdn_base": "https://cdn.exemplo.com/avatars/",
  "default": { "m": "zen_m_b05_d2", "f": null },
  "bmi_bands": [
    { "id": "b01", "min": null, "max": 18.5 },
    { "id": "b02", "min": 18.5, "max": 20.0 },
    { "id": "b03", "min": 20.0, "max": 21.5 },
    { "id": "b04", "min": 21.5, "max": 23.0 },
    { "id": "b05", "min": 23.0, "max": 24.5 },
    { "id": "b06", "min": 24.5, "max": 26.0 },
    { "id": "b07", "min": 26.0, "max": 27.5 },
    { "id": "b08", "min": 27.5, "max": 29.0 },
    { "id": "b09", "min": 29.0, "max": 31.0 },
    { "id": "b10", "min": 31.0, "max": 34.0 },
    { "id": "b11", "min": 34.0, "max": 38.0 },
    { "id": "b12", "min": 38.0, "max": null }
  ],
  "avatars": [
    {
      "id": "zen_m_b07_d1",
      "sex": "m",
      "bmi_band": "b07",
      "definition": "d1",
      "body_shape": "medium",
      "version": 1,
      "assets": {
        "glb": "zen_m_b07_d1_v1.glb",
        "turntable": "zen_m_b07_d1_v1.webp"
      },
      "triangles": 18042,
      "approved": true
    }
  ]
}
```

As faixas de IMC vivem no `library.json`, não no código do app. Assim, refinar a grade no futuro não exige atualização do aplicativo.

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
