"""Propoe a virilha dos suspeitos pela MALHA, e so entao confere com a folha.

A ordem importa e e o ponto do arquivo. O valor proposto sai do anel do tronco -
uma medida de malha, independente da folha - com o vies calibrado nos 23
avatares em que a virilha do w_limbs ja e confiavel. A folha entra DEPOIS, como
conferencia. Se o numero viesse dela, o faixa_ref estaria conferindo o short
contra o proprio valor que o gerou, e os 11 avatares mais problematicos ficariam
sem regua nenhuma (LICOES 1.3).

Regra proposta: virilha = pico mais FORTE do anel do tronco entre 0.33 e 0.55,
mais o vies. Nao e o mais baixo - o mais baixo pega vinco de coxa (b07_d3 em
0.348, b10_d3 em 0.335) e ja tinha estragado a primeira tentativa desta sonda.
"""
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
bmi = {x["id"]: x.get("measured_bmi", 0)
       for x in json.load(open(os.path.join(ROOT, "library.json"),
                               encoding="utf-8"))["avatars"]}


def pico_forte(ring, lo=0.33, hi=0.55, floor=0.015):
    best = None
    for b in range(int(lo * Z_BINS), int(hi * Z_BINS)):
        if ring[b] >= ring[b - 1] and ring[b] >= ring[b + 1] and ring[b] > floor:
            if best is None or ring[b] > best[0]:
                best = (float(ring[b]), b)
    return None if best is None else (best[1] + 0.5) / Z_BINS


dados = {a[:-4]: np.load(os.path.join(BANCO, a))
         for a in sorted(os.listdir(BANCO)) if a.endswith(".npz")}
ids = sorted(dados, key=lambda k: bmi.get(k, 0))

bons, susp = [], []
for aid in ids:
    d = dados[aid]
    cz = float(d["crotch_zh"])
    e, f = smap.get(aid, {}), folha.get(aid, {}).get("short")
    if not f:
        continue
    cos3d = float(np.max(np.atleast_1d(e["waist_zh"])))
    hem3d = float(np.min(np.atleast_1d(e["hem_l_zh"])))
    p = pico_forte(d["tronco_livre"])
    (bons if abs(cos3d - f[0]) < 0.03 and abs(hem3d - f[1]) < 0.03
     else susp).append((aid, cz, p, f))

vies = np.array([cz - p for _a, cz, p, _f in bons if p is not None])
B = float(vies.mean())
print("VIES nos %d confiaveis: virilha - pico = %+.4f  (desvio %.4f, |max| %.4f)"
      % (len(vies), B, vies.std(), np.abs(vies).max()))

# O RECUO virilha->bainha e MEDIDO, nao herdado do chute. A primeira versao
# desta sonda usou 0.035, que e a constante de fallback do w_fit, e com ela a
# proposta saiu -0.027 abaixo da folha em bloco - vies que era da constante, nao
# dos avatares. Nos confiaveis a distancia real e outra, e e ela que diz o que a
# folha esta afirmando sobre a virilha.
rec = np.array([cz - f[1] for _a, cz, _p, f in bons])
R = float(np.median(rec))
print("RECUO nos %d confiaveis: virilha - bainha_folha = %.4f  (desvio %.4f)"
      % (len(rec), R, rec.std()))
print("   janela HEM_BELOW_CROTCH de hoje = (0.015, 0.065)")

print("\n%-15s %5s %8s %8s %8s   %8s %7s" % (
    "id", "imc", "hoje", "pico", "PROPOSTA", "folha", "confere"))
prop = {}
for aid, cz, p, f in susp:
    alvo = f[1] + R              # o que a folha diz da virilha, via recuo
    if p is None:
        print("%-15s %5.1f %8.4f %8s %8s   %8.4f %7s"
              % (aid, bmi.get(aid, 0), cz, "-", "-", alvo, "sem pico"))
        continue
    v = p + B
    prop[aid] = round(v, 4)
    print("%-15s %5.1f %8.4f %8.4f %8.4f   %8.4f %+7.4f"
          % (aid, bmi.get(aid, 0), cz, p, v, alvo, v - alvo))

d = np.array([prop[a] - (f[1] + R) for a, _c, p, f in susp if p is not None])
print("\nconferencia contra a folha: media %+.4f  rms %.4f  |max| %.4f"
      % (d.mean(), np.sqrt((d ** 2).mean()), np.abs(d).max()))
print(json.dumps(prop, indent=1))
