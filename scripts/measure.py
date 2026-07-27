"""measure.py — mede a silhueta dos recortes de referência.

Régua RÁPIDA e APROXIMADA, para julgar uma folha ANTES de gastar créditos na
Meshy. A "barriga" (profundidade do perfil na faixa abdominal, em % da altura
da figura) revela saltos grosseiros. Melhor que julgar no olho.

⚠️ NÃO É A RÉGUA DE VERDADE — quem decide é o scripts/metrics.py.
    Isto mede o DESENHO. O metrics.py mede o MASTER 3D, que é o produto.

⚠️ LIMITAÇÃO CONHECIDA: a silhueta INCLUI OS BRAÇOS.
    Tanto a barriga (perfil) quanto os ombros (frente) sobem se o braço estiver
    um pouco mais afastado ou mais à frente do corpo — sem que o corpo tenha
    mudado. Enquanto a pose se mantém constante entre folhas o erro é constante
    e a ORDEM da série continua válida, que é para o que isto serve.
    Quando a pose varia, a ordem INVERTE: o zen_m_b05h_d1 mediu barriga 22,3
    contra 17,2 do zen_m_b05_d1 (parecia bem maior) e o master 3D deu IMC 26,2
    contra 27,8 — ou seja, MENOR. Ver state.md.

Uso:
    python scripts/measure.py                 # mede todos os recortes existentes
    python scripts/measure.py zen_m_b02_d3    # mede um avatar
    python scripts/measure.py --def d3        # mede uma linha de definição inteira
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

REFS = Path(__file__).resolve().parent.parent / "00_input" / "references"

# Faixa vertical medida, em fração da altura da figura (0 = topo da cabeça).
BELLY_BAND = (0.44, 0.56)
SHOULDER_BAND = (0.18, 0.24)
BG_TOLERANCE = 28  # distância do cinza de fundo que ainda conta como fundo


def silhouette(path):
    """Máscara booleana da figura, por diferença do fundo (cantos da imagem)."""
    img = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
    h, w, _ = img.shape
    corners = np.concatenate([
        img[:8, :8].reshape(-1, 3), img[:8, -8:].reshape(-1, 3),
        img[-8:, :8].reshape(-1, 3), img[-8:, -8:].reshape(-1, 3),
    ])
    bg = np.median(corners, axis=0)
    dist = np.abs(img - bg).max(axis=2)
    return dist > BG_TOLERANCE, h, w


def band_width(mask, top, bot, band):
    """Largura horizontal máxima da silhueta dentro da faixa vertical."""
    fig_h = bot - top
    y0 = top + int(band[0] * fig_h)
    y1 = top + int(band[1] * fig_h)
    widths = []
    for y in range(y0, y1):
        cols = np.flatnonzero(mask[y])
        if cols.size:
            widths.append(cols[-1] - cols[0] + 1)
    if not widths:
        return 0.0
    return max(widths) / fig_h * 100.0


def measure(avatar_id):
    folder = REFS / avatar_id
    out = {"id": avatar_id}
    for view, band, key in (("side", BELLY_BAND, "belly"),
                            ("front", SHOULDER_BAND, "shoulders")):
        path = folder / f"{avatar_id}_ref_{view}.png"
        if not path.exists():
            out[key] = None
            continue
        mask, _, _ = silhouette(path)
        rows = np.flatnonzero(mask.any(axis=1))
        if rows.size < 2:
            out[key] = None
            continue
        out[key] = band_width(mask, rows[0], rows[-1], band)
    return out


def main():
    args = [a for a in sys.argv[1:]]
    if args and args[0] == "--def":
        suffix = "_" + args[1]
        ids = sorted(p.name for p in REFS.iterdir()
                     if p.is_dir() and p.name.endswith(suffix))
    elif args:
        ids = args
    else:
        ids = sorted(p.name for p in REFS.iterdir() if p.is_dir())

    print(f"{'avatar':<16} {'barriga%':>9} {'passo':>7} {'ombros%':>9}")
    prev = None
    for avatar_id in ids:
        m = measure(avatar_id)
        belly = m["belly"]
        shoulders = m["shoulders"]
        step = "" if prev is None or belly is None else f"{belly - prev:+.1f}"
        b = "  --" if belly is None else f"{belly:.1f}"
        s = "  --" if shoulders is None else f"{shoulders:.1f}"
        print(f"{avatar_id:<16} {b:>9} {step:>7} {s:>9}")
        if belly is not None:
            prev = belly


if __name__ == "__main__":
    main()
