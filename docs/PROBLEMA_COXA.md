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

Três caminhos plausíveis, nenhum testado:

1. **Medir a coxa no master** (carregar os dois arquivos; a base geométrica é a
   mesma) e usar só o delta. Barato, mas precisa provar que o campo de
   deformação avaliado no master descreve o mesmo movimento no dist.
2. **Não soldar a coxa**: soldar para as colunas que precisam e medir a coxa na
   malha crua, onde a leitura já bate (+1,1 cm no caso medido).
3. **Escolher o laço por topologia em vez de por tamanho**: `pair_extreme` pega
   os dois maiores laços; perto da virilha o maior pode ser um laço que
   atravessa a entreperna. Filtrar por posição em X e por ser convexo separaria
   perna de entreperna.

## 8. Onde estão as evidências no repositório

- `scripts/metrics.py` — a régua (`find_crotch`, `pair_at`, `pair_extreme`).
- `scripts/morph.py` — o calibrador (`medir`, `conferir_base`, e a soldagem no
  carregamento).
- `qa/probe/sondas/coxa_master_vs_dist.py` — a sonda que produziu o bloco do §4.
- `metrics/library_metrics.json` — os números publicados (a régua externa).
- `config/morph_map.json` — campo `dropped_columns` por avatar.
- `docs/LICOES.md` §7.25 — o registro curto da mesma coisa.
