"""Varre janela do cos e ancora de virilha sobre o banco, contra a folha.

Roda sem Blender, sobre qa/probe/anel/*.npz (ver _banco_anel.py). Duas perguntas,
nesta ordem - a segunda so faz sentido se a primeira for sim:

  1. O MENOR pico forte do anel do tronco e a virilha? Se for, existe uma medida
     de malha para corrigir a ancora dos 5 pesados, e nao e preciso copiar numero
     de folha. A validacao e nos avatares em que a virilha ja esta certa - os que
     batem com a folha nas duas bordas -, porque neles ha com o que comparar.

  2. Que teto da janela absoluta do cos reproduz a folha nas 37? O teto de hoje
     (0.60) foi calibrado nas 39 folhas MASCULINAS, e a mediana feminina e 0.587
     contra ~0.573 delas: o short feminino e de cintura alta. Onze das 37 caem em
     0.59 ou acima e duas passam do teto.

Criterio de sucesso identico ao que escolheu o teto masculino (ver
WAIST_ABS_RANGE no shorts.py): numero de avatares SEM anel, e rms do topo do cos
contra a folha. Uma janela larga nao custa so ruido - ela troca o marco
anatomico por outro -, entao rms subindo reprova a hipotese mesmo que "sem anel"
caia a zero.
"""
import hashlib
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

Z_BINS = 240
WAIST_ABOVE_CROTCH = (0.090, 0.230)
HEM_BELOW_CROTCH = (0.015, 0.065)

BANCO = os.path.join(ROOT, "qa", "probe", "anel")
folha = json.load(open(os.path.join(ROOT, "qa", "probe", "faixa", "_folha.json"),
                       encoding="utf-8"))
smap = json.load(open(os.path.join(ROOT, "config", "shorts_map.json"),
                      encoding="utf-8"))
bmi = {x["id"]: x.get("measured_bmi", 0)
       for x in json.load(open(os.path.join(ROOT, "library.json"),
                               encoding="utf-8"))["avatars"]}

dados = {}
for fn in sorted(os.listdir(BANCO)):
    if not fn.endswith(".npz"):
        continue
    aid = fn[:-4]
    d = np.load(os.path.join(BANCO, fn))
    master = os.path.join(ROOT, "02_master", aid + "_master.glb")
    with open(master, "rb") as f:
        h = hashlib.sha1(f.read()).hexdigest()[:16]
    if str(d["sha"]) != h:
        sys.exit("BANCO VELHO: %s mudou depois de gravado. Rode _banco_anel.py."
                 % aid)
    dados[aid] = d


def picos(ring, lo_b, hi_b, floor=0.0):
    out = []
    for b in range(max(int(lo_b), 1), min(int(hi_b), Z_BINS - 1)):
        if ring[b] >= ring[b - 1] and ring[b] >= ring[b + 1] and ring[b] > floor:
            out.append((float(ring[b]), b))
    out.sort(reverse=True)
    return out


ids = sorted(dados, key=lambda k: bmi.get(k, 0))

# --- 1. o menor pico forte do tronco e a virilha? ---------------------------
# Compara so onde a virilha de hoje merece credito: os avatares cujo cos E
# bainha ja batem com a folha. Se a virilha estivesse errada neles, as duas
# bordas nao teriam como cair no lugar - as duas janelas pendem dela.
print("== 1. menor pico forte do tronco  x  virilha do w_limbs")
print("%-15s %5s  %7s %7s %7s   %s" % ("id", "imc", "virilha", "pico1",
                                       "delta", "confiavel"))
erros = []
for aid in ids:
    d = dados[aid]
    cz = float(d["crotch_zh"])
    e = smap.get(aid, {})
    f = folha.get(aid, {}).get("short")
    if not f:
        continue
    cos3d = float(np.max(np.atleast_1d(e["waist_zh"])))
    hem3d = float(np.min(np.atleast_1d(e["hem_l_zh"])))
    ok = abs(cos3d - f[0]) < 0.03 and abs(hem3d - f[1]) < 0.03

    # pico mais BAIXO com forca que preste, no tronco sem recorte de virilha
    pk = picos(d["tronco_livre"], 0.30 * Z_BINS, 0.55 * Z_BINS, floor=0.02)
    p1 = min((b for _s, b in pk), default=None)
    if p1 is None:
        print("%-15s %5.1f  %7.4f      -       -   %s" % (aid, bmi.get(aid, 0), cz,
                                                          "sim" if ok else "-"))
        continue
    p1 = (p1 + 0.5) / Z_BINS
    print("%-15s %5.1f  %7.4f %7.4f %+7.4f   %s" % (
        aid, bmi.get(aid, 0), cz, p1, p1 - cz, "sim" if ok else "-"))
    if ok:
        erros.append(p1 - cz)
if erros:
    e = np.array(erros)
    print("  nos %d confiaveis: media %+.4f  desvio %.4f  |max| %.4f"
          % (len(e), e.mean(), e.std(), np.abs(e).max()))

# --- 2. teto da janela absoluta ---------------------------------------------
# O ERRO E MEDIDO NOS 37, INCLUINDO QUEM NAO ACHOU ANEL. A primeira versao desta
# varredura media o rms so sobre quem tinha pico, e com isso o teto de 0.60
# aparecia como o melhor (rms 0.0061 contra 0.0081 de 0.62) - mas ele so era
# melhor porque excluia da conta os 11 que ele mesmo fazia falhar, que sao
# justamente os dificeis. Comparacao entre populacoes diferentes nao compara
# nada. Sem anel o codigo nao desiste: cai no chute virilha+0.12, e o usuario
# recebe esse chute. Entao o chute entra no erro, que e o que de fato sai.
def simula(lo, hi, cz, ring):
    a = max(cz + WAIST_ABOVE_CROTCH[0], lo) * Z_BINS
    b = min(cz + WAIST_ABOVE_CROTCH[1], hi) * Z_BINS
    pk = picos(ring, a, b)
    if pk:
        return (pk[0][1] + 0.5) / Z_BINS, True
    return cz + 0.12, False


print("\n== 2. janela absoluta do cos  x  folha (37 femininas)")
print("   erro sobre TODOS os 37: sem anel entra com o chute virilha+0.12")
print("%-18s %8s %8s %8s %8s  %s" % ("janela", "sem anel", "rms", "|max|",
                                     ">0.02", "pior"))
for lo, hi in [(0.48, 0.60), (0.48, 0.61), (0.48, 0.62), (0.48, 0.625),
               (0.48, 0.63), (0.53, 0.625), (0.48, 0.65)]:
    ds, sem, quem = [], 0, []
    for aid in ids:
        d = dados[aid]
        f = folha.get(aid, {}).get("short")
        if not f:
            continue
        v, achou = simula(lo, hi, float(d["crotch_zh"]), d["tronco"])
        sem += 0 if achou else 1
        ds.append(v - f[0])
        quem.append(aid)
    ds = np.array(ds)
    i = int(np.argmax(np.abs(ds)))
    print("%-18s %8d %8.4f %8.4f %8d  %s %+0.3f" % (
        "%.2f .. %.3f" % (lo, hi), sem, float(np.sqrt((ds ** 2).mean())),
        float(np.abs(ds).max()), int((np.abs(ds) > 0.02).sum()),
        quem[i], ds[i]))

# --- 3. a mesma varredura COM a virilha corrigida ---------------------------
# As duas correcoes se confundem se testadas juntas, entao aqui a janela varia
# sobre uma virilha ja corrigida: assim da para ver quanto sobra para o teto
# depois que a ancora deixa de errar.
CORR = {"zen_f_b10_d1": 0.446, "zen_f_b10_d2": 0.462, "zen_f_b11_d2": 0.467,
        "zen_f_b12_d1": 0.417, "zen_f_b10_d3": 0.462}
print("\n== 3. idem, com a virilha corrigida nos 5 pesados")
print("%-18s %8s %8s %8s %8s  %s" % ("janela", "sem anel", "rms", "|max|",
                                     ">0.02", "pior"))
for lo, hi in [(0.48, 0.60), (0.48, 0.61), (0.48, 0.62), (0.48, 0.625),
               (0.48, 0.63)]:
    ds, sem, quem = [], 0, []
    for aid in ids:
        d = dados[aid]
        f = folha.get(aid, {}).get("short")
        if not f:
            continue
        cz = CORR.get(aid, float(d["crotch_zh"]))
        v, achou = simula(lo, hi, cz, d["tronco"])
        sem += 0 if achou else 1
        ds.append(v - f[0])
        quem.append(aid)
    ds = np.array(ds)
    i = int(np.argmax(np.abs(ds)))
    print("%-18s %8d %8.4f %8.4f %8d  %s %+0.3f" % (
        "%.2f .. %.3f" % (lo, hi), sem, float(np.sqrt((ds ** 2).mean())),
        float(np.abs(ds).max()), int((np.abs(ds) > 0.02).sum()),
        quem[i], ds[i]))
