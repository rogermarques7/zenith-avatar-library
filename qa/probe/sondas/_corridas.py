"""TODAS as corridas escuras da folha de costas, sem escolher nenhuma.

O faixa_ref assume que a 1a corrida e a faixa e a 2a e o short. Se a folha tiver
3 corridas - sombra, cabelo, o que for -, a 2a nao e o short e o delta que sai
dali e ficcao. A folha do b08_d1 ja leu faixa frontal em 0.869/0.856, que e uma
peca de 1,3% de altura no pescoco: a regua erra, e antes de mandar 11 avatares
para conserto por causa dela e preciso ver a lista crua."""
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zenith_paths as zp  # noqa: E402
from faixa_ref import corridas  # noqa: E402

ALVOS = ["zen_f_b10_d1", "zen_f_b10_d2", "zen_f_b10_d3", "zen_f_b11_d2",
         "zen_f_b12_d1", "zen_f_b11_d1", "zen_f_b09_d2", "zen_f_b09_d1",
         "zen_f_b07_d1", "zen_f_b06_d1", "zen_f_b05_d1", "zen_f_b08_d1",
         "zen_f_b01_d1"]

for aid in ALVOS:
    p = zp.ref_path(ROOT, aid, "back")
    if not os.path.isfile(p):
        print("%-16s sem folha" % aid)
        continue
    cs = corridas(p)
    print("%-16s %d corridas: %s" % (
        aid, len(cs), "  ".join("%.3f/%.3f" % c for c in cs)))
