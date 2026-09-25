#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""borda_viva.py - acha a borda do TECIDO pelas ARESTAS VIVAS da malha e
desenha a proposta sobre o clay com luz rasante. NAO grava o mapa.

    blender -b -P qa/probe/sondas/borda_viva.py -- --ids zen_f_b06i_d3,...
    blender -b -P qa/probe/sondas/borda_viva.py -- --ids ... --sem-render
    python qa/probe/sondas/borda_viva_folha.py          # risca e monta as folhas

--------------------------------------------------------------------------
O SINAL (sessao 38, 24/09)
--------------------------------------------------------------------------
Cinco detectores de bainha morreram procurando o VINCO (concavidade, degrau
de raio, cume no pixel): em todos existe um vinco de PELE mais fundo que o de
tecido a poucos centimetros - a prega inguinal e o sulco gluteo, que sao as
duas metades da virilha (LICOES.md 4.5n). E a folha, a saida A, e o desenho,
menor que o tecido que a Meshy modelou (4.5l).

A Meshy modela a borda do tecido como aresta VIVA e serrilhada - o angulo
diedro entre as duas faces vizinhas passa de 30 graus -, enquanto a prega de
pele e um vale LISO. Medido em 8 masters: a barra aparece como anel fechado
em volta da perna, separado da virilha, inclusive no zen_m_b09h_d1 (onde a
tentativa 5 achou a virilha) e no zen_f_b01_d1 (6 mm entre as duas). E a
tinta de hoje esta sempre no ponto MAIS BAIXO desse anel: o quantil baixo do
w_ring_map acha a altura em que todos os setores estao vincados, que num anel
inclinado e o fundo dele.

--------------------------------------------------------------------------
O MODELO
--------------------------------------------------------------------------
Cada borda e uma curva fechada z(az) de POUCOS harmonicos - na barra, o
primeiro harmonico e um corte INCLINADO da coxa (3 numeros por perna). O
escalar de hoje tem 1 grau de liberdade e nao segue a diagonal; o tracador de
24 setores livres (bainha_curva.py) tinha liberdade demais e escorregava para
a virilha. Aqui:

  1. RANSAC do 1o harmonico, com nota = COBERTURA de azimute (24 setores). Um
     anel que da a volta vence um arco que so existe de um lado - que e o que
     a virilha e em volta da coxa, e o avental em volta do tronco.
  2. Bainha DUPLA (costura + borda): vale a linha MAIS EXTERNA da peca - a de
     baixo na barra e na base da faixa, a de cima no cos e no topo da faixa.
     E onde o tecido acaba.
  3. Refino robusto (Tukey) com mais harmonicos, so nos pontos perto da curva.
  4. Limiar de angulo ADAPTATIVO por borda (30 -> 12 graus): o cos as vezes e
     aresta mole (zen_f_b03h_d1 so aparece em 14).

A saida traz COBERTURA e RMS por borda. Cobertura baixa nao e numero para
gravar - e avatar para o olho dele.

--------------------------------------------------------------------------
O QUE ESTA SONDA NAO MEDE
--------------------------------------------------------------------------
- Dobra de pele VIVA existe: o avental dos corpos pesados (zen_m_b12_d1) tem
  vincos com diedro alto. O corredor em volta da curva atual e a nota de
  cobertura seguram parte; o resto e o olho.
- A frente do cos debaixo de um avental nao tem borda visivel na malha - quem
  decide ali continua sendo o w_cos_avental.
- Nao olha braco nem axila (tinta no triceps e outra frente).

O RENDER: clay sem pintura, luz rasante que GIRA com a camera (4.5o), camera
ortografica nivelada, BRACOS REMOVIDOS (a mao tapava a lateral da coxa na
vista de lado). As curvas nao sao desenhadas em 3D: a sonda grava o pixel de
cada ponto VISIVEL (raio contra a malha) e o borda_viva_folha.py risca depois,
pontilhado, para nao tapar o relevo.
"""
import argparse
import json
import math
import os
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--ids", default="")
ap.add_argument("--sem-render", action="store_true")
ap.add_argument("--regioes", default="",
                help="re-renderiza SO estas regioes (barra,cos,faixa); as outras "
                     "vistas do proposta.json anterior sao mantidas")
ap.add_argument("--out", default=os.path.join(ROOT, "qa", "revisao", "_viva"))
a = ap.parse_args(argv)

NB = 24                       # setores do mapa (WAIST_AZ_BINS)
LIMIARES = (30.0, 22.0, 16.0, 12.0)
COB_OK = 0.75                 # para de baixar o limiar quando cobre isto
TOL_RANSAC = 0.004            # fracao da altura (~7 mm)
TOL_FINO = 0.0035
ORDEM = {"hem_l": 2, "hem_r": 2, "cos": 3, "faixa_lo": 3, "faixa_hi": 4}
EXTERNA = {"hem_l": "baixo", "hem_r": "baixo", "cos": "cima",
           "faixa_lo": "baixo", "faixa_hi": "cima"}
SETOR_AZ = -math.pi + (np.arange(NB) + 0.5) * 2 * math.pi / NB


# ---------------------------------------------------------------- ajuste --
def base(th, k):
    cols = [np.ones_like(th)]
    for j in range(1, k + 1):
        cols += [np.cos(j * th), np.sin(j * th)]
    return np.stack(cols, axis=1)


def cobertura(th, sel):
    b = ((th[sel] + math.pi) / (2 * math.pi) * NB).astype(int) % NB
    return int((np.bincount(b, minlength=NB) > 0).sum())


def ransac(th, z, rng, it=3000):
    n = len(z)
    if n < 12:
        return None, 0
    P1 = base(th, 1)
    best, bs = None, -1
    for _ in range(it):
        idx = rng.choice(n, 3, replace=False)
        d = np.abs(np.angle(np.exp(1j * (th[idx][:, None] - th[idx][None, :]))))
        if d.max() < math.radians(40):
            continue
        try:
            c = np.linalg.solve(P1[idx], z[idx])
        except np.linalg.LinAlgError:
            continue
        # anel quase horizontal: a inclinacao da bainha/cos real e de poucos
        # centimetros; 0.06 da altura em meia volta ja e outra coisa
        if math.hypot(c[1], c[2]) > 0.035:
            continue
        inl = np.abs(z - P1 @ c) < TOL_RANSAC
        s = cobertura(th, inl) * 10000 + int(inl.sum())
        if s > bs:
            best, bs = c, s
    return best, bs // 10000


def refina(th, z, c0, k, lado):
    """Da semente do RANSAC ate a curva final: escolhe a linha EXTERNA de uma
    borda dupla e refina com k harmonicos, robusto."""
    P1 = base(th, 1)
    r = z - P1 @ c0
    # --- a linha externa: varre um deslocamento paralelo e acha os picos de
    # cobertura. Bainha dupla da dois picos; fica o de fora.
    ds = np.arange(-0.025, 0.0251, 0.0005)
    cov = np.array([cobertura(th, np.abs(r - d) < 0.0025) for d in ds])
    cmax = cov.max()
    picos = [i for i in range(len(ds))
             if cov[i] >= max(0.5 * cmax, 6)
             and cov[i] >= cov[max(0, i - 1)] and cov[i] >= cov[min(len(ds) - 1, i + 1)]]
    # picos colados sao o mesmo pico
    grupos = []
    for i in picos:
        if grupos and i - grupos[-1][-1] <= 4:
            grupos[-1].append(i)
        else:
            grupos.append([i])
    reps = [max(g, key=lambda i: cov[i]) for g in grupos] or [int(np.argmax(cov))]
    esc = min(reps, key=lambda i: ds[i]) if lado == "baixo" else max(reps, key=lambda i: ds[i])
    c = np.zeros(2 * k + 1)
    c[:3] = c0
    c[0] += ds[esc]
    P = base(th, k)
    # densidade: setor com muitos pontos nao pode mandar na curva inteira
    b = ((th + math.pi) / (2 * math.pi) * NB).astype(int) % NB
    dens = np.bincount(b, minlength=NB).astype(float)
    wden = 1.0 / np.maximum(dens[b], 1.0)
    reg = np.zeros(2 * k + 1)
    for j in range(1, k + 1):
        reg[2 * j - 1:2 * j + 1] = 1e-4 * j ** 2
    for tol in (0.008, 0.006, 0.005, TOL_FINO, TOL_FINO):
        r = z - P @ c
        sel = np.abs(r) < tol
        if sel.sum() < 2 * k + 4:
            break
        u = r[sel] / tol
        w = wden[sel] * (1 - u ** 2) ** 2
        A = P[sel] * w[:, None]
        M = A.T @ P[sel] + np.diag(reg) * w.sum()
        c = np.linalg.solve(M, A.T @ z[sel])
    r = z - P @ c
    inl = np.abs(r) < TOL_FINO
    return c, {"cobertura": round(cobertura(th, inl) / NB, 3),
               "n": int(inl.sum()),
               "rms": round(float(np.sqrt(np.mean(r[inl] ** 2))) if inl.any() else 1.0, 5),
               "picos": [round(float(ds[i]), 4) for i in reps],
               "desloc": round(float(ds[esc]), 4)}


ENV_BINS = 48
ENV_DENTRO = 0.004   # quanto o envelope pode entrar para DENTRO da peca
ENV_FORA = 0.015     # quanto pode sair para FORA dela, procurando a ultima linha
ENV_APOIO = 3        # pontos a menos de 2 mm para uma linha contar (nao ruido solto)


def envelope(th, z, f, lado):
    """A LINHA EXTERNA setor a setor, dentro do corredor que o ajuste suave deu.

    Porque existe: a curva de poucos harmonicos assume que as duas linhas da
    bainha dupla sao PARALELAS, e nas costas do zen_f_b06i_d3 nao sao - a de
    cima segue o gluteo e a de baixo e a barra. O ajuste suave troca de linha
    no meio da volta e a azul ficou ~1 cm acima da ultima linha serrilhada nas
    costas-dentro da coxa. Aqui o harmonico so da o CORREDOR; quem diz a
    altura e a linha mais externa que tem apoio (3 pontos em 2 mm), por setor
    de 7,5 graus. Depois mediana de 3 contra o disparo e gaussiana contra a
    escada - o par de sempre (4.5f, 4.5g)."""
    r = z - f
    b = ((th + math.pi) / (2 * math.pi) * ENV_BINS).astype(int) % ENV_BINS
    sinal = -1.0 if lado == "baixo" else 1.0
    out = np.full(ENV_BINS, np.nan)
    for i in range(ENV_BINS):
        m = b == i
        # distancia para FORA da peca: positiva = mais externa que a curva
        fora = sinal * r[m]
        fora = np.sort(fora[(fora > -ENV_DENTRO) & (fora < ENV_FORA)])[::-1]
        for j, v in enumerate(fora):
            if np.sum(np.abs(fora - v) < 0.002) >= ENV_APOIO:
                out[i] = v
                break
    ok = ~np.isnan(out)
    if ok.sum() < ENV_BINS // 3:
        return None, float(ok.mean())
    idx = np.arange(ENV_BINS)
    out = np.interp(idx, idx[ok], out[ok], period=ENV_BINS)
    med = np.array([np.median(out[[(i - 1) % ENV_BINS, i, (i + 1) % ENV_BINS]])
                    for i in range(ENV_BINS)])
    k = np.exp(-0.5 * (np.arange(-3, 4) / 1.2) ** 2)
    k /= k.sum()
    liso = np.array([np.dot(k, med[(i + np.arange(-3, 4)) % ENV_BINS])
                     for i in range(ENV_BINS)])
    return sinal * liso, float(ok.mean())


def ajusta(nome, th_all, z_all, ang_all, rng):
    melhor = None
    for lim in LIMIARES:
        s = ang_all >= lim
        th, z = th_all[s], z_all[s]
        c0, _ = ransac(th, z, rng)
        if c0 is None:
            continue
        c, info = refina(th, z, c0, ORDEM[nome], EXTERNA[nome])
        info["limiar"] = lim
        k = ORDEM[nome]
        f = base(th, k) @ c
        env, cob_env = envelope(th, z, f, EXTERNA[nome])
        info["cobertura_env"] = round(cob_env, 3)
        az_env = -math.pi + (np.arange(ENV_BINS) + 0.5) * 2 * math.pi / ENV_BINS
        if env is None:
            env = np.zeros(ENV_BINS)
        # curva final em 48 setores = suave + envelope; o mapa recebe 24
        fina = base(az_env, k) @ c + env
        info["curva48"] = [round(float(v), 5) for v in fina]
        info["curva"] = [round(float(v), 5) for v in
                         S.w_interp_circ(np, fina, SETOR_AZ)]
        info["env_cm"] = [round(float(env.min()) * 175, 1), round(float(env.max()) * 175, 1)]
        info["coef"] = [float(v) for v in c]
        if melhor is None or info["cobertura"] > melhor["cobertura"] + 0.04:
            melhor = info
        if info["cobertura"] >= COB_OK:
            break
    return melhor


# ------------------------------------------------------------- geometria --
def arestas_vivas(me, co):
    ne, nl, npol = len(me.edges), len(me.loops), len(me.polygons)
    ev = np.empty(ne * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ev)
    ev = ev.reshape(-1, 2)
    le = np.empty(nl, dtype=np.int64)
    me.loops.foreach_get("edge_index", le)
    ls = np.empty(npol, dtype=np.int64)
    lt = np.empty(npol, dtype=np.int64)
    me.polygons.foreach_get("loop_start", ls)
    me.polygons.foreach_get("loop_total", lt)
    pn = np.empty(npol * 3)
    me.polygons.foreach_get("normal", pn)
    pn = pn.reshape(-1, 3)
    lp = np.repeat(np.arange(npol), lt)
    ordem = np.argsort(le, kind="stable")
    le_s, lp_s = le[ordem], lp[ordem]
    cnt = np.bincount(le_s, minlength=ne)
    ini = np.concatenate([[0], np.cumsum(cnt)[:-1]])
    ok = cnt == 2
    f1 = lp_s[ini[ok]]
    f2 = lp_s[ini[ok] + 1]
    cosang = np.clip((pn[f1] * pn[f2]).sum(1), -1, 1)
    ang = np.degrees(np.arccos(cosang))
    eid = np.where(ok)[0]
    mid = co[ev[eid]].mean(axis=1)
    return eid, ev[eid], mid, ang


def curva_mapa(v):
    v = np.atleast_1d(np.asarray(v, dtype=float))
    return np.full(NB, v[0]) if v.size == 1 else v


def uma(aid, smap, rng):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, "02_master", aid + "_master.glb"))
    ob = [o for o in bpy.context.scene.objects if o.type == "MESH"][0]
    me = ob.data
    me.update()
    n = len(me.vertices)
    co = np.empty(n * 3)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    H = float(co[:, 2].max() - co[:, 2].min())
    crotch, leg_id, is_arm = S.w_limbs(me, np, co, H)
    e = smap[aid]
    crz = (e.get("diag") or {}).get("crotch_zh") or crotch / H

    eid, ev, mid, ang = arestas_vivas(me, co)
    braco = is_arm[ev[:, 0]] | is_arm[ev[:, 1]]
    # SO ARESTA DEITADA. A borda de uma peca e um anel: suas arestas vivas sao
    # quase horizontais. Vinco VERTICAL (coluna, linha alba, fenda do gluteo)
    # tambem e aresta viva, e num setor de azimute ele da pontos em TODAS as
    # alturas - o envelope "de cima" subia por ele e o cos saia com um pico na
    # coluna (zen_f_b08h_d3, zen_f_b06h_d3) ou um V na frente.
    vet = co[ev[:, 1]] - co[ev[:, 0]]
    deitada = np.abs(vet[:, 2]) < 0.7071 * np.linalg.norm(vet, axis=1)
    ang = np.where(deitada, ang, 0.0)
    # PERTO do braco, para a faixa: a dobra da AXILA e aresta viva e fica colada
    # na quina da faixa. No zen_f_b05i_d2 o envelope "de cima" subiu por ela e o
    # topo da faixa saiu +9,6 cm nos lados. 3 cm de raio em volta de qualquer
    # vertice de braco; a curva nesses setores vem da interpolacao dos vizinhos.
    arm_idx = np.where(is_arm)[0]
    perto_braco = np.zeros(len(mid), dtype=bool)
    if arm_idx.size:
        kd = KDTree(arm_idx.size)
        for j, vi in enumerate(arm_idx):
            kd.insert(co[vi], j)
        kd.balance()
        perto_braco = np.array([kd.find(tuple(p))[2] < 0.03 for p in mid])
    zh = mid[:, 2] / H
    atual = {
        "hem_l": curva_mapa(e["hem_l_zh"]), "hem_r": curva_mapa(e["hem_r_zh"]),
        "cos": curva_mapa(e["waist_zh"]),
    }
    if "faixa_lo_zh" in e:
        atual["faixa_lo"] = curva_mapa(e["faixa_lo_zh"])
        atual["faixa_hi"] = curva_mapa(e["faixa_hi_zh"])
    centro = {"hem_l": e["hem_center_l"], "hem_r": e["hem_center_r"],
              "cos": [0.0, 0.0], "faixa_lo": [0.0, 0.0], "faixa_hi": [0.0, 0.0]}

    res = {"id": aid, "H": H, "crotch_zh": round(float(crz), 4),
           "cos_avental": bool(e.get("cos_avental")), "bordas": {}}
    for nome, cur in atual.items():
        cx, cy = centro[nome]
        if nome.startswith("hem"):
            lado = mid[:, 0] < 0 if nome == "hem_l" else mid[:, 0] >= 0
            lo = cur.min() - 0.02
            hi = min(cur.max() + 0.08, crz + 0.06)
            sel = lado & ~braco & (zh > lo) & (zh < hi)
        elif nome == "cos":
            lo, hi = cur.min() - 0.04, cur.max() + 0.04
            sel = ~braco & (zh > max(lo, crz + 0.02)) & (zh < hi)
        elif nome == "faixa_lo":
            lo, hi = cur.min() - 0.025, cur.max() + 0.025
            sel = ~braco & ~perto_braco & (zh > lo) & (zh < hi)
        else:
            lo, hi = cur.min() - 0.02, cur.max() + 0.03
            sel = ~braco & ~perto_braco & (zh > lo) & (zh < hi)
        th = np.arctan2(mid[sel, 1] - cy, mid[sel, 0] - cx)
        # CORREDOR POR AZIMUTE, alem do global: em volta da curva atual NAQUELE
        # setor. Com o corredor so global, o topo da faixa do zen_f_b05i_d2 (frente
        # 0.760, costas 0.723) aceitava ate 0.79 nas costas e o RANSAC achou um
        # anel inclinado passando por uma estrutura a 0.785 - +10,8 cm.
        desce, sobe = {"hem_l": (0.02, 0.08), "hem_r": (0.02, 0.08),
                       "cos": (0.04, 0.04), "faixa_lo": (0.025, 0.025),
                       "faixa_hi": (0.02, 0.03)}[nome]
        ref = S.w_interp_circ(np, cur, th)
        zs = zh[sel]
        dentro = (zs > ref - desce) & (zs < ref + sobe)
        th, zs, angs = th[dentro], zs[dentro], ang[sel][dentro]
        info = ajusta(nome, th, zs, angs, rng)
        if info is None:
            res["bordas"][nome] = {"atual": [round(float(v), 5) for v in cur],
                                   "centro": [cx, cy], "falhou": True}
            continue
        info["atual"] = [round(float(v), 5) for v in cur]
        info["centro"] = [cx, cy]
        info["corredor"] = [round(float(lo), 4), round(float(hi), 4)]
        d = np.array(info["curva"]) - cur
        info["delta_cm"] = [round(float(d.min() * H * 100), 1), round(float(d.max() * H * 100), 1)]
        # os pontos, para a folha poder mostrar o que o ajuste viu
        res["bordas"][nome] = info

    outdir = os.path.join(a.out, aid)
    os.makedirs(outdir, exist_ok=True)
    if not a.sem_render:
        res["vistas"] = render(aid, ob, me, co, H, is_arm, res, outdir)
    with open(os.path.join(outdir, "proposta.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    linha = ["{:<15}".format(aid)]
    for nome, b in res["bordas"].items():
        if b.get("falhou"):
            linha.append("{} FALHOU".format(nome))
        else:
            linha.append("{} {:+.1f}..{:+.1f}cm cob{:.2f} L{:.0f}".format(
                nome, b["delta_cm"][0], b["delta_cm"][1], b["cobertura"], b["limiar"]))
    print(" | ".join(linha), flush=True)


# ----------------------------------------------------------------- render --
VISTAS = (0, 60, 120, 180, 240, 300)
RES_X, RES_Y = 1400, 1000


def _curva_z(b, chave):
    if chave == "atual":
        return lambda t: S.w_interp_circ(np, np.array(b["atual"]), t)
    return lambda t: S.w_interp_circ(np, np.array(b["curva48"]), t)


def pontos_3d(bvh, b, chave, H):
    cx, cy = b["centro"]
    t = np.linspace(-math.pi, math.pi, 900, endpoint=False)
    zz = np.atleast_1d(_curva_z(b, chave)(t)) * H
    out = []
    for ti, z in zip(t, zz):
        o = Vector((cx, cy, float(z)))
        d = Vector((math.cos(ti), math.sin(ti), 0.0))
        hit = bvh.ray_cast(o, d, 1.5)
        out.append(None if hit[0] is None else tuple(hit[0]))
    # ⚠️ Raio que passa pelo buraco do braco removido acerta o toco que sobra
    # pendurado (corpos pesados) - risco solto no ar, longe do tronco. Nao e
    # medida, e desenho: corta o que estiver 25% alem da mediana do raio.
    # So no TRONCO (centro na origem). Na perna o centro gravado no mapa pode
    # estar fora do eixo - no zen_f_b07i_d1 o raio vai de 7 a 14 cm em volta
    # dele - e o filtro cortava metade da barra do desenho.
    # Na perna, o raio que sai pelo lado de DENTRO atravessa o vao e acerta a
    # OUTRA perna: risco solto na coxa vizinha. Ponto do lado errado do eixo
    # do corpo nao e desta perna.
    if (cx, cy) != (0.0, 0.0):
        lado = -1.0 if cx < 0 else 1.0
        out = [p if p is not None and p[0] * lado > -0.005 else None for p in out]
    rr = [math.hypot(p[0] - cx, p[1] - cy) for p in out if p is not None]
    if rr and (cx, cy) == (0.0, 0.0):
        lim = 1.25 * float(np.median(rr))
        out = [p if p is not None and math.hypot(p[0] - cx, p[1] - cy) <= lim
               else None for p in out]
    return out


def render(aid, ob, me, co, H, is_arm, res, outdir):
    # sem bracos: a mao tapa a lateral da coxa e a quina da faixa
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if is_arm[v.index]], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    me.update()
    deps = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(ob, deps)

    me.materials.clear()
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    mat = bpy.data.materials.new("clay")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.72, 0.73, 0.75, 1)
    bsdf.inputs["Roughness"].default_value = 0.55
    bsdf.inputs["Metallic"].default_value = 0.0
    me.materials.append(mat)

    sc = bpy.context.scene
    for nome in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = nome
            break
        except TypeError:
            continue
    else:
        raise SystemExit("ABORTADO: sem EEVEE. Workbench apaga relevo (LICOES 1.12).")
    try:
        sc.eevee.taa_render_samples = 16
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.35, 0.38, 1)
    ld = bpy.data.lights.new("k", type="AREA")
    ld.energy = 900
    ld.size = 2
    lamp = bpy.data.objects.new("k", ld)
    sc.collection.objects.link(lamp)
    cd = bpy.data.cameras.new("c")
    cd.type = "ORTHO"
    cam = bpy.data.objects.new("c", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam

    regioes = [("barra", ["hem_l", "hem_r"]), ("cos", ["cos"])]
    if "faixa_lo" in res["bordas"]:
        regioes.append(("faixa", ["faixa_lo", "faixa_hi"]))
    so = [x for x in a.regioes.split(",") if x]
    vistas = {}
    if so:
        antes = os.path.join(outdir, "proposta.json")
        if os.path.isfile(antes):
            with open(antes, encoding="utf-8") as f:
                vistas = json.load(f).get("vistas", {})
        regioes = [r for r in regioes if r[0] in so]
    z = co[:, 2] / H
    for reg, nomes in regioes:
        bs = [res["bordas"][n] for n in nomes]
        vals = []
        for b in bs:
            vals += b["atual"] + b.get("curva", [])
        zlo, zhi = min(vals), max(vals)
        zc = (zlo + zhi) / 2
        faixa_v = (zhi - zlo) + 0.07
        m = (~is_arm) & (np.abs(z - zc) < faixa_v / 2)
        larg = 2.3 * float(np.abs(co[m, 0]).max()) if m.any() else 0.4 * H
        cd.ortho_scale = max(larg, faixa_v * H * RES_X / RES_Y)
        ow, oh = cd.ortho_scale, cd.ortho_scale * RES_Y / RES_X
        curvas = {}
        for n, b in zip(nomes, bs):
            curvas[n] = {"atual": pontos_3d(bvh, b, "atual", H)}
            if "coef" in b:
                curvas[n]["proposta"] = pontos_3d(bvh, b, "proposta", H)
        vistas[reg] = {}
        for angv in VISTAS:
            r = math.radians(angv)
            zcm = zc * H
            cam.location = (5 * math.sin(r), -5 * math.cos(r), zcm)
            cam.rotation_euler = (math.radians(90), 0, r)
            # A LUZ GIRA COM A CAMERA: e a posicao (-3,-3) da vista de frente
            # rodada de r em torno de Z. ⚠️ O bainha_rasante._posiciona_luz tem
            # o seno com sinal trocado - acerta 0 e 180 graus e poe a lampada
            # ATRAS do corpo em 90 e 270. Achado aqui porque a vista de 60 saiu
            # em contraluz; e a 4.5o pela metade.
            lamp.location = (-3 * math.cos(r) + 3 * math.sin(r),
                             -3 * math.sin(r) - 3 * math.cos(r), zcm - H * 0.02)
            lamp.rotation_euler = (math.radians(100), 0, r + math.radians(-40))
            png = "{}_{:03d}.png".format(reg, angv)
            sc.render.filepath = os.path.join(outdir, png)
            bpy.ops.render.render(write_still=True)
            para_cam = Vector((math.sin(r), -math.cos(r), 0.0))
            direita = np.array([math.cos(r), math.sin(r)])
            px = {}
            for n, cc in curvas.items():
                px[n] = {}
                for chave, pts in cc.items():
                    lst = []
                    for p in pts:
                        if p is None:
                            lst.append(None)
                            continue
                        pv = Vector(p)
                        hit = bvh.ray_cast(pv + para_cam * 0.003, para_cam, 20.0)
                        if hit[0] is not None:
                            lst.append(None)
                            continue
                        u = float(np.dot(direita, p[:2]))
                        x = RES_X / 2 + u / ow * RES_X
                        y = RES_Y / 2 - (p[2] - zcm) / oh * RES_Y
                        lst.append([round(x, 1), round(y, 1)])
                    px[n][chave] = lst
            vistas[reg][png] = px
    return vistas


with open(os.path.join(ROOT, "config", "shorts_map.json"), encoding="utf-8") as _f:
    SMAP = json.load(_f)
_IDS = [x for x in a.ids.split(",") if x]
for _i, _aid in enumerate(_IDS, 1):
    print("[{}/{}]".format(_i, len(_IDS)), end=" ", flush=True)
    # semente POR AVATAR: o resultado nao pode depender da ordem da lista
    uma(_aid, SMAP, np.random.default_rng(sum(map(ord, _aid))))
