"""O braco acima da axila por INUNDACAO barrada no vinco.

Terceira tentativa, e as duas anteriores estao registradas porque o que elas
descartam vale:

  profundidade por coluna de x - o braco e raso e o tronco e fundo, mas nas
  colunas do vinco os dois se sobrepoem em x e a leitura borra justo onde se
  precisa cortar (b12_d1: coluna de braco ja lendo 0.151 contra 0.28 do tronco).

  union-find varrendo |x| de fora para dentro (_braco_lateral.py) - a ideia era
  que a superficie externa do braco viraria componente propria ate o vinco. Nao
  vira: EM CORPO PESADO O TRONCO E MAIS LARGO QUE O BRACO. No b12_d1 o peito vai
  a 0.245 da altura e o braco a 0.180, entao varrendo de fora para dentro quem
  aparece primeiro e o tronco. A varredura so achou o antebraco, que a mascara
  topologica ja tinha.

O que sobra e o vinco propriamente dito. Ele e uma dobra concava, e concavidade
por vertice e barata: a media dos vetores para os vizinhos, projetada na normal.
Em superficie convexa isso e negativo; no fundo de um sulco, positivo.

A INUNDACAO parte da mascara topologica (que ja e braco de verdade, medida pelo
w_limbs) e sobe pela malha, recusando vertice de concavidade alta. O vinco vira
uma cerca fechada em volta da insercao do braco, e a inundacao para nela.

A CONFERENCIA e que a faixa tem que continuar sendo um ANEL FECHADO. Se a
inundacao vazar para o tronco, a banda perde setores de azimute - entao a sonda
imprime a cobertura de azimute do que sobra, e nao so a contagem. Vazamento que
nao se denuncia foi o defeito da bainha (LICOES 4.3).

    blender -b -P qa/probe/sondas/_braco_vinco.py -- --root . --id ID [ID...]
"""
import argparse
import json
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--id", nargs="+", required=True)
a = ap.parse_args(argv)

ROOT = os.path.abspath(a.root)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import bpy  # noqa: E402
import shorts as S  # noqa: E402

MAPA = json.load(open(os.path.join(ROOT, "config", "shorts_map.json"),
                      encoding="utf-8"))
AZ = 48


def um(aid):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master",
                                                    aid + "_master.glb"))
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = obj.data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    nrm = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("normal", nrm)
    nrm = nrm.reshape(n, 3)
    z = co[:, 2]
    H = float(z.max() - z.min())
    zh = (z - z.min()) / H
    cx = float(np.median(co[:, 0]))

    start, dst = S.w_adjacency(me, np)
    _cz, _leg, is_arm = S.w_limbs(me, np, co, H)

    # concavidade: media dos vetores para os vizinhos, projetada na normal
    conc = np.zeros(n)
    for v in range(n):
        j0, j1 = start[v], start[v + 1]
        if j1 <= j0:
            continue
        d = co[dst[j0:j1]] - co[v]
        ln = np.linalg.norm(d, axis=1)
        ok = ln > 1e-9
        if not ok.any():
            continue
        conc[v] = float(np.dot((d[ok] / ln[ok, None]).mean(axis=0), nrm[v]))

    e = MAPA.get(aid, {})
    lo = float(np.min(np.atleast_1d(e.get("faixa_lo_zh", 0.68))))
    hi = float(np.max(np.atleast_1d(e.get("faixa_hi_zh", 0.77))))
    banda = (zh >= lo) & (zh <= hi)
    azb = ((np.arctan2(co[:, 1], co[:, 0] - cx) + np.pi)
           / (2 * np.pi) * AZ).astype(int) % AZ

    topo_ini = zh[is_arm].max() if is_arm.any() else 0.0
    print("\n%s  faixa %.3f..%.3f  braco topologico ate zh %.4f  conc "
          "p50 %.3f p90 %.3f p99 %.3f"
          % (aid, lo, hi, topo_ini, np.percentile(conc, 50),
             np.percentile(conc, 90), np.percentile(conc, 99)))
    print("  %-6s %8s %8s %9s %9s   %s"
          % ("T", "novos", "zh_max", "banda_br", "az_sobra", "obs"))

    # TETO na inundacao. Sem ele o vazamento e garantido e nao e por limiar mal
    # escolhido: por CIMA o braco nao tem fronteira nenhuma com o ombro - o
    # deltoide entra no trapezio numa superficie lisa, sem vinco. O vinco so
    # existe na axila. Mas a faixa tambem nunca sobe ate o alto do ombro, entao
    # basta cercar dentro da altura dela.
    teto = (hi + 0.010) * H + z.min()
    n0 = int(banda.sum())
    for T in (0.02, 0.04, 0.06, 0.08, 0.12):
        mask = is_arm.copy()
        pilha = [int(v) for v in np.where(is_arm & (z <= teto))[0]]
        bloq = (conc > T) | (z > teto)
        while pilha:
            v = pilha.pop()
            for j in range(start[v], start[v + 1]):
                u = int(dst[j])
                if mask[u] or bloq[u] or z[u] < z[v] - 0.002 * H:
                    continue
                mask[u] = True
                pilha.append(u)
        nb = banda & ~mask
        cob = len(np.unique(azb[nb])) if nb.any() else 0
        xr = ((co[nb, 0] - cx).max() - (co[nb, 0] - cx).min()) / H if nb.any() else 0
        print("  %-6.2f %8d %8.4f %9d %9d   larg %.3f  sobra %d%%  %s"
              % (T, int(mask.sum() - is_arm.sum()), zh[mask].max(),
                 int((banda & mask).sum()), cob, xr, 100 * int(nb.sum()) // n0,
                 "VAZOU" if cob < AZ else "ok"))


for aid in a.id:
    um(aid)
