import json,os,subprocess
BL=r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
lib={a['id']:a['measured_bmi'] for a in json.load(open('library.json'))['avatars']}
for aid in sorted(lib,key=lambda k:lib[k]):
    if os.path.isfile(f'qa/probe/maps/{aid}.npz'): continue
    o=subprocess.run([BL,"--background","--python","scripts/cache_maps.py","--","--id",aid],
                     capture_output=True,text=True).stdout
    ln=[l for l in o.splitlines() if l.startswith("CACHE ")]
    print(aid, ln[0][6:] if ln else "FALHOU")
