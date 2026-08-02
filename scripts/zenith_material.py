#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
zenith_material.py - fonte unica do MATERIAL dos avatares Zenith.

Importado por process.py (pipeline completo) e por restyle.py (troca de
material sobre masters ja aprovados). Os dois PRECISAM concordar: se cada um
tivesse sua propria constante, um avatar novo sairia com cor diferente dos 39
que ja existem, e a inconsistencia so apareceria no app.

--------------------------------------------------------------------------
A DECISAO (27/07/2026) - o avatar deixou de ser roxo
--------------------------------------------------------------------------
Ate aqui o corpo era #8346C6 (roxo de marca) em material unico. O problema
medido pelo Rogerio: o roxo saturado achata o relevo muscular, que e o FOCO
do app. Corpo colorido + malha de 18k = musculo ilegivel.

O conceito novo separa IDENTIDADE de COR DO CORPO:

  corpo   -> cinza titanio neutro, quase sem cor propria
  Zenith  -> vem da LUZ (rim roxo + preenchimento azul frio), nao do corpo

Consequencia arquitetural: a identidade visual passou a morar FORA do GLB.
O material aqui e so metade da entrega; a outra metade e o ambiente HDR
(scripts/make_env.py) que o app carrega em environment-image. glTF nao
transporta iluminacao de forma portavel - o model-viewer ilumina por IBL.

--------------------------------------------------------------------------
Porque estes numeros
--------------------------------------------------------------------------
BASE #6D737B  - titanio escuro, levemente frio. Mantido exatamente como o
                Rogerio especificou. Albedo e propriedade do material; quem
                controla o quao claro o avatar APARECE e a intensidade do
                ambiente + exposure, nao o hex. Escurecer o albedo "para
                compensar" a luz colorida seria corrigir no lugar errado.

METALLIC 0.50 - MEDIDO, e contra a minha previsao inicial. Eu tinha proposto
                0.25 argumentando que metallic alto zera a difusa e faz o
                corpo sumir no fundo escuro. Uma varredura 3x3 de
                roughness x metallic sobre o zen_m_b05_d3 mostrou o oposto:
                de 0.25 para 0.50 o ganho de leitura muscular e grande, e o
                argumento estava errado porque pressupunha ambiente escuro -
                o ambiente Zenith tem fontes brilhantes e direcionais, entao
                ha o que refletir. Fica em 0.50 e nao 0.80 para preservar
                alguma difusa: 0.80 quase nao melhorou e deixa o avatar
                refem do ambiente (se o app trocar o environment-image, um
                corpo 80% metalico apaga).

ROUGHNESS 0.35 - e o specular que desenha o relevo, e specular concentrado
                desenha melhor. O contorno roxo tambem depende disso: em IBL
                o difuso e de baixa frequencia e nao produz contorno nenhum -
                rim so existe como reflexo. Foi por isso que as primeiras
                tentativas, com 0.45, davam banho roxo em vez de borda.
                Piso pratico: brilho concentrado demais realca cada faceta da
                decimacao. Em 18k, 0.35 ainda esta limpo; com os LODs de
                40k/60k da para testar 0.25 (a linha de cima da varredura).

EMISSIVE 0    - o rim NAO e assado no material. Fresnel depende do angulo de
                camera e o avatar gira sozinho no app; um rim fixo em textura
                ficaria colado no lugar errado meia volta depois.
"""

# --------------------------------------------------------------------------
# REVISTO EM 31/07/2026 (sessao 18) - titanio escuro -> aluminio semifosco
# --------------------------------------------------------------------------
# Escolhido pelo Rogerio no banco de ensaio do avatar_tester.html, que passou a
# permitir trocar cor/acabamento/luz em tempo real sobre o GLB real. Ou seja:
# decidido OLHANDO os 76 corpos sob o HDR de producao, nao por argumento.
#
# O que mudou e por que os numeros antigos (#6D737B / 0.50 / 0.35) ficam
# registrados acima: o raciocinio deles continua valendo - foi a MEDIDA da
# varredura 3x3 que os elegeu, sobre um corpo 18k e material escuro. Com 60k e
# base clara o compromisso e outro: o albedo claro devolve difusa suficiente
# para o corpo nao depender tanto do ambiente, e o metallic mais baixo protege
# o avatar de sumir se o app esquecer de carregar o environment-image - risco
# real, porque metade do visual mora fora do GLB (ver acima).
#
# ATENCAO: mexer aqui NAO altera os GLBs sozinho. Depois de mudar, rodar
#   python scripts/restyle.py --all
# que le os masters e regrava 03_dist/glb/ sem re-decimar e sem tocar em
# 02_master/. Sem isso, avatar novo sai diferente dos que ja existem.
ZENITH_BASE_HEX    = "#B9BCC2"     # aluminio claro
ZENITH_METALLIC    = 0.25
ZENITH_ROUGHNESS   = 0.45

# Short - ainda desligado no pipeline (SHORTS_ENABLED=False em process.py).
# Quando religar, o short e o unico lugar onde faz sentido preto puro: ele
# ancora o contraste e separa tronco de pernas.
ZENITH_SHORTS_HEX  = "#0D0D12"

MATERIAL_NAME        = "Zenith_Body"
SHORTS_MATERIAL_NAME = "Zenith_Shorts"

# Nome anterior, mantido para reconhecer masters/dists da fase roxa.
LEGACY_MATERIAL_NAME = "Zenith_Purple"


def hex_to_linear_rgba(h):
    """baseColorFactor do glTF e LINEAR; o hex da marca e sRGB."""
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (lin[0], lin[1], lin[2], 1.0)


def make_material(bpy, name, hex_color, metallic=ZENITH_METALLIC,
                  roughness=ZENITH_ROUGHNESS):
    """Cria o material Zenith. `bpy` vem do chamador porque este modulo tambem
    e lido fora do Blender (make_env.py usa so as constantes).

    O no e procurado por TIPO (bl_idname), nunca por nome. O nome do no e
    TRADUZIDO pela interface: nesta maquina o Blender esta em portugues e o
    Principled BSDF se chama "BSDF - Pre-fundamentado", entao um
    nodes.get("Principled BSDF") devolve None. A versao anterior fazia
    exatamente isso dentro de um `if bsdf:` - ou seja, num Blender localizado
    ela exportaria o material com os valores PADRAO, sem erro nenhum.
    So nao quebrou porque read_factory_settings() reseta o idioma antes. E
    depender disso e depender de um efeito colateral."""
    m = bpy.data.materials.new(name=name)
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes
                 if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if bsdf is None:
        raise RuntimeError(
            "Principled BSDF nao encontrado no material {!r}. Nos presentes: {}"
            .format(name, [(n.name, n.bl_idname) for n in m.node_tree.nodes]))

    bsdf.inputs["Base Color"].default_value = hex_to_linear_rgba(hex_color)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m


def make_body_material(bpy):
    return make_material(bpy, MATERIAL_NAME, ZENITH_BASE_HEX)


def make_shorts_material(bpy):
    # Short quase preto: fosco e nao-metalico, para nao competir com o rim.
    return make_material(bpy, SHORTS_MATERIAL_NAME, ZENITH_SHORTS_HEX,
                         metallic=0.0, roughness=0.7)
