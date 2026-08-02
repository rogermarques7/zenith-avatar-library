"""Quanto a costura cresce a malha, nos 76, e contra o QUE isso deveria ser lido.

O zen_f_b11_d1 reprovou no --apply por +6.2%, com a trava em 6%. A trava existe
como PROXY de "o campo cruzou zero onde nao devia" - e essa preocupacao ja tem
regua direta, a trava de ilha, que o b11_d1 passou com duas pecas conexas e
100% na pior. Antes de mexer no numero: 6.2% e a ponta de um continuo ou um
salto?

E ha um problema de dimensao na propria trava. A costura e uma CURVA: o numero
de triangulos que ela acrescenta cresce com o COMPRIMENTO da borda da roupa.
Dividir isso pela contagem total de triangulos, que e uma grandeza de AREA,
mistura duas coisas - corpo com mais roupa e com borda mais recortada paga mais
sem estar errado. Por isso a segunda coluna: costura por unidade de `frac`.

    python qa/probe/sondas/_costura.py
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
M = json.load(open(os.path.join(ROOT, "config", "shorts_map.json"),
                   encoding="utf-8"))
ALVO = 60000.0

linhas = []
for aid, e in M.items():
    m = re.search(r"\+(\d+) costura", e.get("summary", ""))
    if not m:
        continue
    tri = 2 * int(m.group(1))          # o --fit conta metade do que o --apply
    frac = e.get("frac") or 1e-9
    linhas.append((tri / ALVO, tri / ALVO / frac, frac, aid))

linhas.sort(reverse=True)
print("%-16s %8s %10s %8s" % ("id", "cresce", "por_frac", "frac"))
for g, gf, f, aid in linhas[:12]:
    print("%-16s %7.2f%% %10.3f %8.3f%s"
          % (aid, 100 * g, gf, f, "   <<< reprovou" if g > 0.06 else ""))
print("  ...")
for g, gf, f, aid in linhas[-3:]:
    print("%-16s %7.2f%% %10.3f %8.3f" % (aid, 100 * g, gf, f))

fem = [l for l in linhas if "_f_" in l[3]]
mas = [l for l in linhas if "_m_" in l[3]]
for nome, gr in (("feminino", fem), ("masculino", mas), ("todos", linhas)):
    g = sorted(x[0] for x in gr)
    gf = sorted(x[1] for x in gr)
    print("\n%-10s n=%2d  cresce p50 %.2f%% p90 %.2f%% max %.2f%%"
          "   por_frac p50 %.3f p90 %.3f max %.3f"
          % (nome, len(gr), 100 * g[len(g) // 2], 100 * g[int(0.9 * len(g))],
             100 * g[-1], gf[len(gf) // 2], gf[int(0.9 * len(gf))], gf[-1]))
