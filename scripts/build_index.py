#!/usr/bin/env python3
"""
build_index.py - Monta o library.json consumido pelo app Zenith.

Le  metrics/library_metrics.json   (IMC e circunferencias MEDIDOS de cada master)
    03_dist/glb/*.glb              (o que existe de fato para servir)
Gera library.json

A MUDANCA DE MODELO (schema 4) - SELECAO POR MEDIDAS
    Ate o schema 3 o app escolhia por IMC dentro de uma linha de definicao, e a
    linha vinha de um limiar de % de GORDURA. Levantado no repositorio do app
    (INTEGRACAO_ZENITH.md secao 4): o app NAO estima gordura - o campo so existe
    se o usuario digitar ou se vier de balanca. A regra pedia uma entrada que o
    usuario tipico nunca tem, e nem quando tem ela fecha: os 12 avatares 'f d3'
    medem 22,7% a 52,6% contra o 'd3_below: 21,0' que o proprio indice publicava.

    A causa e estrutural: circunferencia nao distingue musculo de gordura, e a
    populacao deste app e exatamente onde isso quebra (cintura grossa de
    fisiculturista le como gordura).

    Agora a selecao sai das 9 circunferencias que os DOIS lados ja medem - o
    contrato fechou em 9 de 9 em 01/08. A distancia e a mesma funcao nos 9
    numeros do usuario e nos 9 de cada avatar. 'definition' (d1/d2/d3) continua
    no indice como METADADO (nome de arquivo, folha de contato), e nao filtra
    mais nada.

    COLUNA MARCADA ENTRA COM PESO ZERO. O metrics.py denuncia quando uma medida
    caiu na borda da banda ('at_band_edge') ou abaixo dela ('below_band', o caso
    do 'chest' em A-pose, 21 dos 51 da faixa de usuario). Doutrina da LICOES 1.8:
    extremo que pousa na borda nao e extremo, e corte. Comparar um numero desses
    e comparar ruido, entao ele sai da conta NAQUELE avatar e a distancia se
    renormaliza pelas colunas que sobraram. Decisao do Rogerio em 03/08.
    Excecao: 'thigh' com 'hi' e anatomia (a coxa e mais larga colada na virilha),
    entao nao conta como marcada - mesma excecao que o metrics.py ja documenta.

A MUDANCA DE MODELO ANTERIOR (schema 3)
    O schema 2 tinha uma grade FIXA de faixas de IMC e cada avatar declarava a
    qual faixa pertencia. Isso pressupunha que o corpo produzido correspondia a
    faixa pedida - e a medicao mostrou que nao corresponde: o 'b12_d1' foi
    pedido para IMC >= 38 e o corpo tem IMC 147.

    Agora cada avatar carrega o IMC que ele REALMENTE tem (volume da malha x
    densidade corporal) e o app escolhe o mais proximo dentro da mesma linha de
    definicao. O ID vira apenas nome de arquivo; quem classifica e a medida.

    Isso resolve tres coisas de uma vez:
      - inversoes somem sozinhas (b02_d2 e b03_d2 estavam trocados na grade
        nominal; ordenados por IMC medido cada um cai no seu lugar);
      - avatar novo e INSERCAO pura - entra na lista, vira um ponto a mais no
        eixo, nenhum arquivo existente muda de nome nem de papel;
      - o app nao precisa de atualizacao quando a biblioteca cresce.

ALTURA E IMC (a pegadinha)
    Escala uniforme NAO preserva IMC. Escalando por s, o volume vai com s^3 e a
    altura com s^2, entao o IMC efetivo vai com s. Um avatar medido a 1,75 m
    exibido para alguem de 1,90 m representa ~8,6% mais IMC.
    Por isso o app deve procurar por imc_alvo = imc_usuario * (1,75 / altura),
    e nao pelo IMC do usuario cru. A regra vai gravada no indice para o app nao
    ter que redescobrir.

USO
    python scripts/build_index.py
    python scripts/build_index.py --cdn https://outro.cdn/avatars/   (o default ja e o real)
"""

import os
import re
import sys
import glob
import json
import argparse
import statistics
from datetime import datetime, timezone

SCHEMA_VERSION = 4
REFERENCE_HEIGHT_M = 1.75

# ⚠️ O DEFAULT E O ENDERECO REAL, e isso e de proposito.
#     Ate 05/08 ele era `https://cdn.exemplo.com/avatars/`, e o `--cdn` existia
#     para trocar. So que o library.json daqui e COPIADO para
#     `assets/avatars/` do app, e quem copiasse depois de um rebuild sem a flag
#     trocava o bucket do Supabase por um dominio inexistente - o avatar some da
#     home e nada no log diz por que. E o mesmo argumento da regra 8 do
#     CLAUDE.md contra uma flag `--bump`: **flag se esquece, e esquece-la
#     reintroduz o bug em silencio.** O bucket e PUBLICO, entao a URL nao e
#     segredo e nao fere a regra 1 (sem chave, sem secret, sem rede - este
#     script continua sem falar com ninguem, so escreve o texto no indice).
DEFAULT_CDN = ("https://nhloypjtpgyndmjtcpcf.supabase.co"
               "/storage/v1/object/public/avatars/")

# As 9 colunas que o app coleta e a biblioteca mede. O contrato fechou em 9 de 9
# em 01/08 (shoulder foi a ultima a entrar). 'wrist' e 'waist_navel' ficam de
# fora da DISTANCIA de proposito: o app nao coleta nenhuma das duas.
SELECT_COLUMNS = ["neck", "shoulder", "chest", "waist_min", "hip",
                  "biceps", "forearm", "thigh", "calf"]

# De onde cada coluna vem na tabela `body_measurements` do app. O unico par que
# nao e obvio e o da cintura: `waist_cm` e a cintura MINIMA desde 01/08 (o app
# ja renomeou o rotulo de "Abdomen" para "Cintura"), entao ele bate com
# `waist_min` e NAO com `waist_navel` - a diferenca mediana e 6,5 cm na faixa de
# usuario, mais do que separa dois avatares vizinhos. INTEGRACAO_ZENITH secao 3.
APP_FIELD_MAP = {
    "neck_cm": "neck", "shoulder_cm": "shoulder", "chest_cm": "chest",
    "waist_cm": "waist_min", "hip_cm": "hip", "arm_cm": "biceps",
    "forearm_cm": "forearm", "thigh_cm": "thigh", "calf_cm": "calf",
}

# O TRONCO ESCOLHE O AVATAR; OS MEMBROS SAO ABSORVIDOS PELO MORPH (04/08).
#
# Ate 03/08 as nove colunas pesavam 1,0 — o certo enquanto nao havia morph, e
# errado depois que ele passou a existir. Peso igual gasta a escolha discreta
# tentando acertar o que uma shape key resolve, e paga isso onde a shape key NAO
# resolve. Medido no corpo do Rogerio (cintura 107,5 · panturrilha 36):
#
#   pesos iguais       -> b05_d1  com CINTURA errando +14,1 cm  (morph nenhum cobre)
#   tronco mandando    -> b05h_d2 com peito -0,9 · ombro +1,9 · cintura +5,0
#
# Tres razoes medidas para o tronco mandar:
#   1. a cintura arrasta a estrutura junto (r 0,90 com coxa, 0,94 com gluteo na
#      colecao masculina), entao acerta-la acerta o corpo;
#   2. a desproporcao mora nos MEMBROS — a biblioteca so tem corpos
#      proporcionais (nenhum masculino tem cintura >100 e panturrilha <40), e
#      corrigir isso e exatamente o que o morph faz bem;
#   3. o morph do TRONCO e o arriscado: o peitoral e medido NA LINHA DA AXILA,
#      onde o zenith_avatar_engine quebrou cinco vezes. Passou no teste, mas com
#      folga que nao se gasta a toa.
#
# ⚠️ PROVISORIOS ate o teste de faixa. Os numeros abaixo foram validados no caso
# real acima, mas a regra final e peso ~ 1/(faixa do morph)²: coluna que a shape
# key move muito precisa de pouca precisao na escolha. As faixas serao MEDIDAS
# (como o z_cap foi), e entao estes pesos se derivam delas em vez de serem
# escolhidos.
SELECT_WEIGHTS = {
    "waist_min": 3.0,      # manda: e a coluna que a biblioteca nao consegue morfar muito
    "hip": 2.0,
    "chest": 2.0,
    "shoulder": 2.0,
    "neck": 0.3,           # daqui para baixo, o morph resolve
    "biceps": 0.3,
    "forearm": 0.3,
    "thigh": 0.3,
    "calf": 0.3,
}

# Quantas colunas precisam sobrar (presentes no usuario E nao marcadas no avatar)
# para a distancia valer. Abaixo disso a comparacao e de ruido e o app deve cair
# no fallback por IMC.
MIN_COLUMNS = 3

# ---------------------------------------------------------------------------
# TETO DA CONTRIBUICAO DE UMA COLUNA — protege contra UMA medida errada.
#
# O caso que obrigou isto (04/08): um usuario digitou 28 cm de panturrilha
# (media errado; o valor certo era 36). A distancia e uma soma de QUADRADOS,
# entao aquela coluna sozinha respondeu por 46% da decisao e escolheu um avatar
# com 16 cm de erro de CINTURA. Uma medida ruim em nove estragou as outras oito,
# e em silencio - o corpo entregue continua plausivel na tela.
#
# O teto e 1,5 desvios-padrao, e o numero foi MEDIDO, nao escolhido: entre um
# corpo e o vizinho mais proximo da biblioteca, o residuo por coluna fica em
# p50 0,21 · p90 0,64 · p99 1,49 dp. Ou seja, um residuo legitimo passa de 1,5
# em 0,9% dos casos - acima disso e quase certamente medida errada, nao corpo.
# Cortar ali preserva a DIRECAO (a coluna continua puxando para o lado certo) e
# tira o poder de veto.
Z_CAP = 1.5

# Ordem das linhas de definicao. Continua existindo para percorrer a biblioteca
# e achar buracos de cobertura - NAO e mais filtro de selecao (ver cabecalho).
DEFINITION_FALLBACK = ["d3", "d2", "d1"]

# Linha de definicao usada pelo fallback por IMC (quando o usuario nao digitou
# circunferencia nenhuma). d2 e o meio: nem definicao alta nem baixa.
FALLBACK_DEFINITION = "d2"

# ---------------------------------------------------------------------------
# VETOR DE OBJETIVO - para onde o corpo anda em cada um dos 6 objetivos do app.
#
# POR QUE ISTO MORA AQUI. A tela "Objetivo Zenith" mostra DOIS avatares, atual e
# meta. Achar o da direita por IMC quebra em dois dos seis casos, e quebra feio:
#   - 'recomp' nao move o IMC   -> a meta sai IDENTICA ao atual, dois corpos
#                                  iguais lado a lado sob "31% da meta alcancada";
#   - 'gain_muscle' SOBE o IMC  -> o app escolhe um corpo mais GORDO e o chama de
#                                  "sua melhor versao".
# A biblioteca da a DIRECAO (e ela quem conhece o espaco de medidas); o app da o
# TAMANHO DO PASSO. Direcao x tamanho = um ponto, e o mais proximo desse ponto e
# o avatar da direita. INTEGRACAO_ZENITH secao 5.
#
# OS NUMEROS SAO A TABELA DAQUELA SECAO, TRADUZIDA - nao ha nada de novo aqui:
#   ↓↓ = -1,0   ↓ = -0,5   ↓ leve = -0,25   = 0   ↑ = +0,5   ↑↑ = +1,0
# A unidade e o DESVIO-PADRAO da coluna (scale_cm), nao o centimetro: um passo de
# 1,0 na cintura masculina vale 15,6 cm e no pescoco vale 5,0 cm, que e a
# proporcao em que essas medidas de fato variam entre corpos vizinhos.
#
# ONDE A TABELA CALA, A COLUNA NAO SE MOVE. 'neck' e 'forearm' nao aparecem nela;
# 'forearm' entra junto com o grupo de membros ('braco · coxa · panturrilha'),
# mas 'neck' fica em 0,0 nos tres objetivos de proposito. Chutar -0,25 nele
# porque "pescoco tambem afina" seria inventar constante sem medida (LICOES 1.5).
GOAL_VECTORS = {
    "lose_weight": {
        "has_target_body": True,
        "summary": "Reduzir gordura mantendo massa magra",
        "direction": {"waist_min": -1.0, "hip": -0.5, "chest": -0.25, "shoulder": -0.25,
                      "neck": 0.0, "biceps": 0.0, "forearm": 0.0, "thigh": 0.0, "calf": 0.0},
    },
    "gain_muscle": {
        "has_target_body": True,
        "summary": "Ganhar massa muscular",
        "direction": {"waist_min": 0.0, "hip": 0.0, "chest": 0.5, "shoulder": 0.5,
                      "neck": 0.0, "biceps": 1.0, "forearm": 1.0, "thigh": 1.0, "calf": 1.0},
    },
    "recomp": {
        "has_target_body": True,
        "summary": "Recomposicao: perder gordura e ganhar musculo ao mesmo tempo",
        "direction": {"waist_min": -0.5, "hip": -0.25, "chest": 0.5, "shoulder": 0.5,
                      "neck": 0.0, "biceps": 0.5, "forearm": 0.5, "thigh": 0.5, "calf": 0.5},
    },
    # Estes tres NAO TEM CORPO-ALVO, e isso ja esta no codigo do app: o
    # `maxLevels()` devolve null para eles. A tela nao deve mostrar dois
    # avatares - deve mostrar um. Publicar 'has_target_body: false' e o que
    # impede o app de inventar uma meta para quem nao pediu meta.
    "maintain": {"has_target_body": False, "summary": "Manter o corpo atual", "direction": None},
    "improve_health": {"has_target_body": False, "summary": "Melhorar indicadores de saude", "direction": None},
    "performance": {"has_target_body": False, "summary": "Performance esportiva", "direction": None},
}

# Passo padrao, em desvios-padrao. O app deveria dar o tamanho a partir da meta
# que o usuario declarou - mas hoje ele NAO TEM meta corporal nenhuma
# ('target_weight'/'goal_weight': zero ocorrencias no repositorio), entao a
# biblioteca publica um passo utilizavel para a tela existir. 1,0 desvio-padrao e
# um corpo visivelmente diferente sem ser outra pessoa.
GOAL_DEFAULT_STEP = 1.0

# Uma letra apos a banda marca um avatar INSERIDO (ex.: b05h, e depois b05i
# para a 2a insercao na mesma regiao). Letras a partir de 'h' em ordem, o que
# mantem a ordenacao alfabetica coerente: b05 < b05h < b05i < b06.
# A letra registra a INTENCAO de onde o avatar foi mirado, nao onde ele caiu -
# quem ordena a biblioteca e o measured_bmi (ver ARCHETYPES secao 4).
ID_RE = re.compile(r"^zen_(?P<sex>[mf])_b\d{2}[a-z]?_(?P<definition>d[123])$")

# Faixa onde os usuarios realmente estao. Buraco de cobertura fora dela e
# irrelevante na pratica, por maior que seja o salto em pontos de IMC.
USER_BMI_RANGE = (17.0, 40.0)
DEFAULT_TARGET_BMI = 23.5      # meio da faixa normal; alvo do avatar padrao


def nearest_id(avatars, sex, definition, target_bmi):
    """Avatar mais proximo de um IMC alvo. Sem janela fixa: janela deixa a
    biblioteca sem padrao quando nenhum corpo cai dentro dela."""
    line = [a for a in avatars if a["sex"] == sex and a["definition"] == definition]
    if not line:
        return None
    return min(line, key=lambda a: abs(a["measured_bmi"] - target_bmi))["id"]


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def band_label(waist_cm, height_m, sex="m"):
    """Rotulo legivel, por CINTURA/ALTURA - nao por IMC.

    IMC nao separa musculo de gordura: o 'b07_d3' tem IMC 35,7 e sairia como
    "obesidade II", sendo que e um fisiculturista de cintura 85 cm. A razao
    cintura/altura separa: 0,49 nele, contra 0,82 no 'b08_d1'.

    Existe so para humano (folha de contato, tester). O app nunca decide por
    aqui; ele decide por 'measured_bmi' dentro da linha de definicao.
    """
    if not waist_cm:
        return None
    r = waist_cm / (height_m * 100.0)
    # Os CORTES sao os mesmos nos dois sexos - e a mesma razao cintura/altura,
    # que ja e adimensional. So a concordancia do adjetivo muda.
    for limit, name in ((0.43, "muito magro"), (0.50, "magro"),
                        (0.55, "medio"), (0.63, "cheio"), (0.75, "muito cheio")):
        if r < limit:
            return name.replace("magro", "magra").replace("medio", "media") \
                       .replace("cheio", "cheia") if sex == "f" else name
    return "extremo"


def unreliable_columns(circumferences):
    """Colunas cuja medida o metrics.py denunciou NAQUELE avatar.

    Duas marcas, mesma consequencia: o numero nao esta medindo o que o nome diz.
      - 'below_band'   -> o 'chest' em A-pose, onde o braco funde com o tronco
                          abaixo da linha do mamilo (21 dos 51 da faixa de
                          usuario). Acima daquela altura o casco convexo engole o
                          braco; abaixo, deixa de ser peito.
      - 'at_band_edge' -> o extremo pousou na borda da banda, entao o extremo de
                          verdade esta provavelmente do lado de fora e o que saiu
                          e o limite disfarcado de medida (LICOES 1.8).

    Excecao: 'thigh' com 'hi'. A coxa e mais larga colada na virilha, entao o
    maximo cair no teto e anatomia - o metrics.py ja exclui essa coluna do aviso
    pelo mesmo motivo, com comentario no codigo.
    """
    bad = []
    for col in SELECT_COLUMNS:
        m = circumferences.get(col) or {}
        if m.get("below_band"):
            bad.append(col)
        elif m.get("at_band_edge") and col != "thigh":
            bad.append(col)
    return bad


def column_scales(avatars):
    """Desvio-padrao de cada coluna, por sexo - o divisor que torna centimetros
    de partes diferentes comparaveis entre si.

    Sem isso a distancia vira soma de cm crus, e a cintura (dp 15,6 cm no
    masculino) domina o pescoco (dp 5,0 cm) so por ser um numero maior. Dividindo
    pelo dp, uma unidade passa a significar 'o quanto essa medida costuma variar
    na biblioteca' nas nove colunas.

    Calculado sobre a FAIXA DE USUARIO: as caricaturas de IMC 100+ existem para
    cobrir o eixo, mas incluir uma delas triplicaria o divisor e achataria a
    distancia de todo mundo. Se a linha for curta demais para um dp significar
    algo, usa a biblioteca inteira daquele sexo, e avisa.
    """
    scales, notes = {}, []
    for sex in sorted({a["sex"] for a in avatars}):
        pool = [a for a in avatars
                if a["sex"] == sex
                and USER_BMI_RANGE[0] <= a["measured_bmi"] <= USER_BMI_RANGE[1]]
        if len(pool) < 5:
            pool = [a for a in avatars if a["sex"] == sex]
            notes.append("{}: menos de 5 avatares na faixa de usuario, "
                         "escala calculada sobre a colecao inteira".format(sex))
        scales[sex] = {}
        for col in SELECT_COLUMNS:
            v = [a["circumferences_cm"][col] for a in pool
                 if a["circumferences_cm"].get(col) is not None]
            # Uma coluna constante (ou quase) daria divisor zero e distancia
            # infinita; o piso de 0,1 cm mantem a conta finita sem inventar
            # dispersao onde nao ha.
            scales[sex][col] = max(round(statistics.pstdev(v), 1), 0.1) if len(v) > 1 else None
    return scales, notes


def main():
    ap = argparse.ArgumentParser(description="Monta o library.json a partir das medidas.")
    ap.add_argument("--cdn", default=DEFAULT_CDN, help="base do CDN")
    ap.add_argument("--out", default=None, help="caminho de saida (padrao: library.json)")
    args = ap.parse_args()

    root = repo_root()
    metrics_path = os.path.join(root, "metrics", "library_metrics.json")
    if not os.path.isfile(metrics_path):
        sys.exit("metrics/library_metrics.json nao existe. Rode antes:\n"
                 "  python scripts/metrics.py --all")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)["avatars"]

    avatars = []
    orphans = []      # ficaram FORA do indice
    stale = []        # entraram, mas tem sobra de versao antiga no disco

    # Um id pode ter mais de uma versao no disco - o escritor aposenta a
    # anterior, mas um arquivo copiado a mao ou um export interrompido deixa
    # sobra. Servir as duas colocaria o MESMO id duas vezes no indice, com o
    # nearest_id escolhendo a que calhasse. Aqui vale a versao MAIS ALTA, e a
    # sobra e denunciada em vez de ignorada em silencio.
    newest = {}
    for path in sorted(glob.glob(os.path.join(root, "03_dist", "glb", "*_v*.glb"))):
        fname = os.path.basename(path)
        aid, version = fname[:-4].rsplit("_v", 1)
        if not version.isdigit():
            orphans.append(fname + " (versao nao numerica)")
            continue
        version = int(version)
        if aid not in newest or version > newest[aid]:
            newest[aid] = version

    for aid, version in sorted(newest.items()):
        fname = "{}_v{}.glb".format(aid, version)
        older = [v for v in range(1, version)
                 if os.path.isfile(os.path.join(root, "03_dist", "glb",
                                                "{}_v{}.glb".format(aid, v)))]
        if older:
            stale.append("{}: servindo v{}, mas sobrou no disco {}"
                         .format(aid, version,
                                 ", ".join("v{}".format(v) for v in older)))

        m = ID_RE.match(aid)
        if not m:
            orphans.append(fname + " (nome fora da convencao)")
            continue
        if aid not in metrics:
            # Sem medida nao ha classificacao possivel: fora do indice, e
            # avisado - silenciar seria publicar um avatar inalcancavel.
            orphans.append(fname + " (sem medida em library_metrics.json)")
            continue

        info = metrics[aid]
        turntable = os.path.join(root, "03_dist", "turntable", "{}_v{}.webp".format(aid, version))

        avatars.append({
            "id": aid,
            "sex": m.group("sex"),
            "definition": m.group("definition"),
            "measured_bmi": info["est_bmi"],
            "measured_mass_kg": info["est_mass_kg"],
            # O ROTULO continua saindo do 'waist_navel', e nao da coluna nova.
            # Ele e texto para humano (folha de contato, tester) e os cortes de
            # 0,43/0,50/0,55/0,63/0,75 foram calibrados naquela razao; trocar a
            # coluna sem recalibrar jogaria a biblioteca inteira uma casa para o
            # magro (a diferenca mediana entre as duas cinturas vale 0,061 de
            # razao, e os cortes distam ~0,06 um do outro). Recalibrar exigiria
            # inventar cinco numeros novos sem medida que os sustente.
            "label": band_label(info["circumferences_cm"].get("waist_navel", {}).get("cm"),
                                info["height_m"], m.group("sex")),
            # Ja o NUMERO publicado e o da cintura minima, porque ele existe para
            # ser comparado com o 'waist_cm' do app, que e minima desde 01/08.
            "waist_to_height": (round(info["circumferences_cm"]["waist_min"]["cm"]
                                      / (info["height_m"] * 100.0), 3)
                                if info["circumferences_cm"].get("waist_min", {}).get("cm")
                                else None),
            "body_shape": "medium",
            "version": version,
            "assets": {
                "glb": fname,
                "turntable": os.path.basename(turntable) if os.path.isfile(turntable) else None,
            },
            "circumferences_cm": {k: v.get("cm")
                                  for k, v in info["circumferences_cm"].items()},
            # Peso zero para estas na distancia - o app nao precisa saber POR QUE
            # cada uma caiu, so que comparar aquele numero e comparar ruido.
            "unreliable_columns": unreliable_columns(info["circumferences_cm"]),
            "approved": True,
        })

    avatars.sort(key=lambda a: (a["sex"], a["definition"], a["measured_bmi"]))

    # Buracos de cobertura: onde o salto entre avatares vizinhos e grande, o
    # usuario que cai no meio recebe um corpo distante do dele. Nao e erro -
    # e a lista de onde INSERIR os proximos avatares.
    gaps = []
    for sex in sorted({a["sex"] for a in avatars}):
        for definition in DEFINITION_FALLBACK:
            line = [a for a in avatars if a["sex"] == sex and a["definition"] == definition]
            for lo, hi in zip(line, line[1:]):
                step = round(hi["measured_bmi"] - lo["measured_bmi"], 1)
                if step >= 5.0:
                    mid = (lo["measured_bmi"] + hi["measured_bmi"]) / 2.0
                    gaps.append({
                        "sex": sex, "definition": definition,
                        "between": [lo["id"], hi["id"]],
                        "bmi_from": lo["measured_bmi"], "bmi_to": hi["measured_bmi"],
                        "bmi_step": step,
                        # Salto absoluto engana: o buraco de 40 pontos entre IMC
                        # 107 e 148 quase nao tem usuario, enquanto um de 8
                        # pontos em IMC 30 atinge muita gente.
                        "priority": "high" if USER_BMI_RANGE[0] <= mid <= USER_BMI_RANGE[1] else "low",
                    })
    gaps.sort(key=lambda g: (g["priority"] != "high", -g["bmi_step"]))

    # `nearest_id` ja devolve None quando a linha nao existe, entao o feminino
    # sai null sozinho enquanto a onda feminina nao for produzida - e passa a
    # sair preenchido no primeiro build depois dela, sem tocar aqui.
    defaults = {s: nearest_id(avatars, s, FALLBACK_DEFINITION, DEFAULT_TARGET_BMI)
                for s in ("m", "f")}

    scales, scale_notes = column_scales(avatars)

    # Faixa coberta por coluna e por sexo — sobre a COLECAO INTEIRA, nao so a
    # faixa de usuario: um corpo fora da faixa comum ainda e um corpo, e o que
    # se quer denunciar e o valor que nenhum avatar consegue representar.
    ranges = {}
    for sex in sorted({a["sex"] for a in avatars}):
        pool = [a for a in avatars if a["sex"] == sex]
        ranges[sex] = {}
        for col in SELECT_COLUMNS:
            v = [a["circumferences_cm"][col] for a in pool
                 if a["circumferences_cm"].get(col) is not None]
            ranges[sex][col] = [round(min(v), 1), round(max(v), 1)] if v else None

    index = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cdn_base": args.cdn,
        "reference_height_m": REFERENCE_HEIGHT_M,
        "selection": {
            "rule": "weighted_measure_distance",
            # O que o app precisa fazer, na ordem:
            #
            # 1. ESCALAR o usuario para 1,75 m. Os masters sao todos normalizados
            #    para a altura de referencia, entao comparar cm crus de alguem de
            #    1,90 m com eles acha sempre um corpo maior do que ele e.
            #    Circunferencia vai LINEAR com a escala (diferente do IMC, que vai
            #    com s - ver o cabecalho do arquivo).
            # 2. Somar as colunas que existem DOS DOIS LADOS: presentes no
            #    usuario (todas as circunferencias sao opcionais no onboarding) e
            #    fora de 'unreliable_columns' naquele avatar.
            # 3. Dividir pelo peso somado, e nao pelo numero de colunas - assim
            #    quem preencheu 4 campos e quem preencheu 9 recebem distancias na
            #    mesma escala, e um avatar nao ganha vantagem por ter coluna
            #    marcada.
            # 4. Menor distancia vence, dentro do mesmo 'sex'.
            "columns": SELECT_COLUMNS,
            "app_field_map": APP_FIELD_MAP,
            "weights": SELECT_WEIGHTS,
            "scale_cm": scales,
            # Teto por coluna, em desvios-padrao. Ver Z_CAP no topo do arquivo:
            # existe porque a distancia soma QUADRADOS e uma medida errada
            # sozinha passava a decidir o avatar.
            "z_cap": Z_CAP,
            # Faixa que a biblioteca cobre em cada coluna. Serve para o app
            # DENUNCIAR: valor fora daqui nao tem corpo que o represente, e o
            # mais provavel e que a fita tenha ido no lugar errado. A panturrilha
            # de 28 cm que motivou o teto estava abaixo do minimo de 29,4.
            "plausible_range_cm": ranges,
            "user_scale_formula": "medida_ref = medida_usuario * (reference_height_m / altura_usuario_m)",
            "distance_formula": (
                "sqrt( soma_i( w_i * ((u_i - a_i) / s_i)^2 ) / soma_i( w_i ) ), "
                "i sobre as colunas presentes no usuario e ausentes de "
                "avatar.unreliable_columns; u_i ja escalado para a altura de "
                "referencia; s_i = scale_cm[sexo][i]"
            ),
            "unreliable_column_weight": 0.0,
            "min_columns": MIN_COLUMNS,
            # Empate tem que ser resolvido por criterio DECLARADO. Sem ele, duas
            # implementacoes empatadas devolvem o que a ordenacao interna de cada
            # linguagem calhar de por primeiro, e o banco de casos acusaria uma
            # divergencia que nao e de regra - o pior tipo de alarme falso.
            "tie_break": "menor id em ordem alfabetica",
            # Sexo e COLECAO, nao filtro de exibicao: o candidato so pode sair de
            # avatars com o mesmo 'sex'. Nunca comparar entre colecoes.
            "sex_is_collection": True,
            # Quando o usuario nao digitou circunferencia nenhuma (peso e altura
            # sao os unicos campos que o onboarding exige de fato), sobra o IMC.
            # Ele nao separa musculo de gordura - e por isso que ele e FALLBACK e
            # nao regra - mas e melhor que um avatar fixo.
            "fallback": {
                "rule": "nearest_measured_bmi",
                "when": "menos de min_columns colunas comparaveis",
                "definition": FALLBACK_DEFINITION,
                "target_bmi_formula": "bmi_usuario * (reference_height_m / altura_usuario_m)",
            },
            # Aposentado no schema 4: o app NAO estima % de gordura, e o limiar
            # nao fechava nem quando o dado existia. Ver cabecalho do arquivo.
            "retired": ["definition_thresholds_bodyfat_pct", "definition_fallback"],
        },
        "goal": {
            "vectors": GOAL_VECTORS,
            "default_step": GOAL_DEFAULT_STEP,
            "step_unit": "desvios-padrao da coluna (selection.scale_cm)",
            # A ORIGEM E O AVATAR ATUAL, nao as medidas cruas do usuario. Duas
            # razoes: o usuario pode ter deixado 6 dos 9 campos vazios, e a tela
            # compara dois CORPOS - partir do corpo que ela ja mostra a esquerda
            # e o que faz o par ser coerente.
            "origin": "avatar_atual",
            "target_formula": ("alvo_i = atual_i + passo * direction_i * "
                               "selection.scale_cm[sexo][i], sobre as colunas i "
                               "ausentes de atual.unreliable_columns"),
            "then": "o avatar da meta e o mais proximo do ponto alvo, pela mesma "
                    "distancia da selection",
            # As duas travas que so a biblioteca garante (INTEGRACAO_ZENITH 5).
            # Sem a primeira, 'recomp' mostra o mesmo corpo duas vezes; sem a
            # segunda, um passo pequeno pode cair num vizinho do lado ERRADO e o
            # app promete emagrecimento exibindo um corpo mais cheio.
            "guards": {
                "must_differ_from_current": True,
                "must_move_along_direction": ("a projecao de (candidato - atual) sobre "
                                              "a direcao tem que ser positiva"),
            },
            # A trava acima e AGREGADA de proposito. As duas alternativas foram
            # medidas nos 51 avatares da faixa de usuario x 3 objetivos:
            #   sinal por coluna          -> 23 dos 153 ficam SEM meta, e a
            #                                cintura desviada PIORA (29 -> 38),
            #                                porque rejeitar o melhor candidato
            #                                so faz cair num pior;
            #   coluna parada travada     -> 99 dos 153 ficam sem meta.
            # E o peso extra na coluna parada tambem nao paga (29 -> 21 no peso
            # 5,0, com a mediana do desvio SUBINDO). A conclusao nao e de regra:
            # o corpo "mesma cintura, braco maior" nao existe na biblioteca.
            "known_limitation": (
                "em 29 dos 51 corpos da faixa de usuario a meta de 'gain_muscle' "
                "vem com a cintura mais cheia (mediana +5,8 cm), porque nao ha "
                "vizinho mais musculoso de cintura igual. E buraco de COBERTURA, "
                "nao erro de selecao"
            ),
            # Por isso a regra devolve 'drift_sd': quanto cada coluna que o
            # objetivo declara PARADA de fato andou, em desvios-padrao. Quem
            # consome decide se mostra, se ressalva ou se cala - o que nao pode e
            # a tela prometer uma direcao e exibir outra sem ninguem saber.
            "reports_drift": True,
            # Progresso no app hoje e XP de treino/refeicao/sono - esforco, nao
            # corpo. Quem tem 90 dias de aderencia perfeita e abdomen parado nao
            # pode ver outro corpo na tela.
            "progress_source": "medidas, nunca XP",
        },
        "default": defaults,
        "coverage_gaps": gaps,
        "avatars": avatars,
    }

    out = args.out or os.path.join(root, "library.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print("library.json: {} avatar(es)".format(len(avatars)))
    for sex in sorted({a["sex"] for a in avatars}):
        for definition in DEFINITION_FALLBACK:
            line = [a for a in avatars if a["sex"] == sex and a["definition"] == definition]
            if line:
                print("  {} {}: {} avatares, IMC {:.1f} a {:.1f}".format(
                    sex, definition, len(line),
                    line[0]["measured_bmi"], line[-1]["measured_bmi"]))
    print("\nEscala da distancia (dp em cm na faixa de usuario):")
    for sex in sorted(scales):
        print("  {}: {}".format(sex, "  ".join(
            "{} {}".format(c, scales[sex][c]) for c in SELECT_COLUMNS)))
    for n in scale_notes:
        print("  aviso: " + n)

    # Coluna marcada nao e erro a consertar - e medida que o app precisa ignorar
    # naquele avatar. Imprimir o placar impede que ela cresca em silencio.
    marked = {}
    for a in avatars:
        for c in a["unreliable_columns"]:
            marked.setdefault(c, []).append(a)
    if marked:
        print("\nColunas com peso ZERO na distancia (medida denunciada pelo metrics.py):")
        for c in SELECT_COLUMNS:
            hits = marked.get(c)
            if not hits:
                continue
            in_range = sum(1 for a in hits
                           if USER_BMI_RANGE[0] <= a["measured_bmi"] <= USER_BMI_RANGE[1])
            print("  {:10s} {:2d} avatares ({} na faixa de usuario)".format(c, len(hits), in_range))
        worst = max(avatars, key=lambda a: len(a["unreliable_columns"]))
        print("  pior caso: {} com {} de {} colunas fora".format(
            worst["id"], len(worst["unreliable_columns"]), len(SELECT_COLUMNS)))

    if orphans:
        print("\nFORA DO INDICE ({}):".format(len(orphans)))
        for o in orphans:
            print("  " + o)
    if stale:
        print("\nSOBRA DE VERSAO ({}) - conferir antes de subir ao CDN:".format(len(stale)))
        for s in stale:
            print("  " + s)
    if gaps:
        print("\nBuracos de cobertura (candidatos a insercao):")
        for g in gaps[:8]:
            print("  [{}] {} {}: IMC {:.1f} -> {:.1f}  (salto {:.1f})".format(
                g["priority"], g["sex"], g["definition"],
                g["bmi_from"], g["bmi_to"], g["bmi_step"]))
    print("\n-> {}".format(out))


if __name__ == "__main__":
    main()
