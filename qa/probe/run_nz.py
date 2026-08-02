import json,os,subprocess,sys
sys.path.insert(0,'scripts'); import shorts_ref as R
import zenith_paths as zp
BL=r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
lib={a['id']:a['measured_bmi'] for a in json.load(open('library.json'))['avatars']}
ids=sorted(lib,key=lambda k:lib[k])
res=[]
for aid in ids:
    p=zp.ref_path('.', aid, 'front')
    if not os.path.isfile(p): continue
    pr=R.perfil_frontal(p)
    pr=R._simetriza(pr)[0] if pr else None
    o=subprocess.run([BL,"--background","--python","scripts/probe_nz.py","--",
                      "--id",aid,"--ref",json.dumps(pr)],
                     capture_output=True,text=True).stdout
    ln=[l for l in o.splitlines() if l.startswith("NZRESULT ")]
    if not ln: print(aid,"FALHOU"); continue
    d=json.loads(ln[0][9:]); d['imc']=lib[aid]; res.append(d)
    difs=[e-t for e,t in d['setores'].values() if t is not None]
    print("%-16s IMC %6.1f  n=%d  erro md %+0.4f  max %+0.4f"%(
        aid,lib[aid],len(difs),sum(difs)/len(difs) if difs else 0,
        max(difs,key=abs) if difs else 0))
json.dump(res,open('qa/probe/nz.json','w'),indent=1)
