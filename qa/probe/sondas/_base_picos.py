"""Os picos de anel que o detector VIU na base, ao lado do que a folha diz.

Serve para escolher a correcao manual com evidencia: se o valor da folha bate
com um pico mais fraco que o prior preteriu, a correcao e ENCOSTAR NAQUELE PICO
- que continua sendo uma medida da malha. Se nao ha pico nenhum ali, a correcao
so pode ser o numero da folha, e isso e uma escolha bem mais fraca."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
m = json.load(open(os.path.join(ROOT, "config", "shorts_map.json"), encoding="utf-8"))
f = json.load(open(os.path.join(ROOT, "qa", "probe", "faixa", "_folha.json"),
                   encoding="utf-8"))

alvos = ["zen_f_b09i_d2", "zen_f_b09_d2", "zen_f_b05_d1", "zen_f_b11_d2",
         "zen_f_b10_d3", "zen_f_b04_d3"]
for k in alvos:
    e = m[k]
    d = e.get("diag", {})
    fb = f[k]["faixa"][1]
    print("%-14s folha %.3f   3D %.3f (%+.3f)" % (
        k, fb, e["faixa_lo_zh"], e["faixa_lo_zh"] - fb))
    print("   picos base (forca, zh): %s" % d.get("faixa_peaks_base"))
    print("   picos topo (forca, zh): %s" % d.get("faixa_peaks_topo"))
