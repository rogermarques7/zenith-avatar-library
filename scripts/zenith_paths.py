#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zenith_paths.py - fonte unica do LAYOUT das pastas de entrada e do NOME
do arquivo entregue em 03_dist/glb/.

Mesmo papel que o zenith_material.py tem para o material: se cada script
montasse o caminho por conta propria, bastaria um esquecer a pasta de sexo
para gravar folha feminina no meio da masculina - exatamente a bagunca que
esta separacao existe para evitar. Sao 6 scripts + 3 sondas lendo esses
caminhos; a regra mora aqui e so aqui.

--------------------------------------------------------------------------
A SEPARACAO POR SEXO (28/07/2026) - e SO na ENTRADA
--------------------------------------------------------------------------
    00_input/sheets/m/{id}_sheet.png        00_input/sheets/f/...
    00_input/references/m/{id}/             00_input/references/f/{id}/

    00_input/sheets/m/_mother_m.png         (folha-mae, CHARACTER_BIBLE §7)
    00_input/sheets/f/_mother_f.png

Pedido do Rogerio em 28/07, e o motivo dele decide o escopo: **estas sao as
pastas que ele abre NA MAO** para escolher o que subir na Meshy e o que anexar
no ChatGPT. Com 39 masculinos + 32 femininos no mesmo diretorio, escolher a
referencia certa vira caca ao arquivo.

PELO MESMO MOTIVO, 01_raw/, 02_master/ e 03_dist/glb/ CONTINUAM PLANOS. Sao
pastas de maquina - ninguem navega nelas a mao, o id ja carrega o sexo
(zen_m_ / zen_f_), a ordenacao alfabetica ja agrupa, e o 03_dist ainda seria
caminho de CDN. Separar la seria custo sem ganho (decidido na mesma sessao,
ver state.md).

--------------------------------------------------------------------------
03_dist/glb/{id}_v{n}.glb - O NOME CARREGA A VERSAO, e por isso ele NAO se
sobrescreve (31/07/2026)
--------------------------------------------------------------------------
O caminho do dist e uma URL de CDN, e URL de CDN fica em cache - no CDN e no
celular. Regravar o mesmo {id}_v1.glb com um short novo entrega, para quem ja
baixou, o short VELHO, e para sempre: o app nao tem como saber que o conteudo
mudou se o nome nao mudou. A correcao vira invisivel exatamente para quem ja
usava o app.

Por isso todo script que grava em 03_dist/glb/ passa por dist_glb_next() e
grava a versao SEGUINTE, e o build_index.py deriva o campo "version" do
library.json do nome do arquivo. A regra e simples de proposito: **mudou o
conteudo, mudou o numero**. Nao existe flag --bump, porque flag se esquece, e
esquece-la reintroduz o bug em silencio.
"""

import glob
import os
import re

ID_RE = re.compile(r"^zen_(?P<sex>[mf])_b\d{2}[a-z]?_d[123]$")
DIST_GLB_RE = re.compile(
    r"^(?P<id>zen_[mf]_b\d{2}[a-z]?_d[123])_v(?P<version>\d+)\.glb$")
SEXES = ("m", "f")
VIEWS = ("front", "side", "back")


def sex_of(avatar_id):
    """'zen_f_b05_d2' -> 'f'. Estoura em id malformado de proposito: o nome do
    arquivo e o contrato com o pipeline (CLAUDE.md), e um id que nao casa aqui
    gravaria o avatar na pasta errada em silencio."""
    m = ID_RE.match(avatar_id)
    if not m:
        raise ValueError(
            "id {!r} fora da convencao zen_{{m|f}}_b##[letra]_d#. "
            "O nome do arquivo e o contrato com o pipeline.".format(avatar_id))
    return m.group("sex")


def sheets_dir(root, sex):
    return os.path.join(root, "00_input", "sheets", sex)


def refs_root(root, sex):
    return os.path.join(root, "00_input", "references", sex)


def sheet_path(root, avatar_id):
    return os.path.join(sheets_dir(root, sex_of(avatar_id)), avatar_id + "_sheet.png")


def mother_path(root, sex):
    return os.path.join(sheets_dir(root, sex), "_mother_{}.png".format(sex))


def refs_dir(root, avatar_id):
    return os.path.join(refs_root(root, sex_of(avatar_id)), avatar_id)


def ref_path(root, avatar_id, view):
    """view em VIEWS: front | side | back."""
    if view not in VIEWS:
        raise ValueError("vista {!r} nao e uma de {}".format(view, VIEWS))
    return os.path.join(refs_dir(root, avatar_id),
                        "{}_ref_{}.png".format(avatar_id, view))


def all_sheets(root):
    """[(id, caminho)] dos dois sexos, ordenado. Ignora _mother_*.png, que sao
    copias de folhas ja listadas."""
    out = []
    for sex in SEXES:
        for p in sorted(glob.glob(os.path.join(sheets_dir(root, sex), "*_sheet.png"))):
            out.append((os.path.basename(p)[:-len("_sheet.png")], p))
    return out


def all_ref_dirs(root):
    """[(id, diretorio)] dos dois sexos, ordenado."""
    out = []
    for sex in SEXES:
        base = refs_root(root, sex)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            d = os.path.join(base, name)
            if os.path.isdir(d):
                out.append((name, d))
    return out


def dist_glb_dir(root):
    return os.path.join(root, "03_dist", "glb")


def dist_glb_versions(root, avatar_id):
    """[(versao, caminho)] daquele id, em ordem crescente. Normalmente 1 item."""
    sex_of(avatar_id)   # estoura em id malformado, como o resto do arquivo
    out = []
    for p in glob.glob(os.path.join(dist_glb_dir(root), avatar_id + "_v*.glb")):
        m = DIST_GLB_RE.match(os.path.basename(p))
        if m and m.group("id") == avatar_id:
            out.append((int(m.group("version")), p))
    return sorted(out)


def dist_glb_current(root, avatar_id):
    """(versao, caminho) da MAIOR versao no disco, ou (0, None) se nao existe.
    E o que um leitor (qa_render, testador) deve abrir."""
    v = dist_glb_versions(root, avatar_id)
    return v[-1] if v else (0, None)


def dist_glb_next(root, avatar_id):
    """(versao, caminho) da PROXIMA versao. Nao grava e nao apaga nada.

    Todo escritor de 03_dist/glb/ comeca por aqui - ver o cabecalho."""
    v, _ = dist_glb_current(root, avatar_id)
    return v + 1, os.path.join(dist_glb_dir(root),
                               "{}_v{}.glb".format(avatar_id, v + 1))


def dist_glb_retire(root, avatar_id, keep):
    """Apaga as versoes ANTERIORES a `keep`. Devolve os nomes apagados.

    Chamar so DEPOIS de o arquivo novo passar nas validacoes: enquanto a versao
    velha existir no disco, um export que falhou no meio nao deixa o app sem
    avatar nenhum. Aqui e local - quem ja subiu ao CDN continua servindo a URL
    antiga ate o library.json novo chegar no celular, que e o comportamento que
    se quer."""
    gone = []
    for v, p in dist_glb_versions(root, avatar_id):
        if v < keep:
            os.remove(p)
            gone.append(os.path.basename(p))
    return gone


def ensure_dirs(root):
    """Cria o esqueleto. Barato e idempotente - chamar antes de gravar."""
    for sex in SEXES:
        os.makedirs(sheets_dir(root, sex), exist_ok=True)
        os.makedirs(refs_root(root, sex), exist_ok=True)
