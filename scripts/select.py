#!/usr/bin/env python3
"""
select.py - A REGRA DE SELECAO, em Python, e o banco de casos que o Dart tem que
responder igual.

POR QUE ESTE ARQUIVO EXISTE
    A mesma regra vive em tres lugares: aqui, no `qa/avatar_tester.html` (JS) e
    no app Zenith (Dart). Tres copias de uma regra divergem - e o que diverge
    aqui e QUAL CORPO O USUARIO VE, que e o produto inteiro. O CLAUDE.md ja
    proibe segunda copia do bloco de prompt pelo mesmo motivo.

    A defesa nao e "escrever com cuidado": e `test/selection_cases.json`, um
    banco de casos entrada->id esperado que as tres implementacoes rodam. Copia
    que diverge passa a REPROVAR, em vez de escolher outro corpo em silencio.

    Este arquivo e a implementacao de REFERENCIA. Quando a regra mudar, muda aqui
    primeiro, regera os casos, e as outras duas se ajustam ate passarem.

USO
    python scripts/select.py --demo 1.78 82 --sex m --waist 88 --chest 104
    python scripts/select.py --cases      # regera test/selection_cases.json
    python scripts/select.py --check      # confere a implementacao contra o banco
"""

import os
import sys
import json
import math
import argparse

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INDEX_PATH = os.path.join(REPO, "library.json")
CASES_PATH = os.path.join(REPO, "test", "selection_cases.json")


def load_index(path=INDEX_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def bmi(weight_kg, height_m):
    return weight_kg / (height_m * height_m)


def select(index, sex, height_m, weight_kg, measures):
    """Escolhe o avatar mais proximo. `measures` vem com as chaves DO APP
    (`waist_cm`, `arm_cm`, ...), que e o formato que o app tem na mao - a
    traducao para os nomes da biblioteca e responsabilidade daqui, via o
    `app_field_map` publicado no indice.

    Devolve sempre um dicionario com o id, a distancia, as colunas que entraram
    na conta e qual regra decidiu - o app precisa saber se caiu no fallback para
    nao prometer precisao que nao teve.
    """
    sel = index["selection"]
    ref_h = index["reference_height_m"]
    field_map = sel["app_field_map"]
    weights = sel["weights"]
    scales = sel["scale_cm"].get(sex, {})

    pool = [a for a in index["avatars"] if a["sex"] == sex and a.get("approved")]
    if not pool:
        return None

    # 1. O usuario vai para a estatura de referencia. Circunferencia escala
    #    LINEAR com a altura; e o IMC que escala de outro jeito (ver o
    #    build_index). Fazer isso depois da distancia seria tarde: a comparacao
    #    ja teria sido em escalas diferentes.
    k = ref_h / height_m
    user = {}
    for app_field, col in field_map.items():
        v = measures.get(app_field)
        if v is not None and v > 0:
            user[col] = v * k

    target_bmi = bmi(weight_kg, height_m) * k

    # DUAS DEFESAS, porque uma so nao bastou.
    #
    # (1) FORA DA FAIXA -> SAI DA CONTA. Se o valor esta fora do que a
    #     biblioteca inteira cobre, nenhum corpo o representa e ele e quase
    #     certamente fita no lugar errado. Deixa-lo votar, ainda que com teto,
    #     FAVORECE quem estiver por acaso mais perto do numero errado — foi
    #     assim que o caso 'outlier' reprovou quando so havia teto.
    # (2) DENTRO DA FAIXA -> fica, com TETO de z_cap desvios-padrao, porque
    #     medida errada tambem acontece dentro da faixa.
    #
    # As duas voltam marcadas: a tela pede para conferir em vez de escolher o
    # corpo errado calado.
    suspeitas = []
    faixas = (sel.get("plausible_range_cm") or {}).get(sex, {})
    for col, u in user.items():
        f = faixas.get(col)
        if f and (u < f[0] or u > f[1]):
            suspeitas.append(col)

    z_cap = sel.get("z_cap")
    fora = set(suspeitas)

    scored = []
    for a in pool:
        bad = set(a.get("unreliable_columns") or [])
        num = den = 0.0
        used = []
        for col, u in user.items():
            if col in bad or col in fora:
                continue
            av = (a.get("circumferences_cm") or {}).get(col)
            s = scales.get(col)
            if av is None or not s:
                continue
            w = weights.get(col, 1.0)
            if w <= 0:
                continue
            # TETO: nenhuma coluna passa de z_cap desvios-padrao. Preserva a
            # direcao e tira o poder de veto de uma medida errada. Sem isto uma
            # panturrilha digitada errada respondia por 46% da decisao.
            z = (u - av) / s
            if z_cap:
                z = max(-z_cap, min(z_cap, z))
            num += w * z * z
            den += w
            used.append(col)
        if len(used) >= sel["min_columns"]:
            # Dividir pelo peso somado, nao pela contagem: quem preencheu 4
            # campos e quem preencheu 9 saem na mesma escala de distancia.
            scored.append((math.sqrt(num / den), sorted(used), a))

    if scored:
        # Desempate por id em ordem alfabetica. Nao e cosmetico: sem criterio
        # declarado, Python e Dart empatados devolveriam o que a ordenacao de
        # cada um calhasse de por primeiro, e o banco de casos acusaria uma
        # divergencia que nao e de regra.
        scored.sort(key=lambda t: (round(t[0], 9), t[2]["id"]))
        dist, used, a = scored[0]
        return {"id": a["id"], "distance": round(dist, 4),
                "columns_used": used, "rule": sel["rule"],
                "suspect_columns": sorted(suspeitas)}

    # 2. Fallback: sem colunas comparaveis suficientes, sobra o IMC. Peso e
    #    altura sao os unicos campos que o onboarding realmente exige.
    fb = sel["fallback"]
    line = [a for a in pool if a["definition"] == fb["definition"]]
    if not line:
        line = pool
    # Mesma casa decimal do desempate da distancia (9): as duas implementacoes
    # tem que arredondar igual antes de comparar, ou empatam em lugares
    # diferentes.
    line.sort(key=lambda a: (round(abs(a["measured_bmi"] - target_bmi), 9), a["id"]))
    a = line[0]
    return {"id": a["id"], "distance": round(abs(a["measured_bmi"] - target_bmi), 4),
            "columns_used": [], "rule": fb["rule"],
            "suspect_columns": sorted(suspeitas)}


def select_goal(index, sex, current_id, goal, step=None):
    """O avatar da DIREITA na tela "Objetivo Zenith": para onde este corpo anda
    se a pessoa perseguir o objetivo declarado.

    Devolve None quando o objetivo nao tem corpo-alvo ('maintain',
    'improve_health', 'performance'). Isso nao e falha - e a resposta certa, e a
    tela deve mostrar UM avatar nesses casos. O proprio app ja concorda: o
    `maxLevels()` devolve null para os tres.
    """
    goal_cfg = (index.get("goal") or {}).get("vectors", {}).get(goal)
    if not goal_cfg or not goal_cfg.get("has_target_body"):
        return None

    sel = index["selection"]
    g = index["goal"]
    scales = sel["scale_cm"].get(sex, {})
    direction = goal_cfg["direction"]
    step = g["default_step"] if step is None else step

    by_id = {a["id"]: a for a in index["avatars"]}
    current = by_id.get(current_id)
    if not current or current["sex"] != sex:
        return None

    # O ponto alvo. As colunas marcadas do avatar ATUAL ficam de fora inteiras:
    # somar um deslocamento a um numero que nao esta medindo o que o nome diz
    # produz um alvo errado com cara de preciso.
    bad_here = set(current.get("unreliable_columns") or [])
    target, moving = {}, {}
    for col in sel["columns"]:
        if col in bad_here:
            continue
        cur = (current.get("circumferences_cm") or {}).get(col)
        s = scales.get(col)
        if cur is None or not s:
            continue
        d = direction.get(col, 0.0)
        target[col] = cur + step * d * s
        if d:
            moving[col] = d

    if not target or not moving:
        return None

    pool = [a for a in index["avatars"]
            if a["sex"] == sex and a.get("approved") and a["id"] != current_id]

    scored = []
    for a in pool:
        bad = set(a.get("unreliable_columns") or [])
        num = den = 0.0
        used = []
        # Trava 2: o candidato tem que ANDAR NA DIRECAO. Sem ela, um passo
        # pequeno cai num vizinho do lado errado e o app exibe um corpo mais
        # cheio sob a palavra "emagrecer".
        proj = 0.0
        for col, t in target.items():
            if col in bad:
                continue
            av = (a.get("circumferences_cm") or {}).get(col)
            s = scales.get(col)
            if av is None or not s:
                continue
            w = sel["weights"].get(col, 1.0)
            if w <= 0:
                continue
            num += w * ((t - av) / s) ** 2
            den += w
            used.append(col)
            d = moving.get(col)
            if d:
                proj += d * (av - current["circumferences_cm"][col]) / s
        if len(used) >= sel["min_columns"] and proj > 0:
            scored.append((math.sqrt(num / den), proj, sorted(used), a))

    if not scored:
        return None
    scored.sort(key=lambda t: (round(t[0], 9), t[3]["id"]))
    dist, proj, used, a = scored[0]

    # DENUNCIAR O DESVIO DAS COLUNAS PARADAS. O vetor declara que 'gain_muscle'
    # nao mexe na cintura - mas quem escolhe e o vizinho mais proximo, e em 29
    # dos 51 corpos da faixa de usuario o vizinho mais musculoso tambem e mais
    # cheio de cintura (mediana +5,8 cm). Nao e defeito da regra: foi medido que
    # nem trava por sinal (piora para 38) nem peso extra na coluna parada (chega
    # a 21 no peso 5,0, com a mediana subindo) consertam. O corpo "mesma cintura,
    # braco maior" NAO EXISTE na biblioteca - e um buraco de cobertura, e a
    # producao dele depende de credito na Meshy.
    #
    # Entao a regra entrega o desvio junto com a resposta, em desvios-padrao, em
    # vez de escondê-lo: quem consome decide se mostra, se ressalva ou se cala.
    # Mesma doutrina do 'at_band_edge' - a medida que nao da para consertar tem
    # que pelo menos sair marcada.
    drift = {}
    for col in target:
        if moving.get(col) or col in set(a.get("unreliable_columns") or []):
            continue
        av = (a.get("circumferences_cm") or {}).get(col)
        s = scales.get(col)
        if av is None or not s:
            continue
        delta = (av - current["circumferences_cm"][col]) / s
        if abs(delta) >= 0.05:
            drift[col] = round(delta, 2)

    return {"id": a["id"], "distance": round(dist, 4), "projection": round(proj, 4),
            "columns_used": used, "goal": goal, "step": step,
            "drift_sd": drift,
            "max_drift_sd": round(max((abs(v) for v in drift.values()), default=0.0), 2)}


# ---------------------------------------------------------------- banco de casos

def build_cases(index):
    """Gera os casos. Eles NAO sao um retrato do que a implementacao devolve
    hoje - cada familia existe para prender uma propriedade que pode quebrar:

      identidade  - alimentado com as PROPRIAS medidas de um avatar, o resultado
                    tem que ser ele mesmo. Pega erro de escala, de divisor e de
                    mapeamento de campo de uma vez so.
      altura      - o MESMO corpo declarado em 1,60 m e em 1,95 m tem que cair no
                    mesmo avatar, porque a escala normaliza os dois. Se alguem
                    remover a escala, so este caso acusa.
      parcial     - so 3 ou 4 campos preenchidos: o caso do usuario real, que nao
                    mede antebraco.
      marcada     - avatar cuja coluna esta em `unreliable_columns`: alimentar o
                    numero ruim NAO pode mudar o resultado, porque ele tem peso 0.
      fallback    - sem circunferencia nenhuma, ou menos que `min_columns`.
      sexo        - o mesmo vetor nos dois sexos tem que sair de colecoes
                    diferentes. Vazamento entre colecoes some numa revisao de
                    olho e aparece aqui.
    """
    sel = index["selection"]
    inv = {v: k for k, v in sel["app_field_map"].items()}
    ref_h = index["reference_height_m"]
    cases = []

    def measures_of(a, cols=None, height_m=ref_h):
        """Medidas do avatar em CENTIMETROS DE USUARIO - o inverso da escala que
        o `select` aplica. Passar cm de 1,75 m dizendo que a pessoa tem 1,95 m
        seria um corpo diferente, e o caso testaria outra coisa."""
        k = height_m / ref_h
        out = {}
        for col in (cols or sel["columns"]):
            v = (a.get("circumferences_cm") or {}).get(col)
            if v is not None:
                out[inv[col]] = round(v * k, 1)
        return out

    by_sex = {}
    for a in index["avatars"]:
        by_sex.setdefault(a["sex"], []).append(a)

    for sex, pool in sorted(by_sex.items()):
        user_range = [a for a in pool if 17.0 <= a["measured_bmi"] <= 40.0]
        user_range.sort(key=lambda a: a["measured_bmi"])
        if not user_range:
            continue
        # Extremos e meio da faixa de usuario, mais um com muita coluna marcada.
        picks = [user_range[0], user_range[len(user_range) // 2], user_range[-1]]
        dirty = max(user_range, key=lambda a: len(a.get("unreliable_columns") or []))
        if dirty["id"] not in [p["id"] for p in picks]:
            picks.append(dirty)

        for a in picks:
            w = round(a["measured_bmi"] * ref_h * ref_h, 1)
            cases.append({
                "name": "identidade/{}".format(a["id"]),
                "why": "as proprias medidas do avatar tem que devolver ele mesmo",
                "input": {"sex": sex, "height_cm": ref_h * 100, "weight_kg": w,
                          "measures": measures_of(a)},
                "expect_id": a["id"],
            })

        tall = picks[1]
        for h in (1.60, 1.95):
            cases.append({
                "name": "altura/{}/{:.2f}m".format(tall["id"], h),
                "why": "o mesmo corpo em outra estatura cai no mesmo avatar",
                "input": {"sex": sex, "height_cm": round(h * 100, 1),
                          "weight_kg": round(tall["measured_bmi"] * h * h, 1),
                          "measures": measures_of(tall, height_m=h)},
                "expect_id": tall["id"],
            })

        parcial = picks[1]
        cases.append({
            "name": "parcial/{}".format(parcial["id"]),
            "why": "usuario que so mediu cintura, quadril e ombro",
            "input": {"sex": sex, "height_cm": ref_h * 100,
                      "weight_kg": round(parcial["measured_bmi"] * ref_h * ref_h, 1),
                      "measures": measures_of(parcial, ["waist_min", "hip", "shoulder"])},
            "expect_id": None,      # preenchido pelo run: nao ha resposta obvia a priori
        })

        marcado = dirty if dirty.get("unreliable_columns") else None
        if marcado:
            col = marcado["unreliable_columns"][0]
            base = measures_of(marcado)
            poisoned = dict(base)
            poisoned[inv[col]] = round(base[inv[col]] * 1.5, 1)   # numero absurdo
            cases.append({
                "name": "marcada/{}/{}".format(marcado["id"], col),
                "why": ("a coluna '{}' esta em unreliable_columns deste avatar, "
                        "entao envenena-la nao pode mudar a escolha".format(col)),
                "input": {"sex": sex, "height_cm": ref_h * 100,
                          "weight_kg": round(marcado["measured_bmi"] * ref_h * ref_h, 1),
                          "measures": poisoned},
                "expect_id": marcado["id"],
            })

        # UMA MEDIDA ERRADA NAO PODE TROCAR O CORPO. Caso real de 04/08: o
        # usuario digitou 28 cm de panturrilha em vez de 36, e como a distancia
        # soma QUADRADOS aquela coluna respondeu por 46% da decisao — o avatar
        # escolhido veio com 16 cm de erro de CINTURA. O teto (z_cap) conserta;
        # este caso existe para o conserto nao ser desfeito sem alguem notar.
        vitima = picks[1]
        envenenado = measures_of(vitima)
        pior = min(sel["columns"], key=lambda c: (vitima.get("circumferences_cm") or {}).get(c, 1e9))
        campo_pior = inv[pior]
        envenenado[campo_pior] = round(envenenado[campo_pior] * 0.6, 1)   # fita no lugar errado
        cases.append({
            "name": "outlier/{}/{}".format(vitima["id"], pior),
            "why": ("uma coluna medida errada nao pode mudar o avatar escolhido; "
                    "sem o teto por coluna ela decidia sozinha"),
            "input": {"sex": sex, "height_cm": ref_h * 100,
                      "weight_kg": round(vitima["measured_bmi"] * ref_h * ref_h, 1),
                      "measures": envenenado},
            "expect_id": vitima["id"],
        })

        cases.append({
            "name": "fallback/sem-medida/{}".format(sex),
            "why": "so peso e altura: cai no IMC, na linha d2",
            "input": {"sex": sex, "height_cm": 175.0, "weight_kg": 72.0, "measures": {}},
            "expect_id": None,
        })
        cases.append({
            "name": "fallback/poucas-colunas/{}".format(sex),
            "why": "duas colunas so, abaixo de min_columns: tem que cair no IMC",
            "input": {"sex": sex, "height_cm": 175.0, "weight_kg": 72.0,
                      "measures": measures_of(picks[1], ["waist_min", "hip"])},
            "expect_id": None,
        })

    return cases


def build_goal_cases(index):
    """Casos da tela de objetivo. Duas familias:

      sem-corpo-alvo - 'maintain', 'improve_health' e 'performance' tem que
                       devolver NADA. E o caso que impede a tela de inventar uma
                       meta para quem nao pediu meta.
      direcao        - nos tres que tem alvo, a meta nao pode ser o avatar atual
                       e nao pode andar para o lado contrario. Sao as duas travas
                       que so a biblioteca garante, e as duas quebram calado.
    """
    cases = []
    goals = (index.get("goal") or {}).get("vectors", {})
    by_sex = {}
    for a in index["avatars"]:
        by_sex.setdefault(a["sex"], []).append(a)

    for sex, pool in sorted(by_sex.items()):
        user_range = sorted([a for a in pool if 17.0 <= a["measured_bmi"] <= 40.0],
                            key=lambda a: a["measured_bmi"])
        if not user_range:
            continue
        current = user_range[len(user_range) // 2]
        for goal, cfg in goals.items():
            cases.append({
                "name": "objetivo/{}/{}".format(current["id"], goal),
                "why": ("meta tem que existir e andar na direcao" if cfg["has_target_body"]
                        else "objetivo sem corpo-alvo: a tela mostra UM avatar"),
                "input": {"sex": sex, "current_id": current["id"], "goal": goal},
                "expect_id": None,
                "expect_has_target": cfg["has_target_body"],
            })
    return cases


def main():
    ap = argparse.ArgumentParser(description="Regra de selecao e banco de casos.")
    ap.add_argument("--cases", action="store_true", help="regera test/selection_cases.json")
    ap.add_argument("--check", action="store_true", help="confere contra o banco")
    ap.add_argument("--demo", nargs=2, metavar=("ALTURA_M", "PESO_KG"))
    ap.add_argument("--sex", default="m", choices=["m", "f"])
    for f in ("neck", "shoulder", "chest", "waist", "hip", "arm", "forearm", "thigh", "calf"):
        ap.add_argument("--" + f, type=float, default=None)
    args = ap.parse_args()

    index = load_index()

    if args.cases:
        cases = build_cases(index)
        for c in cases:
            got = select(index, c["input"]["sex"], c["input"]["height_cm"] / 100.0,
                         c["input"]["weight_kg"], c["input"]["measures"])
            if c["expect_id"] is None:
                c["expect_id"] = got["id"]
            c["expect_rule"] = got["rule"]
            c["expect_columns_used"] = got["columns_used"]
            c["expect_distance"] = got["distance"]

        goal_cases = build_goal_cases(index)
        for c in goal_cases:
            i = c["input"]
            got = select_goal(index, i["sex"], i["current_id"], i["goal"])
            c["expect_id"] = got["id"] if got else None
            c["expect_distance"] = got["distance"] if got else None
            if got and got["id"] == i["current_id"]:
                sys.exit("TRAVA: a meta de {} saiu igual ao atual".format(c["name"]))
            if bool(got) != c["expect_has_target"]:
                sys.exit("TRAVA: {} devolveu {} e o vetor diz has_target_body={}"
                         .format(c["name"], got, c["expect_has_target"]))

        payload = {
            "generated_from": {
                "schema_version": index["schema_version"],
                "generated_at": index["generated_at"],
                "avatars": len(index["avatars"]),
            },
            "tolerance": {
                "distance": 0.001,
                "note": ("id e rule tem que bater EXATO; a distancia tolera erro "
                         "de ponto flutuante entre linguagens. Divergencia de id "
                         "com distancia igual e empate mal desempatado - conferir "
                         "o criterio de desempate antes de mexer na regra."),
            },
            "cases": cases,
            "goal_cases": goal_cases,
        }
        os.makedirs(os.path.dirname(CASES_PATH), exist_ok=True)
        with open(CASES_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print("{} casos de selecao + {} de objetivo -> {}".format(
            len(cases), len(goal_cases), CASES_PATH))
        for c in cases:
            print("  {:44s} -> {:16s} [{}]".format(
                c["name"], c["expect_id"], c["expect_rule"]))
        for c in goal_cases:
            print("  {:44s} -> {}".format(
                c["name"], c["expect_id"] or "(sem corpo-alvo)"))
        return

    if args.check:
        if not os.path.isfile(CASES_PATH):
            sys.exit("test/selection_cases.json nao existe. Rode: python scripts/select.py --cases")
        with open(CASES_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        bad = 0
        for c in payload["cases"]:
            i = c["input"]
            got = select(index, i["sex"], i["height_cm"] / 100.0, i["weight_kg"], i["measures"])
            if got["id"] != c["expect_id"] or got["rule"] != c["expect_rule"]:
                bad += 1
                print("FALHOU {}: esperado {} [{}], veio {} [{}]".format(
                    c["name"], c["expect_id"], c["expect_rule"], got["id"], got["rule"]))
        for c in payload.get("goal_cases", []):
            i = c["input"]
            got = select_goal(index, i["sex"], i["current_id"], i["goal"])
            gid = got["id"] if got else None
            if gid != c["expect_id"]:
                bad += 1
                print("FALHOU {}: esperado {}, veio {}".format(
                    c["name"], c["expect_id"], gid))
            elif gid == i["current_id"]:
                bad += 1
                print("FALHOU {}: meta igual ao atual".format(c["name"]))
        total = len(payload["cases"]) + len(payload.get("goal_cases", []))
        print("{}/{} casos passaram".format(total - bad, total))
        sys.exit(1 if bad else 0)

    if args.demo:
        h, w = float(args.demo[0]), float(args.demo[1])
        measures = {}
        for f, app in (("neck", "neck_cm"), ("shoulder", "shoulder_cm"), ("chest", "chest_cm"),
                       ("waist", "waist_cm"), ("hip", "hip_cm"), ("arm", "arm_cm"),
                       ("forearm", "forearm_cm"), ("thigh", "thigh_cm"), ("calf", "calf_cm")):
            v = getattr(args, f)
            if v is not None:
                measures[app] = v
        r = select(index, args.sex, h, w, measures)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
