import sys,io,contextlib,numpy as np
sys.path.insert(0,'qa/probe'); sys.path.insert(0,'scripts')
import bench, shorts as S
dados,refs=bench.main()
NB=S.WAIST_AZ_BINS; FRONT=NB//4; HALF=max(1,NB//6)
fmask=np.zeros(NB,bool)
for d in range(-HALF,HALF+1): fmask[(FRONT+d)%NB]=True

def fit(A,occ,ring,crotch_b,waist_b,hem_b,tem_anel,bmi,
        down=.10,up=0.,back=.05,sigf=.5,fill=0,med=5,raz=1,rz=2):
    M=S.w_fill_holes(np,A,occ,raz,rz) if fill else A
    out=[]
    for j in range(NB):
        l,h=((waist_b-down*S.Z_BINS, waist_b+up*S.Z_BINS) if fmask[j]
             else (waist_b-back*S.Z_BINS, waist_b+back*S.Z_BINS))
        lo=int(max(0,hem_b+1,round(l))); hi=int(min(S.Z_BINS-1,round(h)))
        if hi<lo: out.append(waist_b); continue
        zz=np.arange(lo,hi+1,dtype=float)
        sig=max((waist_b-lo)*sigf,1.0)
        w=M[j,lo:hi+1]*np.exp(-0.5*((zz-waist_b)/sig)**2)
        out.append(lo+int(w.argmax()) if w.size and w.max()>0 else waist_b)
    if med<3: return out
    k=med//2
    return [int(sorted([out[(j+d)%NB] for d in range(-k,k+1)])[k]) for j in range(NB)]

cfgs=[]
for fill in (0,1):
    for down in (.08,.10,.12):
        for sigf in (.4,.5,.7):
            for med in (5,7):
                cfgs.append((f"fill{fill} down{down} sig{sigf} med{med}",
                             lambda fill=fill,down=down,sigf=sigf,med=med,**k:
                             fit(down=down,sigf=sigf,fill=fill,med=med,**k)))
res=[]
for nome,fn in cfgs:
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf): r,rms=bench.avalia(fn,nome,refs,dados)
    res.append((r,rms,nome,buf.getvalue()))
res.sort(key=lambda t:(t[0],t[1]))
print("\n%-32s %5s %8s"%("config","fora","rms"))
for r,rms,n,_ in res[:10]: print("%-32s %5d %8.4f"%(n,r,rms))
print(res[0][3])
