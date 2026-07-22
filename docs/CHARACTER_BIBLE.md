# Character Bible — Zenith

Documento operacional para gerar as **imagens de referência** no ChatGPT.

A consistência da biblioteca inteira depende deste arquivo. **Não improvisar, não reescrever o bloco fixo, não "melhorar" o texto entre gerações.** Qualquer variação de linguagem produz variação de personagem.

---

## 1. Por que a consistência é resolvível

Três travas eliminam quase toda a variação entre conversas:

1. **Careca, sem cabelo, rosto neutro.** Cabelo e feições são o que a IA mais varia entre gerações. Removê-los elimina a maior fonte de inconsistência — e é exatamente como o avatar já aparece no app hoje.
2. **Bloco fixo literal.** O texto abaixo é colado idêntico em toda geração; só o parágrafo `TIPO DE CORPO` muda.
3. **Imagem-mãe anexada.** A cada nova geração, anexar a imagem aprovada de referência e declarar que é a mesma personagem.

A quarta trava é fora do ChatGPT: **a cor roxa não vem da imagem nem da Meshy.** O material Zenith é aplicado no pipeline do Blender, idêntico em todos. A imagem só precisa acertar a **forma**.

---

## 2. Regra que não pode ser violada

> **A altura da personagem é SEMPRE a mesma em todas as imagens.**
> A diferença entre tipos de corpo aparece em **largura e volume**, nunca em altura.

O pipeline normaliza todos os modelos para a mesma altura. Se uma imagem desenhar a personagem mais baixa ou mais alta, a normalização vai distorcer as proporções e o avatar ficará errado — gordo e esticado, ou magro e achatado.

---

## 3. Bloco fixo — FEMININO

Colar literalmente. Substituir apenas `{TIPO_DE_CORPO}`.

```
Gere uma FOLHA DE REFERÊNCIA (character turnaround) do avatar FEMININO do
Zenith, para eu converter em modelo 3D via Multi-View. UMA imagem contendo
3 vistas do MESMO personagem, lado a lado, na ordem exata:
FRENTE | PERFIL LATERAL (virada para a direita) | COSTAS.
É SEMPRE a mesma personagem — só o tipo de corpo muda entre as folhas.

PERSONAGEM (idêntico em todas as imagens):
- Mulher, CARECA, sem nenhum cabelo.
- Rosto neutro e liso, feições suaves e genéricas, sem maquiagem, sem
  expressão marcante, sem detalhes faciais fortes.
- Pele cinza-clara neutra e uniforme (a cor final é aplicada depois).
- Roupa: top de compressão preto liso + shorts de compressão preto liso,
  bem justos ao corpo, sem estampas, sem logos, sem texturas.
- Sem calçados, sem acessórios, sem joias.

POSE E ENQUADRAMENTO (idêntico nas 3 vistas e em todas as folhas):
- A-pose neutra: em pé, ereta, braços afastados do corpo cerca de 40 graus,
  palmas viradas para dentro, pernas na largura dos ombros.
- A MESMA pose exata nas 3 vistas — apenas o ângulo da câmera muda, o corpo
  não se mexe entre as vistas.
- O perfil lateral é um perfil PURO de 90 graus, nunca 3/4.
- Corpo INTEIRO visível, da cabeça aos pés, em TODAS as 3 vistas.
- As 3 vistas na MESMA ESCALA e ALINHADAS: topo da cabeça e sola dos pés na
  mesma altura horizontal nas três.
- Câmera reta, ortográfica, na altura do peito, na mesma altura nas 3 vistas.
  Sem perspectiva, sem distorção de lente, sem close, sem inclinação.
- A personagem ocupa sempre a MESMA ALTURA em todas as folhas geradas.
- Espaçamento uniforme entre as 3 vistas, cada uma centralizada no seu terço
  da imagem.

ALTURA (regra crítica):
- A altura da personagem é SEMPRE A MESMA. A diferença entre os tipos de
  corpo aparece apenas na LARGURA e no VOLUME do corpo, NUNCA na altura.

FUNDO E LUZ (idêntico em todas as imagens):
- Fundo cinza-claro liso e uniforme. Sem cenário, sem chão, sem horizonte.
- Iluminação frontal difusa e neutra, sem sombras duras, sem sombra projetada
  no fundo, sem brilho estourado, sem contraluz.

NÃO INCLUIR: cabelo, texto, rótulos, setas, molduras, grades, linhas de
separação entre as vistas, logos, marcas d'água, ou qualquer marcação sobre
o corpo. Apenas as 3 figuras sobre o fundo liso.

TIPO DE CORPO desta folha (igual nas 3 vistas):
{TIPO_DE_CORPO}

Proporção da imagem larga (paisagem). Maior resolução possível.
```

---

## 4. Bloco fixo — MASCULINO

Idêntico ao feminino, com duas alterações:

- `Mulher, CARECA` → `Homem, CARECO`
- Roupa: `top de compressão preto liso + shorts de compressão preto liso` → `apenas shorts de compressão preto liso, justo, torso nu, sem estampas, sem logos`

Todo o restante permanece palavra por palavra.

---

## 5. Descritores de tipo de corpo

Colar no slot `{TIPO_DE_CORPO}`. Um por arquétipo.

### Feminino — PENDENTE

> A grade feminina ainda usa a numeração antiga de 6 faixas (`b1`–`b6`) e **não deve ser produzida ainda**. Será reescrita com 12 faixas, espelhando a estrutura masculina, depois que a produção masculina validar o pipeline. Os descritores abaixo servem apenas como base de reescrita.


| ID | Descritor |
|---|---|
| `f_b1_d1` | Muito magra e frágil. Ossos aparentes na clavícula e nas costelas, membros muito finos, sem nenhum tônus muscular, quadril estreito, abdômen côncavo. |
| `f_b1_d2` | Muito magra porém com leve tônus. Membros finos com contorno muscular sutil, sem volume, abdômen plano e liso, silhueta reta. |
| `f_b2_d1` | Magra "skinny-fat": esbelta porém sem definição alguma. Superfície lisa e mole, abdômen liso sem gomos, braços e pernas finos mas sem tônus. Arquétipo da mulher sedentária de peso normal. |
| `f_b2_d2` | Magra com tônus leve. Contorno suave de ombros, braços e pernas, abdômen plano sem gomos, aparência saudável mas não atlética. |
| `f_b2_d3` | Magra e definida. Percentual de gordura muito baixo, gomos abdominais visíveis, ombros e pernas torneados, separação muscular clara. Atleta fitness magra. |
| `f_b3_d1` | Peso normal, corpo mole. Cintura pouco marcada, leve acúmulo no abdômen e quadril, sem definição muscular nenhuma, superfície lisa. |
| `f_b3_d2` | Peso normal e levemente atlética. Tônus visível nos braços e pernas, abdômen plano sem gomos, cintura definida, aparência ativa e saudável. |
| `f_b3_d3` | Peso normal e bem definida. Físico de atleta fitness: gomos abdominais marcados, glúteos e coxas torneados, ombros desenhados, cintura fina. |
| `f_b4_d1` | Sobrepeso. Acúmulo de gordura no abdômen, quadril e coxas, contornos arredondados e macios, sem definição muscular, braços mais cheios. |
| `f_b4_d2` | Sobrepeso com musculatura por baixo. Corpo forte e volumoso, ombros e coxas largos, gordura cobrindo os músculos, abdômen sem definição. |
| `f_b4_d3` | Musculosa com pouca gordura. Massa muscular alta, ombros largos, coxas grossas e definidas, abdômen com definição visível apesar do peso elevado. Atleta forte. |
| `f_b5_d1` | Obesidade grau I. Abdômen proeminente, quadril e coxas volumosos, braços cheios, pescoço mais curto, contornos totalmente arredondados. |
| `f_b5_d2` | Obesidade grau I com massa muscular. Corpo grande e forte, estrutura larga, musculatura presente porém coberta por gordura. |
| `f_b5_d3` | Fisiculturista feminina pesada. Volume muscular muito alto com baixo percentual de gordura, ombros e coxas muito desenvolvidos, definição visível. |
| `f_b6_d1` | Obesidade grau II. Corpo muito volumoso, abdômen grande e proeminente, membros espessos, dobras visíveis, silhueta arredondada. |
| `f_b6_d2` | Obesidade grau II com força. Estrutura muito grande e pesada, ombros e costas largos, força evidente sob a camada de gordura. |

### Masculino — 32 arquétipos

Produzir **nesta ordem**, um nível de definição por vez. Cada folha usa a anterior como referência anexa.

#### d1 — definição baixa (12)

| ID | Descritor |
|---|---|
| `m_b01_d1` | Extremamente magro. Costelas, clavícula e escápulas aparentes, membros muito finos, ombros estreitos, abdômen côncavo, nenhuma massa muscular. |
| `m_b02_d1` | Muito magro e sem tônus. Costelas levemente visíveis, braços e pernas finos e moles, ombros estreitos, barriga plana e lisa. |
| `m_b03_d1` | Magro sem definição nenhuma. Corpo liso, braços e pernas finos sem tônus, leve moleza no abdômen, peitoral plano. |
| `m_b04_d1` | Magro "skinny-fat": esbelto porém mole. Pequena camada de gordura na barriga, peitoral sem forma, braços finos sem tônus. |
| `m_b05_d1` | Peso normal, corpo mole. Leve barriga, peitoral plano e sem definição, cintura levemente larga, braços sem tônus. |
| `m_b06_d1` | Peso normal alto. Barriga levemente saliente, contornos arredondados, cintura larga, nenhum tônus muscular. |
| `m_b07_d1` | Sobrepeso leve. Barriga saliente sobre a linha da cintura, peitoral levemente caído, braços cheios e moles. |
| `m_b08_d1` | Sobrepeso. Barriga claramente proeminente, cintura larga, peitoral caído, pescoço mais grosso, membros cheios. |
| `m_b09_d1` | Sobrepeso alto. Barriga grande e arredondada, dobra visível na cintura, membros espessos, ombros arredondados. |
| `m_b10_d1` | Obesidade grau I. Abdômen grande e proeminente, peitoral caído, pescoço curto, membros grossos, silhueta totalmente arredondada. |
| `m_b11_d1` | Obesidade grau II. Corpo muito volumoso, abdômen muito grande, dobras visíveis no tronco, membros muito espessos. |
| `m_b12_d1` | Obesidade grau III. Corpo extremamente volumoso, abdômen enorme e pendente, dobras acentuadas, pescoço muito curto, membros muito grossos. |

#### d2 — definição média (11)

| ID | Descritor |
|---|---|
| `m_b01_d2` | Muito magro com leve tônus. Membros finos com contorno muscular sutil, abdômen plano, ombros estreitos porém com alguma forma. |
| `m_b02_d2` | Magro com tônus leve. Contorno muscular sutil em braços e ombros, abdômen plano e liso, sem volume muscular. |
| `m_b03_d2` | Magro e levemente atlético. Ombros com forma, braços com leve volume, peitoral discreto, abdômen plano sem gomos. |
| `m_b04_d2` | Peso normal com tônus. Peitoral com forma leve, braços sutilmente definidos, abdômen plano, cintura marcada. |
| `m_b05_d2` | Peso normal e atlético. Peitoral e ombros com forma clara, braços com volume moderado, abdômen plano sem gomos. Aparência saudável e ativa. |
| `m_b06_d2` | Peso normal alto com musculatura. Volume muscular moderado coberto por leve camada de gordura, ombros largos, abdômen sem definição. |
| `m_b07_d2` | Sobrepeso leve com musculatura por baixo. Ombros e costas largos, barriga leve, braços grossos, força evidente sob a gordura. |
| `m_b08_d2` | Sobrepeso com boa massa muscular. Tronco largo e espesso, barriga presente, braços e pernas grossos, sem definição visível. |
| `m_b09_d2` | Corpo grande e forte. Ombros muito largos, musculatura evidente sob camada de gordura, barriga proeminente, membros muito grossos. |
| `m_b10_d2` | Obesidade grau I com força. Físico de powerlifter: estrutura muito larga, massa muscular alta sob a gordura, abdômen grande. |
| `m_b11_d2` | Obesidade grau II com força. Corpo enorme e pesado, costas e ombros muito largos, força visível apesar do volume de gordura. |

#### d3 — definição alta (9)

| ID | Descritor |
|---|---|
| `m_b02_d3` | Magro e muito seco. Percentual de gordura muito baixo, gomos abdominais visíveis, serrátil aparente, músculos desenhados porém sem volume. |
| `m_b03_d3` | Magro e definido. Abdômen com gomos marcados, ombros e braços desenhados, peitoral com forma, pouca massa muscular. |
| `m_b04_d3` | Atlético e definido. Gomos abdominais claros, peitoral desenhado, braços e ombros com separação muscular visível. |
| `m_b05_d3` | Musculoso e definido. Peitoral marcado, braços com volume e definição, ombros largos, abdômen com gomos evidentes. |
| `m_b06_d3` | Bem musculoso e seco. Ombros largos, peitoral desenvolvido, dorsais visíveis, abdômen definido, veias aparentes nos braços. |
| `m_b07_d3` | Muito musculoso. Massa alta com baixa gordura, ombros muito largos, braços e coxas volumosos, abdômen definido. |
| `m_b08_d3` | Físico de fisiculturista. Massa muscular alta, peitoral e dorsais desenvolvidos, cintura estreita em relação aos ombros, abdômen definido. |
| `m_b09_d3` | Fisiculturista pesado. Volume muscular muito alto, dorsais largos, braços e coxas muito desenvolvidos, definição mantida. |
| `m_b10_d3` | Fisiculturista de grande porte. Massa muscular extrema, estrutura enorme, ombros e coxas muito volumosos, abdômen ainda definido. |

---

## 5b. Protocolo anti-deriva

Modelos de imagem **perdem o personagem** ao longo de uma conversa. Isso é esperado e não se combate com contexto longo — combate-se com âncora e com tolerância.

### O que realmente precisa ser consistente

| Atributo | Ancorado por | Deriva? |
|---|---|---|
| Altura, pose, câmera, enquadramento | **bloco de texto fixo** | Não — não depende de memória |
| Roupa, fundo, iluminação | **bloco de texto fixo** | Não |
| Proporção e identidade do corpo | imagens anexas | Sim, gradualmente |
| Rosto | imagens anexas | Sim — **e tem pouca importância** |

Tudo que é mensurável está no texto fixo, que é idêntico em toda geração. Isso não deriva porque não depende do modelo lembrar de nada.

### Por que a deriva facial importa pouco

O avatar final é **careca, roxo, com material uniforme e exibido pequeno na tela**. A textura da Meshy é descartada e o material Zenith é aplicado no pipeline. Uma variação sutil de feições na imagem de referência praticamente **não sobrevive** até o asset final.

A decisão de usar careca e rosto neutro existe exatamente para isso: tornar a deriva irrelevante em vez de tentar impedi-la.

### Regras operacionais

1. **Lotes de 3 a 4 folhas por conversa.** Não tentar 12 ou 32 numa conversa só — vai derivar.
2. **Sempre duas imagens anexas**: a folha-mãe (`m_b05_d2`) e a última folha aprovada.
3. **Gerar em sequência pela grade**, para que a folha anterior seja sempre o vizinho imediato.
4. Ao abrir conversa nova, reanexar as duas imagens e colar o bloco fixo. Nada mais é necessário — **cada geração é autossuficiente**.
5. Se derivar: `mantenha a personagem idêntica às imagens anexas`. Se insistir, encerra a conversa e abre outra — é mais rápido que brigar com o contexto.
6. Se a folha sair com altura diferente das anteriores, **descartar sem tentar aproveitar**. Altura é o único erro que o pipeline não consegue corrigir.

---

## 6. Procedimento por imagem

1. Nova conversa (ou a mesma — o bloco fixo protege os dois jeitos).
2. **Anexar DUAS imagens**: a folha-mãe do sexo *e* a última folha aprovada (o vizinho imediato na grade).
3. Colar o bloco fixo com o descritor do arquétipo no slot.
4. Se o resultado divergir do personagem: responder `mantenha a personagem idêntica à imagem anexa — mesmo rosto, mesma careca, mesma roupa, mesma altura`.
5. Se as vistas divergirem entre si: `mantenha a personagem idêntica à vista frontal nas outras duas vistas`.
6. Conferir contra o checklist abaixo.
7. Salvar como `zen_{sexo}_{imc}_{def}_sheet.png` em `00_input/sheets/`.

O recorte em três imagens é feito pelo pipeline, não à mão. Por isso o
espaçamento uniforme entre as vistas é obrigatório — o script divide a folha
em terços. Se uma folha sair com espaçamento irregular, regerar; não tentar
compensar no recorte.

### Checklist antes de salvar

- [ ] Careca, sem nenhum fio de cabelo — nas 3 vistas
- [ ] Rosto neutro, coerente com as outras folhas
- [ ] Ordem correta: frente, perfil, costas
- [ ] Perfil é 90 graus puro, não 3/4
- [ ] A mesma pose nas 3 vistas
- [ ] Corpo inteiro em todas, pés e cabeça visíveis
- [ ] **As 3 vistas alinhadas, mesma escala, mesma altura**
- [ ] **Mesma altura das folhas anteriores**
- [ ] Espaçamento uniforme entre as vistas
- [ ] Fundo cinza liso, sem sombra projetada
- [ ] Sem texto, linhas de separação ou marcações
- [ ] O tipo de corpo corresponde ao descritor pedido — e é o mesmo nas 3 vistas
- [ ] Nome do arquivo correto (é o contrato com o pipeline)

---

## 7. Folha-mãe

A primeira folha aprovada de cada sexo vira a **folha-mãe** e é anexada em todas as gerações seguintes daquele sexo. Usar `m_b05_d2` (peso normal, definição média) como mãe: fica no meio da grade, servindo de âncora equidistante para os dois extremos.

Guardar em `00_input/sheets/_mother_f.png` e `_mother_m.png`.

Vale investir tempo na folha-mãe — regerar até ficar impecável antes de seguir. Ela define o personagem de toda a biblioteca daquele sexo.

Se a folha-mãe for substituída, **toda a biblioteca daquele sexo precisa ser regerada** — a consistência é relativa a ela.
