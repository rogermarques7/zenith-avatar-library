"""QA render — 4 vistas de um GLB de distribuicao em fundo de estudio.

Uso (Blender headless):
  blender -b -P scripts/qa_render.py -- zen_m_b01_d1
  blender -b -P scripts/qa_render.py -- zen_m_b01_d1 --raw     # inspeciona 01_raw/
  blender -b -P scripts/qa_render.py -- zen_m_b01_d1 --torso   # close no tronco

Le 03_dist/glb/{id}_v1.glb (ou 01_raw/{id}_raw.glb com --raw) e grava PNGs em
qa/inspect/{id}/. Nao substitui process.py; e so inspecao visual em 360 graus.

--raw serve para julgar a malha da Meshy ANTES de gastar processamento: se o
cru vier alucinado, o defeito nao e do pipeline e nenhum ajuste de decimacao
conserta. --torso enquadra o tronco, onde vivem os artefatos de abdomen.
"""
import bpy, sys, os, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv:
    raise SystemExit("informe o id, ex.: zen_m_b01_d1")
avatar_id = argv[0]
use_raw = "--raw" in argv
torso = "--torso" in argv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import zenith_paths as zp                                          # noqa: E402

if use_raw:
    glb = os.path.join(REPO, "01_raw", f"{avatar_id}_raw.glb")
else:
    # a versao MAIS ALTA, nunca _v1 fixo: QA que renderiza a versao aposentada
    # aprova o arquivo que o app nao serve mais
    _, glb = zp.dist_glb_current(REPO, avatar_id)
if not glb or not os.path.exists(glb):
    raise SystemExit(f"nao encontrei o GLB de {avatar_id}")

prefix = ("raw_" if use_raw else "") + ("torso_" if torso else "")
outdir = os.path.join(REPO, "qa", "inspect", avatar_id)
os.makedirs(outdir, exist_ok=True)

# cena limpa
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)

mesh = next(o for o in bpy.context.scene.objects if o.type == "MESH")

# bounding box em coordenadas de mundo
bb = [mesh.matrix_world @ Vector(c) for c in mesh.bound_box]
zmin = min(v.z for v in bb); zmax = max(v.z for v in bb)
cx = sum(v.x for v in bb) / 8; cy = sum(v.y for v in bb) / 8
center = Vector((cx, cy, (zmin + zmax) / 2))
height = zmax - zmin

# fundo cinza claro
world = bpy.data.worlds.new("W"); bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.85, 0.86, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

# alvo que camera e luzes miram (track-to constraint = mira robusta)
target = bpy.data.objects.new("target", None)
target.location = center
bpy.context.collection.objects.link(target)

# key + fill na frente, back atras. Sem a luz traseira a vista de costas sai em
# silhueta chapada e nao da para julgar dorsais/escapulas - e o avatar gira no
# app, entao as costas contam tanto quanto a frente (ARCHETYPES §8).
# Cada luz mira o alvo: rotacao fixa apontaria todas para o mesmo lado.
for name, loc, energy in [("key",  ( 2, -3,  3), 800),
                          ("fill", (-3, -2,  1.5), 300),
                          ("back", ( 1,  3.5, 2.5), 600)]:
    ld = bpy.data.lights.new(name, "AREA"); ld.energy = energy; ld.size = 3
    lo = bpy.data.objects.new(name, ld)
    lo.location = (center.x+loc[0], center.y+loc[1], center.z+loc[2])
    bpy.context.collection.objects.link(lo)
    lc = lo.constraints.new("TRACK_TO"); lc.target = target
    lc.track_axis = "TRACK_NEGATIVE_Z"; lc.up_axis = "UP_Y"

# camera
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d)
bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
cam_d.lens = 50
cam_d.sensor_fit = "VERTICAL"
tc = cam.constraints.new("TRACK_TO"); tc.target = target
tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

scene = bpy.context.scene
_engines = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in _engines else "BLENDER_EEVEE"
scene.render.resolution_x = 700; scene.render.resolution_y = 1000
scene.render.film_transparent = False

if torso:
    # tronco = do quadril a base do pescoco; e onde aparecem os artefatos de
    # abdomen. Angulo de 3/4 incluido: a luz rasante revela relevo falso que a
    # vista frontal achata.
    target.location = Vector((center.x, center.y, zmin + height * 0.62))
    dist = height * 1.1
    scene.render.resolution_x = 900; scene.render.resolution_y = 900
    views = {"00_frente": 0, "01_tresquartos": 40, "02_lado": 90}
else:
    dist = height * 2.4
    views = {"00_frente": 0, "01_lado": 90, "02_costas": 180, "03_ladoB": 270}

cam_z = target.location.z
for name, ang in views.items():
    a = math.radians(ang)
    cam.location = (center.x + dist*math.sin(a), center.y - dist*math.cos(a), cam_z)
    scene.render.filepath = os.path.join(outdir, f"{prefix}{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"  -> {prefix}{name}.png")

print(f"QA render OK: {outdir}")
