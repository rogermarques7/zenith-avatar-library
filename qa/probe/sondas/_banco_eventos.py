"""Despeja TODOS os eventos grandes de fusao dos 76, para varrer offline.

O filtro de braco do w_limbs tem tres constantes e nenhuma delas foi medida numa
populacao: as tres sairam de UM avatar (zen_f_b01_d1) contra UM blob. O
zen_f_b12_d1 mostrou o custo disso - os dois bracos dele reprovam em
`ext >= 0.15 H` por 0.004, saem pintados de preto do deltoide ao pulso, e a
faixa atravessa os dois. Mexer no numero por causa de um avatar repetiria
exatamente o metodo que criou o defeito.

Entao o banco. Uma passada de Blender por avatar, o sinal cru no disco, e a
escolha depois - mesmo padrao do _banco_anel.py.

O QUE VAI JUNTO, e por que: `ext` sozinho nao distingue braco de blob, so ordena.
Cada evento leva tambem o afastamento lateral do lado menor (|x| mediano em
alturas de tronco) e o desvio em Y. Braco e LATERAL; blob de mao encostada na
coxa, pescoco e cabelo sao centrais. Isso da um teste independente do `ext`, que
e o que falta para dizer "afrouxar aqui nao deixa entrar lixo" sem apelar para o
proprio numero que se esta afrouxando.

    blender -b -P qa/probe/sondas/_banco_eventos.py -- --root . --id ID [ID...]
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

OUT = os.path.join(ROOT, "qa", "probe", "eventos")
os.makedirs(OUT, exist_ok=True)


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
    z0 = float(z.min())

    start, dst = S.w_adjacency(me, np)
    order = np.argsort(z, kind="stable")
    rank = np.empty(n, dtype=np.int64)
    rank[order] = np.arange(n)
    parent = list(range(n))

    def find(x):
        r = x
        while parent[r] != r:
            r = parent[r]
        while parent[x] != r:
            parent[x], x = r, parent[x]
        return r

    members, ev = {}, []
    sig = max(200, int(0.015 * n))
    for v in order:
        v = int(v)
        parent[v] = v
        members[v] = [v]
        for j in range(start[v], start[v + 1]):
            u = int(dst[j])
            if rank[u] >= rank[v]:
                continue
            ra, rb = find(u), find(v)
            if ra == rb:
                continue
            ma, mb = members[ra], members[rb]
            if len(ma) < len(mb):
                ra, rb, ma, mb = rb, ra, mb, ma
            if len(mb) >= sig and len(ma) >= sig:
                ev.append((float(z[v]), list(mb)))
            parent[rb] = ra
            ma.extend(mb)
            del members[rb]

    # O centro em X e o do CORPO, nao o da malha: a media dos vertices pende para
    # onde ha mais geometria. Mediana e o que resiste a isso.
    cx = float(np.median(co[:, 0]))
    saida = []
    for ez, sm in ev:
        sm = np.array(sm, dtype=np.int64)
        base = float(z[sm].min())
        saida.append({
            "funde_zh": (ez - z0) / H,
            "base_zh": (base - z0) / H,
            "ext_zh": (ez - base) / H,
            "n": int(len(sm)),
            "lat_zh": float(np.median(np.abs(co[sm, 0] - cx))) / H,
            "lat_max_zh": float(np.abs(co[sm, 0] - cx).max()) / H,
        })
    return {"H": H, "n": n, "sig": sig, "eventos": saida}


tudo = {}
p = os.path.join(OUT, "_eventos.json")
if os.path.exists(p):
    tudo = json.load(open(p, encoding="utf-8"))
for aid in a.id:
    tudo[aid] = um(aid)
    print("%-16s %d eventos" % (aid, len(tudo[aid]["eventos"])))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(tudo, f, indent=1)
print("gravado: qa/probe/eventos/_eventos.json  (%d avatares)" % len(tudo))
