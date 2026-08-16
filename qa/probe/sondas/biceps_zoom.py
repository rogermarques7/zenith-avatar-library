# -*- coding: utf-8 -*-
"""Zoom no cotovelo com o morph_biceps num influence dado, material+HDR reais.

    blender -b -P qa/probe/sondas/biceps_zoom.py -- <glb> <influence> <saida.png> [hdr]

Existe para ver se o empurrao do biceps vaza pra baixo do cotovelo - a mesma
regua visual do render_dist.py, so que mirando no braço em vez do tronco.
"""
import math
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
glb, influence, out = argv[0], float(argv[1]), argv[2]
hdr = argv[3] if len(argv) > 3 else None

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not obs:
    raise SystemExit("sem malha em {}".format(glb))

for ob in obs:
    if not ob.data.shape_keys:
        continue
    for kb in ob.data.shape_keys.key_blocks:
        if kb.name == "morph_biceps":
            kb.value = influence

zs = []
for ob in obs:
    mw = ob.matrix_world
    zs += [(mw @ v.co).z for v in ob.data.vertices]
zmin, zmax = min(zs), max(zs)
H = zmax - zmin

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 64
sc.render.resolution_x = 700
sc.render.resolution_y = 700
sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"

w = bpy.data.worlds.new("W")
sc.world = w
w.use_nodes = True
env = w.node_tree.nodes.new("ShaderNodeTexEnvironment")
if hdr:
    env.image = bpy.data.images.load(hdr)
bg = w.node_tree.nodes["Background"]
w.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])

# alvo: braco direito em A-pose, na altura do cotovelo (~0.62-0.66 da altura,
# meio do caminho entre pulso ~0.58 e ombro ~0.73)
alvo_z = zmin + 0.66 * H
alvo_x = 0.15
loc = (alvo_x + 0.35, -1.3, alvo_z)
cam_data = bpy.data.cameras.new("cam")
cam_data.lens = 85
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
cam.location = loc
import mathutils
look = mathutils.Vector((alvo_x, 0, alvo_z)) - mathutils.Vector(loc)
rot_quat = look.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
sc.camera = cam

light_data = bpy.data.lights.new("sun", type="SUN")
light_data.energy = 2.0
light = bpy.data.objects.new("sun", light_data)
sc.collection.objects.link(light)
light.location = (2, -2, 3)

sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("OK", out)
