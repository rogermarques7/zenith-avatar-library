"""Varre a janela e o recuo da BAINHA sobre o banco, contra a folha.

Mesma correcao de metodo do _varre_janela.py: o erro e medido nos avatares
TODOS, e quem nao acha anel entra com o chute, porque o chute e o que sai. Aqui
isso pesa ainda mais - metade das femininas sai com BAINHA-CHUTE, entao uma
varredura que so olhasse quem achou anel estaria avaliando a minoria.

So entram os avatares de virilha confiavel. A janela da bainha e ancorada na
virilha, entao medir com a virilha errada mede a virilha, nao a janela."""
import json
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
Z_BINS = 240
BANCO = os.path.join(ROOT, "qa", "probe", "anel")
folha = json.load(open(os.path.join(ROOT, "qa", "probe", "faixa", "_folha.json"),
                       encoding="utf-8"))
smap = json.load(open(os.path.join(ROOT, "config", "shorts_map.json"),
                      encoding="utf-8"))

dados = {a[:-4]: np.load(os.path.join(BANCO, a))
         for a in sorted(os.listdir(BANCO)) if a.endswith(".npz")}


def picos(ring, lo_b, hi_b):
    out = []
    for b in range(max(int(lo_b), 1), min(int(hi_b), Z_BINS - 1)):
        if ring[b] >= ring[b - 1] and ring[b] >= ring[b + 1] and ring[b] > 0:
            out.append((float(ring[b]), b))
    out.sort(reverse=True)
    return out


bons = []
for aid, d in dados.items():
    e, f = smap.get(aid, {}), folha.get(aid, {}).get("short")
    if not f:
        continue
    cos3d = float(np.max(np.atleast_1d(e["waist_zh"])))
    hem3d = float(np.min(np.atleast_1d(e["hem_l_zh"])))
    if abs(cos3d - f[0]) < 0.03 and abs(hem3d - f[1]) < 0.03:
        bons.append((aid, float(d["crotch_zh"]), f))
print("%d avatares de virilha confiavel\n" % len(bons))

print("%-22s %6s %8s %8s %7s  %s" % ("janela / recuo", "chute", "rms", "|max|",
                                     ">0.02", "pior"))
for lo, hi in [(0.015, 0.065), (0.005, 0.045), (0.005, 0.035), (0.010, 0.035),
               (0.005, 0.030), (0.010, 0.030)]:
    for rec in (0.035, 0.019):
        ds, chute, quem = [], 0, []
        for aid, cz, f in bons:
            d = dados[aid]
            cb = cz * Z_BINS
            v = None
            for perna in ("perna0", "perna1"):
                pk = picos(d[perna], cb - hi * Z_BINS, cb - lo * Z_BINS)
                if pk:
                    h = (pk[0][1] + 0.5) / Z_BINS
                    v = h if v is None else min(v, h)
            if v is None:
                v, chute = cz - rec, chute + 1
            ds.append(v - f[1])
            quem.append(aid)
        ds = np.array(ds)
        i = int(np.argmax(np.abs(ds)))
        print("%-22s %6d %8.4f %8.4f %7d  %s %+.3f" % (
            "%.3f..%.3f  r=%.3f" % (lo, hi, rec), chute,
            float(np.sqrt((ds ** 2).mean())), float(np.abs(ds).max()),
            int((np.abs(ds) > 0.02).sum()), quem[i], ds[i]))
