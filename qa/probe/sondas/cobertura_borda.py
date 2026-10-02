# -*- coding: utf-8 -*-
"""A BORDA da cobertura: usuario = avatar existente com a FORMA deslocada.

    python qa/probe/sondas/cobertura_borda.py

O `cobertura_sim.py` testa usuarios ENTRE corpos (dentro do envelope). Quem cai
FORA do envelope e o usuario que tem a mesma estatura de corpo mas outra forma.
Para cada avatar na faixa de usuario, quatro variantes com ~1 desvio-padrao
populacional de forma (WHR ~0,06 e SHR ~0,05 sobre o quadril):
    cintura +7 cm (maca)   cintura -7 cm (ampulheta)
    ombro   +6 cm (V)      ombro   -6 cm (pera)
e a regra do app decide e morfa. Agrupa o erro pos-morph por faixa de IMC e
direcao - e ali que se ve em que TAMANHO falta qual FORMA.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = [sys.argv[0], "--sexo", "f"]      # so para o import nao imprimir tudo
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import cobertura_sim as cs  # noqa: E402

VAR = [("cintura+7", "waist_navel", +7), ("cintura-7", "waist_navel", -7),
       ("ombro+6", "shoulder", +6), ("ombro-6", "shoulder", -6)]
for sexo in ("f", "m"):
    pool = [x for x in cs.idx["avatars"] if x["sex"] == sexo and 17 <= x["measured_bmi"] <= 40]
    print("\n==== {} ({} corpos x 4 variantes) - media do erro pos-morph (d) e pior cm".format(sexo, len(pool)))
    print("  faixa  | " + " | ".join("{:^20s}".format(v[0]) for v in VAR))
    for lo in range(17, 41, 3):
        linha = []
        bb = [x for x in pool if lo <= x["measured_bmi"] < lo + 3]
        if not bb:
            print("  {:2d}-{:2d}  | (sem corpo)".format(lo, lo + 3))
            continue
        for nome, col, dv in VAR:
            ds, cms = [], []
            for x in bb:
                c = {k: v for k, v in x["circumferences_cm"].items() if k in cs.COLS and v}
                c[col] = c[col] + dv
                av, d0, d1, pior, res = cs.atende(c, x["measured_bmi"], sexo)
                ds.append(d1)
                cms.append(abs(res.get(col, 0.0)))
            linha.append("d {:.2f} | {:4.1f} cm{}".format(sum(ds) / len(ds), max(cms),
                                                         " !" if max(cms) > 4.5 else "  "))
        print("  {:2d}-{:2d}  | ".format(lo, lo + 3) + " | ".join("{:^20s}".format(s) for s in linha)
              + "   (n {})".format(len(bb)))
