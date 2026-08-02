"""Aspereza da borda de CIMA da faixa, nos 37, direto do mapa.

O b08_d3 saiu com uma cunha subindo pelo esterno: 22 setores em 0.723 e DOIS em
0.769. Borda de roupa e curva lisa em azimute - salto isolado de 4,6% da altura
entre setores vizinhos e erro de deteccao, nao anatomia. O prior gaussiano e a
mediana circular de 7 ja existem e nao seguraram no corpo mais musculoso da
serie, onde o sulco entre os peitorais e um vinco vertical forte.

Mede duas coisas por avatar, as duas em fracao da altura:

  salto  maior diferenca entre setores VIZINHOS (circular). E o que se ve.
  subida max(topo) - ancora do anel. Quanto o setor mais alto fugiu.

O criterio e diferencial, como no braco: nao existe regua externa para o
tracado, entao a mudanca certa e a que mexe em quem esta torto e mais ninguem.

    python qa/probe/sondas/_topo_faixa.py
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
M = json.load(open(os.path.join(ROOT, "config", "shorts_map.json"),
                   encoding="utf-8"))

linhas = []
for aid, e in M.items():
    hi = e.get("faixa_hi_zh")
    if not isinstance(hi, list):
        continue
    n = len(hi)
    salto = max(abs(hi[j] - hi[(j + 1) % n]) for j in range(n))
    anc = e.get("diag", {}).get("faixa_topo_anel_zh", min(hi))
    linhas.append((salto, max(hi) - anc, max(hi) - min(hi), anc, aid,
                   e.get("diag", {}).get("faixa_anel_topo")))

linhas.sort(reverse=True)
print("%-16s %7s %7s %7s %8s  %s" % ("id", "salto", "subida", "faixa", "ancora",
                                     "anel_topo"))
for s, sub, rng, anc, aid, anel in linhas:
    flag = "  <<<" if s > 0.020 else ""
    print("%-16s %7.4f %7.4f %7.4f %8.4f  %s%s"
          % (aid.replace("zen_f_", ""), s, sub, rng, anc, anel, flag))

ss = sorted(l[0] for l in linhas)
print("\nsalto: p50 %.4f  p90 %.4f  max %.4f  (%d avatares)"
      % (ss[len(ss) // 2], ss[int(0.9 * len(ss))], ss[-1], len(ss)))
