# -*- coding: utf-8 -*-
"""render_dist.py - o GLB ENTREGUE, com o material dele e o HDR de producao.

    blender -b -P qa/probe/sondas/render_dist.py -- <caminho.glb> <saida.png> [hdr]

POR QUE ISTO EXISTE, e por que nao basta o render do `shorts.py --fit`
---------------------------------------------------------------------
Em 11/08 (sessao 26) eu consertei a borda de cima da faixa nos 37 femininos,
conferi no `qa/shorts/{id}/0_frente.png` de todos, dei o lote por bom - e o
Rogerio abriu o testador e viu **faixa branca no topo de absolutamente todos**.

O render do `--fit` e clay com luz chapada: tecido nao pintado e corpo saem
quase no mesmo tom, e uma tira de 1 cm sem pintar e invisivel nele. No GLB
entregue, com o aluminio `#B9BCC2` e o `zenith_env.hdr`, o preto contra o corpo
claro faz a mesma tira gritar.

A licao NAO e "o limiar estava errado": e que eu julguei 37 avatares numa imagem
que nao mostra o defeito que eu estava procurando, sem perguntar o que aquela
imagem nao mede (LICOES.md 1.1). O conserto do CICLO e este arquivo - defeito de
PINTURA se julga no arquivo que o usuario baixa, nunca no QA intermediario.

Ver LICOES.md 4.5c.
"""
import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
if len(argv) < 2:
    raise SystemExit("uso: ... -- <glb> <saida.png> [hdr]")
glb, out = argv[0], argv[1]
hdr = argv[2] if len(argv) > 2 else None

# Enquadramento do TORSO. A faixa mora perto de 0.72 da altura em todo mundo
# (o personagem tem sempre 1.75 m - CLAUDE.md 2), entao o alvo e fixo em fracao
# e serve do IMC 16 ao 114 sem ajuste por avatar.
ALVO_ZH = 0.72
LENTE = 120.0
DIST = 3.2

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not obs:
    raise SystemExit("sem malha em {}".format(glb))
ob = obs[0]

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 900, 1200
sc.render.film_transparent = False

w = bpy.data.worlds.new("W")
sc.world = w
w.use_nodes = True
nt = w.node_tree
bg = nt.nodes["Background"]
if hdr and os.path.isfile(hdr):
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(hdr)
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
else:
    # Sem HDR o avatar sai cinza e sem identidade - metade do visual mora fora
    # do GLB (CLAUDE.md 4). Continua servindo para julgar PINTURA, mas nao cor.
    bg.inputs["Color"].default_value = (0.05, 0.05, 0.06, 1.0)
bg.inputs["Strength"].default_value = 1.0

zs = [(ob.matrix_world @ v.co).z for v in ob.data.vertices]
alt = max(zs) - min(zs)

cam_d = bpy.data.cameras.new("C")
cam_d.lens = LENTE
cam = bpy.data.objects.new("C", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam
cam.location = (0.0, -DIST, min(zs) + alt * ALVO_ZH)
cam.rotation_euler = (math.radians(90), 0.0, 0.0)

sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("OK", out)
