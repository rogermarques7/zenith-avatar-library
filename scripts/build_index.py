#!/usr/bin/env python3
"""
build_index.py - Monta o library.json consumido pelo app Zenith.

Le  metrics/library_metrics.json   (IMC e circunferencias MEDIDOS de cada master)
    03_dist/glb/*.glb              (o que existe de fato para servir)
Gera library.json

A MUDANCA DE MODELO (schema 3)
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
    python scripts/build_index.py --cdn https://cdn.exemplo.com/avatars/
"""

import os
import re
import sys
import glob
import json
import argparse
from datetime import datetime, timezone

SCHEMA_VERSION = 3
REFERENCE_HEIGHT_M = 1.75
DEFAULT_CDN = "https://cdn.exemplo.com/avatars/"

# Cortes de % de gordura -> nivel de definicao (ARCHETYPES.md secao 5, passo 2).
# Heuristica de SELECAO de asset, nao classificacao clinica.
DEFINITION_THRESHOLDS = {
    "m": {"d3_below": 13.0, "d2_below": 20.0},
    "f": {"d3_below": 21.0, "d2_below": 29.0},
}

# Ordem de rebaixamento quando a linha de definicao nao tem avatar servivel.
DEFINITION_FALLBACK = ["d3", "d2", "d1"]

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
    orphans = []
    for path in sorted(glob.glob(os.path.join(root, "03_dist", "glb", "*_v*.glb"))):
        fname = os.path.basename(path)
        aid, version = fname[:-4].rsplit("_v", 1)

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
            "label": band_label(info["circumferences_cm"].get("waist_navel", {}).get("cm"),
                                info["height_m"], m.group("sex")),
            "waist_to_height": (round(info["circumferences_cm"]["waist_navel"]["cm"]
                                      / (info["height_m"] * 100.0), 3)
                                if info["circumferences_cm"].get("waist_navel", {}).get("cm")
                                else None),
            "body_shape": "medium",
            "version": int(version),
            "assets": {
                "glb": fname,
                "turntable": os.path.basename(turntable) if os.path.isfile(turntable) else None,
            },
            "circumferences_cm": {k: v.get("cm")
                                  for k, v in info["circumferences_cm"].items()},
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
    defaults = {s: nearest_id(avatars, s, "d2", DEFAULT_TARGET_BMI) for s in ("m", "f")}

    index = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "cdn_base": args.cdn,
        "reference_height_m": REFERENCE_HEIGHT_M,
        "selection": {
            "rule": "nearest_measured_bmi_within_definition",
            # Escala uniforme muda o IMC representado: corrigir ANTES de buscar.
            "target_bmi_formula": "bmi_usuario * (reference_height_m / altura_usuario_m)",
            "definition_thresholds_bodyfat_pct": DEFINITION_THRESHOLDS,
            "definition_fallback": DEFINITION_FALLBACK,
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
    if orphans:
        print("\nFORA DO INDICE ({}):".format(len(orphans)))
        for o in orphans:
            print("  " + o)
    if gaps:
        print("\nBuracos de cobertura (candidatos a insercao):")
        for g in gaps[:8]:
            print("  [{}] {} {}: IMC {:.1f} -> {:.1f}  (salto {:.1f})".format(
                g["priority"], g["sex"], g["definition"],
                g["bmi_from"], g["bmi_to"], g["bmi_step"]))
    print("\n-> {}".format(out))


if __name__ == "__main__":
    main()
