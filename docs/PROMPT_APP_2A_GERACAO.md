# Para o app Zenith — subir a biblioteca da 2ª GERAÇÃO e as DUAS CINTURAS femininas

> Escrito em **02/10/2026**, sessão 42 da `zenith-avatar-library`, depois de o
> Rogério validar no testador os 103 corpos (peça, morph e o pescoço por tipo de
> corpo). **Abrir este arquivo numa sessão do Claude Code em
> `C:\Users\VAIO\Desktop\ProjetosFlutter\zenith` e seguir na ordem.**
>
> O contrato de fundo é o `INTEGRACAO_ZENITH.md` (§11 seleção, §12 morph, bloco
> "DECIDIDO EM 28/09"). Este arquivo é a lista do que muda AGORA. Tudo aqui foi
> lido no código do app em 02/10 — os caminhos e linhas são de lá.

---

## 0. O que mudou do lado da biblioteca, desde o que o app tem

| | no app hoje (`assets/avatars/`, 21/08) | biblioteca agora |
|---|---|---|
| corpos | 76 | **103** (55 f · 48 m) — a 2ª geração cobre FORMA: pera, maçã, retângulo, ampulheta |
| roupa | short + faixa | refeitos pela borda viva, aprovados nos 103 |
| shape keys | 9–10 por corpo | **8–12** (62 com 12): 9 de tamanho + até 3 de FORMA acopladas (`morph_waist_flatten`, `morph_hip_flatten`, `morph_chest_flatten`) |
| ombro | bloco "dragona" | deltoide |
| bíceps | faixa acima do cotovelo (errada) | no ventre do bíceps |
| pescoço | mesmo cilindro em todos | **por tipo de corpo** (campo medido na coleção) |
| seleção | `weights` único | **`weights_by_sex`** + **`ratio_checks`** + coluna `waist_min` só no feminino |
| GLB | ~210 KB a 1 MB | até 1,6 MB · **129 MB nos 103** · nome versionado (`{id}_v{n}.glb`) |

Arquivos: `library.json` (87 KB, schema 4), `config/morph_map.json` (857 KB),
`test/selection_cases.json` (24 casos de seleção + objetivo), `test/morph_cases.json`
(824 casos, 722 KB). Réguas do lado de cá, todas verdes em 02/10: seleção
**36/36**, morph **824/824**, material+peça **103/103**.

---

## 1. Copiar os quatro arquivos — SEMPRE juntos

```
cp ../zenith-avatar-library/library.json              assets/avatars/library.json
cp ../zenith-avatar-library/config/morph_map.json     assets/avatars/morph_map.json
cp ../zenith-avatar-library/test/selection_cases.json test/fixtures/selection_cases.json
cp ../zenith-avatar-library/test/morph_cases.json     test/fixtures/morph_cases.json
```

🔴 Índice novo com casos velhos (ou o contrário) reprova sem haver defeito — e
alarme falso ensina a desligar o alarme. Já aconteceu (16–19/08). Os quatro vão
no MESMO commit.

---

## 2. A regra de seleção — `weights_by_sex` e `ratio_checks`

A implementação de REFERÊNCIA é `scripts/select.py` da biblioteca (função
`select`). O app tem a mesma regra em `lib/core/utils/avatar_selector.dart`, e
ela hoje lê `sel.weights` (linhas 126, 235, 495). Duas mudanças:

**2a. Peso por sexo.** O índice publica:

```json
"weights_by_sex": {
  "m": { "waist_navel": 3.0, "hip": 2.0, "chest": 2.0, "shoulder": 2.0,
         "neck": 0.3, "biceps": 0.3, "forearm": 0.3, "thigh": 0.3, "calf": 0.3,
         "waist_min": 0.0 },
  "f": { "waist_navel": 2.0, "hip": 2.0, "chest": 2.0, "shoulder": 2.0,
         "neck": 0.3, "biceps": 0.3, "forearm": 0.3, "thigh": 0.3, "calf": 0.3,
         "waist_min": 1.0 }
}
```

Regra: `pesos = weights_by_sex[sexo] ?? weights`. O `weights` global continua
publicado com `waist_min: 0.0`, então índice velho e app velho não mudam de
comportamento. `AvatarLibraryModel` (`lib/domain/models/avatar_library_model.dart`,
`weights` na linha 99) precisa parsear o mapa novo — ausente = cai no global.

**2b. Trava de razão entre DUAS colunas do usuário.** O índice publica:

```json
"ratio_checks": [ { "sex": "f", "num": "waist_min", "den": "waist_navel",
                    "range": [0.648, 0.984] } ]
```

Depois de escalar para 1,75 m e ANTES da distância: se `num/den` cair fora de
`range`, a coluna `num` vai para `suspect_columns` e **não vota** — é fita no
lugar errado (mínima medida no mesmo ponto do umbigo, ou nas costelas). Mesmo
tratamento de quem cai fora de `plausible_range_cm`.

Trecho de referência (Python, `select.py`):

```python
for rc in sel.get("ratio_checks") or []:
    if rc.get("sex") != sex:
        continue
    n, d = user.get(rc["num"]), user.get(rc["den"])
    if n and d and not (rc["range"][0] <= n / d <= rc["range"][1]):
        if rc["num"] not in suspeitas:
            suspeitas.append(rc["num"])
```

**2c. `app_field_map`** já traz `"waist_min_cm": "waist_min"` — o campo do app
entra na seleção sem código novo, desde que o modelo de medidas o passe ao
seletor (`avatar_library_service.dart:220` e `:534` já mapeiam).

Conferência: os 24 casos de `selection_cases.json` têm que passar no teste Dart
que já existe — **inclusive os dois casos novos de duas cinturas**, que
discriminam a regra (com a mínima no campo único, a Joice real caía em `f_b08_d3`;
com as duas, cai em `f_b07i_d1`).

---

## 3. O morph — nada de regra nova, só conferir

`lib/core/utils/avatar_morpher.dart` já faz o acoplamento de forma
**genericamente** (linha 116: qualquer chave com `couple`), então os achatamentos
de quadril e peito entram sem código. O que conferir:

- os 824 casos de `morph_cases.json` passam;
- ⚠️ até **12 shape keys** por GLB (o caminho legado do three.js parava em 8 —
  a sonda `test/morph_probe.html` da biblioteca já mediu 9 chegando; conferir 12
  no `model_viewer_plus` no device, num corpo com 12, ex. `zen_m_b07k_d1`);
- 🔴 o GLB tem DUAS primitivas (corpo e peça): setar a influence em TODAS;
- 🔴 coluna fora de `columns_used` não morfa (§12.1 do contrato);
- 🔴 nunca `Δ / cm_at_full` — sempre interpolar a `curve`. No pescoço novo, os
  obesos extremos têm curva curta (ex. `zen_m_b11_d2` até +1,0 cm) DE PROPÓSITO:
  ali a régua do pescoço mede a papada e o morph não empurra além do natural.

---

## 4. A tela de medidas — mulher passa a ter DOIS campos de cintura

**Hoje** (`lib/features/measurements/pages/add_measurement_page.dart`): um campo
só, "Cintura", cujo SIGNIFICADO muda pelo sexo (`_cinturaEhMinima`, linhas
~402–440, ~828–840, ~907–957): homem → `waist_cm`; mulher → `waist_min_cm`.
Nasceu do veto de 18/09 (*"duas cinturas seguidas vai gerar fricção"*).

🔴 **Esse veto foi SUBSTITUÍDO pela decisão dele de 28/09**, reafirmada em
02/10: *"no app vai ter 2 campos de cintura"*. Motivo medido: com a mínima no
lugar do umbigo, uma mulher que não treina caía em corpo `d3` (9–12 de 24 na
simulação); com as duas votando, 1 de 24.

**Fica assim:**

| sexo | campos, nesta ordem | coluna | obrigatório |
|---|---|---|---|
| m | **Cintura** (umbigo) | `waist_cm` | como hoje |
| f | **Cintura (umbigo)** | `waist_cm` | sim |
| f | **Cintura mínima** — logo depois | `waist_min_cm` | **sim** (*"se for opcional muitas pessoas gordas vão cair em corpo atlético"*) |

- A coluna `waist_min_cm` já existe no banco, no modelo e no repositório
  (`body_measurement_model.dart:59`, `measurement_repository.dart:81`) — não
  precisa de migração.
- **Validação de plausibilidade no formulário:** razão mínima/umbigo fora de
  **0,648–0,984** → pedir para conferir as duas (é a mesma `ratio_checks`; o
  erro comum é medir os dois no mesmo ponto, razão ~1,0).
- **Linhas antigas ficam na coluna em que nasceram.** Mulher com medida antiga
  tem SÓ UMA das duas (a do campo único: `waist_min_cm` desde 18/09, `waist_cm`
  antes — o próprio `add_measurement_page` já distingue, linhas ~943–944): ao
  editar, a que existe vem preenchida e a outra vazia e obrigatória. Não copiar um para o outro — é
  reclassificar em silêncio um número medido noutro ponto.
- `cinturaEfetivaCm` (`body_measurement_model.dart:80`, `waistMinCm ?? waistCm`)
  é para EXIBIR; revisar quem a usa para não misturar as duas colunas na
  seleção.
- **Navy feminina** usa a mínima (`body_fat_calculator.dart:115/167` já faz) —
  só conferir que continua lendo `waistMinCm`.
- **`goal_target_calculator.dart`** trabalha em `waist_navel` (desde 21/08) — com
  a mulher passando a informar o umbigo, ele recebe o número certo; conferir de
  onde ele lê a cintura da usuária.

---

## 5. O guia "Como tirar suas medidas" — feminino ganha o passo da mínima

**Hoje** (`lib/features/measurements/pages/measurement_guide_page.dart`, passo
da cintura nas linhas ~190–215): UM passo, que no feminino troca o desenho e o
texto — `assetF: 'cintura_min'`, `arteCompletaF: true`, instrução por osso.

**Fica assim — pedido dele em 02/10:** *"já temos o asset antigo lá da cintura
umbigo, é só acrescentar ele e na sequência dele vem o asset da cintura
mínima"*.

| sexo | passo | asset | texto |
|---|---|---|---|
| m | Cintura | `assets/medidas/m/abdomen.png` | como hoje (umbigo) |
| f | **Cintura (umbigo)** | `assets/medidas/f/abdomen.png` (o `abdomen_f` de 21/08; `anel_guia.py` em 02/10: `at_frac 0,613`, mais perto de `waist_navel` — é o umbigo) | *"Passe a fita ao redor da cintura na altura do umbigo. Mantenha a fita nivelada e o abdômen relaxado."* — o mesmo do masculino |
| f | **Cintura mínima** — logo depois | `assets/medidas/f/cintura_min.png` (arte completa, `arteCompletaF`) | o texto por OSSO que já existe: entre a última costela e o osso do quadril + a dobra ao inclinar |

- O feminino passa de 10 para **11 passos**; o masculino fica com 10. O modelo
  `_GuideStep` hoje assume a mesma lista para os dois sexos — o jeito limpo é a
  lista depender do sexo (um passo só-feminino), não um passo que "vira outro".
- A ordem dos passos tem que ser a MESMA ordem dos campos do formulário (§4):
  quem mede e digita segue a mesma sequência.
- 🔴 **A instrução da mínima NUNCA pode ser "a parte mais fina"** — medida de
  fita é landmark, não extremo (em mulher magra o menor perímetro é debaixo das
  costelas). Manter a de osso + dobra.
- O `cintura_min.png` traz o próprio texto (três painéis); o app não escreve por
  cima dele — o comportamento de `arteCompletaF` continua. (O `anel_guia.py` não
  lê arte completa — deu 0,385, lendo um painel; a conferência dela é no olho.)

---

## 6. Subir os GLBs para o Storage — ANTES do build com o índice novo

```
python scripts/publish_avatars.py --dry-run   # tem que listar 103 .glb + o .hdr
python scripts/publish_avatars.py
```

- O script lê `../zenith-avatar-library/03_dist/glb/*.glb` (só a versão corrente
  de cada id está lá — a anterior é aposentada no lado de cá) e o `.hdr`.
- `upsert=false`: nome que já existe é PULADO; versão nova entra com nome novo.
  **Não usar `--force`** a não ser para reparar upload interrompido.
- **Ordem:** upload primeiro, app com o índice novo depois. O índice novo aponta
  para nomes novos (`_v24`, `_v26`…); se o app sair antes, o card fica preto.
  Os nomes velhos continuam no bucket, então quem está numa versão antiga do app
  segue funcionando.

---

## 7. Como validar no device

1. `flutter test` — seleção (24 + objetivo) e morph (824) verdes.
2. As três pessoas reais da biblioteca (`test/pessoas_reais.json` lá; fotos em
   `fotos reais joice e rogerio/`), digitando as medidas do `.txt` de cada uma:

| pessoa | sexo | avatar esperado | resto depois do morph |
|---|---|---|---|
| Rogério (176 cm, 93,55 kg) | m | `zen_m_b07k_d1` | RMS 0,8 cm |
| Joice (159 cm, 62,25 kg, umbigo 88 / mínima 77) | f | `zen_f_b07i_d1` | RMS 0,1 cm (+2,3 na mínima, que não morfa) |
| Ana Júlia (164 cm, 84 kg, umbigo 112 *estimado* / mínima 97) | f | `zen_f_b09h_d1` | RMS 6,2 cm (peitoral −18,6: limite da biblioteca) |

3. Num corpo de 12 shape keys, mexer as medidas e ver o corpo E a peça
   morfarem juntos.
4. O guia feminino: cintura (umbigo) e, em seguida, cintura mínima.

---

## 8. O que NÃO fazer

- Não editar nada da biblioteca a partir do app (os arquivos chegam por cópia).
- Não reimplementar a regra "de cabeça": a referência é o `select.py`, e o
  banco de casos é quem diz se as três implementações concordam.
- Não persistir o avatar escolhido nem a influence (continua em aberto, §11.5
  do contrato) — fora do escopo desta subida.
