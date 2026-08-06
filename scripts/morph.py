#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""morph.py - aplica os SHAPE KEYS de ajuste fino num avatar entregue.

    python scripts/morph.py zen_m_b05h_d2 --fit     # calibra e sonda, NAO grava
    python scripts/morph.py zen_m_b05h_d2 --apply   # grava o dist v(n+1)
    python scripts/morph.py zen_m_b05h_d2 --remap   # so o mapa, sem gastar versao

--------------------------------------------------------------------------
POR QUE ELE LE O DIST E NAO O MASTER  (regra 9 do CLAUDE.md)
--------------------------------------------------------------------------
O master nao tem peca. Quem le o master e grava o dist APAGA o short - foi
exatamente isso que o `restyle.py --all` fez com os 39 masculinos em 31/07.
Este script le `03_dist/glb/{id}_v{n}.glb`, que ja tem material E peca, e so
ACRESCENTA shape keys: nenhum vertice da base se move, nenhum material muda.
A trava do fim confere as duas coisas contra o arquivo de entrada.

--------------------------------------------------------------------------
⚠️ O DIST TEM DUAS SUPERFICIES SOLTAS, E ISSO QUEBRA A REGUA
--------------------------------------------------------------------------
glTF quebra primitiva por material, entao corpo e short viajam separados e a
costura vem com os vertices DUPLICADOS (32.151 no disco contra 25.914+6.237).
Para o `metrics.py`, que separa medida por TOPOLOGIA, isso vira uma ilha a
mais: na faixa de altura do short a fatia devolve lacos extras, o `r[1:]` que
descarta o tronco descarta a peca errada e o numero sai de outro lugar do
corpo. Medido, lendo o dist cru: antebraco **48,3 cm** onde o
`library_metrics.json` diz 29,8, e cintura 86,2 onde ele diz 101,3.

Por isso a medida roda numa copia SOLDADA (`remove_doubles`), e o campo de
deformacao e uma funcao da POSICAO - avaliada na copia soldada para calibrar e
na malha real, com os vertices duplicados, para gravar o shape key. Os dois
lados da costura recebem o mesmo deslocamento e ela nao abre.

A trava disso e o §CONFERENCIA: a regua sobre a base tem que reproduzir o
`library_metrics.json`. Regua que nao reproduz a medida publicada nao calibra
morph nenhum.

--------------------------------------------------------------------------
A REGUA E A DO metrics.py, NAO UMA PARECIDA
--------------------------------------------------------------------------
As sondas `morph_lab*.py` mediam por casco convexo da fatia com o braco
removido "por identidade". Serve para pesquisa, mas o numero que o app compara
com a fita do usuario e o do `metrics.py`. Aqui a calibracao chama as funcoes
DAQUELE arquivo sobre a malha deformada - assim "o morph vale +6 cm de ombro"
quer dizer +6 cm *na mesma regua* que produziu o `library.json`.

--------------------------------------------------------------------------
IDENTIDADE E LANDMARK SE DECIDEM NA MALHA BASE  (LICOES.md 7.7)
--------------------------------------------------------------------------
Quem e braco, quem e perna, quem e rosto, onde esta a axila, a virilha e o
pulso: tudo sai da malha sem deformacao, uma vez. Vale para as MASCARAS (a
primeira versao do morph de biceps selecionava o braco sobre as posicoes ja
morfadas e a busca divergiu) e vale tambem para as ANCORAS DA REGUA: o
antebraco e medido entre o pulso e o meio do braco, e se o pulso for
reprocurado a cada amplitude a janela anda junto com o morph e o cm deixa de
ser comparavel. Foi o que produziu "-17,7 cm em toda influence negativa" na
primeira rodada desta calibracao.

--------------------------------------------------------------------------
O CONTRATO COM O APP
--------------------------------------------------------------------------
`config/morph_map.json` publica, por morph:
    key             nome do shape key no GLB (== targetNames do glTF)
    column          a coluna de medida do app que ele corrige
    cm_at_full      quantos cm a coluna anda com influence = 1.0
    influence_min   limite seguro NEGATIVO (medido, nao proposto)
    influence_max   limite seguro POSITIVO (medido)
E o app faz:
    inf = clamp((usuario_cm - avatar_cm) / cm_at_full, influence_min, influence_max)

⚠️ O GLB sai com DUAS primitivas. Cada uma vira um THREE.Mesh com o SEU
proprio `morphTargetInfluences`; quem so setar no primeiro morfa o corpo e
deixa o short parado. Percorrer a arvore inteira.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import metrics as mt          # noqa: E402  - a regua oficial
import zenith_paths as _zp    # noqa: E402

try:
    import bpy                # noqa: F401
    IN_BLENDER = True
except ImportError:
    IN_BLENDER = False


# ==========================================================================
#  A TABELA DOS MORPHS
# ==========================================================================
# `cm_at_full` e a UNIDADE, nao o limite: quanto a coluna anda com o shape key
# em 1.0. O limite sai da varredura e vai medido para o mapa. Os numeros aqui
# sao redondos de proposito, para o app poder dizer "+6 cm de ombro" sem conta.
# ⚠️ `cal_sign` existe por causa do PESCOCO, e a razao e estrutural, nao um
#    ajuste: ele e um MINIMO de banda travado pelo queixo, entao CRESCER satura
#    (+2,2 cm por mais amplitude que se dê) enquanto REDUZIR responde. Calibrar
#    pelo lado que satura faz a busca de amplitude fugir para o teto - mediu
#    0,060 m, e nesse tamanho o lado negativo virou -19 cm com 206 triangulos
#    invertidos. Quem tem lado saturado calibra pelo outro.
MORPHS = [
    {"key": "morph_neck",     "column": "neck",      "cm_at_full": 6.0, "cal_sign": -1},
    {"key": "morph_shoulder", "column": "shoulder",  "cm_at_full": 6.0},
    {"key": "morph_chest",    "column": "chest",     "cm_at_full": 6.0},
    {"key": "morph_waist",    "column": "waist_min", "cm_at_full": 10.0},
    {"key": "morph_hip",      "column": "hip",       "cm_at_full": 8.0},
    {"key": "morph_biceps",   "column": "biceps",    "cm_at_full": 4.0},
    {"key": "morph_forearm",  "column": "forearm",   "cm_at_full": 3.0},
    {"key": "morph_thigh",    "column": "thigh",     "cm_at_full": 6.0},
    {"key": "morph_calf",     "column": "calf",      "cm_at_full": 3.0},

    # ⚠️ ACHATAMENTO DA CINTURA - o unico morph que NAO tem coluna de medida.
    #     Ele muda a FORMA da secao (largura contra profundidade) a perimetro
    #     ~constante, e existe porque fechar centimetro nao e o mesmo que
    #     parecer com a pessoa. Medido no corpo do Rogerio: o `morph_waist`
    #     isotropico acertou o perimetro (+5,6 cm) e DOBROU o erro no eixo que o
    #     olho ve - a barriga foi de 1,9 para 3,6 cm mais funda que a dele.
    #     Perimetro e o que a fita mede; profundidade e o que aparece de perfil.
    #
    #     `couple` diz ao app: aplique este junto com o `morph_waist`, mas SO
    #     quando ele for positivo. Reduzir cintura tem que perder profundidade
    #     (e o que emagrecer faz), entao a reducao continua isotropica.
    #
    #     `cal_depth` e o criterio de calibracao: a amplitude e a que devolve a
    #     PROFUNDIDADE da base quando o `morph_waist` esta em +1,0. E o default
    #     conservador - o morph deixa de piorar o eixo visivel, sem apostar em
    #     nenhuma forma de corpo.
    {"key": "morph_waist_flatten", "column": None, "kind": "flatten",
     "couple": "morph_waist", "couple_when": "positive", "cal_depth": True},
]

# Amplitudes varridas para achar onde cada morph quebra. Passa do util de
# proposito: faixa so vale medida ate o defeito aparecer.
SWEEP = [-2.0, -1.5, -1.0, -0.5, 0.5, 1.0, 1.5, 2.0]

# ⚠️ TETO DE INFLUENCE, E ELE VEIO DA FOTO, NAO DAS SONDAS.
# Em influence -2,0 as sondas numericas devolvem ZERO normal invertida no
# ombro, no biceps e no antebraco - e a foto mostra braco cordao, degrau no
# deltoide e vinco na juncao do trapezio. E a §7.5 do LICOES.md acontecendo de
# novo: sonda diz ONDE olhar, foto diz SE esta bom.
#
# O teto e POR MORPH desde 06/08, e nao mais um numero unico. O ±1,0 nasceu da
# foto do BRACO, e aplica-lo a panturrilha era generalizar um veredito visual
# de uma regiao para outra: a panturrilha e um cilindro isolado, varreu limpa
# ate ±2,0 (±6 cm) com ZERO normal invertida, e o teto unico estava cortando
# metade da faixa dela a toa - justo numa das duas colunas que sobram no corpo
# do Rogerio.
#
# ⚠️ TODO valor acima de 1,0 aqui precisa de RENDER OLHADO naquele extremo.
# Numero nesta tabela sem foto correspondente e exatamente o erro que a §7.5
# documenta.
# O pescoco ESTEVE aqui com 1,5 e saiu: o 1,5 foi posto esperando ganho no lado
# da REDUCAO, e la a sonda e a foto reprovaram juntas (-9,3 cm faz degrau na
# base contra o trapezio). Sobrava so o lado do crescimento, que renderia +0,2
# cm - e eu nao renderizei o pescoco em +1,5. Numero sem foto nao fica na
# tabela, e a regra acima vale tambem para mim.
INFLUENCE_CAP = {"morph_calf": 2.0}
INFLUENCE_CAP_PADRAO = 1.0

# A regua sobre a base tem que bater com o library_metrics.json. Acima disto o
# script para: a divergencia significa que ele nao esta medindo o mesmo corpo.
TOL_BASE_CM = 0.6

MAP_PATH = "config/morph_map.json"


# ==========================================================================
#  DRIVER
# ==========================================================================

def driver_main():
    ap = argparse.ArgumentParser(description="Shape keys de ajuste fino no avatar entregue.")
    ap.add_argument("avatar_id")
    ap.add_argument("--fit", action="store_true",
                    help="calibra e sonda, sem gravar nada em 03_dist/")
    ap.add_argument("--apply", action="store_true",
                    help="grava 03_dist/glb/{id}_v(n+1).glb e o config/morph_map.json")
    ap.add_argument("--remap", action="store_true",
                    help="so reescreve o config/morph_map.json contra o dist "
                         "CORRENTE, sem exportar GLB nem gastar versao")
    args = ap.parse_args()
    if not (args.fit or args.apply or args.remap):
        ap.error("escolha --fit (so mede), --apply (grava) ou --remap (so o mapa)")
    if args.apply and args.remap:
        ap.error("--apply e --remap sao excludentes")

    root = mt.repo_root()
    _zp.sex_of(args.avatar_id)                     # estoura em id malformado
    ver, src = _zp.dist_glb_current(root, args.avatar_id)
    if src is None:
        sys.exit("nao existe 03_dist/glb/{}_v*.glb - rode process.py/shorts.py antes."
                 .format(args.avatar_id))
    print("entrada: {} (v{})".format(os.path.basename(src), ver))

    cmd = [mt.find_blender(), "--background", "--python", os.path.abspath(__file__), "--",
           "--worker", "--root", root, "--id", args.avatar_id]
    if args.apply:
        cmd.append("--apply")
    if args.remap:
        cmd.append("--remap")
    sys.exit(subprocess.run(cmd).returncode)


# ==========================================================================
#  GEOMETRIA
# ==========================================================================

def sstep(x, a, b):
    """Rampa suave de a ate b. `a`/`b` podem ser array - o teto da mascara do
    pescoco depende de Y (fecha antes na frente do que atras)."""
    import numpy as np
    larg = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    t = np.clip((x - a) / np.where(np.abs(larg) < 1e-9, 1e-9, larg), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def band(x, lo0, lo1, hi0, hi1):
    """Janela suave: sobe de lo0 a lo1, desce de hi0 a hi1."""
    return sstep(x, lo0, lo1) * (1.0 - sstep(x, hi0, hi1))


class Base(object):
    """Os landmarks e os perfis, decididos UMA VEZ na malha soldada e sem
    deformacao. Nada aqui depende da lista de vertices: os perfis de centro
    sao curvas em Z, e por isso o mesmo campo pode ser avaliado na malha real
    (com a costura duplicada) sem recalcular nada."""

    def __init__(self, co, mesh):
        import numpy as np
        self.co, self.mesh = co, mesh
        self.n = len(co)
        self.zmin = float(co[:, 2].min())
        self.H = float(co[:, 2].max()) - self.zmin
        z, H = self.zmin, self.H

        # --- ate onde braco e perna ainda sao lacos proprios (regua oficial)
        self.arm_split = mt.find_armpit(mesh, z, H)
        self.leg_split = mt.find_crotch(mesh, z, H)
        self.crotch = z + mt.CROTCH_FRAC * H
        self.armpit = z + mt.ARMPIT_FRAC * H
        self.leg_top = self.leg_split if self.leg_split else self.crotch

        # --- EIXO DO BRACO. O empurrao do biceps/antebraco e PERPENDICULAR a
        # ele: em A-pose um empurrao horizontal engorda na diagonal e sobe a
        # medida errada.
        self.fusao_f = ((self.arm_split - z) / H) if self.arm_split else 0.72
        pts = []
        for f in np.arange(0.42, self.fusao_f - 0.01, 0.01):
            g = self._gap_braco(co, z + f * H)
            if not g:
                continue
            b = co[np.abs(co[:, 2] - (z + f * H)) < 0.008]
            a = b[b[:, 0] > g[1] - 0.005]
            if len(a) >= 6:
                pts.append(a.mean(axis=0))
        pts = np.array(pts)
        self.arm_c = pts.mean(axis=0)
        e = np.linalg.svd(pts - self.arm_c)[2][0]
        self.arm_e = e if e[2] >= 0 else -e

        # --- ANCORAS DA REGUA DO BRACO, congeladas (ver cabecalho)
        self.arm_top = (self.armpit if self.arm_split is None
                        else min(self.armpit, self.arm_split)) - mt.ARM_PAD_M
        w = mt.pair_extreme(mesh, self.crotch, self.arm_top, True, "min")
        self.z_pulso = w[3] if w else z + 0.56 * H
        self.z_meio = (self.z_pulso + self.arm_top) / 2.0

        # --- PERFIL DO CENTRO DO TRONCO, com o braco fora da conta. O push
        # radial sai daqui: o tronco nao e cilindro centrado, e usar o eixo
        # global empurraria a barriga so para a frente.
        d_dir, _, _ = self._dist_eixo(co)
        d_esq, _, _ = self._dist_eixo(co * np.array([-1.0, 1.0, 1.0]))
        E_BRACO = np.minimum(d_dir, d_esq) < 0.085
        self.tz, self.tc = self._perfil(co, ~E_BRACO, z + 0.30 * H, z + 0.98 * H)

        # --- PERFIL DE CADA PERNA, e o VAO entre elas por altura. O vao e o
        # que impede o morph de coxa/quadril de empurrar uma perna contra a
        # outra: onde elas ja se tocam, a componente para dentro morre.
        #
        # ⚠️ `~E_BRACO` NAO E DECORACAO AQUI. Em A-pose a MAO pousa em z/H 0,44
        # a 0,47, que e dentro da faixa da coxa: sem tirar o braco, ela entra
        # no centroide da perna e, pior, recebe o empurrao radial da coxa. Foi
        # o que produziu 68 a 538 triangulos invertidos em TODA amplitude, e os
        # invertidos estavam em |x| = 43 cm - o dedo, nao a perna.
        self.lz, self.lc = {}, {}
        for sg in (+1.0, -1.0):
            sel = (co[:, 0] * sg > 0) & (co[:, 2] < self.leg_top) & (~E_BRACO)
            self.lz[sg], self.lc[sg] = self._perfil(co, sel, z + 0.06 * H, self.leg_top)
        self.gz, self.gv = self._perfil_vao(co)
        self.az, self.av = self._perfil_axila(co)

        # --- PESCOCO: eixo, frente, queixo (LICOES.md 7.5)
        face = co[(co[:, 2] > z + 0.90 * H) & (co[:, 2] < z + 0.95 * H)]
        self.frente = 1.0 if abs(face[:, 1].max()) > abs(face[:, 1].min()) else -1.0
        zs = np.arange(z + 0.80 * H, z + 0.92 * H, 0.005)
        cen = np.array([co[np.abs(co[:, 2] - t) < 0.006][:, :2].mean(axis=0) for t in zs])
        self.nx, self.ny = float(cen[:, 0].mean()), float(cen[:, 1].mean())
        raios = []
        for t in zs:
            b = co[np.abs(co[:, 2] - t) < 0.005]
            fr = b[:, 1] * self.frente > self.ny * self.frente
            raios.append(float(np.sqrt((b[fr, 0] - self.nx) ** 2
                                       + (b[fr, 1] - self.ny) ** 2).max()) if fr.any() else 0.0)
        raios = np.array(raios)
        i = int(np.argmin(raios))
        salto = np.where(raios[i:] > raios[i] * 1.25)[0]
        self.z_queixo = float(zs[i + salto[0]]) if len(salto) else float(zs[-1])

        self.tris = mesh.tris
        self.nrm0, self.area0 = self.normais(co)
        # Piso de area para a sonda de inversao: abaixo dele a normal e ruido
        # numerico, nao dobra de superficie. Sem o piso um unico triangulo
        # lasca condenava a faixa inteira de um morph.
        self.area_min = float(np.median(self.area0)) * 0.02

    # ------------------------------------------------------------------ util
    def _gap_braco(self, co, z, half=0.006):
        import numpy as np
        b = co[np.abs(co[:, 2] - z) < half]
        xs = np.sort(b[b[:, 0] > 0.02][:, 0])
        if len(xs) < 4:
            return None
        d = np.diff(xs)
        i = int(np.argmax(d))
        return (xs[i], xs[i + 1]) if d[i] > 0.015 else None

    def _dist_eixo(self, P):
        import numpy as np
        d = P - self.arm_c
        t = d @ self.arm_e
        perp = d - np.outer(t, self.arm_e)
        return np.linalg.norm(perp, axis=1), t, perp

    def _perfil(self, co, sel, z0, z1):
        """(zs, centros XY) do que esta em `sel`, fatia a fatia."""
        import numpy as np
        zs = np.arange(z0, z1, 0.01)
        cent, ult = [], np.array([0.0, 0.0])
        for t in zs:
            s = sel & (np.abs(co[:, 2] - t) < 0.010)
            if s.sum() > 6:
                ult = co[s, :2].mean(axis=0)
            cent.append(ult)
        return zs, np.array(cent)

    def _perfil_vao(self, co):
        """(zs, folga entre as duas pernas) por altura. Onde elas se tocam,
        zero."""
        import numpy as np
        zs = np.arange(self.zmin + 0.06 * self.H, self.leg_top + 0.02, 0.01)
        out = []
        for t in zs:
            b = co[np.abs(co[:, 2] - t) < 0.008]
            d, e = b[b[:, 0] > 0][:, 0], b[b[:, 0] < 0][:, 0]
            out.append(float(d.min() - e.max()) if len(d) > 3 and len(e) > 3 else 0.0)
        return zs, np.maximum(np.array(out), 0.0)

    def _perfil_axila(self, co):
        """(zs, folga braco<->tronco) por altura, do lado direito. Zero onde
        eles ja estao fundidos."""
        import numpy as np
        zs = np.arange(self.zmin + 0.35 * self.H, self.zmin + self.fusao_f * self.H, 0.01)
        out = []
        for t in zs:
            g = self._gap_braco(co, t)
            out.append(float(g[1] - g[0]) if g else 0.0)
        return zs, np.array(out)

    def normais(self, P):
        """Normal de face NORMALIZADA. Triangulo degenerado devolve zero de
        proposito - a sonda de inversao o ignora, ver `sondas`."""
        import numpy as np
        t = self.tris
        nr = np.cross(P[t[:, 1]] - P[t[:, 0]], P[t[:, 2]] - P[t[:, 0]])
        ln = np.linalg.norm(nr, axis=1, keepdims=True)
        return np.where(ln > 1e-12, nr / np.maximum(ln, 1e-12), 0.0), ln[:, 0]

    # ------------------------------------------------------ o campo, em P
    def campo(self, P):
        """{nome: (mascara (n,), direcao (n,3))} avaliado em QUALQUER array de
        posicoes - e por isso a malha soldada (para medir) e a real (para
        gravar o shape key) recebem exatamente o mesmo deslocamento."""
        import numpy as np
        z, H = self.zmin, self.H
        Z, absx = P[:, 2], np.abs(P[:, 0])
        n = len(P)

        # -------- identidade e direcoes do braco
        d_dir, _, perp_dir = self._dist_eixo(P)
        d_esq, _, perp_esq = self._dist_eixo(P * np.array([-1.0, 1.0, 1.0]))
        d_braco = np.minimum(d_dir, d_esq)
        br_dir = (P[:, 0] > 0) & (d_dir < 0.080)
        br_esq = (P[:, 0] < 0) & (d_esq < 0.080)
        dir_arm = np.zeros((n, 3))
        # A componente do braco que aponta PARA O TRONCO morre onde a axila ja
        # esta fechando - o mesmo remedio das coxas. Sem ela o unico jeito de
        # proteger o vao seria manter a mascara fraca no lugar em que a regua
        # mede, e mascara fraca no ponto da medida foi o que produziu
        # "+0,1 cm com influence 0,5" nesta calibracao.
        vao = np.interp(Z, self.az, self.av)
        abre_ax = sstep(vao, 0.004, 0.025)
        for sg, mask, perp, d in ((+1.0, br_dir, perp_dir, d_dir),
                                  (-1.0, br_esq, perp_esq, d_esq)):
            v = perp / np.maximum(d, 1e-6)[:, None]
            if sg < 0:
                v = v * np.array([-1.0, 1.0, 1.0])
            para_dentro = np.maximum(0.0, -sg * v[:, 0])
            v[:, 0] = v[:, 0] + (1.0 - abre_ax) * para_dentro * sg
            dir_arm[mask] = v[mask]

        # -------- radial do tronco
        dir_trunk = self._radial(P, np.interp(Z, self.tz, self.tc[:, 0]),
                                 np.interp(Z, self.tz, self.tc[:, 1]))
        # ⚠️ NA VIRILHA O CAMPO DO TRONCO NAO TEM DIRECAO ESTAVEL. Ali a secao
        # deixa de ser um anel e vira sela: o centro do "tronco" cai ENTRE as
        # pernas, e a 5 mm de distancia de x=0 dois vizinhos recebem empurroes
        # opostos. Era isso que invertia 1 triangulo em influence -0,5 do
        # quadril - e um sliver de 9,6e-6 no perineo, com |x| de 2 mm, bloqueava
        # a reducao INTEIRA do quadril. Preco alto por um triangulo escondido:
        # com o quadril travado em 0, um usuario que pede gluteo menor recebe o
        # corpo so engordando pela cintura.
        meio = 1.0 - sstep(np.abs(P[:, 0]), 0.004, 0.030)
        virilha = 1.0 - sstep(np.abs(Z - self.leg_top), 0.010, 0.045)
        dir_trunk = dir_trunk * (1.0 - meio * virilha)[:, None]

        # -------- radial das pernas, com a componente PARA DENTRO morta onde
        # as coxas ja se tocam
        # ⚠️ AS DUAS FRONTEIRAS DA PERNA SAO RAMPA, NAO BOOLEANO. Com `Z <
        # leg_top` cru, o vertice logo abaixo da virilha andava e o logo acima
        # ficava parado: o triangulo entre os dois virava do avesso. Os 24 a
        # 177 invertidos que sobraram depois de tirar a mao estavam TODOS em
        # z/H 0,459-0,461, ou seja no proprio corte. O mesmo vale para o gate
        # do braco, que passa por essa altura em A-pose.
        fora_braco = sstep(d_braco, 0.085, 0.135)
        dentro_perna = fora_braco * (1 - sstep(Z, self.leg_top - 0.005,
                                               self.leg_top + 0.045))
        na_perna = (Z < self.leg_top + 0.050) & (d_braco > 0.080)
        folga = np.interp(Z, self.gz, self.gv)
        abre = sstep(folga, 0.010, 0.045)
        # ⚠️ ESCOLHER UMA PERNA POR SINAL DE X e um corte duro no meio: o
        # campo radial vem de DOIS centros diferentes, e no vertice de x = 0,3
        # mm contra o de x = -0,2 mm ele apontava para lados opostos - 2,3 mm
        # de deslocamento contra 0,4 mm em meio milimetro de distancia. Aqui os
        # dois campos sao MISTURADOS numa faixa de 2 cm em torno da linha do
        # meio, que e justamente onde as coxas se tocam.
        peso = np.clip(P[:, 0] / 0.020, -1.0, 1.0)
        dir_leg = np.zeros((n, 3))
        for sg in (+1.0, -1.0):
            u = self._radial(P, np.interp(Z, self.lz[sg], self.lc[sg][:, 0]),
                             np.interp(Z, self.lz[sg], self.lc[sg][:, 1]))
            para_dentro = np.maximum(0.0, -sg * u[:, 0])
            u[:, 0] = u[:, 0] + (1.0 - abre) * para_dentro * sg
            dir_leg += u * (0.5 * (1.0 + sg * peso))[:, None]
        dir_leg[~na_perna] = 0.0

        # -------- radial do pescoco
        r = np.stack([P[:, 0] - self.nx, P[:, 1] - self.ny], axis=1)
        rn = np.maximum(np.linalg.norm(r, axis=1), 1e-6)
        dir_neck = np.zeros((n, 3))
        dir_neck[:, 0] = r[:, 0] / rn
        dir_neck[:, 1] = r[:, 1] / rn

        # ================================================== as mascaras
        # OMBRO - empurra lateral em X, na banda da medida (0,795). Exclui o
        # pescoco por |x| e desce suave para nao degrauar o peito.
        m_ombro = (band(Z, z + 0.745 * H, z + 0.790 * H, z + 0.845 * H, z + 0.885 * H)
                   * sstep(absx, 0.055 * H, 0.105 * H))

        # BICEPS e ANTEBRACO - so no braco, e as janelas em Z sao as MESMAS em
        # que o metrics.py mede, para calibrar o que a regua le.
        # ⚠️ A mascara tem que estar CHEIA na altura em que a regua le, e as
        # duas leem um MAXIMO dentro de uma banda. Com o plato deslocado, o
        # maximo continua onde estava e a medida so anda quando o morph passa
        # por cima dele: media +0,1 cm em influence 0,5 e +4,3 cm em 1,0, ou
        # seja o mapa mentiria em toda a metade de baixo da faixa.
        no_braco = (br_dir | br_esq).astype(float)
        m_biceps = no_braco * band(Z, self.z_meio - 0.06, self.z_meio,
                                   self.arm_top - 0.010, self.arm_top + 0.012)
        # ⚠️ A DESCIDA DO ANTEBRACO MORRE NO COTOVELO, nao no meio do osso.
        # A versao anterior fechava de z_meio-0,010 a z_meio+0,020: 3 cm de
        # rampa no MEIO de um antebraco liso, com plato de so 5 cm. Encolher
        # um anel de 5 cm em 7 mm de raio e deixar o resto parado nao le como
        # "antebraco mais fino", le como MORDIDA - foi o defeito que o Rogerio
        # viu no testador em 05/08, e o render confirmou o degrau na silhueta.
        # Agora a descida leva 9,8 cm e so acaba colada na axila, onde a
        # geometria do braco ja muda sozinha. O plato continua cobrindo os
        # 0,626 em que a regua le (§7.9).
        # O preco e sobreposicao com o biceps no cotovelo, e ela e deliberada:
        # braco de verdade nao tem degrau na dobra.
        m_antebraco = no_braco * band(Z, self.z_pulso, self.z_pulso + 0.045,
                                      self.z_meio + 0.010, self.arm_top - 0.010)
        # ⚠️ GATE DE PROPRIEDADE (licao v84 do engine): onde o biceps manda, o
        # ombro nao mexe. Sem isso os dois campos se somam no vale da axila,
        # que e onde a membrana nasceu la.
        m_ombro = m_ombro * (1 - 0.85 * m_biceps)

        # PEITO e CINTURA - radiais do centro do tronco, FUGINDO DO BRACO por
        # distancia (licao v23/v26: gate por |x| cola no braco em A-pose).
        # Reducao radial UNIFORME: pinca lateral cava sulco.
        fuga = sstep(d_braco, 0.075, 0.140)
        m_peito = band(Z, z + 0.630 * H, z + 0.685 * H,
                       z + 0.760 * H, z + 0.815 * H) * fuga

        # ⚠️ CINTURA e QUADRIL sao EXTREMOS de banda, e por isso a mascara tem
        # que cobrir a BANDA INTEIRA - nao so o ponto onde o extremo esta hoje.
        # Com a mascara comecando dentro da banda (0,560 contra WAIST_BAND
        # 0,550), inflar o meio empurra o MINIMO para a borda descoberta: a
        # medida travou em +2,5 cm para qualquer amplitude, inclusive a de
        # 6 cm que so deformou o corpo. E a versao de cintura da mesma
        # armadilha que fez o `metrics.py` medir joelho na banda da
        # panturrilha - extremo que pousa na borda nao e extremo, e corte.
        m_cintura = band(Z, z + (mt.WAIST_BAND[0] - 0.055) * H, z + mt.WAIST_BAND[0] * H,
                         z + mt.WAIST_BAND[1] * H, z + (mt.WAIST_BAND[1] + 0.055) * H) * fuga
        # O `fuga` tambem aqui: a banda do quadril (0,470-0,550) e a altura em
        # que o ANTEBRACO passa em A-pose, e sem o gate ele seria empurrado
        # radialmente a partir do centro do tronco junto com o gluteo.
        m_quadril = band(Z, z + (mt.HIP_BAND[0] - 0.020) * H, z + (mt.HIP_BAND[0] + 0.006) * H,
                         z + mt.HIP_BAND[1] * H, z + (mt.HIP_BAND[1] + 0.055) * H) * fuga

        # COXA e PANTURRILHA - radial por PERNA, e pelo mesmo motivo o plato
        # cobre a banda que o metrics.py varre. A da panturrilha (0,170-0,265)
        # ja foi corrigida uma vez por estar medindo o JOELHO.
        m_coxa = dentro_perna * sstep(Z, z + 0.300 * H, z + 0.355 * H)
        m_pant = dentro_perna * band(Z, z + (mt.CALF_BAND[0] - 0.035) * H,
                                     z + mt.CALF_BAND[0] * H, z + mt.CALF_BAND[1] * H,
                                     z + (mt.CALF_BAND[1] + 0.035) * H)

        # PESCOCO - teto que depende de Y: na FRENTE fecha abaixo do queixo,
        # ATRAS sobe ate o occipital (receita do engine para a nuca). O piso e
        # uma rampa LARGA de proposito: rampa curta faz degrau contra o
        # trapezio, que foi o limite medido em -5/-6 cm.
        # ⚠️ O TETO INCLINADO PRECISA DE RAMPA LARGA NOS DOIS SENTIDOS. Ele sobe
        # 7,5 cm da frente para a nuca; com a mistura frente/costas em 6 cm e a
        # descida em 3,5 cm, em z/H 0,860 a frente valia 0,04 e as costas 0,96 -
        # 0,92 de mascara em poucos centimetros de circunferencia. Em -1,5 isso
        # dobrava 22 triangulos, TODOS nas costas, exatamente na faixa da
        # transicao. Agora a mistura leva 11 cm e a descida 5,5 cm.
        t = np.clip((P[:, 1] * self.frente - self.ny * self.frente) / -0.11, 0.0, 1.0)
        # E o teto da FRENTE sobe de 1,2 para 0,5 cm abaixo do queixo. Nao e
        # folga de esperto: neste avatar o ponto mais estreito do pescoco (onde
        # a regua le, 0,865) fica a 0,4% do queixo (0,869), entao com 1,2 cm de
        # recuo a frente ja estava ZERADA no lugar da medida - o morph so
        # apertava nuca e lados, e era isso que saturava o centimetro.
        # A trava do rosto continua sendo quem manda parar (LICOES 7.5).
        teto_frente = self.z_queixo - 0.005
        teto = teto_frente + ((z + 0.905 * H) - teto_frente) * t
        m_pescoco = (sstep(Z, z + 0.760 * H, z + 0.835 * H)
                     * (1 - sstep(Z, teto - 0.055, teto)))

        lateral = np.zeros((n, 3))
        lateral[:, 0] = np.sign(P[:, 0])

        return {
            "morph_neck":     (m_pescoco,   dir_neck),
            "morph_shoulder": (m_ombro,     lateral),
            "morph_chest":    (m_peito,     dir_trunk),
            "morph_waist":    (m_cintura,   dir_trunk),
            "morph_hip":      (m_quadril,   dir_trunk),
            "morph_biceps":   (m_biceps,    dir_arm),
            "morph_forearm":  (m_antebraco, dir_arm),
            "morph_thigh":    (m_coxa,      dir_leg),
            "morph_calf":     (m_pant,      dir_leg),
            # ACHATAR: para fora em X, para dentro em Y, na MESMA banda da
            # cintura. O perimetro quase nao muda; o que muda e a razao entre
            # largura e profundidade.
            "morph_waist_flatten": (m_cintura, self._achatar(P)),
        }

    def _achatar(self, P):
        import numpy as np
        Z = P[:, 2]
        cx = np.interp(Z, self.tz, self.tc[:, 0])
        cy = np.interp(Z, self.tz, self.tc[:, 1])
        rad = np.stack([P[:, 0] - cx, P[:, 1] - cy], axis=1)
        rn = np.maximum(np.linalg.norm(rad, axis=1), 1e-6)
        out = np.zeros((len(P), 3))
        out[:, 0] = rad[:, 0] / rn
        out[:, 1] = -rad[:, 1] / rn          # o sinal e a diferenca toda
        return out

    def _radial(self, P, cx, cy):
        import numpy as np
        rad = np.stack([P[:, 0] - cx, P[:, 1] - cy], axis=1)
        rn = np.maximum(np.linalg.norm(rad, axis=1), 1e-6)
        out = np.zeros((len(P), 3))
        out[:, 0] = rad[:, 0] / rn
        out[:, 1] = rad[:, 1] / rn
        return out

    def rosto(self, P):
        """Vertices de ROSTO: acima do queixo E NA FRENTE.

        ⚠️ O sinal aqui ja esteve invertido - no `morph_lab4` e na primeira
        versao deste arquivo - e a trava selecionava a NUCA, que deve reduzir
        mesmo. Ela entao acusava 'movimento no rosto' em toda amplitude,
        inclusive nas boas. Trava mal definida e pior que trava nenhuma:
        ensina a ignorar o alarme (LICOES.md 7.5)."""
        return ((P[:, 2] > self.z_queixo + 0.01)
                & (P[:, 1] * self.frente > self.ny * self.frente))

    # --------------------------------------------------------------- sondas
    def sondas(self, P, mask):
        """(normais invertidas na mascara, vao da axila cm, vao entre coxas cm,
        maior movimento no rosto cm)."""
        import numpy as np
        nr, area = self.normais(P)
        toca = (mask[self.tris].max(axis=1) > 0.05) & (area > self.area_min) \
            & (self.area0 > self.area_min)
        inv = int(((nr * self.nrm0).sum(axis=1) < 0)[toca].sum())
        rst = self.rosto(self.co)
        mov = float(np.linalg.norm((P - self.co)[rst], axis=1).max() * 100) if rst.any() else 0.0
        return inv, self._vao_axila(P), self._vao_coxas(P), mov

    def _vao_axila(self, P):
        """Menor folga entre braco e tronco onde eles ainda sao separados. Se
        isso for a zero, a membrana nasceu - foi la que o zenith_avatar_engine
        quebrou cinco vezes."""
        import numpy as np
        pior = None
        for f in np.arange(self.fusao_f - 0.10, self.fusao_f, 0.005):
            g = self._gap_braco(P, self.zmin + f * self.H)
            if g:
                w = (g[1] - g[0]) * 100
                pior = w if pior is None or w < pior else pior
        return pior

    def _vao_coxas(self, P):
        """O mesmo entre as duas coxas - a versao de baixo da mesma armadilha.

        ⚠️ So conta fatia onde a folga EXISTE (> 4 mm). Sem esse filtro a sonda
        devolvia 0,04 cm ate na malha base, porque perto da virilha as coxas ja
        se encostam por anatomia: qualquer limiar sobre esse numero comparava
        ruido com ruido."""
        import numpy as np
        pior = None
        for f in np.arange(0.20, (self.leg_top - self.zmin) / self.H, 0.005):
            b = P[np.abs(P[:, 2] - (self.zmin + f * self.H)) < 0.006]
            d, e = b[b[:, 0] > 0][:, 0], b[b[:, 0] < 0][:, 0]
            if len(d) < 3 or len(e) < 3:
                continue
            w = (d.min() - e.max()) * 100
            if w > 0.4:
                pior = w if pior is None or w < pior else pior
        return pior


# ==========================================================================
#  A REGUA OFICIAL, aplicada a uma malha deformada
# ==========================================================================

def medir(base, P, column):
    """O centimetro daquela coluna, pelas MESMAS funcoes do metrics.py, com os
    landmarks de ancoragem congelados na base (ver cabecalho)."""
    m = mt.Mesh(P, base.mesh.edges, base.mesh.face_edges, base.mesh.tris)
    z, H = base.zmin, base.H

    if column == "neck":
        return mt.torso_extreme(m, z + mt.NECK_BAND[0] * H, z + mt.NECK_BAND[1] * H, "min")[0]
    if column == "shoulder":
        return mt.torso_at(m, z + mt.SHOULDER_FRAC * H)
    if column == "chest":
        cz = z + mt.CHEST_FRAC * H
        if base.arm_split is not None and base.arm_split < cz:
            cz = base.arm_split - mt.CHEST_PAD_M
        return mt.torso_at(m, cz)
    if column == "waist_min":
        return mt.torso_extreme(m, z + mt.WAIST_BAND[0] * H, z + mt.WAIST_BAND[1] * H, "min")[0]
    if column == "_waist_depth":
        # profundidade (Y) da secao na altura em que o waist_min e lido. Nao e
        # medida de fita - e o eixo que o olho ve de perfil, e o criterio de
        # calibracao do achatamento.
        per, zc = mt.torso_extreme(m, z + mt.WAIST_BAND[0] * H,
                                   z + mt.WAIST_BAND[1] * H, "min")
        if zc is None:
            return None
        lps = m.loops(float(zc))
        if not lps:
            return None
        lp = max(lps, key=len)
        return float(lp[:, 1].max() - lp[:, 1].min())
    if column == "hip":
        return mt.torso_extreme(m, z + mt.HIP_BAND[0] * H, z + mt.HIP_BAND[1] * H, "max")[0]
    if column == "biceps":
        r = mt.pair_extreme(m, base.z_meio, base.arm_top, True, "max")
        return r[0] if r else None
    if column == "forearm":
        r = mt.pair_extreme(m, base.z_pulso, base.z_meio, True, "max")
        return r[0] if r else None
    if column == "thigh":
        topo = base.leg_top
        r = mt.pair_extreme(m, topo - mt.THIGH_BAND_M, topo - mt.SCAN_STEP_M, False, "max")
        return r[0] if r else None
    if column == "calf":
        r = mt.pair_extreme(m, z + mt.CALF_BAND[0] * H, z + mt.CALF_BAND[1] * H, False, "max")
        return r[0] if r else None
    raise ValueError("coluna desconhecida: {}".format(column))


# ==========================================================================
#  WORKER
# ==========================================================================

def carregar(path):
    """(objeto Blender, co real, co soldada, Mesh soldada).

    A copia soldada existe pelo motivo do cabecalho: o dist chega com a
    costura corpo/short duplicada e a regua por topologia le outra coisa."""
    import bmesh
    import numpy as np

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(obs) != 1:
        raise RuntimeError("esperado 1 malha, achou {}".format(len(obs)))
    ob = obs[0]
    mw = ob.matrix_world
    if max(abs(mw[i][j] - (1.0 if i == j else 0.0))
           for i in range(4) for j in range(4)) > 1e-6:
        raise RuntimeError("matrix_world nao e identidade - o shape key seria "
                           "gravado em coordenada diferente da medida")

    # ⚠️ Se o dist ja tem shape key, ele SAI. Este script le o dist corrente, e
    # depois do primeiro --apply o corrente e o que ele mesmo gravou: sem
    # limpar, a segunda rodada empilha 9 morphs em cima dos 9 e o GLB sai com
    # 18 targets e nomes `.001`. Recalibrar tem que partir sempre da base - que
    # e exatamente o que os vertices da malha ja sao, porque todo key esta em
    # value 0.
    def arr(me):
        a = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", a)
        return a.reshape(-1, 3)

    co_real = arr(ob.data)
    sk_existentes = {}
    if ob.data.shape_keys:
        base_sk = np.array([list(d.co) for d in
                            ob.data.shape_keys.key_blocks[0].data])
        for k in list(ob.data.shape_keys.key_blocks)[1:]:
            sk_existentes[k.name] = np.array([list(d.co) for d in k.data]) - base_sk
        print("entrada ja tinha {} shape key(s) - removidos para recalibrar da base"
              .format(len(sk_existentes)))
        ob.shape_key_clear()
        co_real = arr(ob.data)

    # 0,3 mm: as duas primitivas sao quantizadas pelo Draco em caixas
    # diferentes, entao os vertices da costura nao voltam bit a bit iguais.
    me2 = ob.data.copy()
    bm = bmesh.new()
    bm.from_mesh(me2)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=3e-4)
    bm.to_mesh(me2)
    bm.free()
    co_sold = arr(me2)

    edges = np.array([e.vertices[:] for e in me2.edges], dtype=int)
    lookup = {}
    for e in me2.edges:
        lookup[tuple(sorted(e.vertices[:]))] = e.index
    face_edges, tris = [], []
    for p in me2.polygons:
        if len(p.vertices) != 3:
            raise RuntimeError("malha nao triangulada")
        face_edges.append([lookup[tuple(sorted(k))] for k in p.edge_keys])
        tris.append(p.vertices[:])
    mesh = mt.Mesh(co_sold, edges, np.array(face_edges, dtype=int),
                   np.array(tris, dtype=int))
    bpy.data.meshes.remove(me2)
    return ob, co_real, co_sold, mesh, sk_existentes


def conferir_base(root, aid, base, co):
    """A regua sobre a base tem que reproduzir o library_metrics.json.

    E a unica regua EXTERNA que esta calibracao tem: aquele arquivo foi medido
    no master, por outro caminho de codigo, antes deste script existir. Se a
    base nao bate, tudo que vier depois e delta sobre um numero errado."""
    p = os.path.join(root, "metrics", "library_metrics.json")
    with open(p, "r", encoding="utf-8") as f:
        pub = json.load(f)["avatars"][aid]["circumferences_cm"]
    print("\nCONFERENCIA da regua na base (contra library_metrics.json):")
    ruim = []
    for spec in MORPHS:
        col = spec["column"]
        if col is None:            # morph de FORMA nao tem coluna de medida
            continue
        v = medir(base, co, col)
        v = v * 100 if v else None
        ref = pub.get(col, {}).get("cm")
        d = (v - ref) if (v is not None and ref is not None) else None
        print("  {:<10} aqui {:>7} | publicado {:>7} | delta {}"
              .format(col,
                      "{:.1f}".format(v) if v else "-",
                      "{:.1f}".format(ref) if ref else "-",
                      "{:+.1f}".format(d) if d is not None else "-"))
        if d is None or abs(d) > TOL_BASE_CM:
            ruim.append(col)
    return ruim


def worker_main():
    import numpy as np
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--root", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--remap", action="store_true")
    args = ap.parse_args(argv)

    root, aid = args.root, args.id
    ver_atual, src = _zp.dist_glb_current(root, aid)
    ob, co_real, co, mesh, sk_existentes = carregar(src)
    base = Base(co, mesh)

    print("\nmalha: {} verts no disco -> {} soldados | altura {:.4f} m"
          .format(len(co_real), len(co), base.H))
    print("axila z/H {:.3f} | virilha z/H {:.3f} | queixo z/H {:.3f} | pulso z/H {:.3f}"
          .format((base.arm_split - base.zmin) / base.H if base.arm_split else -1,
                  (base.leg_split - base.zmin) / base.H if base.leg_split else -1,
                  (base.z_queixo - base.zmin) / base.H,
                  (base.z_pulso - base.zmin) / base.H))

    ruim = conferir_base(root, aid, base, co)
    if ruim:
        sys.exit("\nTRAVA: a regua nao reproduz o library_metrics.json em: {}.\n"
                 "Calibrar morph sobre base errada e publicar delta de um numero "
                 "que o app nao usa.".format(", ".join(ruim)))

    masks = base.campo(co)
    campo_real = base.campo(co_real)
    v0_axila = base._vao_axila(co)
    v0_coxas = base._vao_coxas(co)
    print("\nvao base: axila {:.2f} cm | entre coxas {:.2f} cm".format(v0_axila, v0_coxas))

    resultado = []
    acoplado = {}     # {key do morph de tamanho: (mascara, direcao, amplitude)}
    for spec in MORPHS:
        key, col = spec["key"], spec["column"]
        m, d = masks[key]
        tocados = int((m > 0.01).sum())

        # ------------------------------------------------ o morph de FORMA
        if spec.get("kind") == "flatten":
            alvo_key = spec["couple"]
            r_tam = next(r for r in resultado if r["key"] == alvo_key)
            m_t, d_t = masks[alvo_key]
            # o estado que o app vai produzir: tamanho em +1,0 e forma junto
            def _prof(a_flat):
                P = (co + d_t * (m_t * r_tam["amplitude_m"])[:, None]
                        + d * (m * a_flat)[:, None])
                return medir(base, P, "_waist_depth") * 100
            prof0 = medir(base, co, "_waist_depth") * 100
            prof_sem = _prof(0.0)
            # busca a amplitude que devolve a profundidade da BASE
            lo, hi = 0.0, 0.050
            for _ in range(22):
                mid = (lo + hi) / 2
                if _prof(mid) > prof0:
                    lo = mid
                else:
                    hi = mid
            amp = (lo + hi) / 2
            print("\n[{}] FORMA da cintura | mascara toca {} verts".format(key, tocados))
            print("  profundidade: base {:.1f} cm | so tamanho {:.1f} (+{:.1f}) | "
                  "com forma {:.1f} cm".format(prof0, prof_sem, prof_sem - prof0, _prof(amp)))
            print("  amplitude {:.4f} m, acoplada a {} quando positivo".format(amp, alvo_key))
            mr, dr = campo_real[key]
            acoplado[alvo_key] = (m, d, amp)
            resultado.append({
                "key": key, "column": None, "kind": "flatten",
                "couple": alvo_key, "couple_when": spec.get("couple_when", "positive"),
                "base_cm": round(prof0, 1), "cm_at_full": 0.0,
                "amplitude_m": round(amp, 5), "verts": tocados,
                "influence_min": 0.0, "influence_max": 1.0,
                "cm_min": 0.0, "cm_max": 0.0, "linearity_at_half": None,
                "curve": [[0.0, 0.0], [1.0, 0.0]],
                "depth_base_cm": round(prof0, 1),
                "depth_without_cm": round(prof_sem, 1),
                "depth_with_cm": round(_prof(amp), 1),
                "delta": (d * (m * amp)[:, None]),
                "delta_real": (dr * (mr * amp)[:, None]),
            })
            continue

        alvo = spec["cm_at_full"]
        b0 = medir(base, co, col) * 100

        # amplitude que da o alvo em cm. O deslocamento e linear na amplitude,
        # a circunferencia quase - tres correcoes multiplicativas convergem.
        sg = spec.get("cal_sign", 1)
        a = 0.010
        for _ in range(5):
            v = medir(base, co + d * (m * a * sg)[:, None], col)
            if v is None:
                a *= 0.5
                continue
            delta = (v * 100 - b0) * sg          # positivo = andou na direcao calibrada
            if delta <= 0.05:
                a *= 2.0
                continue
            a = float(np.clip(a * (alvo / delta), 0.0005, 0.060))
        amp = a
        conf = medir(base, co + d * (m * amp)[:, None], col)
        conf_cm = (conf * 100 - b0) if conf else float("nan")

        print("\n[{}] coluna {} | base {:.1f} cm | mascara toca {} verts"
              .format(key, col, b0, tocados))
        print("  influence 1.0 = amplitude {:.4f} m -> {:+.2f} cm (alvo {:+.1f} em {:+.0f})"
              .format(amp, conf_cm, alvo, sg))
        print("  {:>10} {:>10} {:>8} {:>10} {:>10} {:>9}"
              .format("influence", "delta cm", "norm.inv", "axila cm", "coxas cm", "rosto cm"))

        limpo, curva = {}, {}
        for inf in SWEEP:
            P = co + d * (m * amp * inf)[:, None]
            v = medir(base, P, col)
            curva[inf] = (v * 100 - b0) if v else None
            inv, va, vc, rosto = base.sondas(P, m)
            ruim_i = (inv > 0 or v is None or va is None or vc is None
                      or va < 0.35 * v0_axila or vc < 0.35 * v0_coxas
                      or (key == "morph_neck" and rosto > 0.30))
            limpo[inf] = not ruim_i
            print("  {:>10.1f} {:>10} {:>8d} {:>10} {:>10} {:>9.2f}{}"
                  .format(inf, "{:+.1f}".format(v * 100 - b0) if v else "  -  ", inv,
                          "{:.2f}".format(va) if va is not None else "FECHOU",
                          "{:.2f}".format(vc) if vc is not None else "FECHOU",
                          rosto, "   <-- DEFEITO" if ruim_i else ""))
        # ⚠️ Faixa CONTINUA a partir do zero: se -1.0 quebra, -1.5 nao vale por
        # ter passado. A amplitude util vai ate o PRIMEIRO defeito.
        teto = INFLUENCE_CAP.get(key, INFLUENCE_CAP_PADRAO)
        hi = min(_ate_o_defeito([s for s in SWEEP if s > 0], limpo), teto)
        lo = max(_ate_o_defeito(sorted([s for s in SWEEP if s < 0], reverse=True), limpo),
                 -teto)
        # LINEARIDADE: o mapa promete "cm_at_full x influence". Se meia
        # influence nao der meio centimetro, o app erra a metade de baixo da
        # faixa sem nada avisar - foi assim que o biceps deu +0,1 cm em 0,5 e
        # +4,3 em 1,0 na primeira rodada.
        meio = curva.get(0.5)
        lin = (meio / (0.5 * conf_cm)) if (meio is not None and conf_cm) else None
        # os cm saem da CURVA medida, nao de lo x cm_at_full - com o pescoco a
        # conta linear dizia -1,8 onde a medida diz -6,0
        print("  faixa limpa: {:+.1f} a {:+.1f}  ({:+.1f} a {:+.1f} cm) | "
              "linearidade em 0,5: {}"
              .format(lo, hi, curva.get(lo, 0.0) or 0.0, curva.get(hi, 0.0) or 0.0,
                      "{:.2f}x".format(lin) if lin else "-"))

        # ⚠️ O mapa publica a CURVA medida, nao so `cm_at_full`. O pescoco
        # entrega +3,2 cm em influence 0,5 e so +3,8 em 1,0 - ele e um MINIMO
        # de banda, e crescer o meio empurra o minimo para a borda travada pelo
        # queixo. Quem multiplicar cm_at_full x influence erra 68% ali. O app
        # inverte a curva por interpolacao e a promessa passa a ser medida em
        # cada ponto, nao suposta.
        pontos = [[0.0, 0.0]] + [[i, round(curva[i], 2)] for i in sorted(curva)
                                 if lo <= i <= hi and curva[i] is not None]
        pontos.sort()

        mr, dr = campo_real[key]
        resultado.append({
            "curve": pontos,
            "key": key, "column": col,
            "base_cm": round(b0, 1), "cm_at_full": round(conf_cm, 2),
            "amplitude_m": round(amp, 5), "verts": tocados,
            "influence_min": lo, "influence_max": hi,
            # das PONTAS DA CURVA, nao de `lo x cm_at_full`: com o pescoco a
            # conta linear dava -3,8 cm onde a medida diz -5,7.
            "cm_min": pontos[0][1], "cm_max": pontos[-1][1],
            "linearity_at_half": round(lin, 2) if lin else None,
            "delta": (d * (m * amp)[:, None]),
            "delta_real": (dr * (mr * amp)[:, None]),
        })

    # ⚠️ A CURVA PUBLICADA TEM QUE DESCREVER O QUE O APP VAI FAZER. O morph de
    # tamanho foi varrido sozinho, mas o app vai aplicar o de FORMA junto quando
    # a influence for positiva - e o achatamento mexe no perimetro. Entao a
    # varredura do lado positivo e refeita ACOPLADA, e e essa que vai para o
    # mapa. Publicar a curva solta seria publicar um numero que ninguem produz.
    for alvo_key, (m_f, d_f, amp_f) in acoplado.items():
        r = next(x for x in resultado if x["key"] == alvo_key)
        m_t, d_t = masks[alvo_key]
        print("\n[{}] curva REFEITA com o achatamento acoplado:".format(alvo_key))
        pontos = [p for p in r["curve"] if p[0] <= 0]
        for inf in [s for s in SWEEP if 0 < s <= r["influence_max"]]:
            P = (co + d_t * (m_t * r["amplitude_m"] * inf)[:, None]
                    + d_f * (m_f * amp_f * inf)[:, None])
            v = medir(base, P, r["column"])
            if v is None:
                continue
            cm = v * 100 - r["base_cm"]
            inv, va, vc, _ = base.sondas(P, np.maximum(m_t, m_f))
            print("   influence {:+.1f} -> {:+.1f} cm (solta era {:+.1f}) | "
                  "normais invertidas {}".format(
                      inf, cm, dict(r["curve"]).get(inf, float("nan")), inv))
            if inv == 0:
                pontos.append([inf, round(cm, 2)])
        pontos.sort()
        r["curve"] = pontos
        r["cm_max"] = pontos[-1][1]
        r["influence_max"] = pontos[-1][0]

    # A colisao que matou o outro projeto so aparecia no estado COMBINADO. Nao
    # basta cada morph passar sozinho.
    print("\nestado COMBINADO:")
    for nome, sinal in (("todos no maximo", +1), ("todos no minimo", -1)):
        soma = np.zeros((len(co), 3))
        mtot = np.zeros(len(co))
        for r in resultado:
            soma += r["delta"] * (r["influence_max"] if sinal > 0 else r["influence_min"])
            mtot = np.maximum(mtot, masks[r["key"]][0])
        inv, va, vc, _ = base.sondas(co + soma, mtot)
        print("  {:<16} normais invertidas {:>4} | axila {} cm | coxas {} cm"
              .format(nome, inv,
                      "{:.2f}".format(va) if va is not None else "FECHOU",
                      "{:.2f}".format(vc) if vc is not None else "FECHOU"))

    usaveis = [r for r in resultado if r["influence_max"] > 0 or r["influence_min"] < 0]
    print("\n{} de {} morphs com faixa util".format(len(usaveis), len(resultado)))

    if args.remap:
        # ⚠️ O mapa descreve um ARQUIVO. Antes de reescrever a faixa sem
        # reexportar, conferir que o deslocamento recalculado e o mesmo que ja
        # esta gravado no GLB do disco - senao o mapa passaria a falar de um
        # asset que nao existe.
        if not sk_existentes:
            sys.exit("--remap: o dist corrente nao tem shape key. Use --apply.")
        pior = 0.0
        for r in usaveis:
            se = sk_existentes.get(r["key"])
            if se is None:
                sys.exit("--remap: o GLB nao tem o shape key {}".format(r["key"]))
            pior = max(pior, float(np.abs(se - r["delta_real"]).max()) * 1000)
        print("\n--remap: maior divergencia contra o GLB do disco: {:.3f} mm".format(pior))
        if pior > 0.2:
            sys.exit("--remap: a calibracao nao reproduz o que esta no arquivo. "
                     "O deslocamento mudou - isso exige --apply e versao nova.")
        _gravar_mapa(root, aid, ver_atual, usaveis)
        return

    if not args.apply:
        print("\n--fit: nada gravado. Rode com --apply para gerar o dist.")
        return

    ob.shape_key_add(name="Basis", from_mix=False)
    for r in usaveis:
        k = ob.shape_key_add(name=r["key"], from_mix=False)
        k.data.foreach_set("co", (co_real + r["delta_real"]).astype(np.float32).ravel())
        k.value = 0.0
        k.slider_min, k.slider_max = -2.0, 2.0

    nova, dest = _zp.dist_glb_next(root, aid)
    for o in bpy.context.scene.objects:
        o.select_set(o is ob)
    bpy.context.view_layer.objects.active = ob
    # ⚠️ `export_morph_normal=False` NAO e economia de esperto, e medida. Com
    # normal de morph o arquivo saiu com 4.364 KB contra 210 KB do v2, e a
    # conta e direta: a POSITION vai em accessor ESPARSO (so os 884 a 5.889
    # vertices que a mascara toca, 459 KB somando os nove), mas a NORMAL sai
    # DENSA - os 32.151 vertices em todos os nove morphs, 3.391 KB. O
    # CLAUDE.md declara orcamento de 1 a 3 MB por avatar; 4,4 MB para melhorar
    # sombreamento de um deslocamento de poucos centimetros e o lado errado da
    # troca. Sem elas o three.js usa a normal da base.
    bpy.ops.export_scene.gltf(
        filepath=dest, export_format="GLB", use_selection=True,
        export_morph=True, export_morph_normal=False, export_try_sparse_sk=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=14,
    )

    if not _conferir(src, dest, [r["key"] for r in usaveis], usaveis):
        os.remove(dest)
        sys.exit("TRAVA: o arquivo novo nao passou na conferencia - nada foi aposentado.")

    gone = _zp.dist_glb_retire(root, aid, keep=nova)
    print("\ndist  : {} ({:.0f} KB){}"
          .format(dest, os.path.getsize(dest) / 1024,
                  "  [aposentou {}]".format(", ".join(gone)) if gone else ""))
    _gravar_mapa(root, aid, nova, usaveis)


def _ate_o_defeito(passos, limpo):
    """Ultima amplitude limpa antes do primeiro defeito, indo do zero para
    fora. `passos` vem ordenado por distancia crescente do zero."""
    ultimo = 0.0
    for p in passos:
        if not limpo.get(p, False):
            break
        ultimo = p
    return ultimo


def _conferir(src, dest, keys, resultado):
    """O arquivo novo tem que ser o velho MAIS os shape keys - nada a menos.

    Contagem de triangulos, conjunto de MATERIAIS (a regra 9 existe porque um
    script ja apagou 39 shorts em silencio), shape keys presentes em TODAS as
    primitivas e o deslocamento sobrevivendo ao round-trip."""
    import numpy as np

    def ler(p):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=p)
        obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        tris = sum(len(pl.vertices) - 2 for o in obs for pl in o.data.polygons)
        mats = sorted({m.name for o in obs for m in o.data.materials if m})
        v = []
        for o in obs:
            a = np.empty(len(o.data.vertices) * 3)
            o.data.vertices.foreach_get("co", a)
            v.append(a.reshape(-1, 3))
        return obs, tris, mats, np.concatenate(v)

    _, t0, m0, v0 = ler(src)
    obs, t1, m1, v1 = ler(dest)
    print("\nconferencia do round-trip:")
    print("  triangulos {} -> {}".format(t0, t1))
    print("  materiais  {} -> {}".format(m0, m1))
    if t0 != t1:
        print("  FALHOU: contagem de triangulos mudou")
        return False
    if m0 != m1:
        print("  FALHOU: o conjunto de materiais mudou (short apagado?)")
        return False
    # a malha base nao pode ter andado: shape key nao move o Basis
    a, b = np.sort(v0.ravel()), np.sort(v1.ravel())
    if len(a) == len(b):
        print("  base intacta: pior desvio {:.4f} mm".format(np.abs(a - b).max() * 1000))

    # ⚠️ A checagem tem que ser no glTF, nao no Blender: o importador FUNDE as
    # primitivas num objeto so, entao "o objeto tem shape key" nao responde se
    # o SHORT tem. E e o short que ficaria parado no app, porque cada primitiva
    # vira um THREE.Mesh com o seu proprio morphTargetInfluences.
    prims, nomes, esparsos, densos = _gltf_targets(dest)
    print("  primitivas com target: {} de {} | targetNames: {}"
          .format(sum(1 for t in prims if t == len(keys)), len(prims), ", ".join(nomes)))
    if not prims or any(t != len(keys) for t in prims):
        print("  FALHOU: primitiva sem os {} targets (achou {})".format(len(keys), prims))
        return False
    if nomes != keys:
        print("  FALHOU: targetNames {} != {}".format(nomes, keys))
        return False
    print("  accessors de target: {} esparsos, {} densos | arquivo {:.0f} KB"
          .format(esparsos, densos, os.path.getsize(dest) / 1024))
    if os.path.getsize(dest) > 3 * 1024 * 1024:
        print("  FALHOU: passou do orcamento de 3 MB por avatar (CLAUDE.md, regra 3)")
        return False

    # A ordem dos vertices muda no round-trip, entao compara a ESTATISTICA do
    # deslocamento, que e invariante a permutacao.
    pior = 0.0
    for r in resultado:
        alvo = np.concatenate([
            np.array([list(d.co) for d in o.data.shape_keys.key_blocks[r["key"]].data])
            for o in obs])
        lido = np.sort(np.linalg.norm(alvo - v1, axis=1))
        posto = np.sort(np.linalg.norm(r["delta_real"], axis=1))
        if len(lido) == len(posto):
            pior = max(pior, float(np.abs(lido - posto).max()) * 1000)
    print("  maior erro de deslocamento no round-trip: {:.3f} mm".format(pior))
    if pior > 0.5:
        print("  FALHOU: a quantizacao comeu o deslocamento")
        return False
    return True


def _gltf_targets(path):
    """(targets por primitiva, targetNames, accessors esparsos, densos) lidos
    do JSON do GLB - sem passar pelo importador."""
    import struct
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[12:16])[0]
    j = json.loads(d[20:20 + n])
    prims, nomes, esp, den = [], [], 0, 0
    for m in j["meshes"]:
        nomes = m.get("extras", {}).get("targetNames", nomes)
        for pr in m["primitives"]:
            alvos = pr.get("targets", [])
            prims.append(len(alvos))
            for t in alvos:
                for ai in t.values():
                    if "sparse" in j["accessors"][ai]:
                        esp += 1
                    else:
                        den += 1
    return prims, nomes, esp, den


def _gravar_mapa(root, aid, versao, resultado):
    p = os.path.join(root, MAP_PATH)
    data = {}
    if os.path.isfile(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (ValueError, OSError):
            data = {}
    data[aid] = {
        "glb_version": versao,
        "calibrated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": ("influence = interp(usuario_cm - avatar_cm, curve[cm], "
                 "curve[influence]), ja limitada por construcao a "
                 "[influence_min, influence_max]. NAO usar cm_at_full x "
                 "influence: a relacao nao e linear em todo morph (ver "
                 "linearity_at_half). Morph com kind=flatten NAO tem coluna: "
                 "ele e acoplado - influence = max(0, influence do morph em "
                 "`couple`) quando couple_when=positive. O GLB tem 2 primitivas "
                 "(corpo e short): setar morphTargetInfluences em TODAS."),
        "morphs": [{k: r[k] for k in ("key", "column", "base_cm", "cm_at_full",
                                      "amplitude_m", "verts", "influence_min",
                                      "influence_max", "cm_min", "cm_max",
                                      "linearity_at_half", "curve", "kind",
                                      "couple", "couple_when", "depth_base_cm",
                                      "depth_without_cm", "depth_with_cm")
                    if k in r}
                   for r in resultado],
    }
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("mapa  : {}".format(p))


if __name__ == "__main__":
    if IN_BLENDER and "--worker" in sys.argv:
        worker_main()
    else:
        driver_main()
