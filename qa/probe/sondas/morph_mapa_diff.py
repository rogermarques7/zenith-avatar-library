# -*- coding: utf-8 -*-
"""O que um lote de morph MUDOU nas faixas publicadas: mapa antigo x corrente.

    python qa/probe/sondas/morph_mapa_diff.py MAPA_ANTIGO.json [--key morph_shoulder]

Por avatar e por morph: faixa em cm (cm_min..cm_max) antes e depois, e quem
GANHOU ou PERDEU o morph. Sem --key lista so o que mudou mais que 0,3 cm.
Existe porque todo re-apply recalibra tudo (a trava do combinado mexe em
cintura/quadril quando qualquer campo muda) - e o diff de faixa e o que diz
se o lote mexeu em mais do que se pretendia.
"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
velho = json.load(open(sys.argv[1], encoding="utf-8"))
novo = json.load(open(os.path.join(ROOT, "config", "morph_map.json"), encoding="utf-8"))
so = sys.argv[sys.argv.index("--key") + 1] if "--key" in sys.argv else None


def faixas(e):
    return {m["key"]: (m["cm_min"], m["cm_max"]) for m in e["morphs"]} if e else {}


ganhou, perdeu, mudou = [], [], []
tot = {"neg": 0.0, "pos": 0.0}
for aid in sorted(novo):
    a, b = faixas(velho.get(aid)), faixas(novo.get(aid))
    if aid not in velho:
        continue
    for k in sorted(set(a) | set(b)):
        if so and k != so:
            continue
        if k not in a:
            ganhou.append((aid, k, b[k]))
        elif k not in b:
            perdeu.append((aid, k, a[k]))
        else:
            dn, dp = b[k][0] - a[k][0], b[k][1] - a[k][1]
            if so or abs(dn) > 0.3 or abs(dp) > 0.3:
                mudou.append((aid, k, a[k], b[k]))
            tot["neg"] += dn
            tot["pos"] += dp
print("GANHOU ({}):".format(len(ganhou)))
for aid, k, f in ganhou:
    print("  {:16s} {:22s} {:+.1f} a {:+.1f} cm".format(aid, k, *f))
print("PERDEU ({}):".format(len(perdeu)))
for aid, k, f in perdeu:
    print("  {:16s} {:22s} era {:+.1f} a {:+.1f} cm".format(aid, k, *f))
print("MUDOU ({}):".format(len(mudou)))
for aid, k, fa, fb in mudou:
    print("  {:16s} {:22s} {:+5.1f} a {:+5.1f}  ->  {:+5.1f} a {:+5.1f}".format(aid, k, fa[0], fa[1], fb[0], fb[1]))
print("soma das mudancas: lado negativo {:+.1f} cm | lado positivo {:+.1f} cm".format(tot["neg"], tot["pos"]))
