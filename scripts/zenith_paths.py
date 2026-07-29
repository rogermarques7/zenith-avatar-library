#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""zenith_paths.py - fonte unica do LAYOUT das pastas de entrada.

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
"""

import glob
import os
import re

ID_RE = re.compile(r"^zen_(?P<sex>[mf])_b\d{2}[a-z]?_d[123]$")
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


def ensure_dirs(root):
    """Cria o esqueleto. Barato e idempotente - chamar antes de gravar."""
    for sex in SEXES:
        os.makedirs(sheets_dir(root, sex), exist_ok=True)
        os.makedirs(refs_root(root, sex), exist_ok=True)
