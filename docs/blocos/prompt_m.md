# Bloco de prompt — MASCULINO

> ⚠️ **COLAR LITERAL. Não reescrever, não "melhorar", não improvisar.** Qualquer
> variação de linguagem produz variação de personagem, e a consistência da
> biblioteca inteira depende deste texto ser idêntico em toda geração.
>
> **Este arquivo é a FONTE ÚNICA do bloco fixo masculino.** O
> `docs/CHARACTER_BIBLE.md` aponta para cá e não guarda uma segunda cópia — duas
> cópias divergiriam.
>
> **O PORQUÊ de cada linha está no `CHARACTER_BIBLE.md`** (§1 travas de
> consistência · §3/§4 razão do bloco · §5 razão dos descritores · §5b anti-deriva
> · §5c controle do tamanho do passo). Abrir de lá **quando a decisão for sobre o
> método**; para montar um prompt, este arquivo basta.

## Bloco fixo — substituir apenas `{TIPO_DE_CORPO}`

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

## Descritores — colar um no slot `{TIPO_DE_CORPO}`

### d1 — definição baixa (12)
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

### d2 — definição média (11)
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

### d3 — definição alta (9)
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
