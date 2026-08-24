# -*- coding: utf-8 -*-
"""
Banco de casos do MORPH - o arbitro entre as implementacoes.

POR QUE ESTE ARQUIVO EXISTE
---------------------------
A regra "medidas do usuario -> influences dos shape keys" vive em TRES lugares:

    JS     test/avatar_tester.html
    Dart   lib/core/utils/avatar_morpher.dart   (no repo do app)
    aqui   este arquivo

E ate hoje nao havia arbitro nenhum entre elas. A selecao tem o
`selection_cases.json` justamente porque cuidado ao escrever nao substitui
banco de casos - a mesma licao vale aqui, e o morph e MAIS silencioso quando
erra: o corpo continua plausivel na tela.

⚠️ ESTA IMPLEMENTACAO FOI ESCRITA A PARTIR DO TEXTO DO CONTRATO
(`docs/INTEGRACAO_ZENITH.md` §12), NAO a partir do codigo Dart. Se ela fosse
uma traducao do Dart, concordaria com ele ate no erro - e o banco nao provaria
nada.

O `morph.py` deste repo NAO serve como referencia: ele CALIBRA (mede a malha no
Blender e publica as curvas). Consumir o mapa e outra funcao, e e esta.

USO
---
    python scripts/morph_cases.py            # gera test/morph_cases.json
    python scripts/morph_cases.py --check    # confere o banco contra a regra

Depois de gerar, copiar para o app:
    test/morph_cases.json  ->  zenith/test/fixtures/morph_cases.json
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(ROOT, "config", "morph_map.json")
INDEX_PATH = os.path.join(ROOT, "library.json")
OUT_PATH = os.path.join(ROOT, "test", "morph_cases.json")

REF_HEIGHT_M = 1.75


def interp_influence(curve, delta_cm):
    """Inverte a curva: dado o deslocamento em cm, devolve a influence.

    A curva e publicada como pares [influence, cm] em influence crescente.

    🔴 NAO usar `delta / cm_at_full`: a relacao nao e linear em todo morph. O
    `morph_neck` entrega +3,2 cm em influence 0,5 e so +3,8 em 1,0 - e um
    MINIMO de banda, e crescer o meio empurra o minimo para a borda travada
    pelo queixo. Multiplicar erra 68% ali.

    Fora das pontas, SATURA. A curva ja carrega os limites medidos daquele
    avatar; extrapolar inventa geometria que ninguem olhou (em -2,0 o braco
    vira cordao e o trapezio ganha vinco).
    """
    if len(curve) < 2:
        return 0.0
    pts = sorted(curve, key=lambda p: p[0])  # por influence
    if delta_cm <= pts[0][1]:
        return pts[0][0]
    if delta_cm >= pts[-1][1]:
        return pts[-1][0]
    for i in range(len(pts) - 1):
        cm_a, cm_b = pts[i][1], pts[i + 1][1]
        if cm_a <= delta_cm <= cm_b:
            span = cm_b - cm_a
            if abs(span) < 1e-9:
                return pts[i][0]
            t = (delta_cm - cm_a) / span
            return pts[i][0] + t * (pts[i + 1][0] - pts[i][0])
    return pts[-1][0]


def solve(entry, height_m, measures_cm, columns_used):
    """A regra inteira do §12.1.

    columns_used vazio = a selecao caiu no fallback por IMC, nenhuma
    circunferencia foi comparada, nao ha o que esculpir.
    """
    if height_m <= 0 or not entry.get("morphs") or not columns_used:
        return {}

    # A MESMA escala da selecao. Divergir aqui corrige para um alvo diferente
    # do que decidiu a escolha do corpo.
    k = REF_HEIGHT_M / height_m
    used = set(columns_used)
    out = {}

    # 1a passada: os morphs de TAMANHO.
    for m in entry["morphs"]:
        col = m.get("column")
        if col is None:
            continue
        key = m["key"]
        if col not in used:
            # 🔴 Coluna que a selecao descartou nao morfa. Zero EXPLICITO: o
            # shape key pode carregar valor de um render anterior.
            out[key] = 0.0
            continue
        v = measures_cm.get(col)
        if v is None or v <= 0:
            out[key] = 0.0
            continue
        delta = v * k - m["base_cm"]
        inf = interp_influence(m["curve"], delta)
        out[key] = max(m["influence_min"], min(m["influence_max"], inf))

    # 2a passada: as chaves ACOPLADAS (dependem do resultado da 1a).
    for m in entry["morphs"]:
        couple = m.get("couple")
        if not couple:
            continue
        driver = out.get(couple, 0.0)
        if m.get("couple_when") == "positive":
            v = driver if driver > 0 else 0.0
        else:
            v = driver
        out[m["key"]] = max(m["influence_min"], min(m["influence_max"], v))

    return out


def build_cases(mapa, index):
    """Casos que cobrem cada armadilha do contrato, para cada avatar do mapa."""
    by_id = {a["id"]: a for a in index["avatars"]}
    cols = index["selection"]["columns"]
    cases = []

    for aid, entry in sorted(mapa.items()):
        if "morphs" not in entry:
            continue
        avatar = by_id.get(aid)
        if avatar is None:
            continue
        base = {}
        for m in entry["morphs"]:
            col = m.get("column")
            if col:
                base[col] = m["base_cm"]

        todas = [c for c in cols if c in base]

        # 1. medidas IGUAIS a base, na altura de referencia -> tudo zero
        cases.append({
            "name": "%s/base" % aid,
            "why": "medida igual a base nao desloca nada",
            "input": {"avatar_id": aid, "height_m": REF_HEIGHT_M,
                      "measures_cm": dict(base), "columns_used": todas},
        })

        # 2. altura diferente -> prova que a escala e aplicada
        cases.append({
            "name": "%s/escala" % aid,
            "why": "a escala para 1,75 m e a MESMA da selecao",
            "input": {"avatar_id": aid, "height_m": 1.90,
                      "measures_cm": dict(base), "columns_used": todas},
        })

        # 3. corpo mais cheio e mais magro (meio da faixa de cada morph)
        for nome, sinal in (("cheio", 1.0), ("magro", -1.0)):
            med = {}
            for m in entry["morphs"]:
                col = m.get("column")
                if not col:
                    continue
                alvo = m["cm_max"] if sinal > 0 else m["cm_min"]
                med[col] = m["base_cm"] + alvo * 0.5
            cases.append({
                "name": "%s/%s" % (aid, nome),
                "why": "meio da faixa medida, dos dois lados",
                "input": {"avatar_id": aid, "height_m": REF_HEIGHT_M,
                          "measures_cm": med, "columns_used": todas},
            })

        # 4. estouro dos dois lados -> tem que SATURAR, nao extrapolar
        for nome, fator in (("estouro_alto", 3.0), ("estouro_baixo", -3.0)):
            med = {}
            for m in entry["morphs"]:
                col = m.get("column")
                if not col:
                    continue
                alvo = m["cm_max"] if fator > 0 else m["cm_min"]
                med[col] = m["base_cm"] + alvo * abs(fator)
            cases.append({
                "name": "%s/%s" % (aid, nome),
                "why": "fora da curva satura na ponta",
                "input": {"avatar_id": aid, "height_m": REF_HEIGHT_M,
                          "measures_cm": med, "columns_used": todas},
            })

        # 5. uma coluna DESCARTADA pela selecao (o caso da panturrilha 28)
        if len(todas) > 3:
            fora = todas[-1]
            med = dict(base)
            med[fora] = base[fora] * 0.7  # numero absurdo, como a fita errada
            cases.append({
                "name": "%s/descartada_%s" % (aid, fora),
                "why": "coluna que nao vota em QUAL corpo nao esculpe o corpo",
                "input": {"avatar_id": aid, "height_m": REF_HEIGHT_M,
                          "measures_cm": med,
                          "columns_used": [c for c in todas if c != fora]},
            })

        # 6. fallback por IMC: nenhuma coluna comparada
        cases.append({
            "name": "%s/fallback_imc" % aid,
            "why": "sem circunferencia comparada nao ha o que esculpir",
            "input": {"avatar_id": aid, "height_m": REF_HEIGHT_M,
                      "measures_cm": dict(base), "columns_used": []},
        })

    return cases


def main():
    ap = argparse.ArgumentParser(description="Banco de casos do morph.")
    ap.add_argument("--check", action="store_true",
                    help="confere o banco existente em vez de gerar")
    args = ap.parse_args()

    with open(MAP_PATH, encoding="utf-8") as f:
        mapa = json.load(f)
    with open(INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)

    versoes = {a["id"]: a["version"] for a in index["avatars"]}
    for aid, entry in mapa.items():
        if "morphs" not in entry:
            continue
        if aid in versoes and entry.get("glb_version") != versoes[aid]:
            sys.exit("TRAVA: %s calibrado no GLB v%s e o indice serve v%s. "
                     "Curva e medida SOBRE uma malha - gerar casos assim "
                     "assinaria um erro." % (aid, entry.get("glb_version"),
                                             versoes[aid]))

    # A PROCEDENCIA do banco, e ela e gravada na geracao E cobrada no --check.
    # Gravar sem cobrar de volta e o que deixou o `selection_cases.json` quatro
    # dias velho em 16/08 sem nenhuma regua daqui acusar - ver a mesma trava em
    # `select.py`, dentro do `--check`.
    stamp_atual = {
        "map_avatars": sorted(k for k in mapa if "morphs" in mapa[k]),
        "glb_versions": {k: mapa[k].get("glb_version")
                         for k in sorted(mapa) if "morphs" in mapa[k]},
        "index_generated_at": index["generated_at"],
    }

    if args.check:
        with open(OUT_PATH, encoding="utf-8") as f:
            banco = json.load(f)

        # TRAVA DE CARIMBO. Duas falhas, duas acoes opostas:
        #
        #   carimbo velho    -> `python scripts/morph_cases.py`, e ler o diff.
        #   influence errada -> a regra mudou de resposta; regerar apaga a prova.
        #
        # ⚠️ E e ela que da UTILIDADE a este --check fora da receita. Rodado logo
        # depois da geracao, ele compara o arquivo recem-escrito com a mesma
        # `solve()` que o escreveu: so pode passar. O carimbo e a unica dimensao
        # em que ele pode reprovar sem que nada no codigo tenha mudado.
        stamp = banco.get("generated_from") or {}
        divergiu = []
        for k, v in stamp_atual.items():
            if stamp.get(k) == v:
                continue
            if k == "index_generated_at":
                detalhe = "banco {!r}   indice {!r}".format(stamp.get(k), v)
            elif k == "map_avatars":
                no_banco = set(stamp.get(k) or [])
                agora = set(v)
                detalhe = "{} no banco, {} no mapa (so no mapa: {} | so no banco: {})".format(
                    len(no_banco), len(agora),
                    sorted(agora - no_banco) or "-", sorted(no_banco - agora) or "-")
            else:
                no_banco = stamp.get(k) or {}
                mudou = sorted(i for i in set(no_banco) | set(v)
                               if no_banco.get(i) != v.get(i))
                detalhe = "{} avatar(es) com glb_version diferente: {}".format(
                    len(mudou), ", ".join("{} v{}->v{}".format(i, no_banco.get(i), v.get(i))
                                          for i in mudou[:8]) + (" ..." if len(mudou) > 8 else ""))
            divergiu.append((k, detalhe))
        if divergiu:
            print("BANCO VELHO - test/morph_cases.json foi gerado de outro mapa/indice:")
            for k, detalhe in divergiu:
                print("  {:19s} {}".format(k, detalhe))
            sys.exit("Rode: python scripts/morph_cases.py  - e leia o diff antes de copiar\n"
                     "para o app. Curva e medida SOBRE uma malha: banco velho com GLB novo\n"
                     "publica influence que ninguem gerou.")

        ruins = 0
        for c in banco["cases"]:
            i = c["input"]
            got = solve(mapa[i["avatar_id"]], i["height_m"],
                        i["measures_cm"], i["columns_used"])
            for k, esperado in c["expect_influences"].items():
                if abs(got.get(k, 0.0) - esperado) > banco["tolerance"]["influence"]:
                    print("  DIVERGIU %s/%s: banco %.6f, regra %.6f"
                          % (c["name"], k, esperado, got.get(k, 0.0)))
                    ruins += 1
        if ruins:
            sys.exit("%d divergencia(s)" % ruins)
        print("%d casos conferidos, todos batem" % len(banco["cases"]))
        return

    cases = build_cases(mapa, index)
    for c in cases:
        i = c["input"]
        c["expect_influences"] = {
            k: round(v, 6)
            for k, v in solve(mapa[i["avatar_id"]], i["height_m"],
                              i["measures_cm"], i["columns_used"]).items()
        }

    payload = {
        "generated_from": stamp_atual,
        "tolerance": {"influence": 1e-06},
        "cases": cases,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("%d casos gravados em %s" % (len(cases), OUT_PATH))
    print("Copiar para o app: zenith/test/fixtures/morph_cases.json")


if __name__ == "__main__":
    main()
