"""O braco ACIMA da axila, por varredura de union-find na LATERAL.

O w_limbs acha o braco varrendo de BAIXO PARA CIMA: o componente do braco existe
enquanto ele nao encosta no tronco, e acaba na fusao. Isso basta em corpo magro,
onde a fusao e a axila e fica acima da faixa. Em corpo pesado a gordura faz o
braco encostar no tronco bem mais embaixo - em 30 dos 37 femininos a fusao cai
ABAIXO do topo da faixa -, e o pedaco de braco que sobra acima dela nao esta
marcado. Como o campo da roupa so olha altura, a faixa sai pintada atravessando
os dois bracos. Visto no b12_d1 (IMC 114), no b10_d1 e no b08_d1: a banda segue
pelo braco com a borda serrilhada.

A IDEIA. E a mesma varredura, girada 90 graus. Ordenando os vertices por |x-cx|
DECRESCENTE e unindo cada um aos vizinhos ja incluidos, a superficie externa de
cada braco aparece como componente propria e so se junta ao tronco quando a
varredura chega no VINCO da axila - que e, por construcao, exatamente a linha
que se quer. Nao e criterio novo: e a ferramenta que ja esta no arquivo, com o
eixo trocado.

Por que nao pela profundidade, que era o outro candidato: o braco e raso (0.06 a
0.09 da altura) e o tronco e fundo (0.20), mas nas colunas do vinco os dois se
sobrepoem em x e a leitura borra - no b12_d1 a coluna de braco ja le 0.151
contra 0.28 do tronco. Degrau que borra justo onde se precisa cortar nao serve.

    blender -b -P qa/probe/sondas/_braco_lateral.py -- --root . --id ID [ID...]
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
    z = co[:, 2]
    H = float(z.max() - z.min())
    zh = (z - z.min()) / H
    cx = float(np.median(co[:, 0]))
    r = np.abs(co[:, 0] - cx)

    start, dst = S.w_adjacency(me, np)

    # A varredura roda so no TRONCO PARA CIMA. Abaixo do quadril o |x| decrescente
    # encontraria as duas pernas, que sao dois componentes legitimos e nao
    # interessam aqui - e o w_limbs ja cuida delas.
    piso = 0.55 * H + z.min()
    vivo = z >= piso
    order = [int(v) for v in np.argsort(-r, kind="stable") if vivo[v]]
    pos = np.full(n, -1, dtype=np.int64)
    for k, v in enumerate(order):
        pos[v] = k

    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    members, ev = {}, []
    sig = max(120, int(0.004 * n))
    for v in order:
        parent[v] = v
        members[v] = [v]
        for j in range(start[v], start[v + 1]):
            u = int(dst[j])
            if pos[u] < 0 or pos[u] >= pos[v]:
                continue
            ra, rb = find(u), find(v)
            if ra == rb:
                continue
            ma, mb = members[ra], members[rb]
            if len(ma) < len(mb):
                ra, rb, ma, mb = rb, ra, mb, ma
            if len(mb) >= sig and len(ma) >= sig:
                ev.append((float(r[v]) / H, list(mb)))
            parent[rb] = ra
            ma.extend(mb)
            del members[rb]

    e = MAPA.get(aid, {})
    lo = float(np.min(np.atleast_1d(e.get("faixa_lo_zh", 0.68))))
    hi = float(np.max(np.atleast_1d(e.get("faixa_hi_zh", 0.77))))
    banda = (zh >= lo) & (zh <= hi)

    print("\n%s  H=%.3f  faixa %.3f..%.3f  %d eventos (sig=%d)"
          % (aid, H, lo, hi, len(ev), sig))
    print("  %-8s %7s %8s %8s %8s %8s   %s"
          % ("vinco_r", "n", "zh_min", "zh_max", "lado", "na_banda", "x_med"))
    for rr, sm in ev[:6]:
        sm = np.array(sm, dtype=np.int64)
        lado = "esq" if np.median(co[sm, 0] - cx) < 0 else "dir"
        print("  %-8.4f %7d %8.4f %8.4f %8s %8d   %+.4f"
              % (rr, len(sm), zh[sm].min(), zh[sm].max(), lado,
                 int(banda[sm].sum()), np.median(co[sm, 0] - cx) / H))

    # Os dois primeiros eventos de lados opostos = os dois bracos.
    braco = np.zeros(n, dtype=bool)
    lados = set()
    for rr, sm in ev:
        sm = np.array(sm, dtype=np.int64)
        lado = "esq" if np.median(co[sm, 0] - cx) < 0 else "dir"
        if lado in lados:
            continue
        lados.add(lado)
        braco[sm] = True
        if len(lados) == 2:
            break

    nb = banda & ~braco
    print("  banda: %d vertices, %d sobram fora do braco, x/H %.3f..%.3f"
          % (banda.sum(), nb.sum(),
             (co[nb, 0] - cx).min() / H, (co[nb, 0] - cx).max() / H))
    print("  braco novo: %d vertices na banda (%d no total)"
          % (int((banda & braco).sum()), int(braco.sum())))


for aid in a.id:
    um(aid)
