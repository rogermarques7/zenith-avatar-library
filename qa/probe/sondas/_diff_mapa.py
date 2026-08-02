"""Diferenca campo a campo entre duas versoes do shorts_map.json.

Refit que muda numero de GEOMETRIA quando so a pintura mudou e regressao
silenciosa: o mapa e o produto (CLAUDE.md regra 3b), e ninguem olha 76 entradas
a mao. Aqui a mudanca esperada aparece separada da inesperada.

    python qa/probe/sondas/_diff_mapa.py antes.json depois.json
"""
import json
import sys

A = json.load(open(sys.argv[1], encoding="utf-8"))
B = json.load(open(sys.argv[2], encoding="utf-8"))

# o que a mascara de pintura PODE mexer. Tudo o mais e geometria detectada e
# deveria sair identico.
PINTURA = {"frac", "islands", "por_peca", "slivers", "escondidas", "summary"}


def achata(d, pre=""):
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, dict):
            out.update(achata(v, pre + k + "."))
        else:
            out[pre + k] = v
    return out


so_a = sorted(set(A) - set(B))
so_b = sorted(set(B) - set(A))
if so_a or so_b:
    print("entradas so no antes: %s\nso no depois: %s" % (so_a, so_b))

campos = {}
for aid in sorted(set(A) & set(B)):
    fa, fb = achata(A[aid]), achata(B[aid])
    for k in sorted(set(fa) | set(fb)):
        if fa.get(k) != fb.get(k):
            campos.setdefault(k, []).append(aid)

pint = {k: v for k, v in campos.items() if k.split(".")[-1] in PINTURA}
geo = {k: v for k, v in campos.items() if k.split(".")[-1] not in PINTURA}

print("\n--- esperado (pintura) ---")
for k in sorted(pint):
    print("  %-28s %2d avatares" % (k, len(pint[k])))
print("\n--- INESPERADO (geometria) ---" if geo else "\n--- geometria: nada mudou ---")
for k in sorted(geo):
    ids = geo[k]
    print("  %-28s %2d avatares  %s" % (k, len(ids),
                                        " ".join(i.replace("zen_f_", "")
                                                 for i in ids[:8])))
