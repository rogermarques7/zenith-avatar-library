# Character Bible — Zenith

Documento operacional para gerar as **imagens de referência** no ChatGPT.

A consistência da biblioteca inteira depende deste arquivo. **Não improvisar, não reescrever o bloco fixo, não "melhorar" o texto entre gerações.** Qualquer variação de linguagem produz variação de personagem.

---

## 1. Por que a consistência é resolvível

Três travas eliminam quase toda a variação entre conversas:

1. **Careca, sem cabelo, rosto neutro.** Cabelo e feições são o que a IA mais varia entre gerações. Removê-los elimina a maior fonte de inconsistência — e é exatamente como o avatar já aparece no app hoje.
2. **Bloco fixo literal.** O texto abaixo é colado idêntico em toda geração; só o parágrafo `TIPO DE CORPO` muda.
3. **Imagem-mãe anexada.** A cada nova geração, anexar a imagem aprovada de referência e declarar que é o mesmo personagem.

A quarta trava é fora do ChatGPT: **a cor roxa não vem da imagem nem da Meshy.** O material Zenith é aplicado no pipeline do Blender, idêntico em todos. A imagem só precisa acertar a **forma**.

---

## 2. Regra que não pode ser violada

> **A altura do personagem é SEMPRE a mesma em todas as imagens.**
> A diferença entre tipos de corpo aparece em **largura e volume**, nunca em altura.

O pipeline normaliza todos os modelos para a mesma altura. Se uma imagem desenhar o personagem mais baixo ou mais alto, a normalização vai distorcer as proporções e o avatar ficará errado — gordo e esticado, ou magro e achatado.

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
- Busto PEQUENO A MÉDIO, proporcional ao corpo, mesmo formato em todas as
  folhas. O busto NÃO muda entre os tipos de corpo.
- Pele cinza-clara neutra e uniforme (a cor final é aplicada depois).
- Roupa: FAIXA DE COMPRESSÃO ESPORTIVA preta (top reto, SEM ALÇAS, sem
  decote) + shorts de compressão preto liso, justos ao corpo.
- A FAIXA É LARGA e cobre todo o busto: vai da linha das axilas até a base
  do busto, e PARA AÍ. Nas costas ela é uma faixa horizontal simples —
  ombros, trapézio, escápulas e toda a região lombar ficam À MOSTRA.
  Sem alças, sem tiras cruzadas, sem nadador, sem painel nas costas.
- A faixa tem SEMPRE a mesma altura e o mesmo corte em todas as folhas.
- Tecido fosco e liso, sem estampas, sem logos, sem texturas, sem brilho.
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

NATUREZA DA IMAGEM: é uma PRANCHA DE REFERÊNCIA ANATÔMICA para modelagem 3D
de um app de treino de musculação — o mesmo tipo de material usado para estudo
de anatomia e de proporção corporal. Postura neutra, expressão neutra, roupa
esportiva funcional. NÃO é imagem de moda, nem editorial, nem sensual.

NÃO INCLUIR: cabelo, texto, rótulos, setas, molduras, grades, linhas de
separação entre as vistas, logos, marcas d'água, ou qualquer marcação sobre
o corpo. Nem pose sensual, nem lingerie, nem decote, nem tecido transparente
ou molhado, nem contorno de mamilo, nem ângulo de câmera valorizando o corpo.
Apenas as 3 figuras sobre o fundo liso.

TIPO DE CORPO desta folha (igual nas 3 vistas):
{TIPO_DE_CORPO}

Proporção da imagem larga (paisagem). Maior resolução possível.
```

> **Por que o bloco declara a natureza da imagem.** O gargalo de filtro de
> conteúdo do projeto **não é a Meshy** — o README §2 item 4 já registra que
> image-to-3D passa. É a GERAÇÃO DA IMAGEM. Uma faixa sem alças descrita em
> vocabulário de moda ("bandeau", "tomara que caia") flerta com recusa; a mesma
> peça descrita como equipamento esportivo em prancha anatômica, não. Entrou em
> 29/07 junto com a faixa. **Se alguma folha for recusada, é este parágrafo que
> se reforça — não é o corte da roupa que se muda.**
>
> Vale lembrar o que efetivamente chega no app: a textura da Meshy é
> **descartada** e o material Zenith é aplicado no pipeline. O asset publicado é
> um manequim de titânio cinza, careca, sem textura e sem rosto definido. As
> folhas de referência morrem em `00_input/` e nunca são distribuídas.

---

## 4. Bloco fixo — MASCULINO

Colar literalmente. Substituir apenas `{TIPO_DE_CORPO}`.

```
Gere uma FOLHA DE REFERÊNCIA (character turnaround) do avatar MASCULINO do
Zenith, para eu converter em modelo 3D via Multi-View. UMA imagem contendo
3 vistas do MESMO personagem, lado a lado, na ordem exata:
FRENTE | PERFIL LATERAL (o personagem olhando para a esquerda da imagem) | COSTAS.
É SEMPRE o mesmo personagem — só o tipo de corpo muda entre as folhas.

PERSONAGEM (idêntico em todas as imagens):
- Homem, CARECO, sem nenhum cabelo.
- Rosto neutro e liso, feições suaves e genéricas, sem expressão marcante,
  sem detalhes faciais fortes.
- Pele cinza-clara neutra e uniforme (a cor final é aplicada depois).
- Roupa: apenas shorts de compressão preto liso, justo, torso nu, sem
  estampas, sem logos, sem texturas.
- Sem calçados, sem acessórios, sem joias.

POSE E ENQUADRAMENTO (idêntico nas 3 vistas e em todas as folhas):
- A-pose neutra: em pé, ereto, braços afastados do corpo cerca de 40 graus,
  palmas viradas para dentro, pernas na largura dos ombros.
- A MESMA pose exata nas 3 vistas — apenas o ângulo da câmera muda, o corpo
  não se mexe entre as vistas.
- O perfil lateral é um perfil PURO de 90 graus, nunca 3/4.
- Corpo INTEIRO visível, da cabeça aos pés, em TODAS as 3 vistas.
- As 3 vistas na MESMA ESCALA e ALINHADAS: topo da cabeça e sola dos pés na
  mesma altura horizontal nas três.
- Câmera reta, ortográfica, na altura do peito, na mesma altura nas 3 vistas.
  Sem perspectiva, sem distorção de lente, sem close, sem inclinação.
- O personagem ocupa sempre a MESMA ALTURA em todas as folhas geradas.
- Espaçamento uniforme entre as 3 vistas, cada uma centralizada no seu terço
  da imagem.

ALTURA (regra crítica):
- A altura do personagem é SEMPRE A MESMA. A diferença entre os tipos de
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

## 5. Descritores de tipo de corpo

Colar no slot `{TIPO_DE_CORPO}`. Um por arquétipo.

### Feminino — 32 arquétipos

> **Reescrito em 28/07/2026, de 6 faixas para 12.** Os 17 descritores antigos
> (`f_b1`…`f_b6`) foram **substituídos**, não renumerados: uma faixa de 6 cobria
> ~5 pontos de IMC e virou duas ou três de 1,5. Nenhum deles foi produzido, então
> não há asset órfão. Grade em `docs/ARCHETYPES.md` §3b.

Produzir **nesta ordem**, um nível de definição por vez. Cada folha usa a
anterior como referência anexa. A folha-mãe é `f_b05_d2` e precisa estar
aprovada antes de qualquer outra.

**O que muda em relação aos descritores masculinos** — vale para os 32:

- O eixo dominante da silhueta feminina é **quadril e cintura**, não ombros e
  peitoral. Todo descritor diz explicitamente o que acontece com o quadril, a
  cintura e os glúteos; sem isso o modelo desenha um homem mais magro.

  > **Não peça "quadril CLARAMENTE mais largo que os ombros" — foi erro meu na
  > 1ª redação, corrigido em 28/07 depois de medir.** Em mulher real o ombro e o
  > quadril têm quase a mesma largura; o que lê como feminino é o **contraste da
  > cintura**, não um quadril maior. Medido na folha-mãe `f_b05_d2` contra a
  > `_mother_m.png` aprovada, mesma régua: ombro **23,5%** da altura contra
  > 27,1% do masculino · quadril **24,3%** contra 24,0% (praticamente igual em
  > absoluto) · cintura **14,8%** contra 17,4% · **cintura/quadril 0,607 contra
  > 0,724**. Ou seja: o feminino aparece porque o **ombro encolheu e a cintura
  > afinou** com o quadril parado, não porque o quadril cresceu. Pedir quadril
  > exagerado empurraria as folhas para uma proporção de desenho animado.
- **O busto é anexado ao bloco fixo, não ao descritor** (§3): "busto pequeno a
  médio, proporcional ao corpo, mesmo formato em todas as folhas". É uma fonte
  de deriva grande e não é o que o app mede — travar em vez de descrever 32 vezes.
- **A roupa de cima é uma FAIXA RETA sem alças** (§3), e isso é decisão de
  produto, não de estilo — ver o quadro abaixo.

> ### 🔑 Por que faixa reta e não top nadador (29/07/2026)
>
> A 1ª folha-mãe voltou com um **racerback largo**, e o Rogério reprovou no olho:
> "esconde muito a musculatura das costas". Medida a cobertura por região no
> recorte de costas, ele estava certo — e o número é pior do que parece, porque
> nas costas os braços entram na largura e **diluem** a conta:
>
> | região | coberta pelo racerback |
> |---|---:|
> | trapézio / ombro | 21,3% |
> | escápulas / rombóides | 37,7% |
> | **dorsal alto (o "V")** | **60,7%** |
> | lombar | 0,4% |
>
> Mais da metade do dorsal alto — o músculo que faz a silhueta em V, e o avatar
> **gira** no app. Pior: os descritores `f_b06_d3`, `f_b08_d3` e `f_b09_d3`
> pedem "dorsais visíveis / desenvolvidos / largos". Com aquele top, **a linha
> d3 inteira perderia de costas justamente o que a distingue.**
>
> **O segundo motivo é topológico e vale mais que o primeiro.** A faixa reta é a
> única opção cuja borda é um **anel fechado** — duas bordas horizontais dando a
> volta no tronco, idênticas em forma ao cós e à bainha do short. Alça de
> racerback sobe pelo ombro, cruza a escápula e some: não tem volta, não tem
> simetria de revolução, e passa em cima da região de mais relevo. Seria o
> problema do short **sem** a propriedade que tornou o short solúvel (lição nº 1
> da sessão 4: *"a bainha dá a VOLTA no membro; o sulco de músculo cobre um
> arco"*).
>
> Bônus de paridade: o masculino é torso nu + short. Faixa + short é o mesmo
> sistema visual, não duas linguagens.
- O ganho de gordura feminino vai primeiro para **quadril, culote e coxas**, e só
  depois para a barriga. Nas bandas `b04`–`b08` isso é o que separa a linha
  feminina da masculina, e está escrito em cada descritor.

#### d1 — definição baixa (12) · > 29% de gordura

| ID | Descritor |
|---|---|
| `f_b01_d1` | Extremamente magra. Clavícula, costelas e escápulas aparentes, membros muito finos, ombros estreitos, quadril estreito, abdômen côncavo, glúteos sem volume, nenhuma massa muscular. |
| `f_b02_d1` | Muito magra e sem tônus. Costelas levemente visíveis, braços e pernas finos e moles, quadril estreito, barriga plana e lisa, silhueta praticamente reta. |
| `f_b03_d1` | Magra sem definição nenhuma. Corpo liso e mole, braços e pernas finos sem tônus, cintura pouco marcada, glúteos pequenos e sem forma. |
| `f_b04_d1` | Magra "skinny-fat": esbelta porém mole. Pequena camada de gordura na barriga baixa, coxas macias, quadril levemente arredondado, nenhum tônus muscular. Arquétipo da mulher sedentária de peso normal. |
| `f_b05_d1` | Peso normal, corpo mole. Leve barriga baixa, gordura acumulada no quadril e na parte interna das coxas, cintura pouco marcada, braços sem tônus. |
| `f_b06_d1` | Peso normal alto. Barriga levemente saliente, quadril e coxas arredondados, cintura larga, contornos macios, nenhum tônus muscular. |
| `f_b07_d1` | Sobrepeso leve. Barriga saliente sobre a linha da cintura, culote no quadril, coxas grossas e macias, braços cheios, cintura pouco definida. |
| `f_b08_d1` | Sobrepeso. Barriga claramente proeminente, quadril largo, coxas espessas que se tocam, braços cheios e moles, pescoço mais grosso. |
| `f_b09_d1` | Sobrepeso alto. Barriga grande e arredondada, dobra visível na cintura, quadril e coxas muito volumosos, ombros arredondados. |
| `f_b10_d1` | Obesidade grau I. Abdômen grande e proeminente, quadril e coxas muito volumosos, braços grossos, pescoço curto, silhueta totalmente arredondada. |
| `f_b11_d1` | Obesidade grau II. Corpo muito volumoso, abdômen muito grande, dobras visíveis no tronco, quadril muito largo, membros muito espessos. |
| `f_b12_d1` | Obesidade grau III. Corpo extremamente volumoso, abdômen enorme e pendente, dobras acentuadas, pescoço muito curto, membros muito grossos. |

#### d2 — definição média (11) · 21–29% de gordura

| ID | Descritor |
|---|---|
| `f_b01_d2` | Muito magra com leve tônus. Membros finos com contorno muscular sutil, sem volume, abdômen plano e liso, ombros e quadril estreitos, silhueta reta. |
| `f_b02_d2` | Magra com tônus leve. Contorno suave em braços e pernas, abdômen plano sem gomos, cintura marcada, aparência saudável mas não atlética. |
| `f_b03_d2` | Magra e levemente atlética. Ombros com forma discreta, coxas e glúteos com leve tônus, abdômen plano sem gomos, cintura fina. |
| `f_b04_d2` | Peso normal com tônus. Glúteos e coxas com forma, braços sutilmente definidos, abdômen plano, cintura marcada, quadril tão largo quanto os ombros. |
| `f_b05_d2` | **FOLHA-MÃE.** Peso normal e atlética, aparência saudável e ativa. Ombros com forma clara, glúteos e coxas torneados, quadril tão largo quanto os ombros e cintura bem mais fina que os dois. Abdômen **PLANO e LISO, SEM gomos abdominais visíveis, SEM linha alba marcada, SEM separação muscular**. Percentual de gordura médio, cerca de 25%: musculatura com forma, mas coberta por uma camada leve de gordura. **NÃO é um físico de atleta seca nem de modelo fitness.** |
| `f_b06_d2` | Peso normal alto com musculatura. Volume muscular moderado coberto por leve camada de gordura, quadril e coxas cheios, abdômen sem definição, cintura pouco marcada. |
| `f_b07_d2` | Sobrepeso leve com musculatura por baixo. Ombros e costas largos, coxas e glúteos volumosos e fortes, barriga leve, força evidente sob a gordura. |
| `f_b08_d2` | Sobrepeso com boa massa muscular. Tronco largo e espesso, barriga presente, braços e coxas grossos, quadril largo, sem definição visível. |
| `f_b09_d2` | Corpo grande e forte. Ombros muito largos, musculatura evidente sob camada de gordura, barriga proeminente, quadril e coxas muito volumosos. |
| `f_b10_d2` | Obesidade grau I com força. Físico de powerlifter feminina: estrutura muito larga, massa muscular alta sob a gordura, abdômen grande, coxas enormes. |
| `f_b11_d2` | Obesidade grau II com força. Corpo enorme e pesado, costas e ombros muito largos, força visível apesar do volume de gordura. |

#### d3 — definição alta (9) · < 21% de gordura

| ID | Descritor |
|---|---|
| `f_b02_d3` | Magra e muito seca, IMC ~19: corpo esguio, **ombros estreitos, membros finos, quadril estreito**. Percentual de gordura muito baixo revelando os músculos que já existem — gomos abdominais visíveis, serrátil aparente. **NÃO adicionar massa muscular**, sem volume de fisiculturista e sem glúteo de atleta: é uma magra definida, não uma atleta cheia. *(Herdado do piloto masculino: a 1ª geração da banda equivalente saiu volumosa demais copiando a massa da mãe `d2`. Nesta banda, anexar SÓ o vizinho e largar a folha-mãe — ver §6.)* |
| `f_b03_d3` | Magra e definida. Abdômen com gomos marcados, ombros e braços desenhados, glúteos firmes porém pequenos, cintura muito fina, pouca massa muscular. |
| `f_b04_d3` | Atlética e definida. Gomos abdominais claros, ombros desenhados, coxas e glúteos torneados com separação muscular visível, cintura fina. |
| `f_b05_d3` | Musculosa e definida. Físico de atleta fitness: ombros e costas desenhados, glúteos e coxas com volume e separação, abdômen com gomos evidentes. |
| `f_b06_d3` | Bem musculosa e seca. Ombros largos, dorsais visíveis, quadríceps com separação clara, abdômen definido, veias aparentes nos braços. |
| `f_b07_d3` | Muito musculosa. Massa alta com baixa gordura, ombros muito largos, braços e coxas volumosos, abdômen definido, cintura estreita. |
| `f_b08_d3` | Físico de fisiculturista feminina. Massa muscular alta, dorsais desenvolvidos, cintura estreita em relação aos ombros e ao quadril, abdômen definido. |
| `f_b09_d3` | Fisiculturista pesada. Volume muscular muito alto, dorsais largos, braços e coxas muito desenvolvidos, definição mantida. |
| `f_b10_d3` | Fisiculturista de grande porte. Massa muscular extrema, estrutura enorme, ombros e coxas muito volumosos, abdômen ainda definido. |

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
| `m_b05_d2` | Peso normal e atlético, aparência saudável e ativa. Peitoral e ombros com forma clara, braços com volume moderado. Abdômen PLANO e LISO, SEM gomos abdominais visíveis, SEM serrátil aparente, SEM separação muscular marcada. Percentual de gordura médio, cerca de 17%: musculatura com forma, mas coberta por uma camada leve de gordura. NÃO é um físico de atleta seco. |
| `m_b06_d2` | Peso normal alto com musculatura. Volume muscular moderado coberto por leve camada de gordura, ombros largos, abdômen sem definição. |
| `m_b07_d2` | Sobrepeso leve com musculatura por baixo. Ombros e costas largos, barriga leve, braços grossos, força evidente sob a gordura. |
| `m_b08_d2` | Sobrepeso com boa massa muscular. Tronco largo e espesso, barriga presente, braços e pernas grossos, sem definição visível. |
| `m_b09_d2` | Corpo grande e forte. Ombros muito largos, musculatura evidente sob camada de gordura, barriga proeminente, membros muito grossos. |
| `m_b10_d2` | Obesidade grau I com força. Físico de powerlifter: estrutura muito larga, massa muscular alta sob a gordura, abdômen grande. |
| `m_b11_d2` | Obesidade grau II com força. Corpo enorme e pesado, costas e ombros muito largos, força visível apesar do volume de gordura. |

#### d3 — definição alta (9)

| ID | Descritor |
|---|---|
| `m_b02_d3` | Magro e muito seco, IMC ~19: corpo esguio, **ombros estreitos, membros finos**. Percentual de gordura muito baixo revelando os músculos que já existem — gomos abdominais visíveis, serrátil aparente, músculos desenhados. **NÃO adicionar massa muscular**, sem volume de fisiculturista: é um magro definido, não um atleta cheio. (Piloto: a 1ª geração saiu volumosa demais herdando a massa da mãe `d2`; o negativo precisa ser forte.) |
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
2. **Em geral duas imagens anexas**: a folha-mãe (`m_b05_d2`) e a última folha aprovada. **Exceção:** quando o alvo é bem mais magro/menos musculoso que a mãe, anexar só o vizinho e largar a mãe — senão o modelo copia a musculatura dela (ver §6, item 2).
3. **Gerar em sequência pela grade**, para que a folha anterior seja sempre o vizinho imediato.
4. Ao abrir conversa nova, reanexar as duas imagens e colar o bloco fixo. Nada mais é necessário — **cada geração é autossuficiente**.
5. Se derivar: `mantenha o personagem idêntico às imagens anexas`. Se insistir, encerra a conversa e abre outra — é mais rápido que brigar com o contexto.
6. Se a folha sair com altura diferente das anteriores, **descartar sem tentar aproveitar**. Altura é o único erro que o pipeline não consegue corrigir.

---

## 5c. Controle do TAMANHO do passo

Consistência de personagem e tamanho do degrau entre bandas são problemas diferentes. O §5b resolve o primeiro; esta seção, o segundo. Vale para qualquer linha, mas foi aprendida na d3.

**1. Adjetivo de intensidade não controla o passo.** "Passo contido", "~10% mais massa", "não o dobro" — o mesmo texto produz degraus diferentes em gerações diferentes. Não é parâmetro, é sugestão.

**2. Bracketing: dar a escala por exemplo.** Anexar **duas** folhas consecutivas já aprovadas e pedir *"gere a próxima etapa desta sequência, com um passo do MESMO TAMANHO do que separa a primeira da segunda"*. O modelo mede o degrau nas imagens em vez de interpretar um advérbio. Duas vezes seguidas entregou o passo pedido (b04_d3 g2, b05_d3 de primeira). **É o padrão, não o plano B.**

**3. Identificar os anexos por CONTEÚDO, nunca por ordem ou nome.** Não dá para contar que o modelo veja o nome do arquivo, e a ordem de upload ele confunde. Escrever *"uma das folhas é visivelmente menos musculosa: essa é a etapa anterior"* e pedir que **ele confirme qual é qual antes de gerar**. Custa uma linha e você vê o erro antes de gastar a geração.

> Marca d'água na folha **não** resolve isso e é proibida: o texto vira uma 4ª mancha sobre o fundo liso e quebra a detecção de figuras do `crop.py`, além de poder chegar na Meshy como geometria. Se quiser rótulo visível, rotular uma **cópia** fora de `00_input/sheets/`.

**4. Interpolação não funciona melhor que extrapolação.** Tentou-se, no b06_d3, pedir o meio-termo exato entre duas imagens anexas. Voltou o mesmo corpo da folha maior. O modelo não desenha o que está entre dois pontos só porque os dois estão à vista.

**5. Duas gerações no mesmo ponto = atrator. Antes de aceitar, TROQUE O ATRATOR.** O modelo tem atratores (o "musculoso e seco" ~32 de ombro, o "obeso ~40% de barriga") e cai neles independente do pedido. Quando duas tentativas medem praticamente igual, o problema não é a folha — mas também **nem sempre é o teto da ferramenta**.

O que **não** tira o corpo de um atrator: adjetivo de intensidade ("bem mais musculoso"), número relativo ("~10% mais massa") e **interpolação** (item 4).

O que tira: **trocar o substantivo de categoria do pedido.** No `b07_d3` a d3 parecia saturada em ~32; escrever *"este corpo é um FISICULTURISTA DE COMPETIÇÃO, não um homem musculoso e seco de academia"* — junto de declarar que a definição já está no teto e **o que cresce é só VOLUME** (deltoides, peitoral, dorsais, braço/coxa, cintura estreita constante) — levou o mesmo pipeline a 36,7 de primeira. O modelo não estava no limite; estava em outra categoria.

**Ordem correta:** (1) bracketing (item 2) · (2) trocar de atrator por nome de categoria · (3) só então declarar saturação, aceitar e seguir.

**Ressalva:** trocar de atrator controla a **direção**, não o **tamanho** — o b07 saiu com o dobro do passo pedido. Contar com overshoot: medir sempre e registrar o salto como candidato a avatar intermediário futuro, que é inserção e não retrabalho.

**6. O bracketing entrega ~2× o passo pedido. Medido, não estimado.** Três amostras, duas linhas, duas direções opostas:

| pedido (passo do par-âncora) | entregue | fator |
|---|---|---|
| b07_d3 — 3,7 de IMC | +8,3 | 2,2× |
| b06h_d3 — 3,7 de IMC | +7,2 | 1,9× |
| b05h_d1 — 2,6 de barriga | +5,1 | 2,0× |

Vale tanto para "ganhar músculo" quanto para "ganhar gordura", então é comportamento do modelo, não da linha. **Ao planejar um alvo, contar com o dobro** — e, na prática, esperar que o corpo caia **perto do vizinho de CIMA** do vão, não no meio dele.

> **⚠️ O fator 2× só vale em ESPAÇO ABERTO.** Quando o alvo cai entre uma âncora e um **atrator forte**, o atrator vence e o passo explode. Medido: `b05i_d1` pediu passo 1,6 de IMC mirando ~31 e entregou **+12,9** (8×), aterrissando em 40,7 — em cima do atrator obeso, acima do próprio vizinho superior do vão. **Nessa situação o tamanho do passo não é controlável por nenhuma formulação testada.** Ver item 8.

**8. As LACUNAS são o negativo dos ATRATORES *daquele gerador* — a ferramenta é TROCAR DE GERADOR, não reformular o prompt.** A faixa de IMC 28–38 na linha d1 ficou vazia porque o **ChatGPT** não gera corpos ali: salta de ~28 direto para ~39–41. Três tentativas com formulações diferentes confirmaram. Dentro de um mesmo gerador, nenhuma redação tira o corpo do atrator — isso continua valendo.

**Mas o buraco não era do problema, era do ChatGPT.** O mesmo prompt e as mesmas referências, rodados no **Gemini**, entregaram IMC 34,0 de primeira — dentro do vão 27,8→38,8 e perto do meio dele (`zen_m_b05j_d1`, 27/07). Foi a única técnica que funcionou depois que bracketing, troca de categoria e interpolação se esgotaram. O overshoot ~2× do item 6 **sobreviveu** à troca (pediu ~3,2, entregou +6,2): o que muda entre geradores é **onde ficam os atratores**, não o fator de passo.

**Ordem revista quando um alvo não sai:** (1) bracketing · (2) trocar de atrator por nome de categoria · (3) **trocar de gerador** · (4) só então declarar saturação e cobrir o resto por **shape keys** no sistema híbrido (os insumos, `circumferences_cm`, já viajam no `library.json`).

> **⚠️ Operacional do Gemini — ele carimba um selo (estrelinha) no canto inferior direito.** O `crop.py` **não** acusa: o selo cai dentro da coluna de uma das vistas em vez de virar uma 4ª figura, passa batido e chega na Meshy como mancha sobre o fundo liso. **Isso é trabalho do `scripts/intake.py`, que roda antes do `crop.py` e apaga o selo sozinho** (cobre com retalho de fundo limpo e confere o resíduo) — não pedir para o humano apagar à mão. Nas duas folhas medidas o selo saiu no MESMO lugar, `x 2464–2559`. A pose do Gemini também é mais fechada (braços mais colados ao corpo), o que faz o `measure.py` **subestimar** a barriga em relação à série do ChatGPT — mais um motivo para decidir no `metrics.py`.

**10. QUEM ESCOLHE O ATRATOR É O SUBSTANTIVO DE CATEGORIA; a âncora só ajusta dentro dele.** Medido na linha d1 do Gemini, três folhas mirando o mesmo vão (27,8→33,3):

| folha | âncora de topo | substantivo do descritor | pouso |
|---|---|---|---:|
| `b05j_d1` | 27,8 | obesidade | 34,0 |
| `b05k_d1` | **24,4** | "OBESIDADE GRAU I" | 33,3 |
| `b05m_d1` | **20,4** | **"SOBREPESO, não obeso"** | **26,9** |

Baixar a âncora em 3,4 moveu o pouso **0,7**. Trocar o substantivo moveu **6,4** — e passou do alvo por baixo. Consequência prática: **um vão é o vazio entre dois atratores nomeáveis do gerador.** Se não existe palavra de categoria entre os dois (aqui: nada entre "sobrepeso" ~27 e "obesidade grau I" ~33,5), nenhuma âncora e nenhum adjetivo colocam corpo ali — trocar de gerador (item 8) ou cobrir por shape keys. Três gerações foram gastas nesse vão antes de aceitar; não repetir.

**9. Para pares de âncoras MUITO parecidas, não peça identificação.** Pedir "diga qual é a etapa mais recente" convida ao erro quando os dois corpos são próximos (e as folhas podem até sugerir a ordem inversa da real — ver a limitação de braço do `measure.py`). Em vez disso: *"gere um corpo mais pesado que os DOIS anexos, com um passo do tamanho da diferença entre eles"*. Dispensa a ordenação e a direção sai correta.

**7. RESOLVIDO — a metade baixa de um buraco se alcança com ÂNCORA BAIXA, e o pouso se prevê por SOMA.**

Era a lição mais resignada do documento ("cada inserção cai no topo do vão, é limite do método"). Estava errada, e o erro era supor que o passo entregue fosse proporcional ao passo pedido. Não é: **o modelo tem um passo MÍNIMO e ignora pedidos menores que ele.**

A regra que prevê o pouso é **aditiva**: `pouso ≈ âncora de topo + 6,5 de IMC`, quase independente do que se pede. Seis amostras, dois geradores, duas linhas — os deltas ficam em +6,2 · +7,2 · +8,1 · +8,3 (fora dois casos: captura por atrator, +12,9; e uma folha cuja medida 2D falhou). Fator multiplicativo não prevê nada: as mesmas amostras dão de 1,9× a 8,0×.

**Como usar: para mirar IMC X, escolher o par cujo membro SUPERIOR esteja em ~X−6,5** — mesmo que esse par esteja bem abaixo do buraco, e não seja o par adjacente a ele.

> **⚠️ A regra aditiva quebra em cima de um atrator, igual ao fator multiplicativo.** No `zen_m_b06i_d3` o delta foi **+3,3** em vez de +6,5 (âncora de topo 23,7 → pouso 27,0), porque o descritor nomeava o atrator "musculoso e seco de academia" e negava a saída ("NÃO um fisiculturista") — o oposto do que o item 5 manda. Amostras da d3: +7,2 · +8,3 · +3,3. **Antes de aplicar a regra, conferir se o descritor não está apontando para um atrator conhecido.**

Comprovado no `zen_m_b05h_d2` (27/07): vão d2 de 26,7→35,0. O par adjacente (`b04_d2`+`b05_d2`, topo 26,7) teria pousado em ~33, no topo do vão, como sempre. Usando um par mais baixo (`b02_d2`+`b04_d2`, topo **22,5**) o corpo caiu em **30,6 — abaixo do ponto médio do vão**, coisa que nenhuma inserção anterior tinha conseguido. O vão saiu da lista `high`.

---

## 6. Procedimento por imagem

1. Nova conversa (ou a mesma — o bloco fixo protege os dois jeitos).
2. **Anexar DUAS imagens**: a folha-mãe do sexo *e* a última folha aprovada (o vizinho imediato na grade).
   > **Exceção — às vezes NÃO anexar a folha-mãe é a solução.** A folha-mãe `m_b05_d2`
   > é um corpo atlético. Quando o arquétipo-alvo é bem mais magro/menos musculoso que
   > ela (ex.: trecho magro da linha d2, `b01`–`b04`), o modelo copia a musculatura da
   > mãe — ombros largos, peitoral e costas desenvolvidos — e o avatar sai musculoso
   > demais, quebrando a continuidade com o vizinho slim. Nesses casos, anexar **só o
   > vizinho imediato** (que já carrega a identidade) e largar a mãe. Não custa
   > consistência: a altura vem do bloco fixo e a deriva facial é irrelevante
   > (careca/roxo). A mãe volta a ser âncora útil quando a banda-alvo se aproxima ou
   > passa do corpo dela (`b05`+). Ver `state.md` (lição d2). Confirmado na produção
   > (b03_d2 e b04_d2 só fecharam ao largar a mãe).
3. Colar o bloco fixo com o descritor do arquétipo no slot.
4. Se o resultado divergir do personagem: responder `mantenha o personagem idêntico à imagem anexa — mesmo rosto, mesma careca, mesma roupa, mesma altura`.
5. Se as vistas divergirem entre si: `mantenha o personagem idêntico à vista frontal nas outras duas vistas`.
6. Conferir contra o checklist abaixo.
7. **Baixar e deixar em Downloads. Não salvar à mão no repositório.** O Claude
   Code roda `python scripts/intake.py {id}`: pega a imagem mais recente do
   Downloads, apaga o selo do Gemini, grava em `00_input/sheets/{id}_sheet.png`
   e se recusa a sobrescrever folha existente.

O recorte em três imagens é feito por script (`scripts/crop.py`), não à mão.
Ele detecta as 3 figuras por diferença de fundo e recorta cada uma com margem
uniforme. Por isso o espaçamento uniforme entre as vistas é obrigatório — se as
figuras estiverem grudadas ou muito irregulares, a detecção falha. Se uma folha
sair com espaçamento irregular, regerar; não tentar compensar no recorte.

> **Direção do perfil não reprova a folha.** O bloco fixo pede o perfil virado
> para um lado, mas modelos de imagem têm discriminação ruim de lateralidade e
> às vezes viram para o outro. O piloto confirmou que a Meshy gera bem com o
> perfil em qualquer direção — o que importa é ser 90° puro, não 3/4. Não
> regerar só por causa do lado.

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

A primeira folha aprovada de cada sexo vira a **folha-mãe** e é anexada em todas as gerações seguintes daquele sexo. Usar a banda `b05_d2` (peso normal, definição média) como mãe — `m_b05_d2` no masculino, **`f_b05_d2` no feminino**: fica no meio da grade, servindo de âncora equidistante para os dois extremos.

> **A folha-mãe feminina não herda nada da masculina.** Não anexar `_mother_m.png`
> ao gerar `f_b05_d2`: são personagens diferentes, e a única coisa que precisa ser
> comum entre os sexos é o **enquadramento** — altura, pose, câmera, fundo —, que
> vem do bloco fixo e não de imagem anexa. Anexar a mãe masculina só arrastaria
> ombro e peitoral para a silhueta feminina.

Guardar em `00_input/sheets/_mother_f.png` e `_mother_m.png`.

Vale investir tempo na folha-mãe — regerar até ficar impecável antes de seguir. Ela define o personagem de toda a biblioteca daquele sexo.

Se a folha-mãe for substituída, **toda a biblioteca daquele sexo precisa ser regerada** — a consistência é relativa a ela.