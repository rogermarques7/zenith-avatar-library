"""Varre o filtro de braco sobre o banco dos 76, offline.

O CRITERIO NAO E "melhorou". A mascara de braco nao tem regua externa: nao ha
folha que diga quais vertices sao braco, e a unica conferencia real e o olho no
render. Entao a varredura nao tenta pontuar - ela DIFERENCIA. Para cada limiar
candidato, quais avatares mudam de mascara em relacao ao filtro de hoje?

Isso e o que serve para decidir, porque 39 masculinos e 36 femininos ja saem
certos com o filtro atual: a mudanca boa e a que muda o zen_f_b12_d1 e mais
ninguem. Um limiar que "acha mais bracos" em avatares que ja estavam bons nao e
melhoria nenhuma - e risco em cima de coisa aprovada, que e como os 39 shorts
foram apagados em 31/07.

O teste independente e o LATERAL. Braco fica na lateral do corpo; blob de mao
na coxa, pescoco e cabelo ficam no meio. Se ao afrouxar o `ext` entrar algum
evento central, o afrouxamento pegou lixo - e isso da para ver sem render.
"""
import json
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
D = json.load(open(os.path.join(ROOT, "qa", "probe", "eventos", "_eventos.json"),
                   encoding="utf-8"))

HOJE = (0.20, 0.85, 0.15)


def aceita(ev, base_min, teto, ext_min):
    """Os indices dos eventos que o filtro aceita como braco (max 2)."""
    out = []
    for i, e in enumerate(ev[1:], start=1):      # events[1:], como no w_limbs
        if (e["base_zh"] > base_min and e["funde_zh"] < teto
                and e["ext_zh"] >= ext_min):
            out.append(i)
            if len(out) == 2:
                break
    return out


print("=== como esta hoje %s ===" % (HOJE,))
n0 = {0: [], 1: [], 2: []}
for aid in sorted(D):
    n0[len(aceita(D[aid]["eventos"], *HOJE))].append(aid)
for k in (0, 1, 2):
    print("  %d bracos: %2d avatares%s" % (
        k, len(n0[k]), ("  " + " ".join(n0[k])) if k < 2 else ""))

print("\n=== a MARGEM de cada avatar no teste que reprovou o b12_d1 ===")
print("dos eventos NAO aceitos hoje, o maior ext_zh de cada avatar\n")
print("%-16s %8s %8s %8s %7s   %s" % ("id", "ext_zh", "base_zh", "lat_zh", "n",
                                      "aceitos hoje"))
quase = []
for aid in sorted(D):
    ev = D[aid]["eventos"]
    ok = set(aceita(ev, *HOJE))
    cand = [(e["ext_zh"], i, e) for i, e in enumerate(ev[1:], start=1)
            if i not in ok and e["base_zh"] > HOJE[0] and e["funde_zh"] < HOJE[1]]
    if not cand:
        continue
    cand.sort(reverse=True)
    x, i, e = cand[0]
    quase.append((x, aid))
    if x > 0.05:
        print("%-16s %8.4f %8.4f %8.4f %7d   %s" % (
            aid, x, e["base_zh"], e["lat_zh"], e["n"], sorted(ok)))
quase.sort(reverse=True)
print("\nmaiores reprovados por ext, em ordem:")
for x, aid in quase[:8]:
    print("   %-16s %.4f" % (aid, x))

print("\n=== quem MUDA de mascara a cada limiar de ext ===")
for ext in (0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.08):
    mud = []
    for aid in sorted(D):
        ev = D[aid]["eventos"]
        a, b = aceita(ev, *HOJE), aceita(ev, HOJE[0], HOJE[1], ext)
        if a != b:
            lat = [round(ev[i]["lat_zh"], 3) for i in b if i not in a]
            mud.append("%s %s->%s lat%s" % (aid, len(a), len(b), lat))
    print("  ext>=%.2f  %d mudam   %s" % (ext, len(mud), "  |  ".join(mud)))

print("\n=== lateral: aceitos hoje contra o resto ===")
la, lo = [], []
for aid in sorted(D):
    ev = D[aid]["eventos"]
    ok = set(aceita(ev, *HOJE))
    for i, e in enumerate(ev[1:], start=1):
        (la if i in ok else lo).append(e["lat_zh"])
la, lo = np.array(la), np.array(lo)
print("  aceitos (bracos): n=%d  lat mediana %.4f  min %.4f  max %.4f"
      % (len(la), np.median(la), la.min(), la.max()))
print("  recusados       : n=%d  lat mediana %.4f  min %.4f  max %.4f"
      % (len(lo), np.median(lo), lo.min(), lo.max()))
