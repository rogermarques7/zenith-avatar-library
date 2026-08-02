# Visão de produto — a biblioteca como API, e o que ela exige

> Levantado pelo Rogério em **31/07/2026**, sessão 18: *"ao invés do zenith avatar
> library servir apenas de integração pro zenith, estava pensando em tornar ele um
> app próprio, na verdade uma api […] loja de roupas, usuário insere medidas, manda
> dados pra api que retorna o avatar e ele pode experimentar roupas sem precisar
> sair de casa."*
>
> Este arquivo é **avaliação, não decisão tomada.** Ele existe para que a conversa
> não recomece do zero, e para que o bloqueio medido abaixo não seja redescoberto
> caro.

## 1. O ativo real não é o GLB

É a **cobertura medida do eixo de IMC** somada ao `metrics.py`, que devolve
circunferências em cm e IMC por volume de malha. Isso é a linguagem que uma loja
de roupas fala. O GLB em si é commodity — qualquer um gera um corpo; poucos têm 76
corpos normalizados, medidos e ordenados.

Some a isso a normalização rígida (altura idêntica, pés em Y=0, centralizado em
X/Z, mesma orientação) — que é justamente o que permite trocar de corpo sem a tela
"pular", e o que um provador virtual precisa para não recalibrar câmera a cada
avatar.

## 2. Topologia: o que ela impede e o que NÃO impede

> ⚠️ **Correção de 31/07, no mesmo dia.** A primeira versão desta seção tratava a
> medida abaixo como *o* bloqueio da visão inteira. **Estava errada, porque eu
> avaliei um plano que não é o do Rogério.** Ele explicou: o app **não interpola
> entre avatares** — ele escolhe o mais próximo pelo mecanismo que já existe e
> aplica **ajustes locais** (bíceps, panturrilha) sobre aquele avatar. A medida
> continua verdadeira; o que muda é o que ela proíbe.
>
> **A distinção que importa:**
>
> | o que se quer fazer | precisa de topologia compartilhada? |
> |---|---|
> | morphar o corpo A **até virar** o corpo B | **sim** — e por isso é impossível hoje |
> | dar ao corpo A shape keys **próprias** ("bíceps +", "panturrilha −") | **não** — cada malha carrega as suas |
>
> O plano do Rogério é a segunda linha. **A topologia não o bloqueia.** Ele já
> tentou a primeira num projeto anterior — *"falhou justamente pq tentei aplicar
> todos ele num único avatar"* — e a biblioteca de 76 corpos existe justamente para
> não precisar dela: o vão entre um avatar e o vizinho é pequeno, então o ajuste
> que sobra é local e pequeno.

**Shape key (morph target) não é efeito visual: é uma segunda posição para CADA
VÉRTICE da MESMA malha.** Interpolar *entre dois corpos* exige que o vértice de
índice *i* seja o mesmo ponto anatômico nos dois — e é isso que foi medido:

Medido com `qa/probe/sondas/probe_topologia.py`, no **par mais favorável possível**
— dois avatares cujas contagens são idênticas:

| | `zen_f_b03_d2` | `zen_f_b04i_d1` |
|---|---:|---:|
| vértices | 29992 | 29992 ✅ |
| arestas | 90000 | 90000 ✅ |
| faces | 60000 | 60000 ✅ |
| valência ordenada | — | **diferente** |
| vizinhos iguais por índice | — | **0,0%** (0 de 4285) |
| distância entre vértices de mesmo índice | — | **0,313 m** (mediana) = **17,9% da altura** |

**Contagem igual é coincidência do ALVO de decimação (60000 tri), não
correspondência.** Um par escolhido ao acaso (`zen_m_b05_d2` × `zen_m_b06_d3`) nem
isso tem: 29988 × 29997 vértices.

**Causa:** cada avatar é uma geração independente da Meshy, seguida de uma
decimação por colapso de arestas guiada pela geometria daquele corpo. Nada nesse
caminho cria correspondência, e nenhum ajuste de parâmetro cria — é estrutural.

**Consequência:** morph **de um avatar para outro** é impossível, não difícil. Já
shape key **local dentro de um avatar** não é afetada — é o plano em curso.

## 3. O plano em curso: ajuste local por região, guiado por medida

O mecanismo do app fica assim, e cada peça dele **já existe ou é barata**:

1. o usuário entrega as medidas reais;
2. o índice escolhe o avatar mais próximo — **já funciona hoje** (`nearest_id`);
3. o `metrics.py` sabe a medida daquele avatar — **já funciona hoje**;
4. onde o delta for grande demais, aplica a shape key daquela região.

O exemplo do Rogério: IMC 28, mas panturrilha mais fina e bíceps mais largo →
usa o avatar de IMC 28 e ajusta **só essas duas regiões**. E a intenção declarada é
começar **só pelos casos extremos**, refinando com o tempo — o que é a ordem certa,
porque o custo de errar um ajuste pequeno é menor que o de não ter o corpo.

### ⚡ O ponto que decide se isso escala: gerar as shape keys por SCRIPT

Esculpir à mão seria **76 avatares × N regiões**. Mas não precisa: uma shape key de
"inflar/desinflar região" é uma deformação radial em torno de um eixo, aplicada a
uma faixa de altura — e **o `metrics.py` já sabe onde cada região começa**, porque
já mede circunferência em `at_frac` nomeados (`calf` 0.317, `biceps` 0.697,
`thigh` 0.46, `waist_min` 0.639…). Um script gera as N shape keys em todos os 76
sem trabalho manual, e é o mesmo tipo de trabalho que o `shorts.py` já faz.

⚠️ **Limitação conhecida que atinge isso em cheio:** o `state.md` registra que
*"`thigh` e circunferências de tronco não valem por avatar — `at_frac` fixo contra
virilha que se move"*. Para o ajuste local, isso importa: a régua precisa achar a
região **naquele corpo**, não numa altura fixa. Resolver isso é pré-requisito do
ajuste de tronco e coxa — e **não** do de bíceps e panturrilha, que são os do
exemplo. Começar por esses dois é, por acaso, começar pelos que a régua já suporta.

⚠️ **Aplicar shape key muda o volume, logo muda o IMC medido.** Em bíceps e
panturrilha o efeito é pequeno, mas se o ajuste crescer para tronco, o corpo servido
deixa de ser o corpo indexado. Vale o `metrics.py` rodar depois do ajuste.

## 4. O template (wrap) — só se o alvo for PROVADOR DE ROUPA

Isto **não** é pré-requisito do ajuste local acima. Vira pré-requisito se a visão
avançar para vestir roupa de verdade, porque aí é preciso:

- **UV consistente** — uma textura/estampa servir em todos os corpos;
- **rig feito uma vez** — hoje não existe nenhum;
- **correspondência anatômica** — a costura da manga cair no mesmo vértice em todo
  corpo.

O caminho é uma malha-base topologicamente fixa, deformada para caber em cada corpo;
a Meshy deixa de produzir o asset final e passa a produzir o **alvo de forma**. Isso
**não descarta nada** — os 76 viram os alvos, que é a regra 5b.

## 5. Onde o projeto está para essa visão

| requisito | estado | exigido por |
|---|---|---|
| cobertura por IMC | ✅ é o ativo | tudo |
| normalização rígida | ✅ e é rara | tudo |
| medidas reais em cm | ✅ `metrics.py` | ajuste local |
| seleção do vizinho mais próximo | ✅ `nearest_id` | ajuste local |
| pipeline reprodutível e documentado | ✅ | tudo |
| régua de região **por avatar** (não `at_frac` fixo) | ⚠️ parcial | ajuste de tronco/coxa |
| shape keys por região, geradas por script | ❌ a fazer | ajuste local |
| entrada por MEDIDAS em vez de IMC | ⚠️ **quase pronta — ver nota** | ajuste local |
| versionamento do asset entregue (cache de CDN) | ✅ desde 01/08 | tudo que atualiza |
| topologia compartilhada | ❌ medido: não existe (§2) | **só** provador de roupa |
| rig / esqueleto · UV / textura | ❌ | **só** provador de roupa |
| simulação de tecido | ❌ fora de escopo | provador de roupa |

⚡ **O item de melhor relação valor/custo é a entrada por medidas.** Uma loja manda
cintura/quadril/busto, não IMC. O `metrics.py` **já mede** essas circunferências em
todos os 76; falta o `build_index.py` indexar por elas em vez de só por
`measured_bmi`. Isso não depende do template e pode ser feito a qualquer momento.

> ✅ **Atualização de 01/08 — isso está mais perto do que parecia.** Ao ler o app
> Zenith descobriu-se que ele **já coleta exatamente as 8 circunferências que o
> `metrics.py` mede** (peitoral, cintura, bíceps, antebraço, coxa, panturrilha,
> quadril, pescoço), sem combinação prévia. Os dois lados já falam os mesmos
> números. O que falta é o `build_index.py` indexar por eles — e **corrigir a
> coluna de cintura**, que está errada (`waist_navel` onde o app coleta
> `waist_min`, 6,5 cm de diferença mediana). Tudo em
> **`docs/INTEGRACAO_ZENITH.md`**, que é onde esse contrato mora agora.
>
> ⚠️ E caiu um pressuposto: o **percentual de gordura não serve como eixo** — o
> app não o estima em lugar nenhum, e a régua de circunferência não distingue
> músculo de gordura na população deste app. Ver §4 daquele arquivo.

## 6. Os dois riscos — VERIFICADOS em 31/07

### 6.1 ✅ Licença da Meshy: plano pago permite uso comercial

Consultado nas fontes primárias (links no fim). O que ficou estabelecido:

- **Plano pago** — *"you own the assets created through our platform"*, **sem
  exigência de atribuição**, desde que não se tenha usado material que viole
  direitos de terceiros. E, sobre revenda: *"the models you create using Meshy are
  exclusively yours, and you have full rights to distribute and sell them."*
- **Plano gratuito** — não há propriedade: é licença **CC BY 4.0**, com crédito
  obrigatório. Confirma a decisão já tomada no projeto de **não** deixar entrar na
  biblioteca nada do plano gratuito.
- Os 76 saíram do plano Pro, e o Rogério gera com a opção **"Privado"** marcada, o
  que casa com a §3.2 dos Terms (cliente pago pode manter o conteúdo privado).

⚠️ **A única restrição que atinge o projeto** é a **§2.6** dos Terms: proíbe *"use
generated digital assets to train, develop, or improve AI models that are
competitive with Meshy"*. Isso **não** afeta o plano atual (provador/ajuste local
não é gerador 3D), mas **afeta um futuro plausível**: se um dia a ideia for treinar
um modelo próprio de geração de corpos usando os avatares como dado, isso está
vedado. Anotar antes de alguém propor.

⚠️ **Ressalva honesta, e não é aconselhamento jurídico:** a redação categórica de
propriedade está no **Help Center**, não nos **Terms of Use** — os Terms (§3.2)
falam em manter conteúdo privado e na licença que o cliente concede à Meshy para
operar o serviço, sem afirmar propriedade com as mesmas palavras. Os dois não são o
mesmo instrumento. E **nenhuma das páginas trata explicitamente de servir assets por
API a terceiros**. Se a API virar receita de verdade, o passo certo é pedir
confirmação por escrito ao suporte da Meshy e **guardar a resposta**.

### 6.2 ✅ Backup: feito e conferido em 31/07

`C:\Users\VAIO\Desktop\ProjetosFlutter\_backup_zenith\zenith_assets_2026-07-31.zip`
— **448 MB**, fora do repositório. Conteúdo conferido contra o disco, pasta a
pasta: `00_input` 308 · `01_raw` 76 · `02_master` 76 · `03_dist` 77 · `config` 2 ·
`metrics` 2 · `library.json`. Inclui os **76 masters**, os **76 GLBs crus** (que
custaram crédito) e as **79 folhas**, que são o material irreproduzível.

🔴 **Isto ainda NÃO é backup de verdade:** o zip está **no mesmo disco** que os
originais. Protege contra apagão acidental e contra uma reclassificação errada;
**não protege contra falha de disco**. Para virar backup, tem que sair da máquina —
HD externo ou nuvem. **Refazer o zip a cada lote novo de avatares.**

## Fontes (licença)

- [Terms of Use — Meshy](https://www.meshy.ai/terms-of-use)
- [Can I use my generated assets for commercial projects?](https://help.meshy.ai/en/articles/9992001-can-i-use-my-generated-assets-for-commercial-projects)
- [Can I sell the models on other platforms?](https://help.meshy.ai/en/articles/9992022-can-i-sell-the-models-on-other-platforms)
- [What is the ownership of the generated models?](https://help.meshy.ai/en/articles/10137554-what-is-the-ownership-of-the-generated-models)

## 7. ✅ A ORDEM DE TRABALHO — decidida em 31/07, revista em 01/08

> *"primeiro quero finalizar os masculinos e depois fazer a integração com o app
> zenith, e posteriormente vou corrigindo a cor dos femininos paralelamente, e
> subindo aos poucos ao app."*

**Revista na sessão 19:** a integração subiu para primeiro. O motivo é que
**defeito de short se julga no olho, e o lugar de olhar é o app** — corrigir 38
shorts em pasta de render e só então descobrir no app é a ordem errada.

1. **Alinhar a biblioteca e integrar** — os 6 passos de `INTEGRACAO_ZENITH.md` §6.
2. **Reaplicar os 38 shorts masculinos** (apagados por acidente, ver §7 daquele
   arquivo) e retomar a fila de 11 correções, do `b11_d1` em diante.
3. **Pintura das peças femininas em paralelo**, subindo ao app aos poucos — 74
   peças, duas por avatar (faixa + short), nenhuma feita ainda.

⚠️ **O template (§4) NÃO entra nessa ordem, e é decisão consciente.** A observação
de que o wrap eliminaria o trabalho de short por-avatar continua verdadeira, mas o
app precisa do short agora, e a visão de provador de roupa não está em execução. Se
o template vier depois, esse trabalho é refeito — **o custo foi visto e aceito**, e
isso não é dívida esquecida.

## 8. Recomendação para quando a API voltar à mesa

Os dois bloqueadores de §6 estão resolvidos. O que falta medir, quando for a hora:

1. **Um script que gere shape key de região** num avatar e o `metrics.py` medindo o
   antes/depois — prova, em um corpo, que o ajuste local muda a circunferência
   alvo **e só ela**. É o experimento que decide a viabilidade do §3, e é barato.
2. **Indexação por medidas** no `build_index.py`, que não depende de nada acima.
3. Só se o alvo virar provador de roupa: o experimento de **wrap** (§4).
