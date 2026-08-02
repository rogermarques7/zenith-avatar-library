"""Sonda 2: o mapa de concavidade e ESPARSO demais para ser lido celula a celula?"""
import os, sys, argparse, math
import bpy, numpy as np
argv = sys.argv[sys.argv.index("--")+1:]
ap = argparse.ArgumentParser(); ap.add_argument("--id", required=True)
a = ap.parse_args(argv)
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import shorts as S

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT,"02_master",a.id+"_master.glb"))
obj=[o for o in bpy.context.scene.objects if o.type=="MESH"][0]; me=obj.data
zs=[v.co.z for v in me.vertices]; H=max(zs)-min(zs)
n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get("co",co); co=co.reshape(n,3)
crotch, leg_id, is_arm = S.w_limbs(me,np,co,H)
ov=S.load_map(ROOT).get(a.id,{}).get("crotch_override_zh")
if ov: crotch=ov*H
crotch_b=int(crotch/H*S.Z_BINS)
k,_=S.w_curvature(me,np); kn=np.clip(k/max(float(np.percentile(k,99.0)),1e-9),0.0,1.0)
z=co[:,2]; torso=np.where((~is_arm)&(z>=crotch))[0]
bs=S.w_back_side_mask(np,S.WAIST_AZ_BINS)
A,ring=S.w_ring_map(np,co,kn,torso,H,"axis",S.WAIST_AZ_BINS,az_mask=bs)
pk=S.w_peaks(np,ring,crotch_b+S.WAIST_ABOVE_CROTCH[0]*S.Z_BINS,crotch_b+S.WAIST_ABOVE_CROTCH[1]*S.Z_BINS)
wb=pk[0][1] if pk else int(crotch_b+0.12*S.Z_BINS)

print("PROBE2 %s  virilha %.4f  anel %.4f"%(a.id,crotch/H,(wb+0.5)/S.Z_BINS))
front=S.WAIST_AZ_BINS//4; half=max(1,S.WAIST_AZ_BINS//6)
fronts=[(front+d)%S.WAIST_AZ_BINS for d in range(-half,half+1)]
lo,hi=crotch_b,wb+3
print("  ocupacao do mapa na frente: %.0f%% das celulas tem vertice"%(
    100*np.mean(A[np.ix_(fronts,range(lo,hi+1))]>0)))

# preenche buracos: max numa vizinhanca (+-1 setor, +-2 fatias), depois suaviza
Af=A.copy()
for _ in range(1):
    P=np.stack([np.roll(Af,d,axis=0) for d in (-1,0,1)])
    Af=P.max(axis=0)
Q=np.stack([np.roll(Af,d,axis=1) for d in (-2,-1,0,1,2)])
Af=Q.max(axis=0)
print("  depois de tapar buracos:    %.0f%%"%(100*np.mean(Af[np.ix_(fronts,range(lo,hi+1))]>0)))

zs_show=list(range(lo,hi+1,3))
print("\n  CRU        zh " + " ".join("%5.3f"%((b+.5)/S.Z_BINS) for b in zs_show))
for j in fronts: print("  s%2d           "%j + " ".join("%5.2f"%A[j,b] for b in zs_show))
print("\n  TAPADO     zh " + " ".join("%5.3f"%((b+.5)/S.Z_BINS) for b in zs_show))
for j in fronts: print("  s%2d           "%j + " ".join("%5.2f"%Af[j,b] for b in zs_show))
print("\n  argmax por setor no mapa TAPADO:")
for j in fronts:
    seg=Af[j,lo:hi+1]; b=lo+int(seg.argmax())
    print("  s%2d  zh %.4f  valor %.3f"%(j,(b+.5)/S.Z_BINS,Af[j,b]))
