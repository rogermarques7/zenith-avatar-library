"""Renderiza os 4 estados do morph. Licao v84 do engine: numero nao mostra
membrana/dobra/vinco — so a foto SOMBREADA mostra. E o zoom na axila e
obrigatorio, porque foi la que aquele projeto quebrou 5 vezes."""
import bpy, sys, os, math

argv = sys.argv[sys.argv.index("--") + 1:]
GLB = argv[argv.index("--glb") + 1]
OUT = os.path.abspath(argv[argv.index("--out") + 1])
HDR = argv[argv.index("--hdr") + 1] if "--hdr" in argv else None
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
ob = [o for o in bpy.data.objects if o.type == "MESH"][0]

sc = bpy.context.scene
# WORKBENCH com CAVIDADE, nao EEVEE: o material Zenith e metalico e escuro, e
# num render de aparencia a membrana/dobra fica escondida no brilho. O engine
# usava exatamente isto para diagnosticar (matcap/cavity revelam vinco e
# colisao de superficie). Aparencia bonita nao e o objetivo deste teste.
sc.render.engine = "BLENDER_WORKBENCH"
sh = sc.display.shading
sh.light = "STUDIO"
sh.color_type = os.environ.get("COLOR_TYPE", "SINGLE")
sh.single_color = (0.62, 0.63, 0.66)
sh.show_cavity = True
sh.cavity_type = "BOTH"
sh.cavity_ridge_factor = 1.6
sh.cavity_valley_factor = 1.6
sh.show_object_outline = False
sc.display.render_aa = "8"
sc.render.resolution_x = 720
sc.render.resolution_y = 900
sc.render.film_transparent = False
sc.view_settings.view_transform = "Standard"

# Ambiente: o mesmo HDR que o app usa, para o julgamento ser sobre o que o
# usuario vai ver de fato.
w = bpy.data.worlds.new("W"); sc.world = w
w.use_nodes = True
nt = w.node_tree; nt.nodes.clear()
bg = nt.nodes.new("ShaderNodeBackground")
out = nt.nodes.new("ShaderNodeOutputWorld")
if HDR and os.path.isfile(HDR):
    # O HDR ILUMINA mas nao aparece: a camera ve fundo escuro. Sem isto o
    # render sai com o ceu do HDR atras e o corpo compete com ele.
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(HDR)
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.inputs[1].default_value = (0.02, 0.02, 0.03, 1)   # o que a camera ve
    nt.links.new(env.outputs[0], mix.inputs[2])           # o que ilumina
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(mix.outputs[0], bg.inputs[0])
else:
    bg.inputs[0].default_value = (0.05, 0.05, 0.06, 1)
nt.links.new(bg.outputs[0], out.inputs[0])

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
cam_data.lens = 85


# Mira por RESTRICAO, nao por euler na mao: a primeira versao calculou a
# rotacao a mao, errou, e as 12 fotos sairam apontando para o ceu do HDR.
alvo_obj = bpy.data.objects.new("alvo", None)
sc.collection.objects.link(alvo_obj)
tr = cam.constraints.new("TRACK_TO")
tr.target = alvo_obj
tr.track_axis = "TRACK_NEGATIVE_Z"
tr.up_axis = "UP_Y"


def mirar(alvo, dist, ang_h, ang_v=0.0):
    alvo_obj.location = alvo
    a = math.radians(ang_h); b = math.radians(ang_v)
    cam.location = (alvo[0] + dist * math.sin(a) * math.cos(b),
                    alvo[1] - dist * math.cos(a) * math.cos(b),
                    alvo[2] + dist * math.sin(b))
    bpy.context.view_layer.update()


kb = ob.data.shape_keys.key_blocks
# ⚠️ O `value` do shape key e CLAMPADO pelo slider, e o importador de glTF
# recria as chaves com o range default 0..1 - o `slider_min/max` que o
# morph.py grava nao atravessa o arquivo. Sem isto, toda influence negativa
# vira 0 e o estado "tudo no minimo" renderiza EXATAMENTE a base: a foto
# parece aprovar o morph quando na verdade nao aplicou nenhum.
# No app isso nao acontece - `morphTargetInfluences` do three.js e float livre.
for _k in kb:
    _k.slider_min, _k.slider_max = -3.0, 3.0
import json as _json
ESTADOS = _json.loads(os.environ.get("ESTADOS", '[["0_base",0,0],["1_ombro",1,0],["2_biceps",0,1],["3_ambos",1,1]]'))
KEYS = _json.loads(os.environ.get("KEYS", '["morph_shoulders","morph_biceps"]'))
# Vistas: corpo inteiro de frente, 3/4 (onde a axila aparece) e zoom na axila.
import json as _j2
VISTAS = _j2.loads(os.environ.get("VISTAS", '[["corpo",[0,0,0.95],3.2,0],["tresquartos",[0,0,1.15],2.2,35],["axila",[0.19,0,1.24],0.55,30]]'))

for est in ESTADOS:
    nome, vals = est[0], est[1:]
    for k in kb:
        if k.name != "Basis":
            k.value = 0.0
    for k, v in zip(KEYS, vals):
        kb[k].value = float(v)
    for vnome, alvo, dist, ang in VISTAS:
        mirar(alvo, dist, ang)
        sc.render.filepath = os.path.join(OUT, "%s_%s.png" % (vnome, nome))
        bpy.ops.render.render(write_still=True)
        print("  ->", os.path.basename(sc.render.filepath))
print("renders em", OUT)
