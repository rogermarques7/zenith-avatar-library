"""Procura na MALHA um sinal de virilha que sobreviva ao corpo obeso.

Motivo de nao resolver isto com override copiado da folha: a folha e a regua
EXTERNA do short. Se ela passar a fornecer o numero que ancora o detector, ela
deixa de ser regua - o faixa_ref confirmaria o short contra o proprio valor que
o gerou, e sobraria zero verificacao justo nos 11 avatares mais problematicos.
Override manual continua valendo como conserto pontual; como conserto de um
terco da colecao, nao.

O que se procura: um pico de anel do tronco que seja a virilha em TODOS os
corpos. Imprime os candidatos ordenados por altura, com forca, para que a regra
saia do dado e nao de um chute sobre ele.

Referencia de verdade nos leves: nos 23 avatares em que cos e bainha ja batem
com a folha, a virilha do w_limbs e confiavel, porque as duas janelas pendem
dela. Nos pesados a referencia e folha_bainha + 0.035 (o recuo calibrado)."""
import json
import os
import sys

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


def picos(ring, lo_b, hi_b, floor=0.0):
    out = []
    for b in range(max(int(lo_b), 1), min(int(hi_b), Z_BINS - 1)):
        if ring[b] >= ring[b - 1] and ring[b] >= ring[b + 1] and ring[b] > floor:
            out.append((float(ring[b]), b))
    return out


dados = {a[:-4]: np.load(os.path.join(BANCO, a))
         for a in sorted(os.listdir(BANCO)) if a.endswith(".npz")}
ids = sorted(dados, key=lambda k: bmi.get(k, 0))

print("%-15s %5s %7s %7s  %s" % ("id", "imc", "wlimbs", "alvo", "picos 0.33-0.55"))
for aid in ids:
    d = dados[aid]
    cz = float(d["crotch_zh"])
    e = smap.get(aid, {})
    f = folha.get(aid, {}).get("short")
    cos3d = float(np.max(np.atleast_1d(e["waist_zh"])))
    hem3d = float(np.min(np.atleast_1d(e["hem_l_zh"])))
    bom = f and abs(cos3d - f[0]) < 0.03 and abs(hem3d - f[1]) < 0.03
    alvo = cz if bom else (f[1] + 0.035 if f else float("nan"))
    pk = picos(d["tronco_livre"], 0.33 * Z_BINS, 0.55 * Z_BINS, floor=0.015)
    pk.sort(key=lambda sb: sb[1])
    s = "  ".join("%.3f@%.3f" % (v, (b + 0.5) / Z_BINS) for v, b in pk[:6])
    print("%-15s %5.1f %7.4f %7.4f%s  %s" % (aid, bmi.get(aid, 0), cz, alvo,
                                             " " if bom else "*", s))
print("\n* = virilha suspeita; alvo = folha_bainha + 0.035")
