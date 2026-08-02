# Bloco de prompt — FEMININO

> ⚠️ **COLAR LITERAL. Não reescrever, não "melhorar", não improvisar.** Qualquer
> variação de linguagem produz variação de personagem, e a consistência da
> biblioteca inteira depende deste texto ser idêntico em toda geração.
>
> **Este arquivo é a FONTE ÚNICA do bloco fixo feminino.** O
> `docs/CHARACTER_BIBLE.md` aponta para cá e não guarda uma segunda cópia — duas
> cópias divergiriam.
>
> **O PORQUÊ de cada linha está no `CHARACTER_BIBLE.md`** (§1 travas de
> consistência · §3/§4 razão do bloco · §5 razão dos descritores · §5b anti-deriva
> · §5c controle do tamanho do passo). Abrir de lá **quando a decisão for sobre o
> método**; para montar um prompt, este arquivo basta.

## Bloco fixo — substituir apenas `{TIPO_DE_CORPO}`

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

## Descritores — colar um no slot `{TIPO_DE_CORPO}`

### d1 — definição baixa (12) · > 29% de gordura
| ID | Descritor |
|---|---|
| `f_b01_d1` | Extremamente magra. Clavícula, costelas e escápulas aparentes, membros muito finos, ombros estreitos, quadril estreito, abdômen côncavo, glúteos sem volume, nenhuma massa muscular. |
| `f_b02_d1` | Muito magra e sem tônus. Costelas levemente visíveis, braços e pernas finos e moles, quadril estreito, barriga plana e lisa, silhueta praticamente reta. |
| `f_b03_d1` | Magra sem definição nenhuma. Corpo liso e mole, braços e pernas finos sem tônus, cintura pouco marcada, glúteos pequenos e sem forma. |
| `f_b04_d1` | Magra "skinny-fat": esbelta porém mole. Pequena camada de gordura na barriga baixa, coxas macias, quadril levemente arredondado, nenhum tônus muscular. Arquétipo da mulher sedentária de peso normal. |
| `f_b05_d1` | Peso normal, corpo mole. Leve barriga baixa, gordura acumulada no quadril e na parte interna das coxas, cintura pouco marcada, braços sem tônus. |
| `f_b04i_d1` | *(inserção da sessão 18, mediu **26,5** — fechou o vão 24,1 → 31,9. **Não é um descritor de categoria: é o lever-âncora isolado**, ver §2.4e)* Mulher comum, SEDENTÁRIA, sem nenhum tônus muscular. É EXATAMENTE O MESMO TIPO DE CORPO da folha anexada, porém MAIS LEVE e MENOS VOLUMOSO — não é outro personagem nem outro estilo de corpo, é a mesma mulher alguns quilos abaixo, no COMEÇO do sobrepeso. **O que MUDA em relação à folha anexada:** a barriga é MENOR (continua macia e saliente sobre o cós, mas claramente MENOS projetada na vista de perfil); o quadril é MENOS LARGO, com culote mais discreto; as coxas são MENOS GROSSAS e se tocam apenas no alto da virilha; os braços são MENOS CHEIOS, e o tríceps cai menos. **O que NÃO MUDA:** a ausência TOTAL de tônus muscular (nenhum músculo desenhado, nenhum gomo abdominal, nenhuma separação); os contornos todos redondos, macios e lisos; a cintura sem nenhum afunilamento marcado; os ombros arredondados e levemente caídos. Ela está ACIMA DO PESO e continua acima do peso — apenas menos que a folha anexada. Ela NÃO é magra, NÃO é atlética e NÃO é obesa. **Âncora `zen_f_b07_d1` (31,9), descendo.** |
| `f_b06_d1` | Mulher de PESO NORMAL ALTO, sem nenhum tônus muscular. Barriga levemente saliente e macia, quadril e coxas arredondados, cintura larga e pouco definida, braços macios. Contornos todos suaves e arredondados. Ela NÃO é obesa e NÃO tem sobrepeso marcado: é apenas uma mulher comum, no limite superior do peso normal, sem nenhum treino. |
| `f_b07_d1` | Sobrepeso leve. Barriga saliente sobre a linha da cintura, culote no quadril, coxas grossas e macias, braços cheios, cintura pouco definida. |
| `f_b08_d1` | Sobrepeso. Barriga claramente proeminente, quadril largo, coxas espessas que se tocam, braços cheios e moles, pescoço mais grosso. |
| `f_b09_d1` | Sobrepeso alto. Barriga grande e arredondada, dobra visível na cintura, quadril e coxas muito volumosos, ombros arredondados. |
| `f_b10_d1` | *(usado, mediu **55,1** — o rótulo mente sobre a banda)* Mulher OBESA NO COMEÇO DA OBESIDADE, sedentária, sem nenhum tônus muscular — o corpo de quem está claramente acima do peso mas ainda anda normalmente, trabalha em pé e sobe escada sem ajuda. Abdômen grande, arredondado e macio, saliente por cima do cós do short. Quadril muito largo, culote marcado nos lados, coxas espessas que se tocam desde a virilha. Braços cheios e moles, com o tríceps caído. Ombros arredondados e caídos, pescoço mais curto e grosso, papada leve. Cintura sem nenhum afunilamento. Contornos todos redondos, macios e lisos. Ela NÃO É OBESA MÓRBIDA: sem avental abdominal pendente, sem dobras caindo sobre as coxas. |
| `f_b11_d1` | Obesidade grau II. Corpo muito volumoso, abdômen muito grande, dobras visíveis no tronco, quadril muito largo, membros muito espessos. |
| `f_b12_d1` | Obesidade grau III. Corpo extremamente volumoso, abdômen enorme e pendente, dobras acentuadas, pescoço muito curto, membros muito grossos. |

### d2 — definição média (11) · 21–29% de gordura
| ID | Descritor |
|---|---|
| `f_b01_d2` | Muito magra com leve tônus. Membros finos com contorno muscular sutil, sem volume, abdômen plano e liso, ombros e quadril estreitos, silhueta reta. |
| `f_b02_d2` | Magra com tônus leve. Contorno suave em braços e pernas, abdômen plano sem gomos, cintura marcada, aparência saudável mas não atlética. |
| `f_b03_d2` | *(usado na sessão 18, mediu **19,8** — alvo era ~20)* BAILARINA CLÁSSICA DE COMPANHIA PROFISSIONAL — a dançarina de balé de repertório, com o corpo construído por anos de barra, sapatilha de ponta e alongamento. É um físico julgado por LINHA e LEVEZA, nunca por volume muscular. Corpo LONGO, ESTREITO e ENXUTO. Ombros estreitos e finos. Braços longos e delgados, com contorno suave e nenhuma massa. Costas com musculatura fina e alongada, escápulas de contorno visível. Cintura muito fina. Abdômen PLANO e LISO, firme, SEM gomos abdominais visíveis e SEM separação muscular. Quadril estreito. Glúteos pequenos, altos e firmes. Coxas longas e finas, com quadríceps e adutores de contorno nítido porém ENXUTO, sem volume; panturrilhas pequenas e bem desenhadas; tornozelos finos. Percentual de gordura na faixa média, cerca de 22%: a musculatura tem forma, mas fica coberta por uma camada leve de gordura — nada de aparência seca ou vascularizada. O músculo dela aparece pelo DESENHO e pelo alongamento, nunca pelo tamanho. Ela NÃO tem corpo de academia, NÃO é fisiculturista e NÃO é atleta de força. **Âncora `zen_f_b04_d2` (22,2), descendo — não a de 18,3.** *(Substituiu a string de adjetivo "Magra e levemente atlética…", que era inerte: em 30/07 devolveu a âncora reescalada, razões paradas, §1.4b.)* |
| `f_b04_d2` | Peso normal com tônus. Glúteos e coxas com forma, braços sutilmente definidos, abdômen plano, cintura marcada, quadril tão largo quanto os ombros. |
| `f_b05_d2` | **FOLHA-MÃE.** Peso normal e atlética, aparência saudável e ativa. Ombros com forma clara, glúteos e coxas torneados, quadril tão largo quanto os ombros e cintura bem mais fina que os dois. Abdômen **PLANO e LISO, SEM gomos abdominais visíveis, SEM linha alba marcada, SEM separação muscular**. Percentual de gordura médio, cerca de 25%: musculatura com forma, mas coberta por uma camada leve de gordura. **NÃO é um físico de atleta seca nem de modelo fitness.** |
| `f_b06_d2` | Peso normal alto com musculatura. Volume muscular moderado coberto por leve camada de gordura, quadril e coxas cheios, abdômen sem definição, cintura pouco marcada. |
| `f_b07_d2` | Sobrepeso leve com musculatura por baixo. Ombros e costas largos, coxas e glúteos volumosos e fortes, barriga leve, força evidente sob a gordura. |
| `f_b08_d2` | Sobrepeso com boa massa muscular. Tronco largo e espesso, barriga presente, braços e coxas grossos, quadril largo, sem definição visível. |
| `f_b09_d2` | Corpo grande e forte. Ombros muito largos, musculatura evidente sob camada de gordura, barriga proeminente, quadril e coxas muito volumosos. |
| `f_b10_d2` | *(usado, mediu **52,6** — o rótulo mente sobre a banda)* ATLETA DE POWERLIFTING FEMININA DA CATEGORIA MAIS PESADA — a competidora de agachamento, supino e levantamento terra, julgada por FORÇA BRUTA, NUNCA por estética. Corpo GRANDE, LARGO e PESADO: estrutura óssea muito larga, massa muscular alta construída por baixo de uma camada espessa de gordura. Ombros e costas muito largos e grossos, braços cheios e potentes, abdômen grande e saliente — barriga de força, firme e arredondada. Quadril muito largo, coxas enormes e sólidas que se tocam, panturrilhas grossas, pescoço grosso. NENHUMA definição muscular visível: a força se lê no TAMANHO e na DENSIDADE, não no desenho do músculo. |
| `f_b11_d2` | Obesidade grau II com força. Corpo enorme e pesado, costas e ombros muito largos, força visível apesar do volume de gordura. |

### d3 — definição alta (9) · < 21% de gordura
| ID | Descritor |
|---|---|
| `f_b02_d3` | *(usado com âncora `b02_d2` 18,3, mediu **16,9** — abriu o pé da `d3`)* CORREDORA DE MARATONA DE ELITE, queniana ou etíope, atleta de fundo de nível mundial. O físico mais LEVE e mais SECO do esporte de alto rendimento: percentual de gordura muito baixo, e massa muscular MÍNIMA — o peso é o inimigo dela. Ombros estreitos e finos. Braços muito finos, com o contorno do tríceps aparecendo pela ausência de gordura, não por volume. Quadril estreito. Pernas longas e finas, com quadríceps e panturrilhas de contorno nítido porém ENXUTO, sem nenhuma massa. Abdômen seco, com gomos visíveis e serrátil aparente sobre as costelas. Cintura muito fina. Ela NÃO tem corpo de academia: NÃO adicionar volume muscular nenhum, NÃO alargar os ombros, NÃO encher as coxas nem os glúteos. Tudo que aparece de músculo aparece porque a gordura sumiu, e não porque o músculo cresceu. *(Anexar SÓ o vizinho e largar a folha-mãe — ver §6.)* |
| `f_b03_d3` | Magra e definida. Abdômen com gomos marcados, ombros e braços desenhados, glúteos firmes porém pequenos, cintura muito fina, pouca massa muscular. |
| `f_b04_d3` | Atlética e definida. Gomos abdominais claros, ombros desenhados, coxas e glúteos torneados com separação muscular visível, cintura fina. |
| `f_b05_d3` | Musculosa e definida. Físico de atleta fitness: ombros e costas desenhados, glúteos e coxas com volume e separação, abdômen com gomos evidentes. |
| `f_b06_d3` | Bem musculosa e seca. Ombros largos, dorsais visíveis, quadríceps com separação clara, abdômen definido, veias aparentes nos braços. |
| `f_b06h_d3` | ATLETA DE BIKINI FITNESS DE COMPETIÇÃO — a divisão MAIS LEVE do fisiculturismo feminino, julgada por proporção e simetria, NÃO por volume muscular. Corpo esbelto e tonificado, com músculo visível mas SEM massa: ombros com forma arredondada e discreta, braços finos e definidos, coxas firmes e torneadas porém MAGRAS, glúteos redondos e firmes de tamanho moderado. Cintura muito fina. Abdômen seco com gomos visíveis. É um físico de PALCO ENXUTO, bem mais leve que uma fisiculturista. |
| `f_b08h_d3` | ATLETA DE CROSSFIT DE ELITE, competidora dos CrossFit Games. Físico funcional e POTENTE, construído para levantamento olímpico e ginástica: ombros redondos e desenvolvidos, dorsais largos que abrem o formato em V nas costas, braços grossos e definidos, antebraços fortes, glúteos e quadríceps potentes e volumosos, panturrilhas marcadas. Corpo SÓLIDO E DENSO, de musculatura pesada. Abdômen seco com gomos bem visíveis e oblíquos marcados. Percentual de gordura baixo. |
| `f_b07_d3` | ATLETA DE WELLNESS DE COMPETIÇÃO — a divisão do fisiculturismo feminino que é julgada pelo desenvolvimento de quadril, glúteos e coxas. Quadríceps e glúteos muito volumosos, com separação muscular clara e visível. Quadril largo e cintura estreita, criando um contraste forte entre os dois. Dorsais e ombros desenvolvidos, braços definidos. Abdômen seco, com gomos visíveis. |
| `f_b08_d3` | Físico de fisiculturista feminina. Massa muscular alta, dorsais desenvolvidos, cintura estreita em relação aos ombros e ao quadril, abdômen definido. |
| `f_b09_d3` | Fisiculturista pesada. Volume muscular muito alto, dorsais largos, braços e coxas muito desenvolvidos, definição mantida. |
| `f_b10_d3` | Fisiculturista de grande porte. Massa muscular extrema, estrutura enorme, ombros e coxas muito volumosos, abdômen ainda definido. |

> ### 🔴 O `f_b07_d3` foi TROCADO em 30/07 — e o descritor velho não deve voltar
>
> Ele era *"Muito musculosa. Massa alta com baixa gordura, ombros muito largos,
> braços e coxas volumosos, abdômen definido, cintura estreita."* — **puro
> intensificador**, e a §2.1 já tinha medido que adjetivo de intensidade não move
> corpo. O `state.md` da sessão 13 chegou a marcar essa linha como inutilizável.
>
> O Rogério a substituiu por um **substantivo de categoria** ("atleta de wellness
> de competição"), que é o único lever medido (§2.2), e o resultado foi o
> `zen_f_b07_d3` em **IMC 27,7** — um corpo que não existia na biblioteca:
> `cintura/quadril` **0,524** e `quadril/peito` **1,317**, ambos os extremos da
> série `d3` inteira, com cintura de **64,3 cm** — mais fina que a da `b05_d3`,
> que tem IMC 21,0.
>
> **A lição é maior que esta linha:** descritor inerte não se conserta com mais
> adjetivo, se conserta trocando o substantivo por uma **categoria do mundo real**
> que já carrega uma forma. "Wellness" é uma divisão de competição com regras de
> julgamento próprias — o gerador sabe o que é. "Muito musculosa" não é nada.
>
> ### 📊 Escada de categorias medida — use isto para MIRAR
>
> Todas femininas, ChatGPT, sessões 13–15. **Esta é a régua de mira, não a
> numeração das bandas** (§2.5: a ordem da tabela NÃO é a ordem dos pousos):
>
> | categoria no descritor | IMC medido | id |
> |---|---:|---|
> | bailarina clássica de companhia | **19,8** | `b03_d2` |
> | bikini fitness de competição | **22,3** | `b06h_d3` |
> | wellness de competição | **27,7** | `b07_d3` |
> | fisiculturista feminina | **28,4** | `b08_d3` |
> | CrossFit de elite | **29,0** | `b08h_d3` |
> | fisiculturista pesada | **30,1** | `b09h_d3` |
> | peso normal alto, sem tônus (`d1`) | **32,4** | `b06_d1` |
>
> ⚠️ **O passo mínimo entre categorias é ~6,3.** Vão mais estreito que isso não se
> fecha trocando descritor — o lever passa a ser a **âncora**.
>
> ### ⚠️ UM LEVER POR FOLHA — não empilhar
>
> **Categoria governa TAMANHO; direção de volume governa FORMA.** Os dois juntos,
> com negações, dão **zero**: no `b06h_d3` eu empilhei categoria leve + *"o passo é
> PEQUENO"* + *"NÃO aumentar ombros/braços/coxas"* e o passo foi **+0,2**. Tirando
> as negações no avatar seguinte, o mesmo lever deu **+6,7**.
>
> **Negação legítima nomeia o ATRATOR a evitar** (*"NÃO é obesa"*), nunca um traço
> que o próprio descritor pede (*"ombros largos… NÃO aumentar ombros"*).
>
> **Duas cláusulas foram usadas no slot junto com o descritor** (o bloco fixo
> ficou literal), e a medida mostra que as duas pegaram:
> 1. **direção do volume** — *"o volume cresce principalmente na METADE DE BAIXO
>    do corpo […] enquanto a cintura permanece estreita"*. Contra o `b08_d3`:
>    coxa igual (74,1 × 75,0) e quadril maior (+2,3), mas peito **−6,8** e bíceps
>    **−3,2**. Cresceu embaixo e *encolheu* em cima.
> 2. **trava de identidade feminina** — a mesma do `b09h_d3`, nomeando os três
>    defeitos do `b09_d3` velho.
