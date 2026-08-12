"""Grava no shorts_map.json a altura do topo FRONTAL da faixa, lida na folha.

    python qa/probe/sondas/faixa_ref.py          # antes: gera o _folha.json
    python qa/probe/sondas/_set_faixa_topo.py    # grava a chave no mapa
    python scripts/shorts.py --all --fit         # a curva e RETRACADA dela

O irmao deste arquivo, _set_faixa_base.py, tem uma doutrina explicita: "trocar
medida de malha por numero de folha sem um pico que sustente seria inverter a
ordem das reguas". Aqui a situacao e a OUTRA, e e por isso que a mesma doutrina
nao se aplica:

  NA BORDA DE CIMA NAO HA MEDIDA DE MALHA PARA SER TROCADA. O _topo_piso.py
  contou, nos 37 femininos, de QUATRO A NOVE dos 9 setores da frente com
  concavidade NULA na ancora (LICOES.md 4.5b). Onde nao ha aro o argmax pega
  ruido de decimacao e a mediana de 7 o alisa num traçado plausivel. Medido no
  b08_d3 sem a valvula: 22 dos 24 setores ficaram na propria ancora e 2
  dispararam +0.046 - a cunha do esterno. Isso nao e um pico fraco preterido
  pelo prior; e ausencia de sinal.

Entao aqui a folha nao esta competindo com uma medida - ela esta ocupando um
lugar vazio. E ela e regua EXTERNA e POR AVATAR, que e exatamente o que a 4.5b
disse que faltava para a decisao ("nao existe regua externa para o traçado por
setor"): continua sem regua para o TRAÇADO, mas a ALTURA DO PICO tem uma, e o
pico e a unica incognita que o modelo precisa.

DUAS FOLHAS SAO ILEGIVEIS E SE DENUNCIAM SOZINHAS. O b08_d1 le topo frontal
0.869 e o b11_d1 le 0.861, contra a faixa 0.750..0.776 das outras 35 - a corrida
escura que o detector pegou nao e a faixa. Esses dois ficam de FORA e seguem no
traçado antigo ate a regua ser consertada. O limite abaixo nao e estetico: e a
janela em que a folha ja se provou legivel nas 35.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
MAPA = os.path.join(ROOT, "config", "shorts_map.json")
FOLHA = os.path.join(ROOT, "qa", "probe", "faixa", "_folha.json")

# A faixa das 35 legiveis e 0.750..0.776. A janela e generosa dos dois lados
# para nao reprovar corpo extremo, e apertada o bastante para pegar a leitura
# que pulou de peca (as duas ilegiveis leem 0.86).
PLAUSIVEL = (0.720, 0.800)


def main():
    with open(FOLHA, "r", encoding="utf-8") as f:
        folha = json.load(f)
    with open(MAPA, "r", encoding="utf-8") as f:
        smap = json.load(f)

    posto, fora = 0, []
    for aid, d in sorted(folha.items()):
        if not aid.startswith("zen_f_") or aid not in smap:
            continue
        fr = d.get("faixa_frente")
        if not fr:
            fora.append((aid, "sem corrida frontal"))
            continue
        topo = float(fr[0])
        if not PLAUSIVEL[0] <= topo <= PLAUSIVEL[1]:
            fora.append((aid, "folha ilegivel: {:.3f}".format(topo)))
            continue
        smap[aid]["faixa_topo_frente_zh"] = round(topo, 5)
        # A valvula do topo reto era o mesmo modelo com amplitude ZERO, e a
        # folha nunca endossa amplitude zero. Quem ganha a folha perde a valvula.
        smap[aid].pop("faixa_topo_reto", None)
        posto += 1

    with open(MAPA, "w", encoding="utf-8") as f:
        json.dump(smap, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    print("faixa_topo_frente_zh gravado em {} avatares".format(posto))
    for aid, por in fora:
        print("  FORA  {:<16} {}".format(aid, por))


main()
