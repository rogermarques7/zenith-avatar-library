# -*- coding: utf-8 -*-
"""COBERTURA medida pela REGRA DO APP, nao por contagem de celula.

    python qa/probe/sondas/cobertura_sim.py [--sexo f|m] [--imc 17,40]

Um corpo so "falta" se um usuario com ele sai mal DEPOIS da selecao e do
morph. Contar celula de IMC/forma (COBERTURA_FORMAS.md) diz onde nao ha corpo;
nao diz se o vizinho + morph ja resolve. Aqui a pergunta e respondida com o
`select.py` e o `morph_cases.solve` de verdade:

1. LEAVE-ONE-OUT - tira cada avatar, trata as 9 medidas dele como um usuario,
   deixa a regra escolher entre os que sobraram e aplica o morph dentro da
   faixa publicada. O erro que sobra diz quao ISOLADO aquele corpo esta: se
   ele nao existisse, quem tem aquele corpo receberia isto.
2. ENTRE VIZINHOS - para cada par de avatares vizinhos (cada um entre os 6
   mais proximos do outro), usuarios em 25/50/75% do caminho. O erro que sobra
   depois do morph aponta BURACO dentro do envelope que a biblioteca ja cobre.

"Erro que sobra" = a distancia da propria selecao (mesmos pesos, mesmas
escalas), recalculada sobre o residuo pos-morph; e o maior residuo em cm nas 4
colunas do tronco. Tudo na estatura de referencia (1,75 m).
"""
import itertools
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import select as _sel  # noqa: E402  (o scripts/select.py, nao o modulo da stdlib)
import morph_cases as mc  # noqa: E402

if not hasattr(_sel, "load_index"):
    import importlib.util
    spec = importlib.util.spec_from_file_location("zsel", os.path.join(ROOT, "scripts", "select.py"))
    _sel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_sel)

a = sys.argv[1:]
SEXOS = [a[a.index("--sexo") + 1]] if "--sexo" in a else ["f", "m"]
IMC = [float(x) for x in (a[a.index("--imc") + 1] if "--imc" in a else "17,40").split(",")]

idx = _sel.load_index()
mapa = json.load(open(os.path.join(ROOT, "config", "morph_map.json"), encoding="utf-8"))
SEL = idx["selection"]
COLS = SEL["columns"]
TRONCO = ["waist_navel", "hip", "chest", "shoulder"]
INV = {v: k for k, v in SEL["app_field_map"].items()}


def cm_da_influence(curve, inf):
    """inverso do interp_influence: quantos cm a curva publicada entrega."""
    pts = sorted(curve)
    if inf <= pts[0][0]:
        return pts[0][1]
    for (i0, c0), (i1, c1) in zip(pts, pts[1:]):
        if inf <= i1:
            t = 0 if i1 == i0 else (inf - i0) / (i1 - i0)
            return c0 + t * (c1 - c0)
    return pts[-1][1]


def forma(c):
    return c["waist_navel"] / c["hip"], c["shoulder"] / c["hip"]


def atende(user_c, user_bmi, sexo, excluir=()):
    """(avatar escolhido, distancia antes, distancia depois do morph, pior cm tronco, residuos)"""
    sub = dict(idx)
    sub["avatars"] = [x for x in idx["avatars"] if x["id"] not in excluir]
    medidas = {INV[c]: v for c, v in user_c.items() if c in INV and v}
    peso = user_bmi * 1.75 ** 2
    r = _sel.select(sub, sexo, 1.75, peso, medidas)
    av = next(x for x in idx["avatars"] if x["id"] == r["id"])
    ent = mapa.get(av["id"])
    infl = mc.solve(ent, 1.75, user_c, r["columns_used"]) if ent else {}
    scales = SEL["scale_cm"][sexo]
    num = den = 0.0
    res = {}
    for col in r["columns_used"]:
        base = av["circumferences_cm"][col]
        ganho = 0.0
        for m in (ent or {}).get("morphs", []):
            if m.get("column") == col:
                ganho = cm_da_influence(m["curve"], infl.get(m["key"], 0.0))
        res[col] = user_c[col] - (base + ganho)
        z = res[col] / scales[col]
        w = SEL["weights"].get(col, 1.0)
        num += w * z * z
        den += w
    pior = max((abs(res[c]), c) for c in TRONCO if c in res) if res else (0, "-")
    return av, r["distance"], (num / den) ** 0.5 if den else None, pior, res


for sexo in SEXOS:
    pool = [x for x in idx["avatars"] if x["sex"] == sexo and x.get("approved")]
    faixa = [x for x in pool if IMC[0] <= x["measured_bmi"] <= IMC[1]]
    print("\n" + "=" * 100)
    print("SEXO {} - {} avatares, {} na faixa de usuario IMC {:.0f}-{:.0f}".format(
        sexo, len(pool), len(faixa), *IMC))

    # ---------------------------------------------------------- 1. LOO
    print("\n1) LEAVE-ONE-OUT - se este corpo nao existisse (so a faixa de usuario):")
    print("   {:16s} {:>5} {:>6} {:>6} | {:16s} {:>6} {:>6} {:>12}".format(
        "corpo", "IMC", "WHR", "SHR", "cairia em", "d.sel", "d.pos", "pior tronco"))
    loo = []
    for x in faixa:
        c = {k: v for k, v in x["circumferences_cm"].items() if k in COLS and v}
        av, d0, d1, pior, _ = atende(c, x["measured_bmi"], sexo, excluir={x["id"]})
        loo.append((d1, x, av, d0, pior))
    loo.sort(key=lambda t: -t[0])
    for d1, x, av, d0, pior in loo[:15]:
        w, s = forma(x["circumferences_cm"])
        print("   {:16s} {:5.1f} {:6.3f} {:6.3f} | {:16s} {:6.3f} {:6.3f} {:>5.1f} cm {}".format(
            x["id"], x["measured_bmi"], w, s, av["id"], d0, d1, pior[0], pior[1]))
    ds = sorted(t[0] for t in loo)
    print("   mediana d.pos {:.3f} | p90 {:.3f} | acima de 0,45: {} de {}".format(
        ds[len(ds) // 2], ds[int(len(ds) * 0.9)], sum(1 for d in ds if d > 0.45), len(ds)))

    # ---------------------------------------------------------- 2. entre vizinhos
    def dvec(p, q):
        sc = SEL["scale_cm"][sexo]
        n = d = 0.0
        for col in COLS:
            u, v = p["circumferences_cm"].get(col), q["circumferences_cm"].get(col)
            if u and v:
                w = SEL["weights"].get(col, 1.0)
                n += w * ((u - v) / sc[col]) ** 2
                d += w
        return (n / d) ** 0.5

    viz = {}
    for x in faixa:
        ds_ = sorted((dvec(x, y), y["id"]) for y in faixa if y is not x)
        viz[x["id"]] = {i for _, i in ds_[:6]}
    pares = [(p, q) for p, q in itertools.combinations(faixa, 2)
             if q["id"] in viz[p["id"]] and p["id"] in viz[q["id"]]]
    pontos = []
    for p, q in pares:
        for t in (0.25, 0.5, 0.75):
            c = {}
            for col in COLS:
                u, v = p["circumferences_cm"].get(col), q["circumferences_cm"].get(col)
                if u and v:
                    c[col] = u + t * (v - u)
            bmi = p["measured_bmi"] + t * (q["measured_bmi"] - p["measured_bmi"])
            av, d0, d1, pior, res = atende(c, bmi, sexo)
            pontos.append((d1, pior, p, q, t, c, bmi, av))
    pontos.sort(key=lambda t: -t[0])
    d_all = sorted(t[0] for t in pontos)
    print("\n2) ENTRE VIZINHOS - {} pares, {} usuarios sinteticos".format(len(pares), len(pontos)))
    print("   d.pos mediana {:.3f} | p90 {:.3f} | p99 {:.3f} | acima de 0,45: {} ({:.1f}%)".format(
        d_all[len(d_all) // 2], d_all[int(len(d_all) * 0.9)], d_all[int(len(d_all) * 0.99)],
        sum(1 for d in d_all if d > 0.45), 100 * sum(1 for d in d_all if d > 0.45) / len(d_all)))
    print("   os PIORES (buraco dentro do envelope):")
    vistos = set()
    for d1, pior, p, q, t, c, bmi, av in pontos:
        chave = tuple(sorted((p["id"], q["id"])))
        if chave in vistos:
            continue
        vistos.add(chave)
        w, s = forma(c)
        print("   d.pos {:.3f} | IMC {:4.1f} WHR {:.3f} SHR {:.3f} | entre {} e {} ({:.0f}%) -> cai em {} | "
              "pior {:.1f} cm {}".format(d1, bmi, w, s, p["id"], q["id"], t * 100, av["id"],
                                        pior[0], pior[1]))
        if len(vistos) >= 12:
            break
