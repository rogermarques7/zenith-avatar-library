import sys,os,numpy as np
sys.path.insert(0,'qa/probe'); sys.path.insert(0,'scripts')
import bench, shorts as S
dados,refs = bench.main()
NB=S.WAIST_AZ_BINS; FRONT=NB//4; HALF=max(1,NB//6)
fmask=np.zeros(NB,bool)
for d in range(-HALF,HALF+1): fmask[(FRONT+d)%NB]=True

def janelas(cb,wb,hemb,down,up,back):
    lo,hi=[],[]
    for j in range(NB):
        if fmask[j]: l,h=wb-down*S.Z_BINS, wb+up*S.Z_BINS
        else:        l,h=wb-back*S.Z_BINS, wb+back*S.Z_BINS
        lo.append(int(max(0,hemb+1,round(l)))); hi.append(int(min(S.Z_BINS-1,round(h))))
    return lo,hi

def prior_fit(A,occ,ring,crotch_b,waist_b,hem_b,tem_anel,bmi,
              down=0.10,up=0.0,back=0.05,sigma_f=0.5,fill=True):
    M = S.w_fill_holes(np,A,occ) if fill else A
    lo,hi=janelas(crotch_b,waist_b,hem_b,down,up,back)
    out=[]
    for j in range(NB):
        if hi[j]<lo[j]: out.append(waist_b); continue
        zz=np.arange(lo[j],hi[j]+1,dtype=float)
        sig=max((waist_b-lo[j])*sigma_f,1.0)
        w=M[j,lo[j]:hi[j]+1]*np.exp(-0.5*((zz-waist_b)/sig)**2)
        out.append(lo[j]+int(w.argmax()) if w.size and w.max()>0 else waist_b)
    return [int(sorted([out[(j+d)%NB] for d in (-2,-1,0,1,2)])[2]) for j in range(NB)]

def base(**kw):  # sessao 4: janela simetrica 0.10, com prior, sem preencher
    return prior_fit(down=0.10,up=0.10,back=0.10,fill=False,**kw)

cfgs=[("sessao4 (simetrica, sem preencher)", base),
      ("assim. 0.10 sem preencher", lambda **k: prior_fit(down=0.10,up=0.0,back=0.05,fill=False,**k)),
      ("assim. 0.10 preenchido",    lambda **k: prior_fit(down=0.10,up=0.0,back=0.05,fill=True,**k)),
      ("assim. 0.16 preench sig.8", lambda **k: prior_fit(down=0.16,up=0.0,back=0.05,sigma_f=0.8,fill=True,**k)),
      ("assim. 0.22 preench sig1.0",lambda **k: prior_fit(down=0.22,up=0.0,back=0.05,sigma_f=1.0,fill=True,**k)),
     ]
res=[]
for nome,fn in cfgs:
    import io,contextlib
    buf=io.StringIO()
    with contextlib.redirect_stdout(buf):
        r,rms=bench.avalia(fn,nome,refs,dados)
    res.append((r,rms,nome,buf.getvalue()))
print("\n%-34s %6s %8s"%("configuracao","fora","rms"))
for r,rms,nome,_ in res: print("%-34s %6d %8.4f"%(nome,r,rms))
print(res[min(range(len(res)),key=lambda i:(res[i][0],res[i][1]))][3])
