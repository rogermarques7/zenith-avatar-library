"""Deriva do library.json quais slots da grade feminina ainda faltam.

Existe porque contar a grade a mao ja errou duas vezes (state.md, §5.4): a d3
comeca em b02 e termina em b10, entao um range b01..b09 inventa um slot que nao
existe e esconde o b10. A fonte das faixas e o docs/blocos/prompt_f.md.
"""
import collections
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GRADE = {
    "d1": [f"b{i:02d}" for i in range(1, 13)],   # b01..b12
    "d2": [f"b{i:02d}" for i in range(1, 12)],   # b01..b11
    "d3": [f"b{i:02d}" for i in range(2, 11)],   # b02..b10
}

with open(os.path.join(ROOT, "library.json"), encoding="utf-8") as fh:
    lib = json.load(fh)

ocupados = collections.defaultdict(set)
insercoes = collections.defaultdict(list)

for av in lib["avatars"]:
    if av["sex"] != "f":
        continue
    m = re.match(r"zen_f_(b\d+)([a-z]?)_(d\d)", av["id"])
    banda, letra, definicao = m.group(1), m.group(2), m.group(3)
    if letra:
        insercoes[definicao].append(av["id"])
    else:
        ocupados[definicao].add(banda)

total = 0
for definicao in ("d1", "d2", "d3"):
    faltam = [b for b in GRADE[definicao] if b not in ocupados[definicao]]
    total += len(faltam)
    print(
        f"f {definicao}: grade {len(GRADE[definicao]):2d}"
        f"  ocupados {len(ocupados[definicao]):2d}"
        f"  insercoes {len(insercoes[definicao])}"
        f"  FALTAM {len(faltam)}  {faltam}"
    )

f = sum(1 for a in lib["avatars"] if a["sex"] == "f")
m = sum(1 for a in lib["avatars"] if a["sex"] == "m")
print(f"\nslots femininos faltando: {total}")
print(f"avatares: {f + m}  ({m} masculinos, {f} femininos)")
