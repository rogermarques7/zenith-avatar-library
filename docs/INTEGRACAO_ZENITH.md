# Integração com o app Zenith — o contrato

> Levantado em **01/08/2026**, sessão 19, lendo o repositório do app
> (`C:\Users\VAIO\Desktop\ProjetosFlutter\zenith`, branch `main`, sprint 44).
>
> Este arquivo é o **contrato entre os dois repositórios**. O que está aqui foi
> lido no código do app, não suposto. Onde houver decisão pendente, está marcada.

## 1. A ordem de trabalho (decidida pelo Rogério em 31/07 e 01/08)

1. ~~Fechar o short dos masculinos~~ → reaberto por defeito → ✅ **os 39 estão
   vestidos** (§7); sobra a fila de ajuste fino no olho dele
2. **Integração com o app Zenith**
3. ~~Pintura das peças femininas em paralelo~~ → ✅ **as 37 vestidas em 02/08**
   (short + faixa); sobra a fila de correção do **top**, que ele lista na sessão
   seguinte

O que a sessão 19 mediu **inverteu a prioridade interna do passo 2**: antes de
escrever qualquer linha no app, o índice precisa de três consertos (§6). Sem
eles a tela de objetivo não tem como funcionar.

## 1b. 🆕 O QUE A SESSÃO 20 FECHOU (01/08) — ler antes do resto

O §6 abaixo tinha 6 passos. **Os passos 1 e 2 estão FEITOS**, o passo 2 saiu
**refutado por medição** (não era o conserto certo), e o §8 foi **regerado e
entregue ao app**. O que mudou:

- ✅ **`shoulder` medido nos 76** e publicado no `library.json`. O contrato de
  medidas fechou em **9 de 9** — não sobra campo do app sem coluna aqui.
- 🔴 **Achado novo, e era grave: `calf` media o JOELHO** em 50 dos 76 (35 dos 51
  na faixa de usuário). Banda corrigida; correção mediana **−2,2 cm**, máxima
  **−5,6 cm**. Doutrina em `LICOES.md` §1.8.
- ❌ **O passo 2 (`chest` vira máximo de banda) está REFUTADO.** Testado: o máximo
  foge para a axila (+8 cm). Medida de fita é landmark, não extremo —
  `LICOES.md` §1.8b. **Não reabrir.**
- 🆕 **Trava nova:** toda medida de extremo grava `at_band_edge` quando encosta na
  borda da banda. Foi ela que pegou os dois erros acima.
- ✅ **Prompt do app entregue** (`docs/PROMPT_APP_INTEGRACAO.md`), e o `coxa.png`
  já foi regerado e substituído.
- 🔴 **Pendência de decisão do Rogério, e ela bloqueia o passo 3:** o `chest` está
  marcado `below_band` em **21 dos 51** avatares da faixa de usuário. Ver §6b.

## 2. ✅ O vetor de medidas JÁ BATE — 9 de 9

O app coleta exatamente as circunferências que o `metrics.py` mede. Isto não foi
combinado; foi descoberto. É o achado que torna a integração barata.

| app — tabela `body_measurements` | tela | biblioteca — `circumferences_cm` |
|---|---|---|
| `chest_cm` | Peitoral | `chest` |
| `waist_cm` | Cintura | **`waist_min`** ⚠️ ver §3 |
| `arm_cm` | Bíceps | `biceps` |
| `forearm_cm` | Antebraço | `forearm` |
| `thigh_cm` | Coxa | `thigh` |
| `calf_cm` | Panturrilha | `calf` |
| `hip_cm` | Glúteo | `hip` |
| `neck_cm` | Pescoço | `neck` |
| `shoulder_cm` | Ombros | ✅ **`shoulder`** — criado em 01/08, nos 76 |
| `weight_kg`, `height_cm` | — | `est_mass_kg`, `height_m` |

Sobras: a biblioteca tem `wrist` e `waist_navel` que o app não coleta.

**Faixas medidas na faixa de usuário (IMC 17–40, n=51)**, para o outro lado saber
o que esperar: `chest` 81,8–121,4 · `waist_min` 60,9–119,4 · `biceps` 20,8–45,4 ·
`forearm` 21,0–40,3 · `thigh` 46,3–79,2 · `calf` 29,4–50,5 · `hip` 87,8–133,4 ·
`neck` 30,5–51,3 · `shoulder` 93,7–155,0.

✅ **Teste de sanidade do `shoulder`:** ele é maior que `chest` em **51 de 51**
avatares da faixa de usuário, sem exceção. E `est_bmi` **não mudou em nenhum dos
76** — a remedição não tocou volume nem massa, então a ordenação do índice e o
`nearest_id` por IMC seguem intactos.

**Consequência para o `VISAO_PRODUTO.md` §5:** a linha *"entrada por MEDIDAS em
vez de IMC"*, listada como ❌ e como o item de melhor relação valor/custo, está
**quase toda pronta** — os dois lados já falam os mesmos números.

## 3. 🔴 `waist_cm` é a cintura MÍNIMA, não a do umbigo

O guia do app instrui: *"Passe a fita ao redor da **parte mais estreita** do
abdômen, logo acima do umbigo."*

O `build_index.py` calcula `waist_to_height` e `band_label` a partir de
**`waist_navel`**. É a coluna errada. Medido nos 76:

| | diferença `waist_navel − waist_min` |
|---|---|
| mediana, biblioteca inteira | 10,7 cm |
| mediana, faixa de usuário (IMC 17–40) | **6,5 cm** |
| máximo na faixa de usuário | **24,2 cm** |

6,5 cm é mais do que separa dois avatares vizinhos da grade. O erro é
**sistemático e para o lado gordo**, e não apareceria em trava nenhuma.

⚠️ **O app se contradiz sozinho:** o formulário de onboarding rotula o campo
**"Abdômen (cm)"** enquanto o guia chama de **"Cintura"** e ensina o ponto mais
estreito. Quem lê o rótulo mede no umbigo, quem abre o guia mede o mínimo, e os
dois vão para a mesma coluna. **Correção pedida no lado do app** (§8).

## 4. 🔴 O app NÃO estima percentual de gordura

Procurado em todo o repositório do app: não existe fórmula. `body_fat_pct` só é
preenchido se o usuário **digitar** (`add_measurement_page.dart:159`) ou se vier
de balança inteligente por Health Connect (`health_weight_service.dart:91`). O
onboarding **nem passa o campo** (`onboarding_page.dart:163`). O trigger
`calc_bmi_bmr` do Postgres calcula IMC e TMB, só.

**Isso invalida a regra que o `library.json` publica hoje:**

```json
"definition_thresholds_bodyfat_pct": {"m": {"d3_below": 13.0}, "f": {"d3_below": 21.0}}
```

Ela pede uma entrada que o usuário típico nunca terá. E mesmo quando tem, não
fecha: rodando Navy sobre os 76, **os 12 avatares `f d3` medem de 22,7% a
52,6%** contra o `d3_below: 21.0` que o próprio índice declara — nenhum
qualificaria.

**Causa raiz:** medida de circunferência não distingue músculo de gordura.
Cintura grossa de fisiculturista lê como gordura. É exatamente a população deste
app. Bate com o que o `state.md` já registrava por outro caminho (`b09_d3` e
`b10_d3` "lendo masculino").

➡️ **Decisão: o eixo de definição NÃO é percentual de gordura.** Sai das 8
circunferências, que é o único dado que os dois lados têm de verdade. A seleção
vira **distância no espaço de medidas** — a mesma função nos 8 números do
usuário e nos 8 de cada avatar.

## 5. O VETOR DE OBJETIVO — por que IMC sozinho não serve

O app tem **6 objetivos** (`profile_model.dart:24` + `zenith_goal_estimator.dart`):
`lose_weight`, `gain_muscle`, `recomp`, `maintain`, `improve_health`, `performance`.

A tela "Objetivo Zenith" mostra **dois** avatares — atual e meta. Para achar o da
direita é preciso saber para onde o objetivo empurra **cada medida**:

| objetivo | cintura | quadril | peito/ombro | braço · coxa · panturrilha | peso | IMC |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| `lose_weight` | **↓↓** | ↓ | ↓ leve | **=** | ↓ | ↓ |
| `gain_muscle` | **=** | = | ↑ | **↑↑** | ↑ | **↑** |
| `recomp` | **↓** | ↓ leve | ↑ | **↑** | = | **=** |
| `maintain` · `improve_health` · `performance` | — | — | — | — | — | — |

A linha do `lose_weight` é o que o app já escreve na tela: *"Reduzir gordura
corporal mantendo massa magra"* — **cintura desce, braço e coxa ficam parados**.

**Os dois casos que quebram com seleção por IMC:**

- **`recomp`**: o IMC não se move → a meta sai **idêntica ao atual** → dois
  corpos iguais na tela sob "31% da meta alcançada".
- **`gain_muscle`**: o IMC **sobe** → o app escolhe um corpo **mais gordo** e o
  chama de "sua melhor versão".

As três últimas não têm corpo-alvo, e isso já está no código do app: o
`maxLevels()` devolve `null` para elas. A tela não deve mostrar dois avatares.

**Divisão de responsabilidade:** a biblioteca dá a **direção** (esta tabela, no
`library.json`, porque é ela que conhece o espaço de medidas). O app dá o
**tamanho do passo** (a meta que o usuário declarou). Direção × tamanho = um
ponto; o `nearest` nesse ponto é o avatar da direita.

**Duas travas que só a biblioteca garante:** a meta **nunca** pode ser o mesmo
avatar do atual, e **nunca** pode cair do lado errado da direção.

⚠️ **O progresso de hoje é COMPORTAMENTAL, não corporal.** O
`computeGoalProgress` soma XP de treino, refeição, sono, suplemento e hidratação.
Não há nada no app que derive corpo-alvo (`target_weight`/`goal_weight`: zero
ocorrências). **Recomendação: o avatar segue as MEDIDAS, nunca o XP.** Quem tem
90 dias de aderência perfeita e abdômen parado não pode ver outro corpo — o XP é
o esforço, o avatar é o resultado.

## 6. O que falta na biblioteca, em ordem

1. ✅ **FEITO — ombro medido nos 76.** Circunferência na linha dos deltoides, em
   `SHOULDER_FRAC = 0.795` — a altura que o **render do próprio app** define. A
   fatia fica acima da axila de propósito: os deltoides estão fundidos ao tronco,
   a seção é um laço fechado único e o casco convexo dele é o que a fita mede.
2. ❌ **REFUTADO — `chest` continua fração fixa.** A ideia era virar "máximo numa
   banda" porque o guia pede "a parte mais larga". Testado em 01/08: o máximo
   **foge para a axila** (+8 cm no `b01_d1`), onde dorsal e deltoide entram no
   casco convexo. Medida de fita é landmark, não extremo. **Não reabrir** —
   `LICOES.md` §1.8b.
   ➡️ Em compensação apareceu o defeito de verdade, que ninguém procurava: a
   **panturrilha media o joelho** em 50 dos 76 (`LICOES.md` §1.8). Corrigido.
3. ✅ **FEITO (03/08) — `build_index.py` indexa por MEDIDAS**, usa `waist_min`, e
   `definition_thresholds_bodyfat_pct` foi aposentado. Schema 4.
4. ✅ **FEITO — `test/selection_cases.json`, 34 casos.** Rodam nas TRÊS
   implementações: Python (`select.py --check`), Dart
   (`test/avatar_selection_test.dart`) e JS (o tester roda sozinho ao abrir).
5. ✅ **FEITO — vetor de objetivo publicado**, os 6 tipos. Os três sem
   corpo-alvo saem com `has_target_body: false`.
6. ✅ **FEITO (03–04/08) — integração no ar.** O avatar 3D aparece na home do
   app, escolhido pelas 9 medidas. Ver §11.

## 6b. 🔴 A DECISÃO QUE BLOQUEIA O PASSO 3 — o peso do `chest`

**`chest` está marcado `below_band` em 21 dos 51 avatares da faixa de usuário
(41%), e em 39 dos 76 no total.**

A causa é estrutural, não bug: os masters estão em **A-pose**, e em 41% dos corpos
os braços fundem com o tronco **abaixo** da linha do mamilo. Acima dessa altura o
casco convexo engloba os braços e o número infla; abaixo, deixa de ser peito e
tende à barriga. O `zen_f_b12_d1` publicava **202,7 cm em `chest` e 202,7 em
`waist_navel`** — o mesmo z, sem nada avisando. Agora vai marcado.

Consertar de verdade exigiria separar a geometria do braço dentro de um laço já
fundido: caro e arriscado.

➡️ **Recomendação: não consertar a medida, e sim ensinar a seleção a conviver com
ela.** O `chest` entra na distância com peso menor — ou fora — nos avatares
marcados, em vez de valer tanto quanto as outras oito colunas. **Decisão do
Rogério, pendente.** Ela define a função de distância do passo 3 e os casos do
passo 4, então nada disso deve ser escrito antes dela.

⚠️ Isso vale também para o teste de calibração com o corpo do Rogério: se os
braços dele fundirem cedo na A-pose, o `chest` do avatar dele virá marcado e essa
coluna não valerá comparação. As outras 8 valem.

## 7. ✅ O estado dos GLBs entregues (02/08) — os 76 estão vestidos

O apagão dos 39 shorts masculinos (`restyle.py --all` da sessão 18, em silêncio)
foi **resolvido**, e o feminino saiu do zero:

- **76/76 com peça no dist.** 39 masculinos com short; **37 femininos com short
  *e* faixa**, aplicados em 02/08.
- **Todo GLB carrega 2 materiais** — `Zenith_Body` (`#B9BCC2` / metallic 0.25 /
  roughness 0.45) e `Zenith_Shorts` (quase preto, metallic 0 / roughness 0.70).
  Conferido de duas formas independentes: `probe_material_dist.py` lendo o disco,
  e o `model-viewer` lendo o GLB **pelo mesmo caminho que o app vai ler**.
- **Versionamento estabilizado:** 76 arquivos, 76 ids, **nenhum id com duas
  versões no disco**, e o `library.json` bate 76 de 76. Os masculinos em v2, os
  femininos em v2 (`b05_d2` e `b01_d1` em v3).
- `config/shorts_map.json` tem as **76 entradas** — *o mapa é o produto*
  (`CLAUDE.md` regra 3b). Nenhuma decisão se perdeu no apagão, só tempo de
  máquina. Causa estrutural e travas criadas em `LICOES.md` §4.2f.

⚠️ **"Tem peça" não é "peça certa".** O Rogério revisou os 76 no testador em
02/08 e aprovou o conjunto, mas com fila de correção: poucos ajustes finos no
masculino e **defeitos concentrados no top (faixa) no feminino**. A lista vem no
começo da próxima sessão. Ver `state.md` e `LICOES.md` §4.5b — o traçado da borda
de cima da faixa **não é medido em avatar nenhum**, e é a decisão de método que
está aberta.

## 8. O lado do app — mudanças pedidas

> ## ✅ ENTREGUE em 01/08 — o prompt final está em `docs/PROMPT_APP_INTEGRACAO.md`
>
> **Não usar o conteúdo abaixo como fonte: ele foi escrito a partir do TEXTO dos
> arquivos, e a medição dos pixels derrubou 3 das 5 afirmações.** Fica aqui como
> registro do que se pensava.
>
> | | §8 dizia | medido em 01/08 |
> |---|---|---|
> | Peitoral | 🔴 barra reta, refazer | **é anel**, texto coerente — ✅ **não mexer** |
> | Ombros | ⚠️ refazer render **e** texto | render **já é anel**; só o texto diz "largura" |
> | Ombro no formulário | "nenhum formulário pede" | **já existe** em `add_measurement_page.dart:465`; falta só no onboarding |
> | Coxa | 🔴 anel baixo demais | 🔴 **confirmado** — 11,6 cm. ✅ **regerado e substituído em 01/08** |
> | Panturrilha | listada como coerente | app **certo**; quem errava era a biblioteca |
>
> **Como eu errei:** descrevi os PNGs pelo **cabeçalho de comentário** do
> `measurement_guide_page.dart` em vez de abrir os binários. Lição em
> `LICOES.md` §1.7b.
>
> **Estado das 4 tarefas entregues ao app:**
> 1. rótulo `Abdômen` → `Cintura` — ✅ liberado para aplicar. Query rodada no
>    Supabase: **1 usuário, 2 linhas com `waist_cm`**, e são do próprio Rogério.
>    Sem migração de dados.
> 2. texto do guia de ombro (largura → circunferência) — com ele
> 3. campo de ombro no onboarding + chave l10n `shoulder` — com ele
> 4. `coxa.png` — ✅ **feito**: anel subiu de `at_frac` 0,394 para **0,441**,
>    dentro da banda 0,432–0,466 que o `metrics.py` usa para definir coxa
>    (`LICOES.md` §1.8c). Arquivo já gravado em `assets/medidas/coxa.png` do
>    repositório do app, **aguardando commit do lado de lá**.

**8a. Ambiguidade de cintura (§3).** Alinhar pelo guia: rótulo vira "Cintura
(cm)" no onboarding e no `add_measurement_page`, com a chave de tradução. Não
mexer no guia. Se já houver medidas em produção, avisar antes — muda semântica de
dado existente.

**8b. Ombros não é coletado.** O modelo tem `shoulderCm`, o repositório grava
`shoulder_cm`, o guia tem a tela — mas nenhum formulário pede. Adicionar, na
ordem do guia (depois de Pescoço, antes de Peitoral).

**8c. Três assets do guia divergem do próprio texto.** Auditados os 10 PNGs de
`assets/medidas/` contra as instruções:

| passo | texto manda | desenho mostra | |
|---|---|---|---|
| Ombros | **largura** deltoide a deltoide | barra reta | ⚠️ |
| Peitoral | **circunferência** | barra reta | 🔴 |
| Coxa | *"parte mais larga"* (alto, na virilha) | anel **acima do joelho** | 🔴 |

Os outros sete (pescoço, bíceps, antebraço, cintura, glúteo, panturrilha,
altura) estão coerentes.

- **Peitoral**: a barra foi reaproveitada do render de ombro — o cabeçalho do
  arquivo entrega (*"v4.2 — Peitoral entrou (a barra horizontal no peito era
  peitoral, não ombro)"*). Refazer como anel.
- **Coxa**: medido na biblioteca, faixa de usuário — coxa (mais larga) **63,0 cm**
  contra panturrilha **41,4 cm**. A perna afina ~22 cm nesse trajeto e o anel do
  desenho cai perto do fim da descida. Refazer no terço superior.
- **Ombros**: ➡️ **decisão tomada — vira CIRCUNFERÊNCIA**, muda o texto e o
  render. Motivo: **largura de ombro é inviável de auto-medir sozinho** (fita
  reta, horizontal, duas pontas fora do campo de visão); circunferência o usuário
  passa em volta e lê na frente. Medida que o usuário faz errado é pior que
  medida menos elegante.

✅ **RESOLVIDO em 01/08 — o `ombro.png` commitado é um ANEL.** Isolado o marcador
por pixel: elipse fechada em perspectiva, na altura **0,795** da estatura, e é o
arquivo mais recente do conjunto (8/jul 01:17), com o working tree do app limpo.
**O Rogério estava certo e eu estava errado** — eu tinha descrito o PNG pelo
cabeçalho de comentário do `.dart`, não pelos pixels.

Consequências: o passo 1 do §6 destravou e foi feito; a biblioteca **adotou os
0,795 do render do app** como `SHOULDER_FRAC`; e do lado do app sobra só corrigir
o **texto**, que ainda diz "largura".

## 9. Onde o avatar entra no app

- **Home** — hoje exibe **um avatar 2D estático**. Vira o GLB girando.
- **Objetivo Zenith** — atual × meta lado a lado. **A tela ainda não existe** no
  repositório (sprint 44, sem `target_weight`).

## 10. Fora de escopo agora

`zenith_avatar_engine` (terceiro repositório) — o Rogério mandou ignorar por
enquanto: *"tem algumas coisas lá que serão muito úteis quando formos aplicar os
morph targets."*

---

## 11. ✅ A INTEGRAÇÃO, COMO ELA FICOU (sessões 23, 03–04/08/2026)

### 11.1 O contrato, em uma tela

```
usuário digita 9 circunferências (body_measurements)
        ↓  escala para 1,75 m  (medida × 1,75/altura — circunferência é LINEAR)
        ↓  descarta coluna fora da faixa da biblioteca  → suspect_columns
        ↓  descarta coluna marcada unreliable NAQUELE avatar
        ↓  distância = sqrt( Σ w·clamp(z, ±1,5)² / Σw )
        ↓  menor distância dentro do MESMO sexo (empate: menor id)
    avatar  →  cdn_base + assets.glb  →  <model-viewer> + environment-image
```

Sem 3 colunas comparáveis, cai no fallback por IMC na linha `d2`.

### 11.2 Onde cada peça mora

| peça | onde |
|---|---|
| regra, implementação de REFERÊNCIA | `scripts/select.py` (esta biblioteca) |
| regra, app | `lib/core/utils/avatar_selector.dart` |
| regra, tester | `test/avatar_tester.html` (roda os casos ao abrir) |
| banco de casos | `test/selection_cases.json` → copiado para `test/fixtures/` do app |
| índice | `library.json` → copiado para `assets/avatars/` do app (67 KB, embutido) |
| GLBs + HDR | Supabase Storage, bucket público `avatars` |
| upload | `scripts/publish_avatars.py` — **no repo do APP**, porque esta biblioteca não tem rede nem chave (regra 1 do CLAUDE.md) |

⚠️ **Mexeu na regra: muda no Python, roda `--cases`, copia os DOIS arquivos.**
Índice novo com casos velhos reprova sem haver defeito — e alarme falso ensina a
desligar o alarme.

### 11.3 As decisões da sessão, e o porquê

- **Peso 0 em coluna marcada** (`unreliable_columns`), não peso reduzido. Vale
  para `below_band` do chest E para `at_band_edge` — a mesma doutrina do §1.8
  aplicada uniformemente. Decisão do Rogério.
- **`z_cap = 1,5 dp` + coluna fora da faixa não vota.** Uma panturrilha digitada
  errada decidia o avatar sozinha. `LICOES.md` §7.1.
- **Tronco escolhe, membros são morfados**: `waist_min` 3,0 · `hip`/`chest`/
  `shoulder` 2,0 · membros 0,3. Provisórios até as faixas de morph fecharem.
  `LICOES.md` §7.3.
- **`model_viewer_plus`** no app. É o único caminho com `environment-image`, e
  sem o HDR o corpo sai cinza (metade do visual mora fora do GLB).

### 11.4 O que o app precisou mudar, e que dói se alguém desfizer

- `android/app/src/main/res/xml/network_security_config.xml` — texto claro
  liberado **só** para `127.0.0.1`. O `model_viewer_plus` serve a página por um
  proxy HTTP local, e o Android 9+ bloqueia por padrão: sem isso a página nunca
  carrega e o card fica preto **sem erro no log**. A flag global
  `usesCleartextTraffic` foi recusada de propósito.
- `android/app/gradle.properties` — heap de 8G para 3G. A máquina tem 7 GB e o
  build morria por OOM.

### 11.5 O que NÃO está feito

- **O avatar escolhido não é persistido** — recalculado a cada abertura. Mudar
  peso ou escala reescreve o passado. `LICOES.md` §7.8.
- **Gênero 'other'** cai na coleção masculina, por falta de decisão de produto.
- **A tela de objetivo não existe.** O `selectGoal` está pronto e testado dos
  dois lados, mas nada o consome ainda.

---

## 12. 🧬 MORPH — o contrato, e o que o app precisa fazer (sessão 24, 05/08)

**Um avatar já sai com shape keys: `zen_m_b05h_d2_v7.glb`**, que é o corpo que a
seleção escolhe para o Rogério. São **9 morphs, um por coluna de medida**, o GLB
pesa **981 KB** (era 210 KB sem morph), e ele foi **aprovado no olho dele em
06/08**. Os outros 75 ainda não têm morph — o app tem que tratar a ausência de
entrada no `morph_map.json` como "sem morph", não como erro.

### 12.1 O que o app faz

```
avatar escolhido  →  config/morph_map.json[id]        (ausente = sem morph)
para cada morph:  SE a coluna não está em columns_used da seleção → influence 0
                  Δ = usuario_cm × (1,75/altura) − morphs[k].base_cm
                  influence = interp(Δ, curve[cm], curve[influence])
                  (a curve já vem limitada a [influence_min, influence_max])
aplicar em TODAS as malhas da árvore
```

🔴 **Coluna que a seleção descartou NÃO morfa.** O `select` devolve
`columns_used` e `suspect_columns`; uma coluna fora de `columns_used` foi
descartada por estar fora da faixa da biblioteca (fita no lugar errado) ou por
ser `unreliable` naquele avatar. Ela não vota em QUAL corpo — então não pode
esculpir o corpo. Medido: uma panturrilha digitada 28 fazia o morph encolher 3 cm
de uma perna que a seleção tinha, corretamente, ignorado. `LICOES.md` §7.18.

⚠️ **A escala para 1,75 m é a MESMA da seleção.** Se divergir, o morph corrige
para um alvo diferente do que decidiu a escolha.

🔴 **`morph_waist_flatten` é uma chave de FORMA, não de tamanho.** Ela não tem
coluna, não sai de medida nenhuma e é **acoplada**: `influence = max(0, influence
do morph_waist)`. Existe porque fechar o perímetro isotropicamente engorda a
barriga em profundidade — no corpo real medido o erro no eixo visível ia de 1,9
para 3,6 cm. Só no crescimento: reduzir cintura tem que perder profundidade, que
é o que emagrecer faz. `LICOES.md` §7.22.

⚠️ **A curva do `morph_waist` já é a ACOPLADA** (+10,8 cm em influence 1,0, não
+10,0). Aplicar o tamanho sem a forma entrega um centímetro que o mapa não
promete.

🔴 **`influence = Δ / cm_at_full` está ERRADO** e é a armadilha do contrato. A
relação não é linear em todo morph: o `morph_neck` entrega **+3,2 cm em
influence 0,5** e só **+3,8 em 1,0** — ele é um mínimo de banda, e crescer o
meio empurra o mínimo para a borda travada pelo queixo. Multiplicar erra 68% ali.
O campo `curve` existe para isso; `cm_at_full` é documentação.

🔴 **O GLB tem DUAS primitivas** (corpo e short são materiais diferentes, e glTF
quebra primitiva por material). No three.js cada uma vira um `THREE.Mesh` com o
**seu próprio `morphTargetInfluences`**. Quem setar só no primeiro morfa o corpo
e **deixa o short parado**. Percorrer a árvore.

### 12.2 Medido no navegador antes de ir para o device

Sonda: `test/morph_probe.html` (three.js 0.160 + Draco + o HDR de produção,
servida por `http://localhost:8765`).

| pergunta | resposta medida |
|---|---|
| os 9 targets chegam? (o caminho legado do three.js para em 8) | **sim**, WebGL2, 9 em cada primitiva |
| as duas primitivas morfam? | **sim** — corpo 25.914 verts, short 6.237 |
| influence NEGATIVA funciona? | **sim** — silhueta de 59.250 px na base para **55.074** em tudo −1 e **63.587** em tudo +1 |
| precisa de enforcer por frame? | **não se reproduziu.** Depois de 7 s de laço de render as nove influences continuavam em −1 e a silhueta idêntica |

⚠️ **O enforcer continua em aberto para o `model_viewer_plus`**, que é o que o
app usa — a sonda acima é three.js puro. Se o morph "não aparecer" no device, é
aí que se olha primeiro, não na malha.

⚠️ **No Blender a influence negativa é engolida**: o importador de glTF recria
os shape keys com slider 0..1, então "tudo no mínimo" renderiza **igual à base**.
Isso é do Blender, não do arquivo — no three.js `morphTargetInfluences` é float
livre. A sonda `morph_render_ab.py` já abre o slider; qualquer ferramenta nova
tem que abrir também, senão a foto aprova um morph que não foi aplicado.

### 12.3 As faixas, medidas neste avatar

Teto de **±1,0 em toda coluna**, e ele veio da **foto**, não das sondas: em −2,0
as sondas numéricas devolvem zero normal invertida no ombro e no braço, e o
render mostra braço cordão, degrau no deltoide e vinco no trapézio. É a §7.5 do
`LICOES.md` de novo. Nos ±1,0 os dois estados combinados renderizam limpos.

| morph | coluna | base cm | faixa medida (cm) |
|---|---|---:|---|
| `morph_neck` | neck | 49,2 | −6,0 a +1,8 |
| `morph_shoulder` | shoulder | 120,7 | −5,9 a +6,0 |
| `morph_chest` | chest | 109,7 | −2,7 a +6,0 |
| `morph_waist` | waist_min | 101,3 | −5,0 a **+10,0** |
| `morph_hip` | hip | 108,5 | −3,8 a +8,0 |
| `morph_biceps` | biceps | 36,0 | −3,5 a +4,0 |
| `morph_forearm` | forearm | 29,7 | −3,1 a +3,1 |
| `morph_thigh` | thigh | 65,3 | −5,9 a +6,0 |
| `morph_calf` | calf | 40,2 | **−6,0 a +6,0** |
| `morph_waist_flatten` | *(forma)* | — | acoplada, 0 a 1,0 |

⚠️ **Estas faixas são DESTE avatar.** Cada corpo tem anatomia diferente e será
calibrado sozinho — o app tem que ler do mapa, nunca embutir número.

⚠️ **O teto de influence é por morph** (`influence_min`/`max` no mapa). A
panturrilha vai a ±2,0 porque é cilindro isolado e a foto aprovou; o resto fica
em ±1,0. `LICOES.md` §7.15.

**Validado contra a fita do corpo real dele** (176 cm, 94 kg, IMC 30,3 · avatar
30,6): erro RMS **4,49 cm antes do morph → 1,14 cm depois**, com 8 das 9 colunas
fechando exatas. Sobra o pescoço (−3,4 cm), e é limite estrutural da biblioteca,
não do morph: `LICOES.md` §7.19.

### 12.4 O que ainda não existe

- **Só este avatar tem morph.** Rodar `python scripts/morph.py {id} --apply` nos
  outros é mecânico, mas cada um gasta uma versão de GLB e precisa subir de novo
  ao Storage. Fazer quando o device aprovar.
- **O `library.json` não carrega o morph** — o mapa é um arquivo separado. Se o
  app preferir um arquivo só, é o `build_index.py` que passa a lê-lo.
- **Nada persiste o avatar escolhido nem a influence aplicada** (§7.8).
