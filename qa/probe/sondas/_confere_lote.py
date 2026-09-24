"""Confere, sem abrir o Blender, se o lote de peca+morph ficou consistente.

    python qa/probe/sondas/_confere_lote.py

Tres perguntas, e as tres sao de CONTABILIDADE - nao substituem as travas do
shorts.py nem o morph_cases.py, mas pegam o estado que da medo depois de um lote
interrompido: avatar que recebeu short novo e ficou SEM shape key.

  1. todo id do shorts_map tem GLB no disco, e um so por id
  2. todo id do morph_map aponta para o glb_version que esta no disco
  3. quem tem entrada no morph_map e NAO tem a versao batendo aparece na lista

A pergunta 2 e a que importa: `shorts --apply` grava o dist a partir do master,
que nao tem shape key (regra 9). Se o `morph --apply` nao correr em cima, o mapa
promete morph que o arquivo nao tem - e isso passa calado em toda regua que
olhe so o material ou so a peca.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
GLB = os.path.join(ROOT, "03_dist", "glb")

smap = json.load(open(os.path.join(ROOT, "config", "shorts_map.json"),
                      encoding="utf-8"))
mmap = json.load(open(os.path.join(ROOT, "config", "morph_map.json"),
                      encoding="utf-8"))

versoes = {}
for f in os.listdir(GLB):
    m = re.match(r"^(zen_[mf]_[a-z0-9_]+)_v(\d+)\.glb$", f)
    if m:
        versoes.setdefault(m.group(1), []).append(int(m.group(2)))

sem_glb = sorted(i for i in smap if i not in versoes)
duplicados = sorted(i for i, v in versoes.items() if len(v) > 1)
fora = []
for aid, e in sorted(mmap.items()):
    v = e.get("glb_version")
    disco = versoes.get(aid, [])
    if not disco or v not in disco:
        fora.append((aid, v, disco))

print("shorts_map: %d   morph_map: %d   ids com GLB: %d"
      % (len(smap), len(mmap), len(versoes)))
print("sem GLB no disco      : %s" % (", ".join(sem_glb) or "nenhum"))
print("id com DUAS versoes   : %s" % (", ".join(duplicados) or "nenhum"))
if fora:
    print("morph_map desalinhado : %d" % len(fora))
    for aid, v, disco in fora:
        print("   %-18s mapa v%s  disco %s" % (aid, v, disco))
else:
    print("morph_map desalinhado : nenhum")
print("sem entrada no morph_map: %d"
      % len([i for i in smap if i not in mmap]))
