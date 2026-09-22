"""probe_superficie.py — a regua que faltava: DEFEITO DE SUPERFICIE no cru.

  blender -b -P qa/probe/sondas/probe_superficie.py -- zen_m_b05n_d1
  blender -b -P qa/probe/sondas/probe_superficie.py -- zen_m_b05n_d1 --dist

Le 01_raw/{id}_raw.glb (ou o dist com --dist) e grava closes com LUZ RASANTE em
qa/superficie/{id}/, nas quatro regioes onde os artefatos da Meshy moram:
peito, faixa (feminino), virilha/peca e maos.

POR QUE ESTE SCRIPT EXISTE (sessao 35, 22/09/2026)
    Duas malhas foram reprovadas nesta sessao por defeito que NENHUMA das 8
    validacoes do process.py ve, porque nenhuma delas olha a superficie:

      zen_m_b05n_d1 (1a tentativa)  short ausente na FRENTE, so existia atras
      zen_m_b06k_d3                 mamilos ausentes nos dois peitorais

    As duas passariam 8/8. A do short e fatal: a regra 3b le a peca da MALHA,
    pelo vinco, e sem tecido nao ha o que detectar.

    E defeito de relevo so aparece com LUZ EM ANGULO. O primeiro veredito desta
    sessao errou porque o render caiu em Workbench (luz chapada) por um
    try/except que engoliu o nome errado da engine. Por isso aqui a engine e
    exigida explicitamente e o script MORRE se ela nao existir: degradar em
    silencio foi o defeito, nao o acidente.

    E o mesmo motivo da LICOES.md 4.5c ("veredito de pintura nao se da no render
    do --fit, ele e clay com luz chapada"), num eixo novo: relevo em vez de tinta.

USO NO FLUXO
    Passo OBRIGATORIO entre o GLB chegar do Downloads e o process.py rodar.
    Processar antes de olhar ja custou um id ocupado e um desfazer manual.
"""
import bpy, sys, os, math

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not argv:
    raise SystemExit("informe o id, ex.: zen_m_b05n_d1")
avatar_id = argv[0]
use_dist = "--dist" in argv

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import zenith_paths as zp                                          # noqa: E402

if use_dist:
    _, glb = zp.dist_glb_current(REPO, avatar_id)
else:
    glb = os.path.join(REPO, "01_raw", f"{avatar_id}_raw.glb")
if not glb or not os.path.exists(glb):
    raise SystemExit(f"nao encontrei o GLB de {avatar_id}")

outdir = os.path.join(REPO, "qa", "superficie", avatar_id)
os.makedirs(outdir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)

meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active

# clay claro e fosco: a peca do dist tem material proprio e mascararia o relevo
ob.data.materials.clear()
mat = bpy.data.materials.new("clay")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.77, 1)
bsdf.inputs["Roughness"].default_value = 0.42
ob.data.materials.append(mat)

co = [ob.matrix_world @ v.co for v in ob.data.vertices]
xs = [p.x for p in co]; ys = [p.y for p in co]; zs = [p.z for p in co]
alt = max(zs) - min(zs)
cx = (max(xs) + min(xs)) / 2
cy = (max(ys) + min(ys)) / 2

sc = bpy.context.scene

# EXPLICITA e DURA: degradar para luz chapada em silencio foi o defeito original
engines = {e.bl_rna.identifier for e in bpy.types.RenderEngine.__subclasses__()}
engine = next((e for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE") if e in engines), None)
if engine is None:
    try:
        sc.render.engine = "BLENDER_EEVEE"
        engine = "BLENDER_EEVEE"
    except TypeError as err:
        raise SystemExit(
            "ABORTADO: nenhuma engine EEVEE nesta build do Blender.\n"
            "Workbench NAO serve — com luz chapada o defeito de relevo fica\n"
            f"invisivel e o veredito sai errado. Detalhe: {err}"
        )
sc.render.engine = engine

sc.render.resolution_x, sc.render.resolution_y = 900, 900
world = bpy.data.worlds.new("w"); sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.8, 0.82, 1)

cam_data = bpy.data.cameras.new("c"); cam_data.type = "ORTHO"
cam = bpy.data.objects.new("c", cam_data); sc.collection.objects.link(cam)
sc.camera = cam

# LUZ RASANTE: e o angulo que revela relevo. Frontal difusa apaga o defeito.
ld = bpy.data.lights.new("k", type="AREA"); ld.energy = 700; ld.size = 2
lamp = bpy.data.objects.new("k", ld); sc.collection.objects.link(lamp)
lamp.rotation_euler = (math.radians(75), 0, math.radians(-40))

# (nome, fracao da altura, span em fracao da altura)
REGIOES = [
    ("peito",   0.745, 0.20),   # mamilo, costura do peitoral
    ("faixa",   0.720, 0.26),   # feminino: bordas do anel, o que o shorts.py le
    ("virilha", 0.500, 0.24),   # cos e bainha do short — regra 3b
    ("maos",    0.530, 0.16),   # dedos fundidos/palmados
]

for nome, zfrac, span in REGIOES:
    zc = min(zs) + alt * zfrac
    cam_data.ortho_scale = alt * span
    lamp.location = (cx - 3, cy - 3, zc + alt * 0.1)
    for vista, ang in (("frontal", 0), ("obliqua", 35)):
        a = math.radians(ang)
        cam.location = (cx + 5 * math.sin(a), cy - 5 * math.cos(a), zc)
        cam.rotation_euler = (math.radians(90), 0, a)
        sc.render.filepath = os.path.join(outdir, f"{avatar_id}_{nome}_{vista}.png")
        bpy.ops.render.render(write_still=True)

print(f"\n[{engine}] {len(REGIOES) * 2} closes em {outdir}")
print("OLHAR ANTES DE RODAR O process.py — as 8 validacoes nao veem superficie.")
