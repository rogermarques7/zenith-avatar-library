#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bainha_curva.py - a bainha como CURVA por azimute da perna, e o render que
prova (ou desmente) o tracado.

    blender -b -P qa/probe/sondas/bainha_curva.py -- --ids zen_f_b06i_d3
    blender -b -P qa/probe/sondas/bainha_curva.py -- --todos --sem-render

Grava qa/probe/hem_curva/{id}.json (a curva, em fracao da altura, por perna) e,
com render, qa/revisao/_hem/{id}/curva_*.png para conferir no olho.

--------------------------------------------------------------------------
O QUE ESTA SONDA DESCOBRIU, E POR QUE ELA PRECISOU EXISTIR (23/09, sessao 37)
--------------------------------------------------------------------------
A bainha e ESCALAR no mapa desde sempre - um numero por perna, um plano
horizontal. O docstring do w_fit justifica isso com uma medida da sessao 4:

    "o vinco da bainha EXISTE, mas e fraco (...) e ele e praticamente
     HORIZONTAL. A bainha ja e um anel reto."

🔴 Aquilo foi medido no `zen_m_b12_d1`, IMC 148 - um corpo em que a coxa e um
cilindro e o short REALMENTE acaba num anel reto. Generalizado para 103, esta
errado. No `zen_f_b06i_d3` a bainha modelada e DIAGONAL: sobe no lado de fora
da coxa e desce para o lado de dentro, e a diferenca entre as duas pontas passa
de 5 cm. Isso esta visivel a olho nu no clay com luz rasante
(`bainha_rasante.py`) - e a tinta, que e um plano horizontal na ponta BAIXA,
sobra preta sobre a pele em todo o resto da volta.

E a queixa do Rogerio em 23/09, palavra por palavra: *"abaixo da barra da perna
tem uma faixa preta alem do limite da barra da perna"*. No `zen_m_b09h_d1`, de
bainha quase horizontal, ele escreveu "pequeno defeito"; no `zen_f_b06i_d3`, de
bainha diagonal, escreveu **"veja o tanto que ficou pintura pra fora"**. As
duas magnitudes batem com as duas geometrias.

--------------------------------------------------------------------------
POR QUE A JANELA NAO E ANCORADA NA VIRILHA
--------------------------------------------------------------------------
Todo o resto do shorts.py ancora na virilha, e aqui isso nao serve: no lado de
FORA a bainha sobe por cima do quadril e fica ACIMA da virilha detectada. Com
teto em `crotch` o tracado gruda no teto (§1.8 - extremo na borda da janela nao
e extremo, e corte) e foi o que aconteceu em 2 dos 3 primeiros testes. A janela
aqui e ancorada na BAINHA DO MAPA, que ja e uma estimativa boa do ponto MAIS
BAIXO do anel, e sobe HEM_SUBIDA acima dela.

--------------------------------------------------------------------------
O QUE ESTA SONDA NAO MEDE
--------------------------------------------------------------------------
- Nao mede bainha onde nao ha vinco modelado. Devolve `sinal` por setor; setor
  fraco fica marcado e quem consome decide.
- O tracado e um CAMINHO DE CUSTO, nao 24 medidas independentes: a penalidade
  de degrau (LAM) impoe continuidade. Isso e o que separa o anel do gomo de
  quadriceps, e tambem o que impede de confiar num setor isolado.
"""
import argparse
import json
import math
import os
import sys

import bpy
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--ids", default="")
ap.add_argument("--todos", action="store_true")
ap.add_argument("--sem-render", action="store_true")
ap.add_argument("--span", type=float, default=0.22)
a = ap.parse_args(argv)

AZ = 24
# quanto a janela sobe acima da bainha do mapa. 0.060 da altura = 10,5 cm: no
# `zen_f_b06i_d3` o lado de fora sobe ~5 cm, e o teto tem de sobrar para o
# maximo nao pousar na borda.
HEM_SUBIDA = 0.060
HEM_DESCIDA = 0.012
# penalidade de degrau do DP, por bin de Z_BINS e por setor de azimute. Medida
# nos tres primeiros: 0.02 e 0.12 dao o MESMO tracado no b06i_d3 e no b01_d1 -
# o sinal domina a penalidade e a escolha nao e critica. Fica no meio.
LAM = 0.05
OUT = os.path.join(ROOT, "qa", "probe", "hem_curva")
RENDER = os.path.join(ROOT, "qa", "revisao", "_hem")


def ridge(A, lo, hi, lam, teto=None):
    """Caminho circular de custo maximo sobre o azimute, com penalidade de
    degrau. `teto` e um bin maximo POR SETOR. Devolve os bins, um por setor."""
    nb, W = A.shape[0], hi - lo + 1
    passos = np.abs(np.subtract.outer(np.arange(W), np.arange(W)))
    custo = np.array([[A[j, lo + z] if (teto is None or lo + z <= teto[j]) else -1e6
                       for z in range(W)] for j in range(nb)])
    melhor = None
    for start in range(W):
        sc = np.full((nb, W), -1e9)
        bk = np.zeros((nb, W), dtype=int)
        sc[0, start] = custo[0, start]
        for j in range(1, nb):
            d = sc[j - 1][None, :] - lam * passos
            k = d.argmax(axis=1)
            sc[j] = d[np.arange(W), k] + custo[j]
            bk[j] = k
        for zend in range(W):
            tot = sc[nb - 1, zend] - lam * abs(zend - start)
            if melhor is None or tot > melhor[0]:
                cam = [zend]
                for j in range(nb - 1, 0, -1):
                    cam.append(int(bk[j, cam[-1]]))
                melhor = (tot, list(reversed(cam)))
    return [lo + z for z in melhor[1]]


def mede(aid, smap):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(
        filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    H = float(co[:, 2].max() - co[:, 2].min())
    k, _ = S.w_curvature(me, np)
    kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)

    lids = [0, 1]
    mx = [float(co[leg_id == l, 0].mean()) if (leg_id == l).any() else 0.0
          for l in lids]
    if mx[0] > mx[1]:
        lids.reverse()

    e = smap[aid]
    res = {"id": aid, "H": round(H, 5), "az_bins": AZ,
           "crotch_zh": round(crotch / H, 4), "pernas": {}}
    for lado, lid in zip("lr", lids):
        sel = np.where(leg_id == lid)[0]
        cx, cy = e.get("hem_center_" + lado, [0.0, 0.0])
        A, ring, occ = S.w_ring_map(np, co, kn, sel, H, (cx, cy), AZ)
        Af = S.w_fill_holes(np, A, occ)
        hm = e["hem_" + lado + "_zh"]
        hm = hm[0] if isinstance(hm, list) else float(hm)
        lo = max(0, int((hm - HEM_DESCIDA) * S.Z_BINS))
        hi = min(S.Z_BINS - 1, int((hm + HEM_SUBIDA) * S.Z_BINS))
        # ---- TETO POR SETOR: geometria, nao calibracao ---------------------
        # O tracado sem teto sobe pelo VINCO INGUINAL nos setores de dentro -
        # medido no zen_m_b09h_d1, em que a bainha real e quase horizontal e a
        # curva subia 7,3 cm rumo a virilha. Nao e ruido: a prega existe e e
        # mais funda que a bainha.
        #
        # O que separa uma da outra nao e profundidade nem altura absoluta, e
        # DE QUE LADO da perna estao. Por FORA a bainha sobe legitimamente por
        # cima do quadril (o short e de cavada alta) e pode passar da virilha.
        # Por DENTRO, acima da virilha nao existe superficie de perna separada -
        # as duas coxas ja se fundiram. Entao o teto interno E a virilha, e isso
        # e fato de topologia, nao limiar escolhido.
        dentro = 1.0 if lado == "l" else -1.0    # a esquerda (x<0) fecha em +x
        teto = []
        for j in range(AZ):
            phi = (j + 0.5) / AZ * 2 * math.pi - math.pi
            t = (math.cos(phi) * dentro + 1.0) / 2.0   # 1 = totalmente interno
            teto.append(int(round(hi + (crotch / H * S.Z_BINS - hi) * t)))
        cam = ridge(Af, lo, hi, LAM, teto)
        zs = [round((b + 0.5) / S.Z_BINS, 4) for b in cam]
        sinal = [round(float(Af[j, cam[j]]), 3) for j in range(AZ)]
        # raio mediano na altura tracada, para poder PROJETAR a curva no render
        # ⚠️ A janela de altura aqui e LARGA de proposito (0.02 da altura). Com
        # 0.004 metade dos setores nao juntava 3 vertices e a curva projetada
        # saia so no meio da imagem - a regua de conferencia ficava cega
        # justamente no lado de FORA, que e onde mora o defeito.
        raios = []
        for j in range(AZ):
            zc = cam[j] / S.Z_BINS * H
            m = sel[np.abs(co[sel, 2] - zc) < 0.020 * H]
            az = np.arctan2(co[m, 1] - cy, co[m, 0] - cx)
            ab = np.clip(((az + math.pi) / (2 * math.pi) * AZ).astype(np.int64), 0, AZ - 1)
            g = m[ab == j]
            raios.append(round(float(np.median(np.hypot(co[g, 0] - cx, co[g, 1] - cy))), 5)
                         if g.size >= 3 else None)
        bons = [j for j in range(AZ) if raios[j] is not None]
        for j in range(AZ):
            if raios[j] is None and bons:
                raios[j] = raios[min(bons, key=lambda b: min(abs(b - j), AZ - abs(b - j)))]
        res["pernas"][lado] = {
            "hem_mapa_zh": round(hm, 4), "centro": [round(cx, 5), round(cy, 5)],
            "curva_zh": zs, "sinal": sinal, "raio": raios,
            "min": min(zs), "max": max(zs),
            "janela": [round((lo + 0.5) / S.Z_BINS, 4), round((hi + 0.5) / S.Z_BINS, 4)],
            "no_teto": sum(1 for b in cam if b >= hi - 1),
            "no_piso": sum(1 for b in cam if b <= lo + 1),
        }
    return res, ob, co, H


def render(aid, res, ob, co, H):
    """Clay com luz rasante + a curva projetada, para o veredito visual."""
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    ob.data.materials.clear()
    mat = bpy.data.materials.new("clay")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.72, 0.73, 0.75, 1)
    b.inputs["Roughness"].default_value = 0.55
    b.inputs["Metallic"].default_value = 0.0
    ob.data.materials.append(mat)

    sc = bpy.context.scene
    for nome in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = nome
            break
        except TypeError:
            continue
    RX, RY = 1100, 900
    sc.render.resolution_x, sc.render.resolution_y = RX, RY
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.35, 0.38, 1)

    z0 = float(co[:, 2].min())
    hm = res["pernas"]["l"]["hem_mapa_zh"]
    zc = z0 + hm * H
    ld = bpy.data.lights.new("k", type="AREA")
    ld.energy = 900
    ld.size = 2
    lamp = bpy.data.objects.new("k", ld)
    sc.collection.objects.link(lamp)

    cd = bpy.data.cameras.new("c")
    cd.type = "ORTHO"
    cd.ortho_scale = H * a.span
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam

    outdir = os.path.join(RENDER, aid)
    os.makedirs(outdir, exist_ok=True)
    marcas = {}
    for nome, ang in (("frente", 0), ("costas", 180)):
        r = math.radians(ang)
        cam.location = (5 * math.sin(r), -5 * math.cos(r), zc)
        cam.rotation_euler = (math.radians(90), 0, r)
        lamp.location = (-3 * math.cos(r) - 3 * math.sin(r),
                         -3 * math.cos(r) + 3 * math.sin(r), zc - H * 0.02)
        lamp.rotation_euler = (math.radians(100), 0, r + math.radians(-40))
        sc.render.filepath = os.path.join(outdir, "curva_" + nome + ".png")
        bpy.ops.render.render(write_still=True)

        # projecao ortografica com camera nivelada: X_cam -> coluna, Z -> linha
        esc = cd.ortho_scale
        pts, linha_mapa = [], []
        for lado in ("l", "r"):
            p = res["pernas"][lado]
            cx, cy = p["centro"]
            for j in range(AZ):
                if p["raio"][j] is None:
                    continue
                phi = (j + 0.5) / AZ * 2 * math.pi - math.pi
                X = cx + p["raio"][j] * math.cos(phi)
                Y = cy + p["raio"][j] * math.sin(phi)
                # so o que esta virado para a camera
                nx, ny = math.cos(phi), math.sin(phi)
                vis = (-nx * math.sin(r) + ny * math.cos(r))
                if vis > -0.15:
                    continue
                xc = X * math.cos(r) + Y * math.sin(r)
                Z = z0 + p["curva_zh"][j] * H
                pts.append([int(round(RX / 2 + xc / esc * RX)),
                            int(round(RY / 2 - (Z - zc) / (esc * RY / RX) * RY))])
            linha_mapa.append(p["hem_mapa_zh"])
        marcas[nome] = {
            "pts": pts,
            "y_mapa": int(round(RY / 2 - (z0 + linha_mapa[0] * H - zc)
                                / (cd.ortho_scale * RY / RX) * RY)),
        }
    with open(os.path.join(outdir, "curva.json"), "w", encoding="utf-8") as f:
        json.dump({"id": aid, "res": [RX, RY], "vistas": marcas}, f)


def main():
    with open(os.path.join(ROOT, "config", "shorts_map.json"), encoding="utf-8") as f:
        smap = json.load(f)
    ids = sorted(smap) if a.todos else [x for x in a.ids.split(",") if x]
    os.makedirs(OUT, exist_ok=True)
    for aid in ids:
        res, ob, co, H = mede(aid, smap)
        if not a.sem_render:
            render(aid, res, ob, co, H)
        with open(os.path.join(OUT, aid + ".json"), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)
        l, r = res["pernas"]["l"], res["pernas"]["r"]
        print("OK {:<18} mapa {:.4f}/{:.4f}  curva l {:.4f}..{:.4f} (teto {}) "
              " r {:.4f}..{:.4f} (teto {})".format(
                  aid, l["hem_mapa_zh"], r["hem_mapa_zh"],
                  l["min"], l["max"], l["no_teto"],
                  r["min"], r["max"], r["no_teto"]))


main()
