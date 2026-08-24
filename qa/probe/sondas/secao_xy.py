"""secao_xy.py - LARGURA x PROFUNDIDADE da secao, nos masters, em cm.

POR QUE ELA EXISTE
    A distancia da selecao e feita de CIRCUNFERENCIA, e circunferencia e cega
    para forma: duas cinturas de 101 cm podem ser redonda ou chata, e o que
    aparece de perfil e a profundidade. Em 06/08 isso foi medido em UM corpo e a
    conclusao ficou explicitamente adiada - com um unico corpo real medido,
    mirar a forma dele seria embutir uma pessoa como padrao de todo mundo.

    Esta sonda e a metade da biblioteca dessa comparacao: ela devolve X e Y de
    cada avatar nas MESMAS alturas que o metrics.py usa, para o numero encostar
    no do corpo real sem conversao nenhuma.

O QUE ELA MEDE, E O QUE NAO
    Le o MASTER, que nao tem peca - a mesma razao do §7.10: no dist a costura
    corpo/short esta duplicada e a leitura mente.

    O TRONCO E SEPARADO DO BRACO POR VAO EM X, nao por profundidade. E a mesma
    doutrina do `_arm_cut_vao` (§4.5g): em A-pose existe ar entre braco e tronco
    na altura da cintura, e ar e sinal binario - nao tem limiar para calibrar
    errado. Onde nao houver vao, a linha sai marcada `colado` e NAO deve ser
    usada, exatamente como a largura de foto com braco colado.

    X e Y sao caixa (extremo a extremo), nao perimetro. A razao X/Y e o produto
    aqui; o cm absoluto so serve para conferir contra o `library_metrics.json`.

USO
    blender -b -P qa/probe/sondas/secao_xy.py -- --root . --sexo f
    blender -b -P qa/probe/sondas/secao_xy.py -- --root . --id zen_m_b05h_d2
"""
import argparse
import json
import os
import sys

import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--root", required=True)
ap.add_argument("--id", nargs="*", default=None)
ap.add_argument("--sexo", choices=["m", "f"], default=None)
ap.add_argument("--saida", default=None)
a = ap.parse_args(argv)

ROOT = os.path.abspath(a.root)
import bpy  # noqa: E402

# As mesmas alturas do metrics.py. Fracao da estatura, medida dos pes.
ALTURAS = {"hip": 0.507, "waist_navel": 0.600, "waist_min": 0.645, "chest": 0.720}

index = json.load(open(os.path.join(ROOT, "library.json"), encoding="utf-8"))
alvos = []
for av in index["avatars"]:
    if a.id and av["id"] not in a.id:
        continue
    if a.sexo and av["sex"] != a.sexo:
        continue
    alvos.append(av)
alvos.sort(key=lambda x: (x["sex"], x["measured_bmi"]))


BIN_M = 0.010        # 1 cm por coluna
VAO_MIN_BINS = 2     # so conta como ar 2 cm seguidos de vazio


def secao(co, zh, alvo, tol=0.006):
    """X e Y do TRONCO na altura `alvo`, em unidades de cena (metros).

    A LARGURA DA COLUNA TEM QUE SER MAIOR QUE O ESPACAMENTO DOS VERTICES.
    A primeira versao usava 96 colunas sobre a fatia inteira (~5 mm cada) e em
    60k triangulos sobra coluna vazia DENTRO do tronco: a caminhada parava no
    primeiro vao falso e a cintura media 6,7 cm de largura. Coluna de 1 cm, e
    vao de verdade so com 2 cm seguidos de vazio.
    """
    m = np.abs(zh - alvo) < tol
    if m.sum() < 40:
        return None
    x, y = co[m, 0], co[m, 1]
    lo, hi = float(x.min()), float(x.max())
    if hi - lo <= 1e-9:
        return None
    nb = max(int(np.ceil((hi - lo) / BIN_M)), 3)
    idx = np.clip(((x - lo) / (hi - lo) * (nb - 1)).astype(int), 0, nb - 1)
    cheio = np.bincount(idx, minlength=nb) > 0
    centro = int(np.clip((np.median(x) - lo) / (hi - lo) * (nb - 1), 0, nb - 1))

    def anda(i, passo):
        while True:
            j = i + passo
            if j < 0 or j >= nb:
                return i, False          # acabou a fatia: nao houve ar deste lado
            if cheio[j]:
                i = j
                continue
            k, vazias = j, 0
            while 0 <= k < nb and not cheio[k]:
                vazias += 1
                k += passo
            if vazias >= VAO_MIN_BINS:
                return i, True           # ar de verdade: aqui acaba o tronco
            if k < 0 or k >= nb:
                return i, False
            i = k                        # buraco raso de malha: atravessa

    i0, ar_esq = anda(centro, -1)
    i1, ar_dir = anda(centro, +1)
    dentro = (idx >= i0) & (idx <= i1)
    xt, yt = x[dentro], y[dentro]
    return {"X": float(xt.max() - xt.min()), "Y": float(yt.max() - yt.min()),
            "colado": not (ar_esq and ar_dir), "n": int(dentro.sum())}


saida = {}
print("{:16s} {:>5s} {:>4s} | {:>7s} {:>7s} {:>6s} | {:>7s} {:>7s} {:>6s}".format(
    "id", "IMC", "sexo", "cint X", "cint Y", "X/Y", "quad X", "quad Y", "X/Y"))
print("-" * 92)
for av in alvos:
    caminho = os.path.join(ROOT, "02_master", av["id"] + "_master.glb")
    if not os.path.isfile(caminho):
        print("{:16s} SEM MASTER".format(av["id"]))
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=caminho)
    obj = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = obj.data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    # MUNDO, NAO LOCAL. O glTF e Y-para-cima e o importador poe a conversao na
    # TRANSFORMACAO do objeto, nao nos vertices: lendo `co` cru, z e a
    # profundidade e a cintura media 6,7 cm de largura. A matriz resolve, e o
    # aviso vale para qualquer sonda nova que leia vertice de GLB.
    M = np.array(obj.matrix_world)
    co = co @ M[:3, :3].T + M[:3, 3]
    z = co[:, 2]
    H = float(z.max() - z.min())
    zh = (z - float(z.min())) / H
    # o master e normalizado em 1,75 m; o cm sai da propria malha, nao de tabela
    cm = 100.0 * H / 1.0 if abs(H - 1.75) > 0.2 else 100.0

    linha = {"sex": av["sex"], "bmi": av["measured_bmi"], "H_m": round(H, 4)}
    for rot, frac in ALTURAS.items():
        s = secao(co, zh, frac)
        if not s:
            continue
        linha[rot] = {"X_cm": round(s["X"] * cm, 1), "Y_cm": round(s["Y"] * cm, 1),
                      "XY": round(s["X"] / s["Y"], 3), "colado": s["colado"]}
    saida[av["id"]] = linha

    def fmt(rot):
        d = linha.get(rot)
        if not d:
            return "{:>7s} {:>7s} {:>6s}".format("-", "-", "-")
        return "{:7.1f} {:7.1f} {:6.3f}{}".format(
            d["X_cm"], d["Y_cm"], d["XY"], "*" if d["colado"] else "")

    print("{:16s} {:5.1f} {:>4s} | {} | {}".format(
        av["id"], av["measured_bmi"], av["sex"], fmt("waist_navel"), fmt("hip")))

print("\n* = braco colado ao tronco nessa altura: a largura inclui o braco e NAO vale.")
destino = a.saida or os.path.join(ROOT, "qa", "probe", "secao_xy.json")
os.makedirs(os.path.dirname(destino), exist_ok=True)
with open(destino, "w", encoding="utf-8") as f:
    json.dump(saida, f, indent=2, ensure_ascii=False)
print("-> {}".format(destino))
