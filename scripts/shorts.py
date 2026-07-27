#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shorts.py - pinta o short de PRETO em cima do corpo titanio, um avatar por vez.

    python scripts/shorts.py --fit zen_m_b05_d3     # detecta, grava proposta, renderiza QA
    python scripts/shorts.py --fit --all
    python scripts/shorts.py --apply zen_m_b05_d3   # regrava 03_dist/glb/ com 2 materiais
    python scripts/shorts.py --apply --all
    python scripts/shorts.py --render zen_m_b05_d3  # so o QA, sem gravar dist

--------------------------------------------------------------------------
PORQUE A PRIMEIRA TENTATIVA FALHOU, E O QUE MUDA AQUI
--------------------------------------------------------------------------
O `process.py` segmentava o short projetando a IMAGEM FRONTAL de referencia
sobre a malha e chamando de short todo pixel escuro (SHORTS_LUMA_MAX), com
uma faixa de altura fixa como guarda-costas. Isso tem tres furos, e os tres
aparecem justamente nos avatares pesados:

  1. a projecao frontal nao sabe o que e frente e o que e costas - qualquer
     sombra escura nas costas virava short;
  2. a faixa de altura fixa (0.35-0.65 da altura) pressupoe proporcao
     constante, e a biblioteca vai de IMC 16 a 148: no b12_d1 o short vive
     numa faixa completamente diferente da do b02_d1;
  3. num corpo obeso a BARRIGA CAI POR CIMA do cos. O short deixa de comecar
     numa linha horizontal e passa a comecar embaixo da prega - que e uma
     curva, nao um plano. Nenhum limiar de altura descreve isso.

Aqui a fonte da verdade passa a ser a PROPRIA MALHA. Em 60k a bainha e o cos
existem como geometria: sao degraus de tecido, com vinco concavo do lado do
corpo. E o mesmo relevo que o Rogerio viu aparecer quando a malha subiu de
18k para 60k. Ou seja, o short ja estava modelado - faltava le-lo.

--------------------------------------------------------------------------
COMO O VINCO E SEPARADO DO MUSCULO
--------------------------------------------------------------------------
Concavidade sozinha nao serve: gomo abdominal, sulco do quadriceps e prega
de gordura sao todos concavos, e num corpo d3 sao mais fundos que a bainha.

O que distingue a bainha e o cos e a TOPOLOGIA, nao a profundidade: eles dao
a VOLTA no membro. Um sulco de musculo cobre um arco; uma bainha fecha o
circulo. Entao a pontuacao nao e "quao fundo", e sim "quanto do perimetro
esta vincado nesta altura" (`ring_score`).

Para isso cada fatia horizontal e resolvida na geometria dela mesma: a fatia
e separada em componentes (duas = duas pernas, uma = tronco), e o azimute e
medido em volta do centroide de CADA componente. Sem isso a perna esquerda e
a direita se misturam no mesmo azimute e o anel some no ruido.

De quebra a contagem de componentes entrega o VIRILHA de graca: e a maior
altura em que a fatia ainda se parte em duas.

--------------------------------------------------------------------------
O MODELO DA REGIAO, E PORQUE ELE E ASSIM
--------------------------------------------------------------------------
    short = (z >= bainha_da_perna) E (z <= cos(azimute))

O cos e uma FUNCAO DO AZIMUTE (`waist_by_bin`), nao um numero: e isso que
acompanha a prega da barriga caindo na frente e subindo nos lados. A bainha
e um numero por perna, porque bainha de short de compressao e um corte
horizontal mesmo - e dois numeros, nao um, porque a pose das folhas nao e
perfeitamente simetrica.

Acima da virilha o teste da bainha e satisfeito de graca (z ja e maior que
ela), entao nao ha caso especial para o tronco e nao ha costura entre as
duas regras.

--------------------------------------------------------------------------
O MAPA E O PRODUTO, NAO O DETECTOR
--------------------------------------------------------------------------
`config/shorts_map.json` guarda os numeros de cada avatar. O `--fit` PROPOE;
quem decide e o olho, avatar por avatar, no render de QA. Qualquer campo
escrito a mao com "source": "manual" e preservado por um `--fit` posterior -
so proposta automatica e sobrescrita.

Isso e deliberado: 39 corpos que vao de esqueletico a obesidade III nao tem
um detector unico que acerte todos, e fingir que tem foi exatamente o erro
da primeira tentativa. O detector existe para transformar 39 trabalhos
manuais em ~5.

Nada aqui toca 02_master/ (regra 7 do CLAUDE.md): igual ao restyle.py, le o
master e regrava so 03_dist/glb/.
"""

import argparse
import glob
import json
import os
import subprocess
import sys

BG_HEX = "#0D0D12"

# --- parametros do detector -------------------------------------------------
Z_BINS        = 240      # fatias horizontais sobre a altura toda
AZ_BINS       = 16       # setores de azimute por componente de fatia
CURV_SMOOTH   = 3        # passadas de suavizacao da concavidade (mata ruido de decimacao)
RING_QUANTILE = 0.35     # quantil sobre os setores de azimute (ver w_ring_map)
RING_SMOOTH   = 2        # suavizacao do perfil de ring_score em z
WAIST_AZ_BINS = 24       # resolucao azimutal do cos
WAIST_WINDOW_ZH = 0.10   # quanto um setor do cos pode se afastar do anel (fracao da altura)

# --- janelas de busca, ancoradas na VIRILHA e calibradas pela biblioteca -----
# A virilha e o unico marco anatomico que acompanha a distorcao de proporcao de
# um corpo de IMC 148. Distancia em fracao da altura, medida nos avatares que a
# primeira rodada acertou (n=33):
#
#   bainha abaixo da virilha : 0.024 a 0.045   -> janela 0.015 a 0.065
#   pico do cos acima dela   : 0.103 a 0.155   -> janela 0.090 a 0.170
#
# Os 6 que erraram caiam FORA dessas faixas e sem sobreposicao com elas (bainha
# em +0.001..+0.007 grudada na virilha, ou +0.095 no joelho; cos em
# +0.037..+0.051). Ou seja: a serie separa certo de errado sozinha, e a janela
# so precisa cortar no vazio entre os dois grupos.
HEM_BELOW_CROTCH   = (0.015, 0.065)
WAIST_ABOVE_CROTCH = (0.090, 0.170)


def repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def map_path(root):
    return os.path.join(root, "config", "shorts_map.json")


def load_map(root):
    p = map_path(root)
    if not os.path.isfile(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save_map(root, data):
    p = map_path(root)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def _die(msg, code=2):
    sys.stderr.write("\n[ERRO] " + msg + "\n")
    sys.exit(code)


def find_blender():
    import shutil
    env = os.environ.get("BLENDER")
    if env:
        if os.path.isfile(env):
            return env
        _die("A variavel BLENDER aponta para arquivo inexistente:\n  {}".format(env))
    onpath = shutil.which("blender")
    if onpath:
        return onpath
    candidates = []
    for base in (r"C:\Program Files\Blender Foundation",
                 r"C:\Program Files (x86)\Blender Foundation"):
        candidates += glob.glob(os.path.join(base, "Blender *", "blender.exe"))
    candidates += glob.glob("/Applications/Blender*.app/Contents/MacOS/Blender")
    candidates += ["/usr/bin/blender", "/usr/local/bin/blender", "/snap/bin/blender"]
    existing = sorted(c for c in candidates if os.path.isfile(c))
    if existing:
        return existing[-1]
    _die("Blender nao encontrado. Defina a variavel BLENDER apontando para o executavel.")


def discover_ids(root):
    """Ordem = measured_bmi do library.json, nao alfabetica. Vizinhos de corpo
    ficam lado a lado, que e como o QA do short se julga (o short do IMC 34 tem
    que parecer o mesmo do IMC 35). Sem indice, cai para alfabetica."""
    masters = {os.path.basename(p)[: -len("_master.glb")]
               for p in glob.glob(os.path.join(root, "02_master", "*_master.glb"))}
    lib = os.path.join(root, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            data = json.load(f)
        ordered = [a["id"] for a in sorted(data.get("avatars", []),
                                           key=lambda a: a.get("measured_bmi", 0))]
        out = [i for i in ordered if i in masters]
        out += sorted(masters - set(out))
        return out
    return sorted(masters)


def composite_previews(paths, bg_hex):
    from PIL import Image
    bg = tuple(int(bg_hex.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    for p in paths:
        im = Image.open(p).convert("RGBA")
        flat = Image.new("RGBA", im.size, bg)
        flat.alpha_composite(im)
        flat.convert("RGB").save(p)


def report(root):
    """Tabela de coerencia ANATOMICA do mapa. Nao abre o Blender: le so o
    shorts_map.json, entao roda em um piscar e da para conferir a cada mudanca.

    Foi este relatorio - e nao a folha de contato - que achou os 6 avatares
    errados da primeira rodada. O motivo e que short se julga na SERIE: um
    short isolado quase sempre parece plausivel, mas 'bainha 9,5% da altura
    abaixo da virilha' salta aos olhos quando os outros 33 estao em 2,4-4,5%.
    Numa biblioteca que vai de IMC 16 a 148 nao existe altura absoluta que
    signifique a mesma coisa nos dois extremos; ancorar na virilha, sim."""
    smap = load_map(root)
    if not smap:
        print("mapa vazio - rode --fit antes.")
        return 1

    bmi = {}
    lib = os.path.join(root, "library.json")
    if os.path.isfile(lib):
        with open(lib, "r", encoding="utf-8") as f:
            bmi = {a["id"]: a.get("measured_bmi", 0) for a in json.load(f)["avatars"]}

    def _one(v):
        return v[0] if isinstance(v, (list, tuple)) else v

    print("{:<15} {:>6}  {:>7} {:>7} {:>8}  {:>7} {:>8}  {}".format(
        "id", "imc", "virilha", "bainha", "v-b", "cos-topo", "topo-v", "obs"))
    print("-" * 88)
    fora = []
    for aid in sorted(smap, key=lambda k: bmi.get(k, 0)):
        e = smap[aid]
        c = e.get("diag", {}).get("crotch_zh")
        if c is None:
            continue
        hem = _one(e["hem_l_zh"])
        w = e["waist_zh"]
        wmax = max(w) if isinstance(w, (list, tuple)) else w
        gap, rise = c - hem, wmax - c
        obs = []
        if not (HEM_BELOW_CROTCH[0] <= gap <= HEM_BELOW_CROTCH[1]):
            obs.append("BAINHA")
        if not (WAIST_ABOVE_CROTCH[0] <= rise <= WAIST_ABOVE_CROTCH[1] + 0.06):
            obs.append("COS")
        if e.get("islands", 1) > 1:
            obs.append("{}ILHAS".format(e["islands"]))
        if obs:
            fora.append(aid)
        print("{:<15} {:>6.1f}  {:>7.3f} {:>7.3f} {:>+8.3f}  {:>7.3f} {:>+8.3f}  {} {}".format(
            aid, bmi.get(aid, 0), c, hem, gap, wmax, rise,
            " ".join(obs), "<<" if obs else ""))
    print("-" * 88)
    print("faixas da serie: v-b {} .. {}   topo-v {} .. {}".format(*HEM_BELOW_CROTCH,
                                                                  *WAIST_ABOVE_CROTCH))
    print("{}/{} dentro da faixa".format(len(smap) - len(fora), len(smap)))
    if fora:
        print("conferir: {}".format(", ".join(fora)))
    return 0


def contact_sheet(root, ids, out_path):
    """Folha de contato das frentes: o short so se julga na SERIE. Um short
    isolado quase sempre parece plausivel; o que denuncia erro e o vizinho de
    IMC ao lado com a bainha noutra altura."""
    from PIL import Image
    tiles = []
    for aid in ids:
        p = os.path.join(root, "qa", "shorts", aid, "0_frente.png")
        if os.path.isfile(p):
            tiles.append((aid, p))
    if not tiles:
        return None
    cols = 8
    tw, th = 200, 290
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (13, 13, 18))
    for i, (aid, p) in enumerate(tiles):
        im = Image.open(p).convert("RGB")
        im.thumbnail((tw, th - 14))
        x = (i % cols) * tw + (tw - im.width) // 2
        y = (i // cols) * th
        sheet.paste(im, (x, y))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path)
    return out_path


# ============================================================================
# DRIVER
# ============================================================================

def driver_main():
    ap = argparse.ArgumentParser(
        description="Segmenta e pinta o short dos avatares Zenith, um a um.")
    ap.add_argument("id", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--fit", action="store_true",
                    help="detecta a regiao, grava a proposta no mapa e renderiza QA")
    ap.add_argument("--apply", action="store_true",
                    help="regrava 03_dist/glb/ com corpo + short")
    ap.add_argument("--render", action="store_true",
                    help="so o render de QA, a partir do que ja esta no mapa")
    ap.add_argument("--check", action="store_true",
                    help="so as travas (regiao conexa), sem render - varredura rapida")
    ap.add_argument("--refit", action="store_true",
                    help="com --fit, sobrescreve tambem entradas marcadas manual")
    ap.add_argument("--sheet", action="store_true",
                    help="monta a folha de contato a partir dos QA existentes")
    ap.add_argument("--report", action="store_true",
                    help="tabela de coerencia anatomica do mapa (instantanea)")
    args = ap.parse_args()

    root = repo_root()

    if args.report:
        return report(root)

    if args.sheet:
        out = contact_sheet(root, discover_ids(root),
                            os.path.join(root, "qa", "shorts", "_contato.png"))
        print("folha de contato: {}".format(os.path.relpath(out, root) if out else "nada a montar"))
        return 0

    modes = [m for m in ("fit", "apply", "render", "check") if getattr(args, m)]
    if len(modes) != 1:
        _die("Escolha exatamente um de --fit / --apply / --render / --check.")
    mode = modes[0]

    if args.all and not args.id:
        ids = discover_ids(root)
    elif args.id and not args.all:
        ids = list(args.id)
    else:
        _die("Informe ao menos um id OU --all.")

    blender = find_blender()
    smap = load_map(root)

    print("Blender : {}".format(blender))
    print("Modo    : {}".format(mode))
    print("IDs     : {}".format(len(ids)))
    print("-" * 74)

    failures = []
    for aid in ids:
        master = os.path.join(root, "02_master", aid + "_master.glb")
        if not os.path.isfile(master):
            print("[SKIP] {}: sem master".format(aid))
            failures.append(aid)
            continue
        entry = smap.get(aid)
        if mode == "fit" and entry and entry.get("source") == "manual" and not args.refit:
            print("[keep] {}: manual, preservado (use --refit para sobrescrever)".format(aid))
            mode_i = "render"
        else:
            mode_i = mode
        if mode_i in ("apply", "render", "check") and not entry:
            print("[SKIP] {}: sem entrada no mapa - rode --fit antes".format(aid))
            failures.append(aid)
            continue

        cmd = [blender, "--background", "--python", os.path.abspath(__file__), "--",
               "--worker", "--mode", mode_i, "--id", aid, "--root", root]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.stdout.decode("utf-8", "replace")
        if proc.returncode != 0:
            print("[FAIL] {} (codigo {})".format(aid, proc.returncode))
            for line in out.splitlines()[-25:]:
                print("       | " + line)
            failures.append(aid)
            continue

        # O Blender sai com codigo 0 mesmo quando o script levanta excecao, entao
        # returncode NAO e prova de sucesso - um worker que estourou ja foi
        # reportado como [ok] aqui. A prova e a linha RESULT.
        for line in out.splitlines():
            if line.startswith("RESULT "):
                res = json.loads(line[len("RESULT "):])
                if mode_i == "fit":
                    res["source"] = "auto"
                    smap[aid] = res
                    save_map(root, smap)
                print("[ok]   {}".format(res.get("summary", aid)))
                break
        else:
            print("[FAIL] {}: worker terminou sem RESULT".format(aid))
            for line in out.splitlines()[-15:]:
                print("       | " + line)
            failures.append(aid)

        look = os.path.join(root, "qa", "shorts", aid)
        pngs = sorted(glob.glob(os.path.join(look, "*.png")))
        if pngs:
            composite_previews(pngs, BG_HEX)

    print("-" * 74)
    print("{}/{} ok".format(len(ids) - len(failures), len(ids)))
    if len(ids) > 1:
        sheet = contact_sheet(root, ids, os.path.join(root, "qa", "shorts", "_contato.png"))
        if sheet:
            print("folha de contato: {}".format(os.path.relpath(sheet, root)))
    if failures:
        print("falharam: {}".format(", ".join(failures)))
        return 1
    return 0


# ============================================================================
# WORKER (dentro do Blender)
# ============================================================================

def w_curvature(me, np, passes=None):
    """Concavidade por vertice: media de dot(normalize(u-v), n) no 1-ring.
    >0 = vizinhos acima do plano tangente = vale. Suavizada, porque a 60k a
    decimacao deixa um ruido de ~5 graus por aresta que abafa a bainha."""
    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)
    nor = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("normal", nor)
    nor = nor.reshape(n, 3)

    ei = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ei)
    ei = ei.reshape(-1, 2)
    a, b = ei[:, 0], ei[:, 1]

    d = co[b] - co[a]
    L = np.linalg.norm(d, axis=1)
    L[L == 0] = 1e-9
    dn = d / L[:, None]

    acc = np.zeros(n)
    cnt = np.zeros(n)
    np.add.at(acc, a, np.einsum("ij,ij->i", dn, nor[a]))
    np.add.at(cnt, a, 1.0)
    np.add.at(acc, b, np.einsum("ij,ij->i", -dn, nor[b]))
    np.add.at(cnt, b, 1.0)
    cnt[cnt == 0] = 1.0
    k = acc / cnt

    for _ in range(CURV_SMOOTH if passes is None else passes):
        s = np.zeros(n)
        c = np.zeros(n)
        np.add.at(s, a, k[b])
        np.add.at(c, a, 1.0)
        np.add.at(s, b, k[a])
        np.add.at(c, b, 1.0)
        c[c == 0] = 1.0
        k = 0.5 * k + 0.5 * (s / c)
    return k, co


def w_adjacency(me, np):
    """CSR de vizinhanca de vertices, a partir das arestas da malha."""
    n = len(me.vertices)
    ei = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ei)
    ei = ei.reshape(-1, 2)
    src = np.concatenate([ei[:, 0], ei[:, 1]])
    dst = np.concatenate([ei[:, 1], ei[:, 0]])
    o = np.argsort(src, kind="stable")
    src, dst = src[o], dst[o]
    start = np.searchsorted(src, np.arange(n + 1))
    return start, dst


def w_limbs(me, np, co, H):
    """Acha VIRILHA e BRACOS pela CONEXAO da malha, nao por limiar de altura.

    Porque nao por altura: a primeira versao procurava o vao entre as pernas
    numa fatia horizontal e achou 0.81 da altura - o vao que ela viu era entre
    o BRACO e o tronco. Em A-pose nao existe altura em que a fatia contenha so
    as pernas: na altura da coxa a fatia tem duas coxas E duas maos.

    O que separa mao de coxa nao e distancia no espaco, e CONEXAO na superficie.
    Entao varre-se a malha de baixo para cima com union-find: cada minimo local
    abre uma componente e cada fusao e um evento. Anatomicamente os eventos
    grandes saem em ordem fixa - os dois pes sao os pontos mais baixos, as duas
    pernas se fundem na VIRILHA, e mais acima cada braco (que comeca na ponta
    dos dedos) se funde no tronco na AXILA.

    Devolve (crotch_z, leg_id, is_arm). leg_id: 0/1 por perna abaixo da
    virilha, -1 fora. is_arm cobre braco+mao ate a axila."""
    n = len(co)
    z = co[:, 2]
    start, dst = w_adjacency(me, np)

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

    members = {}
    events = []                      # (z, membros_menores, membros_maiores)
    sig = max(200, int(0.015 * n))   # fusao "significativa"

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
                events.append((float(z[v]), list(mb), list(ma)))
            parent[rb] = ra
            ma.extend(mb)
            del members[rb]

    leg_id = np.full(n, -1, dtype=np.int64)
    is_arm = np.zeros(n, dtype=bool)
    crotch_z = 0.45 * H

    if events:
        # 1o evento grande = virilha (os pes sao os pontos mais baixos da malha)
        cz, small, big = events[0]
        crotch_z = cz
        leg_id[np.array(small, dtype=np.int64)] = 0
        other = np.array(big, dtype=np.int64)
        leg_id[other[z[other] <= cz]] = 1
        # eventos grandes seguintes cujo lado menor NAO encosta no chao = bracos
        for ez, sm, _bg in events[1:3]:
            sm = np.array(sm, dtype=np.int64)
            if z[sm].min() > 0.20 * H:
                is_arm[sm] = True

    leg_id[is_arm] = -1
    return crotch_z, leg_id, is_arm


def w_back_side_mask(np, az_bins):
    """Setores de azimute que NAO sao a frente do corpo.

    A frente e o unico lugar onde a barriga pode cobrir o cos; nas costas e nos
    lados o elastico esta sempre a vista. Entao a ALTURA do anel se decide so
    aqui, e a frente fica livre para descer ate a prega depois. Sem isso, num
    corpo obeso a prega da barriga (que e o vinco mais forte do tronco) puxava
    o anel inteiro para baixo e o short saia como uma tira fina.

    Convencao do pipeline: a frente do avatar aponta para -Y, ou seja
    atan2(y,x) = -pi/2, que cai no setor az_bins/4."""
    front = az_bins // 4
    half = max(1, az_bins // 6)
    m = np.ones(az_bins, dtype=bool)
    for d in range(-half, half + 1):
        m[(front + d) % az_bins] = False
    return m


def w_ring_map(np, co, kn, sel, H, center_mode, az_bins=AZ_BINS, az_mask=None):
    """Mapa (azimute x altura) da concavidade MAXIMA, e o perfil de anel.

    O perfil e o QUANTIL BAIXO da concavidade sobre os setores de azimute -
    nao a media, e nao a fracao acima de um limiar.

    E essa escolha que separa bainha de musculo. Um gomo abdominal e fundo mas
    so existe na frente: uns 6 dos 16 setores. Um sulco de quadriceps idem. A
    bainha e rasa, porem esta em TODOS os setores, porque da a volta no membro.
    Media e fracao-acima-de-limiar premiam profundidade e deixam o gomo ganhar;
    quantil baixo pergunta "o setor MAIS FRACO desta altura ainda esta vincado?",
    que e a definicao de anel fechado. Foi a troca que fez o cos parar de pousar
    no abdomen.

    center_mode: 'slice' mede o azimute em volta do centroide da propria fatia
    (uma perna nao esta no eixo do corpo); 'axis' mede em volta do eixo; uma
    tupla (cx, cy) fixa o centro - preciso quando a curva resultante vai ser
    REAVALIADA depois em w_field, que nao tem os centroides por fatia."""
    import math
    A = np.zeros((az_bins, Z_BINS))
    if sel.size < 50:
        return A, np.zeros(Z_BINS)
    zb = np.clip((co[sel, 2] / H * Z_BINS).astype(np.int64), 0, Z_BINS - 1)
    for b in np.unique(zb):
        g = sel[zb == b]
        if g.size < 10:
            continue
        if center_mode == "slice":
            cx, cy = co[g, 0].mean(), co[g, 1].mean()
        elif center_mode == "axis":
            cx, cy = 0.0, 0.0
        else:
            cx, cy = center_mode
        az = np.arctan2(co[g, 1] - cy, co[g, 0] - cx)
        ab = np.clip(((az + math.pi) / (2 * math.pi) * az_bins).astype(np.int64),
                     0, az_bins - 1)
        np.maximum.at(A[:, b], ab, kn[g])

    ring = np.quantile(A if az_mask is None else A[az_mask], RING_QUANTILE, axis=0)
    for _ in range(RING_SMOOTH):
        ring = np.convolve(ring, np.array([0.25, 0.5, 0.25]), mode="same")
    return A, ring


def w_peaks(np, ring, lo_b, hi_b, floor=0.0):
    out = []
    for b in range(max(int(lo_b), 1), min(int(hi_b), Z_BINS - 1)):
        if ring[b] >= ring[b - 1] and ring[b] >= ring[b + 1] and ring[b] > floor:
            out.append((float(ring[b]), b))
    out.sort(reverse=True)
    return out


def w_interp_circ(np, vals, az):
    """Interpola circularmente uma curva dada por setor de azimute."""
    import math
    v = np.asarray(vals, dtype=np.float64)
    n = v.size
    if n == 1:
        return np.full(np.shape(az), float(v[0]))
    t = (az + math.pi) / (2 * math.pi) * n - 0.5
    i0 = np.floor(t).astype(np.int64)
    f = t - i0
    return v[i0 % n] * (1 - f) + v[(i0 + 1) % n] * f


def w_resample_circ(np, vals, n_out):
    import math
    az = (np.arange(n_out) + 0.5) / n_out * 2 * math.pi - math.pi
    return w_interp_circ(np, vals, az)


def w_ridge_by_azimuth(np, A, center_b, half_b, az_bins, fallback_b):
    """Para cada setor de azimute, a altura de concavidade maxima dentro de uma
    janela em volta do anel. E isto que faz o cos ACOMPANHAR a prega da barriga
    em vez de cortar reto: cada setor acha a sua propria altura.

    Duas travas, e as duas foram postas depois de ver o estrago:

    1. PRIOR GAUSSIANO em volta do anel. O argmax puro e indefeso contra sulco
       VERTICAL: a linha alba desce pelo meio da barriga e esta forte em toda a
       janela, entao nos setores da frente o argmax pousava em qualquer altura.
       Saia um V no meio do cos. O prior diz "sem uma razao forte, fique na
       altura do anel" - a prega da barriga, que e um vinco fundo e horizontal,
       ainda ganha do prior; a linha alba, que e rasa, nao.
    2. MEDIANA CIRCULAR DE 5 sobre os setores. O cos e uma curva suave em volta
       do corpo; nenhum setor isolado tem o direito de destoar dos vizinhos."""
    lo = max(0, int(center_b - half_b))
    hi = min(Z_BINS, int(center_b + half_b) + 1)
    zz = np.arange(lo, hi, dtype=np.float64)
    sigma = max(half_b * 0.5, 1.0)
    prior = np.exp(-0.5 * ((zz - center_b) / sigma) ** 2)

    out = []
    for j in range(az_bins):
        w = A[j, lo:hi] * prior
        out.append(lo + int(w.argmax()) if w.size and w.max() > 0 else fallback_b)

    return [int(sorted([out[(j + d) % az_bins] for d in (-2, -1, 0, 1, 2)])[2])
            for j in range(az_bins)]


def w_fit(me, np, co, H, crotch, leg_id, is_arm, crotch_override=None):
    """Devolve (cfg em metros, diagnostico).

    A bainha sai como ESCALAR por perna e o cos como curva de 24 setores.

    ---------------------------------------------------------------------
    TENTATIVA DESCARTADA: seguir o vinco setor a setor (passada "fina")
    ---------------------------------------------------------------------
    O Rogerio apontou que a divisa parecia "pular". A hipotese era que a
    bainha modelada pela Meshy serpenteia e que a linha reta passava PERTO
    dela em vez de EM CIMA dela. A correcao natural seria uma segunda
    passada com 48 setores procurando o vinco local numa janela de ~2 cm.

    Foi implementada e PIOROU. Quem explicou foi um render de EMISSAO PURA (sem
    luz nenhuma) pintando cinza a regiao do short e vermelho a concavidade. Sem
    iluminacao porque no render normal a sombra do degrau de tecido se confunde
    com a divisa de cor - foi essa confusao que gerou a hipotese errada. O que
    apareceu:

      - o vinco da bainha EXISTE, mas e fraco - so aparece com a concavidade
        crua, sem suavizacao, e com limiar baixo;
      - e ele e praticamente HORIZONTAL. A bainha ja e um anel reto.

    Com sinal fraco, o argmax dentro da janela encontra ruido de decimacao, nao
    tecido. O resultado foi uma borda cheia de farpas verticais - visivelmente
    pior que a reta. Ou seja: a premissa estava errada. Nao havia serpenteio
    para seguir; a reta JA era a representacao fiel.

    O que o Rogerio viu como "pulando" nao era a divisa de cor - era a sombra
    do degrau de tecido logo acima dela, que e geometria da malha e continua
    la faca-se o que se fizer com a pintura.

    Licao: antes de fazer a borda perseguir um vinco, medir se o vinco tem
    sinal - e medir num render SEM LUZ, porque com luz nao se distingue sombra
    de divisa."""
    k, _ = w_curvature(me, np)
    kn = np.clip(k / max(float(np.percentile(k, 99.0)), 1e-9), 0.0, 1.0)
    z = co[:, 2]

    # A VIRILHA e a ancora de todas as janelas, entao ela e o unico numero que
    # vale a pena poder corrigir a mao. w_limbs devolve "onde as pernas param de
    # se tocar", que na maioria dos corpos E a virilha - mas nao num IMC 148, em
    # que as coxas encostam ate quase o joelho. No zen_m_b12_d1 isso deu 0.297
    # contra ~0.37 de virilha real, e as janelas ancoradas nela levaram o short
    # inteiro 14% da altura para baixo. Corrigir a ancora conserta bainha e cos
    # de uma vez, sem escrever curva na mao.
    if crotch_override:
        crotch = crotch_override * H
    crotch_b = int(crotch / H * Z_BINS)

    # leg_id 0/1 vem da ordem de fusao do union-find, nao do lado. Reordena
    # para (esquerda = x<0, direita = x>=0), que e como w_field le.
    lids = [0, 1]
    mean_x = [float(co[leg_id == lid, 0].mean()) if (leg_id == lid).any() else 0.0
              for lid in lids]
    if mean_x[0] > mean_x[1]:
        lids.reverse()

    # ---- BAINHA: um anel por perna, medido na perna, nao no corpo ----------
    # A janela e ancorada na VIRILHA e calibrada pela propria biblioteca (ver
    # HEM_BELOW_CROTCH). O criterio do anel sozinho nao basta aqui porque os
    # dois vizinhos da bainha TAMBEM sao aneis fechados e mais fortes que ela:
    # a virilha em cima e o joelho embaixo. Com a janela larga a primeira
    # rodada perdeu para os dois - 4 avatares grudaram na virilha (b01_d2,
    # b04_d3, b09_d1, b11_d2) e o b08_d3 caiu no joelho.
    hem_curves, hem_centers, hem_peaks_d = [], [], []
    for lid in lids:
        sel = np.where(leg_id == lid)[0]
        A, ring = w_ring_map(np, co, kn, sel, H, "slice")
        pk = w_peaks(np, ring,
                     crotch_b - HEM_BELOW_CROTCH[1] * Z_BINS,
                     crotch_b - HEM_BELOW_CROTCH[0] * Z_BINS)
        hem_peaks_d.append([[round(s, 3), round((b + 0.5) / Z_BINS, 4)] for s, b in pk[:4]])
        hb = pk[0][1] if pk else int(crotch_b - 0.035 * Z_BINS)

        # centro da perna na altura da bainha. Nao e usado pelo ajuste
        # automatico (que grava a bainha como ESCALAR), e sim para permitir
        # correcao manual por azimute no shorts_map.json.
        near = sel[np.abs(co[sel, 2] - (hb + 0.5) / Z_BINS * H) < 0.03 * H]
        if near.size < 30:
            near = sel
        hem_centers.append([float(co[near, 0].mean()), float(co[near, 1].mean())])
        hem_curves.append((hb + 0.5) / Z_BINS * H)

    # ---- COS: anel no tronco, ignorando os bracos --------------------------
    # A janela comeca ACIMA da virilha: o vinco da virilha e forte e da a volta,
    # entao satisfaz o criterio do anel e vencia como "cos" nos corpos pesados
    # (b07_d1 e b08_d1 pousaram os dois exatamente na altura da virilha).
    torso = np.where((~is_arm) & (z >= crotch))[0]
    A_t, ring_t = w_ring_map(np, co, kn, torso, H, "axis", WAIST_AZ_BINS,
                             az_mask=w_back_side_mask(np, WAIST_AZ_BINS))
    waist_peaks = w_peaks(np, ring_t,
                          crotch_b + WAIST_ABOVE_CROTCH[0] * Z_BINS,
                          crotch_b + WAIST_ABOVE_CROTCH[1] * Z_BINS)
    waist_b = waist_peaks[0][1] if waist_peaks else int(crotch_b + 0.12 * Z_BINS)

    # janela larga: e o que deixa a frente descer ate a prega da barriga
    wf = w_ridge_by_azimuth(np, A_t, waist_b, WAIST_WINDOW_ZH * Z_BINS,
                            WAIST_AZ_BINS, waist_b)

    cfg = {
        "hem_l": hem_curves[0],
        "hem_r": hem_curves[1],
        "hem_center_l": hem_centers[0],
        "hem_center_r": hem_centers[1],
        "waist": [(b + 0.5) / Z_BINS * H for b in wf],
    }
    diag = {
        "crotch_zh": round(crotch / H, 4),
        "arm_verts": int(is_arm.sum()),
        "leg_verts": [int((leg_id == 0).sum()), int((leg_id == 1).sum())],
        "hem_peaks_zh": hem_peaks_d,
        "waist_peaks_zh": [[round(s, 3), round((b + 0.5) / Z_BINS, 4)]
                           for s, b in waist_peaks[:4]],
    }
    return cfg, diag


def w_field(np, co, cfg):
    """Campo escalar com sinal: >0 dentro do short, 0 exatamente na borda.

    d = min(cos(azimute) - z, z - bainha(azimute da perna))

    Existir como CAMPO CONTINUO, e nao como teste booleano, e o que permite
    cortar a malha exatamente na linha (w_cut_boundary).

    Cada curva aceita ESCALAR ou LISTA. O ajuste automatico sempre grava lista
    (48 setores); um escalar escrito a mao no shorts_map.json vale como altura
    constante. E o que mantem a correcao manual barata: para consertar um
    avatar basta escrever "waist": 0.57, sem editar 48 numeros."""
    z = co[:, 2]
    az_body = np.arctan2(co[:, 1], co[:, 0])
    waist = w_interp_circ(np, np.atleast_1d(cfg["waist"]), az_body)

    left = co[:, 0] < 0
    hem = np.empty(len(co), dtype=np.float64)
    for side, key, ckey in ((left, "hem_l", "hem_center_l"),
                            (~left, "hem_r", "hem_center_r")):
        vals = np.atleast_1d(cfg[key])
        if vals.size == 1:
            hem[side] = float(vals[0])
        else:
            cx, cy = cfg[ckey]
            az_leg = np.arctan2(co[side, 1] - cy, co[side, 0] - cx)
            hem[side] = w_interp_circ(np, vals, az_leg)

    return np.minimum(waist - z, z - hem)


def w_cut_boundary(bm, np, bmesh, field_of, is_arm_of):
    """Corta a malha EXATAMENTE na linha do short, em vez de aproximar por
    triangulo inteiro.

    Sem isto a fronteira e quantizada pela malha: cada triangulo e todo preto
    ou todo titanio, e como a bainha nao coincide com nenhuma aresta a borda
    sai numa franja de dente-de-serra de ~6 mm (um triangulo a 60k). Alisar por
    maioria de vizinhanca nao resolve - o dente-de-serra e o PISO de quem
    decide por face, nao ruido em cima dele.

    Aqui cada aresta que cruza a linha e partida no ponto de cruzamento e os
    novos vertices sao ligados dentro da face. A borda passa a ser aresta de
    verdade, exatamente onde o campo zera. Custo: algumas centenas de
    triangulos a mais, so na costura.

    Devolve o numero de vertices inseridos."""
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    d = {v: float(field_of[v.index]) for v in bm.verts}
    arm = {v: bool(is_arm_of[v.index]) for v in bm.verts}

    new_verts = []
    for e in list(bm.edges):
        a, b = e.verts
        da, db = d[a], d[b]
        if (da > 0.0) == (db > 0.0) or da == db:
            continue
        if arm[a] or arm[b]:
            continue
        t = da / (da - db)
        if not (1e-3 < t < 1.0 - 1e-3):
            continue
        try:
            _ne, nv = bmesh.utils.edge_split(e, a, t)
        except Exception:
            continue
        d[nv] = 0.0
        arm[nv] = False
        new_verts.append(nv)

    if new_verts:
        bmesh.ops.connect_verts(bm, verts=new_verts)
    return len(new_verts)


def worker_main():
    import bpy
    import bmesh
    import numpy as np
    import math
    from mathutils import Vector

    argv = sys.argv[sys.argv.index("--") + 1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--worker", action="store_true")
    ap.add_argument("--mode", required=True, choices=["fit", "apply", "render", "check"])
    ap.add_argument("--id", required=True)
    ap.add_argument("--root", required=True)
    a = ap.parse_args(argv)

    sys.path.insert(0, os.path.join(a.root, "scripts"))
    import zenith_material as zm

    master = os.path.join(a.root, "02_master", a.id + "_master.glb")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=master)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if len(meshes) != 1:
        sys.stderr.write("esperava 1 malha, achei {}\n".format(len(meshes)))
        sys.exit(1)
    obj = meshes[0]
    me = obj.data

    zs = [v.co.z for v in me.vertices]
    H = max(zs) - min(zs)

    n = len(me.vertices)
    co = np.empty(n * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(n, 3)

    # A anatomia e recalculada em TODOS os modos (nao so no --fit): a mascara
    # de braco entra na pintura, entao guardar so os numeros do cos/bainha no
    # mapa nao bastaria para reproduzir a regiao.
    crotch, leg_id, is_arm = w_limbs(me, np, co, H)

    # Cada curva pode ser ESCALAR (altura constante) ou LISTA (por azimute).
    # O ajuste automatico grava escalar na bainha e lista no cos; uma correcao
    # manual pode usar qualquer um dos dois.
    def _scale(v, f):
        return [x * f for x in v] if isinstance(v, (list, tuple)) else v * f

    def _round(v, f):
        return ([round(x * f, 5) for x in v] if isinstance(v, (list, tuple))
                else round(v * f, 5))

    if a.mode == "fit":
        # correcao manual da ancora, se houver: sobrevive a um --fit posterior
        ov = load_map(a.root).get(a.id, {}).get("crotch_override_zh")
        cfg, diag = w_fit(me, np, co, H, crotch, leg_id, is_arm, crotch_override=ov)
        entry = {
            # gravado em FRACAO DA ALTURA, nao em metros: assim um numero copiado
            # de um avatar para outro continua querendo dizer a mesma coisa
            "hem_l_zh": _round(cfg["hem_l"], 1.0 / H),
            "hem_r_zh": _round(cfg["hem_r"], 1.0 / H),
            "hem_center_l": [round(x, 5) for x in cfg["hem_center_l"]],
            "hem_center_r": [round(x, 5) for x in cfg["hem_center_r"]],
            "waist_zh": _round(cfg["waist"], 1.0 / H),
            "diag": diag,
        }
        if ov:
            entry["crotch_override_zh"] = ov
    else:
        smap = load_map(a.root)
        entry = smap[a.id]

    cfg = {
        "hem_l": _scale(entry["hem_l_zh"], H),
        "hem_r": _scale(entry["hem_r_zh"], H),
        "hem_center_l": entry.get("hem_center_l", [0.0, 0.0]),
        "hem_center_r": entry.get("hem_center_r", [0.0, 0.0]),
        "waist": _scale(entry["waist_zh"], H),
    }

    tris_master = sum(len(p.vertices) - 2 for p in me.polygons)
    field = w_field(np, co, cfg)

    # Os DOIS slots tem que existir antes de qualquer face receber
    # material_index=1: o Blender limita o indice ao numero de slots, entao
    # atribuir primeiro e criar o slot depois pinta o short de cor de corpo -
    # sem erro nenhum, so o avatar sai inteiro titanio.
    me.materials.clear()
    # ...e PURGAR os datablocks, nao so esvaziar os slots. O master ja vem com
    # um material chamado Zenith_Body (o process.py gravou), e limpar o slot nao
    # apaga o datablock: bpy.data.materials.new("Zenith_Body") encontra o nome
    # ocupado e devolve "Zenith_Body.001", que e o que iria para o GLB do app.
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    me.materials.append(zm.make_body_material(bpy))
    me.materials.append(zm.make_shorts_material(bpy))

    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.verts.layers.float.new("arm")
    bm.verts.ensure_lookup_table()
    bm.verts.index_update()
    for v in bm.verts:
        v[lay] = 1.0 if is_arm[v.index] else 0.0

    added = w_cut_boundary(bm, np, bmesh, field, is_arm)

    # Partir uma aresta transforma o triangulo vizinho em QUAD, e connect_verts
    # nem sempre tem o que ligar dentro dele. Sobra malha mista. O exportador
    # triangula os quads na saida por conta propria, entao contar faces aqui e
    # comparar com triangulos no GLB acusa uma diferenca que nao existe - foi o
    # que reprovou o primeiro --apply (60857 faces contra 61716 triangulos).
    # Triangular aqui faz o que eu valido ser exatamente o que e gravado, e de
    # quebra mantem o dist com a mesma topologia so-de-triangulos do master.
    bmesh.ops.triangulate(bm, faces=bm.faces[:])

    # Depois do corte cada face esta INTEIRA de um lado da linha, entao o
    # centroide decide sem ambiguidade.
    bm.faces.ensure_lookup_table()
    cent = np.array([tuple(f.calc_center_median()) for f in bm.faces],
                    dtype=np.float64)
    fld = w_field(np, cent, cfg)
    n_short = 0
    for i, f in enumerate(bm.faces):
        is_s = bool(fld[i] > 0.0) and not any(v[lay] > 0.5 for v in f.verts)
        f.material_index = 1 if is_s else 0
        n_short += 1 if is_s else 0
    nf = len(bm.faces)

    # ---- TRAVA: o short tem que ser UMA PECA SO -------------------------
    # Quadril + duas coxas formam uma peca unica, ligada pela virilha. Uma mao
    # ou um antebraco pintado por engano fica numa ILHA separada, porque nao ha
    # caminho pela superficie entre a mao e o short. Entao exigir conexidade
    # pega exatamente a falha que da medo: mascara de braco errada.
    #
    # A mascara de braco vem de w_limbs (eventos de fusao do union-find). Ela
    # acerta nos corpos normais, mas nao ha garantia num corpo obeso em que o
    # braco encosta no tronco e a malha funde os dois. Sem esta trava isso sairia
    # calado - um avatar de mao preta no meio de 39.
    seen = [False] * nf
    groups = []
    for f0 in bm.faces:
        if f0.material_index != 1 or seen[f0.index]:
            continue
        stack, members = [f0], []
        seen[f0.index] = True
        while stack:
            f = stack.pop()
            members.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g.material_index == 1 and not seen[g.index]:
                        seen[g.index] = True
                        stack.append(g)
        groups.append(members)
    groups.sort(key=len, reverse=True)

    # Lasca solta e defeito, nao ambiguidade: sao poucos triangulos pretos
    # perdidos no corpo, que o campo pegou de rasparem na linha. Some com elas
    # aqui em vez de tolerar - uma peca com menos de 5% do tamanho da maior nao
    # e short de ninguem. O que sobrevive a este corte e ou a peca principal ou
    # uma divisao de verdade (barriga descendo abaixo da bainha), e essa vale
    # ser reportada.
    slivers = 0
    if groups:
        keep = max(1, int(len(groups[0]) * 0.05))
        for g in groups[1:]:
            if len(g) < keep:
                slivers += len(g)
                for f in g:
                    f.material_index = 0
        groups = [g for g in groups[:1] + groups[1:] if len(g) >= keep]

    comps = [len(g) for g in groups]
    n_short = sum(comps)
    biggest = comps[0] / float(n_short) if comps else 0.0

    bm.to_mesh(me)
    bm.free()
    frac = float(n_short) / nf

    if not comps:
        sys.stderr.write("nenhuma face pintada de short\n")
        sys.exit(1)

    # MAPEAR sinaliza, ENTREGAR recusa. Nem toda ilha e erro: num corpo em que a
    # barriga desce abaixo da bainha, o short REALMENTE aparece como duas
    # manchas separadas. Abortar o --fit nessa hora jogaria fora o ajuste do
    # avatar mais dificil da biblioteca, que e justamente o que se quer guardar
    # para corrigir a mao. Entao aqui so marca; quem se recusa a gravar o GLB e
    # o --apply, mais abaixo.
    suspect = biggest < 0.97
    if suspect:
        sys.stderr.write(
            "[AVISO] short em {} ilhas ({} faces, maior = {:.1%}). Ilha solta e "
            "quase sempre mao/antebraco pintado por falha da mascara de braco - "
            "conferir o render antes de aplicar.\n"
            .format(len(comps), comps[:6], biggest))

    me.update()

    if a.mode == "check":
        # so as travas, sem render: varrer a biblioteca inteira custa minutos
        # em vez de meia hora, entao da para conferir de novo a cada mudanca
        print("RESULT " + json.dumps({
            "summary": "{}: short {:.1%}, {} peca(s), maior {:.1%}, +{} costura{}".format(
                a.id, frac, len(comps), biggest, added,
                "   << CONFERIR" if suspect else "")}))
        sys.exit(0)

    if a.mode == "apply":
        # Ultimo portao antes do asset que o app consome.
        if suspect and not entry.get("allow_islands"):
            sys.stderr.write(
                "recusado: regiao em {} ilhas (maior {:.1%}). Se as ilhas forem "
                "legitimas para este corpo, marque \"allow_islands\": true no "
                "shorts_map.json.\n".format(len(comps), biggest))
            sys.exit(1)
        dist = os.path.join(a.root, "03_dist", "glb", a.id + "_v1.glb")
        tris_before = nf
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.gltf(
            filepath=dist, export_format="GLB", use_selection=True,
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
            export_draco_position_quantization=14,
            export_draco_normal_quantization=14,
        )
        # o export tem que ter mexido so no material
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=dist)
        back = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        tris_after = sum(len(p.vertices) - 2 for o in back for p in o.data.polygons)
        if tris_after != tris_before:
            sys.stderr.write("geometria mudou no export: {} -> {}\n".format(
                tris_before, tris_after))
            sys.exit(1)
        # O corte da costura ACRESCENTA triangulos - e a unica mudanca de
        # geometria permitida aqui, e so na borda do short. Um crescimento
        # grande significaria que o campo cruzou zero onde nao devia.
        growth = (tris_before - tris_master) / float(tris_master)
        if growth > 0.06:
            sys.stderr.write("costura grande demais: {} -> {} ({:+.1%})\n".format(
                tris_master, tris_before, growth))
            sys.exit(1)
        names = [m.name for m in back[0].data.materials]
        if names != [zm.MATERIAL_NAME, zm.SHORTS_MATERIAL_NAME]:
            sys.stderr.write("materiais inesperados no dist: {}\n".format(names))
            sys.exit(1)
        print("RESULT " + json.dumps({
            "summary": "{}: {} tri ({:+d} costura), short {:.1%}".format(
                a.id, tris_after, tris_after - tris_master, frac)}))
        sys.exit(0)

    # ------------------------------------------------------------ render QA
    env = os.path.join(a.root, "03_dist", "env", "zenith_env.hdr")
    if not os.path.isfile(env):
        sys.stderr.write("ambiente nao encontrado: {}\n".format(env))
        sys.exit(1)

    scene = bpy.context.scene
    world = bpy.data.worlds.new("Zenith")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    tex = nt.nodes.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(env)
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(tex.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    zz = [v.z for v in bb]
    center = Vector((0.0, 0.0, (min(zz) + max(zz)) / 2.0))
    height = max(zz) - min(zz)

    target = bpy.data.objects.new("target", None)
    bpy.context.collection.objects.link(target)
    target.location = center
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 85.0
    cam = bpy.data.objects.new("cam", cam_d)
    bpy.context.collection.objects.link(cam)
    scene.camera = cam
    cam.constraints.new("TRACK_TO").target = target

    engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
    scene.render.engine = ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engines
                           else "BLENDER_EEVEE")
    scene.render.resolution_x, scene.render.resolution_y = 560, 800
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    try:
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.look = "None"
    except TypeError:
        pass

    out_dir = os.path.join(a.root, "qa", "shorts", a.id)
    os.makedirs(out_dir, exist_ok=True)
    dist_cam = height * 2.3
    for name, ang in (("0_frente", 0), ("1_lado", 90), ("2_costas", 180)):
        r = math.radians(ang)
        cam.location = center + Vector((math.sin(r) * dist_cam,
                                        -math.cos(r) * dist_cam, height * 0.02))
        bpy.context.view_layer.update()
        scene.render.filepath = os.path.join(out_dir, name + ".png")
        bpy.ops.render.render(write_still=True)

    def _rng(v):
        v = v if isinstance(v, (list, tuple)) else [v]
        return "{:.3f}..{:.3f}".format(min(v), max(v))

    entry["frac"] = round(frac, 4)
    entry["islands"] = len(comps)
    entry["slivers"] = slivers
    entry["summary"] = "{}: short {:.1%} (+{} costura, -{} lasca)  bainha {} / {}  cos {}{}".format(
        a.id, frac, added, slivers, _rng(entry["hem_l_zh"]), _rng(entry["hem_r_zh"]),
        _rng(entry["waist_zh"]),
        "  << {} ILHAS, maior {:.0%}".format(len(comps), biggest) if suspect else "")
    print("RESULT " + json.dumps(entry))
    sys.exit(0)


if __name__ == "__main__":
    if "--worker" in sys.argv:
        worker_main()
    else:
        sys.exit(driver_main())
