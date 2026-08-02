import sys,io,contextlib,json,numpy as np
sys.path.insert(0,'qa/probe'); sys.path.insert(0,'scripts')
import bench, shorts as S, shorts_ref as SR, os
import zenith_paths as zp
dados,refs=bench.main()
# alvo: topo do cos medido na folha de COSTAS (regua externa ja validada)
alvo={}
for aid,_ in dados:
    p=zp.ref_path('.', aid, 'back')
    if os.path.isfile(p):
        m=SR.medir(p)
        if m: alvo[aid]=m[0]

def escolhe(ring,crotch_b,teto,abs_lo,abs_hi,**k):
    pk=S.w_peaks(np,ring,crotch_b+0.090*S.Z_BINS,crotch_b+teto*S.Z_BINS)
    pk=[(s,b) for s,b in pk if abs_lo*S.Z_BINS<=b<=abs_hi*S.Z_BINS]
    return (pk[0][1] if pk else None)

print("%-22s %5s %8s %8s  piores"%("regra","fora","rms","sem_anel"))
for nome,teto,alo,ahi in [("teto .170 (sessao4)",.170,0,1),
                          ("teto .210 (sessao5)",.210,0,1),
                          ("teto .200",.200,0,1),
                          ("teto .210 + abs .48-.60",.210,.48,.60),
                          ("teto .230 + abs .48-.60",.230,.48,.60),
                          ("teto .230 + abs .49-.61",.230,.49,.61)]:
    errs=[]; sem=0; piores=[]
    for aid,d in dados:
        if aid not in alvo: continue
        b=escolhe(d['ring'],d['crotch_b'],teto,alo,ahi)
        if b is None: sem+=1; piores.append((9,aid)); continue
        e=(b+.5)/S.Z_BINS-alvo[aid]
        errs.append(e); piores.append((abs(e),aid))
    piores.sort(reverse=True)
    rms=(sum(e*e for e in errs)/max(len(errs),1))**.5
    fora=sum(1 for e in errs if abs(e)>0.05)+sem
    print("%-22s %5d %8.4f %8d  %s"%(nome,fora,rms,sem,
          ", ".join("%s %.3f"%(a,v) if v<9 else "%s SEM"%a for v,a in piores[:4])))

print("\n--- com RESERVA por argmax na janela, em vez de 'virilha + 0.12' ---")
def escolhe2(ring,crotch_b,teto,alo,ahi,reserva):
    lo=max(int(crotch_b+0.090*S.Z_BINS),int(alo*S.Z_BINS))
    hi=min(int(crotch_b+teto*S.Z_BINS),int(ahi*S.Z_BINS))
    pk=[(s,b) for s,b in S.w_peaks(np,ring,lo,hi)]
    if pk: return pk[0][1],True
    if not reserva: return int(crotch_b+0.12*S.Z_BINS),False
    if hi<=lo: return int(crotch_b+0.12*S.Z_BINS),False
    return lo+int(np.asarray(ring[lo:hi+1]).argmax()),False
for nome,res in [("reserva antiga",False),("reserva argmax",True)]:
    errs=[];piores=[]
    for aid,d in dados:
        if aid not in alvo: continue
        b,ok=escolhe2(d['ring'],d['crotch_b'],.230,.48,.60,res)
        e=(b+.5)/S.Z_BINS-alvo[aid]; errs.append(e); piores.append((abs(e),aid,ok))
    piores.sort(reverse=True)
    rms=(sum(e*e for e in errs)/len(errs))**.5
    print("%-16s fora %d  rms %.4f   piores: %s"%(nome,
        sum(1 for e in errs if abs(e)>0.05),rms,
        ", ".join("%s %.3f%s"%(a,v,"" if ok else "*") for v,a,ok in piores[:4])))
