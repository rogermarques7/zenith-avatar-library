#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_env.py - gera o ambiente de iluminacao Zenith (HDR equiretangular).

    python scripts/make_env.py

Saida: 03_dist/env/zenith_env.hdr

--------------------------------------------------------------------------
PORQUE ISTO E UM ARQUIVO SEPARADO, E NAO LUZES DENTRO DO GLB
--------------------------------------------------------------------------
glTF nao carrega iluminacao de forma portavel. O <model-viewer> (e portanto o
model_viewer_plus no Flutter, que e o mesmo componente numa WebView) ilumina
o modelo por IBL, a partir do atributo `environment-image`. Luz autorada no
arquivo do avatar seria ignorada ou inconsistente entre visualizadores.

Consequencia pratica, e ela e boa: a identidade Zenith mora em UM arquivo de
~320 KB. Reajustar a luz de toda a biblioteca nao re-processa 39 avatares -
troca este .hdr. Isso ja se pagou: a correcao do "ficou prateado demais"
(27/07) foi feita SO aqui, sem tocar em um GLB sequer.

--------------------------------------------------------------------------
A PRIMEIRA VERSAO ERROU: ANEL UNIFORME NAO E RIM, E LUZ AMBIENTE
--------------------------------------------------------------------------
A tentativa inicial usou um anel horizontal invariante em azimute, pela
robustez: nao depende da convencao de mapeamento equiretangular (Blender e
three.js podem diferir na rotacao) nem da posicao da camera.

Renderizado, saiu CHAPADO. O motivo, obvio depois de ver: um anel ilumina a
frente do corpo exatamente tanto quanto as bordas. Luz vinda de todos os
azimutes com a mesma intensidade E luz ambiente - zera a direcionalidade, que
e o unico mecanismo que desenha relevo. O resultado foi um boneco roxo liso,
ou seja, o problema original com outra cor.

Registrado porque a intuicao "simetria = seguro" e forte e volta sempre: em
iluminacao, simetria total = contraste zero.

--------------------------------------------------------------------------
O DESENHO ATUAL - 4 papeis, 6 fontes
--------------------------------------------------------------------------
  KEY     azul frio, alto e de lado, ESTREITA: e quem MODELA o corpo. Sem ela
          o avatar vira silhueta. Estreita porque key larga vira ambiente.
  KICKER  key traseira mais fraca, para a vista de COSTAS ter forma. O avatar
          gira sozinho no app; as costas sao exibidas.
  RIM     dois nucleos roxos estreitos e laterais: pegam as duas bordas da
          silhueta e separam o corpo do fundo escuro. E aqui que a marca vive.
  FILL    azul frio difuso + rebote fraquissimo de baixo, so para o lado
          escuro nao fechar em preto e engolir a perna de tras.

Azimute: `az` e medido a partir da FRENTE do avatar (0 = de frente para ele).
A conversao para a coluna da imagem carrega a convencao do visualizador e foi
MEDIDA, nao deduzida - ver ENV_AZIMUTH_OFFSET_DEG.
"""

import math
import os
import sys

import numpy as np

# ---------------------------------------------------------------- parametros

# 512x256 e proposital. IBL nao usa a resolucao do HDR: o visualizador
# pre-filtra o ambiente num cubemap borrado antes de iluminar, e a fonte mais
# estreita daqui tem 11 graus de raio (~16 px nesta resolucao). A 1024x512 o
# arquivo dava 1,1 MB de resolucao que ninguem ve, num asset que o app baixa
# junto da biblioteca.
#
# O RLE do Radiance quase nao ajuda aqui: a PRIMEIRA versao do ambiente era
# invariante em azimute (cada linha, uma cor so) e comprimia para 38 KB. Com
# fontes direcionais cada pixel e diferente e a compressao some. Nao esperar
# os 38 KB de volta.
WIDTH, HEIGHT = 512, 256

# Alinhamento entre o `az` das luzes abaixo e a coluna da imagem. NAO deduzir
# no papel: foi MEDIDO com uma sonda (esfera difusa iluminada por vermelho em
# az 0, verde em az 90 e azul em az 180, renderizada da camera frontal).
#
# O valor deduzido inicialmente errou por 180 graus, e o sintoma foi
# diagnosticado como problema de balanco por varias iteracoes: a key caiu
# ATRAS do avatar e os dois rims roxos NA FRENTE dele. Dai o corpo sair
# chapado e roxo de frente e bonito de costas - estava certo, so que virado.
ENV_AZIMUTH_OFFSET_DEG = 270.0

# (hex, azimute, elevacao, raio angular, intensidade)
#   azimute 0   = de frente para o avatar
#   azimute 180 = atras dele
LIGHTS = [
    # KEY frontal-lateral: e quem MODELA o corpo de frente.
    # ESTREITA (13 graus) de proposito - key larga vira ambiente e o corpo
    # sai chapado, que foi o sintoma das primeiras versoes.
    #
    # FRIA E FRACA, revisto em 27/07. A 1a versao era #E4EAF6 (quase branca) a
    # intensidade 42, e o Rogerio reprovou: "a cor ficou mais pra prateado".
    # Ele estava certo - com metallic 0.50 uma key branca e forte estoura o
    # specular em branco puro e o corpo le como ACO POLIDO, nao como titanio.
    # A cor do corpo em PBR nao vem so do baseColor: metade vem do que ele
    # reflete. Baixar a intensidade e esfriar a key devolveu o titanio SEM
    # tocar em nenhum GLB.
    ("#93B4EC",   58.0,  38.0, 13.0, 24.0),
    # KEY traseira ("kicker"), mais fraca. NAO e decorativa: sem ela a vista
    # de costas fica iluminada so pelos dois rims, que dali sao luz FRONTAL -
    # e o avatar volta a ser um boneco roxo chapado meia volta depois. Como o
    # avatar gira sozinho no app, as costas sao exibidas e valem tanto quanto
    # a frente.
    ("#D8E2F5",  212.0,  34.0, 15.0, 20.0),
    # Preenchimento azul frio no lado oposto a key: tinge a sombra, nao o
    # corpo todo. E o "azul frio" do briefing.
    ("#4A78E0",  -62.0,  22.0, 36.0,  3.0),
    # RIM roxo - nucleos estreitos, agora bem LATERAIS (nao atras): dessa
    # posicao eles pegam a borda da silhueta tanto de frente quanto de costas,
    # e nunca ficam de frente para a camera.
    ("#8346C6",  112.0,  14.0, 11.0, 44.0),
    ("#8346C6", -112.0,  14.0, 11.0, 44.0),
    # Rebote de baixo, quase nada: impede que a perna de tras feche em preto.
    ("#2A3550",  200.0, -45.0, 45.0,  0.30),
]

# Piso global. Nao e preto absoluto: evita banding no lado escuro.
FLOOR_HEX       = "#0D0D12"
FLOOR_INTENSITY = 0.02


def srgb_hex_to_linear(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return np.array([c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                     for c in srgb], dtype=np.float64)


def _direction(az_deg, elev_deg):
    a, e = math.radians(az_deg), math.radians(elev_deg)
    return np.array([math.cos(e) * math.sin(a), math.sin(e), math.cos(e) * math.cos(a)])


def build_equirect():
    """Retorna (H, W, 3) em radiancia linear."""
    # Linha -> elevacao (topo da imagem = zenite). Coluna -> azimute.
    elev = np.radians(90.0 - 180.0 * (np.arange(HEIGHT) + 0.5) / HEIGHT)
    az = np.radians(360.0 * (np.arange(WIDTH) + 0.5) / WIDTH
                    - ENV_AZIMUTH_OFFSET_DEG)

    ce, se = np.cos(elev)[:, None], np.sin(elev)[:, None]
    dirs = np.stack([ce * np.sin(az)[None, :],
                     np.broadcast_to(se, (HEIGHT, WIDTH)),
                     ce * np.cos(az)[None, :]], axis=-1)

    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float64)
    img += FLOOR_INTENSITY * srgb_hex_to_linear(FLOOR_HEX)

    for hex_color, a, e, radius, intensity in LIGHTS:
        cos_ang = np.clip(dirs @ _direction(a, e), -1.0, 1.0)
        ang = np.degrees(np.arccos(cos_ang))
        # Gaussiana na distancia ANGULAR (nao em lat/long): sem isso o blob
        # esticaria perto dos polos, onde as colunas se comprimem.
        g = np.exp(-0.5 * (ang / radius) ** 2)
        img += g[..., None] * (intensity * srgb_hex_to_linear(hex_color))

    return img


# ------------------------------------------------------------- Radiance .hdr

def to_rgbe(img):
    """float (H,W,3) -> uint8 (H,W,4) no formato RGBE compartilhado."""
    v = img.max(axis=2)
    mant, expo = np.frexp(np.maximum(v, 0.0))    # v = mant * 2**expo
    scale = np.where(v > 1e-32, mant * 256.0 / np.maximum(v, 1e-32), 0.0)
    rgbe = np.zeros(img.shape[:2] + (4,), dtype=np.uint8)
    rgbe[..., :3] = np.clip(img * scale[..., None], 0, 255).astype(np.uint8)
    rgbe[..., 3] = np.where(v > 1e-32, np.clip(expo + 128, 0, 255), 0).astype(np.uint8)
    return rgbe


def _encode_component(line, out):
    """RLE adaptativo do Radiance: byte >128 e run, <=128 e literal."""
    n = len(line)
    i = 0
    while i < n:
        j = i + 1
        while j < n and line[j] == line[i] and (j - i) < 127:
            j += 1
        if j - i >= 4:                       # vale a pena virar run
            out.append(128 + (j - i))
            out.append(int(line[i]))
            i = j
            continue
        start = i
        i += 1
        while i < n and (i - start) < 128:
            # corta o literal quando um run de 4 comeca aqui
            if i + 3 < n and line[i] == line[i + 1] == line[i + 2] == line[i + 3]:
                break
            i += 1
        out.append(i - start)
        out.extend(int(b) for b in line[start:i])


def write_hdr(path, img):
    rgbe = to_rgbe(img)
    h, w = rgbe.shape[:2]
    if not (8 <= w <= 0x7FFF):
        raise ValueError("largura fora da faixa que permite RLE por scanline")

    buf = bytearray()
    buf += b"#?RADIANCE\n"
    buf += b"# Zenith avatar environment - gerado por scripts/make_env.py\n"
    buf += b"FORMAT=32-bit_rle_rgbe\n\n"
    buf += "-Y {} +X {}\n".format(h, w).encode("ascii")
    for row in range(h):
        buf += bytes((2, 2, (w >> 8) & 0xFF, w & 0xFF))
        for ch in range(4):
            _encode_component(rgbe[row, :, ch], buf)

    with open(path, "wb") as fh:
        fh.write(buf)
    return len(buf)


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    out_dir = os.path.join(root, "03_dist", "env")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    out = os.path.join(out_dir, "zenith_env.hdr")

    img = build_equirect()
    size = write_hdr(out, img)

    print("ambiente Zenith gravado")
    print("  arquivo   : {}".format(os.path.relpath(out, root)))
    print("  resolucao : {}x{} equiretangular".format(WIDTH, HEIGHT))
    print("  tamanho   : {:.1f} KB".format(size / 1024.0))
    for hex_color, a, e, radius, intensity in LIGHTS:
        print("  luz       : {} az {:+6.1f}  elev {:+5.1f}  raio {:4.1f}  int {:5.2f}".format(
            hex_color, a, e, radius, intensity))
    print("  luminancia: min {:.4f}  max {:.3f}".format(img.min(), img.max()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
