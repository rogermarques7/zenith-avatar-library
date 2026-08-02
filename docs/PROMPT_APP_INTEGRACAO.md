# Prompt para o repositório do app Zenith — alinhar a coleta de medidas

> Gerado em **01/08/2026**, sessão 20 da `zenith-avatar-library`.
> Substitui o rascunho do `INTEGRACAO_ZENITH.md` §8, que foi escrito a partir do
> *texto* dos arquivos. Este foi escrito a partir da **medição dos pixels** dos 9
> renders do guia — e a medição derrubou 3 das 5 afirmações do rascunho.
>
> **Colar o bloco abaixo numa sessão do Claude Code aberta em
> `C:\Users\VAIO\Desktop\ProjetosFlutter\zenith`.**

---

## Contexto que o outro lado precisa ter

A `zenith-avatar-library` é um segundo repositório, de produção de assets: 76
avatares 3D normalizados (mesma altura 1,75 m, pés em Y=0), cada um com
circunferências medidas em cm sobre a malha. O app vai deixar de exibir um avatar
2D estático e passar a escolher, entre esses 76, o corpo mais próximo do usuário.

**A escolha é feita por DISTÂNCIA NO ESPAÇO DE MEDIDAS** — as circunferências que
o usuário digita contra as circunferências medidas de cada avatar. Não é por IMC
sozinho (quebra em 2 dos 6 objetivos do app) e não é por percentual de gordura (o
app não estima em lugar nenhum, e circunferência não distingue músculo de
gordura na população deste app).

Consequência: **cada campo de medida do app virou entrada de um algoritmo.** Um
rótulo ambíguo ou um desenho que ensina o lugar errado deixa de ser detalhe de
UX e passa a escolher o corpo errado — em silêncio, porque nada no app consegue
detectar que o número veio do lugar errado.

As 8 circunferências que o app já coleta batem **uma a uma** com as que a
biblioteca mede. Isso não foi combinado, foi descoberto — e é o que torna a
integração barata. As mudanças abaixo são o que falta para os dois lados
falarem exatamente a mesma coisa.

---

## O prompt

```
Contexto: este app vai passar a escolher um avatar 3D entre 76 corpos medidos,
por distância no espaço das circunferências que o usuário informa. Cada campo de
medida virou entrada de algoritmo, então rótulo ambíguo e desenho que ensina o
ponto errado passam a escolher o corpo errado, sem nada detectar. As 4 mudanças
abaixo são o que falta para o app e a biblioteca de avatares falarem os mesmos
números. Faça uma de cada vez e me mostre o diff.

--- 1. O rótulo "Abdômen" contradiz o guia, e a diferença é de 6,5 cm ---

Hoje o app ensina uma medida e rotula outra:

  - lib/features/measurements/pages/measurement_guide_page.dart:113-117
    name: 'Cintura', e o texto manda medir "ao redor da PARTE MAIS ESTREITA do
    abdômen, logo acima do umbigo".
  - lib/core/l10n/app_localizations.dart:61   'waist': 'Abdômen (cm)'
  - lib/core/l10n/app_localizations.dart:200  'waist': 'Abdomen (cm)'
  - lib/features/measurements/pages/add_measurement_page.dart:458
    ('Abdômen', 'cm', _waistController)

Quem lê o rótulo mede no umbigo. Quem abre o guia mede o ponto mais estreito. Os
dois vão para a MESMA coluna waist_cm.

Por que importa: medido nos 76 avatares da biblioteca, a diferença entre a
cintura do umbigo e a cintura mínima tem mediana de 6,5 cm na faixa de IMC 17-40,
com máximo de 24,2 cm. 6,5 cm é mais do que separa dois avatares vizinhos da
grade — ou seja, o rótulo errado sozinho já troca o corpo escolhido. E o erro é
sistemático para o lado gordo, então não se cancela na média.

O guia está CERTO e não deve ser tocado: o desenho dele foi medido por pixel e o
anel cai exatamente onde a biblioteca mede a cintura mínima (fração 0,645 da
estatura contra 0,644 — diferença de 0,001).

Fazer:
  - 'waist' vira 'Cintura (cm)' em pt e 'Waist (cm)' em en;
  - a string fixa 'Abdômen' do add_measurement_page:458 vira 'Cintura';
  - onboarding_page.dart:506 tem Validators.bodyMeasurement(v, field: 'abdômen')
    — trocar para 'cintura' para a mensagem de erro não reintroduzir o termo.

ATENÇÃO antes de aplicar: isto muda a SEMÂNTICA de dado que já existe em
produção. Se já houver linhas em body_measurements com waist_cm preenchido, me
avise ANTES de mexer — os valores antigos foram digitados por quem leu
"Abdômen", e vão passar a ser lidos como cintura mínima. Não migre nada por
conta própria; só me diga quantas linhas existem.

--- 2. O texto do guia de ombro contradiz o próprio desenho ---

  - lib/features/measurements/pages/measurement_guide_page.dart:84-85

O texto manda medir "a LARGURA dos ombros de um deltoide ao outro (...) com a
fita na horizontal". Mas o assets/medidas/ombro.png já é um ANEL em volta dos
ombros — circunferência. Isolei o marcador roxo do PNG por pixel para confirmar:
é uma elipse fechada, na altura 0,795 da estatura, não uma barra reta.

Quem manda é o desenho, por dois motivos:

  a) Largura é inviável de auto-medir sozinho: fita reta, na horizontal, com as
     duas pontas fora do campo de visão de quem está medindo. Medida que o
     usuário faz errado é pior que medida menos elegante.
  b) Circunferência o usuário passa em volta e lê na frente do corpo — e é a
     única forma que a biblioteca consegue reproduzir na malha 3D.

Fazer: reescrever a instrução para circunferência, algo como "Passe a fita ao
redor dos ombros, na parte mais larga dos deltoides, com os braços relaxados ao
lado do corpo. Mantenha a fita nivelada." Não mexer no PNG.

--- 3. Falta o campo de ombro no ONBOARDING ---

O campo existe em add_measurement_page.dart:465 ('Ombro', 'cm',
_shoulderController), o modelo tem shoulderCm, o repositório grava shoulder_cm e
o guia tem a tela. Mas o onboarding não pede: os campos dele são weight, height,
waist, chest, arm, forearm, thigh, calf, hip, neck (onboarding_page.dart:475-585)
e param aí.

Por que importa: ombro é o melhor separador que existe entre músculo e gordura
com fita métrica — é a medida que distingue "cintura grossa de fisiculturista" de
"cintura grossa de sedentário", que é exatamente a ambiguidade que faz a seleção
por IMC errar. E o onboarding é onde a maioria dos usuários informa medidas pela
primeira e única vez; sem ele ali, o campo fica quase sempre nulo.

Fazer: adicionar o campo de ombro no onboarding, na ordem do guia (o guia é
Pescoço → Ombros → Peitoral → ...). Criar a chave 'shoulder' no
app_localizations ('Ombro (cm)' / 'Shoulder (cm)') e usá-la nos DOIS lugares — o
add_measurement_page:465 usa a string fixa 'Ombro' hoje.

Aproveitar: no add_measurement_page o Ombro é o ÚLTIMO da grade, enquanto no guia
ele é o segundo. Reordenar a grade para bater com o guia reduz a chance de o
usuário medir uma coisa e digitar em outro campo.

--- 4. O desenho da COXA ensina o lugar errado (este exige regerar imagem) ---

  - assets/medidas/coxa.png

O texto (measurement_guide_page.dart:132) manda medir "ao redor da PARTE MAIS
LARGA da coxa". O desenho mostra o anel bem mais abaixo, quase na descida para o
joelho.

Medido: o anel do PNG está na fração 0,394 da estatura. A parte mais larga da
coxa fica em 0,460 — colada na virilha. São 0,066 de estatura de diferença, ou
cerca de 11,6 cm numa pessoa de 1,75 m. A perna afina uns 22 cm nesse trajeto
(coxa 63,0 cm contra panturrilha 41,4 cm, medianas na faixa de usuário), então o
erro de leitura é grande.

Fazer: regerar o coxa.png com o anel no TERÇO SUPERIOR da coxa, logo abaixo da
virilha, mantendo o mesmo enquadramento, escala e estilo dos outros 9 renders
(corpo à esquerda, anel roxo, fundo preto, sem texto). Este é o único asset do
guia que precisa ser refeito.

--- O que NÃO deve ser mexido (auditado, está certo) ---

  - peitoral.png é anel e o texto pede circunferência na linha dos mamilos.
    Coerente. (Uma anotação antiga dizia que era barra reta; medido, é anel.)
  - panturrilha.png está em 0,214 da estatura, que é onde o ventre da
    panturrilha realmente fica. O desenho está certo — quem estava errada era a
    biblioteca, que media em 0,320 e pegava o joelho. Já corrigido do outro lado.
  - gluteo.png (0,507) e abdomen.png (0,645) batem com a biblioteca em 0,001.
  - pescoco, biceps, antebraco, altura: coerentes.
```

---

## Rastro da medição (para quando alguém quiser reabrir)

Os `at_frac` acima saíram de isolar o marcador roxo de cada PNG por componente
conexa e dividir a altura do anel pela altura da figura — a mesma unidade que o
`metrics.py` usa. A leitura se auto-calibra: bate em 0,001 em duas medidas
independentes (glúteo e cintura), e é isso que dá peso às divergências.

| guia do app | anel em `at_frac` | `metrics.py` | veredito |
|---|---:|---:|---|
| Glúteo | 0,507 | `hip` 0,507 | ✅ |
| Cintura | 0,645 | `waist_min` 0,644 | ✅ — e prova que o índice usava a coluna errada |
| Pescoço | 0,862 | `neck` 0,873 | ✅ |
| Ombro | 0,795 | `shoulder` **0,795** | ✅ — a biblioteca adotou a altura do app |
| Peitoral | 0,751 | `chest` 0,720 | ✅ tolerável, landmark |
| Coxa | 0,394 | `thigh` 0,460 | 🔴 **app errado** |
| Panturrilha | 0,214 | `calf` 0,320 → **0,265 (teto)** | 🔴 **biblioteca errada, corrigida** |

Bíceps e antebraço ficam fora da tabela: o master está em A-pose e o desenho tem
braço caído, então as alturas não são comparáveis. Não é divergência.
