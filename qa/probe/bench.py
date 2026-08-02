"""Banco de ensaio do ajuste do cos, offline.

Le os mapas cacheados por scripts/cache_maps.py e avalia um candidato de
algoritmo contra a regua da FOLHA nos 39 avatares, em segundos. Serve para
escolher parametro com evidencia em vez de rodar --fit --all (25 min) por
palpite - o que ja custou tres rodadas nesta sessao.

    python qa/probe/bench.py
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import zenith_paths as zp  # noqa: E402
import shorts as S          # noqa: E402
import shorts_ref as SR     # noqa: E402

MAPS = os.path.join(ROOT, "qa", "probe", "maps")
CACHE_REF = os.path.join(ROOT, "qa", "probe", "refs.json")


def carrega_refs(ids):
    if os.path.isfile(CACHE_REF):
        with open(CACHE_REF, "r", encoding="utf-8") as f:
            return json.load(f)
    out = {}
    for aid in ids:
        p = os.path.join(zp.refs_dir(ROOT, aid),
                         aid + "_ref_front.png")
        if not os.path.isfile(p):
            continue
        pr = SR.perfil_frontal(p)
        out[aid] = SR._simetriza(pr)[0] if pr else None
    with open(CACHE_REF, "w", encoding="utf-8") as f:
        json.dump(out, f)
    return out


def avalia(fn, nome, refs, dados):
    """fn(A, occ, ring, crotch_b, waist_b, hem_b, tem_anel) -> lista de bins."""
    linhas, ruins = [], 0
    for aid, d in dados:
        w = fn(**d)
        ref = refs.get(aid)
        if not ref:
            continue
        zh = [(b + 0.5) / S.Z_BINS for b in w]
        pares = [(zh[j], ref[j]) for j in range(len(ref)) if ref[j] is not None]
        if len(pares) < 4:
            continue
        difs = [t - r for t, r in pares]
        mx = max(difs, key=abs)
        arco3 = max(t for t, _ in pares) - min(t for t, _ in pares)
        arcor = max(r for _, r in pares) - min(r for _, r in pares)
        if abs(mx) > SR.TOL_TRACADO:
            ruins += 1
        linhas.append((aid, d["bmi"], arcor, arco3, sum(difs) / len(difs), mx))
    rms = (sum(l[5] ** 2 for l in linhas) / max(len(linhas), 1)) ** 0.5
    print("\n=== {} ===   fora: {}/{}   rms(erro_mx): {:.4f}".format(
        nome, ruins, len(linhas), rms))
    for aid, bmi, ar, a3, md, mx in linhas:
        flag = " <<" if abs(mx) > SR.TOL_TRACADO else ""
        print("  {:<15} {:>6.1f}  arco {:.3f}/{:.3f}  md {:+.3f}  mx {:+.3f}{}".format(
            aid, bmi, ar, a3, md, mx, flag))
    return ruins, rms


def main():
    lib = os.path.join(ROOT, "library.json")
    with open(lib, "r", encoding="utf-8") as f:
        bmi = {x["id"]: x.get("measured_bmi", 0) for x in json.load(f)["avatars"]}
    ids = sorted(bmi, key=lambda k: bmi[k])
    refs = carrega_refs(ids)

    dados = []
    for aid in ids:
        p = os.path.join(MAPS, aid + ".npz")
        if not os.path.isfile(p):
            continue
        z = np.load(p)
        cb, wb, hemb, _hmin, tem = [int(x) for x in z["meta"]]
        dados.append((aid, {"A": z["A"].astype(np.float64), "occ": z["occ"],
                            "ring": z["ring"].astype(np.float64),
                            "crotch_b": cb, "waist_b": wb, "hem_b": hemb,
                            "tem_anel": bool(tem), "bmi": bmi[aid]}))
    print("avatares no cache: {}".format(len(dados)))
    return dados, refs


if __name__ == "__main__":
    main()
