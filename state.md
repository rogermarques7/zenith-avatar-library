# state.md — Zenith Avatar Library

Última atualização: **27/07/2026 (sessão 4)**
Fase atual: **O SHORT FOI MAPEADO NOS 39.** `scripts/shorts.py` escrito, mapa em `config/shorts_map.json`, validado por duas réguas independentes.

## ⚡ ABRIR AQUI — sessão 4: o short

**O short é lido da MALHA, não da imagem.** Em 60k a bainha e o cós existem como geometria (é o relevo que apareceu quando a malha subiu de 18k). O `process.py` tentava achar o short projetando a imagem frontal e chamando pixel escuro de tecido; isso não sobrevive a um corpo obeso, em que a barriga cai por cima do cós e imagem e malha discordam sobre onde o tecido começa.

**O modelo da região:**

```
short = (z >= bainha_da_perna) E (z <= cos(azimute)) E nao e braco
```

O cós é **função do azimute** — é isso que acompanha a prega da barriga descendo na frente e subindo nos lados. A bainha é escalar por perna (duas, não uma: a pose das folhas não é simétrica).

### As quatro coisas que essa sessão aprendeu errando

1. **Vinco ≠ músculo, e o que separa é TOPOLOGIA.** Gomo abdominal é mais fundo que bainha, então detectar por profundidade escolhe o errado. A bainha dá a **volta** no membro; o sulco de músculo cobre um arco. A pontuação virou o **quantil baixo da concavidade sobre os setores de azimute** — "o setor mais fraco desta altura ainda está vincado?", que é a definição de anel fechado. Foi a troca que fez o cós parar de pousar no abdômen.
2. **Limiar de altura morre em A-pose.** A 1ª virilha detectada saiu em 0,81 da altura — o vão que o detector viu era entre **braço e tronco**. Não existe altura em que a fatia horizontal contenha só as pernas: na altura da coxa ela contém as duas mãos. Trocado por **union-find varrendo a malha de baixo para cima**: os eventos de fusão entregam virilha e axilas por conexão. O mesmo bug pintava os antebraços de preto.
3. **A bainha fica entre dois anéis MAIS FORTES que ela** — virilha em cima, joelho embaixo, ambos fechados e portanto imunes ao critério do anel. Com janela larga ela perde para um dos dois: 4 avatares grudaram na virilha, 1 caiu no joelho. Resolvido ancorando as janelas na virilha e calibrando pelas faixas medidas da própria biblioteca (ver `HEM_BELOW_CROTCH` / `WAIST_ABOVE_CROTCH`).
4. **Perseguir o vinco setor a setor PIOROU.** A hipótese era que a bainha modelada serpenteia e a reta passava perto dela em vez de em cima. Implementado, encheu a borda de farpas. Quem explicou foi um **render de emissão pura** — sem luz nenhuma, cinza = região pintada, vermelho = concavidade. Sem luz porque no render normal a sombra do degrau de tecido se confunde com a divisa de cor, e foi essa confusão que gerou a hipótese errada. O vinco da bainha é **fraco e praticamente horizontal**: a bainha já é um anel reto, e o `argmax` numa janela de 2 cm com sinal fraco só acha ruído de decimação. **Antes de fazer a borda perseguir um vinco, medir se o vinco tem sinal — e medir sem luz.**

### A borda: o corte é EXATO

Atribuir triângulo inteiro deixava dente-de-serra de ~6 mm — o **piso da quantização**, não ruído em cima dela; suavizar por maioria não tira. Agora a malha é **cortada na linha**: aresta que cruza a fronteira é partida no ponto de cruzamento e religada. Custo ~900 vértices de costura (+2,9% de triângulo), só na borda. O dist do `b05_d2` foi de 183 KB para **201 KB**.

> A linha escura logo acima da bainha no render **não é erro de pintura** — é a sombra do degrau de tecido modelado pela Meshy. Ela continua lá faça-se o que se fizer com a cor, e é ela que faz o olho ler "barra de short".

## 🔴 A LIÇÃO QUE CUSTOU MAIS CARO: conferir contra a SÉRIE não é conferir

O `zen_m_b12_d1` (IMC 148) passou como **"dentro da faixa"** com o cós **25 cm baixo demais**. O Rogério pegou no olho, olhando o render de costas.

**O motivo de eu não ter visto:** as duas travas que existiam eram internas. A de conexidade só pega ilha; o `--report` compara cada avatar **com a série** — e a série pode estar uniformemente errada, porque foi calibrada pelos próprios ajustes. **Não havia nada comparando o resultado com a INTENÇÃO.**

Agora há: **`scripts/shorts_ref.py`** mede o short **na folha de referência**, onde ele é literalmente preto sobre corpo cinza claro, e compara com o 3D. É externo ao detector e independente dele.

O instrumento nasceu errado também, e isso o validou: a 1ª versão acusou "short até os pés" em **todos os d3**. Padrão implausível demais para ser verdade — era a sombra dura entre as coxas dos corpos definidos lida como tecido. Corrigido para medir **fração da largura do corpo em faixa contígua** (sombra não cobre a largura; short cobre).

Com o medidor confiável: **38 dos 39 já batiam** com a referência dentro de ±0,06, a maioria dentro de ±0,02. Só o `b12_d1` estava errado — e era invisível para a outra régua.

**O conserto foi UM número.** A virilha dele tinha sido detectada em 0,297, que é onde as coxas param de se tocar, **não** a virilha anatômica (num IMC 148 as coxas encostam até quase o joelho). Como todas as janelas são ancoradas nela, o short inteiro desceu junto. As próprias relações da série diziam qual deveria ser: cós 0,528 e bainha 0,339 exigem virilha ≈ 0,37. Campo **`crotch_override_zh`** no mapa, que sobrevive a um `--fit` posterior. Resultado: cós 0,385 → **0,544** (referência 0,528).

> **Doutrina:** toda régua interna mede consistência, não correção. Uma biblioteca inteira pode estar coerente e errada. Manter sempre uma régua ancorada **fora** do gerador — aqui, a folha que originou a malha.

## Comandos do short

```
python scripts/shorts.py --fit --all      # detecta, grava o mapa, renderiza QA
python scripts/shorts.py --check --all    # so as travas, sem render (~6 min)
python scripts/shorts.py --report         # coerencia com a SERIE (instantaneo)
python scripts/shorts_ref.py              # coerencia com a REFERENCIA (instantaneo)
python scripts/shorts.py --apply --all    # grava os 2 materiais em 03_dist/glb/
```

`--fit` **propõe**; quem decide é o olho, avatar por avatar. Entrada com `"source": "manual"` não é sobrescrita por um `--fit` posterior.

## Travas automáticas do short (e por que cada uma existe)

| trava | pega | onde |
|---|---|---|
| região **conexa** | mão/antebraço pintado por falha da máscara de braço | sinaliza no `--fit`, **recusa** no `--apply` |
| lasca < 5% da maior peça | triângulos pretos soltos no corpo (5 avatares tinham) | apagada automaticamente |
| contagem de triângulos | export mexendo na malha | `--apply` |
| nome dos materiais | `Zenith_Body.001` indo para o app | `--apply` |
| faixa da série | erro grosso de altura | `--report` |
| folha de referência | série uniformemente errada | `shorts_ref.py` |

**Blender sai com código 0 mesmo com exceção no script** — um worker que estourou foi reportado como `[ok]`. A prova de sucesso é a linha `RESULT`, nunca o exit code.

## Estado do short — CONCLUÍDO

- **39/39** nas duas réguas · zero ilhas · série varrida no olho em ordem de IMC
- **39/39 aplicados** em `03_dist/glb/`, conferidos **no byte** (JSON do GLB): 2 primitives, `Zenith_Body` + `Zenith_Shorts`, `baseColorFactor` exato nos dois
- Peso: **203 KB de média** (era ~183 KB sem short), **7,7 MB** a biblioteca inteira — o orçamento era 1–3 MB *por avatar*, então sobra folga enorme
- Costura: +1.400 a +2.000 triângulos por avatar (~+2,5%), só na borda
- `02_master/` e `00_input/` **intocados**

**Pendências desta frente:**
1. **O short lê CINZA de costas, não preto.** O albedo já é quase preto (`#0D0D12`); o que lava é o specular de Fresnel pegando o kicker traseiro do HDR em ângulo rasante. É decisão do `zenith_material.py`, não da segmentação — e, como toda decisão de material, se resolve com `--apply --all` de novo em ~20 min, sem refazer mapa nem QA
2. `restyle.py` tem o mesmo bug de material não purgado que este script teve (`materials.clear()` esvazia o slot mas não apaga o datablock, então `bpy.data.materials.new("Zenith_Body")` devolve `Zenith_Body.001`). Não grava errado calado — a validação dele reprova — mas quebra sobre estes masters, que já trazem `Zenith_Body`
3. O `--report` do `shorts.py` e o `shorts_ref.py` **não conferem o traçado do cós**, só a altura. Um cós com curva azimutal esquisita mas topo certo passaria nos dois. Hoje isso só é pego no olho

## ⚡ ABRIR AQUI — o que mudou na sessão 3

| item | antes | agora |
|---|---|---|
| corpo | roxo `#8346C6`, metallic 0, rough 0.5 | titânio `#6D737B`, metallic 0.50, rough 0.35 |
| luz | nenhuma (IBL padrão do model-viewer) | `03_dist/env/zenith_env.hdr` (322 KB) |
| malha | 18k triângulos, ~64 KB | **60k triângulos, ~183 KB** |
| `test/compare/` | 6 GLBs roxos de LOD | apagado, junto com o seletor de resolução |
| masters 18k | — | preservados em `02_master_18k/` (fora do git) |

**39/39 PASS no reprocessamento em 60k**, todas as 8 validações, `tris_out` entre 59.990 e 60.000.

**🔑 Por que 18k caiu.** O alvo de 18k tinha sido calibrado **com o avatar roxo**, que escondia o custo da decimação. Assim que o corpo virou titânio com specular, a faceta apareceu e o relevo muscular ficou borrado. O peso final (183 KB com Draco, contra 1–3 MB de orçamento) mostrou que a restrição nunca foi o tamanho. **Lição: não calibrar densidade de malha com um material que esconde geometria.**

**Índice refeito sobre os masters de 60k** (`metrics.py --all` + `build_index.py`). As medidas mudaram pouquíssimo — delta médio de IMC **0,047**, máximo **0,20**, todos positivos (a decimação encolhia levemente o volume). Efeito colateral: o vão d3 que estava em 4,9 virou **5,0** e voltou para a lista `high`. São **2 vãos `high`** agora (d1 27,8→33,3 e d3 27,4→32,4), e o segundo é artefato de arredondamento, não regressão.

**🟠 O TESTADOR MOSTRAVA 30 DE 39 — pego pelo Rogério, e era bug de verdade.** Os botões eram gerados por laços da grade nominal (`b01`…`b12`), que nunca produzem os IDs com sufixo de inserção. Sumiam **exatamente os 9 avatares de inserção** (`b05h/i/j/k/m_d1`, `b05h_d2`, `b06h/i/j_d3`) — os mais caros da produção, os que fecharam vãos de cobertura. Os assets sempre existiram; era só a interface.

Consertado na raiz: o testador agora **lê o `library.json`** e monta a lista dali, ordenada por `measured_bmi` (que é o que o `ARCHETYPES.md` §4 exige para o teste de continuidade — ordenar por nome embaralha a escada de corpos). A lista `AVAILABLE`, mantida à mão, foi eliminada: ela já tinha apodrecido, com o comentário dizendo "36 masters" enquanto listava 39. **Lição: duplicar o índice na interface sempre apodrece; ler a fonte custa um `fetch`.**

**🟠 O TESTADOR SIMULAVA A REGRA DE CLASSIFICACAO ERRADA — corrigido.** Ele montava o id colando faixa nominal + definição (`"zen_m_" + b07 + "_d2"`) e usava a tabela de 12 faixas de IMC. Isso é a lógica **anterior ao schema 3**, revogada em 26/07 quando o `metrics.py` mostrou que o corpo não corresponde à faixa que o nome promete.

O caso que mostra o tamanho do erro: **120 kg / 1,75 m / 35% de gordura**.

| | avatar escolhido | IMC medido do corpo |
|---|---|---|
| regra antiga (nominal) | `zen_m_b12_d1` | **147,7** |
| regra do schema 3 | `zen_m_b06_d1` | **38,9** |

O usuário tem IMC 39,2. A regra antiga entregava um corpo de IMC 147. E os 9 avatares de inserção eram **inalcançáveis**: nenhuma combinação de sliders gera um id com sufixo.

Agora vale a regra do índice: definição pelo % de gordura, e dentro dela o de menor `|measured_bmi − IMC_alvo|`. **A correção de altura passou a existir** (`IMC_alvo = IMC × 1,75/altura`) — ela não estava implementada, e sem ela o testador dava um resultado que o app não daria. Conferido contra o spec em Python, 7/7 casos idênticos. Varrendo os sliders, **38 dos 39** avatares são alcançáveis; o único que nunca ganha é o `b12_d1` (IMC 147,7), cujo vizinho está em 107,3 — precisaria de IMC alvo > 127, fora do alcance dos sliders. Correto, não é bug.

**⚠️ O SHORT AGORA APARECE.** Em 60k a bainha e o cós do short da malha da Meshy viram vincos visíveis (linhas horizontais nas coxas e na cintura). Em 18k a decimação apagava isso. Não é defeito novo — é a pendência do short (`SHORTS_ENABLED=False`) ficando visível. É a próxima frente.

## 🟣→⬜ O AVATAR DEIXOU DE SER ROXO (27/07, sessão 3)

**Feito e verificado: os 39 `03_dist/glb/` estão com o material novo.** Conferido no byte (JSON do GLB): `Zenith_Body`, base `#6D737B`, metallic 0.50, roughness 0.35, nos 39.

O roxo saturado achatava o relevo muscular, que é o foco do app. **A identidade Zenith virou LUZ, não cor de corpo:**

| metade | onde vive | conteúdo |
|---|---|---|
| material | `scripts/zenith_material.py` (fonte única) | titânio `#6D737B` · metallic 0.50 · roughness 0.35 |
| iluminação | `scripts/make_env.py` → `03_dist/env/zenith_env.hdr` (322 KB) | key fria estreita · kicker traseiro · 2 rims roxos laterais · fill azul |

**🔑 A luz fora do GLB já se pagou.** O Rogério reprovou a 1ª versão: *"a cor ficou mais pra prateado"*. Ele estava certo — a key era quase branca (`#E4EAF6`) e forte (42), e com metallic 0.50 isso estoura o specular em branco puro: o corpo lê como **aço polido**, não titânio. Em PBR a cor do corpo não vem só do `baseColor`; metade vem do que ele reflete. Esfriar a key para `#93B4EC` e baixar para 24 devolveu o titânio **sem tocar em um GLB sequer** — trocou-se um arquivo de 322 KB.

**⚠️ Metade do visual mora FORA do GLB e o app precisa saber disso.** glTF não transporta iluminação de forma portável — o model-viewer (e o `model_viewer_plus`, que é o mesmo componente numa WebView) ilumina por IBL, via `environment-image`. Sem carregar o HDR, o avatar aparece cinza e sem identidade. O lado bom: reajustar a luz da biblioteca inteira **troca um arquivo de 325 KB**, não re-processa 39 avatares.

**`scripts/restyle.py` é o caminho para mexer em cor daqui pra frente.** Ele lê `02_master/`, troca só o material e regrava `03_dist/glb/` — **sem re-decimar e sem tocar em master** (a decimação Collapse não é determinística: re-rodar o `process.py` mudaria a topologia que passou no QA, além de violar a regra 7). `--preview {id}` renderiza 4 vistas com o ambiente em `qa/look/{id}/`.

### As três coisas que essa sessão aprendeu errando

1. **Anel uniforme não é rim, é luz ambiente.** A 1ª versão do HDR era invariante em azimute "por robustez". Saiu chapada: luz igual de todos os lados = contraste zero. Simetria total é o oposto de direcionalidade.
2. **A convenção de azimute foi MEDIDA, não deduzida — e o palpite errou por 180°.** A key caiu atrás do avatar e os dois rims roxos na frente dele. O sintoma ("roxo e chapado de frente, bonito de costas") foi diagnosticado como desequilíbrio por várias iterações. A sonda está descrita no cabeçalho do `make_env.py`: esfera difusa com vermelho em az 0, verde em az 90, azul em az 180.
3. **Metallic alto AJUDA — minha previsão estava errada.** Eu argumentei que metallic ≥ 0.5 apagaria o corpo no fundo escuro. Uma varredura 3×3 de roughness × metallic mostrou o contrário: é o **specular** que desenha o músculo, e o difuso é que achata. O argumento pressupunha ambiente escuro, e o ambiente Zenith tem fontes brilhantes.

**Bug latente corrigido de quebra:** `make_material` procurava o nó por nome (`"Principled BSDF"`), mas o Blender desta máquina está **em português** e o nó se chama `"BSDF - Pré-fundamentado"`. Dentro de um `if bsdf:`, isso exportaria o material com valores PADRÃO, sem erro. Só não quebrou porque `read_factory_settings()` reseta o idioma antes. Agora a busca é por `bl_idname` e levanta exceção se não achar.

**Verificação no navegador é parte do fluxo agora.** O preview do Blender não é o runtime: o `.claude/launch.json` sobe um `http.server` na 8765 e o resultado é conferido no model-viewer de verdade. Foi lá que apareceu o roxo excessivo nas costas — que o Blender não mostrava — e que motivou o kicker traseiro.

**Pendências desta frente:** o `--preview` do `restyle.py` usa view transform `Standard` para aproximar o tonemap do model-viewer; não é idêntico, o navegador dá mais roxo. **Decidir 18k/40k/60k é o próximo passo**, e o Rogério pediu para **remover os controles do testador** depois disso. O short (`SHORTS_ENABLED=False`) continua parado e é a próxima frente depois do LOD — a expectativa dele é que seja um a um.

## ⚡ ABRIR AQUI NA SESSÃO NOVA — o que fazer agora

**A onda masculina acabou. Não gerar mais folha nem baixar mais GLB sem motivo novo.** O que sobra não é produção, é infraestrutura:

1. **Ambiente de testes** (o pedido do Rogério ao encerrar esta sessão). Hoje existe só o `test/avatar_tester.html`, que lê `03_dist/glb/` por caminho relativo e **precisa de http (localhost), nunca `file://`** — e só abrir quando ele pedir ([[testador-so-localhost-sob-pedido]]).
2. **Folha de contato de QA ordenada por `measured_bmi`** — nunca foi montada. É o item mais importante do checklist humano (`ARCHETYPES.md` §8, teste da continuidade) e **tem de ser ordenada pela medida, não pelo nome do arquivo** (`ARCHETYPES.md` §4).
3. **Commit pendente** (não feito porque não foi pedido — perguntar antes): `scripts/intake.py` novo, mais `CLAUDE.md`, `docs/CHARACTER_BIBLE.md`, `state.md`, `library.json`, `logs/process.log`, `metrics/library_metrics.json` e `test/avatar_tester.html` modificados. **Os GLBs não entram no git de propósito** (`.gitignore` cobre `01_raw/`, `02_master/`, `03_dist/`, `qa/`, `00_input/`) — a linha antiga deste bloco dizendo "os avatares estão untracked" estava enganando: é intencional.
3b. **⚠️ RISCO REAL DE PERDA: `00_input/sheets/` está fora do git e é IRREPRODUZÍVEL.** São as 39 folhas-mãe da biblioteca; regerar não devolve o mesmo personagem. O próprio `.gitignore` avisa que precisa de backup externo, e esse backup **não existe**. Tratar como prioridade antes de qualquer refatoração de pastas.
4. Pendências antigas que seguem paradas: `render.py` (turntable) não existe e talvez não precise; short desligado (`SHORTS_ENABLED=False`); grade feminina PENDENTE (precisa ser reescrita de 6 para 12 faixas antes de qualquer geração).

### Números finais da onda masculina

| | |
|---|---|
| Avatares | **39** (15 nominais d1 + 12 d2 + 10 d3 + inserções) |
| Todos | 9/9 validações, 18k tri, medidos, no `library.json` schema 3 e no tester |
| Eixo de IMC coberto | d1 16,1→147,6 · d2 19,7→111,8 · d3 19,9→53,8 |
| Vãos `high` | **1** (d1 27,8→33,3) |
| Vãos `low` | 8, todos em IMC 38+ — quase sem população, não valem geração |

## 🔴🔴 O VÃO d1 27,8→33,3 NÃO FECHA — 3 tentativas, e a 3ª saiu pelo outro lado

**`zen_m_b05m_d1` PROCESSADO. 39 avatares.** Cru 120.974 tri, decimação 0,1488, 18.000 tri, 9/9. Medido: **IMC 26,9 · 82,4 kg · cint/alt 0,537 · cintura 94,0 · peito 100,8 · bíceps 30,4**. Var. altura da folha **0,21% — a melhor de toda a produção**. QA em `qa/inspect/zen_m_b05m_d1/`. No tester.

**Mirado em ~30, caiu em 26,9 — ABAIXO da borda inferior do vão (27,8).** O vão seguiu intacto em 5,5.

**As três tentativas, e o que cada uma prova:**

| folha | par de âncoras (topo) | descritor | pouso |
|---|---|---|---:|
| `b05j_d1` | `b05h`+`b05` (27,8) | obesidade | **34,0** |
| `b05k_d1` | `b03`+`b04` (24,4) | "OBESIDADE GRAU I" | **33,3** |
| `b05m_d1` | `b02`+`b03` (20,4) | "SOBREPESO, não obeso" | **26,9** |

Baixar a âncora de 27,8 → 24,4 moveu o pouso **0,7** (captura pelo atrator ~33,5 do Gemini na d1). Trocar o **nome da categoria** moveu **6,4** de uma vez, e passou do alvo. **Confirma a doutrina do §5c item 5 com número: quem manda no pouso é o SUBSTANTIVO DE CATEGORIA, não a âncora.** A âncora ajusta dentro da categoria; o substantivo escolhe em qual atrator o corpo cai. Não existe categoria nomeável entre "sobrepeso" (~27) e "obesidade grau I" (~33,5), e é exatamente isso que o vão é: **o vazio entre dois atratores do gerador.**

**Recomendação registrada: ACEITAR o vão de 5,5 e encerrar a onda masculina.** Já foram gastas 3 gerações e 3 rodadas de Meshy nele. O gerador não tem corpo ali. A cobertura em volta é boa (26,2 · 26,9 · 27,8 de um lado; 33,3 · 34,0 do outro), e o meio se resolve por **shape keys** no sistema híbrido — os insumos (`circumferences_cm`) já viajam no `library.json` desde o schema 3.

> **Nenhum dos três é desperdício.** O `b05m_d1` adensou a fronteira normal/sobrepeso (26,2 · 26,9 · 27,8), que é zona de muito usuário. Doutrina de sempre: inserção, nunca substituição ([[distribuicao-e-visao-hibrida]]).

**Nota de nomenclatura:** a sequência de inserção da d1 é `h · i · j · k · m` — **o `l` foi pulado de propósito**, porque `b05l_d1` se lê como `b051_d1` no `logs/process.log`, que é append-only.

## `zen_m_b05k_d1` — a tentativa 2

**`zen_m_b05k_d1` PROCESSADO.** Cru 131.062 tri, decimação 0,1373, 18.000 tri, 9/9, simetria média 0,00032 m. Medido: **IMC 33,3 · 101,9 kg · cint/alt 0,637 · cintura 111,4 · peito 109,7**. Var. altura da folha 0,28% — **a melhor de toda a produção**. QA em `qa/inspect/zen_m_b05k_d1/`. No tester.

**O vão d1 NÃO fechou: 27,8→34,0 (6,2) virou 27,8→33,3 (5,5), e o corte de `high` é 5,0.** Ganho marginal. Mirado em ~31, caiu em 33,3, colado no `b05j_d1` (34,0).

**🔴 O GEMINI TEM UM ATRATOR EM ~33,5 NA LINHA d1 — e ele explica os dois pousos.** Duas âncoras bem diferentes entregaram praticamente o mesmo corpo:

| folha | par de âncoras | topo | pouso | delta |
|---|---|---|---:|---:|
| `b05j_d1` | `b05h`+`b05` | 27,8 | **34,0** | +6,2 |
| `b05k_d1` | `b03`+`b04` | 24,4 | **33,3** | +8,9 |

Baixar a âncora em 3,4 moveu o pouso em 0,7. **Quando o pouso é insensível à âncora, não é regra aditiva — é captura por atrator** (mesmo padrão do atrator obeso ~40 do ChatGPT, que capturou 3 tentativas). A regra aditiva só descreve o comportamento em espaço aberto; dentro do raio de um atrator ela não vale, para nenhum gerador.

**Suspeita a testar: o descritor apontou para o atrator.** Escrevi "este corpo é um caso de OBESIDADE GRAU I", que é exatamente a faixa 30–35 onde o atrator mora — o mesmo erro do `b06i_d3` (§5c item 7). Ainda não foi tentado na d1: âncora baixa **junto com** nome de categoria abaixo do alvo ("SOBREPESO", não "obesidade").

**`zen_m_b06j_d3` PROCESSADO. 37 avatares. O vão `high` da d3 FECHOU.** Cru 179.778 tri, decimação 0,1001, 18.000 tri, 9/9, altura crua 1,899 m. Medido: **IMC 32,3 · 98,9 kg · cint/alt 0,498 · peito 109,0 · cintura 87,2 · bíceps 44,1**. Var. altura da folha 0,34% (a melhor das 5 folhas do Gemini). QA em `qa/inspect/zen_m_b06j_d3/`. No tester.

O vão 27,4→34,6 (7,2) virou 27,4→**32,3** (4,9) + 32,3→34,6 (2,3) e saiu da lista. **Sobrou um `high` na biblioteca inteira: d1 27,8→34,0.**

**🔑 A REGRA ADITIVA É DO GERADOR, NÃO UNIVERSAL — o +6,5 é do ChatGPT.** No Gemini, na d3, o delta sobre a âncora de topo mediu **+3,3** (`b06i`) e **+4,9** (`b06j`). Aplicar o +6,5 do ChatGPT foi o que fez o `b06i` cair abaixo do vão — a culpa **não** era só do descritor, como a sessão anterior concluiu. Corrigido pela âncora: subir o par de `b04+b05` (topo 23,7) para **`b05+b06` (topo 27,4)** levou o corpo de ~27 para 32,3, com o MESMO descritor.

> Cuidado: esse mesmo par `b05+b06` no **ChatGPT** entregou 34,6 e 35,7 (+7,2/+8,3). O par não determina o pouso; o par **mais o gerador**, sim.

**🟠 Uma folha foi REJEITADA sem gastar Meshy, e a régua 2D acertou.** A g1 do `b06j` mediu 13,9/31,1 contra 13,9/31,4 do `b06i` — mesma folha, na prática. Comparação válida porque é **mesmo gerador, mesma linha, mesma pose**, que é exatamente o caso de uso do `measure.py`. A g2 mediu 15,5/33,4, entre os vizinhos do vão, e o 3D confirmou. **Folha duplicada não vira avatar:** a regra "nunca descartar" vale para master produzido, não para folha reprovada antes da Meshy (precedente: g1 do `b06_d3`).

**🔴 FLUXO CORRIGIDO — arquivo nenhum entra no repo pela mão do Rogério.** Ele cobrou nesta sessão: *"o fluxo é você pega em downloads, apaga selo do gemini, recorta e me devolve as 3 folhas"*. Estava certo e não estava documentado. Escrito o **`scripts/intake.py`**: pega a imagem mais recente do Downloads, acha e apaga o selo, grava em `00_input/sheets/{id}_sheet.png`, recusa sobrescrever sem `--force`. `CLAUDE.md` e `CHARACTER_BIBLE.md` §6 corrigidos.

**⚠️ O `intake.py` teve um bug que ia apagar UMA MÃO — a correção importa.** A 2ª folha do Gemini tem o fundo o dobro de granulado (ruído 27 contra 13); o limiar adaptativo subiu para 54, **o selo ficou ABAIXO dele** e pedaços do corpo viraram blobs soltos — o script elegeu um blob 21×59 na coluna do perfil, que era uma mão. Não usar a máscara de figura do `crop.py` para achar selo. Dois critérios que o corpo não satisfaz: **mais claro que o fundo em todos os canais** (sombra e vinco são mais escuros) e **20 px de fundo limpo em volta** (pedaço de corpo tem corpo do lado). Testado nas 5 folhas do Gemini: 5 selos achados, todos **96×96 px**, resíduo 0; nenhum falso positivo na do ChatGPT. Em 4 das 5 o selo saiu em `y 1248–1343`.

**Próximo passo:** o último vão `high` — **d1 27,8→34,0**, alvo ~31. Pela regra do gerador, no Gemini o delta é ~+4 sobre a âncora de topo, o que pede um par com topo em ~27: **`b05h_d1` (26,2) + `b05_d1` (27,8)**. É o mesmo par que o ChatGPT usou para entregar 40,7 e o Gemini para entregar 34,0 — com passo de par pequeno (1,6), esperar pouso entre 31 e 34. Se voltar colado no 34,0, considerar o vão fechado o bastante e encerrar a produção masculina.

## ⚡ Bloco da sessão anterior (27/07, fim do dia)

**A sessão de hoje testou o GEMINI como segundo gerador e produziu 3 avatares.** Placar: **2 acertos, 1 erro** — e o erro tem causa identificada e é minha, não do Gemini (ver 🟡 abaixo).

| avatar | gerador | vão mirado | IMC | resultado |
|---|---|---|---|---|
| `zen_m_b05j_d1` | Gemini | d1 27,8→38,8 | **34,0** | ✅ meio do vão; 11,0 → 6,2 |
| `zen_m_b05h_d2` | Gemini | d2 26,7→35,0 | **30,6** | ✅ abaixo do meio; vão saiu de `high` |
| `zen_m_b06i_d3` | Gemini | d3 27,4→34,6 | **27,0** | ❌ caiu ABAIXO do vão, colado no `b06_d3` |

**Todos processados 9/9, medidos, no índice, no tester e com QA renderizado.** Nada pendente de pipeline.

**As 3 lições da sessão, em ordem de importância:**
1. **Trocar de gerador é uma ferramenta** — o buraco de IMC 28–38 era do ChatGPT, não do problema (bloco 🟢).
2. **A metade baixa de um vão se alcança com ÂNCORA BAIXA + regra aditiva** (bloco 🟢🟢). Revogou a lição mais resignada do Character Bible.
3. **A regra aditiva tem limite e eu achei o limite errando** (bloco 🟡).

**Próximo passo sugerido:** refazer o `b06i_d3` — quer dizer, **gerar OUTRO** para o vão d3 (nunca substituir), agora com o descritor corrigido do bloco 🟡. E depois o vão d1, que continua aberto em 27,8→34,0.

**Pendências que NÃO bloqueiam:** nada commitado ainda (o repo tem 1 commit e os 36 avatares estão untracked); folha de contato de QA ordenada por `measured_bmi` nunca foi montada; short ainda desligado (`SHORTS_ENABLED=False`).

## 🟡 O ERRO DO `b06i_d3` (27/07) — EU NOMEEI O ATRATOR NO DESCRITOR

**`zen_m_b06i_d3` PROCESSADO. 36 avatares.** Cru 166.512 tri, decimação 0,1081, 17.996 tri, 9/9, simetria média 0,00037 m. Medido: **IMC 27,0 · 82,6 kg · cint/alt 0,455** (a cintura mais seca da biblioteca, 79,7 cm · bíceps 40,2). QA em `qa/inspect/zen_m_b06i_d3/`.

**Mirado no vão d3 (27,4→34,6), caiu em 27,0 — ABAIXO do vão.** O vão não encolheu nada.

**A causa está no descritor que EU escrevi, e é um erro de leitura da própria doutrina.** O `CHARACTER_BIBLE.md` §5c item 5 registra que existe um atrator "musculoso e seco de academia" em ~32 de ombro, e que o que tira o corpo dele é **nomear a categoria fisiculturista**. No descritor eu escrevi o inverso exato: *"É um atleta de academia avançado, NÃO um fisiculturista de competição."* Ou seja, apontei para o atrator e fechei a saída. O corpo entregue mediu ombros 31,4 — em cima do atrator.

**Isso é bom, na verdade:** o erro é atribuível e corrigível, não é limite do Gemini nem da regra aditiva. **A próxima folha do vão d3 deve usar o par `b04_d3`+`b05_d3` de novo, MAS com o descritor invertido** — nomeando fisiculturista/classic physique e declarando que a definição já está no teto e o que cresce é VOLUME.

**Limite descoberto na regra aditiva (+6,5):** aqui o delta foi **+3,3** (âncora de topo `b05_d3` 23,7 → 27,0), metade do previsto. As amostras da d3 agora são +7,2 · +8,3 · **+3,3**. A regra aditiva **não é universal — ela quebra quando o pedido cai em cima de um atrator**, que é a mesma ressalva que já valia para o fator multiplicativo. Registrado no §5c item 7.

## 🟠 BUG DO `crop.py` CORRIGIDO (27/07) — ele não estava validando altura

**A folha `zen_m_b06i_d3` fez o `crop.py` reportar "variação 0,20%, altura 1533px". Os dois números eram falsos** — a figura real tem 1470px e a variação real é 0,41%. O fundo das folhas do Gemini é mais granulado que o do ChatGPT e o **ruído sozinho passava do `FG_THRESHOLD` fixo (18)**, esticando a bbox até a borda do canvas.

Impacto: a figura saía ~4% menor no recorte (cosmético, a Meshy não liga) e, o que importa, **a validação de altura entre as vistas passava a medir o canvas em vez do corpo** — justo a única checagem que o pipeline não consegue refazer depois (§5b item 6).

**Corrigido com duas mudanças no `crop.py`:**
- **limiar adaptativo:** mede o piso de ruído numa faixa de borda (percentil 99,5) e exige 2× isso, com piso no `FG_THRESHOLD` antigo. O log agora imprime `ruido -> limiar`.
- **linha/coluna só conta como figura** se tiver ≥0,5% da dimensão perpendicular em pixels de frente (piso de 3 px), matando ruído isolado.

Regressão conferida em 8 folhas: **as 6 do ChatGPT não mudaram nada.** As 2 folhas Gemini anteriores estavam levemente contaminadas e os números reais são **melhores** que os reportados na hora (`b05j_d1` 0,49→0,28% · `b05h_d2` 0,95→0,52%) — nenhum avatar foi aceito indevidamente. Os 3 recortes do Gemini foram regravados com o script corrigido.

## 🟢🟢 n=2 NO GEMINI — E A METADE BAIXA DO VÃO FOI ALCANÇADA (27/07)

**`zen_m_b05h_d2` PROCESSADO — 2ª folha Gemini. 35 avatares.** Cru 136.778 tri, decimação 0,1316, 18.000 tri, 9/9, simetria média 0,00033 m. Medido: **IMC 30,6 · 93,6 kg · cint/alt 0,587**. Var. altura da folha 0,95%. QA em `qa/inspect/zen_m_b05h_d2/`.

**O vão d2 SAIU da lista `high`:** 26,7→35,0 (8,3) virou 26,7→**30,6** (3,9) + 30,6→35,0 (4,4). Restam só dois `high`: d3 (27,4→34,6) e d1 (27,8→34,0).

**⚠️ 2/2 — o Gemini entrou no vão nas duas linhas.** Não é mais sorte de uma amostra. O que ainda NÃO está provado é que ele seja melhor em geral: o que se sabe é que **os atratores dele ficam em outro lugar**. Ele terá zonas mortas próprias, ainda não encontradas. Doutrina: manter os dois geradores e sacar o Gemini quando o alvo cair em zona morta comprovada do ChatGPT.

**🔑 A ÂNCORA BAIXA FUNCIONOU — a metade baixa do vão deixou de ser inalcançável.** Em vez do par adjacente ao buraco (`b04_d2`+`b05_d2`, topo 26,7), usei um par mais BAIXO (`b02_d2`+`b04_d2`, topo **22,5**, abaixo da borda inferior do vão). Resultado: 30,6, **abaixo do ponto médio do vão** (30,85). **Nenhuma inserção anterior tinha chegado perto disso** — todas colaram no vizinho de cima (1,1 e 1,2 de distância). Isso derruba a resignação do `CHARACTER_BIBLE.md` §5c item 7.

**🔑 A REGRA DE PLANEJAMENTO QUE FUNCIONA É ADITIVA, NÃO MULTIPLICATIVA.** Fator de passo não prevê nada (as amostras vão de 1,9× a 8,0×). O que prevê: **pouso ≈ âncora de topo + 6,5 de IMC**, quase independente do passo pedido. O modelo tem um passo MÍNIMO e ignora pedidos menores que ele.

| avatar | âncora de topo | passo pedido | pouso | delta |
|---|---|---|---|---|
| `b05h_d1` | 24,4 | 2,6 | 26,2 | +1,8* |
| `b06h_d3` | 27,4 | 3,7 | 34,6 | +7,2 |
| `b07_d3` | 27,4 | 3,7 | 35,7 | +8,3 |
| `b05j_d1` (Gem) | 27,8 | 1,6 | 34,0 | +6,2 |
| `b05h_d2` (Gem) | **22,5** | 1,7 | **30,6** | +8,1 |
| `b05i_d1` (GPT) | 27,8 | 1,6 | 40,7 | +12,9† |

\* medida 2D falhou nessa folha, ver bloco abaixo · † capturado pelo atrator obeso do ChatGPT

**Uso prático: para mirar IMC X, escolher o par cujo membro SUPERIOR esteja em ~X−6,5** — mesmo que esse par esteja bem abaixo do buraco. Foi assim que a metade baixa saiu.

**⚠️ O `measure.py` NÃO ATRAVESSA TROCA DE GERADOR — em direção nenhuma.** Não é viés constante, é ruído: no `b05j_d1` ele SUBESTIMOU (leu na metade baixa, o 3D deu metade alta); no `b05h_d2` ele SUPERESTIMOU (leu 17,9 contra 18,0 do `b06_d2`, ou seja "no topo do vão", e o 3D deu 30,6, no meio). **Em folha do Gemini, não usar o `measure.py` para prever posição — só o `metrics.py` decide.** Ele continua servindo para o que sempre serviu: ordenar folhas do MESMO gerador com a MESMA pose.

## 🟢 O ATRATOR É DO GERADOR, NÃO DO PROBLEMA (27/07) — Gemini entra na faixa que o ChatGPT recusa

**`zen_m_b05j_d1` PROCESSADO — 1ª folha gerada no GEMINI. 34 avatares.** Cru 147.978 tri, decimação 0,1216, 18.000 tri, 9/9, simetria média 0,00030 m. Medido: **IMC 34,0 · 104,0 kg · cint/alt 0,631**. Var. altura da folha 0,49%. QA em `qa/inspect/zen_m_b05j_d1/`.

**⚠️ ELE CAIU DENTRO DO BURACO "IMPOSSÍVEL", NO MEIO, DE PRIMEIRA.** O vão d1 era 27,8→38,8 (salto 11,0). Três tentativas no ChatGPT nunca entraram nele — caíram em 38,8 · 39,8 · **40,7**, todas em cima do atrator obeso. O Gemini, **mesmo prompt e mesmas referências**, entregou 34,0. O vão virou 27,8→34,0 (6,2) + 34,0→38,8 (4,8).

**Isso REVOGA a conclusão do bloco 🔴🔴 ("as lacunas não se preenchem por prompt").** A formulação correta é: **as lacunas são o negativo dos atratores DAQUELE gerador.** O buraco de 28–38 é um vazio na distribuição do ChatGPT, não do problema. Trocar de gerador é uma ferramenta nova — e é a primeira em três sessões.

**Consequência para o híbrido de shape keys:** volta a ser refinamento futuro, deixa de ser "provavelmente a única forma de cobrir 28–38". Não descartar; despriorizar.

**Também quebrou a regra da metade baixa (§5c item 7).** Toda inserção anterior caiu colada no vizinho de cima (`b06h_d3` a 1,1 do b07; `b05h_d1` a 1,2 do b06). Esta caiu a **4,8 do vizinho de cima** — perto do meio do vão. É a maior redução de buraco já conseguida (11,0 → 6,2 contra 8,3 → 7,2 da melhor anterior).

**O OVERSHOOT do Gemini foi 3,9× — menor que o do ChatGPT, mas MUITO acima de 2×.** Mesmas âncoras do `b05i_d1` (`b05h_d1`+`b05_d1`, passo 1,6, topo 27,8): ChatGPT entregou +12,9 (**8,0×**), Gemini entregou +6,2 (**3,9×**). Ou seja, a ressalva do §5c item 6 ("perto de um atrator forte o passo explode") vale para os dois — o Gemini só é **menos** capturado. **Não existe fator confiável para planejar alvo no Gemini com n=1;** o que dá para dizer é que ele erra para cima, menos que o ChatGPT.

**⚠️ n=1. Não declarar propriedade do Gemini ainda.** Uma amostra não separa "atratores melhores" de sorte. O teste que decide é repetir nos outros dois vãos `high` — **d2 (26,7→35,0)** e **d3 (27,4→34,6)**. Se entrar nos dois, é propriedade; se voltar a colar no vizinho de cima, foi sorte.

**Operacional do Gemini, aprendido nesta folha:**
- **Ele carimba um selo (estrelinha SynthID visível) no canto inferior direito.** Nesta folha ficou em `x 2464–2559, y 1240–1345` do canvas, **dentro do recorte das costas**. O `crop.py` NÃO acusa: o selo cai dentro da coluna da vista em vez de virar uma 4ª figura, então passa batido e vai para a Meshy como mancha sobre fundo liso. **Conferir e apagar o selo em toda folha do Gemini antes do crop** (copiar fundo limpo por cima; resíduo aceito ≤ 6).
- Estilo e nível de definição bateram com a série do ChatGPT — mesmo mannequin cinza fotorreal. Não houve quebra de continuidade visual.
- **A pose é mais fechada:** braços mais colados ao corpo (recorte de perfil 270px contra 300–334 dos vizinhos ChatGPT). Isso faz o `measure.py` **subestimar** a barriga — leu 19,8 (previa metade baixa do vão) e o 3D deu 34,0 (metade alta). Mais uma confirmação de que a régua 2D não atravessa mudança de pose, e agora nem de gerador.
- **O short é mais comprido e tem costura/textura.** Com `SHORTS_ENABLED=False` a bainha vira uma crista visível atravessando as coxas, mais baixa que nos demais avatares. Entra na pendência já parcada do short, não é defeito novo.

---

Fase anterior (26/07): **d3 em produção — a grade nominal foi ABANDONADA no topo da d3.** d1 completa (12/12), d2 completa (11/11), d3 com b02→b08. **Total: 31 masculinos.** `b09_d3`/`b10_d3` **não serão produzidos** (cairiam em IMC ~65 e ~80, corpo de ninguém); no lugar deles entram **inserções nos buracos de cobertura**. Próximo: `b06h_d3` (folha aprovada e cropada, falta a Meshy).

**Série d3 medida:** barriga b02 12,5 · b03 12,5 · b04 13,3 · b05 13,7 · b06 15,1 · b07 17,4 — ombros b02 27,6 · b03 28,8 · b04 29,3 · b05 30,3 · b06 32,3 · b07 36,7.

## ⚡ ABRIR AQUI NA SESSÃO NOVA (26/07, fim do dia)

**Feito nesta sessão:** `b05_d3`, `b06_d3` e `b07_d3` produzidos ponta a ponta. **30/32.** E, mais importante que os avatares: **`scripts/metrics.py` e `scripts/build_index.py` escritos, os 29 masters medidos, e a classificação da biblioteca inteira refeita sobre medida real** (ver bloco 🔴 abaixo).

## 🟠 A d3 SAIU DA GRADE NOMINAL (26/07) — passou a preencher buracos

## 🔴🔴 O ACHADO ESTRUTURAL (27/07) — AS LACUNAS SÃO O NEGATIVO DOS ATRATORES
> ⚠️ **REVOGADO EM PARTE pelo bloco 🟢 no topo (mesmo dia, mais tarde).** A conclusão "não se preenche por prompt" valia para o ChatGPT. O Gemini entrou no buraco de primeira. O que continua válido: dentro de UM gerador, insistir na formulação não tira o corpo do atrator.

**`b05i_d1` PROCESSADO (3ª inserção). 33 avatares.** 18.000 tri, 9/9, simetria média 0,00039 m. Medido: **IMC 40,7 · 124,7 kg**. Var. altura da folha 0,47%.

**Ele foi mirado em IMC ~31 e caiu em 40,7 — ACIMA do `b06_d1` (38,8), passando por cima do vão inteiro.** Âncoras `b05h_d1`+`b05_d1`, passo pedido 1,6; entregue **+12,9**. Não foi o fator 2×, foi **8×**.

**Onde ele foi parar denuncia a causa:** d1 agora tem 38,8 · 39,8 · **40,7** — três corpos empilhados. É o **atrator obeso** ("~40% de barriga") já registrado na lição d1.

**⚠️⚠️ CONCLUSÃO: o buraco de IMC 28–38 NÃO é falha de prompt. O modelo não produz corpos ali.** As lacunas da biblioteca são o **negativo dos atratores do ChatGPT** — regiões vazias na distribuição do gerador. Mesmo padrão na d3: duas gerações caíram em ~35 e o alvo 31 nunca apareceu. **Parar de tentar preencher 28–38 por prompt; não é questão de achar a formulação certa.**

**⚠️ Isso PROMOVE o sistema híbrido de shape keys** ([[distribuicao-e-visao-hibrida]]): deixa de ser refinamento futuro e passa a ser **provavelmente a única forma de cobrir 28–38**. Os insumos já existem — `circumferences_cm` viaja no `library.json` desde o schema 3.

**Revisão da lição do fator 2× (`CHARACTER_BIBLE.md` §5c item 6):** o fator ~2× vale quando o alvo cai em **espaço aberto**. Quando o alvo cai **entre uma âncora e um atrator forte**, o atrator vence e o passo explode. O tamanho do passo não é controlável nessa situação, por nenhuma formulação testada.

**Formulação nova que FUNCIONOU (vale manter):** para pares de âncoras muito parecidas, em vez de pedir "diga qual é a etapa mais recente" (que com corpos próximos convida ao erro), pedir **"um corpo mais pesado que os DOIS anexos, com o passo do tamanho da diferença entre eles"**. Dispensa a identificação. O modelo entendeu e executou a direção corretamente — o que falhou foi só a magnitude, por causa do atrator.

**⚠️ O NÚMERO 32 NÃO É META (Rogério, 27/07).** "Não precisamos fechar exatamente com 32 avatares, pode passar o número; o importante é aproveitar todos que fizemos e fechar as lacunas que faltam." **A meta é COBERTURA, não contagem.** Produzir enquanto houver buraco `high` no `coverage_gaps`, e parar quando os vãos na faixa IMC 17–40 estiverem aceitáveis — não quando um contador bater num valor.

**`b05h_d1` PROCESSADO (2ª inserção). 32 avatares.** Cru 121.406 tri, decimação 0,148, 18.000 tri, 9/9, simetria média 0,00033 m (a melhor da produção). Medido: **IMC 26,2 · 80,2 kg · cint/alt 0,530**. Var. altura da folha 1,04% — a maior já aceita — e **não deixou marca**: proporções normais no render.

**⚠️ ELE NÃO FOI PARA ONDE FOI MIRADO, E A RÉGUA 2D É A CULPADA.** Pedido para o vão b05→b06 (IMC 27,8→38,8), caiu em **26,2 — ABAIXO do b05_d1**. A régua 2D dizia o contrário (barriga 22,3 contra 17,2 do b05_d1, ou seja "bem maior"). O 3D é coerente: ele é intermediário monotônico entre `b04_d1` (24,4) e `b05_d1` (27,8) em pescoço, peito, cintura, quadril, bíceps e panturrilha.

**A causa: a silhueta do `measure.py` INCLUI OS BRAÇOS.** Nessa folha o braço pende mais à frente, inflando a "profundidade da barriga"; o mesmo vale para a medida de ombros (2D dizia 34,0, mas o peito 3D é 102,0 contra 102,5 do b05_d1, e o bíceps é MENOR). Enquanto a pose ficou constante o erro foi constante e a ordem da série se manteve; **quando a pose variou, a ordem inverteu.** Aviso gravado no cabeçalho do `measure.py`. **Regra: folha se julga no `measure.py`, avatar se decide no `metrics.py`.**

**O avatar fica** — adensa a fronteira normal/sobrepeso, zona de muito usuário. **O buraco grande da d1 (27,8→38,8, salto 11,0) continua intocado** e segue como o alvo `high` nº 1.

**⚠️ Sufixo `h` marca INTENÇÃO, não posição.** O `b05h_d1` foi pedido para o vão b05→b06 e ficou entre b04 e b05. Não importa e não se renomeia: quem ordena é o `measured_bmi` (renomear só moveria a inconsistência para o `process.log`, que é append-only). A folha de contato do QA deve ordenar por `measured_bmi`, não por nome de arquivo. Documentado em `ARCHETYPES.md` §4.

**`b08_d3` PROCESSADO (7º da d3).** Ombros 42,7 (+5,9), barriga 20,2, var. altura 0,23%. Cru **317.528 tri — recorde absoluto**, decimação **0,0567** (a mais agressiva já rodada), 18.000 tri, 9/9, simetria média 0,00068 m. Definição sobreviveu. Medido: **IMC 53,8 · 164,7 kg · bíceps 61,7 cm**. QA em `qa/inspect/zen_m_b08_d3/`. No tester.

**⚠️ O prompt pediu cintura estreita e NÃO segurou.** Cintura foi de 85,4 → **103,8 cm** e a razão cintura/altura de 0,488 → **0,593**: ele não ficou só maior, ficou proporcionalmente mais grosso (rótulo automático virou "cheio", contra "magro" do b07). Os gomos continuam, então ainda lê como d3, mas a premissa de secura da linha começou a ceder no extremo.

**A rampa não saturou — acelerou.** Passos de ombro da d3: `+1,2 · +0,5 · +1,0 · +2,0 · +4,5 · +5,9`. Trocar o atrator no b07 não destravou um degrau, destravou uma rampa. Seguindo ela, `b09_d3`/`b10_d3` cairiam em ombros ~48 e ~54 (IMC ~65 e ~80) — **corpos que o classificador nunca escolheria.**

**Decisão do Rogério (26/07): não produzir b09/b10 da d3; usar os avatares para PREENCHER OS BURACOS.** Coerente com [[distribuicao-e-visao-hibrida]]: inserção, não substituição. Buracos da d3: **27,4→35,7** (8,3) e **35,7→53,8** (18,1, o maior da biblioteca na zona útil).

**Convenção nova para inserido: sufixo `h` na banda** (`zen_m_b06h_d3` fica entre b06 e b07). Preserva a ordenação alfabética (`b06` < `b06h` < `b07`), que é o que mantém vizinhos lado a lado no QA. Documentado em `ARCHETYPES.md` §4; `build_index.py` já aceita o padrão.

**⚠️ COMO PEDIR UM INTERMEDIÁRIO — não peça interpolação.** Pedir "o corpo entre A e B" é a técnica que JÁ FALHOU (§5c item 4). O que se faz: **bracketing com o par ABAIXO do buraco, extrapolando um degrau**, e sem anexar as folhas acima (elas puxam pra cima). Para o `b06h` foram anexados b05+b06 (passo 2,0) pedindo o próximo degrau igual, mais a categoria própria "CLASSIC PHYSIQUE" — a divisão real que fica entre o atrator dos ~32 e o dos ~37.

**`b06h_d3` PROCESSADO (1ª inserção da biblioteca). 32 avatares.** Cru 227.304 tri, decimação 0,0792, 17.992 tri, 9/9, simetria média 0,00048 m. Medido: **IMC 34,6 · 105,9 kg · cint/alt 0,500**. QA em `qa/inspect/zen_m_b06h_d3/`. No tester.

**⚠️ A INSERÇÃO NÃO PREENCHEU O BURACO — e revelou saturação.** Ele caiu a **1,1 de IMC do b07** (34,6 vs 35,7); o buraco 27,4→35,7 só encolheu para 27,4→34,6 (8,3 → 7,2). **`b07_d3` e `b06h_d3` foram gerados com os MESMOS anexos (b05+b06) e caíram no mesmo ponto (35,7 e 34,6)** — saturação pela definição do projeto. **O modelo tem um atrator em ~IMC 35 para "o próximo passo depois do b06"; alvo ~31 é inalcançável a partir dessas âncoras.**

**⚠️ O OVERSHOOT É SISTEMÁTICO E MEDIDO: ~2× o passo pedido — CONFIRMADO EM 3 AMOSTRAS.** `b07_d3` pediu 3,7 e deu +8,3 (2,2×); `b06h_d3` pediu 3,7 e deu +7,2 (1,9×); `b05h_d1` pediu 2,6 de barriga e deu +5,1 (2,0×). **Duas linhas, duas direções opostas (músculo e gordura) — é comportamento do modelo, não da linha.** Documentado em `CHARACTER_BIBLE.md` §5c item 6.

**⚠️ E POR ISSO A METADE BAIXA DE UM BURACO É ESTRUTURALMENTE DIFÍCIL** (§5c item 7). A extrapolação parte sempre da âncora SUPERIOR do par, então para cair logo acima de um avatar X seria preciso um par com X no topo e passo ~metade do desejado — par que quase nunca existe. Resultado prático: **toda inserção cai perto do vizinho de cima e o vão só encolhe por cima.** Aconteceu nas duas: `b06h_d3` ficou a 1,1 do b07; `b05h_d1` ficou a 1,2 do b06. Não é falha de folha, é limite do método. Registrar o resto do buraco e seguir — ele encolhe a cada rodada.

**`b06h_d3`: folha aprovada, ombros 35,8** (alvo era 34,0–34,6; var. altura 0,22%). **Ficou na parte ALTA do buraco** — a 1,0 do b07 de frente e empatada de costas (38,6 vs 38,8). **Aceita mesmo assim porque as técnicas acabaram:** adjetivo não controla passo, interpolação não funciona, e bracketing+categoria já foi usado. Uma g2 não teria ferramenta nova. E 1,0 é degrau legítimo pelos padrões da linha (b02→b03 foi 1,2). **Fica registrado: a metade BAIXA do buraco (IMC ~28–31) continua vazia** e é candidata a inserção futura.

## 🔴 RECLASSIFICAÇÃO POR MEDIDA (26/07) — muda como o app escolhe avatar

**O achado.** `metrics.py` calcula o volume da malha fechada × densidade corporal → massa → **IMC real** de cada master a 1,75 m. Resultado: de `b06` para cima o corpo não corresponde nem de longe à faixa que o nome promete.

| avatar | faixa prometida | IMC real | massa |
|---|---|---:|---:|
| b01–b05 (todas as linhas) | 18,5–24,5 | 16–28 | ok |
| `b06_d1` | 24,5–26,0 | **38,8** | 119 kg |
| `b08_d1` | 27,5–29,0 | **48,0** | 147 kg |
| `b10_d2` | 31,0–34,0 | **84,7** | 260 kg |
| `b12_d1` | ≥ 38,0 | **147,6** | **452 kg** |

Confirmado por três vias independentes: volume, caixa delimitadora (b11_d1 tem **71 cm** de profundidade de corpo) e o próprio render. **O instrumento está certo; os assets é que estavam rotulados errado.** Isso explica com número o "salto b05→b06" sentido nas três linhas: são **12 pontos de IMC** num degrau de banda de 1,5.

**A decisão do Rogério (26/07): NÃO regerar nada.** Eu propus regerar b06→b12 e ele corrigiu — a doutrina dele é constante e já estava registrada ([[distribuicao-e-visao-hibrida]]): **aproveitar tudo, reclassificar, inserir; nunca substituir.** Quanto mais avatares, maior a biblioteca. Os corpos formam uma escada **monotônica e bem ordenada** dentro de cada linha; só o rótulo estava errado.

**Como ficou (schema 3, `ARCHETYPES.md` §5 e §6 reescritas):**
- Acabou o `bmi_bands`. **A lista de avatares É o eixo** — cada um carrega seu `measured_bmi` e o app pega o mais próximo dentro da linha de definição.
- Inversões se resolvem sozinhas: `b02_d2`/`b03_d2` estavam trocados na grade nominal (20,8 vs 20,4).
- Avatar novo vira **inserção pura**: mais um ponto no eixo, sem renomear nem substituir nada, sem atualizar o app.
- **Arquivos NÃO foram renomeados.** O nome é o contrato com o pipeline (`ARCHETYPES` §4) e o app lê o caminho do índice. Renomear 29 assets quebraria histórico, QA e tester por ganho zero.
- `label` legível vem de **cintura/altura, não de IMC**: o `b07_d3` tem IMC 35,7 e sairia "obesidade II" sendo fisiculturista de cintura 85 cm (0,488 → "magro").

**⚠️ Buraco de cobertura real, para inserção futura:** a faixa **IMC 28–38** está vazia nas três linhas (d1 salta 27,8→38,8; d2 26,7→35,0; d3 27,4→35,7). É onde vive boa parte dos usuários com sobrepeso. O `build_index.py` emite isso em `coverage_gaps` com prioridade `high`/`low` — os saltos gigantes na obesidade extrema (107→148) são `low` porque quase não têm população.

**⚠️ Para o app: escala uniforme NÃO preserva IMC.** Volume vai com s³, altura com s², logo o IMC representado vai com s. O mesmo avatar exibido a 1,90 m representa ~8,6% mais IMC que a 1,75 m. O classificador precisa buscar por `IMC_alvo = IMC_usuario × (1,75 / altura)`. A fórmula está gravada no `library.json` em `selection.target_bmi_formula`.

**Comandos novos:**
```
python scripts/metrics.py --all --csv     # mede os masters -> metrics/library_metrics.json
python scripts/build_index.py             # -> library.json
```
`metrics.py` mede o **master 3D** (o produto), diferente do `measure.py`, que mede a **folha 2D** (o desenho). Os dois continuam úteis: o `measure.py` é rápido e serve para julgar folha antes da Meshy; o `metrics.py` é a régua de verdade.

**Próxima ação concreta:** montar o prompt do **`b08_d3`** ([[prompt-sempre-completo]], bloco fixo `CHARACTER_BIBLE.md` §4 + descritor §5 d3 "físico de fisiculturista"). Anexos: `b06_d3` + `b07_d3`, bracketing, identificados por conteúdo. **Ler o bloco ⚠️ do teto logo abaixo antes de escrever o prompt.**

**⚠️ ATENÇÃO no b08_d3:** o b07 veio em 36,7 (passo +4,4, o dobro do alvo). Restam b08/b09/b10 e o teto do modelo está perto. **Se o b08 voltar em ~37, é saturação da ponta musculosa — aí encurtar a cauda da d3** (fundir/cortar b09 e b10, mexendo em `ARCHETYPES.md` §3 e no fallback §5). O Rogério já sinalizou preferência por seguir a grade enquanto der.

**Comandos desta máquina (o Blender não está no PATH):**
```
export BLENDER="/c/Program Files/Blender Foundation/Blender 5.1/blender.exe"
python scripts/process.py {id}                                    # driver, chama o Blender sozinho
"$BLENDER" -b -P scripts/qa_render.py -- {id} --raw --torso        # inspeção do cru, ANTES de processar
"$BLENDER" -b -P scripts/qa_render.py -- {id}                      # QA do dist
python scripts/measure.py --def d3
```
`measure.py` só lê os recortes de `00_input/references/{id}/`, então **para medir uma folha antes de aprovar é preciso cropar antes** — ou medir a folha direto (segmenta por coluna, mesmo método do `crop.py`; barriga = faixa 44–56% do perfil, ombros = 18–24% da frente).

**`b06_d3` PROCESSADO 26/07 (5º da d3).** Barriga 15,1% (+1,4) e ombros 32,3% (+2,0) — **degrau grande, aceito por saturação** (ver bloco abaixo), não por acerto. Var. altura 0,23% (a melhor de toda a produção). Cru 145.852 tri → 17.996 (razão 0,1234), 9/9, simetria média 0,00042 m. Cru inspecionado com `--torso`: blocos abdominais de tamanhos variados, sulcos rasos, sem grade. Render roxo 18k: ombros e peitoral nitidamente maiores que o b05, dorsais mais abertas nas costas, cintura ainda estreita, abdômen seco no perfil. QA em `qa/inspect/zen_m_b06_d3/`. Adicionado ao tester.

**`b05_d3` PROCESSADO 26/07 (4º da d3).** Barriga 13,7% (+0,4) e ombros 30,3% (+1,0) — avança nas duas, e com o **perfil certo da linha seca**: o ganho veio em ombros, não em barriga. Passo combinado (0,4+1,0) idêntico ao do b04 (0,8+0,5). Var. altura 0,45% (a melhor da d3). Cru 150.510 tri → 18.000 (razão 0,1196), 9/9, simetria média 0,00033 m (a melhor da d3). Cru inspecionado com `--torso`: blocos abdominais irregulares e sulcos rasos, sem grade — sulco de flanco no perfil idêntico ao do b04 (oblíquo legítimo, não a incisão reta da g1 do b03). Render roxo 18k: peitoral com forma, deltoides desenhados, cintura estreita sem barriga, quadríceps separados, costas com dorsais/escápulas/sulco espinhal. QA em `qa/inspect/zen_m_b05_d3/`. Adicionado ao tester.

**✅ BRACKETING CONFIRMADO (26/07, b05_d3).** Fechou **de primeira, sem g2** — anexando `b03_d3` + `b04_d3` e pedindo "a terceira etapa, com um passo do MESMO TAMANHO do que separa a primeira da segunda". Segunda vez que a técnica entrega o passo pedido; a lição da linha 10 está validada, não é acaso. Complemento que ajudou: em vez de citar "primeira/segunda folha" (ordem de anexo, que o modelo erra), **descrever os anexos por conteúdo** ("a mais magra é a etapa anterior") e pedir que ele confirme qual é qual antes de gerar — some a dependência de nome de arquivo e de ordem de upload.

**⚠️ SATURAÇÃO NA PONTA MUSCULOSA (26/07, folha b06_d3) — o mesmo fenômeno da ponta obesa, do outro lado.** Alvo do b06 era ombros ~31,0–31,5. A g1 veio 32,4 (passo 2,6× o da série). A g2 pediu **explicitamente o meio-termo entre duas imagens anexas** (b05_d3 30,3 + a própria g1 32,4) — interpolação, não extrapolação — e voltou **32,3**, ou seja o mesmo corpo 0,1 mais magro. **O ChatGPT não produz o corpo entre 30,3 e 32,3: tem um atrator de "musculoso e seco" e cai nele independente do pedido.** Idêntico à lição d1 do extremo obeso (satura ~40%, pula o meio ~36). **Decisão: ACEITAR a g2** (32,3/15,0, var. altura 0,23% — a melhor da produção), não gastar uma 3ª tentativa. A g1 foi descartada: mesmo corpo, não serve como b07. **Regra: quando duas gerações caem no mesmo ponto, é saturação — parar de perseguir o valor e aceitar.**

**⚠️ O SALTO b05→b06 ACONTECE NAS TRÊS LINHAS** — d1 (17,5→23,1), d2 (14,6→17,4), d3 (30,3→32,3). Não é acaso das folhas: é o modelo trocando de modo naquela fronteira de banda. **3º ponto de intermediário futuro registrado, e o mais relevante dos três**, por cair na zona atlética que o Rogério pediu para adensar ([[distribuicao-e-visao-hibrida]]). Os outros dois são d2 b05→b06 e d2 b07→b08 (§0.5).

**`b07_d3` PROCESSADO 26/07 (6º da d3).** Barriga 17,4% (+2,3) e ombros 36,7% (+4,4) — o maior degrau da d3, aceito conscientemente (ver abaixo). Var. altura 0,23%. **Cru 232.500 tri — o mais pesado de TODA a produção**, decimação 0,0774 (a mais agressiva já rodada; a d3 vinha em ~0,12) → 18.000 tri, 9/9, simetria média 0,00065 m. **A definição sobreviveu à decimação agressiva** — era o risco real e não se materializou. Cru inspecionado com `--torso`: gomos fortes mas arredondados e irregulares, pares E/D diferentes, serrátil orgânico — não é a placa estampada que reprovou a g1 do b03_d3. Render roxo 18k: peitoral e deltoides volumosos, dorsais muito abertas nas costas com V nítido, cintura estreita, quadríceps e panturrilhas separados, sem barriga no perfil. QA em `qa/inspect/zen_m_b07_d3/`. Adicionado ao tester. **30/32.**

**✅ FOLHA `b07_d3` APROVADA 26/07 — a saturação da d3 QUEBROU trocando de ATRATOR.** O teste passou: ombros **36,7** (+4,4 sobre o b06) e barriga **17,4** (+2,3), var. altura 0,23%. A d3 **não** estava saturada — o modelo estava preso no atrator "musculoso e seco" (~32). O que destravou foi **nomear outra categoria**: "FISICULTURISTA DE COMPETIÇÃO, não um homem musculoso e seco de academia", somado a declarar que a **definição já está no teto e o que cresce é só VOLUME** (deltoides, peitoral, dorsais, braço/coxa; cintura estreita constante). Bracketing mantido (b05+b06, identificados por conteúdo).

**⚠️ LIÇÃO NOVA — saturação aparente é atrator, não teto.** Quando duas gerações caem no mesmo ponto, a regra antiga mandava aceitar e seguir ([[saturacao-para-de-perseguir]]). O b07 mostra que existe um passo antes de desistir: **trocar o substantivo de categoria** do pedido. Adjetivo de intensidade não move ("mais musculoso"), e interpolação não move (o b06-g2 provou); **trocar o nome da categoria move** — e move demais. Ordem correta: (1) bracketing, (2) trocar de atrator, (3) só então declarar saturação. **Custo:** o passo saiu 2,2× o pedido — trocar de atrator dá para controlar a direção, não o tamanho.

**⚠️ b06→b07 é o 4º ponto de intermediário futuro** (+4,4 ombros / +2,3 barriga, o maior salto da d3). Aceito conscientemente pelo Rogério em 26/07 — a alternativa era perseguir ~34, que é o pedido de interpolação já reprovado no b06. Cai na zona atlética que ele pediu para adensar ([[distribuicao-e-visao-hibrida]]): inserção futura, não retrabalho. Pelo descritor, o corpo lê mais como `b08_d3` que como `b07_d3` — registrar que a cauda da linha ficou comprimida.

**⚠️ ATENÇÃO b06→b10 d3:** a definição já está no teto em b05 (gomos nítidos, serrátil, vascularidade). Restam 4 degraus até o `b10_d3` ("fisiculturista de grande porte"). Do b07 em diante o passo tem de ser **VOLUME** (massa, largura de dorsais, grossura de braço/coxa), não mais definição — senão a linha chega no b10 sem para onde crescer.

**`b04_d3` PROCESSADO 26/07 (3º da d3).** Barriga 13,3% (+0,8) e ombros 29,3% (+0,5) — avança nas **duas** métricas, degrau sólido. Var. altura 0,57%. Cru 140.706 tri → 18.000 (razão 0,128), 9/9, simetria média 0,00043 m. Cru inspecionado com `--torso` antes de processar: abdômen orgânico, sem grade. Render roxo 18k: peitoral mais cheio e ombros mais largos que o b03, cintura estreita, definição d3 intacta; costas com dorsais e escápulas legíveis. QA em `qa/inspect/zen_m_b04_d3/`. Adicionado ao tester.

**⚠️ LIÇÃO d3 (26/07) — adjetivo de intensidade não controla o tamanho do passo; BRACKETING controla.** A g1 do b04_d3 empatou com o b03 (ombros 28,5 vs 28,8, ou seja **para trás**) usando o texto "passo contido, ~10% mais massa, não o dobro" — o mesmo texto que funcionara no b03. Adjetivo é instável entre gerações. **A g2 fechou anexando DUAS folhas (b02_d3 + b03_d3) e pedindo "gere a terceira etapa desta sequência, com um passo do MESMO TAMANHO da primeira para a segunda"** — dá a escala por exemplo em vez de por adjetivo. Mesma técnica que resolveu o `b07_d1` (3 âncoras). **Usar bracketing por padrão da d3 em diante, não só quando falhar.**

**A métrica de ombros foi validada contra fragilidade de faixa (26/07):** testadas 5 faixas verticais (0,16–0,20 / 0,18–0,24 / 0,20–0,26 / 0,22–0,28 / 0,16–0,30) e o ranking entre avatares não muda em nenhuma. Quando a medição disser que um avatar não avançou, é o corpo, não a régua.

**`qa_render.py`: luz traseira adicionada (26/07).** As duas luzes originais ficavam ambas na frente e a vista de costas saía em **silhueta chapada** — impossível julgar dorsais/escápulas, sendo que o avatar gira no app e o checklist exige costas críveis (ARCHETYPES §8). Corrigido: 3ª luz atrás + cada luz agora mira o alvo por TRACK_TO (antes todas tinham a mesma rotação fixa, apontando para o mesmo lado). ⚠️ **Os QA de costas dos 24 avatares anteriores foram julgados com a luz ruim** — não invalida nada (o Rogério viu e aprovou as transições no tester, que tem iluminação própria do model-viewer), mas se sobrar tempo vale re-renderizar a série para revisar as costas em condição decente.

**`b03_d3` PROCESSADO 26/07 (2º da d3).** Barriga 12,5% (estável sobre o b02_d3) e ombros 28,8% (+1,2) — o perfil certo da linha seca: o IMC avança por massa magra, não por gordura. Var. altura da folha 0,69%. Cru 139.833 tri → 17.996 (razão 0,129), 9/9, simetria média 0,00044 m. Render roxo 18k: gomos legíveis mas suavizados pelo material, peitoral com forma, cintura estreita, sem volume de fisiculturista. QA em `qa/inspect/zen_m_b03_d3/`. Adicionado ao tester.

**⚠️ ACHADO NOVO 26/07 — a Meshy varia a QUALIDADE ANATÔMICA entre gerações com o MESMO input.** A 1ª geração do `b03_d3` saiu com o abdômen em **grade**: gomos como blocos retangulares uniformes, sulcos fundos descendo pelo flanco no perfil — relevo de placa estampada, não anatomia. O Rogério pegou no olho; a inspeção do cru confirmou e a comparação com o `b02_d3` cru mostrou que era regressão, não o padrão da d3. **Rerodar na Meshy com as MESMAS 3 referências resolveu** (g2 com gomos menores, assimétricos, sulcos rasos). Já sabíamos que a topologia varia a cada geração (README §2.1); o novo é que a **qualidade** varia junto. **Regra: abdômen em grade = regerar na Meshy (20 créditos), NÃO refazer a folha no ChatGPT.** Risco concentrado na d3, a linha onde o abdômen é o traço principal.

**`scripts/qa_render.py` ganhou `--raw` e `--torso` (26/07)** — `--raw` renderiza de `01_raw/`, para julgar a malha da Meshy **antes** de gastar processamento (se o cru vier alucinado, nenhum ajuste de decimação conserta); `--torso` enquadra o tronco em frente/3-4/lado, onde vivem os artefatos de abdômen. O 3/4 é o que denuncia relevo falso — a vista frontal achata. Foi assim que a grade do b03_d3-g1 ficou provada. Renders do cru reprovado preservados em `qa/inspect/zen_m_b03_d3/g1_torso_*.png`.

## 0.4 HANDOFF d3 (26/07) — LER PRIMEIRO na sessão nova

**Onde parou:** d1 (12/12) e **d2 (11/11) COMPLETAS**. Todos em `03_dist/glb/` + `02_master/` + QA em `qa/inspect/`. Tester `test/avatar_tester.html` sincronizado até b11_d2 (botões b01_d2→b11_d2). As transições d2 foram vistas e **aprovadas pelo Rogério** no tester (localhost) em 26/07.

**Próximo: produzir a LINHA d3 — 9 avatares, ordem `b02 → b03 → … → b10`** (d3 pula b01, b11, b12 — ver grade ARCHETYPES §3). Descritores em `CHARACTER_BIBLE.md` §5 d3. Mesma esteira: Rogério gera a folha no ChatGPT → Claude mede a barriga (pixel) + julga vs descritor/vizinho → crop.py → Rogério sobe no Meshy → Claude renomeia/process.py/qa_render → **SÓ ENTÃO** o prompt do próximo ([[esteira-proximo-prompt]]).

**⚠️ CUIDADO CRÍTICO da d3 — é a linha DEFINIDA (gomos, cortes, serrátil):** a d3 é o oposto do risco da d2. Aqui a definição É desejada, mas o `b02_d3` do piloto ensinou (state §1) que **herda a massa da folha-mãe atlética e vem musculoso/volumoso demais** — precisa vir SECO e magro no volume, só com a gordura baixa revelando o músculo que já existe. **No trecho magro/comum da d3 (b02–b05), largar a folha-mãe e anexar só o vizinho** (mesma lição da d2, [[d2-largar-mae-trecho-magro]] — a mãe atlética puxa pra volumoso). A mãe volta como âncora útil em b06+ (corpo ≥ ao dela). **Medir barriga sempre** ([[medir-folha-antes-de-aprovar]]).

**`b02_d3` do piloto: MANTIDO, não refazer (decidido 26/07 por medição).** A ressalva "veio volumoso demais" era julgamento no olho do piloto, feito antes de d1/d2 existirem. Com a série completa medida (`scripts/measure.py`), o piloto é o **mais estreito da banda b02**: barriga 12,5% e ombros 27,6% contra b02_d2 13,5/29,2 e b02_d1 13,1/29,0. Ou seja, mais seco que os vizinhos da mesma banda — que é exatamente o que a d3 pede. O que se leu como "massa" era **definição visível** (gomos, serrátil), não volume. Re-renderizado com o material atual (roxo 18k, o piloto tinha só render clay): torso com gomos e cortes, perfil fino sem barriga, distinto do b02_d2 liso. Aprovado. Refazer custaria 20 créditos e `--force` sobre master aprovado, com ganho nulo. **d3 começa de fato no b03_d3. Total: 25/32.**

**`scripts/measure.py` criado 26/07** — a medição de barriga/ombros por pixel virou script (antes era inline no histórico do chat, perdido a cada sessão). `python scripts/measure.py` mede tudo, `--def d3` mede uma linha. Barriga = profundidade do perfil na faixa 44–56% da altura; ombros = largura frontal na faixa 18–24%. Calibração ~0,2 pt abaixo dos números do histórico (b01_d1 11,6 vs 11,8 registrado) — a **ordem** é idêntica, que é o que importa. Comparar sempre dentro da mesma linha de definição (a listagem geral ordena alfabético e mistura d1/d2/d3 na coluna "passo").

**Anexos por avatar na d3:** trecho magro (b03–b05) anexa **só o vizinho d3 imediato**, sem a mãe. A mãe volta como âncora em b06+.

**⚠️ LIÇÃO d3 (26/07, achada no b03_d3-g1) — o negativo da d2 NÃO se transporta para a d3.** Na d2 o ganho entre bandas é gordura e o músculo é o inimigo, então o negativo padrão proíbe alargar ombros/braços/costas. **Na d3 o corpo é seco: o que faz o IMC subir de banda É massa muscular.** Copiar aquele negativo congela a progressão — a g1 do b03_d3 saiu com barriga 12,2% e ombros 27,0%, ou seja **MENOR** que o b02_d3 (12,5/27,6), inversão na grade. Folha perfeita de forma (var. altura 0,46%, definição d3 correta), reprovada só por não avançar. **Descritor d3 correto:** pedir explicitamente um degrau de MÚSCULO MAGRO ("ganhou ~4 kg de músculo, diferença visível lado a lado, ~10% mais massa"), mantendo o negativo apenas contra GORDURA e contra volume de fisiculturista. Alvo do b03_d3: ombros ~28,3–28,6, barriga ~12,8–13,0.

## 0.5 Pendências registradas (não bloqueiam a d3)

- **2 pontos de intermediário futuro na zona comum d2** (pós-MVP, decisão MVP §0 manda seguir a grade base): salto b05→b06 (+2.8) e b07→b08 (+4.3). Ver [[distribuicao-e-visao-hibrida]]. Série d2 final: b01 11.8 · b02 12.7 · b03 12.8 · b04 13.9 · b05 14.6 · b06 17.4 · b07 19.2 · b08 23.5 · b09 28.8 · b10 33.6 · b11 40.5.
- **Seletor de resolução do tester:** 40k/60k só existem para `b02_d3` e `b11_d1` (arquivos em `test/compare/`). Trocar a resolução em qualquer outro avatar não muda nada (cai no 18k). NÃO é bug — tester já mostra aviso amarelo explícito ao clicar 40k/60k num avatar sem comparação. Para comparar resolução, selecionar b02_d3 ou b11_d1.
- **Short** continua desligado (`SHORTS_ENABLED=False`); feito a mão no Blender ao final dos masters.

---

## 0.5 HANDOFF d2 (26/07) — LER PRIMEIRO na sessão nova

**Onde parou:** linha d2 em 6/11. Processados e no `03_dist/glb/` + `02_master/` + QA em `qa/inspect/`: b01_d2, b02_d2, b03_d2, b04_d2, b06_d2 (b05_d2 é a mãe, do piloto). **Tester `test/avatar_tester.html` atualizado** com os 6 d2 (botões b01_d2→b06_d2) — servir com `python -m http.server 8000` na raiz (Start-Process destacado) → `http://127.0.0.1:8000/test/avatar_tester.html`.

**⚠️ PENDÊNCIA CRÍTICA — medir a série d2 e resolver o salto do b06:** o Rogério apontou (e a medição confirmou) que o `b06_d2` deu um **salto grande** de volume/gordura em relação à mãe (b05). **Medição preliminar da barriga (profundidade do perfil, % da altura da figura, medida nos recortes side):**

| Avatar | Barriga | Passo |
|---|---|---|
| b01_d2 | 12,0% | — |
| b02_d2 | 12,9% | +0,9 |
| b03_d2 | 13,0% | +0,1 |
| b04_d2 | 13,7% | +0,7 |
| b05_d2 (mãe) | 14,8% | +1,1 |
| **b06_d2** | **17,7%** | **+2,9** |

O passo b05→b06 (+2,9) é ~3× os degraus típicos (~0,8–1,1). Mesmo padrão do d1 (b05→b06 saltou 17,5→23,1). **Decisão já registrada do Rogério: NÃO descartar/refazer o b06 (já está feito, aproveita) — INSERIR um intermediário entre b05 e b06** (ver [[distribuicao-e-visao-hibrida]]: transições grandes → inserir intermediário, não substituir). Na sessão nova: (1) remedir com contexto limpo pra confirmar; (2) decidir o alvo do intermediário (~16%, um b05.5_d2) ou aceitar o gap; (3) seguir. O script de medição inline está no histórico desta sessão (mede o recorte `_ref_side.png`, faixa 44–56% do topo da figura).

**Regra travada nesta sessão (b01–b04 d2):** no trecho magro da d2, **largar a folha-mãe** e anexar só o vizinho imediato — a mãe atlética puxa pra musculoso (b03_d2 e b04_d2 só fecharam assim). Documentado em `CHARACTER_BIBLE.md` §6 item 2 e §5b, e em [[d2-largar-mae-trecho-magro]]. A mãe volta como âncora em b05+ (b06 já usou a mãe e funcionou pro nível de músculo, embora tenha saltado no volume).

**Fluxo por avatar (respeitar — correção do Rogério):** Rogério gera a folha → **Claude cropa/salva as 3 vistas** → Rogério sobe no Meshy e devolve o GLB → Claude renomeia/processa/qa_render → **SÓ ENTÃO** o prompt do próximo. Não adiantar o prompt seguinte na aprovação da folha. Ver [[esteira-proximo-prompt]].

**LINHA d2 COMPLETA (11/11) em 26/07.** Todas processadas, 9/9 cada, no dist+master+QA. Transições vistas e aprovadas pelo Rogério no tester. Próximo: d3 (b02→b10, 9). Descritores em `CHARACTER_BIBLE.md` §5.

**`b11_d2` PROCESSADO 26/07 (11º/ÚLTIMO da d2).** Barriga 40.5% (perfil, +6.9 sobre b10 — banda mais larga IMC 34–37.9 e o modelo satura ~40% no extremo, lição travada da d1; monotônico, ~igual ao d1 b11 39.6), var altura 0.73%. Cru 275.898 tri → 18k (razão 0.065, o mais volumoso da d2), 9/9, simetria média 0,00055 m. Render roxo 18k: corpo enorme e maciço, barriga gigante pendente, ombros muito largos, membros muito espessos, abdômen liso, costas largas sem dorsais — obesidade II com força, d2 correto, aprovado. QA em `qa/inspect/zen_m_b11_d2/`. Adicionado ao tester. **FECHA a linha d2.**

**`b10_d2` PROCESSADO 26/07 (10º da d2).** Barriga 33.6% (perfil, +4.8 sobre b09 — banda larga IMC 31–33.9, degrau grande esperado, monotônico), var altura 0.36%. Cru 220.716 tri → 18k (razão 0.082, o mais volumoso da d2), 9/9, simetria média 0,00061 m. Render roxo 18k: estrutura enorme e larga, ombros/tronco espessos, peito grande mole, barriga proeminente pendente, membros muito grossos, abdômen liso, costas largas lisas sem dorsais — powerlifter obeso, d2 correto, aprovado. QA em `qa/inspect/zen_m_b10_d2/`. Adicionado ao tester. Série d2: b01 11.8 · b02 12.7 · b03 12.8 · b04 13.9 · b05 14.6 · b06 17.4 · b07 19.2 · b08 23.5 · b09 28.8 · b10 33.6.

**`b09_d2` PROCESSADO 26/07 (9º da d2).** Barriga 28.8% (perfil, +5.3 sobre b08 — banda larga IMC 29–30.9, degrau grande esperado, monotônico), var altura 0.72%. Cru 208.502 tri → 18k (razão 0.086, o mais volumoso da d2), 9/9, simetria média 0,00052 m. Render roxo 18k: corpo grande e forte, ombros muito largos, barriga enorme pendente, membros grossos, peito mole, abdômen liso sem gomos, costas largas lisas sem dorsais — d2 correto, aprovado. QA em `qa/inspect/zen_m_b09_d2/`. Adicionado ao tester. Série d2: b01 11.8 · b02 12.7 · b03 12.8 · b04 13.9 · b05 14.6 · b06 17.4 · b07 19.2 · b08 23.5 · b09 28.8.

**`b08_d2` PROCESSADO 26/07 (8º da d2).** Barriga 23.5% (perfil), var altura 0.72%. Passo sobre b07 (19.2) = **+4.3 — grande, maior que o salto do b06 (+2.8)**. **Decisão: ACEITO** (não regerar), pela lição travada da d1: o ChatGPT é bimodal e não entrega degraus uniformes; perseguir ~21.5% seria brigar com a ferramenta sem cravar. Cru 160.886 tri → 18k (razão 0.112), 9/9, simetria média 0,00046 m. Render roxo 18k: tronco largo e espesso, ombros largos, peito mole, barriga grande pendente, abdômen liso sem gomos, costas lisas sem dorsais — sobrepeso com massa, d2 correto, aprovado. QA em `qa/inspect/zen_m_b08_d2/`. Adicionado ao tester. **Registrado como 2º ponto de intermediário futuro na zona comum** (junto do b06, pós-MVP — ver [[distribuicao-e-visao-hibrida]]). Série d2 até aqui: b01 11.8 · b02 12.7 · b03 12.8 · b04 13.9 · b05 14.6 · b06 17.4 · b07 19.2 · b08 23.5.

**`b07_d2` PROCESSADO 26/07 (7º da d2).** Rogério gerou 2 folhas; ambas barriga 19.2%/19.3% (idênticas em volume; +1.8 sobre b06 17.4 = degrau bom, menor que o salto do b06). Diferença era só DEFINIÇÃO: folha_1 (`07_54_56 (1)`) gordura cobrindo músculo, peito mole, abdômen liso, costas lisas = **d2 correto** ("força sob a gordura"); folha_2 (`(2)`) contorno abdominal + peito desenhado + dorsais = definição demais (puxa pra d3, erro clássico da d2). **Escolhida folha_1**, cropada (var altura 0.83%). Cru 2,6 MB, decimou p/ 18000 tri, 9/9, simetria média 0,00034 m. Render roxo 18k: ombros largos, peito mole, barriga arredondada saliente, abdômen liso, costas lisas — sobrepeso leve "força sob a gordura", aprovado. QA em `qa/inspect/zen_m_b07_d2/`. Adicionado ao tester (botão b07_d2). Anexos na geração: mãe + b06.

---

**`b04_d2` processado 25/07 (4º da d2).** Cru 122.160 tri, 9/9, simetria média 0,00029 m. **g1 REPROVADA por massa** (ombros largos, peitoral/braços/costas desenvolvidos — mesmo drift do b03). **SOLUÇÃO: largar a folha-mãe** — g2 anexando SÓ o vizinho `b03_d2` (sem a mãe atlética) saiu certo de primeira: peso normal comum, macio, costas lisas. **REGRA NOVA (documentada em CHARACTER_BIBLE §6 item 2 + [[d2-largar-mae-trecho-magro]]): no trecho magro da d2 (b01–b04), anexar só o vizinho, largar a mãe.** A mãe volta a ser âncora útil em b05+ (corpo ≥ ao dela). QA em `qa/inspect/zen_m_b04_d2/`.

**`b05_d2` = folha-mãe, já produzida no piloto sob Pro** (master+dist existem, `zen_m_b05_d2_v1.glb`). Conta como o 5º da d2, não precisa refazer.

**`b06_d2` processado 26/07 (6º da d2).** Cru 142.004 tri, decimação 0,127, 17996 tri, 9/9, simetria média 0,00028 m. Anexo = a mãe (b05, que é o vizinho). Folha: forte com ombros largos + camada de gordura por cima (barriguinha macia no perfil), abdômen sem definição — "forte porém fofo", o descritor. **⚠️ APROVADO NO OLHO SEM MEDIR (falha minha) — a medição depois deu barriga 17,7%, salto +2,9 sobre a mãe (grande demais, ver Handoff §0.5).** NÃO descartar; resolver com intermediário na sessão nova. QA em `qa/inspect/zen_m_b06_d2/`. **Adicionado ao tester** (`avatar_tester.html`, botão b06_d2).

**`b03_d2` processado 25/07 (3º da d2).** Cru 136.452 tri, decimação 0,132, 9/9, simetria média 0,00028 m. **g1 REPROVADA por massa** — veio musculoso demais (ombros largos, peitoral/braços desenvolvidos, dorsais e trapézio com separação nas costas), lia como b05/b06 ou d3, tão ou mais cheio que a própria mãe. **LIÇÃO d2: a linha d2 herda a massa da folha-mãe atlética e deriva pra musculoso — o negativo padrão não segura no trecho magro (b01–b04).** g2 regerada com negativo MUITO forte ("ombros estreitos, braços finos, COSTAS LISAS sem dorsais, PROIBIDO copiar volume/ombros/peitoral/costas da mãe, muito mais magro que a folha-mãe, passo mínimo sobre o vizinho") → esguio correto, aprovado. Aplicar esse negativo forte em b04_d2 também. QA em `qa/inspect/zen_m_b03_d2/`.

**`b02_d2` processado 25/07 (2º da d2).** Cru 122.370 tri, decimação 0,147, 18000 tri, 9/9, simetria média 0,00027 m. Passo pequeno e limpo sobre o b01: peito/ombros um pouco mais preenchidos, torso menos ossudo, abdômen plano com tônus leve (gomos suavizam no roxo), sem inversão de definição. QA em `qa/inspect/zen_m_b02_d2/`.

**`b01_d2` processado 25/07 (1º da d2).** Cru → 18000 tri, 9/9 validações, simetria média 0,00053 m. Folha (barriga com gomos por magreza, IMC ~18) aprovada; no render roxo 18k os gomos derretem no material liso → lê como "magro com tônus leve", sem corte, distinto de d3. Não herdou a massa da mãe atlética (ombros estreitos, membros finos). QA em `qa/inspect/zen_m_b01_d2/`. **Vigiar:** b02_d2/b03_d2 têm mais gordura → devem vir com abdômen MAIS liso, não mais definido (senão inverte a definição).

---

## 0. HANDOFF d1→d2 (25/07) — HISTÓRICO, SUPERADO pelo §0.4. Ler só para contexto das lições d1.

**Onde parou (25/07):** linha **d1 completa e validada** (12 GLBs em `03_dist/glb/`, todos em `02_master/`, QA em `qa/inspect/`). Folha de contato `qa/inspect/_continuidade_d1.png` aprovada. Tester `test/avatar_tester.html` atualizado com os 12 d1 (botões b01→b12 em ordem); servir com `python -m http.server 8000` na raiz (destacado) → `http://127.0.0.1:8000/test/avatar_tester.html`.

**Próximos passos, em ordem:**
1. **Produzir a linha d2** (11 avatares, b01→b11), mesma esteira do d1: Rogério gera folha no ChatGPT (prompt COMPLETO montado pelo Claude, bloco fixo §4 CHARACTER_BIBLE + descritor d2 §5) → crop.py → Meshy → process.py → qa_render. Ao iniciar d2, a referência anexa volta a ser a folha-mãe (`_mother_m.png`) + a 1ª folha de d2. Ordem: b01→b11.
2. **Produzir a linha d3** (9 avatares, b02→b10).
3. Isso fecha os **32 masculinos**. Depois: **Onda 2 feminina (~32)** = total **64 GLBs do MVP** (meta confirmada pelo Rogério em 25/07).
4. `render.py`/turntable: dispensado (model-viewer aprovado). `build_index.py`: ainda não escrito — montar `library.json` quando os 32 masc. fecharem.
5. **Short**: continua desligado; feito a mão no Blender por avatar, ao FINAL dos masters.

**LIÇÕES da produção d1 (aplicar em d2/d3 e onda fem.):**
- **Descritor d1 padrão é fraco no negativo de tônus** — endurecer sempre (peitoral PLANO, sem deltoide, sem separação de quadríceps etc.). Idem d2/d3: cravar o nível certo, o modelo deriva.
- **No extremo obeso o ChatGPT SATURA ~40% de barriga** (resposta bimodal ~30 ou ~40, pula o meio ~36). Não perseguir valores intermediários com precisão lá em cima — estruturar a grade aceitando isso (foi como b11=39,6 / b12=51,2 se resolveram).
- **Medir barriga por pixel** (profundidade do perfil, % da altura) é o juiz de continuidade — usar sempre pra ordenar a série. Script inline usado está no histórico das mensagens.
- **process.py**: solda non-manifold agora escalona threshold (0,0005→0,001→0,002) — resolve as dobras de 4 faces dos corpos extremos. Se um extremo ainda reprovar watertight, o alvo de tris NÃO é a causa (é knife-edge da decimação); investigar solda.
- **Barriga medida d1 (referência de ordenação):** b01 11,8 · b02 13,6 · b03 13,4 · b04 14,8 · b05 17,5 · b06 23,1 · b07 25,2 · b08 26,4 · b09 30,3 · b10 32,5 · b11 39,6 · b12 51,2.

**DECISÕES NOVAS do Rogério (25/07):**
- **b05→b06 tem salto grande (17,5→23,1).** NÃO regerar/substituir (não perder trabalho aprovado). Em vez disso, quando conveniente, **gerar um avatar INTERMEDIÁRIO entre b05 e b06** (inserção, não substituição). Vale como padrão: transições muito grandes → inserir intermediário, não refazer.
- **Distribuição / prioridade:** quer MAIS densidade nos **corpos comuns e musculosos** (zona quente IMC ~20–29, e os d2/d3 atléticos — a tela Objetivo mostra sobretudo esses como meta). NÃO quer gastar esforço em muitos extremos de obesidade (b09–b12 são casos isolados). As inserções de intermediários devem se concentrar na zona comum/atlética, não nos extremos. Ver [[distribuicao-e-visao-hibrida]].
- **VISÃO FUTURA (bem depois dos 32/64):** o híbrido de shape keys. App escolhe o avatar de medidas mais próximas; se esse avatar tiver shape keys (a esculpir no futuro), as medidas do usuário se adaptam perfeitamente por deformação. Mesmo sistema de seleção de hoje, aprimorado. Ver §9 (morph regional PARKED) e [[distribuicao-e-visao-hibrida]].
- **MVP = seguir o plano igual até os 64 GLBs.** Sem mudar a grade base agora; as melhorias (intermediários, shape keys) vêm depois.

---

## 1. Onde o projeto está

| Item | Estado |
|---|---|
| Plano Meshy Pro | ✅ assinado (~1.305 créditos restantes) |
| Folha-mãe `m_b05_d2` | ✅ aprovada |
| Recorte em 3 vistas | ✅ feito (1200px de altura cada) |
| GLB cru `zen_m_b05_d2_raw.glb` | ✅ baixado, 129.830 tri, 2,2 MB |
| Inspeção do GLB | ✅ feita |
| `scripts/process.py` | ✅ escrito, rodado, 9/9 validações passam |
| `scripts/crop.py` | ✅ escrito — recorta a folha em 3 vistas por detecção de fundo |
| `scripts/qa_render.py` | ✅ escrito — render de QA em 4 vistas do dist GLB (`blender -b -P scripts/qa_render.py -- {id}`) |
| `scripts/render.py` (turntable) | ❌ não escrito — turntable dispensado (model-viewer aprovado); qa_render cobre o QA |
| `scripts/build_index.py` | ❌ não escrito |
| Piloto (4 avatares) | ✅ 4 de 4 (`m_b05_d2`, `m_b02_d3`, `m_b08_d1`, `m_b11_d1`) |
| Teste de entrega no app | ✅ feito via `test/avatar_tester.html` (model-viewer + sliders) |
| Material / resolução | ✅ resolvidos — 18k, roxo com brilho, `shade_smooth`, Draco 14-bit |
| Short | ⏸️ **desligado por ora** (`SHORTS_ENABLED=False`) — corpo todo roxo; feito a mão no Blender ao final |
| Docs reconciliados (§7 + piloto) | ✅ `rules/CLAUDE/README/runbook/CHARACTER_BIBLE` atualizados |

**Decisões desta sessão (23/07), todas travadas:**
- **Resolução 18k** confirmada no teste em escala de app. O "quadriculado" era MATERIAL, não geometria (ver §6b).
- **Material:** roxo `#8346C6` com roughness 0.5 (brilho revela músculo), `shade_smooth` e Draco pos/normal 14 bits. Fosco (0.9) foi testado e **rejeitado** (apaga o músculo). Ver §6b.
- **Formato de entrega:** GLB com auto-rotate (model-viewer). Turntable dispensado.
- **Short desligado** (`SHORTS_ENABLED=False` em `process.py`): corpo todo roxo. A segmentação por projeção frontal serrilha e nenhuma regra serve para todos os corpos (barriga pendente dos obesos quebra tudo — 3 abordagens automáticas tentadas e revertidas). **Plano: fazer o short por avatar, a mão no Blender, ao FINAL** (quando os 32 masters existirem). Rogério pediu explicitamente "um a um, no Blender".

**[HISTÓRICO — d1 e d2 já concluídas. O ponteiro de "próximo" vale agora é o §0.4 (d3).]** Ordem geral `d1 → d2 → d3` (`rules.md` §6). Loop por avatar: Rogério gera a folha no ChatGPT (prompt COMPLETO montado pelo Claude — [[prompt-sempre-completo]]) → baixa em Downloads → Claude Code pega, renomeia, `crop.py`, move o GLB, `process.py`, `qa_render.py`. Short fica para o final.

**VIGIAR na linha `d1` — tônus de tronco no teto:** `b03_d1` e `b05_d1` saíram com peitoral/ombros com um pouco de forma no limite do que `d1` tolera (não é corte; lê como massa sob gordura). Não reprovou nenhum isolado, mas se a linha `d1` inteira ficar levemente tônica demais no **teste de continuidade** final, endurecer o negativo de peitoral/ombros e reavaliar. `b04_d1` (skinny-fat, com "peitoral SEM forma" explícito) saiu mole e serviu de âncora boa.

**Rotina de QA por avatar (o que o Claude faz sozinho):** mede a folha em pixels (nº de vistas, alinhamento, variação de altura <2%) → julga conteúdo vs descritor e vizinho → `qa_render.py` 4 vistas do dist. Rogério **não precisa reconferir cada folha**; o check humano decisivo é o **teste de continuidade** (folha de contato `b01→b12`) no fim de cada nível de definição.

**⚠️ CONTINUIDADE d1 — `b08_d1` (piloto) FURADO, regerar (achado 24/07).** Medição de barriga (profundidade do perfil, % da altura) na linha d1: b01 11,8 · b02 13,6 · b03 13,4 · b04 14,8 · b05 17,5 · b06 23,1 · b07 25,2 · **b08 21,9** · b11 33,6. O `b08_d1` do piloto (21,9%) é **mais magro que o b06 e o b07** — inversão na grade. Foi gerado isolado no piloto, antes da linha d1 calibrada. **Plano:** regerar `b08_d1` maior (~27-28%, claramente "sobrepeso" acima do b07) — vira o PRÓXIMO a produzir, no lugar do b09. Fila d1 restante depois: b09, b10, b12. Vigiar também: (a) o salto b05→b06 foi grande (+5,6) — b06 veio no alto; se o teste de continuidade final ficar irregular, considerar regerar b06 um pouco menor; (b) conferir se b11 (33,6) fica ok com um b10 ~31 no meio. Regerar b08 sobrescreve master aprovado do piloto → usar `--force` consciente.

**`b08_d1` FOLHA regerada e aprovada em 24/07 (barriga 26,4%).** g1 do regen REPROVADA por estourar (30,2% — pulou pro slot do b09/b10; +5 sobre b07 e depois espremeria b09/b10 em 3,4 pts). g2 com descritor "APENAS UM POUCO mais gordo, passo pequeno e sutil" → 26,4%, degrau limpo (+1,2 sobre b07), folga de 7,2 pts até b11. Cropada (referências novas sobrescreveram as do piloto). **PROCESSADO 24/07 com `--force`** — cru 154.542 tri, 9/9, master/dist do piloto sobrescritos. Render roxo 18k: barriga arredondada/pendente um degrau acima do b07, peito mole, corpo liso. Aprovado, inversão corrigida. QA em `qa/inspect/zen_m_b08_d1/`. Nova linha d1: b06 23,1 · b07 25,2 · b08 26,4 · … · b11 33,6. Alvos p/ os do meio: b09 ~28,8, b10 ~31,2.

**`b10_d1` processado em 24/07 (10º).** Barriga 32,5% (g1 de primeira). Cru 229.982 tri (o MAIOR até agora, superou o b11-piloto; decimação 0,078), 9/9. Render roxo 18k: barrigão pendente, coxas grossas, peito mole — obesidade I crível. Aprovado. QA em `qa/inspect/zen_m_b10_d1/`. **DECIDIDO: regerar `b11` maior** — piloto (33,6%) ficou só +1,1 sobre b10, quase idêntico, sendo banda diferente.

**`b12_d1` FOLHA aprovada em 24/07 (barriga 40,7%).** Veio da regen de b11 que ESTOUROU (pedi ~37, saiu 40,7 = grau III, não grau II). Em vez de descartar, aproveitada como b12 (obesidade III) — ideia do Rogério de não desperdiçar. **PROCESSADO 24/07** — cru 263.408 tri (o MAIOR da biblioteca, decimação 0,068), 9/9. Render roxo 18k: barrigão pendente enorme, coxas maciças — grau III, extremo da linha. Aprovado. QA em `qa/inspect/zen_m_b12_d1/`.

**`b11_d1` RESOLVIDO por reestruturação (24/07).** O ChatGPT NÃO consegue gerar barriga ~36% (obeso intermediário): 5 tentativas deram 40,7 / 41,7 / 39,6 / 26,6 / 30,4 — resposta BIMODAL (~30 ou ~40), pula o meio. Nenhum bracketing/negativo segurou. **Decisão:** parar de brigar. Fila do topo virou: b11 = a folha g3 (39,6%) que já tínhamos (custo zero, cropada), b12 = regerar MAIS extremo (~44%) pra abrir o gap (39,6↔40,7 era pequeno demais). Novo topo: b10 32,5 → b11 39,6 → b12 ~44. Salto b10→b11 (+7) grande mas é obesidade I→II (faixas alargam). **LIÇÃO p/ d2/d3 e onda fem.: no extremo obeso o modelo satura ~40; não perseguir valores intermediários acima de ~33 com precisão — aceitar bimodal e estruturar a grade em torno disso.** b11 sheet pronta p/ Meshy → processar com `--force` (sobrescreve piloto). b12 a regerar+reprocessar (`--force`, sobrescreve o b12 40,7 já feito).

**`b11_d1` PROCESSADO 25/07 com `--force`** — g3 (39,6%), cru 266.814 tri, 9/9. Render roxo 18k: barrigão pendente obesidade II, mole, entre b10 e b12. Aprovado. QA em `qa/inspect/zen_m_b11_d1/`.

**`b12_d1` sheet REGERADA extrema (barriga 51,2%, obesidade III mórbida)** — spread do topo resolvido: b10 32,5 → b11 39,6 → b12 51,2. Prompt de b12 soltou todas as palavras de extremo (avental de gordura etc.) e o modelo respondeu (o modo ~40 vira ~51 com push máximo). ⚠️ Var altura da folha 2,47% (>2%, topos derivam ~15px, bases alinhadas) — ACEITA porque crop normaliza cada vista a 1200px; QA render é o árbitro. Cropada, **aguardando Meshy → processar com `--force`** (sobrescreve o b12 40,7 stale). Isso FECHA a linha d1 (12/12).

**`b12_d1` PROCESSADO 25/07 — FECHA a d1 (12/12).** Cru 353.968 tri (o MAIOR de toda a lib, decimação 0,051), 9/9. Avental de gordura, grau III extremo, mole. QA em `qa/inspect/zen_m_b12_d1/`. **BUG do process.py corrigido no caminho:** decimação simétrica desta malha extrema deixava 1 aresta non-manifold (dobra de 4 faces, 1,37mm, mão-na-coxa) que a solda de 0,0005 não pegava — reprovava watertight em QUALQUER alvo de tris. Diagnóstico: o merge inicial na crua (passo 3) + decimate simétrico fundem duas superfícies que quase se tocam. Fix: **solda non-manifold agora escalona o threshold (0,0005 → 0,001 → 0,002)** quando sobra aresta; só age em vértices non-manifold selecionados (no-op em malha limpa). Blindado p/ os próximos extremos (d2/d3, onda fem.).

**`b09_d1` processado em 24/07 (9º).** Barriga 30,3% (g1 de primeira). Cru 202.272 tri (grande, decimação 0,089), 9/9. Render roxo 18k: barriga pendente maior, peito mole, corpo liso — degrau claro sobre b08. Aprovado. QA em `qa/inspect/zen_m_b09_d1/`. Linha d1: b06 23,1 · b07 25,2 · b08 26,4 · b09 30,3 · b11 33,6. Alvo b10 ~32%. Candidato-banco b08-g1 (30,2) ficou redundante (perto do b09) — gerar b10 do zero mirando ~32.

**BANCO de folhas aproveitáveis (ideia do Rogério — não desperdiçar geração):** a g1 reprovada do b08 (barriga ~30,2%) está no Downloads do Rogério (`ChatGPT Image 24 de jul. de 2026, 08_42_49.png`), bom candidato a **b10** (alvo ~31%). Testar antes de gerar b10 do zero. Regra geral: custo é na Meshy (20 cr/GLB), não no ChatGPT (folha grátis) → no estágio de FOLHA regerar à vontade p/ cravar o alvo; no estágio de GLB, se sair um pouco fora mas encaixar em slot vizinho vazio, RENOMEAR e aproveitar em vez de re-rodar Meshy.

**`b07_d1` processado em 24/07 (7º)** — 9/9, cru 140.642 tri, decimação 0,13. **g1 REPROVADA por volume** (barriga do tamanho do b08, colou no vizinho de cima). g2 regerada com 3 âncoras anexas (mãe + b06 limite-baixo + b08 limite-alto) e descritor "corpo EXATAMENTE no meio, NÃO copiar barriga do b08" → barriga 25,2% (degrau limpo sobre b06 23,1%), tônus mole ok. Render roxo 18k: barriga arredondada mole, peito com leve queda sem forma muscular, pernas/costas lisas. Aprovado. QA em `qa/inspect/zen_m_b07_d1/`.

**`b06_d1` processado em 24/07 (6º)** — 9/9, cru 148.114 tri, decimação 0,12. Peso normal alto, barriga arredondada e pendente. **1ª geração REPROVADA por conteúdo** (peitoral definido, deltoides/quadríceps/dorsais musculosos — leu como `d2`, mais definido que o próprio `b06_d2`; era o risco de tônus da linha `d1` finalmente cruzando o teto). Regerada com **negativo de tônus endurecido** ("peitoral PLANO sem contorno, ombros sem deltoide, pernas sem separação de quadríceps, costas sem dorsais, mesmo corpo mole do b05") → g2 aprovada. No render roxo 18k o peito lê mole e liso; sobrou leve separação de quadríceps nas pernas (dentro da tolerância já aceita em b03/b05/b08/b11). Barriga deu passo generoso sobre o b05 — **vigiar no teste de continuidade final** se não saltou demais. QA em `qa/inspect/zen_m_b06_d1/`. **Lição p/ b07+: o descritor d1 padrão do CHARACTER_BIBLE é fraco no negativo de tônus; endurecer sempre.**

**`b05_d1` processado em 24/07 (5º)** — 9/9, cru 130.756 tri (o mais volumoso da série d1). Dad-bod com barriga arredondada, aprovado. Ressalva de tônus de tronco (ver acima). QA em `qa/inspect/zen_m_b05_d1/`.

**`b04_d1` processado em 24/07 (4º)** — 9/9, cru 119.450 tri. Skinny-fat aprovado de primeira; barriguinha mole sobreviveu à decimação. O negativo "peitoral SEM forma" cortou o contorno de peitoral que subia no `b03`. QA em `qa/inspect/zen_m_b04_d1/`.

**`b03_d1` processado em 23/07 (3º)** — 9/9, watertight limpo (correção non-manifold segurou), cru 111.962 tri. Folha aprovada de primeira; progressão sutil correta. Ressalva a vigiar: peitoral/deltoide com contorno natural no limite do que `d1` tolera (forma de repouso, não corte). QA em `qa/inspect/zen_m_b03_d1/`.

**`b02_d1` processado em 23/07 (2º de produção)** — folha aprovada de primeira (progressão sutil correta sobre o `b01_d1`, torso liso). Cru 119.272 tri. **Reprovou na 1ª passada por 1 aresta non-manifold** (4 faces, nos dedos do pé, z_frac 0,01): a decimação **simétrica** (`use_symmetry="X"`) belisca uma aresta de ~0,1 mm na extremidade fundida; `fill_holes` não resolve (não é furo). **Corrigido no `process.py`** (passo 7): laço que solda SÓ os vértices non-manifold com `NONMANIFOLD_WELD_M=0.0005` — local, não toca mãos/dedos. Reprocessado 9/9, simetria idêntica (media 0,34mm), `tris=17996`. Correção vale para os próximos 30. QA render em `qa/inspect/zen_m_b02_d1/`.

**`b01_d1` processado em 23/07 (1º de produção)** — v1 reprovada por conteúdo (six-pack/serrátil herdados da mãe atlética; `d1` não pode ter definição, e ficaria mais definido que o próprio `b01_d2`). Regerada com negativo reforçado ("ossos pela falta de gordura, NÃO músculo; superfície lisa e mole") → v2 aprovada. 9/9 validações, cru **112.136 tri** (o MENOR de todos — corpo magérrimo tem menos volume; decimação 0,16). QA render 4 vistas em `qa/inspect/zen_m_b01_d1/`: roxo liso, magreza e ausência de definição preservadas a 18k. Vinco leve na coxa (barra do short herdada da malha), aceito como no piloto.

**`m_b11_d1` processado em 23/07** — 9/9 validações, `shorts_frac=0.1227`, cru **229.058 tri** (o maior; decimação 12,7:1, a mais agressiva). Render em `qa/inspect/zen_m_b11_d1/`. Volume, barriga pendular e dobras do tronco sobreviveram mesmo à decimação máxima. Torso liso (`d1` correto); leve def. nas pernas de novo — 2º caso, Melhoria de imagem confirmada como fraca e fora do torso, **mantida ligada**. Costura do short a mais serrilhada dos três (barriga cobre o short).

**`m_b08_d1` processado em 23/07** — 9/9 validações, `shorts_frac=0.1070`, cru 150.860 tri. Render de QA em `qa/inspect/zen_m_b08_d1/` (clay+cavidade e liso roxo). Achados: (a) **volume sobreviveu** à decimação; (b) **superfície lisa OK** — o facetamento que aparecia no clay some no render liso de entrega, 18k valida também o extremo gordo; (c) a **Melhoria de imagem NÃO inventou definição no torso** (barriga lisa) — risco dos `d1` parcialmente aposentado, confirmar no `b11_d1`; (d) as pernas vieram com leve definição indevida (não reprova sozinho). Conteúdo da folha: sobrepeso crível, torso correto pra `d1`.

**`m_b02_d3` processado em 23/07** — 9/9 validações, `shorts_frac=0.0724`, master+dist exportados. Render de QA em `qa/inspect/zen_m_b02_d3/` (4 vistas, clay+cavidade). **A definição muscular SOBREVIVEU à decimação para 18k** — gomos, serrátil e musculatura das costas legíveis no arquétipo mais exigente da grade. Ressalva de conteúdo: a folha saiu com volume muscular acima do `b02` (IMC 18,5–19,9 deveria ser bem mais magro — ombros estreitos, membros finos); serve pro piloto, mas o `b02_d3` de produção precisa vir mais magro e o descritor precisa endurecer o negativo ("ombros estreitos, membros finos, NÃO adicionar massa").

---

## 2. A folha-mãe

Três folhas foram geradas. A **segunda** (14:04) é a folha-mãe.

| Folha | Resultado |
|---|---|
| 1 (13:54) | ❌ definição alta demais — gomos abdominais, serrátil aparente. Era `d3`, não `d2`. |
| 2 (14:04) | ✅ **APROVADA** — abdômen liso, peitoral com forma. Salva como `_mother_m.png` |
| 3 (14:30) | ❌ voltou a definição; perfil espelhado |

Medição da folha 2: variação de altura entre as 3 vistas **0,71%**, topo da cabeça no mesmo pixel, canvas 1774×887, e é a única onde o corte em terços não encosta em nenhuma figura.

**O descritor original de `m_b05_d2` era vago e produziu a folha reprovada.** O descritor reforçado que funcionou:

> Peso normal e atlético, aparência saudável e ativa. Peitoral e ombros com forma clara, braços com volume moderado. Abdômen PLANO e LISO, SEM gomos abdominais visíveis, SEM serrátil aparente, SEM separação muscular marcada. Percentual de gordura médio, cerca de 17%: musculatura com forma, mas coberta por uma camada leve de gordura. NÃO é um físico de atleta seco.

---

## 3. Configuração da Meshy (validada no piloto)

| Opção | Valor |
|---|---|
| Aba | Espaço de Trabalho → Imagem para 3D |
| Tipo de Modelo | Padrão |
| Modelo de IA | Meshy 6 |
| Divisão automática | **Desligada** — quebraria a validação de malha única |
| Multi-View | **Ligado** — frontal principal + lado + costas |
| Pose | **DESLIGADA** ⚠️ contraria o runbook |
| Melhoria de imagem | **Ligada** |
| Licença | Privado |
| Download | GLB, **sem textura**, **sem Redimensionar** |

**Pose desligada é achado do piloto.** Ligada, o Meshy impõe pose canônica própria e abre demais os braços; desligada, ele segue a referência (que já está em A-pose). Resultado visivelmente melhor.

**Melhoria de imagem fica ligada nos 32.** Trocar no meio da biblioteca é pior que qualquer das duas opções. Risco a vigiar: pode adicionar definição que não existe na referência — apareceria nos `d1` do piloto.

Fluxo: **"Gerar Multi-visão" primeiro**, conferir o conjunto de vistas, só então "Gerar". Poupa os 20 créditos do modelo se as vistas saírem tortas.

Custo: 20 créditos por avatar. 32 × 20 = 640. Créditos resetam mensalmente e não acumulam.

---

## 4. Fatos medidos do GLB cru

Inspeção de `zen_m_b05_d2_raw.glb` (Blender 5.1 headless):

- 129.830 triângulos / 64.903 vértices — **muito abaixo dos ~211k que o README supõe**
- Malha única, sem armature, sem hierarquia, **sem material e sem textura**
- Watertight, 0 arestas de borda, 0 non-manifold, 1 ilha, normais corretas
- Simetria: desvio médio 2,2 mm, máximo 9,4 mm
- Bounding box 1,027 × 0,325 × 1,899 — altura no eixo Z (Blender), personagem encara −Y
- Centrado na origem **em todos os eixos**, inclusive o vertical: pés em Z ≈ −0,95, não em 0
- **Dedos das mãos e dos pés fundidos** (problema clássico do Meshy) — aceito, sem conserto viável
- Vincos de superfície na coxa, barra do short e coluna — vigiar após decimação

Topologia quase ideal. O `process.py` faz transformação, não reparo.

---

## 5. Constantes do `process.py`

```
CANONICAL_HEIGHT_M = 1.75
TARGET_TRIS        = 18000
TRIS_TOLERANCE     = 0.15
ZENITH_PURPLE_HEX  = "#8346C6"   # corpo
ZENITH_SHORTS_HEX  = "#0D0D12"   # short
SHORTS_LUMA_MAX    = 90
SHORTS_TRIS_MIN    = 0.02
SHORTS_TRIS_MAX    = 0.25
SHORTS_Z_MIN       = 0.35        # fração da altura canônica
SHORTS_Z_MAX       = 0.65
```

**Roxo `#8346C6`** = cor da palavra "poder" no título da Home. Amostrado da tela. O gradiente do avatar na tela (`#321E51` sombra → `#5C3A91` meio-tom → `#B17DDF` realce) é resultado **já iluminado** — não serve como base color.

**Short `#0D0D12`** em vez de preto puro: preto absoluto não recebe luz e vira buraco no corpo girando.

**Altura canônica 1,75 m:** o 1,899 do Meshy é arbitrário e muda a cada geração.

**Decimação parametrizada** (`--tris`): se o QA do piloto mostrar que `b02_d3` perdeu os gomos, sobe o alvo sem reescrever nada.

---

## 6. Separação corpo/short

O GLB não tem material nem UV — nada na geometria distingue o short. A solução: **projetar a imagem frontal de referência sobre a malha normalizada**. A malha foi gerada a partir dessa imagem, então as proporções batem. Pixel escuro + altura na faixa do quadril/coxa = short.

Resultado medido: `shorts_frac = 0,0929` (9,3%), dentro da faixa, 9/9 validações passam.

**Fallback bloqueia.** Sem `{id}_ref_front.png`, o script aborta com código 1 e não exporta. Motivo: a referência vem do recorte, faltar é erro de operação com conserto trivial; avatar de short roxo na CDN é defeito.

**Artefato conhecido e aceito:** borda serrilhada na cintura e na barra do short. Limite de topologia a 18k, não de método. Vai para avaliação no QA do piloto — **não suavizar**, alisar comeria a barra.

Manchas nas escápulas (sombras da frente vazando para as costas) foram eliminadas pelo filtro de faixa-Z.

---

## 6b. Teste de entrega no app (23/07) — resolvido o "quadriculado"

Ferramenta: `test/avatar_tester.html` — `<model-viewer>` com auto-rotate + sliders de peso/altura/%gordura que rodam o classificador do `ARCHETYPES.md` e mostram qual `id` o app escolheria. Servir por http: `python -m http.server 8000` na raiz (subir **destacado** com `Start-Process`, senão morre entre execuções). Abre em `http://127.0.0.1:8000/test/avatar_tester.html`.

**O "monte de quadrados" que aparecia no celular NÃO era falta de triângulo — era material.** Diagnóstico ponto a ponto:
- Material brilhante padrão (roughness 0.5 default) + normais Draco a 10 bits + sem `shade_smooth` explícito → a luz do model-viewer realçava cada faceta.
- Tentativa 1 (fosco, roughness 0.9): matou a faceta **e** a musculatura junto — corpo de sabonete. Rejeitado.
- **Solução (no `process.py`):** roughness **0.5** (brilho revela o músculo), `bpy.ops.object.shade_smooth()` antes do export (normais suaves por vértice; de quebra o dist caiu de ~278KB para ~68KB), e quantização Draco de **posição e normal a 14 bits** (o default 10 re-facetava).
- **18k confirmado suficiente** no teste em escala de app — músculo nítido, sem quadriculado. Gerado 40k/60k em `test/compare/` para comparar (18k=66KB, 40k=135KB, 60k=192KB); 18k aprovado, os maiores ficam de reserva.

**Formato de entrega decidido: GLB com auto-rotate (model-viewer).** Aprovado no tester; dispensa turntable pré-renderizado.

**Pendente:** a borda serrilhada do short — o Rogério pediu conserto individual por avatar, depois de travar a resolução. Ainda em aberto.

---

## 7. Mudanças nos documentos — ✅ APLICADAS 23/07

Lote aplicado após fechar o piloto, em `rules.md`, `CLAUDE.md`, `README.md`, `runbook.md` e `CHARACTER_BIBLE.md`. Duas divergências do plano original, propositais:

- **Item 3/6 (recorte):** o plano dizia "recorte pelo Claude no chat". Virou **recorte por script** (`crop.py`) — reprodutível, que era o motivo original da regra. `rules.md` §1 e `CHARACTER_BIBLE.md` §6 atualizados para isso.
- **Item 8 (créditos):** o plano dizia "a diferença 20 vs 30 não é textura, é a Divisão automática". Isso está **incorreto/confuso** — o piloto mediu 20 créditos sem textura, e textura é o +10 (Texture Stage). O `runbook.md` e o `README.md` §5 registram a versão medida (20 = Model Stage; textura seria +10). Divisão automática não altera crédito; ela foi documentada como regra de qualidade (quebra a malha única), não de custo.

Lista original abaixo, para histórico:

### `docs/CHARACTER_BIBLE.md`
1. Seção 5, descritor de `m_b05_d2` → substituir pelo texto reforçado (seção 2 deste arquivo).
2. Seção 6 e checklist → **direção do perfil deixa de reprovar folha**. Modelos de imagem têm discriminação ruim de lateralidade; nenhuma redação resolve. O conserto é espelhamento horizontal no recorte — operação exata, sem perda, corpo em A-pose é simétrico.
3. Seção 6, item 7 → o recorte é feito pelo Claude no chat, não à mão nem por divisão em terços.

### `runbook.md`
4. Fase 5, Pose → **desligada**.
5. Fase 5, adicionar: "Gerar Multi-visão" antes de "Gerar"; Melhoria de imagem ligada; Licença Privado; sem Redimensionar no download.
6. Fase 4 → recorte pelo Claude, com upscale para 1200px de altura e margem de 8% lateral / 5% vertical.
7. Fase 0 → concluída.

### `README.md`
8. Seção 2, item sobre créditos: a diferença 20 vs 30 **não é textura**, é a Divisão automática. Model Stage = 20, Texture Stage = 10.
9. Seção 4: o cru do Meshy 6 Pro tem ~130k faces, não ~211k. Calibrar decimação sobre o número real.
10. Nova regra: **Divisão automática sempre desligada** — separa o modelo em partes e quebra a validação de malha única.

---

## 8. Decisões em aberto

| Questão | Resolve quando |
|---|---|
| **GLB com auto-rotate vs turntable pré-renderizado** | piloto, testando no app |
| ~~Definição muscular sobrevive à decimação para 18k?~~ **RESOLVIDO 23/07: SIM** (QA `m_b02_d3`) | — |
| Resolução das vistas (~1200px vs 1040px recomendado pela Meshy) | QA do piloto |
| ~~Melhoria de imagem adiciona definição indevida nos `d1`?~~ **RESOLVIDO 23/07: leve, só pernas, torso sempre liso → mantida ligada** (`b08_d1` e `b11_d1`) | — |
| Tolerância para dedos fundidos | QA do piloto |
| Iluminação (glow, luz de estúdio) | junto com o formato de entrega |
| ~~Facetamento em superfície lisa a 18k~~ **RESOLVIDO 23/07: aceitável** — some no render liso de entrega (`b08_d1`) | — |
| ~~"Quadriculado" no model-viewer / celular~~ **RESOLVIDO 23/07: era MATERIAL, não geometria** | — |
| ~~GLB auto-rotate vs turntable~~ **model-viewer (GLB auto-rotate) aprovado no teste do tester** | — |
| ~~Borda serrilhada do short~~ **DECIDIDO 23/07: short desligado por ora** (`SHORTS_ENABLED=False`, corpo todo roxo). Feito por avatar, a mão no Blender, ao FINAL. 3 abordagens automáticas (suavizar borda / faixa-Z / caixa-Z+X) tentadas e revertidas — nenhuma regra serve para todos os corpos. | ao final da produção dos 32 |

---

## 9. PARKED — proposta híbrida (morph regional)

**Não descartada. Reavaliar depois do piloto.**

Proposta do Rogério: reduzir a grade de 32 para ~10 avatares e aplicar morph targets regionais (por circunferência) esculpidos em cada um.

**É distinta do projeto abandonado:** morph *dentro* de um modelo (shape keys na própria malha) sempre funciona; o que não funciona é morfar *entre* modelos de topologias diferentes. A distinção é válida.

**Ponto forte:** IMC vira seleção, morph cobre só circunferências. No projeto anterior, o morph de IMC era o que mais dava trabalho — aplicar gordura e tirar definição ao mesmo tempo é reescrever superfície, não deformar volume.

**Fatos que sustentam:** o app **obriga** medição mensal de circunferências, então há dado para alimentar os morphs em todo usuário.

**Restrição técnica:** o Decimate não roda em malha com shape keys. Os morphs teriam de ser esculpidos na malha já decimada de 18k — pouca topologia para deformação regional crível.

**Decisão:** seguir com os 32. Reavaliar quando o piloto disser se a definição sobrevive à decimação. Se for adiante, a forma preferida é **32 avatares + morphs regionais procedurais em cima**, gerados por script que roda em todos — não 10 esculpidos à mão.

---

## 10. Pendências do lado do app Zenith (outro repositório)

O app hoje só tem entrada para o eixo IMC. **O eixo de definição (`d1`/`d2`/`d3`) não tem como ser determinado** — o campo % de gordura está opcional e vazio.

Sem ele, cada faixa de IMC tem 3 avatares possíveis e o app não escolhe. É justamente o eixo que mostra ganho de músculo: quem treina um ano e troca gordura por massa mantendo o peso não muda de faixa de IMC, muda de `d1` para `d2`.

**Saída, com dados que já existem na tela:** fórmula US Navy, a partir de abdômen, pescoço e altura.

```
%gordura = 495 / (1,0324 − 0,19077 × log10(abdômen − pescoço)
                          + 0,15456 × log10(altura)) − 450
```
(cm; validar contra referência antes de subir)

Recomendações: promover **Pescoço** e **Abdômen** para fora do bloco "Todas opcionais"; precedência no classificador = % digitado → Navy → `d2` padrão; a tela Objetivo precisa de peso-meta **e** gordura-meta.

Não bloqueia nada aqui. Os 32 assets são os mesmos.