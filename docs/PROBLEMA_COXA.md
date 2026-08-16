# O morph de COXA não fecha em 28 dos 76 avatares — problema aberto

> **Escrito para ser lido por quem não conhece o projeto.** É o enunciado de um
> problema que ficou em aberto em 11/08/2026, com os números medidos, o que já
> foi testado e as restrições que qualquer solução tem de respeitar.

## 1. O contexto mínimo

Uma biblioteca de **76 avatares 3D** (39 masculinos, 37 femininos) alimenta um
app de musculação. O usuário digita **9 circunferências** (pescoço, ombro,
peitoral, cintura, glúteo, bíceps, antebraço, coxa, panturrilha); o app escolhe
o avatar mais próximo e depois **esculpe o que sobra com shape keys** — um por
coluna de medida.

Cada avatar existe em duas formas:

| arquivo | o que é | tem roupa? |
|---|---|---|
| `02_master/{id}.glb` | malha normalizada, é onde as medidas **publicadas** foram tiradas | **não** |
| `03_dist/glb/{id}_v{n}.glb` | o que o app baixa: mesma malha + material + **short** (e **faixa** no feminino, como peça separada por material) | **sim** |

O calibrador de shape keys (`scripts/morph.py`) **lê o dist**, não o master —
por uma regra dura do projeto: quem lê o master e grava o dist **apaga a peça**
(já aconteceu, 39 shorts perdidos de uma vez).

E ele tem uma **trava de régua externa**: antes de calibrar, mede as 9 colunas
na malha base e compara com o `metrics/library_metrics.json`, que foi medido no
**master**, por outro caminho de código, antes de o calibrador existir. Se a
régua não reproduz o número publicado, ela não pode publicar deltas sobre ele.

## 2. O sintoma

**Oito das nove colunas batem em ±0,1 cm. A coxa não bate.**

| | avatares | desvio mediano | pior |
|---|---:|---:|---:|
| masculino | 38 medidos | **0,0 cm** | +6,9 |
| feminino | 37 medidos | **+3,6 cm** | **+18,5** |

Fora da tolerância (0,6 cm): **6 de 38 masculinos, 21 de 37 femininos.**
O sinal é **sempre positivo** — o dist lê a coxa mais grossa que o master.

Piores casos:

| avatar | IMC | dist | master | delta |
|---|---:|---:|---:|---:|
| `zen_f_b08h_d3` | 29,0 | 78,1 | 59,6 | **+18,5** |
| `zen_f_b04h_d1` | 24,1 | 68,9 | 53,1 | +15,8 |
| `zen_f_b05_d3` | 21,0 | 64,0 | 49,5 | +14,5 |
| `zen_m_b06_d3` | 27,4 | 63,4 | 56,5 | +6,9 |

Consequência: a trava derruba a coluna (e só ela — os outros oito morphs são
publicados), então **28 dos 76 avatares ficaram sem morph de coxa**, 21 deles
femininos.

## 3. Como a coxa é medida (`scripts/metrics.py`)

```python
CROTCH_FRAC   = 0.466      # ancora anatomica: fracao da altura
THIGH_BAND_M  = 0.060      # 6 cm
SCAN_STEP_M   = 0.005

crotch    = base + CROTCH_FRAC * height
leg_split = find_crotch(mesh, base, height)   # menor z em que as duas pernas
                                              # ja viraram UM laco (a pelve)
thigh_top = min(crotch, leg_split)
banda     = (thigh_top - 0.060, thigh_top - 0.005)
coxa      = pair_extreme(mesh, *banda, skip_torso=False, mode="max")
```

`pair_extreme` varre a banda de 5 em 5 mm, em cada z pega os **dois maiores
laços** da seção (perna esquerda e direita), tira a média dos dois perímetros,
guarda o z de maior valor — e **remede nesse z corrigindo a inclinação do
membro** (`axis_correct=True`, que projeta a seção perpendicular ao eixo da
perna em vez de horizontal).

## 4. 🔴 O achado que muda o diagnóstico — não é o master contra o dist

A hipótese inicial era "o tecido do short entra na circunferência". **Medido,
ela não se sustenta**, e o número aponta para outro lugar.

Rodando o `metrics.py` **direto no arquivo dist**, sem mais nada:

```
zen_f_b08h_d3   dist cru
  virilha anatomica 0.816 | leg_split 0.840 | topo 0.816
  banda 0.756..0.810 | z escolhido 0.806 | coxa 60.7 cm (esq 60.4 / dir 61.0)
  lacos crus naquele z: 73.9 cm e 73.9 cm
  -> publicado no master: 59.6 cm   (diferenca +1.1 cm, DENTRO do esperado
                                     para espessura de tecido)
```

Mas o `morph.py`, no mesmo avatar e na mesma coluna, lê **78,1 cm**. A diferença
entre os dois caminhos é **uma etapa só**:

> O `morph.py` não mede na malha do dist como ela está no arquivo. Ela chega com
> os vértices da costura corpo/short **duplicados** (glTF quebra primitiva por
> material), o que quebra os laços da seção — então ele mede numa **cópia
> SOLDADA** (`remove_doubles`). Essa soldagem existe porque sem ela o
> **antebraço** lia 48,3 cm onde o índice diz 29,8.

Ou seja: **a soldagem conserta o antebraço e estraga a coxa.** E há uma segunda
pista no mesmo bloco: os laços crus naquele z medem **73,9 cm**, e a correção de
inclinação os traz para **60,7** — 13 cm de correção. Um laço que precisa de 13 cm
de correção de eixo é um laço **oblíquo ou fundido**, não uma seção limpa de
coxa. Perto da virilha, o short une as duas pernas, e é plausível que depois de
soldado o "laço da perna" passe a ser um laço que atravessa a entreperna.

Isso também explica por que o feminino é muito pior: o short feminino é mais
curto e mais justo na virilha, e a faixa acrescenta uma terceira superfície.

## 5. O que já foi testado e NÃO resolve

- **Aumentar a tolerância da trava.** Não é ruído: +18,5 cm em coxa de 59,6 é
  31%. Publicar delta sobre essa base seria publicar centímetro errado no app.
- **Trocar `min(crotch, leg_split)` por só `crotch`.** No caso acima os dois são
  praticamente iguais (0,816 e 0,840), então o topo da banda não é a variável.
- **Derrubar o avatar inteiro quando uma coluna falha.** Era o comportamento
  antigo; custava 8 morphs bons para salvar 1 ruim. Hoje cai só a coluna.
- **🔴 Filtrar por MATERIAL (13/08) — o caminho 3 do §7, tentado e MATADO.**
  `carregar()` já sabe separar face por material (`Zenith_Body` vs
  `Zenith_Shorts`, gravado por polígono); a tentativa foi excluir as faces do
  short do mapa face→aresta usado **só na coluna coxa**, forçando o laço a
  fechar pela pele. Resultado, medido em `--fit` (nada gravado):
  - **Reduz o erro em quem já falhava** (`zen_f_b03_d1`: +11,2 → +3,4 cm),
    mas não o suficiente pra passar a tolerância de 0,6 cm em NENHUM dos
    avatares testados.
  - **🔴 E QUEBRA quem já passava**: em `zen_m_b02_d1` e `zen_m_b02_d3` — dois
    masculinos com a coxa OK hoje — a banda inteira (virilha−6cm até
    virilha−0,5cm) cai **debaixo do short**, sem nenhuma face de corpo ali.
    Sem face de corpo, o laço "fecha" por um fragmento qualquer e sai **9,9 cm**
    e **6,3 cm** onde o publicado é 51,5 e 54,5. Revertido antes de qualquer
    `--apply` — nenhum GLB foi tocado, mas **não usar esta abordagem sem
    fallback para a malha cheia quando o laço filtrado vier vazio/degenerado.**
  - Achado útil que sobrevive: a contaminação por short **não é a mesma coisa**
    em todo avatar. Às vezes é "a peça alarga o laço" (o caso do §4, dá pra
    filtrar), às vezes é "a peça é toda a banda" (não dá — não sobra pele pra
    medir ali, e a resposta certa provavelmente é o caminho 1, medir no
    master mesmo).
  - Ferramentas que sobraram, ambas em `qa/probe/sondas/`: `coxa_master_vs_dist.py`
    tinha um bug de path (`{id}.glb` em vez de `{id}_master.glb` — por isso
    nunca tinha rodado; corrigido) e `coxa_solda.py`, nova, isola se a solda em
    si (não o material) desloca a virilha — não desloca, `leg_split` bate
    entre malha crua e soldada no mesmo avatar.

- **🔴 Filtrar por material COM FALLBACK pra malha cheia (mesma sessão, tentativa
  2) — MATOU DE OUTRO JEITO.** Ideia: quando o laço corpo-só vem vazio ou
  menor que 70% da versão cheia (sinal do defeito acima), usar a versão cheia
  em vez do lixo. Consertou os 2 casos que a tentativa 1 tinha quebrado
  (`zen_m_b02_d1`/`d3` voltaram a bater exato). **Mas testado nos 48 avatares
  que hoje passam a coxa (não só os 2 conhecidos), achou 10 REGRESSÕES NOVAS**
  — `zen_m_b05i_d1` (−4,0), `b06_d1` (−5,1), `b06_d2` (−4,4), `b07_d2` (−3,1),
  `b08_d2` (−4,6), `b09_d2` (−5,9), `b10_d2` (−6,7), `zen_f_b06_d2` (−4,0),
  `b09h_d2` (−1,5), `b09i_d2` (−3,4). Nestes o laço corpo-só acha algo
  **plausível mas ERRADO** — grande o bastante pra não disparar o fallback de
  70%, pequeno o bastante pra não bater com o master. Revertido antes de
  qualquer `--apply`; nenhum GLB chegou a carregar essa calibração.

  **A lição que fica: o limiar de plausibilidade (0,7×) é arbitrário e não
  tem como ser calibrado direito com uma trava tão grosseira** — o que separa
  "corpo-só achou a perna certa" de "corpo-só achou outra coisa plausível" não
  é o TAMANHO do laço, é a TOPOLOGIA dele (se ele ainda é convexo, se cruza a
  linha média, etc.), que este método nunca olhou. Antes de tentar de novo,
  testar SEMPRE nos 48 que hoje passam, não só nos avatares conhecidos como
  problema — foi isso que expôs a tentativa 2.

## 6. Restrições que qualquer solução tem de respeitar

1. **O calibrador não pode ler o master e gravar o dist** — apaga a peça. (Ler o
   master *só para medir* e continuar gravando no dist é permitido e é a linha
   mais promissora; ninguém testou.)
2. **A régua tem de continuar sendo a do `metrics.py`**, não uma parecida: o
   número que o app compara com a fita do usuário é o daquele arquivo. Uma coxa
   medida por outro método deixa de ser comparável com o `library.json`.
3. **A soldagem não pode simplesmente sair** — ela é o que faz o antebraço, o
   bíceps e a cintura lerem certo no dist.
4. **`metrics.py` é usado pela biblioteca inteira** (76 avatares, o índice, a
   seleção). Mexer nele exige remedir tudo e conferir contra o
   `library_metrics.json` antes e depois.
5. O morph é **deslocamento de vértice** com máscara suave; a calibração busca a
   amplitude que dá um alvo em cm (6,0 cm para a coxa) e depois varre ±2,0 de
   influence procurando normal invertida. Só o valor em cm depende da régua — a
   máscara e o campo de deformação da coxa **não** estão sob suspeita.

## 7. A pergunta

**Como medir a circunferência da coxa numa malha que tem short, de forma
comparável com a medida feita na mesma malha sem short?**

Três caminhos plausíveis. O 3 foi tentado em 13/08 e morreu (§5) — não por
princípio errado, mas porque **filtrar por material não é o mesmo que filtrar
por topologia**: material some por completo em bandas onde a peça cobre a
banda inteira, e aí não sobra face de corpo nenhuma pra fechar o laço. Os
outros dois continuam de pé:

1. **Medir a coxa no master** (carregar os dois arquivos; a base geométrica é a
   mesma) e usar só o delta. Barato, mas precisa provar que o campo de
   deformação avaliado no master descreve o mesmo movimento no dist. **Favorito
   depois de 13/08** — é o único que não depende de sobrar pele visível na
   banda contaminada.
2. **Não soldar a coxa**: soldar para as colunas que precisam e medir a coxa na
   malha crua, onde a leitura já bate (+1,1 cm no caso medido).
3. ~~Escolher o laço por topologia em vez de por tamanho~~ — tentado como
   "filtrar por material" em 13/08, reduz mas não fecha o erro, e quebra 2
   avatares que hoje passam. Ver §5. Uma variante ainda não tentada: filtrar
   por material **e** cair de volta pra malha cheia quando o laço filtrado vier
   vazio ou anormalmente pequeno — não testada.

## 7b. ✅ RESOLVIDO em 14/08 — pelo caminho 4, que não estava nesta lista

Nenhum dos três caminhos acima foi o vencedor. O que fechou o problema foi
**parar de tentar trocar a medida** e corrigir o NÚMERO:

`calibrar_offset_coxa()`, em `scripts/morph.py`. A medição continua rodando pela
malha **cheia**, exatamente como sempre — sem nenhum risco de laço vazio ou
degenerado, que é como os três caminhos anteriores morreram. Só se soma um
**offset constante**, medido **uma vez** contra o `library_metrics.json` na base
sem deformação, que fecha exatamente a diferença ali.

**Placar: 75 dos 76 têm morph de coxa** (só o `zen_m_b06h_d3` não), contra os 48
de 11/08. O `dropped_columns` da biblioteca inteira hoje é `forearm` 3 ·
`biceps` 2 · `waist_min` 1 — **a coxa saiu da lista.**

### A suposição que isso carrega — está escrita porque não foi verificada

O excesso de tecido dentro da banda é **aproximadamente constante em cm ao longo
da amplitude do morph**. É plausível: a mesma máscara de empurrão que move a pele
próxima move o tecido próximo. Mas **não foi verificada contra medida real de
coxa deformada**, porque tal medida não existe no projeto.

A guarda é o teto: `COXA_OFFSET_MAX_CM = 22`, um pouco acima da pior
contaminação já vista na biblioteca (+18,5 cm no `zen_f_b08h_d3`). Acima disso o
offset não estaria corrigindo fabrico, estaria escondendo **landmark errado** — e
aí a coluna cai como sempre caiu.

### O que isso NÃO resolve

O `metrics.py` continua medindo a coxa errado no dist. O offset conserta o
**morph**, que é quem precisa da leitura; o `library_metrics.json` (medido no
master) nunca teve o problema. Se um dia algo mais passar a medir a coxa no dist,
o problema volta inteiro — os caminhos 1 e 2 continuam de pé para esse dia.

## 8. Onde estão as evidências no repositório

- `scripts/metrics.py` — a régua (`find_crotch`, `pair_at`, `pair_extreme`).
- `scripts/morph.py` — o calibrador (`medir`, `conferir_base`, e a soldagem no
  carregamento).
- `qa/probe/sondas/coxa_master_vs_dist.py` — a sonda que produziu o bloco do §4.
- `metrics/library_metrics.json` — os números publicados (a régua externa).
- `config/morph_map.json` — campo `dropped_columns` por avatar.
- `docs/LICOES.md` §7.25 — o registro curto da mesma coisa.
